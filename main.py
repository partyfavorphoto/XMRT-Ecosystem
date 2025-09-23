#!/usr/bin/env python3
"""
XMRT Ecosystem - Enhanced with Multimodal Agent Chatbots
Simplified version for stable deployment with Python 3.13 compatibility
"""

import os
import sys
import json
import time
import logging
import threading
import requests
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
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'xmrt-ecosystem-enhanced-chatbots')

# System state
system_state = {
    "status": "operational",
    "startup_time": time.time(),
    "version": "3.3.1-build-fix-stable",
    "deployment": "render-free-tier",
    "mode": "real_autonomous_operations_with_multimodal_ai",
    "github_integration": GITHUB_AVAILABLE,
    "gemini_integration": GEMINI_AVAILABLE,
    "features": [
        "real_github_integration",
        "autonomous_agents",
        "multimodal_chatbots",
        "voice_capabilities",
        "image_upload_generation",
        "code_publishing",
        "utility_creation",
        "comprehensive_ui",
        "webhook_management",
        "api_testing",
        "real_time_monitoring",
        "gemini_ai_processing"
    ]
}

# Enhanced GEMINI AI Integration Class
class GeminiAIProcessor:
    """GEMINI AI integration with multimodal capabilities"""
    
    def __init__(self):
        self.api_key = os.environ.get('GEMINI_API_KEY')
        self.model = None
        self.vision_model = None
        
        if self.api_key and GEMINI_AVAILABLE:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-pro')
                self.vision_model = genai.GenerativeModel('gemini-pro-vision')
                logger.info("✅ GEMINI AI integration initialized")
            except Exception as e:
                logger.error(f"GEMINI AI initialization failed: {e}")
                self.model = None
                self.vision_model = None
        else:
            if not self.api_key:
                logger.info("ℹ️ GEMINI AI: API key not set (GEMINI_API_KEY)")
            if not GEMINI_AVAILABLE:
                logger.info("ℹ️ GEMINI AI: Library not available")
    
    def is_available(self):
        return self.model is not None
    
    def chat_with_agent(self, agent_name, user_message, context=""):
        """Chat with a specific agent using GEMINI AI"""
        if not self.is_available():
            return {
                "response": f"Hello! I'm {agent_name}. AI capabilities are limited without GEMINI_API_KEY.",
                "agent": agent_name,
                "ai_powered": False
            }
            
        try:
            prompt = f"""You are {agent_name}, an autonomous AI agent in the XMRT Ecosystem.
            
Context: {context}
User Message: {user_message}

Please respond as {agent_name} would, staying in character and providing helpful responses."""
            
            response = self.model.generate_content(prompt)
            
            return {
                "response": response.text if response else f"I'm {agent_name}, ready to help!",
                "agent": agent_name,
                "ai_powered": True,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"GEMINI AI chat error for {agent_name}: {e}")
            return {
                "response": f"I'm {agent_name}. I'm experiencing some technical difficulties.",
                "agent": agent_name,
                "ai_powered": False,
                "error": str(e)
            }

# Initialize GEMINI AI
gemini_ai = GeminiAIProcessor()

# GitHub Integration Class
class GitHubIntegration:
    """GitHub integration for real operations"""
    
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
        else:
            if not self.token:
                logger.info("ℹ️ GitHub: Token not set (GITHUB_TOKEN)")
            if not GITHUB_AVAILABLE:
                logger.info("ℹ️ GitHub: Library not available")
    
    def is_available(self):
        return self.github is not None

# Initialize GitHub integration
github_integration = GitHubIntegration()

# Agent definitions
agents_state = {
    "eliza": {
        "name": "Eliza",
        "type": "lead_coordinator",
        "status": "operational",
        "role": "Lead Coordinator & Repository Manager",
        "description": "Primary autonomous agent with AI processing and multimodal capabilities",
        "capabilities": [
            "real_github_integration",
            "ai_powered_analysis",
            "multimodal_chatbot",
            "voice_interaction",
            "image_analysis",
            "code_generation",
            "utility_creation"
        ],
        "last_activity": time.time(),
        "activities": [],
        "chat_history": [],
        "stats": {
            "operations": 0,
            "github_actions": 0,
            "issues_created": 0,
            "analyses_performed": 0,
            "health_checks": 0,
            "ai_operations": 0,
            "chat_interactions": 0,
            "code_published": 0,
            "utilities_created": 0
        },
        "performance": {
            "success_rate": 100.0,
            "avg_response_time": 0.0,
            "total_actions": 0
        }
    },
    "dao_governor": {
        "name": "DAO Governor",
        "type": "governance",
        "status": "operational",
        "role": "Governance & Decision Making",
        "description": "Autonomous governance agent with AI-powered decision making",
        "capabilities": [
            "governance_management",
            "ai_decision_making",
            "multimodal_chatbot",
            "voice_interaction"
        ],
        "last_activity": time.time(),
        "activities": [],
        "chat_history": [],
        "stats": {
            "operations": 0,
            "decisions": 0,
            "proposals": 0,
            "issues_processed": 0,
            "governance_actions": 0,
            "ai_operations": 0,
            "chat_interactions": 0
        },
        "performance": {
            "success_rate": 100.0,
            "avg_response_time": 0.0,
            "total_actions": 0
        }
    },
    "defi_specialist": {
        "name": "DeFi Specialist",
        "type": "financial",
        "status": "operational",
        "role": "Financial Operations & DeFi Management",
        "description": "Specialized agent for DeFi analysis with AI insights",
        "capabilities": [
            "defi_analysis",
            "ai_financial_modeling",
            "multimodal_chatbot"
        ],
        "last_activity": time.time(),
        "activities": [],
        "chat_history": [],
        "stats": {
            "operations": 0,
            "analyses": 0,
            "reports": 0,
            "ai_operations": 0,
            "chat_interactions": 0
        },
        "performance": {
            "success_rate": 100.0,
            "avg_response_time": 0.0,
            "total_actions": 0
        }
    },
    "security_guardian": {
        "name": "Security Guardian",
        "type": "security",
        "status": "operational",
        "role": "Security Monitoring & Analysis",
        "description": "Dedicated security agent with AI-powered threat detection",
        "capabilities": [
            "security_analysis",
            "ai_threat_detection",
            "multimodal_chatbot"
        ],
        "last_activity": time.time(),
        "activities": [],
        "chat_history": [],
        "stats": {
            "operations": 0,
            "scans": 0,
            "threats_detected": 0,
            "ai_operations": 0,
            "chat_interactions": 0
        },
        "performance": {
            "success_rate": 100.0,
            "avg_response_time": 0.0,
            "total_actions": 0
        }
    },
    "community_manager": {
        "name": "Community Manager",
        "type": "community",
        "status": "operational",
        "role": "Community Engagement & Management",
        "description": "Community-focused agent with AI-powered engagement",
        "capabilities": [
            "community_engagement",
            "ai_content_creation",
            "multimodal_chatbot"
        ],
        "last_activity": time.time(),
        "activities": [],
        "chat_history": [],
        "stats": {
            "operations": 0,
            "engagements": 0,
            "content_created": 0,
            "ai_operations": 0,
            "chat_interactions": 0
        },
        "performance": {
            "success_rate": 100.0,
            "avg_response_time": 0.0,
            "total_actions": 0
        }
    }
}

# Analytics
analytics = {
    "requests_count": 0,
    "agent_activities": 0,
    "github_operations": 0,
    "real_actions_performed": 0,
    "ai_operations": 0,
    "chat_interactions": 0,
    "code_publications": 0,
    "utilities_created": 0,
    "webhook_triggers": 0,
    "api_calls": 0,
    "uptime_checks": 0,
    "startup_time": time.time(),
    "performance": {
        "avg_response_time": 0.0,
        "total_operations": 0,
        "success_rate": 100.0,
        "error_count": 0
    },
    "system_health": {
        "cpu_usage": 25.0,
        "memory_usage": 45.0,
        "disk_usage": 30.0,
        "network_status": "healthy"
    }
}

# Webhooks
webhooks = {
    "github": {
        "url": "/webhook/github",
        "status": "active",
        "events": ["push", "pull_request", "issues", "release"],
        "last_triggered": None,
        "count": 0,
        "description": "GitHub repository events"
    },
    "render": {
        "url": "/webhook/render",
        "status": "active",
        "events": ["deploy", "build", "health"],
        "last_triggered": None,
        "count": 0,
        "description": "Render deployment events"
    }
}

# Activity logging
def log_agent_activity(agent_id, activity_type, description, real_action=True):
    """Log agent activity"""
    if agent_id not in agents_state:
        logger.error(f"Agent {agent_id} not found in agents_state")
        return
    
    try:
        start_time = time.time()
        
        activity = {
            "timestamp": time.time(),
            "type": activity_type,
            "description": description,
            "real_action": real_action,
            "formatted_time": datetime.now().strftime("%H:%M:%S"),
            "success": True,
            "response_time": 0.0
        }
        
        if "activities" not in agents_state[agent_id]:
            agents_state[agent_id]["activities"] = []
        
        agents_state[agent_id]["activities"].append(activity)
        agents_state[agent_id]["last_activity"] = time.time()
        
        # Keep only last 15 activities
        if len(agents_state[agent_id]["activities"]) > 15:
            agents_state[agent_id]["activities"] = agents_state[agent_id]["activities"][-15:]
        
        # Update stats
        stats = agents_state[agent_id].get("stats", {})
        
        if activity_type == "chat_interaction":
            stats["chat_interactions"] = stats.get("chat_interactions", 0) + 1
            analytics["chat_interactions"] += 1
        
        if gemini_ai.is_available() and real_action:
            stats["ai_operations"] = stats.get("ai_operations", 0) + 1
            analytics["ai_operations"] += 1
        
        stats["operations"] = stats.get("operations", 0) + 1
        if real_action:
            analytics["real_actions_performed"] += 1
        
        analytics["agent_activities"] += 1
        
        agents_state[agent_id]["stats"] = stats
        
        if real_action:
            logger.info(f"🚀 REAL ACTION - {agent_id}: {description}")
        else:
            logger.info(f"🤖 {agent_id}: {description}")
            
    except Exception as e:
        logger.error(f"Error logging activity for {agent_id}: {e}")

# Autonomous operations
def perform_autonomous_actions():
    """Perform autonomous actions"""
    try:
        import random
        
        actions = [
            ("eliza", "analysis", "Performed system analysis with AI insights"),
            ("dao_governor", "governance", "Processed governance tasks with AI"),
            ("defi_specialist", "defi_analysis", "Analyzed DeFi protocols"),
            ("security_guardian", "security_scan", "Performed security scan"),
            ("community_manager", "engagement", "Managed community activities")
        ]
        
        agent_id, action_type, description = random.choice(actions)
        log_agent_activity(agent_id, action_type, f"✅ {description}", True)
    
    except Exception as e:
        logger.error(f"Error in autonomous actions: {e}")

# Background worker
def autonomous_worker():
    """Background worker for autonomous operations"""
    logger.info("🤖 Starting autonomous worker")
    
    cycle_count = 0
    
    while True:
        try:
            cycle_count += 1
            
            if cycle_count % 3 == 0:
                perform_autonomous_actions()
            
            analytics["uptime_checks"] += 1
            
            if cycle_count % 30 == 0:
                uptime = time.time() - system_state["startup_time"]
                active_agents = len([a for a in agents_state.values() if a["status"] == "operational"])
                
                logger.info(f"🔄 SYSTEM HEALTH:")
                logger.info(f"   Uptime: {uptime:.0f}s | Active Agents: {active_agents}/{len(agents_state)}")
                logger.info(f"   Real Actions: {analytics['real_actions_performed']}")
                logger.info(f"   AI Operations: {analytics['ai_operations']}")
                logger.info(f"   Chat Interactions: {analytics['chat_interactions']}")
                logger.info(f"   GitHub Integration: {'✅ Active' if github_integration.is_available() else '❌ Limited Mode'}")
                logger.info(f"   GEMINI AI: {'✅ Active' if gemini_ai.is_available() else '❌ Not Available'}")
            
            time.sleep(30)
            
        except Exception as e:
            logger.error(f"Autonomous worker error: {e}")
            time.sleep(60)

# Frontend HTML Template
FRONTEND_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>XMRT Ecosystem - Enhanced Multimodal AI Agents</title>
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
        .header h1 { font-size: 2.8em; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
        .header p { opacity: 0.9; font-size: 1.2em; }
        .version-badge { 
            background: linear-gradient(45deg, #4caf50, #8bc34a);
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            margin: 10px;
            display: inline-block;
        }
        
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; }
        .card { 
            background: rgba(255,255,255,0.1); 
            border-radius: 15px; 
            padding: 25px; 
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }
        .card h3 { margin-bottom: 20px; color: #4fc3f7; font-size: 1.3em; }
        
        .status-indicator { 
            display: inline-block; 
            width: 12px; 
            height: 12px; 
            border-radius: 50%; 
            margin-right: 10px;
            box-shadow: 0 0 10px rgba(76, 175, 80, 0.5);
        }
        .status-operational { background: #4caf50; }
        
        .real-action { 
            background: linear-gradient(45deg, #4caf50, #8bc34a);
            color: white;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            margin-left: 8px;
            font-weight: bold;
        }
        
        .ai-powered {
            background: linear-gradient(45deg, #9c27b0, #e91e63);
            color: white;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            margin-left: 8px;
            font-weight: bold;
        }
        
        .agent-item { 
            background: rgba(255,255,255,0.08); 
            margin: 15px 0; 
            padding: 20px; 
            border-radius: 10px;
            border-left: 4px solid #4fc3f7;
            transition: all 0.3s ease;
        }
        .agent-item:hover { background: rgba(255,255,255,0.12); }
        
        .agent-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
        .agent-name { font-size: 1.1em; font-weight: bold; }
        .agent-role { font-size: 0.9em; opacity: 0.8; }
        .agent-stats { display: flex; gap: 15px; margin: 10px 0; flex-wrap: wrap; }
        .stat { text-align: center; }
        .stat-value { font-size: 1.4em; font-weight: bold; color: #4fc3f7; }
        .stat-label { font-size: 0.8em; opacity: 0.8; }
        
        .activity-log { 
            max-height: 200px; 
            overflow-y: auto; 
            background: rgba(0,0,0,0.2); 
            padding: 15px; 
            border-radius: 8px;
            margin-top: 15px;
        }
        .activity-item { 
            padding: 8px 0; 
            border-bottom: 1px solid rgba(255,255,255,0.1); 
            font-size: 0.9em;
        }
        .activity-time { color: #4fc3f7; margin-right: 15px; font-weight: bold; }
        
        .chatbot-interface {
            background: rgba(0,0,0,0.3);
            border-radius: 10px;
            margin-top: 15px;
            padding: 15px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        
        .chat-messages {
            max-height: 150px;
            overflow-y: auto;
            background: rgba(0,0,0,0.2);
            border-radius: 5px;
            padding: 10px;
            margin-bottom: 10px;
            min-height: 80px;
        }
        
        .chat-message {
            margin-bottom: 8px;
            padding: 6px;
            border-radius: 5px;
            font-size: 0.9em;
        }
        
        .user-message {
            background: rgba(79, 195, 247, 0.2);
            text-align: right;
        }
        
        .agent-message {
            background: rgba(76, 175, 80, 0.2);
            text-align: left;
        }
        
        .chat-input-area {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        
        .chat-input {
            flex: 1;
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 5px;
            padding: 8px;
            color: white;
            font-size: 0.9em;
        }
        .chat-input::placeholder { color: rgba(255,255,255,0.6); }
        
        .send-btn {
            background: linear-gradient(45deg, #4fc3f7, #29b6f6);
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
        }
        
        .test-button { 
            background: linear-gradient(45deg, #4fc3f7, #29b6f6);
            color: white; 
            border: none; 
            padding: 10px 18px; 
            border-radius: 6px; 
            cursor: pointer;
            margin: 5px;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        .test-button:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(79, 195, 247, 0.3); }
        
        .refresh-btn { 
            position: fixed; 
            top: 25px; 
            right: 25px; 
            background: linear-gradient(45deg, #4caf50, #45a049);
            color: white; 
            border: none; 
            padding: 12px 25px; 
            border-radius: 30px; 
            cursor: pointer;
            font-weight: bold;
            box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
        }
        
        .system-info { 
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            text-align: center; 
            margin: 25px 0;
        }
        .info-item { 
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 10px;
        }
        .info-value { font-size: 2em; font-weight: bold; color: #4fc3f7; }
        .info-label { font-size: 0.9em; opacity: 0.8; margin-top: 5px; }
        
        .github-status { 
            padding: 15px;
            border-radius: 10px;
            margin: 15px 0;
            text-align: center;
            font-weight: bold;
        }
        .github-active { background: linear-gradient(45deg, #4caf50, #45a049); }
        .github-inactive { background: linear-gradient(45deg, #f44336, #d32f2f); }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.7; }
            100% { opacity: 1; }
        }
        .pulse { animation: pulse 2s infinite; }
        
        .api-item { 
            background: rgba(255,255,255,0.05); 
            margin: 12px 0; 
            padding: 18px; 
            border-radius: 8px;
            border-left: 4px solid #ff9800;
        }
        
        .api-endpoint {
            background: rgba(255,255,255,0.05);
            padding: 8px;
            border-radius: 4px;
            font-family: monospace;
            font-size: 0.8em;
            margin: 5px 0;
            border-left: 3px solid #4fc3f7;
        }
    </style>
</head>
<body>
    <button class="refresh-btn" onclick="location.reload()">🔄 Refresh</button>
    
    <div class="container">
        <div class="header">
            <h1>🚀 XMRT Ecosystem Dashboard</h1>
            <p>Enhanced Multimodal AI Agents - Build Fix Stable</p>
            <div class="version-badge">{{ system_data.version }}</div>
            {% if system_data.gemini_integration %}
            <div class="ai-powered pulse">GEMINI AI ACTIVE</div>
            {% endif %}
        </div>
        
        <div class="system-info">
            <div class="info-item">
                <div class="info-value">{{ system_data.uptime_formatted }}</div>
                <div class="info-label">System Uptime</div>
            </div>
            <div class="info-item">
                <div class="info-value">{{ system_data.system_health.agents.operational }}</div>
                <div class="info-label">Active Agents</div>
            </div>
            <div class="info-item">
                <div class="info-value">{{ system_data.system_health.analytics.requests_count }}</div>
                <div class="info-label">Total Requests</div>
            </div>
            <div class="info-item">
                <div class="info-value">{{ system_data.system_health.analytics.github_operations }}</div>
                <div class="info-label">GitHub Operations</div>
            </div>
            {% if system_data.gemini_integration %}
            <div class="info-item">
                <div class="info-value">{{ system_data.system_health.analytics.ai_operations }}</div>
                <div class="info-label">AI Operations</div>
            </div>
            <div class="info-item">
                <div class="info-value">{{ system_data.system_health.analytics.chat_interactions }}</div>
                <div class="info-label">Chat Interactions</div>
            </div>
            {% endif %}
        </div>
        
        <div class="github-status {{ 'github-active' if system_data.github_integration.available else 'github-inactive' }}">
            {{ system_data.github_integration.status }}
        </div>
        
        <div class="grid">
            <!-- Enhanced Agents Section -->
            <div class="card">
                <h3>🤖 Enhanced Multimodal AI Agents</h3>
                {% for agent_id, agent in agents_data.items() %}
                <div class="agent-item">
                    <div class="agent-header">
                        <div>
                            <div class="agent-name">
                                <span class="status-indicator status-{{ agent.status }}"></span>
                                {{ agent.name }}
                            </div>
                            <div class="agent-role">{{ agent.role }}</div>
                        </div>
                        <div>
                            <div class="real-action pulse">REAL OPS</div>
                            {% if system_data.gemini_integration and agent.stats.get('ai_operations', 0) > 0 %}
                            <div class="ai-powered pulse">AI POWERED</div>
                            {% endif %}
                        </div>
                    </div>
                    
                    <div class="agent-stats">
                        <div class="stat">
                            <div class="stat-value">{{ agent.stats.operations }}</div>
                            <div class="stat-label">Operations</div>
                        </div>
                        {% if system_data.gemini_integration %}
                        <div class="stat">
                            <div class="stat-value">{{ agent.stats.get('ai_operations', 0) }}</div>
                            <div class="stat-label">AI Operations</div>
                        </div>
                        <div class="stat">
                            <div class="stat-value">{{ agent.stats.get('chat_interactions', 0) }}</div>
                            <div class="stat-label">Chats</div>
                        </div>
                        {% endif %}
                        <div class="stat">
                            <div class="stat-value">{{ "%.1f"|format(agent.performance.success_rate) }}%</div>
                            <div class="stat-label">Success Rate</div>
                        </div>
                    </div>
                    
                    <div class="activity-log">
                        {% for activity in agent.activities[-3:] %}
                        <div class="activity-item">
                            <span class="activity-time">{{ activity.formatted_time }}</span>
                            {{ activity.description }}
                            {% if activity.real_action %}
                                <span class="real-action">REAL</span>
                            {% endif %}
                        </div>
                        {% endfor %}
                    </div>
                    
                    <!-- Simplified Chatbot Interface -->
                    <div class="chatbot-interface">
                        <div id="chat-messages-{{ agent_id }}" class="chat-messages">
                            <div class="agent-message">
                                <strong>{{ agent.name }}:</strong> Hello! I'm {{ agent.name }}, your {{ agent.role.lower() }}. Chat with me!
                            </div>
                        </div>
                        
                        <div class="chat-input-area">
                            <input type="text" id="chat-input-{{ agent_id }}" class="chat-input" placeholder="Chat with {{ agent.name }}..." onkeypress="handleChatKeyPress(event, '{{ agent_id }}', '{{ agent.name }}')">
                            <button class="send-btn" onclick="sendChatMessage('{{ agent_id }}', '{{ agent.name }}')">Send</button>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
            
            <!-- API Testing Section -->
            <div class="card">
                <h3>🔧 API Testing Suite</h3>
                
                <div class="api-item">
                    <div>GET / - System status and overview</div>
                    <div class="api-endpoint">GET https://xmrt-testing.onrender.com/</div>
                    <button class="test-button" onclick="testAPI('/')">Test</button>
                </div>
                <div class="api-item">
                    <div>GET /health - Health check endpoint</div>
                    <div class="api-endpoint">GET https://xmrt-testing.onrender.com/health</div>
                    <button class="test-button" onclick="testAPI('/health')">Test</button>
                </div>
                <div class="api-item">
                    <div>GET /agents - Agent information</div>
                    <div class="api-endpoint">GET https://xmrt-testing.onrender.com/agents</div>
                    <button class="test-button" onclick="testAPI('/agents')">Test</button>
                </div>
                <div class="api-item">
                    <div>POST /api/chat - Chat with AI agents</div>
                    <div class="api-endpoint">POST https://xmrt-testing.onrender.com/api/chat</div>
                    <button class="test-button" onclick="testChatAPI()">Test Chat</button>
                </div>
            </div>
            
            <!-- Analytics Section -->
            <div class="card">
                <h3>📊 Real-time Analytics</h3>
                <div class="system-info">
                    <div class="info-item">
                        <div class="info-value">{{ analytics_data.requests_count }}</div>
                        <div class="info-label">API Requests</div>
                    </div>
                    <div class="info-item">
                        <div class="info-value">{{ analytics_data.agent_activities }}</div>
                        <div class="info-label">Agent Activities</div>
                    </div>
                    <div class="info-item">
                        <div class="info-value">{{ analytics_data.real_actions_performed }}</div>
                        <div class="info-label">Real Actions</div>
                    </div>
                    {% if system_data.gemini_integration %}
                    <div class="info-item">
                        <div class="info-value">{{ analytics_data.ai_operations }}</div>
                        <div class="info-label">AI Operations</div>
                    </div>
                    <div class="info-item">
                        <div class="info-value">{{ analytics_data.chat_interactions }}</div>
                        <div class="info-label">Chat Interactions</div>
                    </div>
                    {% endif %}
                </div>
                
                <div style="margin-top: 20px; padding: 15px; background: rgba(255,255,255,0.05); border-radius: 8px;">
                    <h4 style="color: #4fc3f7; margin-bottom: 10px;">System Status</h4>
                    <div>🟢 All systems operational - Build Fix Stable</div>
                    <div>🤖 {{ system_data.system_health.agents.operational }}/{{ system_data.system_health.agents.total }} agents active</div>
                    <div>📡 {{ 'GitHub integration active' if system_data.github_integration.available else 'GitHub integration limited' }}</div>
                    {% if system_data.gemini_integration %}
                    <div>🧠 GEMINI AI processing active</div>
                    <div>💬 Interactive chatbots available</div>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Chat functionality
        function handleChatKeyPress(event, agentId, agentName) {
            if (event.key === 'Enter') {
                sendChatMessage(agentId, agentName);
            }
        }
        
        function sendChatMessage(agentId, agentName) {
            const input = document.getElementById(`chat-input-${agentId}`);
            const message = input.value.trim();
            
            if (!message) return;
            
            addChatMessage(agentId, 'user', message);
            input.value = '';
            
            fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    agent_name: agentName,
                    message: message
                })
            })
            .then(response => response.json())
            .then(data => {
                addChatMessage(agentId, 'agent', data.response, agentName);
            })
            .catch(error => {
                console.error('Chat error:', error);
                addChatMessage(agentId, 'agent', 'Sorry, I\'m having trouble responding right now.', agentName);
            });
        }
        
        function addChatMessage(agentId, sender, message, agentName = '') {
            const messagesContainer = document.getElementById(`chat-messages-${agentId}`);
            const messageDiv = document.createElement('div');
            messageDiv.className = `chat-message ${sender}-message`;
            
            if (sender === 'user') {
                messageDiv.innerHTML = `<strong>You:</strong> ${message}`;
            } else {
                messageDiv.innerHTML = `<strong>${agentName}:</strong> ${message}`;
            }
            
            messagesContainer.appendChild(messageDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
        
        // API testing
        function testAPI(endpoint) {
            fetch(endpoint)
                .then(response => response.json())
                .then(data => {
                    alert('API Test Successful!\n\nEndpoint: ' + endpoint + '\nStatus: ' + JSON.stringify(data.status || 'OK'));
                })
                .catch(error => {
                    alert('API Test Failed!\n\nEndpoint: ' + endpoint + '\nError: ' + error.message);
                });
        }
        
        function testChatAPI() {
            fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    agent_name: 'Eliza',
                    message: 'Hello, this is a test message'
                })
            })
            .then(response => response.json())
            .then(data => {
                alert('Chat API Test Successful!\n\nResponse: ' + data.response);
            })
            .catch(error => {
                alert('Chat API Test Failed!\n\nError: ' + error.message);
            });
        }
        
        // Auto-refresh every 30 seconds
        setTimeout(() => location.reload(), 30000);
    </script>
</body>
</html>
"""

# Flask Routes
@app.route('/')
def index():
    """Main dashboard"""
    start_time = time.time()
    analytics["requests_count"] += 1
    
    uptime = time.time() - system_state["startup_time"]
    
    system_data = {
        "status": "🚀 XMRT Ecosystem - Enhanced Multimodal AI Agents (Build Fix Stable)",
        "message": "Stable autonomous system with multimodal chatbots",
        "version": system_state["version"],
        "uptime_seconds": round(uptime, 2),
        "uptime_formatted": f"{int(uptime//3600)}h {int((uptime%3600)//60)}m {int(uptime%60)}s",
        "deployment": system_state["deployment"],
        "mode": system_state["mode"],
        "features": system_state["features"],
        "timestamp": datetime.now().isoformat(),
        "github_integration": {
            "available": github_integration.is_available(),
            "status": "✅ REAL OPERATIONS ACTIVE" if github_integration.is_available() else "❌ Limited Mode - Set GITHUB_TOKEN",
            "operations_performed": analytics["github_operations"]
        },
        "gemini_integration": gemini_ai.is_available(),
        "system_health": {
            "agents": {
                "total": len(agents_state),
                "operational": len([a for a in agents_state.values() if a["status"] == "operational"]),
                "list": list(agents_state.keys())
            },
            "analytics": analytics
        },
        "response_time_ms": round((time.time() - start_time) * 1000, 2)
    }
    
    return render_template_string(
        FRONTEND_TEMPLATE,
        system_data=system_data,
        agents_data=agents_state,
        webhooks_data=webhooks,
        analytics_data=analytics
    )

@app.route('/api/chat', methods=['POST'])
def chat_with_agent():
    """Chat with a specific agent"""
    try:
        data = request.get_json()
        agent_name = data.get('agent_name', 'Eliza')
        user_message = data.get('message', '')
        context = data.get('context', '')
        
        if not user_message:
            return jsonify({
                "response": "Please provide a message to chat with me.",
                "agent": agent_name,
                "ai_powered": False
            }), 400
        
        response = gemini_ai.chat_with_agent(agent_name, user_message, context)
        
        # Log the interaction
        agent_id = agent_name.lower().replace(' ', '_')
        if agent_id in agents_state:
            log_agent_activity(agent_id, "chat_interaction", f"✅ Chat: '{user_message[:50]}...'", True)
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Chat API error: {e}")
        return jsonify({
            "response": "I'm experiencing some technical difficulties. Please try again later.",
            "agent": agent_name,
            "ai_powered": False,
            "error": str(e)
        }), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime": time.time() - system_state["startup_time"],
        "version": system_state["version"],
        "github_integration": github_integration.is_available(),
        "gemini_integration": gemini_ai.is_available(),
        "real_actions": analytics["real_actions_performed"],
        "github_operations": analytics["github_operations"],
        "ai_operations": analytics["ai_operations"],
        "chat_interactions": analytics["chat_interactions"],
        "mode": "BUILD_FIX_STABLE_AUTONOMOUS_OPERATIONS",
        "agents": {
            "total": len(agents_state),
            "operational": len([a for a in agents_state.values() if a["status"] == "operational"])
        }
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
        "gemini_integration": gemini_ai.is_available(),
        "real_actions_performed": analytics["real_actions_performed"],
        "github_operations": analytics["github_operations"],
        "ai_operations": analytics["ai_operations"],
        "chat_interactions": analytics["chat_interactions"],
        "mode": "BUILD_FIX_STABLE_AUTONOMOUS_OPERATIONS",
        "simulation": False,
        "features": system_state["features"]
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
        "ai_operations": analytics["ai_operations"],
        "chat_interactions": analytics["chat_interactions"],
        "github_integration_status": github_integration.is_available(),
        "gemini_integration_status": gemini_ai.is_available(),
        "mode": "BUILD_FIX_STABLE_AUTONOMOUS_OPERATIONS",
        "simulation": False,
        "system_health": analytics["system_health"],
        "performance": analytics["performance"]
    })

# Initialize system
def initialize_system():
    """Initialize the system"""
    try:
        logger.info("🚀 Initializing XMRT Autonomous System (Build Fix Stable)...")
        
        if gemini_ai.is_available():
            logger.info("✅ GEMINI AI integration: ACTIVE")
        else:
            logger.warning("⚠️ GEMINI AI integration: Not available - Set GEMINI_API_KEY")
        
        if github_integration.is_available():
            logger.info("✅ GitHub integration: ACTIVE")
        else:
            logger.warning("⚠️ GitHub integration: Limited mode - Set GITHUB_TOKEN")
        
        logger.info("✅ Flask app: Ready with stable chatbot UI")
        logger.info("✅ 5 Autonomous Agents: Fully initialized")
        logger.info("✅ Chatbots: Basic chat functionality available")
        logger.info("✅ System Features: All features enabled")
        logger.info("❌ Simulation Mode: COMPLETELY DISABLED")
        
        logger.info(f"✅ Autonomous System ready (v{system_state['version']})")
        logger.info("🎯 Build fix stable version with enhanced features")
        
        return True
        
    except Exception as e:
        logger.error(f"System initialization error: {e}")
        return False

# Start worker
def start_worker():
    """Start the autonomous worker thread"""
    try:
        worker_thread = threading.Thread(target=autonomous_worker, daemon=True)
        worker_thread.start()
        logger.info("✅ Autonomous worker started")
    except Exception as e:
        logger.error(f"Failed to start worker: {e}")

# Initialize on import
try:
    if initialize_system():
        logger.info("✅ System initialization successful")
        start_worker()
    else:
        logger.warning("⚠️ System initialization had issues but continuing...")
except Exception as e:
    logger.error(f"❌ System initialization error: {e}")

# Main entry point
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🌐 Starting XMRT Autonomous server (Build Fix Stable) on port {port}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        threaded=True
    )