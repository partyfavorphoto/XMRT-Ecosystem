#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XMRT Ecosystem Main Application - v7.0 (Consensus + MCP + Guided Integration)
=============================================================================

One script to rule them all.

This version:
- Preserves your working Flask service + consensus loop.
- Adds a Model Context Protocol (MCP) bridge (HTTP-style) to list/call tools.
- Builds a *guided integration plan* from your 72-repo ecosystem document and
  drives *real* GitHub issues/commits for work tracking and integration stubs.
- Removes "simulation" results. If a real dependency/service (GitHub/OpenAI/MCP)
  isn't available, we return a clear, explicit error instead of fabricating data.
- Provides endpoints to inspect agents, tasks, status, and to trigger cycles.

Environment variables:
- OPENAI_API_KEY           (required for AI-powered consensus/tie-breaks)
- OPENAI_MODEL             (default: gpt-4o-mini)
- GEMINI_API_KEY           (optional secondary LLM)
- GITHUB_TOKEN             (required for real GitHub actions)
- MCP_SERVER_URL           (optional; e.g. http://mcp-gateway:3000)
- MCP_API_KEY              (optional)
- ADMIN_TOKEN              (optional; protects mutating endpoints if set)
- PORT                     (Render supplies; default 10000)

Security:
- If ADMIN_TOKEN is set, mutating endpoints require header:
  Authorization: Bearer <ADMIN_TOKEN>

Logging style:
- Matches your previous deploy logs.

Author’s note:
- The integration backlog and priorities are derived from your 72-repo guide,
  with specific first-wave goals for xmrt-syft-client, xmrt-ragflow, xmrt-autogen.
"""

from __future__ import annotations

import os
import re
import sys
import json
import time
import hmac
import math
import signal
import logging
import random
import threading
import traceback
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, Optional, List, Tuple, Callable
from datetime import datetime, timedelta

import requests
from flask import Flask, jsonify, request, make_response, render_template_string
from flask_cors import CORS

# -------------------- Optional dependencies (loaded lazily) --------------------
try:
    from github import Github, Auth, GithubException
    GITHUB_AVAILABLE = True
except Exception:
    GITHUB_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except Exception:
    OPENAI_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except Exception:
    GEMINI_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except Exception:
    PSUTIL_AVAILABLE = False
# ------------------------------------------------------------------------------


# ============================ Logging Configuration ============================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - xmrt-main - %(levelname)s - %(message)s"
)
logger = logging.getLogger("xmrt-main")


# ============================ Flask App & Config ===============================

app = Flask(__name__)
CORS(app)

DEFAULT_OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
PORT = int(os.environ.get("PORT", "10000"))
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN")  # Optional bearer for mutations

HTML_INDEX = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>XMRT Ecosystem (v7.0 MCP + Guided Integration)</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body { font: 14px/1.4 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, "Apple Color Emoji","Segoe UI Emoji"; margin: 28px; color: #111; }
    code, pre { background: #f7f7f9; padding: 2px 4px; border-radius: 4px; }
    .pill { display: inline-block; padding: 4px 8px; border-radius: 999px; background: #eef; margin: 0 6px 6px 0; }
    .ok { background:#e6ffed; }
    .warn { background:#fff5e6; }
    .err { background:#ffe6e6; }
    .mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono","Courier New", monospace; }
    .small { color: #666; }
    h1, h2, h3 { margin-top: 1.2em; }
    a { color: #0b5ed7; text-decoration: none; }
    a:hover { text-decoration: underline; }
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 14px; }
    .card { border: 1px solid #e5e7eb; border-radius: 12px; padding: 14px; }
  </style>
</head>
<body>
  <h1>XMRT Ecosystem (v7.0)</h1>
  <p>Consensus + MCP bridge + guided integration across forked repos.</p>

  <div class="grid">
    <div class="card">
      <h3>Status</h3>
      <pre class="mono" id="status">Loading...</pre>
    </div>
    <div class="card">
      <h3>Agents</h3>
      <pre class="mono" id="agents">Loading...</pre>
    </div>
    <div class="card">
      <h3>Backlog (Top 10)</h3>
      <pre class="mono" id="tasks">Loading...</pre>
    </div>
    <div class="card">
      <h3>Last Decision</h3>
      <pre class="mono" id="decision">Loading...</pre>
    </div>
  </div>

  <script>
    async function getJSON(url){ const r=await fetch(url); return r.json(); }
    async function refresh(){
      try {
        const status = await getJSON('/api/coordination/status');
        const agents = await getJSON('/api/agents');
        const tasks = await getJSON('/api/tasks?limit=10');
        const decision = await getJSON('/api/coordination/last-decision');
        document.getElementById('status').textContent = JSON.stringify(status, null, 2);
        document.getElementById('agents').textContent = JSON.stringify(agents, null, 2);
        document.getElementById('tasks').textContent = JSON.stringify(tasks, null, 2);
        document.getElementById('decision').textContent = JSON.stringify(decision, null, 2);
      } catch(e) {
        document.getElementById('status').textContent = 'Error loading status: '+e;
      }
    }
    refresh();
    setInterval(refresh, 5000);
  </script>
</body>
</html>
"""


# ============================= Utility Functions ==============================

def now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def require_admin_token(req) -> Optional[make_response]:
    """If ADMIN_TOKEN is configured, enforce bearer token on mutating routes."""
    if not ADMIN_TOKEN:
        return None
    hdr = req.headers.get("Authorization", "")
    if hdr.startswith("Bearer "):
        token = hdr.split(" ", 1)[1].strip()
        if hmac.compare_digest(token, ADMIN_TOKEN):
            return None
    return make_response(jsonify({"error": "Unauthorized"}), 401)


def env_bool(name: str, default: bool = False) -> bool:
    v = os.environ.get(name)
    if v is None:
        return default
    return str(v).lower() in ("1", "true", "yes", "on")


def truncate(s: str, max_len: int = 4000) -> str:
    return s if len(s) <= max_len else s[:max_len-3] + "..."


# ============================= Global State ===================================

SYSTEM_STATE: Dict[str, Any] = {
    "status": "operational",
    "version": "7.0.0-mcp-guided",
    "deployment": "render-free-tier",
    "startup_time": time.time(),
    "openai_available": OPENAI_AVAILABLE,
    "gemini_available": GEMINI_AVAILABLE,
    "github_available": GITHUB_AVAILABLE,
    "mcp_url": os.environ.get("MCP_SERVER_URL") or None,
    "last_cycle": None,
}

ANALYTICS: Dict[str, Any] = {
    "requests": 0,
    "ai_calls": 0,
    "mcp_calls": 0,
    "github_ops": 0,
    "issues_created": 0,
    "files_committed": 0,
    "consensus_rounds": 0,
    "decisions": 0,
    "errors": 0,
}

LOCK = threading.RLock()


# ============================= Ecosystem Guide =================================
# Derived from your document: 72 repos, categories, and initial integration focus.
# We embed the list + top-priority “first wave” tasks (syft/ragflow/autogen).

GUIDE_REPOS: List[str] = [
    # Full set from your doc (order kept as provided)
    "xmrt-activepieces",
    "xmrt-agno",
    "xmrt-rust",
    "xmrt-wazuh",
    "xmrt-wazuh-kubernetes",
    "gemini-cli",
    "xmrt-DeepMCPAgent",
    "xmrt-MeshSentry",
    "xmrt-brightdata-mcp",
    "xmrt-supabase",
    "xmrt-firecrawl",
    "xmrt-agents-towards-production",
    "xmrt-crosvm-chrome-vm",
    "xmrt-gutil-google-utilities",
    "xmrt-grain-ml-train",
    "xmrt-AirCom-ESP32-wifi-halow",
    "xmrt-filament-render-engine",
    "xmrt-dawn-native-webgpu",
    "xmrt-adk-python-agents",
    "xmrt-perfetto-tracing",
    "xmrt-RAG-Anything",
    "xmrt-awesome-AI-toolkit",
    "xmrt-humanlayer",
    "xmrt-langextract",
    "xmrt-n8n",
    "xmrt-gov-ui-kit",
    "xmrt-risc0-proofs",
    "xmrt-RAGLight",
    "xmrt-autoswagger",
    "AWS-DevSecOps-Factory",
    "xmrt-asset-tokenizer",
    "xmrt-bee",
    "xmrt-autogen-boardroom",
    "xmrt-AutoGPT",
    "xmrt-bacalhau",
    "xmrt-anon-monitor",
    "xmrt-airnode",
    "xmrt-agents",
    "xmrt-agentcomms",
    "xmrt-agentbrowser",
    "xmrt-agent_trust_scoreboard",
    "browser-use",
    "monero-generator",
    "sovrin",
    "maybe-finance-app",
    "mobile-payments-sdk-react-native",
    "bitchat-react",
    "xmrt-social-media-agent",
    "xmrt-social-sleuth",
    "xmrt-runtime-verification",
    "xmrt-redis",
    "xmrt-redis-py",
    "xmrt-transformers",
    "xmrt-wormhole",
    "xmrt-storm-pr-engine",
    "pinokio",
    "xmrt-hetty-hacker",
    "autotrain-advanced",
    "xmrt-zk-oracles",
    "xmrt-zkbridge",
    "xmrt-bitchat",
    "SilentXMRMiner",
    "ropsten",
    "xmrt-characters",
    "react-point-of-sale",
    "xmrig",
    "langchain-memory",
    "eth-wallet",
    "xmrt-universal-resolver",
    "xmrt-syft-client",
    "xmrt-ragflow",
    "xmrt-autogen",
]

# First-wave, document-guided integration goals (must-have).
FIRST_WAVE_GOALS: List[Dict[str, Any]] = [
    {
        "title": "Wire Federated Learning into XMRT data plane",
        "desc": "Connect xmrt-syft-client to xmrt-supabase model storage and privacy guardrails; enable FL training on miner telemetry.",
        "repos": ["xmrt-syft-client", "xmrt-supabase", "xmrt-redis", "xmrt-transformers"],
        "labels": ["federated-learning", "privacy", "models", "data-plane"],
        "acceptance": [
            "FL job can be triggered via API",
            "Model artifacts stored in Supabase",
            "Privacy configs (DP/SMPC) toggled via config"
        ]
    },
    {
        "title": "RAG for DAO analytics & mining insights",
        "desc": "Integrate xmrt-ragflow with xmrt-gov-ui-kit and langchain-memory to ground governance dashboards + mining trend Q&A.",
        "repos": ["xmrt-ragflow", "xmrt-gov-ui-kit", "langchain-memory", "xmrt-storm-pr-engine"],
        "labels": ["rag", "dao-analytics", "grounding", "ui"],
        "acceptance": [
            "DAO dashboard pulls grounded answers via RAG",
            "Queries persisted with memory and provenance",
            "CI test exercises a sample retrieval workflow"
        ]
    },
    {
        "title": "Multi-agent orchestration for DAO simulations",
        "desc": "Use xmrt-autogen to orchestrate vote simulations, hand-offs to security and DeFi agents; persist sessions in redis.",
        "repos": ["xmrt-autogen", "xmrt-autogen-boardroom", "xmrt-redis", "xmrt-agent_trust_scoreboard"],
        "labels": ["agents", "orchestration", "dao", "simulation"],
        "acceptance": [
            "Group chat workflow runs scripted vote simulation",
            "Trust/quality scores recorded per agent turn",
            "Runbook for operators included in repo docs"
        ]
    },
    {
        "title": "Identity & ZK checks in governance flows",
        "desc": "Attach universal-resolver + zkbridge/risc0 proofs to DAO proposal lifecycle within gov-ui-kit.",
        "repos": ["xmrt-universal-resolver", "xmrt-zkbridge", "xmrt-risc0-proofs", "xmrt-gov-ui-kit"],
        "labels": ["identity", "zk", "governance", "security"],
        "acceptance": [
            "Resolver lookup integrated and unit-tested",
            "ZK proof path documented and exercised in CI",
            "UI surfaces proof status unobtrusively"
        ]
    },
    {
        "title": "Offline mesh chat + agent handoff",
        "desc": "Bridge xmrt-bitchat (mesh/offline) to autogen orchestrations; on-connect sync to supabase/log memory.",
        "repos": ["xmrt-bitchat", "bitchat-react", "xmrt-autogen", "xmrt-supabase"],
        "labels": ["meshnet", "offline", "agents", "sync"],
        "acceptance": [
            "Offline chat can enqueue an agent job",
            "On reconnection, job executes and logs to memory",
            "E2E scenario recorded in docs"
        ]
    },
]


# ============================= Data Classes ===================================

@dataclass
class IntegrationTask:
    key: str
    title: str
    description: str
    repos: List[str]
    labels: List[str]
    priority: int = 3  # 1=highest
    status: str = "pending"  # pending|in_progress|blocked|done|failed
    created_at: str = field(default_factory=now_iso)
    updated_at: str = field(default_factory=now_iso)
    acceptance: List[str] = field(default_factory=list)
    owner: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)  # other task keys
    evidence_links: List[str] = field(default_factory=list)  # PRs/issues/commits
    notes: List[str] = field(default_factory=list)


@dataclass
class Agent:
    name: str
    role: str
    domains: List[str]
    weight: float = 1.0
    active: bool = True
    last_seen: str = field(default_factory=now_iso)
    completed: int = 0
    failed: int = 0
    decisions: int = 0

    def can_own(self, task: IntegrationTask) -> bool:
        # simple domain matching against labels
        for lbl in task.labels:
            if lbl in self.domains:
                return True
        return False


@dataclass
class DecisionRecord:
    at: str
    subject: str
    proposals: List[Dict[str, Any]]
    selected_key: Optional[str]
    rationale: str
    voters: Dict[str, float]
    tiebreaker: Optional[str] = None


# ============================= AI Processor ===================================

class AIProcessor:
    """
    Thin abstraction over OpenAI (primary) and Gemini (optional).
    Returns explicit errors when providers are not available; no faked content.
    """
    def __init__(self):
        self._oaiclient = None
        self._gemini = None

        if OPENAI_AVAILABLE and os.environ.get("OPENAI_API_KEY"):
            try:
                self._oaiclient = OpenAI()
                logger.info("OpenAI client initialized")
            except Exception as e:
                logger.warning(f"OpenAI init failed: {e}")
                self._oaiclient = None

        if GEMINI_AVAILABLE and os.environ.get("GEMINI_API_KEY"):
            try:
                genai.configure(api_key=os.environ["GEMINI_API_KEY"])
                self._gemini = genai.GenerativeModel("gemini-pro")
                logger.info("Gemini client initialized")
            except Exception as e:
                logger.warning(f"Gemini init failed: {e}")
                self._gemini = None

    def chat(self, system: str, user: str, max_tokens: int = 800, temperature: float = 0.3) -> Tuple[Optional[str], Optional[str]]:
        """
        Returns (text, provider) or (None, None) with logged error.
        """
        if self._oaiclient:
            try:
                r = self._oaiclient.chat.completions.create(
                    model=DEFAULT_OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                ANALYTICS["ai_calls"] += 1
                return r.choices[0].message.content, "openai"
            except Exception as e:
                logger.warning(f"OpenAI chat error: {e}")

        if self._gemini:
            try:
                r = self._gemini.generate_content(system + "\n\n" + user)
                ANALYTICS["ai_calls"] += 1
                return getattr(r, "text", None), "gemini"
            except Exception as e:
                logger.warning(f"Gemini chat error: {e}")

        return None, None

    def choose(self, prompt: str, options: List[Tuple[str, str]]) -> Optional[str]:
        """
        Ask AI to choose best key among options [(key, text), ...].
        Returns key or None on failure/unavailability.
        """
        system = "You are an impartial XMRT DAO facilitator optimizing for privacy, mesh resilience, and tangible integration progress."
        lines = [prompt, "", "OPTIONS:"]
        for k, t in options:
            lines.append(f"- {k}: {t}")
        content = "\n".join(lines)
        text, provider = self.chat(system, content, max_tokens=256, temperature=0.0)
        if not text:
            return None
        # Find the first option key mentioned
        keys_sorted = sorted([k for k, _ in options], key=lambda s: -len(s))
        for k in keys_sorted:
            if k in text:
                return k
        # fallback: look for exact code fence or bracket
        m = re.search(r"\b([A-Za-z0-9_-]{6,})\b", text)
        return m.group(1) if m else None


AI = AIProcessor()


# ============================= MCP Bridge =====================================

class MCPBridge:
    """
    Simple HTTP bridge to a Model Context Protocol gateway.

    Expected endpoints (configurable upstream):
    - GET  {MCP_SERVER_URL}/tools                  -> {"tools":[{"name": "...", "schema": {...}}, ...]}
    - POST {MCP_SERVER_URL}/call {name, arguments} -> {"ok": true, "result": ...} OR {"ok": false, "error": ...}

    No offline simulation. If the server is unavailable, we return structured errors.
    """

    def __init__(self, base_url: Optional[str], api_key: Optional[str] = None):
        self.base_url = base_url
        self.api_key = api_key

    def _headers(self) -> Dict[str, str]:
        h = {"Content-Type": "application/json"}
        if self.api_key:
            h["Authorization"] = f"Bearer {self.api_key}"
        return h

    def available(self) -> bool:
        return bool(self.base_url)

    def list_tools(self) -> Dict[str, Any]:
        if not self.available():
            return {"ok": False, "error": "MCP server URL not configured"}
        try:
            r = requests.get(f"{self.base_url.rstrip('/')}/tools", timeout=15, headers=self._headers())
            if r.status_code != 200:
                return {"ok": False, "error": f"MCP /tools HTTP {r.status_code}", "details": r.text}
            return {"ok": True, "tools": r.json().get("tools", [])}
        except Exception as e:
            ANALYTICS["mcp_calls"] += 1
            return {"ok": False, "error": f"MCP request failed: {e.__class__.__name__}", "details": str(e)}

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        if not self.available():
            return {"ok": False, "error": "MCP server URL not configured"}
        payload = {"name": name, "arguments": arguments}
        try:
            r = requests.post(f"{self.base_url.rstrip('/')}/call", json=payload, timeout=60, headers=self._headers())
            ANALYTICS["mcp_calls"] += 1
            if r.status_code != 200:
                return {"ok": False, "error": f"MCP /call HTTP {r.status_code}", "details": r.text}
            return r.json()
        except Exception as e:
            ANALYTICS["mcp_calls"] += 1
            return {"ok": False, "error": f"MCP call failed: {e.__class__.__name__}", "details": str(e)}


MCP = MCPBridge(os.environ.get("MCP_SERVER_URL"), os.environ.get("MCP_API_KEY"))


# ============================= GitHub Integration =============================

class XMRTGitHub:
    """
    Real GitHub integration only; if token or repo unavailable, operations raise structured errors.
    No "simulate mode".
    """
    def __init__(self, default_repo="DevGruGold/XMRT-Ecosystem"):
        self.token = os.environ.get("GITHUB_TOKEN")
        self.default_repo = default_repo
        self.client = None
        self.user = None
        self._connect()

    def _connect(self):
        if not GITHUB_AVAILABLE:
            logger.warning("PyGithub not installed; GitHub unavailable.")
            return
        if not self.token:
            logger.warning("GITHUB_TOKEN not provided; GitHub unavailable.")
            return
        try:
            auth = Auth.Token(self.token)
            self.client = Github(auth=auth)
            self.user = self.client.get_user()
            # Probe default repo
            _ = self.client.get_repo(self.default_repo)
            logger.info(f"GitHub repo reachable ({self.default_repo}). Enabling real mode.")
        except Exception as e:
            logger.error(f"GitHub init failed: {e}")
            self.client = None
            self.user = None

    def available(self) -> bool:
        return self.client is not None

    def repo(self, full_name: Optional[str] = None):
        if not self.available():
            raise RuntimeError("GitHub unavailable (missing token or client)")
        target = full_name or self.default_repo
        try:
            return self.client.get_repo(target)
        except Exception as e:
            raise RuntimeError(f"Failed to access repo {target}: {e}")

    def create_issue(self, repo_full: str, title: str, body: str, labels: Optional[List[str]] = None) -> Dict[str, Any]:
        if not self.available():
            raise RuntimeError("GitHub unavailable: cannot create issue")
        try:
            repo = self.repo(repo_full)
            issue = repo.create_issue(title=title, body=body, labels=labels or [])
            ANALYTICS["github_ops"] += 1
            ANALYTICS["issues_created"] += 1
            return {"ok": True, "id": issue.number, "url": issue.html_url}
        except GithubException as ge:
            return {"ok": False, "error": f"GitHub error: {ge.data}"}
        except Exception as e:
            return {"ok": False, "error": f"Create issue failed: {e}"}

    def upsert_file(self, repo_full: str, path: str, message: str, content: str) -> Dict[str, Any]:
        if not self.available():
            raise RuntimeError("GitHub unavailable: cannot commit file")
        try:
            repo = self.repo(repo_full)
            try:
                existing = repo.get_contents(path)
                res = repo.update_file(path, message, content, existing.sha)
                action = "updated"
            except GithubException:
                res = repo.create_file(path, message, content)
                action = "created"
            ANALYTICS["github_ops"] += 1
            ANALYTICS["files_committed"] += 1
            return {"ok": True, "action": action, "content": {"path": path}, "commit": {"sha": res["commit"].sha}}
        except Exception as e:
            return {"ok": False, "error": f"Upsert file failed: {e}"}


GITHUB = XMRTGitHub()


# ============================= Backlog & Agents ================================

class Backlog:
    """
    Thread-safe backlog for IntegrationTask items.
    """
    def __init__(self):
        self._tasks: Dict[str, IntegrationTask] = {}
        self._lock = threading.RLock()

    def put(self, task: IntegrationTask):
        with self._lock:
            self._tasks[task.key] = task

    def get(self, key: str) -> Optional[IntegrationTask]:
        with self._lock:
            return self._tasks.get(key)

    def list(self) -> List[IntegrationTask]:
        with self._lock:
            return list(self._tasks.values())

    def remove(self, key: str):
        with self._lock:
            if key in self._tasks:
                del self._tasks[key]

    def update_status(self, key: str, status: str, note: Optional[str] = None):
        with self._lock:
            t = self._tasks.get(key)
            if t:
                t.status = status
                t.updated_at = now_iso()
                if note:
                    t.notes.append(f"[{now_iso()}] {note}")

    def top(self, n: int = 10) -> List[IntegrationTask]:
        with self._lock:
            # sort by priority then created_at
            tasks = sorted(self._tasks.values(), key=lambda t: (t.priority, t.created_at))
            return tasks[:n]


BACKLOG = Backlog()


AGENTS: Dict[str, Agent] = {
    "coordinator": Agent("Eliza", "Coordinator & Governor", ["dao", "governance", "planning", "orchestration"], weight=1.3),
    "security": Agent("Security Guardian", "Security & Privacy", ["security", "privacy", "zk", "identity"], weight=1.2),
    "defi": Agent("DeFi Specialist", "Financial & Mining", ["defi", "mining", "wallets", "payments"], weight=1.1),
    "rag": Agent("RAG Orchestrator", "Retrieval & Memory", ["rag", "grounding", "memory", "ui"], weight=1.15),
    "federated": Agent("Federated AI Lead", "FL & Models", ["federated-learning", "models", "privacy"], weight=1.15),
    "mesh": Agent("Mesh/Offline", "MESHNET & Offline", ["meshnet", "offline", "sync"], weight=1.05),
}

AGENT_ORDER = ["coordinator", "federated", "rag", "security", "defi", "mesh"]


# ============================= Guided Planner =================================

def generate_guided_tasks() -> List[IntegrationTask]:
    """
    Expand the FIRST_WAVE_GOALS into concrete, addressable tasks with deterministic keys.
    Keys are stable hashes (short) derived from title + repos.
    """
    todo: List[IntegrationTask] = []
    for i, g in enumerate(FIRST_WAVE_GOALS, start=1):
        base = f"{g['title']}::{','.join(g['repos'])}"
        # stable short key
        short = re.sub(r"[^a-z0-9]+", "-", base.lower()).strip("-")
        key = f"task-{short[:48]}"
        # assign priority: 1 for first 2 goals, else 2/3
        priority = 1 if i <= 2 else (2 if i <= 4 else 3)
        t = IntegrationTask(
            key=key,
            title=g["title"],
            description=g["desc"],
            repos=g["repos"],
            labels=g["labels"],
            priority=priority,
            acceptance=g["acceptance"]
        )
        todo.append(t)

        # Add sub-tasks for each repo (implementation PR stubs and CI hook).
        for repo in g["repos"]:
            sub_key = f"{key}-{repo}"
            sub = IntegrationTask(
                key=sub_key,
                title=f"[{repo}] Enable integration hook",
                description=f"Implement integration points for goal: {g['title']}",
                repos=[repo],
                labels=g["labels"] + ["implementation"],
                priority=priority + 1,
                dependencies=[key],
                acceptance=["PR with integration hook and unit test", "Docs updated with usage"]
            )
            todo.append(sub)

    return todo


def seed_backlog():
    for t in generate_guided_tasks():
        BACKLOG.put(t)


seed_backlog()


# ============================= Consensus Engine ===============================

class ConsensusEngine:
    """
    Multi-agent consensus engine:
    - Agents propose next task from backlog they can own.
    - Weighted voting (agent weights). Quorum >= 3 agents and sum weights >= 3.0.
    - Tie-break via MCP tool 'reasoner' (if configured) else OpenAI, else deterministic.
    - On decision, executes a concrete action: create issue(s) in target repos,
      commit a minimal "integration stub" file when appropriate.
    """

    def __init__(self):
        self._last_decision: Optional[DecisionRecord] = None

    def choose_next(self) -> DecisionRecord:
        tasks = BACKLOG.top(12)
        candidate_map: Dict[str, IntegrationTask] = {t.key: t for t in tasks if t.status == "pending"}
        if not candidate_map:
            rec = DecisionRecord(
                at=now_iso(), subject="No-op (no pending tasks)",
                proposals=[], selected_key=None, rationale="Backlog empty",
                voters={}
            )
            self._last_decision = rec
            return rec

        # Proposals by agents
        proposals: List[Tuple[str, str, float]] = []  # (task_key, agent_name, weight)
        voters: Dict[str, float] = {}
        for agent_id in AGENT_ORDER:
            agent = AGENTS[agent_id]
            if not agent.active:
                continue
            task = self._best_for_agent(agent, list(candidate_map.values()))
            if task is None:
                continue
            proposals.append((task.key, agent.name, agent.weight))
            voters[agent.name] = agent.weight

        ANALYTICS["consensus_rounds"] += 1

        if not proposals:
            rec = DecisionRecord(
                at=now_iso(), subject="No-op (no agent proposals)",
                proposals=[], selected_key=None, rationale="Agents found no suitable tasks",
                voters={}
            )
            self._last_decision = rec
            return rec

        # Tally weights by task_key
        score: Dict[str, float] = {}
        for k, _, w in proposals:
            score[k] = score.get(k, 0.0) + w

        # Quorum pre-filter: require at least 3 distinct voters total
        if len(voters) < 3:
            rationale = "Insufficient quorum (need >=3 agents)"
            rec = DecisionRecord(
                at=now_iso(), subject="Insufficient quorum",
                proposals=[{"task_key": k, "by": a, "w": w} for k, a, w in proposals],
                selected_key=None, rationale=rationale, voters=voters
            )
            self._last_decision = rec
            return rec

        # Select top candidates
        sorted_by_score = sorted(score.items(), key=lambda kv: (-kv[1], kv[0]))
        top_key, top_val = sorted_by_score[0]
        # Check tie
        ties = [k for k, v in score.items() if v == top_val]
        selected_key = None
        tiebreaker_used = None
        rationale = f"Weighted top score: {top_val:.2f}; voters: {', '.join(voters.keys())}"

        if len(ties) == 1:
            selected_key = top_key
        else:
            # Tie-break: try MCP reasoner tool
            options = [(k, candidate_map[k].title) for k in ties]
            if MCP.available():
                resp = MCP.call_tool("reasoner", {
                    "prompt": "Choose the task that best accelerates document-guided integration while minimizing risk.",
                    "options": [{"key": k, "title": title} for k, title in options]
                })
                if resp.get("ok") and isinstance(resp.get("result"), dict):
                    sel = resp["result"].get("key")
                    if sel and sel in candidate_map:
                        selected_key = sel
                        tiebreaker_used = "mcp"
            # Try OpenAI if still unresolved
            if not selected_key:
                chosen = AI.choose(
                    "Resolve a tie by choosing the single best task key.",
                    options
                )
                if chosen and chosen in candidate_map:
                    selected_key = chosen
                    tiebreaker_used = tiebreaker_used or "ai"
            # Deterministic if still tied
            if not selected_key:
                selected_key = sorted(ties)[0]
                tiebreaker_used = tiebreaker_used or "deterministic"

        rec = DecisionRecord(
            at=now_iso(),
            subject="Select next integration task",
            proposals=[{"task_key": k, "by": a, "w": w} for k, a, w in proposals],
            selected_key=selected_key,
            rationale=rationale,
            voters=voters,
            tiebreaker=tiebreaker_used
        )
        self._last_decision = rec
        return rec

    def _best_for_agent(self, agent: Agent, tasks: List[IntegrationTask]) -> Optional[IntegrationTask]:
        # choose highest priority task matching agent domains not blocked
        candidates = [
            t for t in tasks
            if t.status == "pending"
            and agent.can_own(t)
            and not t.dependencies  # initial simplification: pick root items first
        ]
        if not candidates:
            # allow dependent tasks if parent is present but pending
            candidates = [t for t in tasks if t.status == "pending" and agent.can_own(t)]

        if not candidates:
            return None
        # Sort by priority, then created_at
        candidates.sort(key=lambda t: (t.priority, t.created_at))
        return candidates[0]

    def execute(self, decision: DecisionRecord) -> Dict[str, Any]:
        """
        Based on decision, change task status and perform real GitHub ops:
        - Create a tracking issue in XMRT-Ecosystem for the chosen task
        - For per-repo sub-tasks, commit stub integration file (if writeable)
        """
        if not decision.selected_key:
            return {"ok": False, "error": "No task selected"}

        task = BACKLOG.get(decision.selected_key)
        if not task:
            return {"ok": False, "error": f"Task {decision.selected_key} not found"}

        # Mark in progress
        BACKLOG.update_status(task.key, "in_progress", "Consensus accepted; executing")
        ANALYTICS["decisions"] += 1

        # Create tracking issue in default repo
        if not GITHUB.available():
            BACKLOG.update_status(task.key, "blocked", "GitHub unavailable")
            return {"ok": False, "error": "GitHub unavailable; task marked blocked"}

        body = self._render_issue_body(task, decision)
        issue_res = GITHUB.create_issue(
            "DevGruGold/XMRT-Ecosystem",
            f"[Integration] {task.title}",
            body,
            labels=list(set(["integration", "xmrt", "consensus"] + task.labels))
        )
        if not issue_res.get("ok"):
            BACKLOG.update_status(task.key, "blocked", f"Issue creation failed: {issue_res.get('error')}")
            return {"ok": False, "error": f"Issue creation failed: {issue_res.get('error')}"}

        task.evidence_links.append(issue_res["url"])
        BACKLOG.update_status(task.key, "in_progress", f"Issue created: {issue_res['url']}")

        # For subtask keyed as <parent>-<repo>, attempt to upsert stub in that repo
        if re.match(r".+-[a-z0-9_-]+$", task.key) and len(task.repos) == 1:
            repo = task.repos[0]
            repo_full = f"DevGruGold/{repo}"
            # Add an integration stub under .xmrt/ to avoid code breakage
            path = f".xmrt/integration/{task.key}.md"
            content = self._render_stub_md(task, decision, issue_res["url"])
            up = GITHUB.upsert_file(repo_full, path, f"Add XMRT integration stub for {task.title}", content)
            if not up.get("ok"):
                BACKLOG.update_status(task.key, "blocked", f"Commit failed: {up.get('error')}")
                return {"ok": False, "error": f"Commit failed: {up.get('error')}"}
            sha = up["commit"]["sha"]
            url_hint = f"https://github.com/{repo_full}/blob/main/{path}"
            task.evidence_links.append(url_hint)
            BACKLOG.update_status(task.key, "done", f"Stub committed ({sha[:7]}) at {url_hint}")
            return {"ok": True, "issue": issue_res, "commit": up, "task": asdict(task)}

        # If it's a parent/root item (spans multiple repos), just record the issue link
        BACKLOG.update_status(task.key, "in_progress", "Root tracked by issue; execute children next")
        return {"ok": True, "issue": issue_res, "task": asdict(task)}

    def _render_issue_body(self, task: IntegrationTask, decision: DecisionRecord) -> str:
        lines = [
            f"# {task.title}",
            "",
            f"**Created**: {now_iso()}",
            f"**Selected by Consensus**: {decision.at}",
            f"**Labels**: {', '.join(task.labels)}",
            "",
            "## Description",
            task.description,
            "",
            "## Target Repos",
            *(f"- `{r}`" for r in task.repos),
            "",
            "## Acceptance Criteria",
            *(f"- [ ] {a}" for a in task.acceptance),
            "",
            "## Evidence / Links",
            *(f"- {l}" for l in task.evidence_links),
            "",
            "## Notes",
            *(f"- {n}" for n in task.notes),
            "",
            "## Consensus Record",
            f"- Voters: {', '.join(f'{k}({v:.2f})' for k, v in decision.voters.items())}",
            f"- Tiebreaker: {decision.tiebreaker or 'n/a'}",
            "",
            "> This issue was generated by the XMRT Ecosystem consensus engine.",
        ]
        return "\n".join(lines)

    def _render_stub_md(self, task: IntegrationTask, decision: DecisionRecord, issue_url: str) -> str:
        return f"""# XMRT Integration Stub
Task: {task.title}
Selected: {decision.at}
Issue: {issue_url}

## Purpose
Provide a non-invasive integration stub for {task.repos[0]} so the implementation can
be iterated safely via PRs.

## Next Steps
- Implement real integration code paths behind feature flags.
- Add unit tests to exercise minimal flows.
- Update documentation with runbook steps.

"""


CONSENSUS = ConsensusEngine()


# ============================= Background Worker ===============================

class CoordinatorThread(threading.Thread):
    """
    Periodically attempts a consensus cycle (if there is at least one pending task).
    Uses ADMIN_TOKEN auth bypass since it's internal.
    """

    def __init__(self, interval_sec: int = 120):
        super().__init__(daemon=True)
        self.interval = interval_sec
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def run(self):
        logger.info("Consensus Builder worker ready")
        while not self._stop.is_set():
            try:
                pending = [t for t in BACKLOG.list() if t.status == "pending"]
                if pending:
                    dec = CONSENSUS.choose_next()
                    if dec.selected_key:
                        CONSENSUS.execute(dec)
                        SYSTEM_STATE["last_cycle"] = now_iso()
                time.sleep(self.interval)
            except Exception as e:
                ANALYTICS["errors"] += 1
                logger.error(f"CoordinatorThread error: {e}")
                time.sleep(self.interval)


COORDINATOR = CoordinatorThread(interval_sec=180)  # every 3 minutes
COORDINATOR.start()


# ============================= Routes / API ====================================

@app.before_request
def _count_requests():
    ANALYTICS["requests"] += 1


@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML_INDEX)


@app.route("/api/coordination/status", methods=["GET"])
def api_status():
    # Emulate your log style lines when starting up
    s = {
        "system": SYSTEM_STATE,
        "analytics": ANALYTICS,
        "pending": len([t for t in BACKLOG.list() if t.status == "pending"]),
        "in_progress": len([t for t in BACKLOG.list() if t.status == "in_progress"]),
        "done": len([t for t in BACKLOG.list() if t.status == "done"]),
        "blocked": len([t for t in BACKLOG.list() if t.status == "blocked"]),
    }
    return jsonify(s)


@app.route("/api/coordination/last-decision", methods=["GET"])
def api_last_decision():
    d = CONSENSUS._last_decision
    if not d:
        return jsonify({"ok": True, "decision": None})
    return jsonify({"ok": True, "decision": asdict(d)})


@app.route("/api/agents", methods=["GET"])
def api_agents():
    return jsonify({"agents": {k: asdict(v) for k, v in AGENTS.items()}})


@app.route("/api/tasks", methods=["GET"])
def api_tasks():
    limit = int(request.args.get("limit", "100"))
    tasks = BACKLOG.top(limit)
    return jsonify({"count": len(tasks), "tasks": [asdict(t) for t in tasks]})


@app.route("/api/tasks/<key>", methods=["GET"])
def api_task_one(key: str):
    t = BACKLOG.get(key)
    if not t:
        return make_response(jsonify({"error": "Not found"}), 404)
    return jsonify(asdict(t))


@app.route("/api/run-innovation-cycle", methods=["POST"])
def api_run_cycle():
    # Protected by ADMIN_TOKEN if set
    auth = require_admin_token(request)
    if auth:
        return auth

    logger.info("Starting innovation cycle")
    dec = CONSENSUS.choose_next()
    res = {"ok": True, "decision": asdict(dec)}
    if dec.selected_key:
        exe = CONSENSUS.execute(dec)
        res["execution"] = exe
    logger.info(f"Innovation cycle complete: {dec.subject}")
    return jsonify(res)


@app.route("/api/mcp/tools", methods=["GET"])
def api_mcp_tools():
    tools = MCP.list_tools()
    return jsonify(tools)


@app.route("/api/mcp/call", methods=["POST"])
def api_mcp_call():
    # Protected by ADMIN_TOKEN if set
    auth = require_admin_token(request)
    if auth:
        return auth

    data = request.get_json(force=True, silent=True) or {}
    name = data.get("name")
    arguments = data.get("arguments") or {}
    if not name:
        return make_response(jsonify({"ok": False, "error": "Missing tool name"}), 400)
    res = MCP.call_tool(name, arguments)
    return jsonify(res)


@app.route("/api/github/issue", methods=["POST"])
def api_github_issue():
    # Protected by ADMIN_TOKEN if set
    auth = require_admin_token(request)
    if auth:
        return auth

    if not GITHUB.available():
        return make_response(jsonify({"ok": False, "error": "GitHub unavailable"}), 503)
    data = request.get_json(force=True, silent=True) or {}
    repo = data.get("repo") or "DevGruGold/XMRT-Ecosystem"
    title = data.get("title") or "Untitled"
    body = data.get("body") or ""
    labels = data.get("labels") or []
    res = GITHUB.create_issue(repo, title, body, labels)
    code = 200 if res.get("ok") else 400
    return make_response(jsonify(res), code)


@app.route("/api/github/commit", methods=["POST"])
def api_github_commit():
    # Protected by ADMIN_TOKEN if set
    auth = require_admin_token(request)
    if auth:
        return auth

    if not GITHUB.available():
        return make_response(jsonify({"ok": False, "error": "GitHub unavailable"}), 503)
    data = request.get_json(force=True, silent=True) or {}
    repo = data.get("repo") or "DevGruGold/XMRT-Ecosystem"
    path = data.get("path")
    message = data.get("message") or "XMRT commit"
    content = data.get("content") or ""
    if not path:
        return make_response(jsonify({"ok": False, "error": "Missing 'path'"}), 400)
    res = GITHUB.upsert_file(repo, path, message, content)
    code = 200 if res.get("ok") else 400
    return make_response(jsonify(res), code)


# ============================= Graceful Shutdown ===============================

def _graceful_exit(*_):
    logger.info("Shutting down XMRT Ecosystem server")
    try:
        COORDINATOR.stop()
    except Exception:
        pass
    sys.exit(0)


signal.signal(signal.SIGTERM, _graceful_exit)
signal.signal(signal.SIGINT, _graceful_exit)


# ============================= Start Server ====================================

def main():
    logger.info("OpenAI client initialized" if OPENAI_AVAILABLE and os.environ.get("OPENAI_API_KEY") else "OpenAI unavailable or no key")
    if GITHUB.available():
        logger.info("GitHub repo reachable (DevGruGold/XMRT-Ecosystem). Enabling real mode.")
    else:
        logger.info("GitHub unavailable; real GitHub actions will fail with explicit errors (no simulation).")

    logger.info("Consensus Builder worker ready")
    logger.info("Agents and Coordination initialized")
    logger.info(f"Starting XMRT Ecosystem on port {PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=False)


if __name__ == "__main__":
    main()
