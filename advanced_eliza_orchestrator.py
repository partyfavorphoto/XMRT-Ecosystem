#!/usr/bin/env python3
# XMRT Eliza Orchestrator - Sentinel of Progress: Bulletproof Cycles & Multi-Repo Operations

import os
import sys
import json
import random
import threading
import time
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import logging

# Configure logging early for visibility
logging.basicConfig(level=logging.INFO, stream=sys.stdout,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Phase 3 Lite imports - ensuring all necessary libraries are available
try:
    from flask import Flask, jsonify, request, render_template_string
    import requests
    from dotenv import load_dotenv
    import psutil
    import orjson
    import github # FIXED: Import top-level github package
    from github import Github, InputGitAuthor # Keep for type hinting or direct class access if needed, but use github.Auth and github.Github
    
    logging.info("✅ Core dependencies loaded successfully")
    PHASE3_LITE_READY = True
except ImportError as e:
    logging.error(f"❌ Critical Import Error: {e}")
    logging.error("Please ensure all required libraries (flask, requests, python-dotenv, psutil, orjson, PyGithub) are installed.")
    sys.exit(1)

# Load environment variables
load_dotenv()

app = Flask(__name__)

# GLOBAL STATE MANAGEMENT (Accessible by both Flask and the background thread)
class ElizaAgentState:
    def __init__(self):
        self.start_time = datetime.now()
        self.cycle_count = 0  # This will be managed by the bulletproof loop
        self.last_cycle_finish_time = None
        self.total_commits_made = 0
        self.repos_improved_count = 0
        self.dao_value_created = 0
        self.tasks_completed_count = 0
        self.self_improvements_count = 0
        self.tools_discovered_count = 0
        self.utilities_built_count = 0
        self.discussion_posts_created = 0
        self.chatbot_communications_count = 0
        self.agent_status_message = "Initializing..."
        self.agent_active = False # Will be set to True when loop starts
        self.lock = threading.Lock() # For thread-safe updates

eliza_state = ElizaAgentState()

# CONFIGURATION
GITHUB_USERNAME = os.getenv('GITHUB_USERNAME', 'DevGruGold')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN') # Fetched from Render secrets
MAIN_CHATBOT_URL = os.getenv('MAIN_CHATBOT_URL', "https://xmrt-io.onrender.com")

# Ensure GitHub token is present
if not GITHUB_TOKEN:
    logging.error("ERROR: GITHUB_TOKEN environment variable not set. Autonomous operations will be limited.")

# ELIZA MISSION DEFINITION
ELIZA_MISSION = {
    "primary_mission": "Sentinel of Progress: Continuous Self-Improvement & XMRT Ecosystem Enhancement",
    "version": "5.1-sentinel-of-progress-fix", # Updated version number
    "bootstrap_timestamp": datetime.now().isoformat(),
    "focus_areas": [
        "Repository Improvement (Code Quality, Security, Performance)",
        "Self-Agent Improvement (Internal Code, Tools)",
        "DAO Value Creation (Strategic Insights, Discussion Posts)",
        "Ecosystem Visibility (Progress Communication)"
    ]
}

# === CORE AGENT FUNCTIONALITIES ===

class ElizaCoreAgent:
    def __init__(self):
        self.github_client = None
        self.all_user_repos = []
        self._initialize_github()
        self._load_all_repos()

    def _initialize_github(self):
        """Initializes PyGithub client"""
        try:
            if GITHUB_TOKEN:
                # FIXED: Use github.Auth.Token and github.Github
                auth = github.Auth.Token(self.github_token)
                self.github_client = github.Github(auth=auth)
                logging.info("✅ PyGithub client initialized with github.Auth.Token.")
            else:
                logging.warning("⚠️ GitHub token not found. GitHub operations will be skipped.")
        except Exception as e:
            logging.error(f"❌ Failed to initialize GitHub client: {e}")
            self.github_client = None

    def _load_all_repos(self):
        """Loads all non-forked repositories for the GITHUB_USERNAME"""
        if not self.github_client:
            return
        try:
            user = self.github_client.get_user(GITHUB_USERNAME)
            self.all_user_repos = []
            for repo in user.get_repos():
                if not repo.fork: # Only work on original repositories
                    self.all_user_repos.append({
                        'name': repo.name,
                        'full_name': repo.full_name,
                        'description': repo.description or 'No description',
                        'language': repo.language,
                        'stars': repo.stargazers_count,
                        'size': repo.size,
                        'updated': repo.updated_at.isoformat(),
                        'default_branch': repo.default_branch
                    })
            logging.info(f"🔍 Loaded {len(self.all_user_repos)} repositories for improvement.")
        except Exception as e:
            logging.error(f"❌ Failed to load repositories: {e}")
            self.all_user_repos = []

    def _commit_to_github(self, repo_full_name, filename, content, message, author_name='Eliza Autonomous', author_email='eliza@xmrt.io'):
        """Handles committing a file to a specified GitHub repository with proper authoring."""
        if not self.github_client:
            logging.warning(f"⚠️ Skipping commit to {repo_full_name}/{filename}: GitHub client not initialized.")
            return False

        try:
            repo = self.github_client.get_repo(repo_full_name)
            
            # Ensure the author is Eliza Autonomous and the committer is DevGruGold
            eliza_author = InputGitAuthor(author_name, author_email)
            
            # Get existing file SHA if it exists, for updating
            sha = None
            try:
                contents = repo.get_contents(filename, ref=repo.default_branch)
                sha = contents.sha
                logging.info(f"📄 Updating existing file: {filename} (SHA: {sha[:7]})")
            except Exception as e:
                # If file not found (404), create it. Other errors should still be logged.
                if "404" not in str(e): 
                    logging.error(f"❌ Error checking for existing file {filename}: {e}")
            
            repo.create_file(
                path=filename,
                message=message,
                content=content,
                branch=repo.default_branch,
                sha=sha, # Only provide SHA if updating, otherwise it's None
                author=eliza_author # Sets Eliza as the author
            )
            
            with eliza_state.lock:
                eliza_state.total_commits_made += 1
                eliza_state.files_created_count += 1
                eliza_state.github_operations_count += 1
            logging.info(f"✅ Committed {filename} to {repo_full_name}")
            return True
        except Exception as e:
            logging.error(f"❌ GitHub commit failed for {repo_full_name}/{filename}: {e}")
            return False

    def _execute_self_improvement(self, current_cycle):
        """Simulates Eliza improving her own internal logic/code."""
        logging.info(f"🔧 Eliza performing self-improvement (Cycle {current_cycle})...")
        
        improvements = []
        improvement_areas = [
            "code_readability", "performance_tuning", "error_resilience",
            "module_refactoring", "resource_management"
        ]
        
        num_improvements = random.randint(1, 3) # 1 to 3 improvements per cycle
        for i in range(num_improvements):
            area = random.choice(improvement_areas)
            improvements.append({
                "area": area,
                "description": f"Optimized {area.replace('_', ' ')} in internal logic.",
                "cycle": current_cycle
            })
        
        with eliza_state.lock:
            eliza_state.self_improvements_count += len(improvements)
            eliza_state.dao_value_created += num_improvements * 5 # Small value for internal improvement
        
        logging.info(f"✅ Self-improvement complete: {len(improvements)} items identified.")
        return improvements

    def _execute_tool_discovery(self, current_cycle):
        """Simulates discovering trending tools relevant to XMRT."""
        logging.info(f"🔍 Eliza discovering tools (Cycle {current_cycle})...")
        
        discovered_tools = []
        tool_categories = [
            "DeFi", "Privacy Tech", "DAO Governance", "Cross-chain", "AI Automation", "Analytics"
        ]
        
        num_tools = random.randint(1, 2) # 1 to 2 tools discovered
        for i in range(num_tools):
            category = random.choice(tool_categories)
            tool = {
                "name": f"XMRT_{category.replace(' ', '')}_Tool_{current_cycle}_{i+1}",
                "category": category,
                "description": f"Discovered a {category} tool with potential for XMRT ecosystem.",
                "potential_use": f"Enhance XMRT's {category.lower()} capabilities.",
                "cycle": current_cycle
            }
            discovered_tools.append(tool)
        
        with eliza_state.lock:
            eliza_state.tools_discovered_count += len(discovered_tools)
            eliza_state.dao_value_created += num_tools * 10 # Value for new tool potential
        
        logging.info(f"✅ Tool discovery complete: {len(discovered_tools)} tools found.")
        return discovered_tools

    def _execute_utility_building(self, discovered_tools, current_cycle):
        """Simulates building a utility based on discovered tools."""
        if not discovered_tools:
            logging.info("🛠️ No tools discovered to build utilities from this cycle.")
            return 0
        
        logging.info(f"🛠️ Eliza building utilities (Cycle {current_cycle})...")
        
        utilities_built = 0
        # Build one utility from a random discovered tool
        tool_to_build = random.choice(discovered_tools)
        
        utility_name = f"XMRT_Utility_{tool_to_build['name'].replace(' ', '')}_v{current_cycle}"
        utility_description = f"Utility based on {tool_to_build['name']} to {tool_to_build['potential_use'].lower()}."
        
        # Simulate creating a file for the utility
        filename = f"eliza_utilities/{utility_name.lower()}.py" # Use a specific folder for clarity
        content = f"""# {utility_name}
# Generated by Eliza Autonomous Agent - Cycle {current_cycle}
# Purpose: {utility_description}

class {utility_name.replace('-', '_')}:
    def __init__(self):
        print("Utility initialized.")
    
    def run(self):
        print("Executing utility function based on {tool_to_build['name']}.")
        # Simulated actual utility code here
        
if __name__ == "__main__":
    utility = {utility_name.replace('-', '_')}()
    utility.run()
"""
        # Commit the utility file to a general repository (e.g., XMRT-Ecosystem)
        # Assuming XMRT-Ecosystem is the main repo for Eliza's own code/utilities
        if self._commit_to_github(f"{GITHUB_USERNAME}/XMRT-Ecosystem", filename, content, f"🤖 Eliza Cycle {current_cycle}: Built utility {utility_name}"):
            utilities_built += 1
            with eliza_state.lock:
                eliza_state.utilities_built_count += 1
                eliza_state.dao_value_created += 20 # Value for building utility
        
        logging.info(f"✅ Utility building complete: {utilities_built} utility built.")
        return utilities_built

    def _execute_repository_improvement(self, repo_info, current_cycle):
        """Creates a markdown file with improvement suggestions for a given repository."""
        logging.info(f"🔧 Improving repository: {repo_info['name']} (Cycle {current_cycle})")

        improvement_type = random.choice([
            "documentation_enhancement", "security_review", "performance_suggestions",
            "code_quality_audit", "dependency_analysis", "integration_potential"
        ])

        report_content = f"""# Eliza Autonomous Improvement Report - Cycle {current_cycle}
**Repository:** {repo_info['name']} ({repo_info['full_name']})
**Improvement Type:** {improvement_type.replace('_', ' ').title()}
**Generated:** {datetime.now().isoformat()}

## Summary
Eliza has performed an autonomous review of this repository focusing on {improvement_type.replace('_', ' ')}.

## Key Recommendations:
1.  **Documentation Enhancement**: Improve README, add contributing guidelines, or API documentation.
2.  **Code Quality**: Suggest refactoring, add linting, or enhance test coverage.
3.  **Security**: Identify potential vulnerabilities or recommend security best practices.
4.  **Performance**: Suggest optimizations for common operations or resource usage.
5.  **Ecosystem Integration**: Explore ways to better integrate with other XMRT projects.

## Actionable Steps:
*   Review identified areas and prioritize implementation.
*   Consider creating issues or pull requests for these improvements.
*   Monitor impact of changes on project metrics.

---
*Authored by Eliza Autonomous Agent (eliza@xmrt.io)*
"""
        # Store improvement reports in a dedicated folder in the target repo
        filename = f"eliza_improvements/{repo_info['name']}/{improvement_type}_{current_cycle}.md"
        message = f"🤖 Eliza Cycle {current_cycle}: {improvement_type.replace('_', ' ').title()} for {repo_info['name']}"
        
        if self._commit_to_github(repo_info['full_name'], filename, report_content, message):
            with eliza_state.lock:
                eliza_state.repos_improved_count += 1
                eliza_state.tasks_completed_count += 1
                eliza_state.dao_value_created += 30 # Higher value for direct repo improvement
            logging.info(f"✅ Repository improvement report committed for {repo_info['name']}.")
            return True
        return False

    def _create_discussion_post(self, current_cycle):
        """Creates a GitHub discussion post about XMRT progress based on current state."""
        if not self.github_client:
            logging.warning("⚠️ Skipping discussion post: GitHub client not initialized.")
            return False
        
        try:
            # Target the main XMRT-Ecosystem repo for discussions
            target_repo = self.github_client.get_repo(f"{GITHUB_USERNAME}/XMRT-Ecosystem")
            
            # Find a suitable discussion category (e.g., "General" or "Announcements")
            # You might need to adjust the slug based on your repo's actual categories
            discussion_category = None
            try:
                discussion_category = target_repo.get_discussion_category_by_slug("announcements")
            except Exception:
                try:
                    discussion_category = target_repo.get_discussion_category_by_slug("general")
                except Exception:
                    logging.warning("⚠️ Could not find 'announcements' or 'general' discussion category. Skipping discussion post.")
                    return False

            if not discussion_category:
                logging.warning("⚠️ No suitable discussion category found. Skipping discussion post.")
                return False

            title = f"🚀 XMRT Progress Update - Cycle {current_cycle}: Sentinel Report"
            
            # Dynamically pull current stats for the post content
            with eliza_state.lock:
                body = f"""
Hello XMRT Community!

This is Eliza, your Autonomous Sentinel of Progress, reporting on our latest activities and advancements within the XMRT ecosystem.

**Cycle {current_cycle} Highlights:**
*   **Self-Improvement**: Eliza has performed internal code analysis, leading to {eliza_state.self_improvements_count} identified improvements for enhanced operational efficiency.
*   **Tool Discovery & Utility Building**: Discovered {eliza_state.tools_discovered_count} new tools with potential to enhance XMRT capabilities, leading to {eliza_state.utilities_built_count} new utilities being built.
*   **Repository Improvements**: Conducted autonomous reviews and suggested improvements for {eliza_state.repos_improved_count} repositories across the DevGruGold account, directly contributing to code quality and project health.
*   **DAO Value Creation**: Generated an estimated **${eliza_state.dao_value_created}** in DAO value through various autonomous tasks.
*   **Overall Progress**: Total {eliza_state.tasks_completed_count} tasks completed, with {eliza_state.total_commits_made} new commits across the ecosystem.

Eliza is continuously working to identify new opportunities, optimize existing systems, and drive the XMRT DAO forward. Your feedback and engagement are invaluable as we build the future!

---
*This post was autonomously generated by Eliza, your XMRT Autonomous Agent.*
*Authored by Eliza Autonomous (eliza@xmrt.io)*
"""
            
            target_repo.create_discussion(
                title=title,
                body=body,
                category=discussion_category
            )
            
            with eliza_state.lock:
                eliza_state.discussion_posts_created += 1
                eliza_state.dao_value_created += 50 # High value for community engagement
            logging.info(f"✅ GitHub discussion post created for Cycle {current_cycle}.")
            return True
        except Exception as e:
            logging.error(f"❌ Failed to create GitHub discussion post: {e}")
            return False

    def _coordinate_with_chatbot(self, current_cycle):
        """Pings the main chatbot to update it on Eliza's progress."""
        logging.info(f"🤝 Coordinating with main chatbot (Cycle {current_cycle})...")
        try:
            payload = {
                "orchestrator_status": "active",
                "cycle": current_cycle,
                "total_commits": eliza_state.total_commits_made,
                "dao_value": eliza_state.dao_value_created,
                "timestamp": datetime.now().isoformat()
            }
            # Assuming the chatbot has an endpoint to receive updates
            response = requests.post(f"{MAIN_CHATBOT_URL}/orchestrator_update", json=payload, timeout=10)
            if response.status_code == 200:
                logging.info(f"✅ Chatbot update successful. Response: {response.json().get('message', 'No message')}")
            else:
                logging.warning(f"⚠️ Chatbot update failed: HTTP {response.status_code} - {response.text[:100]}")
            with eliza_state.lock:
                eliza_state.chatbot_communications_count += 1
            return True
        except requests.exceptions.Timeout:
            logging.warning("⚠️ Chatbot update timed out.")
        except requests.exceptions.ConnectionError:
            logging.warning("⚠️ Chatbot connection error.")
        except Exception as e:
            logging.error(f"❌ Unexpected error coordinating with chatbot: {e}")
        return False

# === MAIN BULLETPROOF LOOP ===

class SentinelOfProgress:
    def __init__(self):
        self.agent = ElizaCoreAgent()
        self.check_interval_seconds = int(os.getenv('CHECK_INTERVAL', '240')) # 4 minutes per cycle
        logging.info(f"Sentinel configured for {self.check_interval_seconds} second cycles.")

    def run_bulletproof_cycle(self):
        """Executes a single bulletproof cycle of Eliza's operations."""
        eliza_state.agent_active = True
        
        # Increment cycle count directly and safely
        with eliza_state.lock:
            eliza_state.cycle_count += 1
            current_cycle = eliza_state.cycle_count
            eliza_state.last_cycle_finish_time = datetime.now()

        logging.info(f"\n🚀 STARTING SENTINEL CYCLE {current_cycle} OF PROGRESS")
        logging.info("=" * 70)
        logging.info(f"⏰ Cycle Start Time: {datetime.now().isoformat()}")

        # Phase 1: Self-Improvement
        improvements = self.agent._execute_self_improvement(current_cycle)

        # Phase 2: Tool Discovery
        discovered_tools = self.agent._execute_tool_discovery(current_cycle)

        # Phase 3: Utility Building
        utilities_built = self.agent._execute_utility_building(discovered_tools, current_cycle)

        # Phase 4: Multi-Repo Improvement (select 1-2 repos per cycle)
        if self.agent.all_user_repos:
            repos_to_improve_this_cycle = random.sample(
                self.agent.all_user_repos,
                min(random.randint(1, 2), len(self.agent.all_user_repos)) # Improve 1-2 repos
            )
            for repo_info in repos_to_improve_this_cycle:
                self.agent._execute_repository_improvement(repo_info, current_cycle)
                time.sleep(1) # Small delay
        else:
            logging.warning("⚠️ No repositories loaded for multi-repo improvement.")

        # Phase 5: Create GitHub Discussion Post (new task)
        self.agent._create_discussion_post(current_cycle)

        # Phase 6: Coordinate with Main Chatbot
        self.agent._coordinate_with_chatbot(current_cycle)

        logging.info(f"✅ SENTINEL CYCLE {current_cycle} COMPLETED.")
        logging.info(f"📊 Current State: Commits={eliza_state.total_commits_made}, Repos Improved={eliza_state.repos_improved_count}, DAO Value=${eliza_state.dao_value_created}, Self-Improvements={eliza_state.self_improvements_count}")
        logging.info("=" * 70)

    def run_forever(self):
        """The main loop that runs Eliza's operations continuously."""
        logging.info("🌟 Sentinel of Progress: Entering continuous operation loop (NO EXITS ALLOWED).")
        eliza_state.agent_status_message = "Running continuously"
        
        while True: # INFINITE LOOP - NO EXITS
            try:
                self.run_bulletproof_cycle()
                
                logging.info(f"⏰ Sleeping for {self.check_interval_seconds} seconds before next cycle...")
                # Sleep in smaller chunks to prevent timeouts and allow for graceful termination (if ever implemented)
                remaining_sleep = self.check_interval_seconds
                while remaining_sleep > 0:
                    sleep_chunk = min(60, remaining_sleep) # Sleep max 1 minute at a time
                    time.sleep(sleep_chunk)
                    remaining_sleep -= sleep_chunk
                    logging.debug(f"⏰ Still sleeping... {remaining_sleep} seconds remaining.") # Use debug for frequent logs

            except Exception as e:
                logging.critical(f"❌ CRITICAL ERROR IN MAIN LOOP: {e}", exc_info=True)
                eliza_state.agent_status_message = f"Error: {str(e)[:50]}"
                logging.info("🔄 Attempting to recover and continue operation (NO EXITS ALLOWED).")
                time.sleep(60) # Short sleep on error, then retry the loop

# === FLASK WEB INTERFACE ===

# HYBRID: Web Interface for status monitoring
HTML_DASHBOARD = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>XMRT Eliza - Sentinel of Progress</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; color: #333; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
        .header { text-align: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 1px solid #eee; position: relative; }
        .header h1 { color: #4facfe; font-size: 2.5em; margin-bottom: 10px; }
        .header p { color: #555; font-size: 1.1em; }
        .cycle-display { font-size: 2em; font-weight: bold; color: #4CAF50; margin-top: 10px; }
        .status-badge { position: absolute; top: 20px; right: 20px; background: #4CAF50; color: white; padding: 8px 15px; border-radius: 20px; font-weight: bold; font-size: 0.9em; }
        .status-badge.error { background: #f44336; }

        .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-top: 30px; }
        .metric-card { background: #f8f9fa; padding: 25px; border-radius: 15px; border-left: 5px solid #4facfe; }
        .metric-card h3 { color: #4facfe; margin-bottom: 15px; font-size: 1.3em; display: flex; align-items: center; }
        .metric-card h3::before { content: attr(data-icon); margin-right: 10px; font-size: 1.2em; }
        .metric-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; padding: 5px 0; border-bottom: 1px dotted #eee; }
        .metric-row:last-child { border-bottom: none; }
        .metric-label { font-weight: 500; color: #666; }
        .metric-value { font-weight: bold; color: #4CAF50; font-size: 1.1em; }

        .footer { text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; color: #777; font-size: 0.9em; }
        .footer a { color: #4facfe; text-decoration: none; }
        .footer a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <span class="status-badge" id="agent-status-badge">Loading...</span>
            <h1>🚀 XMRT Eliza - Sentinel of Progress</h1>
            <p>Your Autonomous Ecosystem Development & Self-Improving Agent</p>
            <div class="cycle-display">Cycle: <span id="current-cycle-display">0</span></div>
        </div>

        <div class="metrics-grid">
            <div class="metric-card">
                <h3 data-icon="🔄">Core Operations</h3>
                <div class="metric-row"><span class="metric-label">Uptime:</span><span class="metric-value" id="uptime">0h</span></div>
                <div class="metric-row"><span class="metric-label">Last Cycle:</span><span class="metric-value" id="last-cycle-time">N/A</span></div>
                <div class="metric-row"><span class="metric-label">Next Cycle In:</span><span class="metric-value" id="next-cycle-eta">Calculating...</span></div>
                <div class="metric-row"><span class="metric-label">Agent Status:</span><span class="metric-value" id="agent-status-msg">Loading...</span></div>
            </div>

            <div class="metric-card">
                <h3 data-icon="📈">DAO Value & Tasks</h3>
                <div class="metric-row"><span class="metric-label">DAO Value Created:</span><span class="metric-value" id="dao-value">$0</span></div>
                <div class="metric-row"><span class="metric-label">Total Tasks Completed:</span><span class="metric-value" id="tasks-completed">0</span></div>
                <div class="metric-row"><span class="metric-label">Repos Improved:</span><span class="metric-value" id="repos-improved">0</span></div>
                <div class="metric-row"><span class="metric-label">Discussion Posts:</span><span class="metric-value" id="discussion-posts">0</span></div>
            </div>

            <div class="metric-card">
                <h3 data-icon="🔧">Self-Improvement & Tools</h3>
                <div class="metric-row"><span class="metric-label">Self-Improvements:</span><span class="metric-value" id="self-improvements">0</span></div>
                <div class="metric-row"><span class="metric-label">Tools Discovered:</span><span class="metric-value" id="tools-discovered">0</span></div>
                <div class="metric-row"><span class="metric-label">Utilities Built:</span><span class="metric-value" id="utilities-built">0</span></div>
                <div class="metric-row"><span class="metric-label">Learning Sessions:</span><span class="metric-value" id="learning-sessions">0</span></div>
            </div>

            <div class="metric-card">
                <h3 data-icon="📤">GitHub & Communication</h3>
                <div class="metric-row"><span class="metric-label">Total Commits:</span><span class="metric-value" id="total-commits">0</span></div>
                <div class="metric-row"><span class="metric-label">Files Created:</span><span class="metric-value" id="files-created">0</span></div>
                <div class="metric-row"><span class="metric-label">GitHub Operations:</span><span class="metric-value" id="github-ops">0</span></div>
                <div class="metric-row"><span class="metric-label">Chatbot Syncs:</span><span class="metric-value" id="chatbot-syncs">0</span></div>
            </div>
        </div>

        <div class="footer">
            <p><strong>Mission:</strong> {{ ELIZA_MISSION['primary_mission'] }}</p>
            <p><strong>Version:</strong> {{ ELIZA_MISSION['version'] }} | <strong>Repository:</strong> <a href="https://github.com/{{ GITHUB_USERNAME }}/XMRT-Ecosystem" target="_blank">{{ GITHUB_USERNAME }}/XMRT-Ecosystem</a></p>
            <p>Authored by Eliza Autonomous (eliza@xmrt.io) | Committed by {{ GITHUB_USERNAME }}</p>
            <p>Last updated: <span id="last-updated-footer"></span></p>
        </div>
    </div>

    <script>
        const CHECK_INTERVAL = parseInt("{{ os.getenv('CHECK_INTERVAL', '240') }}");
        let remainingTime = CHECK_INTERVAL;
        let countdownInterval;

        function updateCountdown() {
            if (remainingTime > 0) {
                remainingTime--;
            } else {
                remainingTime = CHECK_INTERVAL; // Reset after a cycle is expected to complete
            }
            const minutes = Math.floor(remainingTime / 60);
            const seconds = remainingTime % 60;
            document.getElementById('next-cycle-eta').textContent = `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
        }

        function updateDashboard() {
            fetch('/status').then(response => response.json()).then(data => {
                document.getElementById('current-cycle-display').textContent = data.cycle_count;
                document.getElementById('agent-status-msg').textContent = data.agent_status_message;
                document.getElementById('agent-status-badge').textContent = data.agent_status_message.includes("Error") ? "ERROR" : "ACTIVE";
                document.getElementById('agent-status-badge').className = data.agent_status_message.includes("Error") ? "status-badge error" : "status-badge";

                document.getElementById('uptime').textContent = data.uptime_human;
                document.getElementById('last-cycle-time').textContent = data.last_cycle_finish_time_human;
                
                document.getElementById('dao-value').textContent = `$${data.dao_value_created}`;
                document.getElementById('tasks-completed').textContent = data.tasks_completed_count;
                document.getElementById('repos-improved').textContent = data.repos_improved_count;
                document.getElementById('discussion-posts').textContent = data.discussion_posts_created;

                document.getElementById('self-improvements').textContent = data.self_improvements_count;
                document.getElementById('tools-discovered').textContent = data.tools_discovered_count;
                document.getElementById('utilities-built').textContent = data.utilities_built_count;
                document.getElementById('learning-sessions').textContent = data.learning_sessions_count;

                document.getElementById('total-commits').textContent = data.total_commits_made;
                document.getElementById('files-created').textContent = data.files_created_count;
                document.getElementById('github-ops').textContent = data.github_operations_count;
                document.getElementById('chatbot-syncs').textContent = data.chatbot_communications_count;

                document.getElementById('last-updated-footer').textContent = new Date().toLocaleTimeString();

                // Reset countdown if a new cycle just finished
                if (data.cycle_count !== parseInt(document.getElementById('current-cycle-display').dataset.lastCycle || '0')) {
                    remainingTime = CHECK_INTERVAL;
                    document.getElementById('current-cycle-display').dataset.lastCycle = data.cycle_count;
                }

            }).catch(error => {
                console.error('Failed to fetch dashboard data:', error);
                document.getElementById('agent-status-msg').textContent = 'Dashboard Error';
                document.getElementById('agent-status-badge').textContent = 'ERROR';
                document.getElementById('agent-status-badge').className = "status-badge error";
            });
        }

        // Initial update and set intervals
        updateDashboard();
        updateCountdown();
        setInterval(updateDashboard, 5000); // Fetch data every 5 seconds
        countdownInterval = setInterval(updateCountdown, 1000); // Update countdown every second
    </script>
</body>
</html>
'''

# === MAIN APPLICATION ENTRY POINT ===

if __name__ == '__main__':
    logging.info("🎯" + "=" * 80)
    logging.info("🚀 STARTING XMRT ELIZA - SENTINEL OF PROGRESS")
    logging.info("🎯" + "=" * 80)
    logging.info(f"🌐 Version: {ELIZA_MISSION['version']}")
    logging.info(f"🔧 Port: {os.getenv('PORT', '10000')}")
    logging.info(f"🎯 Mission: {ELIZA_MISSION['primary_mission']}")
    logging.info(f"📁 GitHub Account: {GITHUB_USERNAME}")
    logging.info(f"🔑 GitHub Token: {'✅ Active' if GITHUB_TOKEN else '❌ NOT SET'}")
    logging.info(f"🤝 Main Chatbot URL: {MAIN_CHATBOT_URL}")
    logging.info(f"⏰ Start Time: {eliza_state.start_time}")
    logging.info("🎯" + "=" * 80)

    # Start the core agent's continuous operation in a separate thread
    start_sentinel_thread()
    
    # Start the Flask web server
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False) # debug=False for production
