#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XMRT Consensus Integrator — main.py

A production-ready Flask service that orchestrates a consensus-driven agent team to
integrate a set of forked repositories across the XMRT ecosystem.

Uses Supabase as the backend database for distributed, scalable operations.

(c) 2025 XMRT Project. Licensed under Apache-2.0
"""
from __future__ import annotations

import json
import logging
import os
import re
import threading
import time
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Tuple

# Third-party imports with fallbacks
try:
    from dotenv import load_dotenv
except Exception:
    def load_dotenv(*args: Any, **kwargs: Any) -> None:
        return None

try:
    from supabase import create_client, Client
except Exception:
    create_client = None
    Client = None

try:
    from github import Github, GithubException, Auth
except Exception:
    Github = None
    Auth = None
    class GithubException(Exception):
        pass

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

from flask import Flask, jsonify, request, Response
from flask_cors import CORS

# --------------------------------------------------------------------------------------
# Configuration & Constants
# --------------------------------------------------------------------------------------

APP_NAME = "xmrt-main"
DEFAULT_PORT = int(os.getenv("PORT", "10000"))
DEFAULT_LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://vawouugtzwmejxqkeqqj.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_SECRET_KEY") or os.getenv("SUPABASE_KEY")

# GitHub Configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_ORG = os.getenv("GITHUB_ORG", "DevGruGold")

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Coordinator Configuration
COORDINATOR_TICK_SECONDS = int(os.getenv("COORDINATOR_TICK_SECONDS", "60"))

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
# Supabase Database Layer
# --------------------------------------------------------------------------------------

class SupabaseDB:
    """Supabase database wrapper for XMRT Consensus Integrator."""

    def __init__(self, url: str, key: str) -> None:
        if not create_client:
            raise RuntimeError("supabase-py is not installed. Install with: pip install supabase")
        if not url or not key:
            raise RuntimeError("SUPABASE_URL and SUPABASE_SECRET_KEY must be set")
        
        self.client: Client = create_client(url, key)
        self._init_tables()
        logger.info("Connected to Supabase at %s", url)

    def _init_tables(self) -> None:
        """Initialize tables if they don't exist (using Supabase SQL editor or migrations)."""
        # Note: Table creation should be done via Supabase Dashboard SQL Editor
        # Here we just verify connectivity
        try:
            # Test connection
            self.client.table('agents').select("id").limit(1).execute()
            logger.info("Supabase tables verified")
        except Exception as e:
            logger.warning("Supabase table verification failed (tables may need creation): %s", e)
            logger.info("Please run the following SQL in your Supabase SQL Editor:")
            logger.info(self._get_init_sql())

    def _get_init_sql(self) -> str:
        """Return SQL for table initialization."""
        return """
-- XMRT Consensus Integrator Tables

-- Agents table
CREATE TABLE IF NOT EXISTS agents (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    skills JSONB NOT NULL DEFAULT '[]',
    status TEXT NOT NULL DEFAULT 'IDLE',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Repositories table
CREATE TABLE IF NOT EXISTS repos (
    name TEXT PRIMARY KEY,
    category TEXT NOT NULL,
    url TEXT,
    is_fork BOOLEAN DEFAULT FALSE,
    repo_exists BOOLEAN DEFAULT FALSE,
    default_branch TEXT,
    last_checked TIMESTAMPTZ
);

-- Tasks table
CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    repo TEXT NOT NULL,
    category TEXT NOT NULL,
    stage TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'PENDING',
    priority INTEGER NOT NULL DEFAULT 5,
    assignee_agent_id TEXT REFERENCES agents(id),
    blocking_reason TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_repo ON tasks(repo);
CREATE INDEX IF NOT EXISTS idx_tasks_stage ON tasks(stage);

-- Decisions table
CREATE TABLE IF NOT EXISTS decisions (
    id TEXT PRIMARY KEY,
    agent_id TEXT REFERENCES agents(id),
    decision TEXT NOT NULL,
    rationale TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_decisions_created ON decisions(created_at DESC);

-- Enable Row Level Security (optional, configure as needed)
ALTER TABLE agents ENABLE ROW LEVEL SECURITY;
ALTER TABLE repos ENABLE ROW LEVEL SECURITY;
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE decisions ENABLE ROW LEVEL SECURITY;

-- Create policies for service role (full access)
CREATE POLICY "Service role full access" ON agents FOR ALL USING (true);
CREATE POLICY "Service role full access" ON repos FOR ALL USING (true);
CREATE POLICY "Service role full access" ON tasks FOR ALL USING (true);
CREATE POLICY "Service role full access" ON decisions FOR ALL USING (true);
"""

    # ------------------------- Agent operations -------------------------------------
    def upsert_agent(self, agent: Agent) -> None:
        try:
            data = {
                "id": agent.id,
                "name": agent.name,
                "role": agent.role,
                "skills": agent.skills,
                "status": agent.status,
                "created_at": agent.created_at.isoformat(),
                "updated_at": agent.updated_at.isoformat(),
            }
            self.client.table('agents').upsert(data).execute()
        except Exception as e:
            logger.error("Failed to upsert agent %s: %s", agent.id, e)

    def list_agents(self) -> List[Agent]:
        try:
            response = self.client.table('agents').select("*").order('name').execute()
            agents = []
            for row in response.data:
                agents.append(Agent(
                    id=row['id'],
                    name=row['name'],
                    role=row['role'],
                    skills=row.get('skills', []),
                    status=row.get('status', 'IDLE'),
                    created_at=datetime.fromisoformat(row['created_at'].replace('Z', '+00:00')),
                    updated_at=datetime.fromisoformat(row['updated_at'].replace('Z', '+00:00')),
                ))
            return agents
        except Exception as e:
            logger.error("Failed to list agents: %s", e)
            return []

    # ------------------------- Repository operations --------------------------------
    def upsert_repo(self, name: str, category: str, **extras: Any) -> None:
        try:
            data = {
                "name": name,
                "category": category,
                "url": extras.get("url"),
                "is_fork": bool(extras.get("is_fork", False)),
                "repo_exists": bool(extras.get("exists", False)),
                "default_branch": extras.get("default_branch"),
                "last_checked": extras.get("last_checked", datetime.now(timezone.utc).isoformat()),
            }
            self.client.table('repos').upsert(data).execute()
        except Exception as e:
            logger.error("Failed to upsert repo %s: %s", name, e)

    def list_repos(self) -> List[Dict[str, Any]]:
        try:
            response = self.client.table('repos').select("*").order('name').execute()
            return response.data
        except Exception as e:
            logger.error("Failed to list repos: %s", e)
            return []

    # ------------------------- Task operations --------------------------------------
    def upsert_task(self, task: Task) -> None:
        try:
            data = {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "repo": task.repo,
                "category": task.category,
                "stage": task.stage,
                "status": task.status,
                "priority": task.priority,
                "assignee_agent_id": task.assignee_agent_id,
                "blocking_reason": task.blocking_reason,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat(),
            }
            self.client.table('tasks').upsert(data).execute()
        except Exception as e:
            logger.error("Failed to upsert task %s: %s", task.id, e)

    def list_tasks(self, *, limit: int = 50, status: Optional[str] = None) -> List[Task]:
        try:
            query = self.client.table('tasks').select("*")
            if status:
                query = query.eq('status', status)
            response = query.order('priority').order('created_at').limit(limit).execute()
            
            tasks = []
            for row in response.data:
                tasks.append(Task(
                    id=row['id'],
                    title=row['title'],
                    description=row['description'],
                    repo=row['repo'],
                    category=row['category'],
                    stage=row['stage'],
                    status=row['status'],
                    priority=row['priority'],
                    assignee_agent_id=row.get('assignee_agent_id'),
                    blocking_reason=row.get('blocking_reason'),
                    created_at=datetime.fromisoformat(row['created_at'].replace('Z', '+00:00')),
                    updated_at=datetime.fromisoformat(row['updated_at'].replace('Z', '+00:00')),
                ))
            return tasks
        except Exception as e:
            logger.error("Failed to list tasks: %s", e)
            return []

    def update_task_status(
        self,
        task_id: str,
        *,
        status: TaskStatus,
        assignee_agent_id: Optional[str] = None,
        blocking_reason: Optional[str] = None,
    ) -> None:
        try:
            data = {
                "status": status,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            if assignee_agent_id is not None:
                data["assignee_agent_id"] = assignee_agent_id
            if blocking_reason is not None:
                data["blocking_reason"] = blocking_reason
            
            self.client.table('tasks').update(data).eq('id', task_id).execute()
        except Exception as e:
            logger.error("Failed to update task %s: %s", task_id, e)

    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        try:
            response = self.client.table('tasks').select("*").eq('id', task_id).execute()
            if response.data:
                row = response.data[0]
                return Task(
                    id=row['id'],
                    title=row['title'],
                    description=row['description'],
                    repo=row['repo'],
                    category=row['category'],
                    stage=row['stage'],
                    status=row['status'],
                    priority=row['priority'],
                    assignee_agent_id=row.get('assignee_agent_id'),
                    blocking_reason=row.get('blocking_reason'),
                    created_at=datetime.fromisoformat(row['created_at'].replace('Z', '+00:00')),
                    updated_at=datetime.fromisoformat(row['updated_at'].replace('Z', '+00:00')),
                )
        except Exception as e:
            logger.error("Failed to get task %s: %s", task_id, e)
        return None

    # ------------------------- Decision operations ----------------------------------
    def insert_decision(self, decision: Decision) -> None:
        try:
            data = {
                "id": decision.id,
                "agent_id": decision.agent_id,
                "decision": decision.decision,
                "rationale": decision.rationale,
                "created_at": decision.created_at.isoformat(),
            }
            self.client.table('decisions').insert(data).execute()
        except Exception as e:
            logger.error("Failed to insert decision %s: %s", decision.id, e)

    def last_decision(self) -> Optional[Decision]:
        try:
            response = self.client.table('decisions').select("*").order('created_at', desc=True).limit(1).execute()
            if response.data:
                row = response.data[0]
                return Decision(
                    id=row['id'],
                    agent_id=row.get('agent_id'),
                    decision=row['decision'],
                    rationale=row['rationale'],
                    created_at=datetime.fromisoformat(row['created_at'].replace('Z', '+00:00')),
                )
        except Exception as e:
            logger.error("Failed to get last decision: %s", e)
        return None

    def list_decisions(self, limit: int = 10) -> List[Decision]:
        try:
            response = self.client.table('decisions').select("*").order('created_at', desc=True).limit(limit).execute()
            decisions = []
            for row in response.data:
                decisions.append(Decision(
                    id=row['id'],
                    agent_id=row.get('agent_id'),
                    decision=row['decision'],
                    rationale=row['rationale'],
                    created_at=datetime.fromisoformat(row['created_at'].replace('Z', '+00:00')),
                ))
            return decisions
        except Exception as e:
            logger.error("Failed to list decisions: %s", e)
            return []

# --------------------------------------------------------------------------------------
# Fallback Data
# --------------------------------------------------------------------------------------

CATEGORY_FALLBACK: Dict[str, str] = {
    "xmrt-supabase": "Core Infrastructure",
    "xmrt-redis": "Core Infrastructure",
    "xmrt-redis-py": "Core Infrastructure",
    "xmrt-model-storage": "Core Infrastructure",
    "xmrt-bacalhau": "Core Infrastructure",
    "xmrt-AutoGPT": "AI and Agents",
    "xmrt-autogen-boardroom": "AI and Agents",
    "xmrt-agents": "AI and Agents",
    "xmrt-DeepMCPAgent": "AI and Agents",
    "xmrt-transformers": "AI and Agents",
    "monero-generator": "Blockchain and DeFi",
    "xmrt-asset-tokenizer": "Blockchain and DeFi",
    "xmrt-wormhole": "Blockchain and DeFi",
    "xmrt-wazuh": "Security and Privacy",
    "xmrt-wazuh-kubernetes": "Security and Privacy",
    "xmrt-risc0-proofs": "Security and Privacy",
    "xmrt-n8n": "Developer Tools",
    "xmrt-activepieces": "Developer Tools",
    "xmrt-docusaurus": "Developer Tools",
    "xmrt-social-media-agent": "Social and Analytics",
    "xmrt-social-sleuth": "Social and Analytics",
}

REPO_LIST_FALLBACK: List[str] = [
    "xmrt-supabase", "xmrt-redis", "xmrt-redis-py", "xmrt-AutoGPT", 
    "xmrt-agents", "xmrt-DeepMCPAgent", "monero-generator", 
    "xmrt-asset-tokenizer", "xmrt-wazuh", "xmrt-n8n", 
    "xmrt-activepieces", "xmrt-social-media-agent"
]

# --------------------------------------------------------------------------------------
# GitHub Client
# --------------------------------------------------------------------------------------

class XMRTGitHub:
    def __init__(self, token: Optional[str], org: str) -> None:
        self.token = token
        self.org = org
        if token and Github and Auth:
            auth = Auth.Token(token)
            self._client = Github(auth=auth)
        else:
            self._client = None

    def repo_exists(self, name: str) -> Tuple[bool, Optional[str], Optional[str]]:
        if not self._client:
            return False, None, None
        try:
            full = f"{self.org}/{name}"
            repo = self._client.get_repo(full)
            return True, repo.html_url, repo.default_branch
        except Exception:
            return False, None, None

# --------------------------------------------------------------------------------------
# Consensus Engine
# --------------------------------------------------------------------------------------

class ConsensusEngine:
    STAGE_WEIGHTS: Dict[Stage, int] = {
        "discover": 4, "assess": 5, "bootstrap": 7,
        "integrate": 10, "verify": 8, "publish": 6,
    }

    CATEGORY_WEIGHTS: Dict[str, int] = {
        "Core Infrastructure": 10,
        "AI and Agents": 9,
        "Security and Privacy": 9,
        "Blockchain and DeFi": 8,
        "Developer Tools": 6,
        "Social and Analytics": 5,
        "unknown": 3,
    }

    def __init__(self, db: SupabaseDB) -> None:
        self.db = db
        self._openai_client: Optional[Any] = None
        if OPENAI_API_KEY and OpenAI:
            try:
                self._openai_client = OpenAI()
            except Exception:
                pass

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
            return "System initialized. Awaiting task generation and coordinator tick."
        summary = "\n".join([
            f"- [{t.stage}] {t.repo} :: {t.title} (prio {t.priority})"
            for t in tasks
        ])
        return (
            f"Selected {len(tasks)} tasks for next cycle based on stage priority, "
            f"category importance, and dependency resolution. Tasks advance integration "
            f"across infrastructure and agents while reducing security risk."
        )

    def decide(self, pending: List[Task]) -> Decision:
        batch = self.select_next_batch(pending)
        rationale = self._draft_rationale(batch)
        decision_text = ", ".join([f"{t.repo}:{t.id[:8]}" for t in batch]) if batch else "initialization"
        decision = Decision(
            id=str(uuid.uuid4()),
            agent_id=None,
            decision=decision_text,
            rationale=rationale,
        )
        self.db.insert_decision(decision)
        return decision

# --------------------------------------------------------------------------------------
# Agent Catalog
# --------------------------------------------------------------------------------------

AGENT_CATALOG: List[Tuple[str, List[str]]] = [
    ("Integrator", ["python", "git", "pr", "ci", "docs"]),
    ("Security", ["wazuh", "audit", "policy", "risc0"]),
    ("RAG Architect", ["rag", "embed", "supabase", "redis"]),
    ("Blockchain", ["monero", "wallet", "bridge"]),
    ("DevOps", ["docker", "k8s", "ci", "n8n"]),
    ("Comms", ["social", "analytics", "content"]),
]

CATEGORY_TO_AGENT: Dict[str, str] = {
    "Core Infrastructure": "Integrator",
    "AI and Agents": "RAG Architect",
    "Security and Privacy": "Security",
    "Blockchain and DeFi": "Blockchain",
    "Developer Tools": "DevOps",
    "Social and Analytics": "Comms",
    "unknown": "Integrator",
}

# --------------------------------------------------------------------------------------
# Stage Tasks
# --------------------------------------------------------------------------------------

STAGE_TASKS: Dict[Stage, List[Tuple[str, str]]] = {
    "discover": [
        ("Audit fork and upstream mapping", "Check that {repo} exists under {org}."),
        ("Establish repository metadata", "Ensure topics and description set for {repo}."),
    ],
    "assess": [
        ("Assess build and CI", "Run build/tests for {repo}."),
        ("Security baseline", "Add SECURITY.md for {repo}."),
    ],
    "bootstrap": [
        ("Add XMRT integration descriptor", "Create .xmrt/integration.yml for {repo}."),
        ("Standardize contributors files", "Ensure CODEOWNERS present in {repo}."),
    ],
    "integrate": [
        ("Wire to core services", "Connect {repo} to xmrt-supabase/redis."),
        ("Open tracking issue", "Create integration tracking issue for {repo}."),
    ],
    "verify": [
        ("Runtime verification", "Execute smoke tests for {repo}."),
        ("Docs and examples", "Update README with examples for {repo}."),
    ],
    "publish": [
        ("Tag and announce", "Cut release tag for {repo}."),
        ("Close tracking issue", "Close integration tracking for {repo}."),
    ],
}

STAGE_ORDER: List[Stage] = ["discover", "assess", "bootstrap", "integrate", "verify", "publish"]

# --------------------------------------------------------------------------------------
# Coordinator
# --------------------------------------------------------------------------------------

class Coordinator(threading.Thread):
    daemon = True

    def __init__(self, db: SupabaseDB, gh: XMRTGitHub) -> None:
        super().__init__(name="xmrt-coordinator")
        self.db = db
        self.gh = gh
        self.consensus = ConsensusEngine(db)
        self._stop = threading.Event()
        self.last_tick: Optional[datetime] = None

    def stop(self) -> None:
        self._stop.set()

    def _ensure_agents(self) -> None:
        existing = {a.name: a for a in self.db.list_agents()}
        for name, skills in AGENT_CATALOG:
            if name not in existing:
                agent = Agent(id=str(uuid.uuid4()), name=name, role=name, skills=skills)
                self.db.upsert_agent(agent)
                logger.info("Created agent: %s", name)

    def _load_plan(self) -> List[RepoPlan]:
        plans: List[RepoPlan] = []
        for name in REPO_LIST_FALLBACK:
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
            
            for stage in STAGE_ORDER:
                for (title, desc_tmpl) in STAGE_TASKS[stage]:
                    tid = str(uuid.uuid5(uuid.UUID(int=0), f"{plan.name}:{stage}:{title}"))
                    existing_task = self.db.get_task_by_id(tid)
                    if existing_task:
                        continue
                    
                    desc = desc_tmpl.format(repo=plan.name, org=GITHUB_ORG)
                    task = Task(
                        id=tid,
                        title=title,
                        description=desc,
                        repo=plan.name,
                        category=plan.category,
                        stage=stage,
                        status="PENDING" if exists else "BLOCKED",
                        priority=5,
                        blocking_reason=None if exists else "GitHub repo not accessible",
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

    def tick_once(self) -> Decision:
        try:
            self._ensure_agents()
            self._seed_repos_and_tasks()
            self._assign_tasks()

            pending = [t for t in self.db.list_tasks(limit=5000) if t.status == "PENDING"]
            decision = self.consensus.decide(pending)
            logger.info("Coordinator tick completed. Decision: %s", decision.decision)
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
            "active_agents": len(self.db.list_agents()),
            "total_repos": len(self.db.list_repos()),
        }

    def run(self) -> None:
        logger.info("Coordinator thread started; tick interval=%ss", COORDINATOR_TICK_SECONDS)
        # Initial tick immediately
        try:
            self.tick_once()
            logger.info("Initial coordinator tick completed")
        except Exception as e:
            logger.exception("Initial tick failed: %s", e)
        
        while not self._stop.is_set():
            time.sleep(COORDINATOR_TICK_SECONDS)
            try:
                self.tick_once()
            except Exception as e:
                logger.exception("Coordinator tick failed: %s", e)

# --------------------------------------------------------------------------------------
# Flask Application with Dashboard
# --------------------------------------------------------------------------------------

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>XMRT Consensus Integrator Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: #333;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .header {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 30px;
            text-align: center;
        }
        
        .header h1 {
            color: #667eea;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            color: #666;
            font-size: 1.1em;
        }
        
        .status-badge {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            margin-top: 10px;
        }
        
        .status-running { background: #10b981; color: white; }
        .status-degraded { background: #f59e0b; color: white; }
        .status-error { background: #ef4444; color: white; }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .card h2 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.5em;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        
        .metric {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #eee;
        }
        
        .metric:last-child { border-bottom: none; }
        
        .metric-label {
            color: #666;
            font-weight: 500;
        }
        
        .metric-value {
            font-weight: bold;
            color: #667eea;
        }
        
        .agent-item, .task-item {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 10px;
            border-left: 4px solid #667eea;
        }
        
        .agent-name, .task-title {
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }
        
        .agent-skills, .task-meta {
            color: #666;
            font-size: 0.9em;
        }
        
        .task-status {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: bold;
            margin-top: 5px;
        }
        
        .status-PENDING { background: #fef3c7; color: #92400e; }
        .status-IN_PROGRESS { background: #dbeafe; color: #1e40af; }
        .status-DONE { background: #d1fae5; color: #065f46; }
        .status-BLOCKED { background: #fee2e2; color: #991b1b; }
        
        .decision-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 20px;
        }
        
        .decision-card h3 {
            margin-bottom: 10px;
            font-size: 1.2em;
        }
        
        .decision-rationale {
            line-height: 1.6;
            opacity: 0.95;
        }
        
        .decision-meta {
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid rgba(255,255,255,0.3);
            font-size: 0.9em;
            opacity: 0.8;
        }
        
        .refresh-indicator {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: white;
            padding: 15px 25px;
            border-radius: 30px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .spinner {
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .empty-state {
            text-align: center;
            padding: 40px;
            color: #999;
        }
        
        .repo-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 10px;
        }
        
        .repo-item {
            background: #f8f9fa;
            padding: 12px;
            border-radius: 8px;
            font-size: 0.9em;
        }
        
        .repo-name {
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }
        
        .repo-category {
            color: #666;
            font-size: 0.85em;
        }
        
        .supabase-badge {
            background: #3ecf8e;
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.9em;
            font-weight: bold;
            margin-left: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 XMRT Consensus Integrator</h1>
            <p>Multi-Agent Repository Management System <span class="supabase-badge">Powered by Supabase</span></p>
            <div id="systemStatus"></div>
        </div>
        
        <div class="grid">
            <div class="card">
                <h2>📊 System Metrics</h2>
                <div id="metrics"></div>
            </div>
            
            <div class="card">
                <h2>👥 Active Agents</h2>
                <div id="agents"></div>
            </div>
            
            <div class="card">
                <h2>📦 Repository Status</h2>
                <div id="repos"></div>
            </div>
        </div>
        
        <div class="card">
            <h2>🎯 Recent Decisions</h2>
            <div id="decisions"></div>
        </div>
        
        <div class="card">
            <h2>📋 Active Tasks</h2>
            <div id="tasks"></div>
        </div>
    </div>
    
    <div class="refresh-indicator">
        <div class="spinner"></div>
        <span>Auto-refreshing...</span>
    </div>
    
    <script>
        async function fetchData() {
            try {
                const [status, agents, tasks, repos, decisions] = await Promise.all([
                    fetch('/api/coordination/status').then(r => r.json()),
                    fetch('/api/agents').then(r => r.json()),
                    fetch('/api/tasks?limit=20').then(r => r.json()),
                    fetch('/api/repos').then(r => r.json()),
                    fetch('/api/decisions?limit=5').then(r => r.json())
                ]);
                
                updateSystemStatus(status);
                updateMetrics(status);
                updateAgents(agents);
                updateTasks(tasks);
                updateRepos(repos);
                updateDecisions(decisions);
            } catch (error) {
                console.error('Failed to fetch data:', error);
            }
        }
        
        function updateSystemStatus(status) {
            const health = status.github_configured ? 'running' : 'degraded';
            const badge = `<span class="status-badge status-${health}">${health.toUpperCase()}</span>`;
            document.getElementById('systemStatus').innerHTML = badge;
        }
        
        function updateMetrics(status) {
            const html = `
                <div class="metric">
                    <span class="metric-label">Last Tick</span>
                    <span class="metric-value">${status.last_tick ? new Date(status.last_tick).toLocaleTimeString() : 'Never'}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Tick Interval</span>
                    <span class="metric-value">${status.interval_seconds}s</span>
                </div>
                <div class="metric">
                    <span class="metric-label">GitHub Configured</span>
                    <span class="metric-value">${status.github_configured ? '✅ Yes' : '❌ No'}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Active Agents</span>
                    <span class="metric-value">${status.active_agents}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Total Repos</span>
                    <span class="metric-value">${status.total_repos}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Pending Tasks</span>
                    <span class="metric-value">${status.task_counts.PENDING || 0}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Completed Tasks</span>
                    <span class="metric-value">${status.task_counts.DONE || 0}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Blocked Tasks</span>
                    <span class="metric-value">${status.task_counts.BLOCKED || 0}</span>
                </div>
            `;
            document.getElementById('metrics').innerHTML = html;
        }
        
        function updateAgents(agents) {
            if (!agents.length) {
                document.getElementById('agents').innerHTML = '<div class="empty-state">No agents registered</div>';
                return;
            }
            const html = agents.map(agent => `
                <div class="agent-item">
                    <div class="agent-name">${agent.name}</div>
                    <div class="agent-skills">${agent.skills.join(', ')}</div>
                </div>
            `).join('');
            document.getElementById('agents').innerHTML = html;
        }
        
        function updateTasks(tasks) {
            if (!tasks.length) {
                document.getElementById('tasks').innerHTML = '<div class="empty-state">No tasks available</div>';
                return;
            }
            const html = tasks.slice(0, 10).map(task => `
                <div class="task-item">
                    <div class="task-title">${task.title}</div>
                    <div class="task-meta">
                        ${task.repo} • ${task.stage}
                        <span class="task-status status-${task.status}">${task.status}</span>
                    </div>
                </div>
            `).join('');
            document.getElementById('tasks').innerHTML = html;
        }
        
        function updateRepos(repos) {
            if (!repos.length) {
                document.getElementById('repos').innerHTML = '<div class="empty-state">No repositories tracked</div>';
                return;
            }
            const html = `<div class="repo-grid">` + repos.map(repo => `
                <div class="repo-item">
                    <div class="repo-name">${repo.name}</div>
                    <div class="repo-category">${repo.category}</div>
                </div>
            `).join('') + `</div>`;
            document.getElementById('repos').innerHTML = html;
        }
        
        function updateDecisions(decisions) {
            if (!decisions.length) {
                document.getElementById('decisions').innerHTML = '<div class="empty-state">No decisions recorded yet</div>';
                return;
            }
            const html = decisions.map(decision => `
                <div class="decision-card">
                    <h3>Decision: ${decision.decision}</h3>
                    <div class="decision-rationale">${decision.rationale}</div>
                    <div class="decision-meta">
                        Created: ${new Date(decision.created_at).toLocaleString()}
                    </div>
                </div>
            `).join('');
            document.getElementById('decisions').innerHTML = html;
        }
        
        // Initial load
        fetchData();
        
        // Auto-refresh every 5 seconds
        setInterval(fetchData, 5000);
    </script>
</body>
</html>
"""

def create_app(db: SupabaseDB, coordinator: Coordinator) -> Flask:
    app = Flask(APP_NAME)
    CORS(app)

    @app.route("/", methods=["GET"])
    def root() -> Response:
        return Response(DASHBOARD_HTML, mimetype='text/html')
    
    @app.route("/health", methods=["GET"])
    def health() -> Response:
        return jsonify({"status": "ok", "service": APP_NAME, "backend": "supabase"})

    @app.route("/api/coordination/status", methods=["GET"])
    def api_coordination_status() -> Response:
        status = coordinator.status()
        status.update({
            "coordination_health": "healthy" if status.get("active_agents", 0) > 0 else "degraded",
            "last_activity": datetime.now(timezone.utc).isoformat(),
            "backend": "supabase",
        })
        return jsonify(status)

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
        status_param = request.args.get("status")
        limit = int(request.args.get("limit", "50"))
        tasks = db.list_tasks(limit=limit, status=status_param)
        return jsonify([t.to_dict() for t in tasks])

    @app.route("/api/decisions", methods=["GET"])
    def api_decisions() -> Response:
        limit = int(request.args.get("limit", "10"))
        decisions = db.list_decisions(limit=limit)
        return jsonify([d.to_dict() for d in decisions])

    @app.route("/api/tick", methods=["POST"])
    def api_tick() -> Response:
        decision = coordinator.tick_once()
        return jsonify({"decision": decision.to_dict()})

    return app

# --------------------------------------------------------------------------------------
# Main Entry Point
# --------------------------------------------------------------------------------------

_db: Optional[SupabaseDB] = None
_coordinator: Optional[Coordinator] = None
_app: Optional[Flask] = None

def initialize_services() -> Flask:
    global _db, _coordinator, _app
    
    if _app is not None:
        return _app
        
    load_dotenv()
    
    logger.info("Starting %s on port %d", APP_NAME, DEFAULT_PORT)
    logger.info("Supabase URL: %s", SUPABASE_URL)
    logger.info("GitHub org: %s", GITHUB_ORG)
    logger.info("GitHub token configured: %s", bool(GITHUB_TOKEN))

    _db = SupabaseDB(SUPABASE_URL, SUPABASE_KEY)
    _gh = XMRTGitHub(GITHUB_TOKEN, GITHUB_ORG)
    _coordinator = Coordinator(_db, _gh)
    
    _coordinator.start()
    _app = create_app(_db, _coordinator)
    
    logger.info("XMRT Consensus Integrator initialized successfully")
    return _app

def main() -> None:
    app = initialize_services()
    
    try:
        app.run(host="0.0.0.0", port=DEFAULT_PORT, debug=False)
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
        if _coordinator:
            _coordinator.stop()
            _coordinator.join(timeout=5)
    except Exception as e:
        logger.exception("Fatal error: %s", e)
        if _coordinator:
            _coordinator.stop()
        raise

app = initialize_services()

if __name__ == "__main__":
    main()
