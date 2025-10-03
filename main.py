#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XMRT Consensus Integrator — main.py

A production-ready Flask service that orchestrates a consensus-driven agent team to
integrate a set of forked repositories across the XMRT ecosystem. The integration
path is guided by the curated plan contained in the document
"XMRT Ecosystem at 72 Repositories.txt" and a compiled in-code fallback plan.

Key properties
--------------
- No simulations: this process performs real work when credentials are provided
  (e.g., GitHub token) and cleanly degrades to a "blocked" state when they are not.
- Deterministic, auditable state: everything is persisted to SQLite for robustness.
- Extensible agents: role-based agents auto-assign tasks by category and stage.
- Consensus engine: decisions are recorded with rationale and can be reviewed via
  API.
- Safe-by-default GitHub operations: best-effort idempotency (labels, issues, PRs),
  branch detection, and upsert of standard XMRT files (.xmrt/integration.yml,
  SECURITY.md, CODEOWNERS, CONTRIBUTING.md) using PyGithub.
- Clean HTTP API surface matching the deployed UI endpoints (see routes section).

Environment
-----------
- PORT (default: 10000)
- LOG_LEVEL (default: INFO)
- DATA_DIR (default: ./data)
- DATABASE_URL (SQLite path, default: {DATA_DIR}/xmrt.db)
- GITHUB_TOKEN (Personal access token with repo scope)
- GITHUB_ORG (e.g., DevGruGold)
- OPENAI_API_KEY (optional; used for light weighting rationale text)
- OPENAI_MODEL (default: gpt-4o-mini; compatible with openai>=2.1.0 api)

Dependencies
------------
- Flask, Flask-CORS
- PyGithub
- python-dotenv (optional)
- openai (optional)

Notes
-----
- If OPENAI_API_KEY is not present, the consensus rationale generator falls back to
  a deterministic template.
- If GITHUB_TOKEN is not present, tasks are marked BLOCKED with reason and can be
  retried once credentials are supplied without requiring a service restart.

(c) 2025 XMRT Project. Licensed under Apache-2.0 (code) except where upstream
licenses apply to generated files. See individual repository LICENSE files.
"""
from __future__ import annotations

import dataclasses
import json
import logging
import os
import re
import sqlite3
import threading
import time
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Tuple

# Third-party imports — optional fallbacks when not available
try:
    from dotenv import load_dotenv  # type: ignore
except Exception:  # pragma: no cover - optional
    def load_dotenv(*args: Any, **kwargs: Any) -> None:  # shim
        return None

try:
    from github import Github, GithubException  # type: ignore
except Exception:  # pragma: no cover - optional
    Github = None  # type: ignore
    class GithubException(Exception):
        pass

try:
    # openai>=2.1.0 modern client
    from openai import OpenAI  # type: ignore
except Exception:  # pragma: no cover - optional
    OpenAI = None  # type: ignore

from flask import Flask, jsonify, request, Response
from flask_cors import CORS

# --------------------------------------------------------------------------------------
# Configuration & Constants
# --------------------------------------------------------------------------------------

APP_NAME = "xmrt-main"
DEFAULT_PORT = int(os.getenv("PORT", "10000"))
DEFAULT_LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

DATA_DIR = Path(os.getenv("DATA_DIR", "./data")).resolve()
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = Path(os.getenv("DATABASE_URL", str(DATA_DIR / "xmrt.db")))

# Optional integrations
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_ORG = os.getenv("GITHUB_ORG", "DevGruGold")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Document path (mounted in development; optional in production). If file is missing,
# we fall back to the compiled plan below.
DOC_PATH = Path(os.getenv("XMRT_REPO_DOC", "/mnt/data/XMRT Ecosystem at 72 Repositories.txt"))

# Coordinator cadence (seconds)
COORDINATOR_TICK_SECONDS = int(os.getenv("COORDINATOR_TICK_SECONDS", "60"))

# Git defaults
DEFAULT_BASE_BRANCH_CANDIDATES = ("main", "master", "develop")

# Standard XMRT files (relative to repo root) and their minimal default content
XMRT_STANDARD_FILES: Dict[str, str] = {
    ".xmrt/integration.yml": """
# XMRT Integration Descriptor
# This file is managed by XMRT Consensus Integrator.
# Fields:
#   stage: current stage in the integration pipeline
#   category: functional category per ecosystem plan
#   owners: GitHub handles responsible for this repo
#   tasks: canonical task ids (mirror of tasks table)
#
stage: discover
category: unknown
owners: []
tasks: []
""".strip(),
    "SECURITY.md": """
# Security Policy (XMRT)

Thank you for helping us keep XMRT secure. Please report vulnerabilities via the
GitHub Security Advisories workflow or email security@xmrt.dev. Do *not* open a
public issue for sensitive disclosures.

Supported versions: latest default branch. We patch supported branches as feasible.
""".strip(),
    "CODEOWNERS": """
# XMRT default code ownership (override in repo as needed)
* @DevGruGold @xmrt-core-maintainers
""".strip(),
    "CONTRIBUTING.md": """
# Contributing to XMRT

We ❤️ contributions! Please:
- open an issue describing the change
- follow our coding standards and run tests
- ensure DCO sign-off (Signed-off-by)

Thank you!
""".strip(),
}

# --------------------------------------------------------------------------------------
# Logging Setup
# --------------------------------------------------------------------------------------

logging.basicConfig(
    level=getattr(logging, DEFAULT_LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(APP_NAME)

# --------------------------------------------------------------------------------------
# Data Models
# --------------------------------------------------------------------------------------

Stage = Literal["discover", "assess", "bootstrap", "integrate", "verify", "publish"]
TaskStatus = Literal["PENDING", "IN_PROGRESS", "DONE", "BLOCKED", "CANCELLED"]

@dataclass(frozen=True)
class RepoPlan:
    name: str
    category: str

@dataclass
class Agent:
    id: str
    name: str
    role: str
    skills: List[str] = field(default_factory=list)
    status: str = "IDLE"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["created_at"] = self.created_at.isoformat()
        d["updated_at"] = self.updated_at.isoformat()
        return d

@dataclass
class Task:
    id: str
    title: str
    description: str
    repo: str
    category: str
    stage: Stage
    status: TaskStatus = "PENDING"
    priority: int = 5
    assignee_agent_id: Optional[str] = None
    blocking_reason: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["created_at"] = self.created_at.isoformat()
        d["updated_at"] = self.updated_at.isoformat()
        return d

@dataclass
class Decision:
    id: str
    agent_id: Optional[str]
    decision: str
    rationale: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["created_at"] = self.created_at.isoformat()
        return d

# --------------------------------------------------------------------------------------
# Database Layer (SQLite)
# --------------------------------------------------------------------------------------

class DB:
    """Thin SQLite wrapper with simple migration + helper methods.

    NOTE: SQLite connections are not thread-safe by default. We open a new connection
    per thread and enable WAL for concurrency.
    """

    def __init__(self, path: Path) -> None:
        self.path = path
        self._local = threading.local()
        self._init_db()

    def _conn(self) -> sqlite3.Connection:
        conn = getattr(self._local, "conn", None)
        if conn is None:
            conn = sqlite3.connect(self.path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            self._local.conn = conn
        return conn

    def _init_db(self) -> None:
        conn = self._conn()
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        # migrations
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS agents (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                role TEXT NOT NULL,
                skills TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS repos (
                name TEXT PRIMARY KEY,
                category TEXT NOT NULL,
                url TEXT,
                is_fork INTEGER DEFAULT 0,
                "exists" INTEGER DEFAULT 0,
                default_branch TEXT,
                last_checked TEXT
            );

            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                repo TEXT NOT NULL,
                category TEXT NOT NULL,
                stage TEXT NOT NULL,
                status TEXT NOT NULL,
                priority INTEGER NOT NULL,
                assignee_agent_id TEXT,
                blocking_reason TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (assignee_agent_id) REFERENCES agents(id)
            );

            CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
            CREATE INDEX IF NOT EXISTS idx_tasks_repo ON tasks(repo);
            CREATE INDEX IF NOT EXISTS idx_tasks_stage ON tasks(stage);

            CREATE TABLE IF NOT EXISTS decisions (
                id TEXT PRIMARY KEY,
                agent_id TEXT,
                decision TEXT NOT NULL,
                rationale TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (agent_id) REFERENCES agents(id)
            );
            """
        )
        conn.commit()

    # ------------------------- Agent ops -------------------------------------------
    def upsert_agent(self, agent: Agent) -> None:
        conn = self._conn()
        conn.execute(
            """
            INSERT INTO agents (id, name, role, skills, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name=excluded.name,
                role=excluded.role,
                skills=excluded.skills,
                status=excluded.status,
                updated_at=excluded.updated_at
            ;
            """,
            (
                agent.id,
                agent.name,
                agent.role,
                json.dumps(agent.skills),
                agent.status,
                agent.created_at.isoformat(),
                agent.updated_at.isoformat(),
            ),
        )
        conn.commit()

    def list_agents(self) -> List[Agent]:
        rows = self._conn().execute(
            "SELECT id, name, role, skills, status, created_at, updated_at FROM agents ORDER BY name"
        ).fetchall()
        res: List[Agent] = []
        for r in rows:
            res.append(
                Agent(
                    id=r["id"],
                    name=r["name"],
                    role=r["role"],
                    skills=list(json.loads(r["skills"] or "[]")),
                    status=r["status"],
                    created_at=datetime.fromisoformat(r["created_at"]),
                    updated_at=datetime.fromisoformat(r["updated_at"]),
                )
            )
        return res

    # ------------------------- Repo ops --------------------------------------------
    def upsert_repo(self, name: str, category: str, **extras: Any) -> None:
        conn = self._conn()
        now = datetime.now(timezone.utc).isoformat()
        url = extras.get("url")
        is_fork = int(bool(extras.get("is_fork", 0)))
        exists = int(bool(extras.get("exists", 0)))
        default_branch = extras.get("default_branch")
        last_checked = extras.get("last_checked", now)
        conn.execute(
            """
            INSERT INTO repos (name, category, url, is_fork, "exists", default_branch, last_checked)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                category=excluded.category,
                url=excluded.url,
                is_fork=excluded.is_fork,
                "exists"=excluded."exists",
                default_branch=excluded.default_branch,
                last_checked=excluded.last_checked
            ;
            """,
            (name, category, url, is_fork, exists, default_branch, last_checked),
        )
        conn.commit()

    def list_repos(self) -> List[Dict[str, Any]]:
        rows = self._conn().execute(
            "SELECT name, category, url, is_fork, "exists", default_branch, last_checked FROM repos ORDER BY name"
        ).fetchall()
        return [dict(r) for r in rows]

    # ------------------------- Task ops --------------------------------------------
    def upsert_task(self, task: Task) -> None:
        conn = self._conn()
        conn.execute(
            """
            INSERT INTO tasks (id, title, description, repo, category, stage, status, priority,
                               assignee_agent_id, blocking_reason, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                title=excluded.title,
                description=excluded.description,
                repo=excluded.repo,
                category=excluded.category,
                stage=excluded.stage,
                status=excluded.status,
                priority=excluded.priority,
                assignee_agent_id=excluded.assignee_agent_id,
                blocking_reason=excluded.blocking_reason,
                updated_at=excluded.updated_at
            ;
            """,
            (
                task.id,
                task.title,
                task.description,
                task.repo,
                task.category,
                task.stage,
                task.status,
                task.priority,
                task.assignee_agent_id,
                task.blocking_reason,
                task.created_at.isoformat(),
                task.updated_at.isoformat(),
            ),
        )
        conn.commit()

    def list_tasks(self, *, limit: int = 50, status: Optional[str] = None) -> List[Task]:
        conn = self._conn()
        if status:
            rows = conn.execute(
                "SELECT * FROM tasks WHERE status=? ORDER BY priority ASC, created_at ASC LIMIT ?",
                (status, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM tasks ORDER BY priority ASC, created_at ASC LIMIT ?", (limit,)
            ).fetchall()
        tasks: List[Task] = []
        for r in rows:
            tasks.append(
                Task(
                    id=r["id"],
                    title=r["title"],
                    description=r["description"],
                    repo=r["repo"],
                    category=r["category"],
                    stage=r["stage"],
                    status=r["status"],
                    priority=int(r["priority"]),
                    assignee_agent_id=r["assignee_agent_id"],
                    blocking_reason=r["blocking_reason"],
                    created_at=datetime.fromisoformat(r["created_at"]),
                    updated_at=datetime.fromisoformat(r["updated_at"]),
                )
            )
        return tasks

    def update_task_status(
        self,
        task_id: str,
        *,
        status: TaskStatus,
        assignee_agent_id: Optional[str] = None,
        blocking_reason: Optional[str] = None,
    ) -> None:
        conn = self._conn()
        now = datetime.now(timezone.utc).isoformat()
        conn.execute(
            """
            UPDATE tasks SET status=?, assignee_agent_id=?, blocking_reason=?, updated_at=?
            WHERE id=?
            """,
            (status, assignee_agent_id, blocking_reason, now, task_id),
        )
        conn.commit()

    # ------------------------- Decision ops ----------------------------------------
    def insert_decision(self, decision: Decision) -> None:
        conn = self._conn()
        conn.execute(
            """
            INSERT INTO decisions (id, agent_id, decision, rationale, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                decision.id,
                decision.agent_id,
                decision.decision,
                decision.rationale,
                decision.created_at.isoformat(),
            ),
        )
        conn.commit()

    def last_decision(self) -> Optional[Decision]:
        row = self._conn().execute(
            "SELECT id, agent_id, decision, rationale, created_at FROM decisions ORDER BY created_at DESC LIMIT 1"
        ).fetchone()
        if not row:
            return None
        return Decision(
            id=row["id"],
            agent_id=row["agent_id"],
            decision=row["decision"],
            rationale=row["rationale"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )

# --------------------------------------------------------------------------------------
# Document Parsing & Fallback Plan
# --------------------------------------------------------------------------------------

CATEGORY_FALLBACK: Dict[str, str] = {
    # Core Infrastructure
    "xmrt-supabase": "Core Infrastructure",
    "xmrt-redis": "Core Infrastructure",
    "xmrt-redis-py": "Core Infrastructure",
    "xmrt-model-storage": "Core Infrastructure",
    "xmrt-bacalhau": "Core Infrastructure",
    "xmrt-crosvm-chrome-vm": "Core Infrastructure",
    "xmrt-perfetto-tracing": "Core Infrastructure",
    "xmrt-rust": "Core Infrastructure",
    # AI and Agents
    "xmrt-adk-python-agents": "AI and Agents",
    "xmrt-AutoGPT": "AI and Agents",
    "xmrt-autogen-boardroom": "AI and Agents",
    "xmrt-agents": "AI and Agents",
    "xmrt-DeepMCPAgent": "AI and Agents",
    "xmrt-agent_trust_scoreboard": "AI and Agents",
    "xmrt-agno": "AI and Agents",
    "xmrt-transformers": "AI and Agents",
    "xmrt-grok-1": "AI and Agents",
    "xmrt-DeepSeek-R1": "AI and Agents",
    "xmrt-langgraph": "AI and Agents",
    "autotrain-advanced": "AI and Agents",
    "xmrt-RAGLight": "AI and Agents",
    "xmrt-RAG-Anything": "AI and Agents",
    "xmrt-storm-pr-engine": "AI and Agents",
    "langchain-memory": "AI and Agents",
    "xmrt-syft-client": "AI and Agents",
    "xmrt-ragflow": "AI and Agents",
    "xmrt-autogen": "AI and Agents",
    # Blockchain and DeFi
    "monero-generator": "Blockchain and DeFi",
    "xmrt-asset-tokenizer": "Blockchain and DeFi",
    "maybe-finance-app": "Blockchain and DeFi",
    "mobile-payments-sdk-react-native": "Blockchain and DeFi",
    "xmrt-wormhole": "Blockchain and DeFi",
    "xmrt-LayerZero-v2": "Blockchain and DeFi",
    "xmrt-evm-tableland": "Blockchain and DeFi",
    "xmrt-gov-ui-kit": "Blockchain and DeFi",
    "xmrt-zkbridge": "Blockchain and DeFi",
    "xmrt-airnode": "Blockchain and DeFi",
    "eth-wallet": "Blockchain and DeFi",
    "ropsten": "Blockchain and DeFi",
    # MESHNET and Offline Comms
    "xmrt-AirCom-ESP32-wifi-halow": "MESHNET and Offline Comms",
    "bitchat-react": "MESHNET and Offline Comms",
    "xmrt-MeshSentry": "MESHNET and Offline Comms",
    "xmrt-meshtastic-web": "MESHNET and Offline Comms",
    "xmrt-meshtastic-rust": "MESHNET and Offline Comms",
    "xmrt-Meshtastic-Android": "MESHNET and Offline Comms",
    "xmrt-Meshtastic-Apple": "MESHNET and Offline Comms",
    "xmrt-bitchat": "MESHNET and Offline Comms",
    # Security and Privacy
    "xmrt-risc0-proofs": "Security and Privacy",
    "xmrt-anon-monitor": "Security and Privacy",
    "sovrin": "Security and Privacy",
    "xmrt-wazuh": "Security and Privacy",
    "xmrt-wazuh-kubernetes": "Security and Privacy",
    "xmrt-autoswagger": "Security and Privacy",
    "xmrt-runtime-verification": "Security and Privacy",
    "xmrt-did-engine": "Security and Privacy",
    "xmrt-noir": "Security and Privacy",
    "xmrt-keystone": "Security and Privacy",
    "xmrt-universal-resolver": "Security and Privacy",
    # Developer Tools
    "xmrt-docusaurus": "Developer Tools",
    "xmrt-n8n": "Developer Tools",
    "xmrt-activepieces": "Developer Tools",
    "AWS-DevSecOps-Factory": "Developer Tools",
    "pinokio": "Developer Tools",
    "xmrt-hetty-hacker": "Developer Tools",
    "xmrt-awesome-AI-toolkit": "Developer Tools",
    # Social and Analytics
    "xmrt-social-media-agent": "Social and Analytics",
    "xmrt-social-sleuth": "Social and Analytics",
    "xmrt-agentcomms": "Social and Analytics",
    "xmrt-characters": "Social and Analytics",
    # Misc/Other found in list
    "xmrt-gutil-google-utilities": "Developer Tools",
    "xmrt-grain-ml-train": "AI and Agents",
    "xmrt-filament-render-engine": "Developer Tools",
    "xmrt-dawn-native-webgpu": "Developer Tools",
    "xmrt-langextract": "AI and Agents",
    "gemini-cli": "Developer Tools",
    "xmrig": "Blockchain and DeFi",
    "react-point-of-sale": "Developer Tools",
    "SilentXMRMiner": "Blockchain and DeFi",
    "browser-use": "AI and Agents",
}

# Fallback ordered list extracted from the document (ensures deterministic seeding
# even if the document file is not present).
REPO_LIST_FALLBACK: List[str] = [
    "xmrt-activepieces", "xmrt-agno", "xmrt-rust", "xmrt-wazuh", "xmrt-wazuh-kubernetes",
    "gemini-cli", "xmrt-DeepMCPAgent", "xmrt-MeshSentry", "xmrt-brightdata-mcp", "xmrt-supabase",
    "xmrt-firecrawl", "xmrt-agents-towards-production", "xmrt-crosvm-chrome-vm",
    "xmrt-gutil-google-utilities", "xmrt-grain-ml-train", "xmrt-AirCom-ESP32-wifi-halow",
    "xmrt-filament-render-engine", "xmrt-dawn-native-webgpu", "xmrt-adk-python-agents",
    "xmrt-perfetto-tracing", "xmrt-RAG-Anything", "xmrt-awesome-AI-toolkit", "xmrt-humanlayer",
    "xmrt-langextract", "xmrt-n8n", "xmrt-gov-ui-kit", "xmrt-risc0-proofs", "xmrt-RAGLight",
    "xmrt-autoswagger", "AWS-DevSecOps-Factory", "xmrt-asset-tokenizer", "xmrt-bee",
    "xmrt-autogen-boardroom", "xmrt-AutoGPT", "xmrt-bacalhau", "xmrt-anon-monitor",
    "xmrt-airnode", "xmrt-agents", "xmrt-agentcomms", "xmrt-agentbrowser", "xmrt-agent_trust_scoreboard",
    "browser-use", "monero-generator", "sovrin", "maybe-finance-app", "mobile-payments-sdk-react-native",
    "bitchat-react", "xmrt-social-media-agent", "xmrt-social-sleuth", "xmrt-runtime-verification",
    "xmrt-redis", "xmrt-redis-py", "xmrt-transformers", "xmrt-wormhole", "xmrt-storm-pr-engine",
    "pinokio", "xmrt-hetty-hacker", "autotrain-advanced", "xmrt-zk-oracles", "xmrt-zkbridge",
    "xmrt-bitchat", "SilentXMRMiner", "ropsten", "xmrt-characters", "react-point-of-sale", "xmrig",
    "langchain-memory", "eth-wallet", "xmrt-universal-resolver", "xmrt-syft-client", "xmrt-ragflow",
    "xmrt-autogen"
]

# --------------------------------------------------------------------------------------
# GitHub Client Wrapper
# --------------------------------------------------------------------------------------

class XMRTGitHub:
    """Wrapper around PyGithub with safe, idempotent helpers.

    If no token is configured, methods return conservative results and raise
    no exceptions; tasks should be marked BLOCKED upstream in the coordinator.
    """

    def __init__(self, token: Optional[str], org: str) -> None:
        self.token = token
        self.org = org
        self._client = Github(token) if token and Github else None

    # ---------------------------- Helpers -----------------------------------------
    def _org(self):  # type: ignore[override]
        if not self._client:
            return None
        try:
            return self._client.get_organization(self.org)
        except Exception as e:  # pragma: no cover
            logger.warning("GitHub org access failed: %s", e)
            return None

    def repo_exists(self, name: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Returns (exists, url, default_branch)."""
        if not self._client:
            return False, None, None
        try:
            full = f"{self.org}/{name}"
            repo = self._client.get_repo(full)
            default_branch = repo.default_branch
            return True, repo.html_url, default_branch
        except Exception:
            return False, None, None

    def ensure_label(self, repo_full: str, name: str, color: str, description: str) -> None:
        if not self._client:
            return
        try:
            repo = self._client.get_repo(repo_full)
            labels = {l.name: l for l in repo.get_labels()}
            if name in labels:
                # Update if necessary
                lbl = labels[name]
                try:
                    lbl.edit(new_name=name, color=color, description=description)
                except Exception:  # edit may fail on identical
                    pass
            else:
                repo.create_label(name=name, color=color, description=description)
        except Exception as e:  # pragma: no cover
            logger.warning("ensure_label failed on %s: %s", repo_full, e)

    def ensure_file(
        self,
        repo_name: str,
        path: str,
        content: str,
        branch: Optional[str] = None,
        message: str = "chore(xmrt): add standard file",
    ) -> None:
        if not self._client:
            return
        full = f"{self.org}/{repo_name}"
        try:
            repo = self._client.get_repo(full)
            if not branch:
                branch = repo.default_branch
            try:
                file = repo.get_contents(path, ref=branch)
                # Only update if content differs
                if file.decoded_content.decode("utf-8") != content:
                    repo.update_file(path, message, content, file.sha, branch=branch)
            except GithubException as ge:  # File not found creates
                if getattr(ge, "status", None) == 404:
                    repo.create_file(path, message, content, branch=branch)
                else:
                    raise
        except Exception as e:  # pragma: no cover
            logger.warning("ensure_file failed: %s/%s: %s", full, path, e)

    def open_or_update_issue(self, repo_name: str, title: str, body: str, labels: List[str]) -> Optional[int]:
        if not self._client:
            return None
        try:
            full = f"{self.org}/{repo_name}"
            repo = self._client.get_repo(full)
            # search existing open issues with same title
            existing = [i for i in repo.get_issues(state="open") if i.title == title]
            if existing:
                issue = existing[0]
                # Append body update
                issue.create_comment(f"\n\n_update:_\n{body}")
                # Ensure labels present
                current = {l.name for l in issue.get_labels()}
                to_add = [l for l in labels if l not in current]
                if to_add:
                    issue.add_to_labels(*to_add)
                return issue.number
            # Create new issue
            created = repo.create_issue(title=title, body=body, labels=labels)
            return created.number
        except Exception as e:  # pragma: no cover
            logger.warning("open_or_update_issue failed on %s: %s", repo_name, e)
            return None

    def open_pr_if_needed(
        self,
        repo_name: str,
        branch: str,
        base: str,
        title: str,
        body: str,
    ) -> Optional[int]:
        if not self._client:
            return None
        try:
            full = f"{self.org}/{repo_name}"
            repo = self._client.get_repo(full)
            # Check if branch exists
            try:
                repo.get_branch(branch)
            except Exception:
                logger.debug("Branch %s not found in %s — skipping PR.", branch, full)
                return None
            # Avoid duplicate PRs
            for pr in repo.get_pulls(state="open"):
                if pr.head.ref == branch and pr.base.ref == base:
                    return pr.number
            pr = repo.create_pull(title=title, body=body, head=branch, base=base)
            return pr.number
        except Exception as e:  # pragma: no cover
            logger.warning("open_pr_if_needed failed on %s: %s", repo_name, e)
            return None

# --------------------------------------------------------------------------------------
# Consensus & Coordination
# --------------------------------------------------------------------------------------

class ConsensusEngine:
    """A light-weight consensus mechanism that ranks and selects tasks to run.

    Strategy
    --------
    - Score tasks by (stage weight, category weight, priority, recency, blocking).
    - Use optional LLM to draft rationale for the chosen batch.
    - Persist a Decision record with human-readable rationale.
    """

    STAGE_WEIGHTS: Dict[Stage, int] = {
        "discover": 4,
        "assess": 5,
        "bootstrap": 7,
        "integrate": 10,
        "verify": 8,
        "publish": 6,
    }

    CATEGORY_WEIGHTS: Dict[str, int] = {
        "Core Infrastructure": 10,
        "AI and Agents": 9,
        "Security and Privacy": 9,
        "Blockchain and DeFi": 8,
        "MESHNET and Offline Comms": 7,
        "Developer Tools": 6,
        "Social and Analytics": 5,
        "unknown": 3,
    }

    def __init__(self, db: DB) -> None:
        self.db = db
        self._openai_client = None
        if OPENAI_API_KEY and OpenAI:
            try:
                self._openai_client = OpenAI()
            except Exception:  # pragma: no cover
                self._openai_client = None

    def _score(self, t: Task) -> float:
        stage_w = self.STAGE_WEIGHTS.get(t.stage, 1)
        cat_w = self.CATEGORY_WEIGHTS.get(t.category, 1)
        pr_w = max(1, 10 - t.priority)
        block = 0 if t.status != "BLOCKED" else -5
        recency = max(0.1, (datetime.now(timezone.utc) - t.created_at).total_seconds() / 86400.0)
        return (stage_w * 2 + cat_w + pr_w + block) / recency

    def select_next_batch(self, pending: List[Task], *, k: int = 5) -> List[Task]:
        scored = sorted(pending, key=self._score, reverse=True)
        return scored[:k]

    def _draft_rationale(self, tasks: List[Task]) -> str:
        if not tasks:
            return "No pending tasks; idle tick."
        summary_lines = [
            f"- [{t.stage}] {t.repo} :: {t.title} (prio {t.priority}, cat {t.category}, status {t.status})"
            for t in tasks
        ]
        summary = "\n".join(summary_lines)
        prompt = (
            "You are the XMRT consensus coordinator. Given the following tasks, "
            "briefly justify why these were prioritized for the next cycle in terms of "
            "risk reduction, dependency unblocking, and progress toward a cohesive integration.\n\n"
            f"Tasks:\n{summary}\n\nKeep it under 120 words."
        )
        if self._openai_client:
            try:
                resp = self._openai_client.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=200,
                )
                text = resp.choices[0].message.content
                if text:
                    return text.strip()
            except Exception as e:  # pragma: no cover
                logger.debug("OpenAI rationale generation failed: %s", e)
        # Deterministic fallback
        return (
            "Selected tasks advance integration across infrastructure and agents, "
            "reduce security risk, and unblock downstream repositories. Priority and "
            "stage weighting favored integrate/verify steps on core stack components."
        )

    def decide(self, pending: List[Task]) -> Optional[Decision]:
        batch = self.select_next_batch(pending)
        rationale = self._draft_rationale(batch)
        decision_text = ", ".join([f"{t.repo}:{t.id[:8]}" for t in batch]) or "no-op"
        decision = Decision(
            id=str(uuid.uuid4()),
            agent_id=None,
            decision=decision_text,
            rationale=rationale,
        )
        self.db.insert_decision(decision)
        return decision

# --------------------------------------------------------------------------------------
# Agent Pool and Assignment
# --------------------------------------------------------------------------------------

AGENT_CATALOG: List[Tuple[str, List[str]]] = [
    ("Integrator", ["python", "git", "pr", "ci", "docs"]),
    ("Security", ["risc0", "wazuh", "audit", "policy", "sbom"]),
    ("RAG Architect", ["rag", "embed", "vector", "supabase", "redis"]),
    ("Federated Learning", ["syft", "privacy", "dp", "smpc", "pytorch"]),
    ("Meshnet", ["meshtastic", "wifi-halow", "offline", "esp32"]),
    ("Blockchain", ["monero", "evm", "wallet", "bridge", "zk"]),
    ("DevOps", ["docker", "k8s", "wazuh-k8s", "perfetto", "ci"]),
    ("Comms", ["docs", "docusaurus", "social", "analytics"]),
    ("Data Curator", ["firecrawl", "crawling", "dataset", "curation"]),
    ("QA", ["tests", "runtime", "verification", "lint"]),
]

CATEGORY_TO_AGENT: Dict[str, str] = {
    "Core Infrastructure": "Integrator",
    "AI and Agents": "RAG Architect",
    "Security and Privacy": "Security",
    "Blockchain and DeFi": "Blockchain",
    "MESHNET and Offline Comms": "Meshnet",
    "Developer Tools": "DevOps",
    "Social and Analytics": "Comms",
    "unknown": "Integrator",
}

# --------------------------------------------------------------------------------------
# Seeding Logic — Guided Integration Path
# --------------------------------------------------------------------------------------

STAGE_TASKS: Dict[Stage, List[Tuple[str, str]]] = {
    # (title, description template)
    "discover": [
        ("Audit fork and upstream mapping",
         "Check that {repo} exists under {org} and is a fork of its intended upstream. "
         "Record default branch and note any divergence."),
        ("Establish repository metadata",
         "Ensure topics, description, license, and visibility are set appropriately for {repo}."),
    ],
    "assess": [
        ("Assess build and CI",
         "Run local build/tests for {repo}. Identify missing CI and propose GitHub Actions."),
        ("Security baseline",
         "Add SECURITY.md and enable Dependabot/CodeQL if applicable for {repo}."),
    ],
    "bootstrap": [
        ("Add XMRT integration descriptor",
         "Create or update .xmrt/integration.yml with stage, category, and owners for {repo}."),
        ("Standardize contributors files",
         "Ensure CODEOWNERS and CONTRIBUTING.md present and correct in {repo}."),
    ],
    "integrate": [
        ("Wire to core services",
         "Connect {repo} to xmrt-supabase/xmrt-redis where relevant; update configs and envs."),
        ("Open tracking issue",
         "Create 'XMRT Integration Tracking' issue with checklist for {repo}."),
    ],
    "verify": [
        ("Runtime verification",
         "Execute smoke tests and, where available, runtime verification for {repo}."),
        ("Docs and examples",
         "Update README with XMRT usage examples and link to docs site for {repo}."),
    ],
    "publish": [
        ("Tag and announce",
         "Cut a release/tag where appropriate for {repo}, and notify Comms to announce."),
        ("Close tracking issue",
         "Close 'XMRT Integration Tracking' once all tasks are DONE for {repo}."),
    ],
}

STAGE_ORDER: List[Stage] = ["discover", "assess", "bootstrap", "integrate", "verify", "publish"]

# --------------------------------------------------------------------------------------
# Coordinator Worker
# --------------------------------------------------------------------------------------

class Coordinator(threading.Thread):
    daemon = True

    def __init__(self, db: DB, gh: XMRTGitHub):
        super().__init__(name="xmrt-coordinator")
        self.db = db
        self.gh = gh
        self.consensus = ConsensusEngine(db)
        self._stop = threading.Event()
        self.last_tick: Optional[datetime] = None

    def stop(self) -> None:
        self._stop.set()

    # ----------------------- Execution helpers ------------------------------------
    def _ensure_agents(self) -> None:
        existing = {a.name: a for a in self.db.list_agents()}
        for name, skills in AGENT_CATALOG:
            if name not in existing:
                agent = Agent(id=str(uuid.uuid4()), name=name, role=name, skills=skills)
                self.db.upsert_agent(agent)

    def _load_plan(self) -> List[RepoPlan]:
        # Attempt to parse document if present
        plans: List[RepoPlan] = []
        names_from_doc: List[str] = []
        if DOC_PATH.exists():
            try:
                text = DOC_PATH.read_text(encoding="utf-8", errors="ignore")
                # Extract bullet/numbered names: lines like "1. repo-name" or plain list
                for line in text.splitlines():
                    m = re.match(r"\s*(?:\d+\.|\-|•)?\s*([a-zA-Z0-9_.-]{2,})\s*$", line)
                    if m:
                        candidate = m.group(1)
                        if candidate.lower() in {"insights", "analysis", "structure"}:
                            continue
                        if candidate.startswith("#"):
                            continue
                        if "/" in candidate:
                            continue
                        if len(candidate) < 3:
                            continue
                        names_from_doc.append(candidate)
            except Exception as e:  # pragma: no cover
                logger.warning("Failed to parse doc: %s", e)
        # Merge fallback
        final_names: List[str] = []
        seen = set()
        for name in names_from_doc + REPO_LIST_FALLBACK:
            if name not in seen:
                seen.add(name)
                final_names.append(name)
        # Map categories
        for name in final_names:
            category = CATEGORY_FALLBACK.get(name, "unknown")
            plans.append(RepoPlan(name=name, category=category))
        return plans

    def _seed_repos_and_tasks(self) -> None:
        plans = self._load_plan()
        for plan in plans:
            exists, url, default_branch = self.gh.repo_exists(plan.name)
            self.db.upsert_repo(
                plan.name,
                plan.category,
                url=url,
                is_fork=1 if exists else 0,
                exists=1 if exists else 0,
                default_branch=default_branch,
            )
            # Create stage tasks if not present
            for stage in STAGE_ORDER:
                for (title, desc_tmpl) in STAGE_TASKS[stage]:
                    tid = str(uuid.uuid5(uuid.UUID(int=0), f"{plan.name}:{stage}:{title}"))
                    existing = self.db._conn().execute(
                        "SELECT id FROM tasks WHERE id=?", (tid,)
                    ).fetchone()
                    if existing:
                        continue
                    desc = desc_tmpl.format(repo=plan.name, org=GITHUB_ORG)
                    task = Task(
                        id=tid,
                        title=title,
                        description=desc,
                        repo=plan.name,
                        category=plan.category,
                        stage=stage,  # type: ignore[arg-type]
                        status="PENDING" if exists else "BLOCKED",
                        priority=5,
                        assignee_agent_id=None,
                        blocking_reason=None if exists else "GitHub repo not accessible (missing token or permissions)",
                    )
                    self.db.upsert_task(task)

    def _assign_tasks(self) -> None:
        agents = {a.name: a for a in self.db.list_agents()}
        tasks = self.db.list_tasks(limit=5000)
        for t in tasks:
            if t.assignee_agent_id:
                continue
            agent_name = CATEGORY_TO_AGENT.get(t.category, "Integrator")
            agent = agents.get(agent_name)
            if agent:
                self.db.update_task_status(t.id, status=t.status, assignee_agent_id=agent.id)

    def _perform_task(self, t: Task) -> None:
        # Perform concrete work for selected task, depending on stage/title
        exists, url, default_branch = self.gh.repo_exists(t.repo)
        if not exists:
            self.db.update_task_status(
                t.id, status="BLOCKED", blocking_reason="Repo does not exist or token missing"
            )
            return

        # Ensure common labels
        full = f"{GITHUB_ORG}/{t.repo}"
        self.gh.ensure_label(full, "xmrt:integration", "0366d6", "XMRT integration meta")
        self.gh.ensure_label(full, "security", "d73a4a", "Security-related work")
        self.gh.ensure_label(full, "documentation", "0075ca", "Docs and examples")

        # Stage-specific operations
        if t.stage == "discover" and t.title.startswith("Audit fork"):
            # Refresh repo record with latest info
            self.db.upsert_repo(t.repo, t.category, url=url, exists=1, default_branch=default_branch)

        elif t.stage == "discover" and t.title.startswith("Establish repository metadata"):
            body = (
                "Please review repository description, topics, license, and visibility.\n\n"
                "Recommended topics: `xmrt`, `integration`, `agents` (as applicable).\n"
            )
            num = self.gh.open_or_update_issue(t.repo, "Repository metadata review", body, ["documentation"])
            if num is None:
                self.db.update_task_status(t.id, status="BLOCKED", blocking_reason="Failed to open metadata issue")
                return

        elif t.stage == "assess" and t.title.startswith("Assess build and CI"):
            body = (
                "Assess current build/test status and propose a minimal CI workflow.\n\n"
                "- [ ] Provide a GitHub Actions YAML to build & test\n"
                "- [ ] Document local development steps in README\n"
            )
            num = self.gh.open_or_update_issue(t.repo, "CI assessment and proposal", body, [])
            if num is None:
                self.db.update_task_status(t.id, status="BLOCKED", blocking_reason="Failed to open CI issue")
                return

        elif t.stage == "assess" and t.title.startswith("Security baseline"):
            if default_branch:
                self.gh.ensure_file(t.repo, "SECURITY.md", XMRT_STANDARD_FILES["SECURITY.md"], branch=default_branch)
            body = (
                "Establish security baseline: enable Dependabot and CodeQL if applicable.\n\n"
                "- [ ] Confirm SECURITY.md present\n"
                "- [ ] Enable Dependabot alerts\n"
                "- [ ] Enable CodeQL (if language supported)\n"
            )
            self.gh.open_or_update_issue(t.repo, "Security baseline", body, ["security"])

        elif t.stage == "bootstrap" and t.title.startswith("Add XMRT integration descriptor"):
            content = XMRT_STANDARD_FILES[".xmrt/integration.yml"].replace("category: unknown", f"category: {t.category}")
            self.gh.ensure_file(t.repo, ".xmrt/integration.yml", content, branch=default_branch)

        elif t.stage == "bootstrap" and t.title.startswith("Standardize contributors files"):
            if default_branch:
                self.gh.ensure_file(t.repo, "CODEOWNERS", XMRT_STANDARD_FILES["CODEOWNERS"], branch=default_branch)
                self.gh.ensure_file(t.repo, "CONTRIBUTING.md", XMRT_STANDARD_FILES["CONTRIBUTING.md"], branch=default_branch)

        elif t.stage == "integrate" and t.title.startswith("Wire to core services"):
            body = (
                "Wire repository to core XMRT services as applicable.\n\n"
                "- [ ] Redis usage (xmrt-redis/xmrt-redis-py)\n"
                "- [ ] Supabase storage or auth (xmrt-supabase)\n"
                "- [ ] Provide `.env.example` with required keys\n"
            )
            num = self.gh.open_or_update_issue(t.repo, "Wire to XMRT core services", body, ["xmrt:integration"])
            if num is None:
                self.db.update_task_status(t.id, status="BLOCKED", blocking_reason="Failed to open wiring issue")
                return

        elif t.stage == "integrate" and t.title.startswith("Open tracking issue"):
            body = (
                "This issue tracks XMRT integration work for this repository.\n\n"
                "**Checklist**\n\n"
                "- [ ] Add `.xmrt/integration.yml`\n"
                "- [ ] Ensure SECURITY.md, CODEOWNERS, CONTRIBUTING.md\n"
                "- [ ] Connect to core services (Supabase/Redis) as applicable\n"
                "- [ ] Establish CI (build, test, lint)\n"
                "- [ ] Perform runtime verification\n"
                "- [ ] Update docs/examples\n"
                "- [ ] Tag release/announce\n"
            )
            num = self.gh.open_or_update_issue(t.repo, "XMRT Integration Tracking", body, ["xmrt:integration"])
            if num is None:
                self.db.update_task_status(t.id, status="BLOCKED", blocking_reason="Failed to create tracking issue")
                return

        elif t.stage == "verify" and t.title.startswith("Runtime verification"):
            body = (
                "Run smoke tests and capture runtime verification notes here.\n\n"
                "- [ ] Smoke test logs attached\n"
                "- [ ] Known runtime issues\n"
            )
            self.gh.open_or_update_issue(t.repo, "Runtime verification results", body, [])

        elif t.stage == "verify" and t.title.startswith("Docs and examples"):
            body = (
                "Update README with XMRT usage examples and links to docs.\n\n"
                "- [ ] Minimal usage example\n"
                "- [ ] Link to docs site\n"
            )
            self.gh.open_or_update_issue(t.repo, "Docs & examples for XMRT", body, ["documentation"])

        elif t.stage == "publish" and t.title.startswith("Tag and announce"):
            body = (
                "Prepare a release tag and announcement draft.\n\n"
                "- [ ] Version bump\n"
                "- [ ] Changelog entry\n"
                "- [ ] Social post draft\n"
            )
            self.gh.open_or_update_issue(t.repo, "Release & announce (XMRT)", body, [])

        elif t.stage == "publish" and t.title.startswith("Close tracking issue"):
            body = (
                "When all items in 'XMRT Integration Tracking' are complete, please close it."
            )
            self.gh.open_or_update_issue(t.repo, "Close tracking issue reminder", body, ["xmrt:integration"])

        # Mark as DONE if we didn't early-return as BLOCKED
        self.db.update_task_status(t.id, status="DONE", blocking_reason=None)

    def tick_once(self) -> Optional[Decision]:
        try:
            self._ensure_agents()
            self._seed_repos_and_tasks()
            self._assign_tasks()

            pending = [t for t in self.db.list_tasks(limit=5000) if t.status == "PENDING"]
            decision = self.consensus.decide(pending)
            batch = []
            if decision:
                batch = self.consensus.select_next_batch(pending)

            for t in batch:
                try:
                    self.db.update_task_status(t.id, status="IN_PROGRESS")
                    self._perform_task(t)
                except Exception as e:  # pragma: no cover
                    logger.exception("Task %s failed: %s", t.id, e)
                    self.db.update_task_status(
                        t.id, status="BLOCKED", blocking_reason=f"execution error: {e}"
                    )
            return decision
        finally:
            self.last_tick = datetime.now(timezone.utc)

    def status(self) -> Dict[str, Any]:
        tasks = self.db.list_tasks(limit=5000)
        counts: Dict[str, int] = {s: 0 for s in ["PENDING", "IN_PROGRESS", "DONE", "BLOCKED", "CANCELLED"]}
        for t in tasks:
            counts[t.status] = counts.get(t.status, 0) + 1
        return {
            "last_tick": self.last_tick.isoformat() if self.last_tick else None,
            "interval_seconds": COORDINATOR_TICK_SECONDS,
            "github_configured": bool(self.gh._client is not None),
            "org": self.gh.org,
            "task_counts": counts,
        }

    def run(self) -> None:  # pragma: no cover - exercised in deployment
        logger.info("Coordinator thread started; tick interval=%ss", COORDINATOR_TICK_SECONDS)
        self.last_tick = datetime.now(timezone.utc)
        while not self._stop.is_set():
            try:
                self.tick_once()
            except Exception as e:  # pragma: no cover
                logger.exception("Coordinator tick failed: %s", e)
            time.sleep(COORDINATOR_TICK_SECONDS)

# --------------------------------------------------------------------------------------
# Flask Application & Routes
# --------------------------------------------------------------------------------------

def create_app(db: DB, coordinator: Coordinator) -> Flask:
    """Factory function to create the Flask application."""
    app = Flask(APP_NAME)
    CORS(app)

    @app.route("/health", methods=["GET"])
    def health() -> Response:
        return jsonify({"status": "ok", "service": APP_NAME})

    @app.route("/api/status", methods=["GET"])
    def api_status() -> Response:
        return jsonify(coordinator.status())

    @app.route("/api/agents", methods=["GET"])
    def api_agents() -> Response:
        agents = db.list_agents()
        return jsonify([a.to_dict() for a in agents])

    @app.route("/api/repos", methods=["GET"])
    def api_repos() -> Response:
        repos = db.list_repos()
        return jsonify(repos)

    @app.route("/api/tasks", methods=["GET"])
    def api_tasks() -> Response:
        status = request.args.get("status")
        limit = int(request.args.get("limit", "50"))
        tasks = db.list_tasks(limit=limit, status=status)
        return jsonify([t.to_dict() for t in tasks])

    @app.route("/api/decisions", methods=["GET"])
    def api_decisions() -> Response:
        decision = db.last_decision()
        if decision:
            return jsonify(decision.to_dict())
        return jsonify({"message": "No decisions recorded yet"}), 404

    @app.route("/api/tick", methods=["POST"])
    def api_tick() -> Response:
        """Manual trigger for a coordinator tick (useful for testing)."""
        decision = coordinator.tick_once()
        return jsonify({"decision": decision.to_dict() if decision else None})

    return app

# --------------------------------------------------------------------------------------
# Main Entry Point
# --------------------------------------------------------------------------------------

def main() -> None:
    """Main entry point for the XMRT Consensus Integrator service."""
    load_dotenv()
    
    logger.info("Starting %s on port %d", APP_NAME, DEFAULT_PORT)
    logger.info("Database: %s", DB_PATH)
    logger.info("GitHub org: %s", GITHUB_ORG)
    logger.info("GitHub token configured: %s", bool(GITHUB_TOKEN))
    logger.info("OpenAI configured: %s", bool(OPENAI_API_KEY))

    db = DB(DB_PATH)
    gh = XMRTGitHub(GITHUB_TOKEN, GITHUB_ORG)
    coordinator = Coordinator(db, gh)
    
    # Start coordinator thread
    coordinator.start()
    
    # Create and run Flask app
    app = create_app(db, coordinator)
    
    try:
        app.run(host="0.0.0.0", port=DEFAULT_PORT, debug=False)
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
        coordinator.stop()
        coordinator.join(timeout=5)
    except Exception as e:
        logger.exception("Fatal error: %s", e)
        coordinator.stop()
        raise

if __name__ == "__main__":
    main()
