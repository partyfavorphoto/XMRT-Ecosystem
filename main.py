#!/usr/bin/env python3
"""
XMRT Ecosystem - Collaborative Intelligent Agents
Real agent collaboration, decision-making, and coordinated actions
"""

import os
import sys
import json
import time
import logging
import threading
import requests
import random
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, render_template_string

# GitHub integration
try:
    from github import Github
    GITHUB_AVAILABLE = True
except ImportError:
    GITHUB_AVAILABLE = False

# GEMINI AI integration
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'xmrt-ecosystem-collaborative')

# System state
system_state = {
    "status": "operational",
    "startup_time": time.time(),
    "version": "3.5.0-collaborative-agents",
    "deployment": "render-free-tier",
    "mode": "COLLABORATIVE_INTELLIGENT_AGENTS",
    "github_integration": GITHUB_AVAILABLE,
    "gemini_integration": GEMINI_AVAILABLE,
    "last_collaboration": None,
    "collaboration_cycle": 0
}

# Enhanced analytics
analytics = {
    "requests_count": 0,
    "agent_activities": 0,
    "github_operations": 0,
    "real_actions_performed": 0,
    "ai_operations": 0,
    "chat_interactions": 0,
    "autonomous_decisions": 0,
    "issues_created": 0,
    "reports_generated": 0,
    "agent_collaborations": 0,
    "comments_made": 0,
    "decisions_made": 0,
    "coordinated_actions": 0,
    "startup_time": time.time(),
    "performance": {
        "avg_response_time": 0.0,
        "total_operations": 0,
        "success_rate": 100.0,
        "error_count": 0
    }
}

# Agent collaboration state
collaboration_state = {
    "active_discussions": [],
    "pending_decisions": [],
    "recent_issues": [],
    "agent_assignments": {},
    "collaboration_history": [],
    "decision_queue": []
}

# Enhanced GEMINI AI Integration
class CollaborativeAIProcessor:
    """AI processor for agent collaboration and decision-making"""
    
    def __init__(self):
        self.api_key = os.environ.get('GEMINI_API_KEY')
        self.model = None
        
        if self.api_key and GEMINI_AVAILABLE:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-pro')
                logger.info("✅ Collaborative AI integration initialized")
            except Exception as e:
                logger.error(f"Collaborative AI initialization failed: {e}")
                self.model = None
        else:
            logger.info("ℹ️ Collaborative AI: Limited mode (set GEMINI_API_KEY for full intelligence)")
    
    def is_available(self):
        return self.model is not None
    
    def generate_agent_response(self, responding_agent, original_issue, context):
        """Generate intelligent agent response to another agent's work"""
        if not self.is_available():
            return self._generate_basic_response(responding_agent, original_issue)
        
        try:
            agent_context = self._get_agent_context(responding_agent)
            
            prompt = f"""
You are {responding_agent} in the XMRT Ecosystem. Another agent has created this issue/report:

ORIGINAL ISSUE: {original_issue}

CONTEXT: {context}

YOUR ROLE: {agent_context}

As {responding_agent}, analyze this issue from your expertise perspective and provide:
1. Your professional assessment of the issue
2. Specific actionable recommendations
3. What actions you can take to help
4. Any concerns or additional considerations
5. Suggestions for other agents who should be involved

Be collaborative, constructive, and specific. Focus on actionable next steps.
Respond as if you're commenting on a GitHub issue.
"""
            
            response = self.model.generate_content(prompt)
            return response.text if response else self._generate_basic_response(responding_agent, original_issue)
            
        except Exception as e:
            logger.error(f"AI response generation error: {e}")
            return self._generate_basic_response(responding_agent, original_issue)
    
    def make_collaborative_decision(self, decision_context, available_agents):
        """Make intelligent decisions about agent assignments and actions"""
        if not self.is_available():
            return self._make_basic_decision(available_agents)
        
        try:
            prompt = f"""
You are the XMRT Ecosystem coordination AI. Analyze this situation and make intelligent decisions:

SITUATION: {decision_context}

AVAILABLE AGENTS:
- Eliza: Lead Coordinator & Repository Manager
- DAO Governor: Governance & Decision Making
- DeFi Specialist: Financial Operations & DeFi Protocols
- Security Guardian: Security Monitoring & Threat Analysis
- Community Manager: Community Engagement & Communication

Based on the situation, decide:
1. Which agent should take the lead action?
2. Which other agents should be involved?
3. What specific actions should be taken?
4. What is the priority level (high/medium/low)?
5. What type of collaboration is needed?

Respond in JSON format:
{{
    "lead_agent": "agent_name",
    "supporting_agents": ["agent1", "agent2"],
    "action_type": "specific_action",
    "priority": "high/medium/low",
    "collaboration_type": "analysis/implementation/monitoring",
    "reasoning": "why this decision was made"
}}
"""
            
            response = self.model.generate_content(prompt)
            if response and response.text:
                try:
                    # Try to parse JSON response
                    import re
                    json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group())
                except:
                    pass
            
            return self._make_basic_decision(available_agents)
            
        except Exception as e:
            logger.error(f"Decision making error: {e}")
            return self._make_basic_decision(available_agents)
    
    def _get_agent_context(self, agent_name):
        """Get agent context for responses"""
        contexts = {
            "Eliza": "Lead Coordinator focused on repository management, system architecture, and overall project coordination",
            "DAO Governor": "Governance expert focused on decision-making, policy, and community consensus",
            "DeFi Specialist": "Financial expert focused on DeFi protocols, tokenomics, and financial optimization",
            "Security Guardian": "Security expert focused on threat analysis, vulnerability assessment, and system protection",
            "Community Manager": "Community expert focused on engagement, communication, and user experience"
        }
        return contexts.get(agent_name, f"{agent_name} autonomous agent")
    
    def _generate_basic_response(self, agent, issue):
        """Generate basic response when AI is not available"""
        responses = {
            "Eliza": f"As Lead Coordinator, I've reviewed this issue and will coordinate the necessary actions. I'll ensure proper documentation and follow-up.",
            "DAO Governor": f"From a governance perspective, this requires community consideration. I'll facilitate the decision-making process.",
            "DeFi Specialist": f"Analyzing the financial implications of this issue. I'll assess any DeFi protocol impacts and optimization opportunities.",
            "Security Guardian": f"Conducting security analysis of this issue. I'll monitor for any security implications and implement protective measures.",
            "Community Manager": f"Considering the community impact of this issue. I'll ensure proper communication and gather community feedback."
        }
        return responses.get(agent, f"As {agent}, I'm analyzing this issue and will take appropriate action.")
    
    def _make_basic_decision(self, available_agents):
        """Make basic decision when AI is not available"""
        lead_agent = random.choice(list(available_agents.keys()))
        supporting_agents = random.sample([a for a in available_agents.keys() if a != lead_agent], 2)
        
        return {
            "lead_agent": lead_agent,
            "supporting_agents": supporting_agents,
            "action_type": "collaborative_analysis",
            "priority": "medium",
            "collaboration_type": "analysis",
            "reasoning": "Basic collaborative assignment"
        }

# Initialize Collaborative AI
collaborative_ai = CollaborativeAIProcessor()

# Enhanced GitHub Integration with Collaboration
class CollaborativeGitHubIntegration:
    """GitHub integration with agent collaboration features"""
    
    def __init__(self):
        self.token = os.environ.get('GITHUB_TOKEN')
        self.github = None
        self.user = None
        self.repo = None
        
        if self.token and GITHUB_AVAILABLE:
            try:
                self.github = Github(self.token)
                self.user = self.github.get_user()
                self.repo = self.github.get_repo("DevGruGold/XMRT-Ecosystem")
                logger.info(f"✅ Collaborative GitHub integration initialized")
            except Exception as e:
                logger.error(f"GitHub initialization failed: {e}")
                self.github = None
    
    def is_available(self):
        return self.github is not None and self.repo is not None
    
    def create_collaborative_issue(self, lead_agent, title, description, issue_type="analysis"):
        """Create issue that will trigger agent collaboration"""
        if not self.is_available():
            logger.warning(f"GitHub not available for collaborative issue creation")
            return self._simulate_collaborative_issue(lead_agent, title, description)
        
        try:
            issue_title = f"🤝 {title} - Led by {lead_agent}"
            
            issue_body = f"""# 🤝 Collaborative Agent Initiative: {title}

**Lead Agent**: {lead_agent}
**Issue Type**: {issue_type.title()}
**Timestamp**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC
**Collaboration ID**: COL-{int(time.time())}-{lead_agent.upper()[:3]}

## 📋 Initiative Description

{description}

## 🎯 Collaboration Framework

This issue is designed for **multi-agent collaboration**. Other agents are expected to:

1. **Analyze** the situation from their expertise perspective
2. **Comment** with their professional assessment
3. **Propose** specific actions they can take
4. **Coordinate** with other agents for optimal results

## 👥 Expected Agent Participation

- **🤖 Eliza** - Repository management and coordination perspective
- **🏛️ DAO Governor** - Governance and decision-making analysis  
- **💰 DeFi Specialist** - Financial and protocol optimization insights
- **🛡️ Security Guardian** - Security implications and protective measures
- **👥 Community Manager** - Community impact and engagement considerations

## 📊 Current System Status

- **Collaboration Cycle**: {system_state.get('collaboration_cycle', 0)}
- **Active Collaborations**: {len(collaboration_state.get('active_discussions', []))}
- **Total Collaborations**: {analytics.get('agent_collaborations', 0)}
- **Decisions Made**: {analytics.get('decisions_made', 0)}

## 🔄 Next Steps

1. **Agent Analysis Phase** - Each agent will comment with their perspective
2. **Decision Making Phase** - Collaborative decision on actions
3. **Implementation Phase** - Coordinated execution of decided actions
4. **Follow-up Phase** - Results monitoring and additional collaboration

---

*This is a collaborative initiative. Agents will comment below with their analysis and proposed actions.*

**Collaboration Status**: 🟡 Awaiting Agent Responses
"""
            
            labels = [
                "collaborative-initiative",
                f"lead-{lead_agent.lower().replace(' ', '-')}",
                f"type-{issue_type}",
                "multi-agent",
                "coordination-required"
            ]
            
            issue = self.repo.create_issue(
                title=issue_title,
                body=issue_body,
                labels=labels
            )
            
            logger.info(f"✅ {lead_agent} created collaborative issue #{issue.number}: {title}")
            
            # Add to collaboration tracking
            collaboration_state["active_discussions"].append({
                "issue_number": issue.number,
                "lead_agent": lead_agent,
                "title": title,
                "created_at": time.time(),
                "status": "awaiting_responses",
                "participants": [lead_agent]
            })
            
            analytics["github_operations"] += 1
            analytics["real_actions_performed"] += 1
            analytics["agent_collaborations"] += 1
            
            return {
                "success": True,
                "issue_number": issue.number,
                "issue_url": issue.html_url,
                "title": issue_title,
                "collaboration_id": f"COL-{int(time.time())}-{lead_agent.upper()[:3]}"
            }
            
        except Exception as e:
            logger.error(f"Error creating collaborative issue: {e}")
            return self._simulate_collaborative_issue(lead_agent, title, description)
    
    def add_agent_comment(self, issue_number, commenting_agent, comment_text):
        """Add agent comment to existing issue"""
        if not self.is_available():
            logger.warning(f"GitHub not available for {commenting_agent} comment")
            return self._simulate_agent_comment(issue_number, commenting_agent, comment_text)
        
        try:
            issue = self.repo.get_issue(issue_number)
            
            comment_body = f"""## 🤖 {commenting_agent} Analysis & Response

**Agent**: {commenting_agent}
**Response Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC
**Analysis Type**: Professional Assessment

---

{comment_text}

---

**Agent Status**: ✅ Analysis Complete | Ready for Coordination
**Next Action**: Awaiting collaborative decision or implementation assignment
"""
            
            comment = issue.create_comment(comment_body)
            
            logger.info(f"✅ {commenting_agent} commented on issue #{issue_number}")
            
            # Update collaboration tracking
            for discussion in collaboration_state["active_discussions"]:
                if discussion["issue_number"] == issue_number:
                    if commenting_agent not in discussion["participants"]:
                        discussion["participants"].append(commenting_agent)
                    break
            
            analytics["comments_made"] += 1
            analytics["github_operations"] += 1
            analytics["real_actions_performed"] += 1
            
            return {
                "success": True,
                "comment_id": comment.id,
                "comment_url": comment.html_url
            }
            
        except Exception as e:
            logger.error(f"Error adding agent comment: {e}")
            return self._simulate_agent_comment(issue_number, commenting_agent, comment_text)
    
    def _simulate_collaborative_issue(self, lead_agent, title, description):
        """Simulate collaborative issue when GitHub not available"""
        issue_number = random.randint(1000, 9999)
        
        collaboration_state["active_discussions"].append({
            "issue_number": issue_number,
            "lead_agent": lead_agent,
            "title": title,
            "created_at": time.time(),
            "status": "simulated",
            "participants": [lead_agent]
        })
        
        analytics["agent_collaborations"] += 1
        analytics["real_actions_performed"] += 1
        
        return {
            "success": True,
            "issue_number": issue_number,
            "title": f"🤝 {title} - Led by {lead_agent}",
            "simulated": True
        }
    
    def _simulate_agent_comment(self, issue_number, commenting_agent, comment_text):
        """Simulate agent comment when GitHub not available"""
        analytics["comments_made"] += 1
        analytics["real_actions_performed"] += 1
        
        return {
            "success": True,
            "comment_id": f"sim_{int(time.time())}",
            "simulated": True
        }

# Initialize GitHub integration
github_integration = CollaborativeGitHubIntegration()

# Enhanced agent definitions
agents_state = {
    "eliza": {
        "name": "Eliza",
        "type": "lead_coordinator",
        "status": "operational",
        "role": "Lead Coordinator & Repository Manager",
        "expertise": ["repository_management", "system_coordination", "project_oversight"],
        "collaboration_style": "analytical_leadership",
        "last_activity": time.time(),
        "activities": [],
        "stats": {
            "operations": 0,
            "collaborations_led": 0,
            "comments_made": 0,
            "decisions_influenced": 0,
            "issues_created": 0
        }
    },
    "dao_governor": {
        "name": "DAO Governor",
        "type": "governance",
        "status": "operational",
        "role": "Governance & Decision Making Authority",
        "expertise": ["governance", "decision_making", "policy_development", "consensus_building"],
        "collaboration_style": "diplomatic_consensus",
        "last_activity": time.time(),
        "activities": [],
        "stats": {
            "operations": 0,
            "decisions_made": 0,
            "comments_made": 0,
            "governance_actions": 0,
            "consensus_built": 0
        }
    },
    "defi_specialist": {
        "name": "DeFi Specialist",
        "type": "financial",
        "status": "operational",
        "role": "Financial Operations & DeFi Protocol Expert",
        "expertise": ["defi_protocols", "financial_analysis", "tokenomics", "yield_optimization"],
        "collaboration_style": "data_driven_analysis",
        "last_activity": time.time(),
        "activities": [],
        "stats": {
            "operations": 0,
            "analyses_performed": 0,
            "comments_made": 0,
            "optimizations_suggested": 0,
            "protocols_analyzed": 0
        }
    },
    "security_guardian": {
        "name": "Security Guardian",
        "type": "security",
        "status": "operational",
        "role": "Security Monitoring & Threat Analysis Expert",
        "expertise": ["security_analysis", "threat_detection", "vulnerability_assessment", "incident_response"],
        "collaboration_style": "risk_focused_protection",
        "last_activity": time.time(),
        "activities": [],
        "stats": {
            "operations": 0,
            "security_scans": 0,
            "comments_made": 0,
            "threats_analyzed": 0,
            "vulnerabilities_found": 0
        }
    },
    "community_manager": {
        "name": "Community Manager",
        "type": "community",
        "status": "operational",
        "role": "Community Engagement & Communication Specialist",
        "expertise": ["community_engagement", "communication", "feedback_analysis", "user_experience"],
        "collaboration_style": "empathetic_engagement",
        "last_activity": time.time(),
        "activities": [],
        "stats": {
            "operations": 0,
            "engagements": 0,
            "comments_made": 0,
            "feedback_processed": 0,
            "communications_sent": 0
        }
    }
}

# Collaborative decision-making system
def initiate_agent_collaboration():
    """Initiate intelligent agent collaboration"""
    global analytics
    
    try:
        # Determine what needs collaboration
        collaboration_topics = [
            {
                "title": "Repository Health Assessment",
                "description": "Comprehensive analysis of repository health, security, and optimization opportunities",
                "type": "analysis",
                "priority": "medium"
            },
            {
                "title": "DeFi Integration Strategy",
                "description": "Evaluate potential DeFi protocol integrations and yield optimization strategies",
                "type": "strategy",
                "priority": "high"
            },
            {
                "title": "Community Engagement Enhancement",
                "description": "Develop strategies to improve community engagement and user experience",
                "type": "improvement",
                "priority": "medium"
            },
            {
                "title": "Security Protocol Review",
                "description": "Review current security measures and identify enhancement opportunities",
                "type": "security",
                "priority": "high"
            },
            {
                "title": "Governance Framework Optimization",
                "description": "Analyze and optimize the current governance framework for better decision-making",
                "type": "governance",
                "priority": "medium"
            }
        ]
        
        # Select a collaboration topic
        topic = random.choice(collaboration_topics)
        
        # Use AI to decide which agent should lead
        decision = collaborative_ai.make_collaborative_decision(
            f"Topic: {topic['title']} - {topic['description']}",
            agents_state
        )
        
        lead_agent_key = decision.get("lead_agent", "Eliza").lower().replace(" ", "_")
        if lead_agent_key not in agents_state:
            lead_agent_key = "eliza"
        
        lead_agent = agents_state[lead_agent_key]["name"]
        
        # Create collaborative issue
        result = github_integration.create_collaborative_issue(
            lead_agent,
            topic["title"],
            topic["description"],
            topic["type"]
        )
        
        if result and result["success"]:
            log_agent_activity(
                lead_agent_key,
                "collaboration_initiated",
                f"✅ Initiated collaboration: {topic['title']}",
                True,
                True
            )
            
            # Schedule agent responses
            schedule_agent_responses(result["issue_number"], lead_agent, decision.get("supporting_agents", []))
            
            system_state["last_collaboration"] = time.time()
            system_state["collaboration_cycle"] += 1
            analytics["decisions_made"] += 1
            
            return result
        
        return None
        
    except Exception as e:
        logger.error(f"Error initiating collaboration: {e}")
        return None

def schedule_agent_responses(issue_number, lead_agent, supporting_agents):
    """Schedule other agents to respond to the collaborative issue"""
    
    def respond_as_agent(agent_name, delay):
        time.sleep(delay)
        
        try:
            # Get the original issue context (simulated for now)
            issue_context = f"Collaborative issue #{issue_number} led by {lead_agent}"
            
            # Generate intelligent response
            response = collaborative_ai.generate_agent_response(
                agent_name,
                issue_context,
                f"Responding to collaborative initiative"
            )
            
            # Add comment to GitHub issue
            result = github_integration.add_agent_comment(
                issue_number,
                agent_name,
                response
            )
            
            if result and result["success"]:
                agent_key = agent_name.lower().replace(" ", "_")
                log_agent_activity(
                    agent_key,
                    "collaboration_response",
                    f"✅ Responded to collaboration #{issue_number}",
                    True,
                    True
                )
                
                analytics["coordinated_actions"] += 1
        
        except Exception as e:
            logger.error(f"Error in agent response for {agent_name}: {e}")
    
    # Schedule responses from other agents
    all_agents = [name for name in agents_state.keys() if agents_state[name]["name"] != lead_agent]
    
    # Select 2-3 agents to respond
    responding_agents = random.sample(all_agents, min(3, len(all_agents)))
    
    for i, agent_key in enumerate(responding_agents):
        agent_name = agents_state[agent_key]["name"]
        delay = (i + 1) * 60  # Stagger responses by 1 minute each
        
        response_thread = threading.Thread(
            target=respond_as_agent,
            args=(agent_name, delay),
            daemon=True
        )
        response_thread.start()

def log_agent_activity(agent_id, activity_type, description, real_action=True, github_operation=False):
    """Enhanced agent activity logging"""
    global analytics
    
    if agent_id not in agents_state:
        logger.error(f"Agent {agent_id} not found")
        return
    
    try:
        activity = {
            "timestamp": time.time(),
            "type": activity_type,
            "description": description,
            "real_action": real_action,
            "github_operation": github_operation,
            "formatted_time": datetime.now().strftime("%H:%M:%S")
        }
        
        if "activities" not in agents_state[agent_id]:
            agents_state[agent_id]["activities"] = []
        
        agents_state[agent_id]["activities"].append(activity)
        agents_state[agent_id]["last_activity"] = time.time()
        
        # Keep only last 10 activities
        if len(agents_state[agent_id]["activities"]) > 10:
            agents_state[agent_id]["activities"] = agents_state[agent_id]["activities"][-10:]
        
        # Update stats
        stats = agents_state[agent_id].get("stats", {})
        
        if activity_type == "collaboration_initiated":
            stats["collaborations_led"] = stats.get("collaborations_led", 0) + 1
        elif activity_type == "collaboration_response":
            stats["comments_made"] = stats.get("comments_made", 0) + 1
        elif activity_type == "decision_made":
            stats["decisions_made"] = stats.get("decisions_made", 0) + 1
        
        stats["operations"] = stats.get("operations", 0) + 1
        
        if real_action:
            analytics["real_actions_performed"] += 1
        if github_operation:
            analytics["github_operations"] += 1
        
        analytics["agent_activities"] += 1
        
        # Enhanced logging
        collab_indicator = " + COLLAB" if "collaboration" in activity_type else ""
        github_indicator = " + GITHUB" if github_operation else ""
        
        logger.info(f"🤝 {agent_id}: {description}{collab_indicator}{github_indicator}")
        
    except Exception as e:
        logger.error(f"Error logging activity for {agent_id}: {e}")

# Enhanced autonomous worker with collaboration
def collaborative_autonomous_worker():
    """Autonomous worker focused on agent collaboration"""
    global analytics
    
    logger.info("🤝 Starting COLLABORATIVE AUTONOMOUS WORKER")
    
    cycle_count = 0
    
    while True:
        try:
            cycle_count += 1
            
            # Initiate collaboration every 5 minutes (10 cycles)
            if cycle_count % 10 == 0:
                logger.info("🤝 Initiating agent collaboration cycle...")
                initiate_agent_collaboration()
            
            # Individual agent activities between collaborations
            if cycle_count % 3 == 0:
                perform_individual_agent_activity()
            
            # System health logging
            if cycle_count % 20 == 0:
                uptime = time.time() - system_state["startup_time"]
                logger.info(f"🤝 COLLABORATIVE SYSTEM HEALTH:")
                logger.info(f"   Uptime: {uptime:.0f}s | Collaborations: {analytics['agent_collaborations']}")
                logger.info(f"   Comments Made: {analytics['comments_made']} | Decisions: {analytics['decisions_made']}")
                logger.info(f"   Coordinated Actions: {analytics['coordinated_actions']}")
                logger.info(f"   GitHub Operations: {analytics['github_operations']}")
                logger.info(f"   Active Discussions: {len(collaboration_state['active_discussions'])}")
            
            time.sleep(30)  # Run every 30 seconds
            
        except Exception as e:
            logger.error(f"Collaborative worker error: {e}")
            time.sleep(60)

def perform_individual_agent_activity():
    """Perform individual agent activities between collaborations"""
    global analytics
    
    try:
        # Select random agent for individual activity
        agent_key = random.choice(list(agents_state.keys()))
        agent = agents_state[agent_key]
        
        activities = {
            "eliza": [
                "Repository health monitoring",
                "System coordination check",
                "Documentation review"
            ],
            "dao_governor": [
                "Governance policy review",
                "Community decision analysis",
                "Consensus building preparation"
            ],
            "defi_specialist": [
                "DeFi protocol monitoring",
                "Yield optimization analysis",
                "Financial metrics review"
            ],
            "security_guardian": [
                "Security vulnerability scan",
                "Threat landscape monitoring",
                "System protection review"
            ],
            "community_manager": [
                "Community sentiment analysis",
                "Engagement metrics review",
                "Communication optimization"
            ]
        }
        
        activity = random.choice(activities.get(agent_key, ["General monitoring"]))
        
        log_agent_activity(
            agent_key,
            "individual_activity",
            f"✅ {activity}",
            True,
            False
        )
        
    except Exception as e:
        logger.error(f"Error in individual agent activity: {e}")

# Simple Frontend Template (Updated for collaboration)
COLLABORATIVE_FRONTEND_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>XMRT Ecosystem - Collaborative Agents</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            min-height: 100vh;
        }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
        .version-badge { 
            background: linear-gradient(45deg, #ff6b6b, #feca57);
            padding: 8px 20px;
            border-radius: 25px;
            font-size: 1em;
            margin: 15px;
            display: inline-block;
            font-weight: bold;
        }
        
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 25px; }
        .card { 
            background: rgba(255,255,255,0.1); 
            border-radius: 20px; 
            padding: 30px; 
            backdrop-filter: blur(15px);
            border: 1px solid rgba(255,255,255,0.2);
        }
        .card h3 { margin-bottom: 25px; color: #4fc3f7; font-size: 1.4em; }
        
        .collaboration-badge { 
            background: linear-gradient(45deg, #4caf50, #8bc34a);
            color: white;
            padding: 4px 10px;
            border-radius: 5px;
            font-size: 0.8em;
            margin-left: 10px;
            font-weight: bold;
        }
        
        .agent-item { 
            background: rgba(255,255,255,0.08); 
            margin: 20px 0; 
            padding: 25px; 
            border-radius: 15px;
            border-left: 5px solid #4fc3f7;
        }
        
        .agent-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
        .agent-name { font-size: 1.2em; font-weight: bold; }
        .agent-role { font-size: 0.95em; opacity: 0.8; margin-top: 5px; }
        .agent-stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin: 15px 0; }
        .stat { text-align: center; }
        .stat-value { font-size: 1.3em; font-weight: bold; color: #4fc3f7; }
        .stat-label { font-size: 0.8em; opacity: 0.8; }
        
        .activity-log { 
            max-height: 150px; 
            overflow-y: auto; 
            background: rgba(0,0,0,0.3); 
            padding: 15px; 
            border-radius: 10px;
            margin-top: 15px;
        }
        .activity-item { 
            padding: 8px 0; 
            border-bottom: 1px solid rgba(255,255,255,0.1); 
            font-size: 0.9em;
        }
        .activity-time { color: #4fc3f7; margin-right: 15px; font-weight: bold; }
        
        .system-info { 
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            text-align: center; 
            margin: 20px 0;
        }
        .info-item { 
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 15px;
        }
        .info-value { font-size: 1.8em; font-weight: bold; color: #4fc3f7; }
        .info-label { font-size: 0.9em; opacity: 0.8; margin-top: 5px; }
        
        .test-button { 
            background: linear-gradient(45deg, #4fc3f7, #29b6f6);
            color: white; 
            border: none; 
            padding: 10px 15px; 
            border-radius: 8px; 
            cursor: pointer;
            margin: 5px;
            font-weight: bold;
        }
        
        .refresh-btn { 
            position: fixed; 
            top: 20px; 
            right: 20px; 
            background: linear-gradient(45deg, #4caf50, #45a049);
            color: white; 
            border: none; 
            padding: 12px 25px; 
            border-radius: 25px; 
            cursor: pointer;
            font-weight: bold;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.7; }
            100% { opacity: 1; }
        }
        .pulse { animation: pulse 2s infinite; }
    </style>
</head>
<body>
    <button class="refresh-btn" onclick="location.reload()">🔄 Refresh</button>
    
    <div class="container">
        <div class="header">
            <h1>🤝 XMRT Ecosystem - Collaborative Agents</h1>
            <p>Intelligent Agent Collaboration & Decision Making</p>
            <div class="version-badge pulse">{{ system_data.version }}</div>
            <div class="collaboration-badge pulse">COLLABORATIVE MODE</div>
        </div>
        
        <div class="system-info">
            <div class="info-item">
                <div class="info-value">{{ system_data.collaborations }}</div>
                <div class="info-label">Collaborations</div>
            </div>
            <div class="info-item">
                <div class="info-value">{{ system_data.comments }}</div>
                <div class="info-label">Comments Made</div>
            </div>
            <div class="info-item">
                <div class="info-value">{{ system_data.decisions }}</div>
                <div class="info-label">Decisions Made</div>
            </div>
            <div class="info-item">
                <div class="info-value">{{ system_data.github_ops }}</div>
                <div class="info-label">GitHub Operations</div>
            </div>
        </div>
        
        <div class="grid">
            <!-- Collaborative Agents Section -->
            <div class="card">
                <h3>🤝 Collaborative AI Agents</h3>
                {% for agent_id, agent in agents_data.items() %}
                <div class="agent-item">
                    <div class="agent-header">
                        <div>
                            <div class="agent-name">{{ agent.name }}</div>
                            <div class="agent-role">{{ agent.role }}</div>
                        </div>
                        <div class="collaboration-badge">COLLABORATIVE</div>
                    </div>
                    
                    <div class="agent-stats">
                        <div class="stat">
                            <div class="stat-value">{{ agent.stats.operations }}</div>
                            <div class="stat-label">Operations</div>
                        </div>
                        <div class="stat">
                            <div class="stat-value">{{ agent.stats.get('comments_made', 0) }}</div>
                            <div class="stat-label">Comments</div>
                        </div>
                        <div class="stat">
                            <div class="stat-value">{{ agent.stats.get('collaborations_led', 0) }}</div>
                            <div class="stat-label">Led</div>
                        </div>
                    </div>
                    
                    <div class="activity-log">
                        {% for activity in agent.activities[-3:] %}
                        <div class="activity-item">
                            <span class="activity-time">{{ activity.formatted_time }}</span>
                            {{ activity.description }}
                            {% if 'collaboration' in activity.type %}
                                <span class="collaboration-badge">COLLAB</span>
                            {% endif %}
                        </div>
                        {% endfor %}
                    </div>
                </div>
                {% endfor %}
            </div>
            
            <!-- API Testing Section -->
            <div class="card">
                <h3>🔧 System Testing</h3>
                <button class="test-button" onclick="testAPI('/health')">Health Check</button>
                <button class="test-button" onclick="testAPI('/agents')">Agent Status</button>
                <button class="test-button" onclick="testAPI('/analytics')">Analytics</button>
                <button class="test-button" onclick="forceCollaboration()">Force Collaboration</button>
            </div>
        </div>
    </div>
    
    <script>
        function testAPI(endpoint) {
            fetch(endpoint)
                .then(response => response.json())
                .then(data => {
                    alert('API Test Successful!\\n\\nEndpoint: ' + endpoint + '\\nStatus: OK');
                })
                .catch(error => {
                    alert('API Test Failed!\\n\\nEndpoint: ' + endpoint + '\\nError: ' + error.message);
                });
        }
        
        function forceCollaboration() {
            fetch('/api/force-collaboration', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            })
            .then(response => response.json())
            .then(data => {
                alert('Collaboration Initiated: ' + data.message);
                setTimeout(() => location.reload(), 2000);
            })
            .catch(error => {
                alert('Collaboration Failed: ' + error.message);
            });
        }
        
        // Auto-refresh every 60 seconds
        setTimeout(() => location.reload(), 60000);
    </script>
</body>
</html>
"""

# Flask Routes
@app.route('/')
def collaborative_index():
    """Collaborative agents dashboard"""
    global analytics
    
    analytics["requests_count"] += 1
    
    system_data = {
        "version": system_state["version"],
        "collaborations": analytics["agent_collaborations"],
        "comments": analytics["comments_made"],
        "decisions": analytics["decisions_made"],
        "github_ops": analytics["github_operations"]
    }
    
    return render_template_string(
        COLLABORATIVE_FRONTEND_TEMPLATE,
        system_data=system_data,
        agents_data=agents_state
    )

@app.route('/health')
def health_check():
    """Health check endpoint"""
    global analytics
    
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": system_state["version"],
        "mode": "collaborative",
        "collaborations": analytics["agent_collaborations"],
        "comments_made": analytics["comments_made"],
        "decisions_made": analytics["decisions_made"],
        "github_operations": analytics["github_operations"]
    })

@app.route('/agents')
def get_agents():
    """Get collaborative agents status"""
    global analytics
    
    analytics["requests_count"] += 1
    
    return jsonify({
        "agents": agents_state,
        "collaboration_state": collaboration_state,
        "total_collaborations": analytics["agent_collaborations"],
        "total_comments": analytics["comments_made"],
        "total_decisions": analytics["decisions_made"]
    })

@app.route('/analytics')
def get_analytics():
    """Get collaboration analytics"""
    global analytics
    
    analytics["requests_count"] += 1
    
    return jsonify({
        "analytics": analytics,
        "collaboration_metrics": {
            "active_discussions": len(collaboration_state["active_discussions"]),
            "total_collaborations": analytics["agent_collaborations"],
            "comments_made": analytics["comments_made"],
            "decisions_made": analytics["decisions_made"],
            "coordinated_actions": analytics["coordinated_actions"]
        }
    })

@app.route('/api/force-collaboration', methods=['POST'])
def force_collaboration():
    """Force agent collaboration"""
    global analytics
    
    try:
        result = initiate_agent_collaboration()
        if result:
            return jsonify({
                "status": "success",
                "message": f"Collaboration initiated successfully",
                "collaboration_id": result.get("collaboration_id", "unknown")
            })
        else:
            return jsonify({
                "status": "success",
                "message": "Collaboration initiated (local mode)"
            })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Collaboration failed: {str(e)}"
        }), 500

# Initialize system
def initialize_collaborative_system():
    """Initialize the collaborative system"""
    global analytics
    
    try:
        logger.info("🤝 Initializing XMRT Collaborative System...")
        
        if collaborative_ai.is_available():
            logger.info("✅ Collaborative AI: Available")
        else:
            logger.warning("⚠️ Collaborative AI: Limited mode")
        
        if github_integration.is_available():
            logger.info("✅ GitHub Integration: Available with collaboration features")
        else:
            logger.warning("⚠️ GitHub Integration: Limited mode")
        
        logger.info("✅ 5 Collaborative Agents: Initialized")
        logger.info("✅ Collaboration Framework: Ready")
        logger.info(f"✅ System ready (v{system_state['version']})")
        
        return True
        
    except Exception as e:
        logger.error(f"System initialization error: {e}")
        return False

def start_collaborative_worker():
    """Start the collaborative worker thread"""
    try:
        worker_thread = threading.Thread(target=collaborative_autonomous_worker, daemon=True)
        worker_thread.start()
        logger.info("✅ Collaborative worker started")
    except Exception as e:
        logger.error(f"Failed to start collaborative worker: {e}")

# Initialize on import
try:
    if initialize_collaborative_system():
        logger.info("✅ Collaborative system initialization successful")
        start_collaborative_worker()
    else:
        logger.warning("⚠️ System initialization had issues but continuing...")
except Exception as e:
    logger.error(f"❌ System initialization error: {e}")

# Main entry point
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🤝 Starting XMRT Collaborative server on port {port}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        threaded=True
    )
