
#!/usr/bin/env python3
"""
start_xmrt_system.py — XMRT Ecosystem Worker Orchestrator (Render-friendly)

Purpose:
- Starts optional MCP servers (GitHub / Render / XMRT) as child processes
- Runs autonomous background loops (learning, GitHub discovery/maintenance, deployment monitoring)
- Emits coordination events to the web app (if COORDINATION_ENDPOINT is set) or logs locally

This script DOES NOT bind to a network port. Run it as a Render "Background Worker".
For the web UI and API, use gunicorn with main_enhanced_coordination:app.

Key env vars (safe defaults applied when possible):
  Required:
    - GITHUB_TOKEN                : GitHub PAT (repo/public_repo scope as needed)
    - OPENAI_API_KEY              : If downstream analysis uses OpenAI (optional for this worker)

  Strongly recommended / safety:
    - XMRT_DRY_RUN=1              : Prevents write mutations (advisory only in this worker)
    - GITHUB_SAFE_MODE=advice     : advice | issues | prs | disabled
    - GITHUB_ALLOWLIST_ORGS=DevGruGold
    - GITHUB_BLOCKLIST_ORGS=

  Discovery / scanning:
    - GITHUB_GLOBAL_DISCOVERY=0   : 1 to enable global GitHub search (search API)
    - GITHUB_SEARCH_QUERIES="monero OR xmrt in:readme,description language:rust,python"
    - GITHUB_MAX_REPOS_PER_CYCLE=25
    - GITHUB_REPOS="DevGruGold/XMRT-Ecosystem,DevGruGold/xmrtassistant"

  Cadence:
    - SCAN_INTERVAL_SECONDS=900
    - SCAN_JITTER_SECONDS=60
    - MONITOR_INTERVAL_SECONDS=120
    - LEARNING_INTERVAL_SECONDS=300

  Coordination bridge (optional):
    - COORDINATION_ENDPOINT="https://<your-web-url>/api/coordination/trigger"
    - COORDINATION_TOKEN="<shared-secret-if-you-enforce-one>"

  Logging / misc:
    - LOG_LEVEL=info
"""

import os
import sys
import json
import time
import shlex
import signal
import queue
import random
import logging
import asyncio
import threading
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional

# Third-party (optional at runtime; guarded)
try:
    from github import Github, GithubException, RateLimitExceededException
except Exception:  # pragma: no cover
    Github = None
    GithubException = Exception
    RateLimitExceededException = Exception

# ---------------------------
# Logging
# ---------------------------
LOG_LEVEL = os.getenv("LOG_LEVEL", "info").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("xmrt.startup")

# ---------------------------
# Utilities
# ---------------------------
def _b2bool(v: Optional[str], default: bool = False) -> bool:
    if v is None:
        return default
    return str(v).strip().lower() in {"1", "true", "yes", "y", "on"}

def _env_csv(key: str, default: str = "") -> List[str]:
    raw = os.getenv(key, default)
    if not raw:
        return []
    return [x.strip() for x in raw.split(",") if x.strip()]

def _jittered_sleep(base_seconds: int, jitter_seconds: int) -> None:
    time.sleep(base_seconds + random.randint(0, max(0, jitter_seconds)))

def _safe_int(key: str, default: int) -> int:
    try:
        return int(os.getenv(key, str(default)))
    except Exception:
        return default

# ---------------------------
# Coordination bridge
# ---------------------------
def emit_coordination_event(event_type: str, payload: Dict[str, Any]) -> None:
    """
    POST an event to the web coordination API if COORDINATION_ENDPOINT is set,
    otherwise just log it locally.
    """
    endpoint = os.getenv("COORDINATION_ENDPOINT")
    if not endpoint:
        logger.info("Coordination event (local): %s %s", event_type, json.dumps(payload)[:800])
        return

    try:
        import requests  # local import to avoid hard dep if not used

        headers = {"Content-Type": "application/json"}
        token = os.getenv("COORDINATION_TOKEN")
        if token:
            headers["Authorization"] = f"Bearer {token}"

        body = {"event_type": event_type, "payload": payload}
        resp = requests.post(endpoint, headers=headers, json=body, timeout=15)
        if resp.status_code < 300:
            logger.info("Emitted coordination event to %s: %s", endpoint, event_type)
        else:
            logger.warning("Coordination endpoint %s returned %s: %s", endpoint, resp.status_code, resp.text[:500])
    except Exception as e:  # pragma: no cover
        logger.warning("Failed to emit coordination event to %s: %s", endpoint, e)

# ---------------------------
# MCP server management
# ---------------------------
class MCPProcess:
    def __init__(self, name: str, script: Path):
        self.name = name
        self.script = script
        self.proc: Optional[subprocess.Popen] = None

    def start(self) -> bool:
        if not self.script.exists():
            logger.warning("MCP script not found for %s: %s", self.name, self.script)
            return False
        try:
            self.proc = subprocess.Popen(
                [sys.executable, str(self.script)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            logger.info("Started MCP %s (PID=%s)", self.name, self.proc.pid)
            return True
        except Exception as e:  # pragma: no cover
            logger.error("Failed to start MCP %s: %s", self.name, e)
            return False

    def is_running(self) -> bool:
        return self.proc is not None and self.proc.poll() is None

    def stop(self, timeout: float = 5.0) -> None:
        if self.proc and self.is_running():
            try:
                self.proc.terminate()
                self.proc.wait(timeout=timeout)
                logger.info("Stopped MCP %s", self.name)
            except Exception as e:  # pragma: no cover
                logger.warning("Error stopping MCP %s: %s", self.name, e)

# ---------------------------
# GitHub automation
# ---------------------------
class GithubAutomation:
    def __init__(self) -> None:
        self.token = os.getenv("GITHUB_TOKEN")
        self.safe_mode = os.getenv("GITHUB_SAFE_MODE", "advice").lower()  # advice|issues|prs|disabled
        self.dry_run = _b2bool(os.getenv("XMRT_DRY_RUN", "1"), default=True)
        self.allow_orgs = set(x.lower() for x in _env_csv("GITHUB_ALLOWLIST_ORGS", "DevGruGold"))
        self.block_orgs = set(x.lower() for x in _env_csv("GITHUB_BLOCKLIST_ORGS", ""))
        self.global_discovery = _b2bool(os.getenv("GITHUB_GLOBAL_DISCOVERY", "0"))
        self.max_repos = _safe_int("GITHUB_MAX_REPOS_PER_CYCLE", 25)
        self.seed_repos = _env_csv("GITHUB_REPOS", "DevGruGold/XMRT-Ecosystem,DevGruGold/xmrtassistant")
        self.search_queries = os.getenv(
            "GITHUB_SEARCH_QUERIES",
            "monero OR xmrt in:readme,description language:rust language:python",
        )

        self.gh = Github(self.token, per_page=min(100, self.max_repos)) if self.token and Github else None

    def _allowed_repo(self, full_name: str) -> bool:
        try:
            org = full_name.split("/")[0].lower()
        except Exception:
            return False
        if self.block_orgs and org in self.block_orgs:
            return False
        if self.allow_orgs and org not in self.allow_orgs and not self.global_discovery:
            return False
        return True

    def _list_seed_repos(self) -> List[str]:
        return [r for r in self.seed_repos if self._allowed_repo(r)]

    def _search_repos(self) -> List[str]:
        if not (self.gh and self.global_discovery and self.search_queries):
            return []
        out = []
        try:
            q = self.search_queries
            logger.info("GitHub search query: %s", q)
            for repo in self.gh.search_repositories(query=q)[: self.max_repos]:
                full = repo.full_name
                if self._allowed_repo(full):
                    out.append(full)
            return out
        except RateLimitExceededException as e:  # pragma: no cover
            logger.warning("GitHub rate limit exceeded: %s", e)
            return []
        except GithubException as e:  # pragma: no cover
            logger.warning("GitHub search error: %s", e)
            return []
        except Exception as e:  # pragma: no cover
            logger.warning("Unexpected GitHub search error: %s", e)
            return []

    def analyze_repo(self, full_name: str) -> Dict[str, Any]:
        """
        Lightweight, safe analysis of a repo. Avoids mutations unless safe_mode permits and dry_run=False.
        """
        result = {"repo": full_name, "status": "ok", "actions": []}
        if not self.gh:
            result["status"] = "skipped"
            result["reason"] = "GitHub client not initialized"
            return result

        try:
            repo = self.gh.get_repo(full_name)
            default_branch = repo.default_branch or "main"
            topics = []
            try:
                topics = repo.get_topics()
            except Exception:
                pass

            # Heuristics: surface missing files or stale issues (advice mode)
            advice = []
            if "security" not in topics and "dependabot" not in topics:
                advice.append("Consider enabling Dependabot and adding SECURITY.md")

            if default_branch not in {"main", "master"}:
                advice.append(f"Non-standard default branch '{default_branch}'")

            # Emit coordination event with findings
            payload = {
                "action": "repo_analysis",
                "repo": full_name,
                "default_branch": default_branch,
                "topics": topics,
                "advice": advice,
                "safe_mode": self.safe_mode,
                "dry_run": self.dry_run,
            }
            emit_coordination_event("coordination.request", payload)

            # Optional safe write actions (issues/PRs) — gated
            if not self.dry_run and self.safe_mode in {"issues", "prs"} and advice and self._allowed_repo(full_name):
                title = "XMRT Ecosystem Advice: Project Hardening Suggestions"
                body = (
                    "This is an automated suggestion from the XMRT ecosystem worker.\n\n"
                    "Recommendations:\n"
                    + "".join(f"- {a}\n" for a in advice)
                    + "\nSet `XMRT_DRY_RUN=1` to disable actions, or `GITHUB_SAFE_MODE=advice` to only log suggestions."
                )
                try:
                    repo.create_issue(title=title, body=body)
                    result["actions"].append("opened_issue")
                except Exception as e:  # pragma: no cover
                    logger.info("Could not open issue on %s: %s", full_name, e)

            return result
        except GithubException as e:
            return {"repo": full_name, "status": "error", "error": str(e)}
        except Exception as e:
            return {"repo": full_name, "status": "error", "error": str(e)}

    def run_cycle(self) -> Dict[str, Any]:
        """
        One automation cycle:
          - analyze seed repos
          - (optional) search & analyze global repos
        """
        analyzed: List[Dict[str, Any]] = []
        seeds = self._list_seed_repos()
        for r in seeds:
            analyzed.append(self.analyze_repo(r))

        if self.global_discovery:
            for r in self._search_repos():
                analyzed.append(self.analyze_repo(r))

        summary = {
            "count": len(analyzed),
            "ok": sum(1 for a in analyzed if a.get("status") == "ok"),
            "errors": [a for a in analyzed if a.get("status") == "error"],
        }
        logger.info("GitHub automation summary: %s ok / %s total", summary["ok"], summary["count"])
        emit_coordination_event("coordination.request", {"action": "automation_summary", **summary})
        return summary

# ---------------------------
# System Manager
# ---------------------------
class XMRTSystemManager:
    def __init__(self) -> None:
        self.processes: Dict[str, MCPProcess] = {}
        self.shutdown_flag = threading.Event()

        # Intervals
        self.scan_interval = _safe_int("SCAN_INTERVAL_SECONDS", 900)
        self.scan_jitter = _safe_int("SCAN_JITTER_SECONDS", 60)
        self.monitor_interval = _safe_int("MONITOR_INTERVAL_SECONDS", 120)
        self.learning_interval = _safe_int("LEARNING_INTERVAL_SECONDS", 300)

        # Components
        self.gh_automation = GithubAutomation()

        # State snapshot
        self.state_lock = threading.Lock()
        self.state: Dict[str, Any] = {
            "startup_time": time.time(),
            "mcp_servers": {},
            "agents": {},         # logical agent bookkeeping only (no processes here)
            "health_checks": {},
            "last_update": time.time(),
        }

        # Validate minimal environment — be lenient to keep worker alive
        if not os.getenv("GITHUB_TOKEN"):
            logger.warning("GITHUB_TOKEN is not set. GitHub automation will be skipped.")
        if not os.getenv("OPENAI_API_KEY"):
            logger.info("OPENAI_API_KEY is not set. Downstream LLM analysis will be skipped if required.")

    # ---------- MCP ----------
    def start_mcp_servers(self) -> None:
        logger.info("Starting MCP servers...")
        configs = {
            "github": Path("mcp-integration/github_mcp_server_clean.py"),
            "render": Path("mcp-integration/render_mcp_server_clean.py"),
            "xmrt": Path("mcp-integration/xmrt_mcp_server_clean.py"),
        }
        for name, script in configs.items():
            proc = MCPProcess(name, script)
            ok = proc.start()
            if ok:
                self.processes[name] = proc
                with self.state_lock:
                    self.state["mcp_servers"][name] = {
                        "status": "running",
                        "pid": proc.proc.pid if proc.proc else None,
                        "started_at": time.time(),
                    }
            else:
                with self.state_lock:
                    self.state["mcp_servers"][name] = {"status": "not_found"}

    def monitor_loop(self) -> None:
        logger.info("Deployment monitoring loop started (interval=%ss)", self.monitor_interval)
        while not self.shutdown_flag.is_set():
            try:
                for name, proc in list(self.processes.items()):
                    status = "running" if proc.is_running() else "stopped"
                    with self.state_lock:
                        self.state["mcp_servers"].setdefault(name, {})["status"] = status
                with self.state_lock:
                    self.state["health_checks"]["deployment_monitoring"] = {
                        "status": "healthy",
                        "last_check": time.time(),
                    }
                    self.state["last_update"] = time.time()
            except Exception as e:  # pragma: no cover
                logger.warning("Monitor error: %s", e)
            time.sleep(self.monitor_interval)

    # ---------- Learning ----------
    def learning_loop(self) -> None:
        logger.info("Learning loop started (interval=%ss)", self.learning_interval)
        # lightweight heartbeat; real learning is delegated to app-side agents
        while not self.shutdown_flag.is_set():
            with self.state_lock:
                self.state["agents"]["heartbeat"] = {
                    "status": "alive",
                    "last_activity": time.time(),
                }
                self.state["last_update"] = time.time()
            emit_coordination_event(
                "coordination.request",
                {"action": "heartbeat", "source": "worker", "ts": int(time.time())},
            )
            time.sleep(self.learning_interval)

    # ---------- GitHub Automation ----------
    def github_loop(self) -> None:
        if not self.gh_automation.gh:
            logger.info("GitHub automation disabled (no GITHUB_TOKEN or PyGithub missing).")
            return
        logger.info(
            "GitHub automation loop started (interval=%ss ±%ss) global_discovery=%s",
            self.scan_interval, self.scan_jitter, self.gh_automation.global_discovery,
        )
        while not self.shutdown_flag.is_set():
            try:
                self.gh_automation.run_cycle()
            except Exception as e:  # pragma: no cover
                logger.warning("GitHub automation cycle error: %s", e)
            _jittered_sleep(self.scan_interval, self.scan_jitter)

    # ---------- Lifecycle ----------
    def start(self) -> None:
        logger.info("🚀 XMRT Worker starting… (no network port will be opened)")
        self.start_mcp_servers()

        # Threads
        threading.Thread(target=self.monitor_loop, name="monitor", daemon=True).start()
        threading.Thread(target=self.learning_loop, name="learning", daemon=True).start()
        threading.Thread(target=self.github_loop, name="github", daemon=True).start()

        # Initial coordination event
        emit_coordination_event(
            "coordination.request",
            {
                "action": "worker_started",
                "mcp": list(self.state["mcp_servers"].keys()),
                "safe_mode": os.getenv("GITHUB_SAFE_MODE", "advice"),
                "dry_run": _b2bool(os.getenv("XMRT_DRY_RUN", "1"), True),
            },
        )

    def stop(self) -> None:
        logger.info("Stopping XMRT Worker…")
        self.shutdown_flag.set()
        for proc in self.processes.values():
            proc.stop()

    def status_snapshot(self) -> Dict[str, Any]:
        with self.state_lock:
            return json.loads(json.dumps(self.state))

# ---------------------------
# Entrypoint
# ---------------------------
def main() -> None:
    mgr = XMRTSystemManager()

    # Graceful shutdown handlers
    def _graceful(signum, frame):  # pragma: no cover
        logger.info("Received signal %s; shutting down.", signum)
        mgr.stop()
        sys.exit(0)

    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, _graceful)

    mgr.start()
    logger.info("XMRT worker is running. (Use the web service for API/UI)")

    # Keep alive
    try:
        while True:
            time.sleep(60)
            snap = mgr.status_snapshot()
            active_mcp = sum(1 for s in snap["mcp_servers"].values() if s.get("status") == "running")
            logger.info("Status: %s MCP servers running", active_mcp)
    except KeyboardInterrupt:  # pragma: no cover
        _graceful("KeyboardInterrupt", None)

if __name__ == "__main__":
    main()
```
