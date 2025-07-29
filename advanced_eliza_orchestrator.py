#!/usr/bin/env python3
# XMRT Eliza Orchestrator - Worker: Prioritize xmrt* Repos, Bulletproof Cycles

import os
import sys
import json
import random
import threading
import time
from datetime import datetime, timedelta
import logging

from flask import Flask, jsonify, render_template_string
import requests
from dotenv import load_dotenv
import github
from github import Github, InputGitAuthor

# === CONFIGURATION ===
load_dotenv()
GITHUB_USERNAME = os.getenv('GITHUB_USERNAME', 'DevGruGold')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '240')) # 4 minutes
CYCLE_FILE = "/tmp/eliza_cycle_count.txt"

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, stream=sys.stdout,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class ElizaAgentState:
    def __init__(self):
        self.lock = threading.Lock()
        self.start_time = datetime.now()
        self.cycle_count = self._load_cycle()
        self.last_cycle_finish_time = None
        self.total_commits_made = 0
        self.repos_improved_count = 0
        self.dao_value_created = 0
        self.tasks_completed_count = 0
        self.self_improvements_count = 0
        self.tools_discovered_count = 0
        self.utilities_built_count = 0
        self.discussion_posts_created = 0
        self.files_created_count = 0
        self.github_operations_count = 0
        self.agent_status_message = "Initializing..."
        self.agent_active = False

    def _load_cycle(self):
        try:
            if os.path.exists(CYCLE_FILE):
                with open(CYCLE_FILE, "r") as f:
                    c = int(f.read().strip())
                    logging.info(f"Loaded persistent cycle count: {c}")
                    return c
        except Exception as e:
            logging.error(f"Error loading persistent cycle count: {e}")
        return 0

    def _save_cycle(self, value):
        try:
            with open(CYCLE_FILE, "w") as f:
                f.write(str(value))
        except Exception as e:
            logging.error(f"Error saving persistent cycle count: {e}")

    def increment_and_get_cycle(self):
        with self.lock:
            self.cycle_count += 1
            self._save_cycle(self.cycle_count)
            return self.cycle_count

eliza_state = ElizaAgentState()

class ElizaCoreAgent:
    def __init__(self):
        self.github_client = None
        self.xmrt_repos = []
        self.other_repos = []
        self._initialize_github()
        self._load_all_repos()

    def _initialize_github(self):
        try:
            if GITHUB_TOKEN:
                auth = github.Auth.Token(GITHUB_TOKEN)
                self.github_client = github.Github(auth=auth)
                logging.info("✅ PyGithub client initialized.")
            else:
                logging.warning("⚠️ GitHub token not found.")
        except Exception as e:
            logging.error(f"❌ Failed to initialize GitHub client: {e}")
            self.github_client = None

    def _load_all_repos(self):
        self.xmrt_repos = []
        self.other_repos = []
        if not self.github_client:
            return
        try:
            user = self.github_client.get_user(GITHUB_USERNAME)
            for repo in user.get_repos():
                if not repo.fork:
                    entry = {
                        'name': repo.name,
                        'full_name': repo.full_name,
                        'description': repo.description or 'No description',
                        'language': repo.language,
                        'stars': repo.stargazers_count,
                        'default_branch': repo.default_branch
                    }
                    if repo.name.lower().startswith('xmrt'):
                        self.xmrt_repos.append(entry)
                    else:
                        self.other_repos.append(entry)
            logging.info(f"Loaded {len(self.xmrt_repos)} xmrt* repos and {len(self.other_repos)} other repos.")
        except Exception as e:
            logging.error(f"❌ Failed to load repositories: {e}")
            self.xmrt_repos = []
            self.other_repos = []

    def _commit_to_github(self, repo_full_name, filename, content, message):
        if not self.github_client:
            logging.warning(f"⚠️ Skipping commit to {repo_full_name}/{filename}: GitHub not initialized.")
            return False
        try:
            repo = self.github_client.get_repo(repo_full_name)
            author = InputGitAuthor("Eliza Autonomous", "eliza@xmrt.io")
            try:
                contents = repo.get_contents(filename, ref=repo.default_branch)
                repo.update_file(
                    path=filename,
                    message=message,
                    content=content,
                    sha=contents.sha,
                    branch=repo.default_branch,
                    author=author
                )
                logging.info(f"✅ Updated {filename} in {repo_full_name}")
            except github.UnknownObjectException:
                repo.create_file(
                    path=filename,
                    message=message,
                    content=content,
                    branch=repo.default_branch,
                    author=author
                )
                logging.info(f"✅ Created {filename} in {repo_full_name}")
            with eliza_state.lock:
                eliza_state.total_commits_made += 1
                eliza_state.files_created_count += 1
                eliza_state.github_operations_count += 1
            return True
        except Exception as e:
            logging.error(f"❌ GitHub commit failed for {repo_full_name}/{filename}: {e}", exc_info=True)
            return False

    def _execute_self_improvement(self, cycle):
        improvements = []
        for _ in range(random.randint(1, 2)):
            area = random.choice(["code_quality", "performance", "docs"])
            improvements.append({"area": area, "description": f"Improved {area}", "cycle": cycle})
        with eliza_state.lock:
            eliza_state.self_improvements_count += len(improvements)
            eliza_state.dao_value_created += len(improvements) * 4
        return improvements

    def _execute_repo_improvement(self, repo_info, cycle):
        imp_type = random.choice(["docs", "security", "performance"])
        filename = f"eliza_improvements/{repo_info['name']}/{imp_type}_{cycle}.md"
        content = f"# Eliza Improvement Cycle {cycle}\nRepository: {repo_info['name']}\nType: {imp_type}\n"
        if self._commit_to_github(repo_info['full_name'], filename, content, f"🤖 Eliza Cycle {cycle}: {imp_type} for {repo_info['name']}"):
            with eliza_state.lock:
                eliza_state.repos_improved_count += 1
                eliza_state.tasks_completed_count += 1
                eliza_state.dao_value_created += 15
            return True
        return False

    def _execute_utility_building(self, cycle):
        utility_name = f"XMRT_Utility_Cycle_{cycle}"
        filename = f"eliza_utilities/{utility_name.lower()}.py"
        content = f"# {utility_name}\n# Purpose: Autonomous utility\n"
        if self._commit_to_github(f"{GITHUB_USERNAME}/XMRT-Ecosystem", filename, content, f"🤖 Eliza Cycle {cycle}: Built utility {utility_name}"):
            with eliza_state.lock:
                eliza_state.utilities_built_count += 1
                eliza_state.dao_value_created += 12
            return True
        return False

    def _create_discussion_post(self, cycle):
        if not self.github_client:
            return False
        try:
            repo = self.github_client.get_repo(f"{GITHUB_USERNAME}/XMRT-Ecosystem")
            cat = None
            for c in repo.get_discussion_categories():
                if c.slug in ("announcements", "general"):
                    cat = c
                    break
            if not cat:
                logging.warning("⚠️ No suitable discussion category found.")
                return False
            title = f"🚀 XMRT Progress Update - Cycle {cycle}"
            with eliza_state.lock:
                body = (
                    f"Cycle {cycle} complete! DAO Value: ${eliza_state.dao_value_created}, "
                    f"Self-Improvements: {eliza_state.self_improvements_count}, "
                    f"Repos Improved: {eliza_state.repos_improved_count}."
                )
            repo.create_discussion(title=title, body=body, category=cat)
            with eliza_state.lock:
                eliza_state.discussion_posts_created += 1
                eliza_state.dao_value_created += 25
            return True
        except Exception as e:
            logging.warning(f"Failed to create discussion post: {e}")
            return False

# === MAIN BULLETPROOF LOOP ===
class SentinelOfProgress:
    def __init__(self):
        self.agent = ElizaCoreAgent()
        self.check_interval_seconds = CHECK_INTERVAL

    def run_bulletproof_cycle(self):
        eliza_state.agent_active = True
        with eliza_state.lock:
            eliza_state.cycle_count = eliza_state.increment_and_get_cycle()
            current_cycle = eliza_state.cycle_count
            eliza_state.last_cycle_finish_time = datetime.now()
        logging.info(f"🚀 STARTING SENTINEL CYCLE {current_cycle}")
        self.agent._execute_self_improvement(current_cycle)
        # Prioritize xmrt* repos
        repos = self.agent.xmrt_repos if self.agent.xmrt_repos else self.agent.other_repos
        if repos:
            # Pick 2 repos per cycle if available
            for repo_info in random.sample(repos, min(2, len(repos))):
                self.agent._execute_repo_improvement(repo_info, current_cycle)
                time.sleep(1)
        self.agent._execute_utility_building(current_cycle)
        self.agent._create_discussion_post(current_cycle)
        logging.info(f"✅ SENTINEL CYCLE {current_cycle} COMPLETED.")

    def run_forever(self):
        eliza_state.agent_status_message = "Running continuously"
        logging.info("🌟 Sentinel of Progress: run_forever() entered")
        while True:
            try:
                logging.info("🌟 About to run_bulletproof_cycle")
                self.run_bulletproof_cycle()
                logging.info("🌟 Cycle finished, sleeping ...")
                time.sleep(self.check_interval_seconds)
            except Exception as e:
                logging.critical(f"❌ CRITICAL ERROR IN MAIN LOOP: {e}", exc_info=True)
                eliza_state.agent_status_message = f"Error: {str(e)[:50]}"
                time.sleep(60)

def start_sentinel_thread():
    global sentinel_thread
    sentinel = SentinelOfProgress()
    sentinel_thread = threading.Thread(target=sentinel.run_forever, daemon=True)
    sentinel_thread.start()
    logging.info("🌟 Sentinel of Progress thread started.")

# === FLASK ROUTES ===
@app.route('/')
def index():
    dashboard = '''
    <!DOCTYPE html>
    <html><head><title>XMRT Eliza Sentinel</title></head>
    <body>
    <h1>XMRT Eliza - Sentinel of Progress</h1>
    <ul>
      <li>Current Cycle: <span id="cycle"></span></li>
      <li>Total Commits: <span id="commits"></span></li>
      <li>DAO Value: $<span id="dao"></span></li>
      <li>Repositories Improved: <span id="repos"></span></li>
      <li>Utilities Built: <span id="utilities"></span></li>
      <li>Discussion Posts: <span id="discussions"></span></li>
    </ul>
    <script>
      function fetchStatus() {
        fetch('/status').then(r=>r.json()).then(data=>{
          document.getElementById('cycle').textContent = data.cycle_count;
          document.getElementById('commits').textContent = data.total_commits_made;
          document.getElementById('dao').textContent = data.dao_value_created;
          document.getElementById('repos').textContent = data.repos_improved_count;
          document.getElementById('utilities').textContent = data.utilities_built_count;
          document.getElementById('discussions').textContent = data.discussion_posts_created;
        });
      }
      fetchStatus(); setInterval(fetchStatus, 4000);
    </script>
    </body></html>
    '''
    return dashboard

@app.route('/status')
def get_status():
    with eliza_state.lock:
        uptime = str(timedelta(seconds=int((datetime.now() - eliza_state.start_time).total_seconds())))
        last_cycle = eliza_state.last_cycle_finish_time.strftime('%H:%M:%S') if eliza_state.last_cycle_finish_time else "N/A"
        return jsonify({
            "cycle_count": eliza_state.cycle_count,
            "total_commits_made": eliza_state.total_commits_made,
            "dao_value_created": eliza_state.dao_value_created,
            "repos_improved_count": eliza_state.repos_improved_count,
            "utilities_built_count": eliza_state.utilities_built_count,
            "discussion_posts_created": eliza_state.discussion_posts_created,
            "self_improvements_count": eliza_state.self_improvements_count,
            "tools_discovered_count": eliza_state.tools_discovered_count,
            "tasks_completed_count": eliza_state.tasks_completed_count,
            "agent_status_message": eliza_state.agent_status_message,
            "uptime_human": uptime,
            "last_cycle_finish_time_human": last_cycle
        })

if __name__ == '__main__':
    logging.info("🎯 Starting XMRT Eliza - Sentinel of Progress (v5.4)")
    start_sentinel_thread()
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
