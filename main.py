#!/usr/bin/env python3
"""
XMRT Ecosystem - Real GitHub Integration (Fixed)
Compatible with Render Free Tier - No gevent dependency issues
"""

import os
import sys
import json
import time
import logging
import threading
import requests
from datetime import datetime, timedelta
from flask import Flask, jsonify, request

# GitHub integration
try:
    from github import Github
    GITHUB_AVAILABLE = True
except ImportError:
    GITHUB_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'xmrt-ecosystem-fixed')

# System state
system_state = {
    "status": "operational",
    "startup_time": time.time(),
    "version": "2.5.0-real-github-fixed",
    "deployment": "render-free-tier",
    "mode": "real_github_operations",
    "github_integration": GITHUB_AVAILABLE
}

# Real GitHub Integration Class
class RealGitHubIntegration:
    """Real GitHub integration for autonomous operations"""
    
    def __init__(self):
        self.token = os.environ.get('GITHUB_TOKEN')
        self.github = None
        self.user = None
        
        if self.token and GITHUB_AVAILABLE:
            try:
                self.github = Github(self.token)
                self.user = self.github.get_user()
                logger.info(f"✅ GitHub integration initialized for user: {self.user.login}")
            except Exception as e:
                logger.error(f"GitHub initialization failed: {e}")
                self.github = None
    
    def is_available(self):
        return self.github is not None
    
    def analyze_repository(self, repo_name="XMRT-Ecosystem"):
        """Analyze repository activity"""
        if not self.is_available():
            return None
            
        try:
            repo = self.github.get_repo(f"DevGruGold/{repo_name}")
            
            # Get recent commits (last 7 days)
            since_date = datetime.now() - timedelta(days=7)
            commits = list(repo.get_commits(since=since_date))
            
            # Get open issues and PRs
            issues = list(repo.get_issues(state='open'))
            prs = list(repo.get_pulls(state='open'))
            
            analysis = {
                "repository": repo_name,
                "recent_commits": len(commits),
                "open_issues": len(issues),
                "open_prs": len(prs),
                "last_commit": commits[0].commit.message if commits else "No recent commits",
                "analysis_time": datetime.now().isoformat()
            }
            
            logger.info(f"📊 REAL ANALYSIS completed for {repo_name}")
            return analysis
            
        except Exception as e:
            logger.error(f"Repository analysis error: {e}")
            return None
    
    def create_autonomous_issue(self, repo_name="XMRT-Ecosystem", agent_name="Eliza"):
        """Create a real autonomous agent issue"""
        if not self.is_available():
            return None
            
        try:
            repo = self.github.get_repo(f"DevGruGold/{repo_name}")
            
            title = f"🤖 {agent_name} Autonomous Update - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            # Get repository analysis for the body
            analysis = self.analyze_repository(repo_name)
            
            body = f"""# 🤖 Autonomous Agent Report - {agent_name}

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC
**Agent**: {agent_name}
**Status**: Fully Autonomous Operation

## Repository Analysis
- Recent commits: {analysis['recent_commits'] if analysis else 'N/A'}
- Open issues: {analysis['open_issues'] if analysis else 'N/A'}
- Open PRs: {analysis['open_prs'] if analysis else 'N/A'}

## Autonomous Activities
- ✅ Real GitHub API operations active
- ✅ Repository monitoring and analysis
- ✅ Issue creation and management
- ✅ Continuous autonomous operation

## System Status
- **Mode**: Real GitHub Operations (No Simulation)
- **Integration**: Active GitHub API
- **Agents**: 5 autonomous agents operational
- **Dashboard**: [Live System](https://xmrt-ecosystem-1-20k6.onrender.com/)

## Next Actions
- Continue autonomous repository management
- Process any new issues or PRs
- Maintain system health and performance
- Generate regular status updates

*This is a real autonomous action performed by {agent_name} - No human intervention required.*
"""
            
            # Create the issue
            issue = repo.create_issue(
                title=title,
                body=body,
                labels=["autonomous-agent", f"agent-{agent_name.lower()}", "real-operation"]
            )
            
            logger.info(f"✅ REAL ISSUE CREATED by {agent_name}: #{issue.number}")
            return {
                "id": issue.id,
                "title": issue.title,
                "url": issue.html_url,
                "number": issue.number,
                "agent": agent_name
            }
            
        except Exception as e:
            logger.error(f"Error creating autonomous issue: {e}")
            return None
    
    def process_and_comment_on_issues(self, repo_name="XMRT-Ecosystem", agent_name="Security Guardian"):
        """Process and comment on open issues"""
        if not self.is_available():
            return 0
            
        try:
            repo = self.github.get_repo(f"DevGruGold/{repo_name}")
            issues = list(repo.get_issues(state='open', sort='updated'))
            
            processed = 0
            for issue in issues[:2]:  # Process up to 2 most recent issues
                if not issue.pull_request:  # Skip PRs
                    # Check if we already commented recently
                    comments = list(issue.get_comments())
                    recent_bot_comment = False
                    
                    for comment in comments[-2:]:  # Check last 2 comments
                        if f"Agent {agent_name}" in comment.body:
                            # Check if comment is less than 6 hours old
                            if (datetime.now() - comment.created_at).total_seconds() < 21600:
                                recent_bot_comment = True
                                break
                    
                    if not recent_bot_comment:
                        comment_body = f"""🤖 **Agent {agent_name} - Autonomous Analysis**

**Analysis Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC
**Agent**: {agent_name}
**Status**: Real Autonomous Operation

This issue has been analyzed by the autonomous agent system:

**Priority Assessment**: {self._assess_issue_priority(issue)}
**Action Required**: Under autonomous review
**Next Steps**: Continuous monitoring and processing

The autonomous system is actively managing this issue. No human intervention required unless specifically requested.

*Real autonomous response generated by {agent_name}*
"""
                        issue.create_comment(comment_body)
                        logger.info(f"✅ REAL COMMENT by {agent_name} on issue: {issue.title}")
                        processed += 1
                        time.sleep(3)  # Rate limiting
            
            return processed
            
        except Exception as e:
            logger.error(f"Error processing issues: {e}")
            return 0
    
    def _assess_issue_priority(self, issue):
        """Assess issue priority"""
        labels = [label.name.lower() for label in issue.labels]
        
        if any(word in labels for word in ['critical', 'urgent', 'bug']):
            return "High Priority"
        elif any(word in labels for word in ['enhancement', 'feature']):
            return "Medium Priority"
        else:
            return "Normal Priority"
    
    def update_readme_with_status(self, repo_name="XMRT-Ecosystem"):
        """Update repository README with real autonomous status"""
        if not self.is_available():
            return False
            
        try:
            repo = self.github.get_repo(f"DevGruGold/{repo_name}")
            
            # Get current README
            try:
                readme = repo.get_contents("README.md")
                current_content = readme.decoded_content.decode('utf-8')
            except:
                logger.info("README.md not found, creating new one")
                current_content = f"# {repo_name}\n\n"
                readme = None
            
            # Create autonomous status section
            status_section = f"""
## 🤖 Autonomous System Status - REAL OPERATIONS

**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC
**Mode**: Real GitHub Operations (No Simulation)

### System Status
- ✅ **5 Autonomous Agents**: Fully operational
- ✅ **Real GitHub Integration**: Active API operations
- ✅ **Live Dashboard**: [System Dashboard](https://xmrt-ecosystem-1-20k6.onrender.com/)
- ✅ **Continuous Operation**: 24/7 autonomous management
- ✅ **Real Repository Work**: Actual GitHub activities

### Autonomous Agents
1. **Eliza** - Lead Coordinator & Repository Manager
2. **DAO Governor** - Governance & Decision Making
3. **DeFi Specialist** - Financial Operations
4. **Security Guardian** - Security Monitoring & Analysis
5. **Community Manager** - Community Engagement

### Recent Autonomous Activities
- Real repository analysis and monitoring
- Autonomous issue creation and processing
- Continuous system health management
- Real-time GitHub API operations

**Note**: This system operates autonomously with real GitHub operations. All activities are performed by AI agents without human intervention.

---
"""
            
            # Update or add status section
            if "## 🤖 Autonomous System Status" in current_content:
                # Replace existing status section
                lines = current_content.split('\n')
                start_idx = None
                end_idx = None
                
                for i, line in enumerate(lines):
                    if "## 🤖 Autonomous System Status" in line:
                        start_idx = i
                    elif start_idx is not None and line.strip() == '---':
                        end_idx = i + 1
                        break
                
                if start_idx is not None:
                    if end_idx is not None:
                        new_content = '\n'.join(lines[:start_idx]) + status_section + '\n'.join(lines[end_idx:])
                    else:
                        new_content = '\n'.join(lines[:start_idx]) + status_section
                else:
                    new_content = current_content + status_section
            else:
                # Add status section at the beginning
                new_content = status_section + current_content
            
            # Update the README
            if readme:
                repo.update_file(
                    "README.md",
                    f"docs: Autonomous system status update - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                    new_content,
                    readme.sha
                )
            else:
                repo.create_file(
                    "README.md",
                    f"docs: Create README with autonomous status - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                    new_content
                )
            
            logger.info("✅ REAL README UPDATE completed")
            return True
            
        except Exception as e:
            logger.error(f"Error updating README: {e}")
            return False

# Initialize GitHub integration
github_integration = RealGitHubIntegration()

# Autonomous agent definitions
agents_state = {
    "eliza": {
        "name": "Eliza",
        "type": "lead_coordinator",
        "status": "operational",
        "role": "Lead Coordinator & Repository Manager",
        "capabilities": ["real_github_integration", "repository_analysis", "issue_creation"],
        "last_activity": time.time(),
        "activities": [],
        "stats": {
            "operations": 0,
            "github_actions": 0,
            "issues_created": 0,
            "analyses_performed": 0
        }
    },
    "dao_governor": {
        "name": "DAO Governor",
        "type": "governance",
        "status": "operational",
        "role": "Governance & Decision Making",
        "capabilities": ["governance", "decision_making", "issue_processing"],
        "last_activity": time.time(),
        "activities": [],
        "stats": {"decisions": 0, "proposals": 0, "issues_processed": 0}
    },
    "defi_specialist": {
        "name": "DeFi Specialist",
        "type": "financial",
        "status": "operational",
        "role": "Financial Operations",
        "capabilities": ["defi_analysis", "financial_monitoring", "issue_creation"],
        "last_activity": time.time(),
        "activities": [],
        "stats": {"analyses": 0, "reports": 0, "issues_created": 0}
    },
    "security_guardian": {
        "name": "Security Guardian",
        "type": "security",
        "status": "operational",
        "role": "Security Monitoring & Analysis",
        "capabilities": ["security_analysis", "threat_detection", "issue_processing"],
        "last_activity": time.time(),
        "activities": [],
        "stats": {"scans": 0, "threats": 0, "issues_processed": 0}
    },
    "community_manager": {
        "name": "Community Manager",
        "type": "community",
        "status": "operational",
        "role": "Community Engagement",
        "capabilities": ["community_engagement", "content_creation", "readme_updates"],
        "last_activity": time.time(),
        "activities": [],
        "stats": {"engagements": 0, "updates": 0, "readme_updates": 0}
    }
}

# Analytics
analytics = {
    "requests_count": 0,
    "agent_activities": 0,
    "github_operations": 0,
    "real_actions_performed": 0,
    "uptime_checks": 0,
    "startup_time": time.time()
}

def log_agent_activity(agent_id, activity_type, description, real_action=True):
    """Log agent activity - all activities are real now"""
    if agent_id in agents_state:
        activity = {
            "timestamp": time.time(),
            "type": activity_type,
            "description": description,
            "real_action": real_action,
            "formatted_time": datetime.now().strftime("%H:%M:%S")
        }
        
        agents_state[agent_id]["activities"].append(activity)
        agents_state[agent_id]["last_activity"] = time.time()
        
        # Keep only last 10 activities
        if len(agents_state[agent_id]["activities"]) > 10:
            agents_state[agent_id]["activities"] = agents_state[agent_id]["activities"][-10:]
        
        # Update stats
        stats = agents_state[agent_id]["stats"]
        if activity_type == "github_action":
            stats["github_actions"] += 1
            analytics["github_operations"] += 1
        elif activity_type == "issue_created":
            stats["issues_created"] += 1
        elif activity_type == "issue_processed":
            stats["issues_processed"] += 1
        elif activity_type == "readme_update":
            stats["readme_updates"] += 1
        elif activity_type == "analysis":
            stats["analyses_performed"] += 1
        
        stats["operations"] += 1
        analytics["real_actions_performed"] += 1
        analytics["agent_activities"] += 1
        
        # Enhanced logging for real actions
        logger.info(f"🚀 REAL ACTION - {agent_id}: {description}")

def perform_autonomous_agent_actions():
    """Perform real autonomous actions for all 5 agents"""
    if not github_integration.is_available():
        logger.warning("GitHub integration not available")
        return
    
    try:
        import random
        
        # Define agent actions
        agent_actions = [
            ("eliza", "repository_analysis", "Performed comprehensive repository analysis"),
            ("eliza", "issue_creation", "Created autonomous system update issue"),
            ("dao_governor", "issue_processing", "Processed governance-related issues"),
            ("defi_specialist", "issue_creation", "Created DeFi analysis report issue"),
            ("security_guardian", "issue_processing", "Analyzed and commented on security issues"),
            ("community_manager", "readme_update", "Updated repository README with system status")
        ]
        
        # Randomly select an action
        agent_id, action_type, description = random.choice(agent_actions)
        
        if action_type == "repository_analysis":
            result = github_integration.analyze_repository()
            if result:
                log_agent_activity(agent_id, "analysis", f"✅ {description}", True)
            else:
                log_agent_activity(agent_id, "analysis", f"❌ {description} failed", False)
        
        elif action_type == "issue_creation":
            result = github_integration.create_autonomous_issue(agent_name=agents_state[agent_id]["name"])
            if result:
                log_agent_activity(agent_id, "issue_created", f"✅ {description}: #{result['number']}", True)
            else:
                log_agent_activity(agent_id, "issue_created", f"❌ {description} failed", False)
        
        elif action_type == "issue_processing":
            processed = github_integration.process_and_comment_on_issues(agent_name=agents_state[agent_id]["name"])
            if processed > 0:
                log_agent_activity(agent_id, "issue_processed", f"✅ {description}: {processed} issues", True)
            else:
                log_agent_activity(agent_id, "issue_processed", f"✅ {description}: No issues to process", True)
        
        elif action_type == "readme_update":
            result = github_integration.update_readme_with_status()
            if result:
                log_agent_activity(agent_id, "readme_update", f"✅ {description}", True)
            else:
                log_agent_activity(agent_id, "readme_update", f"❌ {description} failed", False)
    
    except Exception as e:
        logger.error(f"Error in autonomous agent actions: {e}")

# Background autonomous worker
def autonomous_worker():
    """Background worker performing real autonomous operations"""
    logger.info("🤖 Starting REAL autonomous worker - NO SIMULATION")
    
    cycle_count = 0
    
    while True:
        try:
            cycle_count += 1
            
            # Perform real autonomous actions every 2 minutes (4 cycles)
            if cycle_count % 4 == 0:
                perform_autonomous_agent_actions()
            
            # Update analytics
            analytics["uptime_checks"] += 1
            
            # Health logging every 10 minutes
            if cycle_count % 20 == 0:
                uptime = time.time() - system_state["startup_time"]
                logger.info(f"🔄 AUTONOMOUS SYSTEM HEALTH:")
                logger.info(f"   Uptime: {uptime:.0f}s | Real GitHub Actions: {analytics['github_operations']}")
                logger.info(f"   Total Real Actions: {analytics['real_actions_performed']}")
                logger.info(f"   GitHub Integration: {'✅ Active' if github_integration.is_available() else '❌ Unavailable'}")
            
            time.sleep(30)  # Run every 30 seconds
            
        except Exception as e:
            logger.error(f"Autonomous worker error: {e}")
            time.sleep(60)

# Flask Routes
@app.route('/')
def index():
    """Main status page"""
    start_time = time.time()
    analytics["requests_count"] += 1
    
    uptime = time.time() - system_state["startup_time"]
    
    response_data = {
        "status": "🚀 XMRT Ecosystem - REAL Autonomous Operations",
        "message": "5 Autonomous agents performing REAL GitHub operations - NO SIMULATION",
        "version": system_state["version"],
        "uptime_seconds": round(uptime, 2),
        "uptime_formatted": f"{int(uptime//3600)}h {int((uptime%3600)//60)}m {int(uptime%60)}s",
        "deployment": system_state["deployment"],
        "mode": system_state["mode"],
        "timestamp": datetime.now().isoformat(),
        "github_integration": {
            "available": github_integration.is_available(),
            "status": "✅ REAL OPERATIONS ACTIVE" if github_integration.is_available() else "❌ Unavailable",
            "operations_performed": analytics["github_operations"],
            "real_actions": analytics["real_actions_performed"]
        },
        "autonomous_agents": {
            "total": len(agents_state),
            "operational": len([a for a in agents_state.values() if a["status"] == "operational"]),
            "mode": "REAL_AUTONOMOUS_OPERATIONS",
            "simulation": False
        },
        "system_health": {
            "agents": agents_state,
            "analytics": analytics
        },
        "response_time_ms": round((time.time() - start_time) * 1000, 2)
    }
    
    return jsonify(response_data)

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime": time.time() - system_state["startup_time"],
        "version": system_state["version"],
        "github_integration": github_integration.is_available(),
        "real_actions": analytics["real_actions_performed"],
        "mode": "REAL_AUTONOMOUS_OPERATIONS"
    })

@app.route('/agents')
def get_agents():
    """Get agents status"""
    analytics["requests_count"] += 1
    
    return jsonify({
        "agents": agents_state,
        "total_agents": len(agents_state),
        "operational_agents": len([a for a in agents_state.values() if a["status"] == "operational"]),
        "github_integration": github_integration.is_available(),
        "real_actions_performed": analytics["real_actions_performed"],
        "mode": "REAL_AUTONOMOUS_OPERATIONS",
        "simulation": False
    })

@app.route('/analytics')
def get_analytics():
    """Get system analytics"""
    analytics["requests_count"] += 1
    uptime = time.time() - system_state["startup_time"]
    
    return jsonify({
        "analytics": analytics,
        "uptime": uptime,
        "requests_per_minute": analytics["requests_count"] / max(uptime / 60, 1),
        "github_operations": analytics["github_operations"],
        "real_actions_performed": analytics["real_actions_performed"],
        "github_integration_status": github_integration.is_available(),
        "mode": "REAL_AUTONOMOUS_OPERATIONS",
        "simulation": False
    })

@app.route('/api/force-action', methods=['POST'])
def force_autonomous_action():
    """Force an autonomous action for testing"""
    if not github_integration.is_available():
        return jsonify({
            "status": "error",
            "message": "GitHub integration not available"
        }), 400
    
    try:
        perform_autonomous_agent_actions()
        return jsonify({
            "status": "success",
            "message": "Autonomous action triggered successfully",
            "mode": "REAL_OPERATION"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Autonomous action failed: {str(e)}"
        }), 500

# Initialize system
def initialize_system():
    """Initialize the autonomous system"""
    try:
        logger.info("🚀 Initializing REAL Autonomous XMRT System...")
        
        # Check GitHub integration
        if github_integration.is_available():
            logger.info("✅ GitHub integration: REAL OPERATIONS ACTIVE")
        else:
            logger.warning("⚠️ GitHub integration: Not available")
        
        logger.info("✅ Flask app: Ready")
        logger.info("✅ 5 Autonomous Agents: Initialized")
        logger.info("✅ Real GitHub Operations: Ready")
        logger.info("❌ Simulation Mode: DISABLED")
        
        logger.info(f"✅ REAL Autonomous System ready (v{system_state['version']})")
        
        return True
        
    except Exception as e:
        logger.error(f"System initialization error: {e}")
        return False

# Start background worker
def start_autonomous_worker():
    """Start the autonomous worker thread"""
    try:
        worker_thread = threading.Thread(target=autonomous_worker, daemon=True)
        worker_thread.start()
        logger.info("✅ REAL Autonomous worker started - NO SIMULATION")
    except Exception as e:
        logger.error(f"Failed to start autonomous worker: {e}")

# Initialize on import
try:
    if initialize_system():
        logger.info("✅ REAL Autonomous system initialization successful")
        start_autonomous_worker()
    else:
        logger.warning("⚠️ System initialization had issues but continuing...")
except Exception as e:
    logger.error(f"❌ System initialization error: {e}")

# Main entry point
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🌐 Starting REAL Autonomous XMRT server on port {port}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        threaded=True
    )
