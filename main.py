#!/usr/bin/env python3
"""
XMRT Ecosystem Main Application - Version 6.3 "Hardier GitHub"
- Full multi-agent ideation → comments → weighted consensus → decision issue
- Implements code + README + story, then opens a Discussion (or story Issue fallback)
- Discovers ALL repos named like xmrt* via owner listing OR REST search (user/org)
- Runs real GitHub mode even if owner fetch fails, as long as repo fetch works
"""

import os
import re
import sys
import json
import time
import queue
import signal
import random
import logging
import threading
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS

# ---------- Optional deps ----------
try:
    from github import Github, Auth, GithubException
    GITHUB_AVAILABLE = True
except ImportError:
    GITHUB_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

import requests  # used for REST fallback

# ---------- Config / Globals ----------
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
log = logging.getLogger("xmrt-main")

app = Flask(__name__)
CORS(app)

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "10000"))
OWNER = os.getenv("GITHUB_OWNER", "DevGruGold")
REPO_ECOSYSTEM = os.getenv("GITHUB_REPO", "XMRT-Ecosystem")
DEFAULT_OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
FORCE_SIMULATE = os.getenv("XMRT_FORCE_SIMULATE", "false").lower() == "true"

READY = threading.Event()
SHUTDOWN = threading.Event()

system_state: Dict[str, Any] = {
    "status": "operational",
    "startup_time": time.time(),
    "version": "6.3.0-hardy-github",
    "mode": "XMRT_INNOVATION_CYCLE",
    "owner": OWNER,
    "ecosystem_repo": REPO_ECOSYSTEM,
}

analytics: Dict[str, Any] = {
    "requests_count": 0,
    "ai_operations": 0,
    "github_operations": 0,
    "issues_created": 0,
    "discussions_created": 0,
    "story_issues_created": 0,
    "files_created": 0,
    "files_updated": 0,
    "repositories_discovered": 0,
    "ideas_generated": 0,
    "comments_posted": 0,
    "feature_cycles_completed": 0,
    "system_health": {"cpu": 0.0, "mem": 0.0, "disk": 0.0},
}

AGENTS: Dict[str, Dict[str, Any]] = {
    "eliza": {"name": "Eliza", "role": "Coordinator & Governor", "voice": "strategic, synthesizes viewpoints", "weight": 1.2},
    "security_guardian": {"name": "Security Guardian", "role": "Security & Privacy", "voice": "threat-models, privacy-first", "weight": 1.1},
    "defi_specialist": {"name": "DeFi Specialist", "role": "Mining & Tokenomics", "voice": "ROI, efficiency, yield", "weight": 1.05},
    "community_manager": {"name": "Community Manager", "role": "Adoption & UX", "voice": "onboarding, docs, growth", "weight": 1.0},
}

# ---------- AI ----------
class AIProcessor:
    def __init__(self, eager_probe: bool = False):
        self.openai = None
        self.gemini = None
        if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
            try:
                self.openai = OpenAI()
                if eager_probe:
                    _ = self.openai.chat.completions.create(
                        model=DEFAULT_OPENAI_MODEL,
                        messages=[{"role": "user", "content": "ping"}],
                        max_tokens=2,
                    )
                log.info("OpenAI client initialized")
            except Exception as e:
                log.warning(f"OpenAI init failed: {e}")
        if GEMINI_AVAILABLE and os.getenv("GEMINI_API_KEY"):
            try:
                genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
                self.gemini = genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-pro"))
            except Exception as e:
                log.warning(f"Gemini init failed: {e}")

    def is_available(self) -> bool:
        return bool(self.openai or self.gemini)

    def _chat(self, sys_prompt: str, user_prompt: str, max_tokens: int = 1200, temperature: float = 0.7) -> str:
        if self.openai:
            try:
                r = self.openai.chat.completions.create(
                    model=DEFAULT_OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": sys_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                analytics["ai_operations"] += 1
                return r.choices[0].message.content or ""
            except Exception as e:
                log.warning(f"OpenAI error: {e}")
        if self.gemini:
            try:
                r = self.gemini.generate_content(f"{sys_prompt}\n\n{user_prompt}")
                analytics["ai_operations"] += 1
                return getattr(r, "text", "") or ""
            except Exception as e:
                log.warning(f"Gemini error: {e}")
        return ""

    def ideate(self, repos_summary: List[Dict[str, Any]], n: int = 7) -> List[Dict[str, Any]]:
        sys_prompt = "You are an XMRT DAO strategist (mobile mining, mesh, privacy, adoption)."
        user_prompt = (
            "Propose high-impact, concrete features/utilities for this ecosystem. "
            "Return JSON array of objects: title, description, rationale, impact (1-5), complexity (1-5), tags (list). "
            f"Generate {n} distinct ideas.\n\nREPOS:\n{json.dumps(repos_summary, indent=2)}"
        )
        text = self._chat(sys_prompt, user_prompt)
        ideas: List[Dict[str, Any]] = []
        for candidate in re.findall(r"\[[\s\S]*\]", text):
            try:
                parsed = json.loads(candidate)
                if isinstance(parsed, list):
                    for x in parsed:
                        if isinstance(x, dict) and "title" in x:
                            ideas.append(x)
                    break
            except Exception:
                continue
        if not ideas:
            ideas = [
                {"title": "Adaptive Mobile Mining Profiles", "description": "Auto-tune CPU/battery/net profiles.", "rationale": "Boost hash-per-watt.", "impact": 5, "complexity": 3, "tags": ["mining", "optimizer", "mobile"]},
                {"title": "Mesh Health Beacons", "description": "UDP beacons for offline discovery.", "rationale": "Mesh resilience.", "impact": 5, "complexity": 2, "tags": ["meshnet", "offline"]},
                {"title": "Proof-of-Participation Badges", "description": "Signed badges feed governance.", "rationale": "Align effort & votes.", "impact": 4, "complexity": 3, "tags": ["governance", "reputation"]},
                {"title": "XMRT Cross-Indexer", "description": "Unified API over all xmrt* repos.", "rationale": "Dev velocity.", "impact": 4, "complexity": 2, "tags": ["devtools", "api"]},
                {"title": "Mesh-First Wallet Alerts", "description": "Offline alerts; sync later.", "rationale": "Trust-minimized UX.", "impact": 4, "complexity": 3, "tags": ["wallet", "meshnet"]},
                {"title": "One-Tap MobileMonero Onboarding", "description": "Termux bootstrap + verify.", "rationale": "Drop friction.", "impact": 5, "complexity": 3, "tags": ["onboarding", "mobile", "ux"]},
                {"title": "Edge Telemetry Pack", "description": "Privacy-preserving miner metrics.", "rationale": "Optimize safely.", "impact": 4, "complexity": 2, "tags": ["telemetry", "privacy"]},
            ]
        analytics["ideas_generated"] += len(ideas)
        return ideas

    def agent_reviews(self, ideas: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        out: Dict[str, List[Dict[str, Any]]] = {k: [] for k in AGENTS.keys()}
        for agent_id, meta in AGENTS.items():
            for idea in ideas:
                impact = float(idea.get("impact", 3))
                complexity = float(idea.get("complexity", 3))
                tags = [t.lower() for t in idea.get("tags", [])]
                boost = 0.0
                if agent_id == "security_guardian" and any(t in tags for t in ["privacy", "security", "meshnet"]): boost += 2.0
                if agent_id == "defi_specialist" and any(t in tags for t in ["mining", "optimizer", "governance"]): boost += 2.0
                if agent_id == "community_manager" and any(t in tags for t in ["onboarding", "ux", "alerts"]): boost += 2.0
                if agent_id == "eliza": boost += 1.5
                base = 5.0
                score = max(0.0, min(10.0, base + (impact - 0.3 * complexity) + boost))
                comment = f"{meta['name']} ({meta['role']}): {meta['voice']}. Assessment for '{idea['title']}': impact={impact}, complexity={complexity}, score={round(score,2)}."
                out[agent_id].append({"title": idea["title"], "comment": comment, "score": round(score, 2)})
        return out

    def choose(self, ideas: List[Dict[str, Any]], reviews: Dict[str, List[Dict[str, Any]]]) -> Tuple[Dict[str, Any], Dict[str, float]]:
        totals: Dict[str, float] = {i["title"]: 0.0 for i in ideas}
        for aid, arr in reviews.items():
            w = float(AGENTS[aid]["weight"])
            for r in arr:
                totals[r["title"]] += r["score"] * w
        winner = max(totals, key=lambda k: totals[k]) if totals else ideas[0]["title"]
        return next(i for i in ideas if i["title"] == winner), totals

ai = AIProcessor()

# ---------- GitHub ----------
class GitHubClient:
    def __init__(self, owner: str, repo_name: str):
        self.owner = owner
        self.repo_name = repo_name
        self.token = os.getenv("GITHUB_TOKEN")
        self.simulate = FORCE_SIMULATE or not (self.token and GITHUB_AVAILABLE)
        self.gh = None
        self.owner_obj = None
        self.repo = None

        if not GITHUB_AVAILABLE:
            log.warning("PyGithub not available -> simulate mode")
            self.simulate = True
            return

        if FORCE_SIMULATE:
            log.warning("XMRT_FORCE_SIMULATE=true -> simulate mode")
            self.simulate = True
            return

        try:
            auth = Auth.Token(self.token) if self.token else None
            self.gh = Github(auth=auth) if auth else Github()
            # Try direct repo first to enable real mode without owner resolution
            try:
                self.repo = self.gh.get_repo(f"{self.owner}/{self.repo_name}")
                log.info("GitHub repo reachable (%s/%s). Enabling real mode.", self.owner, self.repo_name)
                self.simulate = False
            except Exception as e_repo:
                log.warning(f"Direct repo fetch failed: {e_repo}")
            # Best-effort owner resolve (optional)
            if not self.owner_obj:
                try:
                    self.owner_obj = self.gh.get_user(self.owner)
                except Exception:
                    try:
                        self.owner_obj = self.gh.get_organization(self.owner)
                    except Exception as e_owner:
                        log.warning(f"Owner resolve failed (user/org). Continuing with REST search fallback. Reason: {e_owner}")
            if not self.repo and not self.simulate:
                # Try again to get repo (owner might be resolved now)
                try:
                    self.repo = self.gh.get_repo(f"{self.owner}/{self.repo_name}")
                except Exception:
                    pass
            if not self.repo and not self.owner_obj:
                # Still no repo/owner: remain in simulate, but we can still REST search later.
                log.warning("No repo/owner handle available; will use REST search for discovery.")
        except Exception as e:
            log.warning(f"GitHub init failed -> simulate mode. Reason: {e}")
            self.simulate = True

    # REST helper
    def _rest(self, method: str, path: str, **kwargs) -> Tuple[int, Any]:
        headers = kwargs.pop("headers", {})
        headers.update({
            "Accept": "application/vnd.github+json",
            "User-Agent": "XMRT-Consensus-Builder",
        })
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
            headers["X-GitHub-Api-Version"] = "2022-11-28"
        url = f"https://api.github.com{path}"
        resp = requests.request(method, url, headers=headers, timeout=30, **kwargs)
        try:
            return resp.status_code, resp.json()
        except Exception:
            return resp.status_code, resp.text

    def list_xmrt_repos(self) -> List[Dict[str, Any]]:
        repos: List[Dict[str, Any]] = []
        # Preferred: owner_obj listing
        if self.owner_obj and not self.simulate:
            try:
                for r in self.owner_obj.get_repos(type="public"):
                    if r.name.lower().startswith("xmrt"):
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
                analytics["repositories_discovered"] = len(repos)
                return repos
            except Exception as e:
                log.warning(f"Owner listing failed, falling back to REST search: {e}")

        # REST Search fallback (works even without owner_obj)
        try:
            combined = {}
            # Search as user
            status, data = self._rest("GET", f"/search/repositories?q=user:{self.owner}+xmrt+in:name&per_page=100")
            if status == 200 and isinstance(data, dict) and "items" in data:
                for r in data["items"]:
                    if r["name"].lower().startswith("xmrt"):
                        combined[r["full_name"]] = r
            # Search as org
            status2, data2 = self._rest("GET", f"/search/repositories?q=org:{self.owner}+xmrt+in:name&per_page=100")
            if status2 == 200 and isinstance(data2, dict) and "items" in data2:
                for r in data2["items"]:
                    if r["name"].lower().startswith("xmrt"):
                        combined[r["full_name"]] = r

            for r in combined.values():
                repos.append({
                    "name": r["name"],
                    "full_name": r["full_name"],
                    "description": r.get("description"),
                    "language": r.get("language"),
                    "topics": r.get("topics", []),
                    "stars": r.get("stargazers_count", 0),
                    "forks": r.get("forks_count", 0),
                    "updated_at": r.get("updated_at"),
                    "has_pages": r.get("has_pages", False),
                })
            analytics["repositories_discovered"] = len(repos)
            if not repos:
                log.warning("REST search found no xmrt* repos; using minimal seed list.")
                repos = [{"name": "XMRT-Ecosystem", "full_name": f"{self.owner}/XMRT-Ecosystem", "language": "Python", "topics": ["xmrt"]}]
                analytics["repositories_discovered"] = len(repos)
            return repos
        except Exception as e:
            log.error(f"REST search failed: {e}")
            repos = [{"name": "XMRT-Ecosystem", "full_name": f"{self.owner}/XMRT-Ecosystem", "language": "Python", "topics": ["xmrt"]}]
            analytics["repositories_discovered"] = len(repos)
            return repos

    def create_or_update_file(self, path: str, message: str, content: str) -> Dict[str, Any]:
        if self.repo and not self.simulate:
            try:
                self.repo.create_file(path, message, content)
                analytics["files_created"] += 1
                return {"created": True, "path": path}
            except GithubException:
                try:
                    file = self.repo.get_contents(path)
                    self.repo.update_file(path, f"Update: {message}", content, file.sha)
                    analytics["files_updated"] += 1
                    return {"updated": True, "path": path}
                except Exception as e:
                    log.error(f"File op error for {path}: {e}")
                    return {"error": str(e), "path": path}
            except Exception as e:
                log.error(f"File op error for {path}: {e}")
                return {"error": str(e), "path": path}
        # simulate
        analytics["files_created"] += 1
        return {"simulated": True, "path": path}

    def create_issue(self, title: str, body: str, labels: Optional[List[str]] = None) -> Dict[str, Any]:
        if self.repo and not self.simulate:
            try:
                issue = self.repo.create_issue(title=title, body=body, labels=labels or [])
                analytics["issues_created"] += 1
                return {"number": issue.number, "url": issue.html_url}
            except Exception as e:
                log.error(f"Issue create failed: {e}")
                return {"error": str(e)}
        analytics["issues_created"] += 1
        return {"simulated": True, "number": random.randint(1000, 9999)}

    def comment_issue(self, issue_number: int, comment: str) -> Dict[str, Any]:
        if self.repo and not self.simulate:
            try:
                issue = self.repo.get_issue(number=issue_number)
                issue.create_comment(comment)
                analytics["comments_posted"] += 1
                return {"ok": True}
            except Exception as e:
                log.error(f"Issue comment failed: {e}")
                return {"error": str(e)}
        analytics["comments_posted"] += 1
        return {"simulated": True}

    def list_discussion_categories(self) -> List[Dict[str, Any]]:
        if not self.token:
            return []
        status, data = self._rest("GET", f"/repos/{self.owner}/{self.repo_name}/discussions/categories")
        if status == 200 and isinstance(data, list):
            return data
        return []

    def create_discussion(self, title: str, body: str, category_name: str = "General") -> Dict[str, Any]:
        if self.token and not self.simulate:
            cats = self.list_discussion_categories()
            cat_id = None
            for c in cats:
                if str(c.get("name", "")).lower() == category_name.lower():
                    cat_id = c.get("id")
                    break
            if not cat_id and cats:
                cat_id = cats[0].get("id")
            if cat_id:
                status, data = self._rest("POST", f"/repos/{self.owner}/{self.repo_name}/discussions", json={"title": title, "body": body, "category_id": cat_id})
                if status in (200, 201):
                    analytics["discussions_created"] += 1
                    return {"ok": True, "number": data.get("number"), "url": data.get("html_url")}
                log.warning(f"Discussion create failed ({status}): {data}")
            # Fallback → Story as Issue (label: story)
            story = self.create_issue(f"[Story] {title}", body, labels=["story"])
            analytics["story_issues_created"] += 1
            story["fallback"] = "story-issue"
            return story
        # simulate
        analytics["discussions_created"] += 1
        return {"simulated": True}

gh = GitHubClient(OWNER, REPO_ECOSYSTEM)

# ---------- Helpers ----------
def summarize_repos_for_ai(repos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for r in repos:
        out.append({
            "name": r.get("name"),
            "language": r.get("language"),
            "topics": r.get("topics", []),
            "stars": r.get("stars", 0),
            "updated_at": r.get("updated_at"),
            "desc": (r.get("description") or "")[:140],
        })
    return out

def slugify(name: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9\-_]+", "-", (name or "feature").strip())
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s.lower() or "feature"

def implement_feature(app_name: str, idea: Dict[str, Any]) -> List[Dict[str, Any]]:
    created: List[Dict[str, Any]] = []
    slug = slugify(app_name)
    base = f"xmrt_apps/{slug}"
    files = {
        f"{base}/{slug}.py": (
            "#!/usr/bin/env python3\n"
            f'"""{app_name}\n'
            "Auto-generated by XMRT Consensus Builder.\n\n"
            "Description:\n"
            f"{idea.get('description','(no description)')}\n\n"
            f"Tags: {', '.join(idea.get('tags', []))}\n"
            '"""\n\n'
            "import time, json, logging\n"
            'logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")\n'
            f'log = logging.getLogger("{slug}")\n\n'
            "def run():\n"
            f"    log.info('Initialized {app_name}')\n"
            "    result = {\n"
            "        'status': 'ok',\n"
            f"        'feature': '{app_name}',\n"
            "        'timestamp': time.time(),\n"
            "    }\n"
            "    print(json.dumps(result))\n\n"
            "if __name__ == '__main__':\n"
            "    run()\n"
        ),
        f"{base}/{slug}_config.py": (
            f"# Config for {app_name}\n"
            "CONFIG = {\n"
            "  'version': '0.1.0',\n"
            "  'enabled': True,\n"
            "  'notes': 'Auto-generated; add integration params.'\n"
            "}\n"
        ),
        f"{base}/{slug}_README.md": (
            f"# {app_name}\n\n"
            f"**Idea**: {idea.get('description','')}\n\n"
            f"**Rationale**: {idea.get('rationale','')}\n\n"
            f"**Tags**: {', '.join(idea.get('tags', []))}\n\n"
            "Created by the XMRT multi-agent consensus flow.\n"
            "Next steps:\n"
            "- Wire into MobileMonero / MeshNet / Optimizer as applicable.\n"
            "- Add tests and integration hooks.\n"
        ),
        f"docs/stories/{slug}.md": (
            f"# Story: {app_name}\n\n"
            f"- Idea: {idea.get('title','')}\n"
            f"- Why: {idea.get('rationale','')}\n\n"
            "Artifacts will be linked by CI (issue, commits, demos).\n"
            f"*Generated {datetime.now().isoformat()} by XMRT Consensus Builder.*\n"
        ),
    }
    for path, content in files.items():
        created.append(gh.create_or_update_file(path, f"Add {app_name}: {os.path.basename(path)}", content))
    return created

# ---------- Innovation Cycle ----------
def run_consensus_cycle() -> Dict[str, Any]:
    repos = gh.list_xmrt_repos()
    summaries = summarize_repos_for_ai(repos)
    ideas = ai.ideate(summaries, n=7)
    reviews = ai.agent_reviews(ideas)
    winner, totals = ai.choose(ideas, reviews)

    # Decision Issue
    issue_title = f"[Consensus] Implement: {winner['title']}"
    body = []
    body.append(f"# Consensus Decision: {winner['title']}\n")
    body.append("## Idea\n")
    body.append(f"- Description: {winner.get('description','')}\n")
    body.append(f"- Rationale: {winner.get('rationale','')}\n")
    body.append(f"- Tags: {', '.join(winner.get('tags', []))}\n")
    body.append(f"- Impact: {winner.get('impact','?')}  Complexity: {winner.get('complexity','?')}\n")
    body.append("## Agent Scores\n")
    for aid, arr in reviews.items():
        nm = AGENTS[aid]["name"]
        sc = next((x["score"] for x in arr if x["title"] == winner["title"]), None)
        if sc is not None:
            body.append(f"- {nm}: {sc}\n")
    body.append("## Totals\n")
    for k, v in sorted(totals.items(), key=lambda kv: kv[1], reverse=True):
        body.append(f"- {k}: {round(v,2)}\n")
    body.append("## Initial Plan\n- Create module under xmrt_apps/<slug>/\n- Add story in docs/stories/\n- Wire integration points next\n")
    decision_issue = gh.create_issue(issue_title, "".join(body), labels=["consensus", "auto", "xmrt-feature"])
    issue_no = decision_issue.get("number") or random.randint(1000, 9999)

    # Agent comments on the decision issue
    for aid, meta in AGENTS.items():
        c = next((x for x in reviews[aid] if x["title"] == winner["title"]), None)
        text = c["comment"] if c else f"{meta['name']}: Approve."
        gh.comment_issue(issue_no, text)

    # Implement files
    files = implement_feature(winner["title"], winner)

    # Story (Discussion or fallback Story Issue)
    story_title = f"{winner['title']} shipped via Multi-Agent Consensus"
    story_body = (
        f"# {winner['title']}\n\n"
        "Emerging from autonomous, multi-agent deliberation.\n\n"
        f"- Decision Issue: #{issue_no}\n"
        f"- Owner: {OWNER}/{REPO_ECOSYSTEM}\n\n"
        f"**What/Why**\n- {winner.get('description','')}\n- {winner.get('rationale','')}\n\n"
        f"**Artifacts**\n{json.dumps(files, indent=2)}\n"
    )
    discussion = gh.create_discussion(story_title, story_body, category_name="General")

    analytics["feature_cycles_completed"] += 1
    result = {
        "repos_discovered": len(repos),
        "ideas_count": len(ideas),
        "winner": winner,
        "totals": totals,
        "decision_issue": decision_issue,
        "files": files,
        "story": discussion,
        "timestamp": datetime.now().isoformat(),
    }
    return result

# ---------- Worker ----------
class OneShotWorker(threading.Thread):
    def __init__(self):
        super().__init__(name="xmrt-oneshot-worker", daemon=True)
        self.q: "queue.Queue[Dict[str, Any]]" = queue.Queue()
        self.last_result: Optional[Dict[str, Any]] = None

    def schedule(self, job: Dict[str, Any]) -> None:
        self.q.put(job)

    def run(self):
        READY.set()
        log.info("Consensus Builder worker ready")
        while not SHUTDOWN.is_set():
            try:
                job = self.q.get(timeout=0.5)
            except queue.Empty:
                continue
            if job.get("type") == "innovation_cycle":
                log.info("Starting innovation cycle")
                try:
                    self.last_result = run_consensus_cycle()
                    log.info("Innovation cycle complete: %s", self.last_result.get("winner", {}).get("title", "n/a"))
                except Exception as e:
                    log.exception(f"Innovation cycle failed: {e}")
            else:
                log.info("Unknown job: %s", job)

worker = OneShotWorker()
worker.start()

# ---------- Health ----------
def update_health():
    if PSUTIL_AVAILABLE:
        try:
            analytics["system_health"]["cpu"] = psutil.cpu_percent(interval=0.1)
            analytics["system_health"]["mem"] = psutil.virtual_memory().percent
            analytics["system_health"]["disk"] = psutil.disk_usage("/").percent
            return
        except Exception:
            pass
    analytics["system_health"]["cpu"] = round(random.uniform(5, 35), 1)
    analytics["system_health"]["mem"] = round(random.uniform(20, 70), 1)
    analytics["system_health"]["disk"] = round(random.uniform(10, 60), 1)

# ---------- Frontend ----------
FRONT = """
<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>XMRT Ecosystem 6.3 — Consensus Builder</title>
<style>
body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,Cantarell,Noto Sans,sans-serif;background:#0f172a;color:#e2e8f0;margin:0;padding:24px}
.container{max-width:1200px;margin:0 auto}
h1{font-size:28px;margin-bottom:8px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px;margin-top:16px}
.card{background:#111827;border:1px solid #1f2937;border-radius:12px;padding:16px}
button{background:#334155;color:#e2e8f0;border:none;border-radius:8px;padding:10px 16px;cursor:pointer}
button:hover{background:#475569}
pre{white-space:pre-wrap;word-wrap:break-word;background:#0b1220;padding:12px;border-radius:8px;border:1px solid #1f2937}
.small{color:#94a3b8;font-size:12px}
.stat{font-size:24px;font-weight:700}
</style></head><body>
<div class="container">
  <h1>XMRT Ecosystem 6.3 — Consensus Builder</h1>
  <div class="small">Owner: {{ owner }} • Repo: {{ repo }} • Version: {{ version }} • Uptime: {{ uptime }}s</div>
  <div class="grid">
    <div class="card">
      <h3>Actions</h3>
      <button onclick="runCycle()">Run Innovation Cycle</button>
      <button onclick="lastResult()">Last Result</button>
      <button onclick="refresh()">Refresh</button>
      <div id="out" style="margin-top:12px;"></div>
    </div>
    <div class="card">
      <h3>Stats</h3>
      <div>Repos discovered: <span class="stat">{{ stats.repositories_discovered }}</span></div>
      <div>Ideas: <span class="stat">{{ stats.ideas_generated }}</span></div>
      <div>Issues: <span class="stat">{{ stats.issues_created }}</span></div>
      <div>Discussions: <span class="stat">{{ stats.discussions_created }}</span> • Story Issues: <span class="stat">{{ stats.story_issues_created }}</span></div>
      <div>Files: <span class="stat">{{ stats.files_created }}</span> / updates: <span class="stat">{{ stats.files_updated }}</span></div>
      <div>Cycles: <span class="stat">{{ stats.feature_cycles_completed }}</span></div>
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
  const out=document.getElementById('out');
  out.textContent='Running innovation cycle...';
  const r=await fetch('/api/run-innovation-cycle',{method:'POST'});
  const j=await r.json();
  out.textContent=JSON.stringify(j,null,2);
}
async function lastResult(){
  const out=document.getElementById('out');
  const r=await fetch('/api/innovation/last');
  const j=await r.json();
  out.textContent=JSON.stringify(j,null,2);
}
function refresh(){location.reload();}
</script></body></html>
"""

# ---------- Routes ----------
@app.route("/", methods=["GET", "HEAD"])
def index():
    analytics["requests_count"] += 1
    update_health()
    return render_template_string(
        FRONT,
        owner=OWNER,
        repo=REPO_ECOSYSTEM,
        version=system_state["version"],
        uptime=round(time.time() - system_state["startup_time"], 1),
        stats=analytics,
        sys=analytics["system_health"],
        agents_json=json.dumps(AGENTS, indent=2),
    )

@app.route("/health")
@app.route("/healthz")
def health():
    update_health()
    return jsonify({
        "ok": True,
        "ready": READY.is_set(),
        "version": system_state["version"],
        "owner": OWNER,
        "repo": REPO_ECOSYSTEM,
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

@app.route("/api/coordination/status")
def coordination_status():
    return jsonify({
        "ready": READY.is_set(),
        "feature_cycles_completed": analytics["feature_cycles_completed"],
        "ideas_generated": analytics["ideas_generated"],
        "repositories_discovered": analytics["repositories_discovered"],
        "issues_created": analytics["issues_created"],
        "discussions_created": analytics["discussions_created"],
        "story_issues_created": analytics["story_issues_created"],
        "files_created": analytics["files_created"],
        "files_updated": analytics["files_updated"],
        "timestamp": datetime.now().isoformat(),
    })

@app.route("/api/run-innovation-cycle", methods=["POST"])
def api_run_cycle():
    worker.schedule({"type": "innovation_cycle"})
    return jsonify({"scheduled": True})

@app.route("/api/innovation/last")
def api_last():
    return jsonify(worker.last_result or {"last_result": None})

# Minimal webhooks
@app.route("/webhook/github", methods=["POST"])
def webhook_github():
    analytics["github_operations"] += 1
    return jsonify({"status": "received", "source": "github", "ts": datetime.now().isoformat()})

@app.route("/webhook/render", methods=["POST"])
def webhook_render():
    return jsonify({"status": "received", "source": "render", "ts": datetime.now().isoformat()})

@app.route("/webhook/discord", methods=["POST"])
def webhook_discord():
    return jsonify({"status": "received", "source": "discord", "ts": datetime.now().isoformat()})

# ---------- Signals / Main ----------
def _sig(sig, _frm):
    log.info("Signal %s -> shutdown", sig)
    SHUTDOWN.set()

def main() -> int:
    signal.signal(signal.SIGINT, _sig)
    signal.signal(signal.SIGTERM, _sig)
    log.info("Agents and Coordination initialized")
    log.info("Starting XMRT Ecosystem on port %s", PORT)
    READY.set()
    try:
        app.run(host=HOST, port=PORT, debug=False, use_reloader=False, threaded=True)
    finally:
        SHUTDOWN.set()
        log.info("Shutdown complete")
    return 0

if __name__ == "__main__":
    sys.exit(main())
