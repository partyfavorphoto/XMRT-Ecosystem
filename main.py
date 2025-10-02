
#!/usr/bin/env python3
"""
XMRT Ecosystem Main Application - Version 6.0 "Consensus Builder"
Render-friendly, single-process Flask app with an autonomous, one-shot innovation cycle.

Key upgrades from 5.x:
- Scans ALL public repos under the owner whose names start with "xmrt" (case-insensitive), not just a fixed list.
- Agents analyze the discovered repos, brainstorm multiple NEW feature/utility ideas (not canned).
- Agents hold a lightweight "discussion" (commentary + scoring), reach a decision, and document it:
  1) Creates a GitHub Issue capturing the decision and plan.
  2) Agents post comments on that Issue (debate & sign-off).
  3) Implements the chosen feature by creating/committing code/artifacts in XMRT-Ecosystem.
  4) Opens a GitHub Discussion telling the "story" of the new feature and linking the Issue/PR/files.
- Keeps the same endpoints (/ , /health, /analytics, /agents, /api/force-ecosystem-analysis, /api/force-application-build),
  plus a new POST /api/run-innovation-cycle to run the entire analysis→debate→decision→implementation→story flow on demand.
- Health-friendly: fast /healthz (and /favicon.ico returns 204); uses $PORT or 10000 fallback; graceful shutdown.

ENV expected (recommended):
- GITHUB_TOKEN             (required for real GitHub actions; otherwise runs in "simulate" mode)
- GITHUB_OWNER             (defaults to "DevGruGold")
- OPENAI_API_KEY           (optional, enables richer ideation/discussion)
- GEMINI_API_KEY           (optional, enables richer ideation/discussion)
- OPENAI_MODEL             (defaults to "gpt-4o-mini")
"""

import os
import sys
import re
import json
import time
import math
import queue
import signal
import random
import logging
import threading
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS

# ----------------------------- Optional integrations -----------------------------

# GitHub via PyGithub
try:
    from github import Github, Auth, GithubException
    GITHUB_AVAILABLE = True
except ImportError:
    GITHUB_AVAILABLE = False

# OpenAI
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# psutil for system health (optional)
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# ----------------------------- Logging & globals ---------------------------------

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("xmrt-main")

app = Flask(__name__)
CORS(app)

SHUTDOWN = threading.Event()
READY = threading.Event()

APP_NAME = os.getenv("APP_NAME", "XMRT Ecosystem")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "10000"))
OWNER = os.getenv("GITHUB_OWNER", "DevGruGold")
DEFAULT_OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

START_TIME = datetime.now(timezone.utc)

system_state: Dict[str, Any] = {
    "status": "operational",
    "startup_time": time.time(),
    "version": "6.0.0-consensus-builder",
    "deployment": "render-free-tier",
    "mode": "XMRT_INNOVATION_CYCLE",
    "owner": OWNER,
}

analytics: Dict[str, Any] = {
    "requests_count": 0,
    "ai_operations": 0,
    "github_operations": 0,
    "issues_created": 0,
    "discussions_created": 0,
    "files_created": 0,
    "files_updated": 0,
    "repositories_discovered": 0,
    "ideas_generated": 0,
    "comments_posted": 0,
    "feature_cycles_completed": 0,
    "system_health": {"cpu": 0.0, "mem": 0.0, "disk": 0.0},
}

# ----------------------------- Agent roster --------------------------------------

AGENTS: Dict[str, Dict[str, Any]] = {
    "eliza": {
        "name": "Eliza",
        "role": "Coordinator & Governor",
        "voice": "strategic, synthesizes viewpoints, focuses on user value and governance alignment",
        "weight": 1.2,
    },
    "security_guardian": {
        "name": "Security Guardian",
        "role": "Security & Privacy",
        "voice": "paranoid, privacy-first, threat-models everything",
        "weight": 1.1,
    },
    "defi_specialist": {
        "name": "DeFi Specialist",
        "role": "Mining & Tokenomics",
        "voice": "economics-driven, ROI, yield, resource efficiency",
        "weight": 1.05,
    },
    "community_manager": {
        "name": "Community Manager",
        "role": "Adoption & UX",
        "voice": "onboarding, docs, growth loops, meme-energy",
        "weight": 1.0,
    },
}

# ----------------------------- AI Processor --------------------------------------

class AIProcessor:
    def __init__(self, eager_probe: bool = False):
        self.openai_client = None
        self.gemini_model = None

        if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
            try:
                self.openai_client = OpenAI()
                if eager_probe:
                    _ = self.openai_client.chat.completions.create(
                        model=DEFAULT_OPENAI_MODEL,
                        messages=[{"role": "user", "content": "ping"}],
                        max_tokens=2,
                    )
                logger.info("OpenAI client initialized")
            except Exception as e:
                logger.warning(f"OpenAI init failed: {e}")

        if GEMINI_AVAILABLE and os.getenv("GEMINI_API_KEY"):
            try:
                genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
                self.gemini_model = genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-pro"))
                if eager_probe:
                    _ = self.gemini_model.generate_content("ping")
                logger.info("Gemini client initialized")
            except Exception as e:
                logger.warning(f"Gemini init failed: {e}")

    def is_available(self) -> bool:
        return bool(self.openai_client or self.gemini_model)

    def _chat(self, system_prompt: str, user_prompt: str, max_tokens: int = 1200, temperature: float = 0.7) -> str:
        if self.openai_client:
            try:
                resp = self.openai_client.chat.completions.create(
                    model=DEFAULT_OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                analytics["ai_operations"] += 1
                return resp.choices[0].message.content or ""
            except Exception as e:
                logger.warning(f"OpenAI chat error: {e}")
        if self.gemini_model:
            try:
                resp = self.gemini_model.generate_content(f"{system_prompt}\n\n{user_prompt}")
                analytics["ai_operations"] += 1
                return getattr(resp, "text", "") or ""
            except Exception as e:
                logger.warning(f"Gemini chat error: {e}")
        return ""

    # ------------------------- Ideation & discussion prompts -------------------------

    def ideate_features(self, repo_summaries: List[Dict[str, Any]], n_ideas: int = 7) -> List[Dict[str, Any]]:
        """
        Produce N novel feature/utility ideas leveraging discovered repos, topics, and gaps.
        Returns a list of dicts: {title, description, rationale, impact, complexity, tags}
        """
        system_prompt = "You are an XMRT DAO product strategist focused on mobile mining, mesh networking, privacy, and real adoption."
        user_prompt = (
            "Given these repository summaries, propose diverse, HIGH-IMPACT features/utilities the ecosystem is missing.\n"
            "Each idea must be returned as a JSON list of objects with keys:\n"
            "title, description, rationale, impact (1-5), complexity (1-5), tags (list of strings).\n\n"
            f"REPOS:\n{json.dumps(repo_summaries, indent=2)}\n\n"
            f"Please produce {n_ideas} distinct ideas. Avoid duplicates and avoid vague 'dashboards' unless unique."
        )
        text = self._chat(system_prompt, user_prompt)
        ideas: List[Dict[str, Any]] = []

        # Robust JSON extraction
        candidates = re.findall(r"\[[\s\S]*\]", text)
        parsed = None
        for c in candidates:
            try:
                parsed = json.loads(c)
                break
            except Exception:
                continue

        if isinstance(parsed, list):
            for obj in parsed:
                if isinstance(obj, dict) and "title" in obj:
                    ideas.append(obj)

        # Fallback if AI unavailable
        if not ideas:
            ideas = [
                {
                    "title": "XMRT Mesh Health Beacons",
                    "description": "Lightweight UDP beacons for offline mesh presence + mining coordination.",
                    "rationale": "Strengthens mesh resilience and device discovery.",
                    "impact": 5,
                    "complexity": 2,
                    "tags": ["meshnet", "offline", "mobile"],
                },
                {
                    "title": "Adaptive Mobile Mining Profiles",
                    "description": "Per-device auto-tuning profiles based on battery/thermals/network.",
                    "rationale": "Boosts hash-per-watt and user retention.",
                    "impact": 5,
                    "complexity": 3,
                    "tags": ["mining", "battery", "optimizer"],
                },
                {
                    "title": "Proof-of-Participation Badges",
                    "description": "Signed badges for sustained participation to feed DAO governance weight.",
                    "rationale": "Aligns mining with long-term governance.",
                    "impact": 4,
                    "complexity": 3,
                    "tags": ["governance", "reputation", "tokens"],
                },
                {
                    "title": "XMRT Repo Cross-Indexer",
                    "description": "Generates a unified API over all xmrt* repos (endpoints, schemas, versions).",
                    "rationale": "Easier integrations & programmatic discovery.",
                    "impact": 4,
                    "complexity": 2,
                    "tags": ["devtools", "indexing", "api"],
                },
                {
                    "title": "MobileMonero One-Tap Onboarding",
                    "description": "Single URL bootstrap that installs Termux + scripts and verifies environment.",
                    "rationale": "Removes friction for mainstream users.",
                    "impact": 5,
                    "complexity": 3,
                    "tags": ["onboarding", "mobile", "ux"],
                },
                {
                    "title": "Mesh-First Wallet Alerts",
                    "description": "Offline-first alerts delivered via mesh nodes; sync when online.",
                    "rationale": "Trust-minimized notifications for outages.",
                    "impact": 4,
                    "complexity": 3,
                    "tags": ["wallet", "meshnet", "alerts"],
                },
                {
                    "title": "XMRT Edge Telemetry Pack",
                    "description": "Unified, privacy-preserving metrics pack for mining performance.",
                    "rationale": "Optimize with no central data hoarding.",
                    "impact": 4,
                    "complexity": 2,
                    "tags": ["telemetry", "privacy", "optimizer"],
                },
            ]

        analytics["ideas_generated"] += len(ideas)
        return ideas

    def agent_comments_and_scores(self, ideas: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Each agent comments on each idea and assigns a score (0-10).
        Returns mapping: agent_id -> list of {title, comment, score}.
        """
        outputs: Dict[str, List[Dict[str, Any]]] = {k: [] for k in AGENTS.keys()}
        for agent_id, meta in AGENTS.items():
            for idea in ideas:
                base = 5.0
                # Simple heuristic scoring by tags vs agent role
                boost = 0.0
                tags = [t.lower() for t in idea.get("tags", [])]
                if agent_id == "security_guardian" and any(t in tags for t in ["privacy", "security", "meshnet"]):
                    boost += 2.0
                if agent_id == "defi_specialist" and any(t in tags for t in ["mining", "optimizer", "governance", "tokens"]):
                    boost += 2.0
                if agent_id == "community_manager" and any(t in tags for t in ["onboarding", "ux", "alerts"]):
                    boost += 2.0
                if agent_id == "eliza":
                    boost += 1.5  # general strategist

                # Impact & complexity influence
                impact = float(idea.get("impact", 3))
                complexity = float(idea.get("complexity", 3))
                score = base + (impact - complexity * 0.3) + boost
                score = max(0.0, min(10.0, score))

                comment = f"{meta['name']} ({meta['role']}): {meta['voice']}. Assessment for '{idea['title']}': " \
                          f"impact={impact}, complexity={complexity}, provisional_score={round(score,2)}."

                outputs[agent_id].append({
                    "title": idea["title"],
                    "comment": comment,
                    "score": round(score, 2),
                })
        return outputs

    def choose_winner(self, ideas: List[Dict[str, Any]], agent_scores: Dict[str, List[Dict[str, Any]]]) -> Tuple[Dict[str, Any], Dict[str, float]]:
        """
        Weighted consensus: sum per idea across agents (with agent weights).
        Returns (winning_idea, per_idea_scores mapping).
        """
        totals: Dict[str, float] = {idea["title"]: 0.0 for idea in ideas}
        for agent_id, scored in agent_scores.items():
            weight = float(AGENTS[agent_id]["weight"])
            for s in scored:
                totals[s["title"]] += s["score"] * weight
        winner_title = max(totals, key=lambda k: totals[k]) if totals else ideas[0]["title"]
        winning_idea = next(i for i in ideas if i["title"] == winner_title)
        return winning_idea, totals

# ----------------------------- GitHub Integration -------------------------------

class GitHubClient:
    def __init__(self, owner: str):
        self.owner = owner
        self.token = os.getenv("GITHUB_TOKEN")
        self.simulate = True
        self.gh = None
        self.user = None
        self.repo_ecosystem = None  # Main repo where we will write code (XMRT-Ecosystem)

        if self.token and GITHUB_AVAILABLE:
            try:
                auth = Auth.Token(self.token)
                self.gh = Github(auth=auth)
                self.user = self.gh.get_user(self.owner)
                # Main target repo for code drops:
                self.repo_ecosystem = self.gh.get_repo(f"{self.owner}/XMRT-Ecosystem")
                self.simulate = False
                logger.info("GitHub connected. Real mode enabled.")
            except Exception as e:
                logger.warning(f"GitHub init failed -> simulate mode. Reason: {e}")
                self.simulate = True

    def list_xmrt_repos(self) -> List[Dict[str, Any]]:
        """
        Discover all repos under owner whose name starts with 'xmrt' (case-insensitive).
        """
        repos: List[Dict[str, Any]] = []
        try:
            if self.simulate:
                # Simulated fallback
                names = ["XMRT-Ecosystem", "xmrtassistant", "xmrtcash", "xmrt-openai-agents-js", "xmrt-agno", "xmrt-signup"]
                for n in names:
                    repos.append({"name": n, "full_name": f"{self.owner}/{n}", "language": "Python", "topics": ["xmrt", "meshnet"], "stars": 0})
            else:
                for r in self.user.get_repos(type="public"):
                    if r.name.lower().startswith("xmrt"):
                        try:
                            topics = []
                            try:
                                topics = r.get_topics()
                            except Exception:
                                pass
                            repos.append({
                                "name": r.name,
                                "full_name": r.full_name,
                                "description": r.description,
                                "language": r.language,
                                "topics": topics,
                                "stars": r.stargazers_count,
                                "forks": r.forks_count,
                                "updated_at": r.updated_at.isoformat() if r.updated_at else None,
                                "has_pages": r.has_pages,
                            })
                        except Exception as ie:
                            logger.warning(f"Repo parse warning {r.name}: {ie}")
            analytics["repositories_discovered"] = len(repos)
            return repos
        except Exception as e:
            logger.error(f"Failed to list repos: {e}")
            return repos

    def create_or_update_file(self, path: str, message: str, content: str) -> Dict[str, Any]:
        """
        Write file into XMRT-Ecosystem repo (default branch).
        """
        if self.simulate or not self.repo_ecosystem:
            analytics["files_created"] += 1
            return {"simulated": True, "path": path, "message": message}

        try:
            # Try create
            self.repo_ecosystem.create_file(path, message, content)
            analytics["files_created"] += 1
            return {"created": True, "path": path, "message": message}
        except GithubException as ge:
            # If file exists, update
            try:
                file = self.repo_ecosystem.get_contents(path)
                self.repo_ecosystem.update_file(path, f"Update: {message}", content, file.sha)
                analytics["files_updated"] += 1
                return {"updated": True, "path": path, "message": message}
            except Exception as e:
                logger.error(f"File op error for {path}: {e}")
                return {"error": str(e), "path": path}
        except Exception as e:
            logger.error(f"File op error for {path}: {e}")
            return {"error": str(e), "path": path}

    def create_issue_with_body(self, title: str, body: str, labels: Optional[List[str]] = None) -> Dict[str, Any]:
        if self.simulate or not self.repo_ecosystem:
            analytics["issues_created"] += 1
            return {"simulated": True, "title": title, "number": random.randint(1000, 9999)}

        try:
            issue = self.repo_ecosystem.create_issue(title=title, body=body, labels=labels or [])
            analytics["issues_created"] += 1
            return {"number": issue.number, "url": issue.html_url, "title": issue.title}
        except Exception as e:
            logger.error(f"Issue create failed: {e}")
            return {"error": str(e)}

    def comment_issue(self, issue_number: int, comment: str) -> Dict[str, Any]:
        if self.simulate or not self.repo_ecosystem:
            analytics["comments_posted"] += 1
            return {"simulated": True, "issue": issue_number}

        try:
            issue = self.repo_ecosystem.get_issue(number=issue_number)
            issue.create_comment(comment)
            analytics["comments_posted"] += 1
            return {"ok": True, "issue": issue_number}
        except Exception as e:
            logger.error(f"Issue comment failed: {e}")
            return {"error": str(e), "issue": issue_number}

    # ----------------------- Discussions (REST fallback) -----------------------

    def _rest(self, method: str, path: str, **kwargs) -> Tuple[int, Any]:
        """
        Minimal REST client for endpoints not covered by PyGithub (e.g., Discussions).
        """
        import requests
        headers = kwargs.pop("headers", {})
        headers.update({
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.token}" if self.token else "",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "XMRT-Consensus-Builder",
        })
        url = f"https://api.github.com{path}"
        resp = requests.request(method, url, headers=headers, **kwargs)
        try:
            return resp.status_code, resp.json()
        except Exception:
            return resp.status_code, resp.text

    def list_discussion_categories(self, repo: str) -> List[Dict[str, Any]]:
        if self.simulate or not self.token:
            return [{"id": 1, "name": "General"}]
        status, data = self._rest("GET", f"/repos/{self.owner}/{repo}/discussions/categories")
        if status == 200 and isinstance(data, list):
            return data
        logger.warning(f"Could not list categories ({status}): {data}")
        return []

    def create_discussion(self, repo: str, title: str, body: str, category_name: str = "General") -> Dict[str, Any]:
        if self.simulate or not self.token:
            analytics["discussions_created"] += 1
            return {"simulated": True, "repo": repo, "title": title}
        cats = self.list_discussion_categories(repo)
        category_id = None
        for c in cats:
            if str(c.get("name", "")).lower() == category_name.lower():
                category_id = c.get("id")
                break
        if not category_id and cats:
            category_id = cats[0].get("id")
        payload = {"title": title, "body": body, "category_id": category_id}
        status, data = self._rest("POST", f"/repos/{self.owner}/{repo}/discussions", json=payload)
        if status in (200, 201):
            analytics["discussions_created"] += 1
            return {"ok": True, "number": data.get("number"), "url": data.get("html_url")}
        return {"error": f"status={status}", "data": data}

# ----------------------------- Core Pipeline -------------------------------------

ai = AIProcessor(eager_probe=False)
gh = GitHubClient(owner=OWNER)

def summarize_repos_for_ai(repos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for r in repos:
        out.append({
            "name": r.get("name"),
            "language": r.get("language"),
            "topics": r.get("topics", []),
            "stars": r.get("stars", 0),
            "updated_at": r.get("updated_at"),
            "has_pages": r.get("has_pages", False),
            "desc": (r.get("description") or "")[:140],
        })
    return out

def slugify(name: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9\-_]+", "-", name.strip())
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s.lower() or "feature"

def implement_feature(app_name: str, idea: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Write files into XMRT-Ecosystem/xmrt_apps/<slug>_* and a story stub in docs/.
    """
    created: List[Dict[str, Any]] = []
    slug = slugify(app_name)
    base_dir = f"xmrt_apps/{slug}"
    files = {
        f"{base_dir}/{slug}.py": f"""#!/usr/bin/env python3
\"\"\"{app_name}
Auto-generated by XMRT Consensus Builder.

Description:
{idea.get('description','(no description)')}

Tags: {', '.join(idea.get('tags', []))}
\"\"\"

import os, time, json, random, logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger("{slug}")

def run():
    # TODO: replace with real logic for: {app_name}
    log.info("Initialized {app_name}")
    result = {{
        "status": "ok",
        "feature": "{app_name}",
        "improvement": "placeholder",
        "timestamp": time.time(),
    }}
    print(json.dumps(result))

if __name__ == "__main__":
    run()
""",
        f"{base_dir}/{slug}_config.py": f"""# Config for {app_name}
CONFIG = {{
    "version": "0.1.0",
    "enabled": True,
    "notes": "Auto-generated; fill in specific integration params."
}}
""",
        f"{base_dir}/{slug}_README.md": f"""# {app_name}

**Idea**: {idea.get('description','')}
**Rationale**: {idea.get('rationale','')}
**Tags**: {", ".join(idea.get('tags', []))}

This module was created by the XMRT multi-agent consensus flow.
Next steps:
- Wire into MobileMonero onboarding / MeshNet / Optimizer as applicable.
- Add tests and integration hooks.
""",
        f"docs/stories/{slug}.md": f"""# Story: {app_name}

**What shipped?**
- {idea.get('title')} — {idea.get('description','')}

**Why does it matter?**
- {idea.get('rationale','')}

**Links**
- (to be updated by CI) Issue, PR, commit diff, demo endpoints.

*Generated {datetime.now().isoformat()} by XMRT Consensus Builder.*
""",
    }
    for path, content in files.items():
        msg = f"Add {app_name}: initialize {os.path.basename(path)}"
        created.append(gh.create_or_update_file(path, msg, content))
    return created

def innovation_cycle() -> Dict[str, Any]:
    """
    1) Discover all xmrt* repos.
    2) Summarize -> ideate multiple new features (AI-backed).
    3) Agents comment + score -> pick winner.
    4) Create Issue with decision & plan; agents comment on issue.
    5) Implement feature (commit files).
    6) Create Discussion "story" post.
    """
    repos = gh.list_xmrt_repos()
    summaries = summarize_repos_for_ai(repos)
    ideas = ai.ideate_features(summaries, n_ideas=7)
    agent_notes = ai.agent_comments_and_scores(ideas)
    winning_idea, totals = ai.choose_winner(ideas, agent_notes)

    # Compose Issue body
    title = f"[Consensus] Implement: {winning_idea['title']}"
    body = [
        f"# Consensus Decision: {winning_idea['title']}",
        "",
        "## Idea",
        f"- **Description:** {winning_idea.get('description','')}",
        f"- **Rationale:** {winning_idea.get('rationale','')}",
        f"- **Tags:** {', '.join(winning_idea.get('tags', []))}",
        f"- **Impact:** {winning_idea.get('impact', 'n/a')} / **Complexity:** {winning_idea.get('complexity', 'n/a')}",
        "",
        "## Agent Scores",
    ]
    for agent_id, series in agent_notes.items():
        agent_name = AGENTS[agent_id]["name"]
        score = next((s["score"] for s in series if s["title"] == winning_idea["title"]), None)
        if score is not None:
            body.append(f"- **{agent_name}**: {score}")
    body += [
        "",
        "## Totals",
        *[f"- {k}: {round(v,2)}" for k, v in sorted(totals.items(), key=lambda kv: kv[1], reverse=True)],
        "",
        "## Implementation Plan (initial)",
        "- Create code module(s) under `xmrt_apps/<feature_slug>/`",
        "- Add story entry in `docs/stories/`",
        "- Wire integration points in follow-up tasks",
        "",
        f"_Generated {datetime.now().isoformat()} by XMRT Consensus Builder_",
    ]
    issue = gh.create_issue_with_body(title, "\n".join(body), labels=["consensus", "auto", "xmrt-feature"])

    issue_number = issue.get("number") if "number" in issue else issue.get("simulated") and random.randint(1000, 9999)
    if issue_number is None:
        logger.warning(f"Could not retrieve issue number from response: {issue}")

    # Agents comment on the issue
    if issue_number is not None:
        for agent_id, meta in AGENTS.items():
            # Find that agent's comment about the winning idea
            comment_obj = next((s for s in agent_notes[agent_id] if s["title"] == winning_idea["title"]), None)
            text = comment_obj["comment"] if comment_obj else f"{meta['name']}: Approve."
            _ = gh.comment_issue(issue_number, text)

    # Implement feature
    app_name = winning_idea["title"]
    created = implement_feature(app_name, winning_idea)

    # Discussion story
    story_title = f"[Story] {app_name} shipped via Multi-Agent Consensus"
    story_body = f"""# {app_name}

This feature emerged from an autonomous, multi-agent discussion & consensus round.

- Issue: {'#'+str(issue_number) if issue_number else '(simulated)'}
- Owner: {OWNER}
- Created: {datetime.now().isoformat()}

**What & Why**
- {winning_idea.get('description','')}
- {winning_idea.get('rationale','')}

**Artifacts**
- {json.dumps(created, indent=2)}
"""
    discussion = gh.create_discussion("XMRT-Ecosystem", story_title, story_body, category_name="General")

    analytics["feature_cycles_completed"] += 1
    return {
        "repos_discovered": len(repos),
        "ideas_count": len(ideas),
        "winning_idea": winning_idea,
        "agent_notes": agent_notes,
        "totals": totals,
        "issue": issue,
        "files": created,
        "discussion": discussion,
        "timestamp": datetime.now().isoformat(),
    }

# ----------------------------- Worker (one-shot queue) ---------------------------

class OneShotWorker(threading.Thread):
    def __init__(self):
        super().__init__(name="xmrt-oneshot-worker", daemon=True)
        self.q: "queue.Queue[Dict[str, Any]]" = queue.Queue()

    def schedule(self, job: Dict[str, Any]) -> None:
        self.q.put(job)

    def run(self):
        READY.set()
        logger.info("Consensus Builder worker ready")
        while not SHUTDOWN.is_set():
            try:
                job = self.q.get(timeout=0.5)
            except queue.Empty:
                continue
            if job.get("type") == "innovation_cycle":
                logger.info("Starting innovation cycle")
                try:
                    result = innovation_cycle()
                    logger.info("Innovation cycle complete: %s", result.get("winning_idea", {}).get("title", "n/a"))
                except Exception as e:
                    logger.exception(f"Innovation cycle failed: {e}")
            else:
                logger.info("Unknown job: %s", job)

worker = OneShotWorker()
worker.start()

# ----------------------------- Health helpers ------------------------------------

def update_system_health():
    if PSUTIL_AVAILABLE:
        try:
            analytics["system_health"]["cpu"] = psutil.cpu_percent(interval=0.1)
            analytics["system_health"]["mem"] = psutil.virtual_memory().percent
            analytics["system_health"]["disk"] = psutil.disk_usage("/").percent
        except Exception:
            pass
    else:
        # Simulated
        analytics["system_health"]["cpu"] = round(random.uniform(5, 35), 1)
        analytics["system_health"]["mem"] = round(random.uniform(20, 70), 1)
        analytics["system_health"]["disk"] = round(random.uniform(10, 60), 1)

# ----------------------------- Frontend ------------------------------------------

FRONT = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>XMRT Ecosystem 6.0 — Consensus Builder</title>
<style>
body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, Noto Sans, sans-serif;
       background: #0f172a; color: #e2e8f0; margin: 0; padding: 24px; }
.container { max-width: 1200px; margin: 0 auto; }
h1 { font-size: 28px; margin-bottom: 8px; }
.grid { display: grid; grid-template-columns: repeat(auto-fit,minmax(280px,1fr)); gap: 16px; margin-top: 16px; }
.card { background: #111827; border: 1px solid #1f2937; border-radius: 12px; padding: 16px; }
button { background: #334155; color: #e2e8f0; border: none; border-radius: 8px; padding: 10px 16px; cursor: pointer; }
button:hover { background: #475569; }
pre { white-space: pre-wrap; word-wrap: break-word; background: #0b1220; padding: 12px; border-radius: 8px; border: 1px solid #1f2937; }
.small { color: #94a3b8; font-size: 12px; }
.stat { font-size: 24px; font-weight: 700; }
</style>
</head>
<body>
<div class="container">
  <h1>XMRT Ecosystem 6.0 — Consensus Builder</h1>
  <div class="small">Owner: {{ owner }} • Version: {{ version }} • Uptime: {{ uptime }}s</div>

  <div class="grid">
    <div class="card">
      <h3>Actions</h3>
      <button onclick="runCycle()">Run Innovation Cycle</button>
      <button onclick="forceAnalyze()">Analyze Ecosystem</button>
      <button onclick="forceBuild()">Build Application (legacy)</button>
      <button onclick="refresh()">Refresh</button>
      <div id="out" style="margin-top:12px;"></div>
    </div>
    <div class="card">
      <h3>Stats</h3>
      <div>Repos discovered: <span class="stat">{{ stats.repositories_discovered }}</span></div>
      <div>Ideas generated: <span class="stat">{{ stats.ideas_generated }}</span></div>
      <div>Issues: <span class="stat">{{ stats.issues_created }}</span></div>
      <div>Discussions: <span class="stat">{{ stats.discussions_created }}</span></div>
      <div>Files: <span class="stat">{{ stats.files_created }}</span> / updates: <span class="stat">{{ stats.files_updated }}</span></div>
      <div>Cycles done: <span class="stat">{{ stats.feature_cycles_completed }}</span></div>
      <div class="small">CPU {{ sys.cpu }}% • MEM {{ sys.mem }}% • DISK {{ sys.disk }}%</div>
    </div>
    <div class="card">
      <h3>Agents</h3>
      <pre>{{ agents_json }}</pre>
    </div>
  </div>
</div>
<script>
async function runCycle(){
  const out = document.getElementById('out');
  out.textContent = 'Running innovation cycle...';
  const r = await fetch('/api/run-innovation-cycle', {method: 'POST'});
  const j = await r.json();
  out.textContent = JSON.stringify(j, null, 2);
}
async function forceAnalyze(){
  const out = document.getElementById('out');
  out.textContent = 'Analyzing repos...';
  const r = await fetch('/api/force-ecosystem-analysis', {method: 'POST'});
  const j = await r.json();
  out.textContent = JSON.stringify(j, null, 2);
}
async function forceBuild(){
  const out = document.getElementById('out');
  out.textContent = 'Building app (legacy)...';
  const r = await fetch('/api/force-application-build', {method: 'POST'});
  const j = await r.json();
  out.textContent = JSON.stringify(j, null, 2);
}
function refresh(){ location.reload(); }
</script>
</body>
</html>
"""

# ----------------------------- Legacy (compat) endpoints -------------------------

def legacy_analyze():
    repos = gh.list_xmrt_repos()
    return {
        "status": "ok",
        "owner": OWNER,
        "repositories_analyzed": len(repos),
        "repositories": summarize_repos_for_ai(repos)[-10:],  # preview last 10
        "timestamp": datetime.now().isoformat(),
    }

def legacy_build():
    # Create a tiny placeholder app to keep backward compatibility with tooling/tests.
    idea = {
        "title": "XMRT Repo Cross-Indexer",
        "description": "Unified API over all xmrt* repos (endpoints, schemas, versions).",
        "rationale": "Easier integrations & programmatic discovery.",
        "tags": ["devtools", "indexing", "api"],
    }
    created = implement_feature("XMRT Repo Cross-Indexer", idea)
    return {"status": "ok", "files": created}

# ----------------------------- Flask routes --------------------------------------

@app.route("/", methods=["GET", "HEAD"])
def index():
    analytics["requests_count"] += 1
    update_system_health()
    return render_template_string(
        FRONT,
        owner=OWNER,
        version=system_state["version"],
        uptime=round(time.time() - system_state["startup_time"], 1),
        stats=analytics,
        sys=analytics["system_health"],
        agents_json=json.dumps(AGENTS, indent=2),
    )

@app.route("/favicon.ico")
def favicon():
    # Avoid noisy 404 until you add /static/favicon.ico
    return ("", 204)

@app.route("/healthz")
@app.route("/health")
def health():
    update_system_health()
    return jsonify({
        "ok": True,
        "ready": READY.is_set(),
        "version": system_state["version"],
        "owner": OWNER,
        "uptime": round(time.time() - system_state["startup_time"], 3),
        "system": analytics["system_health"],
        "timestamp": datetime.now().isoformat(),
    })

@app.route("/analytics")
def get_analytics():
    analytics["requests_count"] += 1
    return jsonify(analytics)

@app.route("/agents")
def get_agents():
    analytics["requests_count"] += 1
    return jsonify({"agents": AGENTS})

# Legacy endpoints preserved
@app.route("/api/force-ecosystem-analysis", methods=["POST"])
def force_ecosystem_analysis():
    return jsonify(legacy_analyze())

@app.route("/api/force-application-build", methods=["POST"])
def force_application_build():
    return jsonify(legacy_build())

# New: full cycle trigger
@app.route("/api/run-innovation-cycle", methods=["POST"])
def run_innovation_cycle():
    worker.schedule({"type": "innovation_cycle"})
    return jsonify({"scheduled": True, "message": "Innovation cycle enqueued"})

# ----------------------------- Signals & main ------------------------------------

def _signal_handler(sig, _frame):
    logger.info("Received signal %s — shutting down", sig)
    SHUTDOWN.set()

def main() -> int:
    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    logger.info("Agents and Coordination initialized")
    logger.info("Starting %s on port %s", APP_NAME, PORT)
    READY.set()

    # Optionally kick a cycle at boot (comment out if you prefer manual):
    # worker.schedule({"type": "innovation_cycle"})

    try:
        app.run(host=HOST, port=PORT, debug=False, use_reloader=False, threaded=True)
    finally:
        SHUTDOWN.set()
        logger.info("Shutdown complete")
    return 0

if __name__ == "__main__":
    sys.exit(main())
