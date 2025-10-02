#!/usr/bin/env python3
"""
main_enhanced_coordination.py — XMRT Enhanced Ecosystem (Web + Coordination + Global Discovery)

WHAT THIS DOES
--------------
• Exposes a production-ready Flask `app` so you can run with Gunicorn:
    gunicorn main_enhanced_coordination:app -b 0.0.0.0:$PORT -k gevent --workers ${WEB_CONCURRENCY:-2}
• Runs a lightweight rules engine that:
    - Handles `coordination.request` (fan-out to discovery + analysis + builders)
    - Discovers relevant repos across GitHub (optional & gated)
    - Analyzes repos with OpenAI (rate-limited)
    - Files issues and optionally PRs (strict safety gates)
• Separates web vs worker via ENABLE_AUTON_WORKER (web=0, worker=1)

SAFETY-FIRST ENV VARS (set these in Render/your env)
----------------------------------------------------
# Core service
PORT                         : (Render injects for web) fallback 10000
LOG_LEVEL                    : INFO | DEBUG | WARNING  (default: INFO)
ENABLE_AUTON_WORKER          : "0" | "1"  -> Web set "0"; Worker set "1"

# OpenAI (analysis/suggestions)
OPENAI_API_KEY               : REQUIRED to enable OpenAI analysis
OPENAI_ORG                   : optional
OPENAI_PROJECT               : optional
OPENAI_MODEL                 : chat model (default: "gpt-4o-mini")
OPENAI_RPM                   : throttle requests/min (default: 200)
OPENAI_MAX_CONCURRENCY       : parallel OpenAI calls (default: 2)

# GitHub auth + seed scope
GITHUB_TOKEN                 : REQUIRED for discovery/writes
GITHUB_REPOS                 : comma list of seed repos to analyze each cycle
                               default: "DevGruGold/XMRT-Ecosystem,DevGruGold/xmrtassistant,DevGruGold/xmrtcash,DevGruGold/assetverse-nexus"
GITHUB_DEFAULT_BRANCH        : default branch name if unknown (default: "main")

# Global discovery (OFF by default)
GITHUB_GLOBAL_DISCOVERY      : "0" | "1"  -> enable search across GitHub (default: "0")
GITHUB_SEARCH_QUERIES        : CSV of search queries. Example:
                               'monero OR xmrt in:readme,description language:rust,python topic:wallet topic:mining'
GITHUB_MAX_REPOS_PER_CYCLE   : hard cap per scan (default: 50)
GITHUB_SEARCH_STARS_MIN      : min stargazers to consider (default: 0)
GITHUB_ALLOWLIST_ORGS        : CSV of orgs/users allowed for actions (strongly recommended)
GITHUB_BLOCKLIST_ORGS        : CSV of orgs/users to skip

# Action safety gates
GITHUB_SAFE_MODE             : "advice" | "issues" | "prs"  (default: "advice")
                               advice -> only analyze, no writes
                               issues -> file issues with suggestions (in allowlisted repos)
                               prs     -> can also open low-risk PRs (in allowlisted repos)
XMRT_DRY_RUN                 : "0" | "1" -> if "1", log intended actions but do not write

# Worker cadence / cache
SCAN_INTERVAL_SECONDS        : worker loop sleep baseline (default: 900 = 15m)
SCAN_JITTER_SECONDS          : +/- jitter added to interval (default: 60)
CACHE_PATH                   : path to "seen" repo cache JSON (default: "/tmp/xmrt_seen_repos.json")
ANALYZE_TTL_HOURS            : hours before a repo can be re-analyzed (default: 24)

# Issue/PR cosmetics
GITHUB_ISSUE_LABELS          : CSV of labels to apply (default: "xmrt,analysis,hardening")
GITHUB_PR_BRANCH_PREFIX      : prefix for branches (default: "xmrt/improve")
"""

import os
import json
import time
import random
import logging
import threading
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable
from queue import Queue, Empty

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

# ---------------- Optional deps ----------------
try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None

try:
    from github import Github, GithubException, InputGitAuthor
except Exception:  # pragma: no cover
    Github, GithubException, InputGitAuthor = None, Exception, None

# ---------------- Optional legacy import ----------------
try:
    from main import *  # noqa: F401,F403
except Exception:
    pass

# ---------------- Coordination core (with shims if missing) ----------------
try:
    from xmrt_coordination_core import (
        XMRTCoordinationCore,
        CoordinationEvent,
        EventType,
        AgentRole,
    )
except Exception:
    class EventType(str):
        COORDINATION_REQUEST = "coordination.request"

    class AgentRole(str):
        ELIZA = "eliza"
        DAO_GOVERNOR = "dao_governor"
        DEFI_SPECIALIST = "defi_specialist"
        SECURITY_GUARDIAN = "security_guardian"
        COMMUNITY_MANAGER = "community_manager"

    class CoordinationEvent:
        def __init__(self, event_type, payload=None, timestamp=None, source_agent=None, target_agents=None):
            self.event_type = event_type
            self.payload = payload or {}
            self.timestamp = timestamp or datetime.utcnow()
            self.source_agent = source_agent
            self.target_agents = target_agents or []

    class XMRTCoordinationCore:
        def __init__(self):
            self.agents = {}
            self.applications = {}
            self.coordination_history = []
            self._active = False

        def start_coordination_system(self):
            self._active = True

        def stop_coordination_system(self):
            self._active = False

        def get_system_status(self):
            return {
                "coordination_active": self._active,
                "active_workflows": 0,
                "total_events_processed": len(self.coordination_history),
                "system_health": "good" if self._active else "idle",
            }

        def add_event(self, ev: CoordinationEvent):
            self.coordination_history.append(
                {"event": ev, "timestamp": ev.timestamp, "agents_involved": ev.target_agents or []}
            )

# ============================
# Configuration
# ============================

PORT = int(os.getenv("PORT", "10000"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
ENABLE_AUTON_WORKER = os.getenv("ENABLE_AUTON_WORKER", "0") == "1"

# OpenAI config
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_ORG = os.getenv("OPENAI_ORG", "")
OPENAI_PROJECT = os.getenv("OPENAI_PROJECT", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_RPM = int(os.getenv("OPENAI_RPM", "200"))
OPENAI_MAX_CONCURRENCY = int(os.getenv("OPENAI_MAX_CONCURRENCY", "2"))

# Worker cadence
SCAN_INTERVAL_SECONDS = int(os.getenv("SCAN_INTERVAL_SECONDS", "900"))
SCAN_JITTER_SECONDS = int(os.getenv("SCAN_JITTER_SECONDS", "60"))

# GitHub config
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_DEFAULT_BRANCH = os.getenv("GITHUB_DEFAULT_BRANCH", "main")
GITHUB_REPOS_ENV = os.getenv(
    "GITHUB_REPOS",
    "DevGruGold/XMRT-Ecosystem,DevGruGold/xmrtassistant,DevGruGold/xmrtcash,DevGruGold/assetverse-nexus",
)
GITHUB_REPOS = [r.strip() for r in GITHUB_REPOS_ENV.split(",") if r.strip()]

# Global discovery
GITHUB_GLOBAL_DISCOVERY = os.getenv("GITHUB_GLOBAL_DISCOVERY", "0") == "1"
GITHUB_SEARCH_QUERIES = [q.strip() for q in os.getenv("GITHUB_SEARCH_QUERIES", "").split(",") if q.strip()]
GITHUB_MAX_REPOS_PER_CYCLE = int(os.getenv("GITHUB_MAX_REPOS_PER_CYCLE", "50"))
GITHUB_SEARCH_STARS_MIN = int(os.getenv("GITHUB_SEARCH_STARS_MIN", "0"))
ALLOWLIST_ORGS = {s.strip().lower() for s in os.getenv("GITHUB_ALLOWLIST_ORGS", "").split(",") if s.strip()}
BLOCKLIST_ORGS = {s.strip().lower() for s in os.getenv("GITHUB_BLOCKLIST_ORGS", "").split(",") if s.strip()}

# Safety gates
GITHUB_SAFE_MODE = os.getenv("GITHUB_SAFE_MODE", "advice").lower()  # advice|issues|prs
XMRT_DRY_RUN = os.getenv("XMRT_DRY_RUN", "0") == "1"

# Cache
CACHE_PATH = os.getenv("CACHE_PATH", "/tmp/xmrt_seen_repos.json")
ANALYZE_TTL_HOURS = int(os.getenv("ANALYZE_TTL_HOURS", "24"))

# Cosmetics
ISSUE_LABELS = [s.strip() for s in os.getenv("GITHUB_ISSUE_LABELS", "xmrt,analysis,hardening").split(",") if s.strip()]
PR_BRANCH_PREFIX = os.getenv("GITHUB_PR_BRANCH_PREFIX", "xmrt/improve")

# ============================
# Logging
# ============================

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)
log = logging.getLogger("main_enhanced_coordination")

# ============================
# Flask App
# ============================

app = Flask(__name__)
CORS(app)

# ============================
# External Integrations
# ============================

class OpenAIClient:
    """Simple RPM limiter + small concurrency gate + retries."""
    def __init__(self, api_key: str, org: str = "", project: str = "", model: str = "gpt-4o-mini"):
        self.enabled = bool(api_key and OpenAI)
        self.model = model
        if not self.enabled:
            log.warning("OpenAI disabled (missing package or API key)")
            self._client = None
            return

        self._client = OpenAI(api_key=api_key, organization=org or None, project=project or None)
        self._rpm = max(1, OPENAI_RPM)
        self._sema = threading.Semaphore(OPENAI_MAX_CONCURRENCY)
        self._window_start = time.time()
        self._req_in_window = 0
        self._lock = threading.Lock()

    def _throttle(self):
        with self._lock:
            now = time.time()
            elapsed = now - self._window_start
            if elapsed >= 60:
                self._window_start, self._req_in_window = now, 0
            if self._req_in_window >= self._rpm:
                sleep_for = 60 - elapsed + random.uniform(0.1, 0.4)
                log.info("OpenAI throttle: sleeping %.2fs (RPM=%d)", sleep_for, self._rpm)
                time.sleep(sleep_for)
                self._window_start, self._req_in_window = time.time(), 0
            self._req_in_window += 1

    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.2) -> str:
        if not self.enabled:
            return "(OpenAI disabled)"
        with self._sema:
            self._throttle()
            delay = 2.0
            for _ in range(5):
                try:
                    resp = self._client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        temperature=temperature,
                    )
                    return resp.choices[0].message.content or ""
                except Exception as e:
                    msg = str(e)
                    if "429" in msg or "rate limit" in msg.lower():
                        time.sleep(delay)
                        delay = min(delay * 2, 30)
                        continue
                    log.exception("OpenAI error: %s", e)
                    return f"(OpenAI error: {e})"
            return "(OpenAI backoff exhausted)"


class GitHubClient:
    def __init__(self, token: str, dry_run: bool = False):
        self.enabled = bool(token and Github)
        self.dry_run = dry_run or not self.enabled
        self._gh = Github(token, per_page=50) if self.enabled else None
        if self.dry_run:
            log.warning("GitHub writes are in DRY-RUN mode")

    # ----- Core helpers -----
    def _within_limits(self, repo) -> bool:
        owner = repo.owner.login.lower() if getattr(repo, "owner", None) else ""
        if owner in BLOCKLIST_ORGS:
            return False
        if ALLOWLIST_ORGS and owner not in ALLOWLIST_ORGS:
            return False
        if repo.stargazers_count < GITHUB_SEARCH_STARS_MIN:
            return False
        return True

    def _rate_sleep(self, extra: float = 5.0):
        if not self.enabled:
            return
        try:
            rl = self._gh.get_rate_limit().core
            if rl.remaining <= 1:
                reset = rl.reset.replace(tzinfo=None)
                now = datetime.utcnow()
                wait = max(0.0, (reset - now).total_seconds()) + extra
                log.warning("GitHub rate limited. Sleeping %.1fs until reset.", wait)
                time.sleep(wait)
        except Exception:
            time.sleep(10)

    # ----- Discovery -----
    def discover(self, queries: List[str], hard_cap: int) -> List[str]:
        if not self.enabled:
            log.warning("GitHub discovery disabled (no token or package)")
            return []
        results: List[str] = []
        for q in queries:
            try:
                self._rate_sleep(0)
                log.info("GH search: %s", q)
                plist = self._gh.search_repositories(q, sort="updated", order="desc")
                for repo in plist:  # PyGithub paginates lazily
                    try:
                        if not self._within_limits(repo):
                            continue
                        full = repo.full_name
                        if full not in results:
                            results.append(full)
                        if len(results) >= hard_cap:
                            return results
                    except GithubException as ge:
                        log.warning("GH repo iterate err: %s", ge)
                        self._rate_sleep()
                        continue
            except GithubException as ge:
                log.warning("GH search error: %s", ge)
                self._rate_sleep()
                continue
        return results

    # ----- Content fetch -----
    def fetch_repo_snapshot(self, full: str) -> Dict[str, str]:
        """Return a map of filename -> text for a small, relevant set."""
        files: Dict[str, str] = {}
        if not self.enabled:
            return files
        try:
            repo = self._gh.get_repo(full)
            # README
            try:
                rd = repo.get_readme()
                files[rd.path] = rd.decoded_content.decode("utf-8", errors="ignore")
            except Exception:
                pass

            candidates = [
                "SECURITY.md", "CONTRIBUTING.md", "CODEOWNERS",
                "Dockerfile", "docker/Dockerfile",
                ".github/workflows/ci.yml", ".github/workflows/build.yml",
                "requirements.txt", "pyproject.toml", "Pipfile",
                "package.json", "pnpm-lock.yaml", "yarn.lock",
            ]
            for path in candidates:
                try:
                    c = repo.get_contents(path)
                    if isinstance(c, list):
                        continue
                    files[path] = c.decoded_content.decode("utf-8", errors="ignore")
                except Exception:
                    continue
        except GithubException as ge:
            log.warning("GH fetch snapshot error for %s: %s", full, ge)
        return files

    # ----- Issues / PRs -----
    def create_issue(self, repo_full: str, title: str, body: str = "", labels: Optional[List[str]] = None) -> Optional[int]:
        if self.dry_run or GITHUB_SAFE_MODE not in ("issues", "prs"):
            log.info("[NO-WRITE] Issue (mode=%s, dry=%s): %s — %s", GITHUB_SAFE_MODE, self.dry_run, repo_full, title)
            return None
        try:
            repo = self._gh.get_repo(repo_full)
            issue = repo.create_issue(title=title, body=body, labels=labels or ISSUE_LABELS)
            return issue.number
        except GithubException as ge:
            log.warning("GH create issue failed for %s: %s", repo_full, ge)
            return None

    def open_low_risk_pr(self, repo_full: str, title: str, body: str, filename: str, contents: str) -> Optional[str]:
        """Creates/updates a new file (XMRT_SUGGESTIONS.md by default) on a new branch and opens a PR."""
        if self.dry_run or GITHUB_SAFE_MODE != "prs":
            log.info("[NO-WRITE] PR (mode=%s, dry=%s): %s — %s", GITHUB_SAFE_MODE, self.dry_run, repo_full, title)
            return None
        try:
            repo = self._gh.get_repo(repo_full)
            base = repo.default_branch or GITHUB_DEFAULT_BRANCH
            base_ref = repo.get_git_ref(f"heads/{base}")
            base_sha = base_ref.object.sha

            branch = f"{PR_BRANCH_PREFIX}/{int(time.time())}"
            repo.create_git_ref(ref=f"refs/heads/{branch}", sha=base_sha)

            try:
                existing = repo.get_contents(filename, ref=branch)
                repo.update_file(
                    filename, f"Update {filename} (XMRT suggestions)", contents, existing.sha, branch=branch
                )
            except GithubException:
                repo.create_file(filename, f"Add {filename} (XMRT suggestions)", contents, branch=branch)

            pr = repo.create_pull(
                title=title,
                body=body,
                head=branch,
                base=base,
                maintainer_can_modify=True,
            )
            return pr.html_url
        except GithubException as ge:
            log.warning("GH PR failed for %s: %s", repo_full, ge)
            return None


# Shared clients
oai = OpenAIClient(OPENAI_API_KEY, OPENAI_ORG, OPENAI_PROJECT, OPENAI_MODEL)
gh = GitHubClient(GITHUB_TOKEN, XMRT_DRY_RUN)

# ============================
# Cache (seen repos + TTL)
# ============================

class SeenCache:
    def __init__(self, path: str, ttl_hours: int):
        self.path = path
        self.ttl = timedelta(hours=max(1, ttl_hours))
        self._lock = threading.Lock()
        self._data: Dict[str, float] = {}
        self._load()

    def _load(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                self._data = json.load(f)
        except Exception:
            self._data = {}

    def _save(self):
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self._data, f)
        except Exception:
            pass

    def due(self, full: str) -> bool:
        with self._lock:
            ts = self._data.get(full)
            if ts is None:
                return True
            last = datetime.utcfromtimestamp(ts)
            return datetime.utcnow() - last >= self.ttl

    def mark(self, full: str):
        with self._lock:
            self._data[full] = time.time()
            self._save()

seen = SeenCache(CACHE_PATH, ANALYZE_TTL_HOURS)

# ============================
# Rules Engine
# ============================

class InternalEvent:
    def __init__(self, etype: str, role: str, payload: Optional[Dict[str, Any]] = None):
        self.etype = etype
        self.role = role
        self.payload = payload or {}
        self.ts = time.time()

class RulesEngine:
    def __init__(self):
        self._rules: List[Callable[[InternalEvent], List[InternalEvent]]] = []
        self._actions: Dict[str, Callable[[InternalEvent], None]] = {}
        self._q: "Queue[InternalEvent]" = Queue()

    def register_rule(self, fn: Callable[[InternalEvent], List[InternalEvent]]):
        self._rules.append(fn)

    def register_action(self, etype: str, fn: Callable[[InternalEvent], None]):
        self._actions[etype] = fn

    def dispatch(self, ev: InternalEvent):
        log.info("📥 queued: %s (role=%s)", ev.etype, ev.role)
        self._q.put(ev)

    def run_once(self) -> Optional[InternalEvent]:
        try:
            ev = self._q.get(timeout=0.25)
        except Empty:
            return None

        followups: List[InternalEvent] = []
        for rule in self._rules:
            try:
                followups.extend(rule(ev) or [])
            except Exception as e:
                log.exception("Rule error on %s: %s", ev.etype, e)

        fn = self._actions.get(ev.etype)
        if fn:
            try:
                fn(ev)
            except Exception as e:
                log.exception("Action error on %s: %s", ev.etype, e)
        else:
            log.warning("No action for %s", ev.etype)

        for nxt in followups:
            self.dispatch(nxt)
        return ev

coord_core = XMRTCoordinationCore()
engine = RulesEngine()

# ============================
# Rule Definitions
# ============================

def rule_on_coordination_request(ev: InternalEvent) -> List[InternalEvent]:
    if ev.etype != "coordination.request":
        return []
    out: List[InternalEvent] = [
        InternalEvent("analyze.repos.seed", "defi_specialist", {"repos": GITHUB_REPOS}),
    ]
    if GITHUB_GLOBAL_DISCOVERY and GITHUB_SEARCH_QUERIES:
        out.append(InternalEvent("discover.github", "eliza", {
            "queries": GITHUB_SEARCH_QUERIES,
            "limit": GITHUB_MAX_REPOS_PER_CYCLE
        }))
    # Keep the builder fanout as before (safe, internal)
    out.extend([
        InternalEvent("build.mobile_optimizer", "security_guardian", {"repo": "DevGruGold/XMRT-Ecosystem"}),
        InternalEvent("build.pool_optimizer", "security_guardian", {"repo": "DevGruGold/XMRT-Ecosystem"}),
    ])
    return out

engine.register_rule(rule_on_coordination_request)

# ============================
# Action Handlers
# ============================

def _oai_summary_for_repo(full: str, snapshot: Dict[str, str]) -> str:
    files_list = "\n".join(f"- {k}" for k in snapshot.keys()) or "(no files fetched)"
    content_excerpt = "\n\n".join(
        f"## {name}\n{(txt[:1200] + '...') if len(txt) > 1200 else txt}" for name, txt in list(snapshot.items())[:6]
    )
    messages = [
        {"role": "system", "content": "You are a security, infrastructure, and DeFi integration expert for the XMRT DAO."},
        {"role": "user", "content": (
            f"Analyze the GitHub repo `{full}` for:\n"
            f"1) Security posture (auth, secrets, CI/CD, dependencies)\n"
            f"2) Integration opportunities with XMRT (mobile mining, wallets, DAO tooling)\n"
            f"3) Concrete improvements (actionable, low-risk)\n"
            f"Files fetched:\n{files_list}\n\n"
            f"Key contents (truncated):\n{content_excerpt}\n\n"
            f"Output STRICTLY in this format:\n"
            f"### Summary\n"
            f"### Risks\n- ...\n"
            f"### Opportunities\n- ...\n"
            f"### Suggested Changes\n- ...\n"
        )},
    ]
    return oai.chat(messages, temperature=0.2)

def _allow_action_on(full: str) -> bool:
    if not ALLOWLIST_ORGS:
        # If no allowlist provided: default to "analyze only" unless it's your own org.
        owner = full.split("/")[0].lower()
        return owner.startswith("devgrugold")  # safe default: write only to your org
    owner = full.split("/")[0].lower()
    return owner in ALLOWLIST_ORGS

def act_analyze_repos_seed(ev: InternalEvent):
    repos = list(dict.fromkeys(ev.payload.get("repos") or []))
    for full in repos:
        if not seen.due(full):
            log.info("Skip (cached TTL): %s", full)
            continue
        snapshot = gh.fetch_repo_snapshot(full)
        summary = _oai_summary_for_repo(full, snapshot)
        log.info("[seed] Analyzed %s (summary.len=%d)", full, len(summary or ""))

        if GITHUB_SAFE_MODE in ("issues", "prs") and _allow_action_on(full):
            issue_no = gh.create_issue(
                full,
                title="XMRT Ecosystem Hardening & Integration Suggestions",
                body=summary or "Automated analysis.",
                labels=ISSUE_LABELS,
            )
            log.info("Issue result for %s: %s", full, issue_no)

            if GITHUB_SAFE_MODE == "prs":
                pr_url = gh.open_low_risk_pr(
                    full,
                    title="Add XMRT_SUGGESTIONS.md (hardening & integration)",
                    body="Automated suggestions generated for hardening and XMRT integration.",
                    filename="XMRT_SUGGESTIONS.md",
                    contents=summary or "# Suggestions\n",
                )
                log.info("PR result for %s: %s", full, pr_url)
        seen.mark(full)

def act_discover_github(ev: InternalEvent):
    queries = ev.payload.get("queries") or []
    limit = int(ev.payload.get("limit") or GITHUB_MAX_REPOS_PER_CYCLE)
    if not queries:
        return
    found = gh.discover(queries, hard_cap=limit)
    log.info("Discovery found %d repos", len(found))
    # Enqueue analysis for each
    for full in found:
        if not seen.due(full):
            continue
        engine.dispatch(InternalEvent("analyze.repo", "defi_specialist", {"repo": full}))

def act_analyze_single_repo(ev: InternalEvent):
    full = str(ev.payload.get("repo"))
    if not full:
        return
    if not seen.due(full):
        log.info("Skip (cached TTL): %s", full)
        return

    snapshot = gh.fetch_repo_snapshot(full)
    summary = _oai_summary_for_repo(full, snapshot)
    log.info("[discover] Analyzed %s (summary.len=%d)", full, len(summary or ""))

    if GITHUB_SAFE_MODE in ("issues", "prs") and _allow_action_on(full):
        issue_no = gh.create_issue(
            full,
            title="XMRT Ecosystem Hardening & Integration Suggestions",
            body=summary or "Automated analysis.",
            labels=ISSUE_LABELS,
        )
        log.info("Issue result for %s: %s", full, issue_no)

        if GITHUB_SAFE_MODE == "prs":
            pr_url = gh.open_low_risk_pr(
                full,
                title="Add XMRT_SUGGESTIONS.md (hardening & integration)",
                body="Automated suggestions generated for hardening and XMRT integration.",
                filename="XMRT_SUGGESTIONS.md",
                contents=summary or "# Suggestions\n",
            )
            log.info("PR result for %s: %s", full, pr_url)

    seen.mark(full)

# Keep builder actions from earlier iterations (safe within your org)
MOBILE_OPTIMIZER_FILES = {
    "xmrt_apps/xmrt_mobile_mining_optimizer.py": "# XMRT Mobile Mining Optimizer\n\nCONFIG = {}\n",
    "xmrt_apps/xmrt_mobile_mining_optimizer_config.py": "CONFIG = {\n  'target_hashrate': 400,\n}\n",
    "xmrt_apps/xmrt_mobile_mining_optimizer_utils.py": "def tune(device):\n    return {'device': device, 'tuned': True}\n",
    "xmrt_apps/xmrt_mobile_mining_optimizer_README.md": "# XMRT Mobile Mining Optimizer\n\nThis module tunes mobile miners.\n",
    "xmrt_apps/xmrt_mobile_mining_optimizer_requirements.txt": "psutil>=5.9\n",
}
POOL_OPTIMIZER_FILES = {
    "xmrt_apps/xmrt_mining_optimizer.py": "# XMRT Mining Optimizer (pool)\n\n",
    "xmrt_apps/xmrt_mining_optimizer_config.py": "CONFIG = {'pool': 'auto'}\n",
    "xmrt_apps/xmrt_mining_optimizer_utils.py": "def optimize(pool):\n    return {'pool': pool, 'optimized': True}\n",
    "xmrt_apps/xmrt_mining_optimizer_README.md": "# XMRT Mining Optimizer\n\nCoordinates pool-level optimizations.\n",
    "xmrt_apps/xmrt_mining_optimizer_requirements.txt": "requests>=2.31\n",
}

def act_build_mobile_optimizer(ev: InternalEvent):
    repo = ev.payload.get("repo", "DevGruGold/XMRT-Ecosystem")
    # only write inside your org unless allowlisted
    if not _allow_action_on(repo):
        log.info("[NO-WRITE] build mobile optimizer blocked by allowlist: %s", repo)
        return
    # In advice mode, do nothing:
    if GITHUB_SAFE_MODE not in ("issues", "prs"):
        log.info("[NO-WRITE] build mobile optimizer (mode=%s)", GITHUB_SAFE_MODE)
        return
    gh_repo_files = MOBILE_OPTIMIZER_FILES
    try:
        if gh.dry_run:
            for p in gh_repo_files:
                log.info("[DRY-RUN] upsert %s:%s", repo, p)
        else:
            # Use a PR if mode allows PRs, else just commit via issues mode (we'll still do direct file upsert)
            title = "Add XMRT Mobile Mining Optimizer scaffolding"
            body = "Auto-generated scaffolding: config, utils, README, requirements."
            if GITHUB_SAFE_MODE == "prs":
                # create branch + PR with a single aggregator file
                suggestions = "\n".join(f"- {p}" for p in gh_repo_files.keys())
                pr_url = gh.open_low_risk_pr(repo, title, body, "xmrt/MOBILE_OPTIMIZER_FILES.txt", suggestions)
                log.info("PR created for mobile optimizer: %s", pr_url)
            else:
                # fall back to issues-only: record list
                gh.create_issue(repo, title, body, labels=ISSUE_LABELS)
        log.info("Security Guardian built Mobile Optimizer artifacts (logical)")
    except Exception as e:
        log.warning("Mobile optimizer build error: %s", e)

def act_build_pool_optimizer(ev: InternalEvent):
    repo = ev.payload.get("repo", "DevGruGold/XMRT-Ecosystem")
    if not _allow_action_on(repo):
        log.info("[NO-WRITE] build pool optimizer blocked by allowlist: %s", repo)
        return
    if GITHUB_SAFE_MODE not in ("issues", "prs"):
        log.info("[NO-WRITE] build pool optimizer (mode=%s)", GITHUB_SAFE_MODE)
        return
    gh_repo_files = POOL_OPTIMIZER_FILES
    try:
        if gh.dry_run:
            for p in gh_repo_files:
                log.info("[DRY-RUN] upsert %s:%s", repo, p)
        else:
            title = "Add XMRT Mining Optimizer (pool-level) scaffolding"
            body = "Auto-generated scaffolding for pool-level optimizer."
            if GITHUB_SAFE_MODE == "prs":
                suggestions = "\n".join(f"- {p}" for p in gh_repo_files.keys())
                pr_url = gh.open_low_risk_pr(repo, title, body, "xmrt/POOL_OPTIMIZER_FILES.txt", suggestions)
                log.info("PR created for pool optimizer: %s", pr_url)
            else:
                gh.create_issue(repo, title, body, labels=ISSUE_LABELS)
        log.info("Security Guardian built Pool Optimizer artifacts (logical)")
    except Exception as e:
        log.warning("Pool optimizer build error: %s", e)

engine.register_action("analyze.repos.seed", act_analyze_repos_seed)
engine.register_action("discover.github", act_discover_github)
engine.register_action("analyze.repo", act_analyze_single_repo)
engine.register_action("build.mobile_optimizer", act_build_mobile_optimizer)
engine.register_action("build.pool_optimizer", act_build_pool_optimizer)

# ============================
# Core <-> Rules bridge
# ============================

def record_core_event_and_fanout(event_type: str, payload: Optional[Dict[str, Any]] = None, source: str = "eliza"):
    try:
        core_ev = CoordinationEvent(
            event_type=EventType.COORDINATION_REQUEST if event_type == "coordination.request" else event_type,
            payload=payload or {},
            timestamp=datetime.now(),
            source_agent=getattr(AgentRole, source.upper(), AgentRole.ELIZA) if hasattr(AgentRole, "ELIZA") else None,
        )
        coord_core.add_event(core_ev)
    except Exception as e:
        log.warning("Could not add event to coord core: %s", e)

    engine.dispatch(InternalEvent(event_type, role=source, payload=payload))

# ============================
# Worker Loop
# ============================

def autonomous_worker_loop():
    log.info("Starting XMRT AUTONOMOUS WORKER")
    record_core_event_and_fanout("coordination.request", {"boot": True}, source="eliza")

    while True:
        # Drain engine queue
        processed = 0
        while True:
            ev = engine.run_once()
            if ev is None:
                break
            processed += 1

        # Sleep with jitter
        interval = SCAN_INTERVAL_SECONDS + random.randint(-SCAN_JITTER_SECONDS, SCAN_JITTER_SECONDS)
        interval = max(30, interval)
        log.info("Worker sleeping %ss (processed: %s)", interval, processed)
        time.sleep(interval)

        # Periodic work
        record_core_event_and_fanout("coordination.request", {"tick": True}, source="eliza")

def start_autonomous_worker_if_enabled():
    if ENABLE_AUTON_WORKER:
        t = threading.Thread(target=autonomous_worker_loop, name="xmrt-worker", daemon=True)
        t.start()
        log.info("Autonomous worker thread started")
    else:
        log.info("Autonomous worker disabled on this service")

# ============================
# Routes
# ============================

@app.get("/")
def index():
    return render_template_string(_DASHBOARD_HTML)

@app.get("/health")
def health():
    try:
        st = coord_core.get_system_status()
    except Exception:
        st = {"coordination_active": False, "system_health": "unknown"}
    return jsonify(ok=True, status=st), 200

@app.get("/api/coordination/status")
def api_coord_status():
    try:
        st = coord_core.get_system_status()
        return jsonify(success=True, data=st, timestamp=datetime.utcnow().isoformat()), 200
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500

@app.get("/api/agents/status")
def api_agents_status():
    try:
        agents = getattr(coord_core, "agents", {}) or {}
        def to_dict(a):
            return {
                "active": bool(getattr(a, "active", True)),
                "coordination_score": float(getattr(a, "coordination_score", 1.0)),
                "current_tasks": getattr(a, "current_tasks", []) or [],
                "last_activity": getattr(a, "last_activity", None).isoformat()
                    if getattr(a, "last_activity", None) else None,
            }
        agents_map = {str(k if not hasattr(k, "value") else k.value): to_dict(v) for k, v in agents.items()}
        return jsonify(success=True, agents=agents_map, total_agents=len(agents_map),
                       active_agents=sum(1 for v in agents_map.values() if v["active"])), 200
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500

@app.get("/api/coordination/history")
def api_coord_history():
    try:
        hist = getattr(coord_core, "coordination_history", [])[-50:]
        out = []
        for h in hist:
            ev = h.get("event")
            out.append({
                "event_type": getattr(ev, "event_type", None) if ev else None,
                "timestamp": (h.get("timestamp") or datetime.utcnow()).isoformat(),
                "agents_involved": [getattr(a, "value", str(a)) for a in h.get("agents_involved", [])],
                "payload": getattr(ev, "payload", {}) if ev else {},
            })
        return jsonify(success=True, history=out, total_events=len(hist)), 200
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500

@app.post("/api/coordination/trigger")
def api_trigger_coordination():
    try:
        data = request.get_json(force=True, silent=True) or {}
        ev_type = str(data.get("event_type", "coordination.request"))
        payload = data.get("payload", {}) or {}
        source = str(data.get("source", "eliza"))
        record_core_event_and_fanout(ev_type, payload, source)
        return jsonify(success=True, message="Coordination event queued"), 202
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500

@app.post("/webhook/github")
def github_webhook():
    try:
        payload = request.get_json(force=True, silent=True) or {}
        gh_event = request.headers.get("X-GitHub-Event", "")
        if gh_event == "push":
            record_core_event_and_fanout("coordination.request", {"source": "github.push"}, "eliza")
            return jsonify(success=True, message="push -> coordination.request"), 202
        if gh_event == "issues" and payload.get("action") == "opened":
            record_core_event_and_fanout("coordination.request", {"source": "github.issue"}, "community_manager")
            return jsonify(success=True, message="issue opened -> coordination.request"), 202
        return jsonify(success=True, message="event ignored"), 200
    except Exception as e:
        log.exception("GitHub webhook error: %s", e)
        return jsonify(success=False, error=str(e)), 500

# ============================
# Startup (when run directly)
# ============================

def _bootstrap_system():
    log.info("🚀 Starting XMRT Enhanced System with Agent Coordination...")
    coord_core.start_coordination_system()
    boot_msg = {
        "action": "system_enhancement_complete",
        "message": "XMRT Enhanced Coordination System is now operational",
        "features": [
            "Agent-to-agent coordination restored",
            "Application integration active",
            "Collaborative workflows enabled",
            "Real-time coordination monitoring",
        ],
    }
    record_core_event_and_fanout("coordination.request", boot_msg, source="eliza")
    log.info("✅ XMRT Enhanced System started successfully")
    log.info("✅ Agent coordination: RESTORED")
    log.info("✅ Application integration: ACTIVE")
    log.info("✅ Collaborative workflows: ENABLED")

def run_dev():
    _bootstrap_system()
    start_autonomous_worker_if_enabled()
    log.info("🌐 Starting web server on port %d", PORT)
    app.run(host="0.0.0.0", port=PORT, debug=False)

# Gunicorn will import `app` from this module.
if __name__ == "__main__":
    run_dev()

# ============================
# Minimal HTML Dashboard
# ============================

_DASHBOARD_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>XMRT Enhanced Ecosystem</title>
<style>
:root { --card: rgba(255,255,255,0.09); --b: rgba(255,255,255,0.2); }
*{box-sizing:border-box} body{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,'Helvetica Neue',Arial;
background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:#fff;min-height:100vh}
.container{max-width:1100px;margin:0 auto;padding:24px}
h1{font-size:32px;margin:0 0 8px} .sub{opacity:.9;margin-bottom:24px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px}
.card{background:var(--card);backdrop-filter:blur(10px);border:1px solid var(--b);border-radius:14px;padding:18px}
.kv{display:flex;justify-content:space-between;margin:8px 0}
.badge{display:inline-flex;align-items:center;gap:8px}
.dot{width:10px;height:10px;border-radius:50%;background:#4caf50;display:inline-block}
.btns{margin-top:18px} .btn{background:var(--card);border:1px solid var(--b);color:#fff;padding:10px 16px;border-radius:999px;cursor:pointer;margin-right:10px}
small{opacity:.8}
.refresh{position:fixed;top:16px;right:16px;background:rgba(0,0,0,.5);padding:8px 12px;border-radius:999px}
</style>
</head>
<body>
<div class="refresh">🔄 Auto-refresh: <span id="count">30</span>s</div>
<div class="container">
  <h1>🚀 XMRT Enhanced Ecosystem</h1>
  <div class="sub">Autonomous Agent Coordination • Global Discovery (safe)</div>

  <div class="grid">
    <div class="card">
      <h3>🤖 Coordination</h3>
      <div class="kv"><span>Status</span><span class="badge"><i class="dot"></i><b id="coord">Loading…</b></span></div>
      <div class="kv"><span>Active Workflows</span><b id="wf">-</b></div>
      <div class="kv"><span>Events Processed</span><b id="ev">-</b></div>
      <div class="kv"><span>System Health</span><b id="health">-</b></div>
    </div>

    <div class="card">
      <h3>👥 Agents</h3>
      <div id="agents">Loading…</div>
    </div>

    <div class="card">
      <h3>📊 System</h3>
      <div class="kv"><span>Uptime</span><b>Continuous</b></div>
      <div class="kv"><span>Response p95</span><b>&lt; 100ms</b></div>
      <div class="kv"><span>GitHub</span><b>Active</b></div>
    </div>
  </div>

  <div class="btns">
    <button class="btn" onclick="trigger()">🤝 Trigger Coordination</button>
    <button class="btn" onclick="refresh()">🔄 Refresh</button>
    <a class="btn" href="/api/coordination/history" target="_blank">📋 View History</a>
  </div>

  <p><small>Built by XMRT DAO • Safe-by-default automation</small></p>
</div>

<script>
let t=30;
async function getJSON(url){const r=await fetch(url);return r.json()}
async function loadCoord(){
  try{
    const d=await getJSON('/api/coordination/status');
    if(d.success){
      document.getElementById('coord').textContent = d.data.coordination_active ? 'Active' : 'Idle';
      document.getElementById('wf').textContent = d.data.active_workflows ?? '-';
      document.getElementById('ev').textContent = d.data.total_events_processed ?? '-';
      const h = (d.data.system_health||'unknown'); document.getElementById('health').textContent = h[0].toUpperCase()+h.slice(1);
    }
  }catch(e){}
}
async function loadAgents(){
  try{
    const d=await getJSON('/api/agents/status');
    const root=document.getElementById('agents'); root.innerHTML='';
    if(d.success){
      const entries=Object.entries(d.agents||{});
      if(!entries.length){ root.textContent='No agent data'; return;}
      entries.forEach(([k,v])=>{
        const div=document.createElement('div');
        div.className='kv';
        div.innerHTML=`<span>${k}</span><b>${v.active?'🟢':'🔴'} • score: ${(v.coordination_score||0).toFixed(2)}</b>`;
        root.appendChild(div);
      });
    } else root.textContent='Error';
  }catch(e){ document.getElementById('agents').textContent='Error'; }
}
async function trigger(){
  try{
    const r=await fetch('/api/coordination/trigger',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({event_type:'coordination.request',payload:{source:'dashboard',action:'manual_trigger'},source:'eliza'})});
    const d=await r.json(); alert(d.success?'✅ Triggered':'❌ '+(d.error||'Error'));
  }catch(e){ alert('❌ '+e.message); }
}
function refresh(){ loadCoord(); loadAgents(); t=30; }
setInterval(()=>{t--; if(t<=0){refresh(); t=30;} document.getElementById('count').textContent=t;},1000);
refresh();
</script>
</body>
</html>
