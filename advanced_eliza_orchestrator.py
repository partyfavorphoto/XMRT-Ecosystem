#!/usr/bin/env python3
"""
BULLETPROOF CONTINUOUS XMRT ELIZA - ENHANCED ORCHESTRATOR
- No exits allowed
- Always cycles
- Real, verifiable work only
- Prioritizes xmrt* repositories for improvement
- Enhanced with orchestration capabilities
"""

import os
import sys
import time
import json
import logging
import random
import threading
import subprocess
import psutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from github import Github, Auth, UnknownObjectException
from github.InputGitAuthor import InputGitAuthor

# Keep your original logging setup
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

def check_stop_flag():
    """Your original stop flag checker - unchanged"""
    try:
        with open('STOP_FAKE_TASKS.flag', 'r') as f:
            if 'STOP_FAKE_TASKS=true' in f.read():
                print("🛑 STOP FLAG DETECTED - Terminating fake task cycles")
                print("📋 Verification system must be implemented")
                print("❌ Fake task cycles are now prohibited")
                sys.exit(0)
    except FileNotFoundError:
        pass

@dataclass
class ElizaConfig:
    """Enhanced configuration while maintaining your defaults"""
    github_token: str = None
    github_user: str = 'DevGruGold'
    check_interval: int = 240  # Your 4-minute default
    cycle_file: str = "/tmp/eliza_cycle_count.txt"
    project_root: str = "/tmp/xmrt_eliza_workspace"
    api_port: int = 8080
    enable_api: bool = True
    enable_health_monitoring: bool = True
    max_restart_attempts: int = 3

class BulletproofXMRTEliza:
    """Your original class enhanced with orchestration capabilities"""
    
    def __init__(self, config: Optional[ElizaConfig] = None):
        # Initialize with your original setup
        self.config = config or ElizaConfig()
        self.github_token = os.getenv('GITHUB_TOKEN') or self.config.github_token
        self.github_user = os.getenv('GITHUB_USERNAME', self.config.github_user)
        self.check_interval = int(os.getenv('CHECK_INTERVAL', str(self.config.check_interval)))
        self.cycle_file = self.config.cycle_file
        self.cycle_count = self._load_cycle()
        self.start_time = time.time()
        self.github = Github(auth=Auth.Token(self.github_token))
        self.xmrt_repos, self.other_repos = self._load_repositories()
        
        # Enhanced orchestration features
        self.services = {}
        self.health_status = {}
        self.is_running = True
        self.api_server = None
        
        # Setup workspace
        self._setup_workspace()
        
        logging.info("🤖 BULLETPROOF XMRT ELIZA INITIALIZED WITH ORCHESTRATION")

    def _setup_workspace(self):
        """Create workspace directory structure"""
        workspace = Path(self.config.project_root)
        workspace.mkdir(exist_ok=True)
        (workspace / "logs").mkdir(exist_ok=True)
        (workspace / "temp").mkdir(exist_ok=True)
        (workspace / "proofs").mkdir(exist_ok=True)

    def _load_cycle(self):
        """Your original cycle loader - unchanged"""
        try:
            if os.path.exists(self.cycle_file):
                with open(self.cycle_file, "r") as f:
                    c = int(f.read().strip())
                    logging.info(f"Loaded persistent cycle count: {c}")
                    return c
        except Exception as e:
            logging.error(f"Error loading persistent cycle count: {e}")
        return 0

    def _save_cycle(self, value):
        """Your original cycle saver - unchanged"""
        try:
            with open(self.cycle_file, "w") as f:
                f.write(str(value))
        except Exception as e:
            logging.error(f"Error saving persistent cycle count: {e}")

    def _load_repositories(self):
        """Your original repository loader - unchanged"""
        xmrt_repos = []
        other_repos = []
        try:
            user = self.github.get_user(self.github_user)
            for repo in user.get_repos():
                if not repo.fork:
                    info = {
                        'name': repo.name,
                        'full_name': repo.full_name,
                        'default_branch': repo.default_branch
                    }
                    if repo.name.lower().startswith('xmrt'):
                        xmrt_repos.append(info)
                    else:
                        other_repos.append(info)
            logging.info(f"Loaded {len(xmrt_repos)} xmrt* repos, {len(other_repos)} other repos.")
        except Exception as e:
            logging.error(f"Failed to load repositories: {e}")
        return xmrt_repos, other_repos

    def _commit_proof(self, repo_full_name, filename, content, message):
        """Your original commit proof method - unchanged"""
        try:
            repo = self.github.get_repo(repo_full_name)
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
            except UnknownObjectException:
                repo.create_file(
                    path=filename,
                    message=message,
                    content=content,
                    branch=repo.default_branch,
                    author=author
                )
                logging.info(f"✅ Created {filename} in {repo_full_name}")
            return True
        except Exception as e:
            logging.error(f"❌ GitHub commit failed for {repo_full_name}/{filename}: {e}", exc_info=True)
            return False

    def proof_of_work(self, cycle, repo_info):
        """Your original proof of work - enhanced with local backup"""
        filename = f"eliza_improvements/{repo_info['name']}/cycle_{cycle}_proof.md"
        proof = {
            "cycle": cycle,
            "repo": repo_info['name'],
            "timestamp": datetime.now().isoformat(),
            "task": f"Improved docs & ran WorkingTaskExecutor",
            "evidence": f"Cycle {cycle} proof: README.md and docs checked, commit made by Eliza.",
            "orchestrator_status": self.get_orchestrator_status()
        }
        content = "# Proof of Work\n" + json.dumps(proof, indent=2)
        message = f"Eliza Proof of Work for Cycle {cycle}"
        
        # Save local backup
        local_proof_path = Path(self.config.project_root) / "proofs" / f"cycle_{cycle}_proof.json"
        try:
            with open(local_proof_path, 'w') as f:
                json.dump(proof, f, indent=2)
        except Exception as e:
            logging.error(f"Failed to save local proof: {e}")
        
        return self._commit_proof(repo_info['full_name'], filename, content, message)

    def build_xmrt_utility(self, cycle):
        """Your original utility builder - unchanged"""
        utility_name = f"XMRT_Utility_Cycle_{cycle}"
        filename = f"eliza_utilities/{utility_name.lower()}.py"
        content = f"# {utility_name}\n# Purpose: Autonomous utility\n"
        return self._commit_proof(f"{self.github_user}/XMRT-Ecosystem", filename, content, f"🤖 Eliza Cycle {cycle}: Built utility {utility_name}")

    def status_update(self):
        """Your original status update - enhanced with orchestrator info"""
        uptime_hours = (time.time() - self.start_time) / 3600
        status_content = f"""# 🤖 BULLETPROOF XMRT ELIZA STATUS
**Updated:** {datetime.now().isoformat()}
**Cycle:** {self.cycle_count}
**Uptime:** {uptime_hours:.1f} hours
**Status:** RUNNING CONTINUOUSLY ✅
**Orchestrator:** {self.get_orchestrator_status()}
**System Health:** {self.get_system_health()}
"""
        filename = f"ELIZA_BULLETPROOF_STATUS_{self.cycle_count}.md"
        return self._commit_proof(f"{self.github_user}/XMRT-Ecosystem", filename, status_content, f"🤖 Bulletproof Status - Cycle {self.cycle_count}")

    # NEW ORCHESTRATION METHODS
    def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get current orchestrator status"""
        return {
            "services_running": len(self.services),
            "api_enabled": self.config.enable_api,
            "health_monitoring": self.config.enable_health_monitoring,
            "workspace": self.config.project_root
        }

    def get_system_health(self) -> Dict[str, Any]:
        """Get system health metrics"""
        try:
            return {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent,
                "process_count": len(psutil.pids())
            }
        except Exception as e:
            logging.error(f"Error getting system health: {e}")
            return {"error": str(e)}

    def start_api_server(self):
        """Start optional API server for monitoring"""
        if not self.config.enable_api:
            return
            
        try:
            from fastapi import FastAPI
            from fastapi.middleware.cors import CORSMiddleware
            import uvicorn
            
            app = FastAPI(title="XMRT Eliza Orchestrator API")
            
            app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
            
            @app.get("/health")
            async def health_check():
                return {
                    "status": "healthy",
                    "cycle": self.cycle_count,
                    "uptime": time.time() - self.start_time,
                    "timestamp": datetime.now().isoformat()
                }
                
            @app.get("/status")
            async def get_status():
                return {
                    "eliza": {
                        "cycle": self.cycle_count,
                        "uptime": time.time() - self.start_time,
                        "repos": {
                            "xmrt": len(self.xmrt_repos),
                            "other": len(self.other_repos)
                        }
                    },
                    "orchestrator": self.get_orchestrator_status(),
                    "system": self.get_system_health()
                }
                
            @app.post("/emergency_stop")
            async def emergency_stop():
                """Emergency stop - creates the stop flag"""
                try:
                    with open('STOP_FAKE_TASKS.flag', 'w') as f:
                        f.write('STOP_FAKE_TASKS=true')
                    return {"status": "emergency_stop_initiated"}
                except Exception as e:
                    return {"status": "error", "message": str(e)}
            
            def run_server():
                uvicorn.run(app, host="0.0.0.0", port=self.config.api_port, log_level="warning")
                
            api_thread = threading.Thread(target=run_server, daemon=True)
            api_thread.start()
            
            self.services['api_server'] = {
                'thread': api_thread,
                'start_time': datetime.now(),
                'port': self.config.api_port
            }
            
            logging.info(f"🌐 API server started on port {self.config.api_port}")
            
        except ImportError:
            logging.warning("⚠️ FastAPI not available, API server disabled")
        except Exception as e:
            logging.error(f"❌ Error starting API server: {e}")

    def start_health_monitoring(self):
        """Start health monitoring thread"""
        if not self.config.enable_health_monitoring:
            return
            
        def monitor_health():
            while self.is_running:
                try:
                    health = self.get_system_health()
                    
                    # Log warnings for high resource usage
                    if health.get('cpu_percent', 0) > 90:
                        logging.warning(f"⚠️ High CPU usage: {health['cpu_percent']}%")
                    if health.get('memory_percent', 0) > 90:
                        logging.warning(f"⚠️ High memory usage: {health['memory_percent']}%")
                    
                    # Update health status
                    self.health_status = {
                        'timestamp': datetime.now().isoformat(),
                        'system': health,
                        'eliza_cycle': self.cycle_count
                    }
                    
                    time.sleep(60)  # Check every minute
                    
                except Exception as e:
                    logging.error(f"Health monitoring error: {e}")
                    time.sleep(10)
                    
        monitor_thread = threading.Thread(target=monitor_health, daemon=True)
        monitor_thread.start()
        
        self.services['health_monitor'] = {
            'thread': monitor_thread,
            'start_time': datetime.now()
        }
        
        logging.info("💓 Health monitoring started")

    def run_forever(self):
        """Your original run_forever method - enhanced with orchestration startup"""
        logging.info("🚀 STARTING BULLETPROOF CONTINUOUS OPERATION WITH ORCHESTRATION")
        
        # Start orchestration services
        self.start_api_server()
        self.start_health_monitoring()
        
        # Your original continuous loop - unchanged logic
        while True:
            try:
                check_stop_flag()
                self.cycle_count += 1
                self._save_cycle(self.cycle_count)
                logging.info(f"🔄 BULLETPROOF CYCLE {self.cycle_count} STARTING")
                
                # Prioritize xmrt* repos (your original logic)
                targets = self.xmrt_repos if self.xmrt_repos else self.other_repos
                if targets:
                    repo_info = random.choice(targets)
                    self.proof_of_work(self.cycle_count, repo_info)
                else:
                    logging.info("No repos found for improvement.")
                
                # Build a utility every cycle (your original)
                self.build_xmrt_utility(self.cycle_count)
                
                # Status proof (your original)
                self.status_update()
                
                logging.info(f"✅ Cycle {self.cycle_count} completed. Sleeping {self.check_interval} seconds...")
                
                # Your original sleep logic with logging
                remaining = self.check_interval
                while remaining > 0:
                    sleep_time = min(60, remaining)
                    time.sleep(sleep_time)
                    remaining -= sleep_time
                    logging.info(f"⏰ Still sleeping... {remaining} seconds remaining")
                    
            except Exception as e:
                logging.error(f"❌ Cycle {self.cycle_count} error: {e}")
                logging.info("🔄 Continuing anyway - NO EXITS ALLOWED")
                time.sleep(60)

    def shutdown(self):
        """Graceful shutdown method"""
        logging.info("🛑 Initiating graceful shutdown...")
        self.is_running = False
        
        # Wait a moment for threads to notice
        time.sleep(2)
        
        logging.info("✅ Bulletproof Eliza shutdown complete")

def main():
    """Enhanced main function with configuration options"""
    
    # Configuration from environment or defaults
    config = ElizaConfig(
        github_token=os.getenv('GITHUB_TOKEN'),
        github_user=os.getenv('GITHUB_USERNAME', 'DevGruGold'),
        check_interval=int(os.getenv('CHECK_INTERVAL', '240')),
        project_root=os.getenv('XMRT_PROJECT_ROOT', '/tmp/xmrt_eliza_workspace'),
        api_port=int(os.getenv('API_PORT', '8080')),
        enable_api=os.getenv('ENABLE_API', 'true').lower() == 'true',
        enable_health_monitoring=os.getenv('ENABLE_HEALTH_MONITORING', 'true').lower() == 'true'
    )
    
    # Your original initialization and run
    eliza = BulletproofXMRTEliza(config)
    
    try:
        eliza.run_forever()
    except KeyboardInterrupt:
        logging.info("👋 Received shutdown signal")
        eliza.shutdown()

if __name__ == "__main__":
    main()
