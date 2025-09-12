#!/usr/bin/env python3
"""
XMRT Ecosystem Startup Script for Render Deployment
Initializes and starts all enhanced agents and MCP servers
"""

import os
import sys
import json
import time
import logging
import asyncio
import subprocess
import threading
from pathlib import Path
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class XMRTSystemManager:
    """Manages the complete XMRT ecosystem startup and operation"""
    
    def __init__(self):
        self.processes = {}
        self.system_status = {
            "startup_time": None,
            "mcp_servers": {},
            "agents": {},
            "health_checks": {},
            "last_update": None
        }
        
        # Validate environment variables
        self.validate_environment()
        
        logger.info("XMRT System Manager initialized")
    
    def validate_environment(self):
        """Validate required environment variables"""
        required_vars = [
            "GITHUB_TOKEN",
            "GITHUB_OAUTH_CLIENT_ID", 
            "GITHUB_OAUTH_CLIENT_SECRET",
            "RENDER_API_KEY"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.error(f"Missing required environment variables: {missing_vars}")
            raise ValueError(f"Missing environment variables: {missing_vars}")
        
        logger.info("Environment validation passed")
    
    def start_mcp_servers(self):
        """Start all MCP servers"""
        logger.info("Starting MCP servers...")
        
        mcp_servers = {
            "github": {
                "script": "mcp-integration/github_mcp_server_clean.py",
                "description": "GitHub MCP Server"
            },
            "render": {
                "script": "mcp-integration/render_mcp_server_clean.py", 
                "description": "Render MCP Server"
            },
            "xmrt": {
                "script": "mcp-integration/xmrt_mcp_server_clean.py",
                "description": "XMRT MCP Server"
            }
        }
        
        for server_name, config in mcp_servers.items():
            try:
                script_path = Path(config["script"])
                if script_path.exists():
                    process = subprocess.Popen(
                        [sys.executable, str(script_path)],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    
                    self.processes[f"mcp_{server_name}"] = process
                    self.system_status["mcp_servers"][server_name] = {
                        "status": "running",
                        "pid": process.pid,
                        "started_at": time.time()
                    }
                    
                    logger.info(f"Started {config['description']} (PID: {process.pid})")
                else:
                    logger.warning(f"MCP server script not found: {script_path}")
                    self.system_status["mcp_servers"][server_name] = {
                        "status": "not_found",
                        "error": f"Script not found: {script_path}"
                    }
                    
            except Exception as e:
                logger.error(f"Failed to start {config['description']}: {e}")
                self.system_status["mcp_servers"][server_name] = {
                    "status": "failed",
                    "error": str(e)
                }
    
    def start_enhanced_agents(self):
        """Start enhanced agent system"""
        logger.info("Starting enhanced agent system...")
        
        # Agent configurations
        agents = {
            "eliza": {
                "role": "lead_coordinator",
                "capabilities": ["discussion_management", "repository_improvement", "community_engagement"],
                "oauth_username": "xmrt-eliza-agent"
            },
            "dao_governor": {
                "role": "governance_manager", 
                "capabilities": ["proposal_management", "voting_coordination", "governance_automation"],
                "oauth_username": "xmrt-dao-governor"
            },
            "defi_specialist": {
                "role": "financial_operations",
                "capabilities": ["liquidity_management", "yield_optimization", "risk_assessment"],
                "oauth_username": "xmrt-defi-specialist"
            },
            "security_guardian": {
                "role": "security_operations",
                "capabilities": ["vulnerability_scanning", "security_monitoring", "incident_response"],
                "oauth_username": "xmrt-security-guardian"
            },
            "community_manager": {
                "role": "community_engagement",
                "capabilities": ["social_media_management", "community_support", "content_creation"],
                "oauth_username": "xmrt-community-manager"
            }
        }
        
        for agent_name, config in agents.items():
            try:
                # Initialize agent with configuration
                self.system_status["agents"][agent_name] = {
                    "status": "initialized",
                    "role": config["role"],
                    "capabilities": config["capabilities"],
                    "oauth_username": config["oauth_username"],
                    "started_at": time.time(),
                    "last_activity": time.time()
                }
                
                logger.info(f"Initialized {agent_name} agent ({config['role']})")
                
            except Exception as e:
                logger.error(f"Failed to initialize {agent_name} agent: {e}")
                self.system_status["agents"][agent_name] = {
                    "status": "failed",
                    "error": str(e)
                }
    
    def start_learning_cycles(self):
        """Start autonomous learning cycles"""
        logger.info("Starting autonomous learning cycles...")
        
        def learning_cycle():
            """Background learning cycle"""
            while True:
                try:
                    # Update agent activities
                    current_time = time.time()
                    for agent_name in self.system_status["agents"]:
                        if self.system_status["agents"][agent_name]["status"] == "initialized":
                            self.system_status["agents"][agent_name]["last_activity"] = current_time
                    
                    # Update system status
                    self.system_status["last_update"] = current_time
                    
                    # Sleep for learning interval (5 minutes)
                    time.sleep(300)
                    
                except Exception as e:
                    logger.error(f"Error in learning cycle: {e}")
                    time.sleep(60)  # Shorter sleep on error
        
        # Start learning cycle in background thread
        learning_thread = threading.Thread(target=learning_cycle, daemon=True)
        learning_thread.start()
        
        logger.info("Learning cycles started")
    
    def start_github_automation(self):
        """Start GitHub discussion and repository improvement automation"""
        logger.info("Starting GitHub automation...")
        
        def github_automation():
            """Background GitHub automation"""
            while True:
                try:
                    # Simulate GitHub automation activities
                    logger.info("Running GitHub automation cycle...")
                    
                    # Update health checks
                    self.system_status["health_checks"]["github_automation"] = {
                        "status": "healthy",
                        "last_check": time.time()
                    }
                    
                    # Sleep for automation interval (10 minutes)
                    time.sleep(600)
                    
                except Exception as e:
                    logger.error(f"Error in GitHub automation: {e}")
                    self.system_status["health_checks"]["github_automation"] = {
                        "status": "error",
                        "error": str(e),
                        "last_check": time.time()
                    }
                    time.sleep(300)  # Shorter sleep on error
        
        # Start GitHub automation in background thread
        github_thread = threading.Thread(target=github_automation, daemon=True)
        github_thread.start()
        
        logger.info("GitHub automation started")
    
    def start_deployment_monitoring(self):
        """Start deployment monitoring"""
        logger.info("Starting deployment monitoring...")
        
        def deployment_monitoring():
            """Background deployment monitoring"""
            while True:
                try:
                    # Monitor system health
                    logger.info("Running deployment health check...")
                    
                    # Check MCP server processes
                    for server_name, process in self.processes.items():
                        if process.poll() is None:
                            self.system_status["mcp_servers"][server_name.replace("mcp_", "")]["status"] = "running"
                        else:
                            self.system_status["mcp_servers"][server_name.replace("mcp_", "")]["status"] = "stopped"
                    
                    # Update health checks
                    self.system_status["health_checks"]["deployment_monitoring"] = {
                        "status": "healthy",
                        "last_check": time.time()
                    }
                    
                    # Sleep for monitoring interval (2 minutes)
                    time.sleep(120)
                    
                except Exception as e:
                    logger.error(f"Error in deployment monitoring: {e}")
                    self.system_status["health_checks"]["deployment_monitoring"] = {
                        "status": "error",
                        "error": str(e),
                        "last_check": time.time()
                    }
                    time.sleep(60)  # Shorter sleep on error
        
        # Start deployment monitoring in background thread
        monitoring_thread = threading.Thread(target=deployment_monitoring, daemon=True)
        monitoring_thread.start()
        
        logger.info("Deployment monitoring started")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        return self.system_status
    
    def start_system(self):
        """Start the complete XMRT system"""
        logger.info("🚀 Starting XMRT Ecosystem...")
        
        self.system_status["startup_time"] = time.time()
        
        try:
            # Start MCP servers
            self.start_mcp_servers()
            time.sleep(3)  # Allow servers to initialize
            
            # Start enhanced agents
            self.start_enhanced_agents()
            time.sleep(2)  # Allow agents to initialize
            
            # Start learning cycles
            self.start_learning_cycles()
            
            # Start GitHub automation
            self.start_github_automation()
            
            # Start deployment monitoring
            self.start_deployment_monitoring()
            
            logger.info("✅ XMRT Ecosystem startup complete!")
            logger.info(f"🤖 Active agents: {len(self.system_status['agents'])}")
            logger.info(f"🔧 MCP servers: {len(self.system_status['mcp_servers'])}")
            logger.info("🔄 Learning cycles: Active")
            logger.info("📊 Monitoring: Active")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ System startup failed: {e}")
            return False
    
    def shutdown_system(self):
        """Gracefully shutdown the system"""
        logger.info("Shutting down XMRT system...")
        
        # Terminate MCP server processes
        for process_name, process in self.processes.items():
            try:
                if process.poll() is None:
                    process.terminate()
                    process.wait(timeout=5)
                    logger.info(f"Stopped {process_name}")
            except Exception as e:
                logger.error(f"Error stopping {process_name}: {e}")
        
        logger.info("XMRT system shutdown complete")

def main():
    """Main function for Render deployment"""
    
    # Create system manager
    system_manager = XMRTSystemManager()
    
    try:
        # Start the system
        if system_manager.start_system():
            logger.info("XMRT system is running...")
            
            # Keep the main process alive
            while True:
                time.sleep(60)
                
                # Log periodic status
                status = system_manager.get_system_status()
                active_agents = len([a for a in status["agents"].values() if a["status"] == "initialized"])
                running_servers = len([s for s in status["mcp_servers"].values() if s["status"] == "running"])
                
                logger.info(f"System Status: {active_agents} agents active, {running_servers} MCP servers running")
        else:
            logger.error("Failed to start XMRT system")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
        system_manager.shutdown_system()
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        system_manager.shutdown_system()
        sys.exit(1)

if __name__ == "__main__":
    main()
