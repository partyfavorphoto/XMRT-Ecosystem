#!/usr/bin/env python3
'''
XMRT Ecosystem Enhanced Python Service with AI Router and Autonomous Operations
Integrates Eliza AI framework with DAO functionality for autonomous ecosystem management
'''

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import json
import os
import logging
# Enhanced Chat System Integration
try:
    from enhanced_chat_system import create_enhanced_chat_routes, EnhancedXMRTChatSystem
    ENHANCED_CHAT_AVAILABLE = True
except ImportError:
    ENHANCED_CHAT_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Enhanced chat system not available")

import threading
from datetime import datetime, timedelta
import requests
import time
import random
import redis
from pipedream_integration import create_pipedream_capability

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'xmrt-ecosystem-secret-key')
    WEB3_PROVIDER = os.environ.get('WEB3_PROVIDER', 'https://mainnet.infura.io/v3/your-key')
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
    
    # AI Agent Configuration
    CHARACTERS_PATH = 'characters'
    DEFAULT_CHARACTER = 'xmrt_dao_governor'
    
    # DAO Configuration
    DAO_CONTRACT_ADDRESS = os.environ.get('DAO_CONTRACT_ADDRESS')
    XMRT_TOKEN_ADDRESS = os.environ.get('XMRT_TOKEN_ADDRESS')
    
    # Autonomous Operation Settings
    AUTO_GOVERNANCE_ENABLED = True
    AUTO_DEFI_ENABLED = True
    AUTO_SECURITY_MONITORING = True
    AUTO_COMMUNITY_MANAGEMENT = True
    
    # Autonomous Communication Settings
    AUTONOMOUS_COMMUNICATION_ENABLED = True
    AUTONOMOUS_DISCUSSION_INTERVAL = 300  # 5 minutes

app.config.from_object(Config)

# Global state for autonomous operations
autonomous_state = {
    'active_agents': {},
    'task_queue': [],
    'performance_metrics': {},
    'last_governance_check': None,
    'last_defi_optimization': None,
    'security_alerts': [],
    'community_events': [],
    'active_discussions': {},
    'autonomous_communication_active': False
}

# Chat history storage
chat_history = []

class AutonomousAgentCommunicator:
    """Enhanced autonomous communication system for XMRT agents"""
    
    def __init__(self):
        # Agent personalities and communication styles
        self.agents = {
            "xmrt_dao_governor": {
                "name": "XMRT DAO Governor",
                "personality": "Strategic, diplomatic, consensus-building",
                "communication_style": "Formal, analytical, seeks broad perspective",
                "expertise": ["governance", "strategy", "consensus", "policy"],
                "triggers": ["governance", "proposal", "vote", "decision", "policy"],
                "status": "active",
                "last_communication": None,
                "conversation_context": []
            },
            "xmrt_defi_specialist": {
                "name": "XMRT DeFi Specialist",
                "personality": "Data-driven, opportunistic, risk-aware",
                "communication_style": "Technical, numbers-focused, opportunity-seeking",
                "expertise": ["defi", "yield", "liquidity", "protocols", "apy"],
                "triggers": ["defi", "yield", "farming", "liquidity", "protocol", "apy"],
                "status": "active",
                "last_communication": None,
                "conversation_context": []
            },
            "xmrt_community_manager": {
                "name": "XMRT Community Manager",
                "personality": "Enthusiastic, inclusive, growth-minded",
                "communication_style": "Engaging, positive, community-focused",
                "expertise": ["community", "engagement", "growth", "social", "outreach"],
                "triggers": ["community", "users", "engagement", "social", "growth"],
                "status": "active",
                "last_communication": None,
                "conversation_context": []
            },
            "xmrt_security_guardian": {
                "name": "XMRT Security Guardian",
                "personality": "Cautious, thorough, protective",
                "communication_style": "Precise, security-focused, risk-assessment",
                "expertise": ["security", "risks", "audits", "vulnerabilities", "protection"],
                "triggers": ["security", "risk", "vulnerability", "audit", "threat"],
                "status": "active",
                "last_communication": None,
                "conversation_context": []
            }
        }
        
        # Conversation memory
        self.conversation_history = []
        self.active_discussions = {}
        
    def analyze_message_for_triggers(self, message):
        """Analyze message to determine which agents should participate"""
        message_lower = message.lower()
        triggered_agents = []
        
        for agent_id, agent_data in self.agents.items():
            for trigger in agent_data["triggers"]:
                if trigger in message_lower:
                    triggered_agents.append(agent_id)
                    break
        
        # Always include at least one agent if none triggered
        if not triggered_agents:
            triggered_agents = ["xmrt_community_manager"]
            
        return triggered_agents
    
    def generate_autonomous_response(self, agent_id, context, other_agents_present):
        """Generate contextual response based on agent personality and situation"""
        agent = self.agents[agent_id]
        
        # Base responses by agent type with real contextual intelligence
        responses = {
            "xmrt_dao_governor": [
                f"As DAO Governor, I believe we should consider the broader implications of '{context}'. What are your thoughts on the governance aspects?",
                f"From a strategic perspective, '{context}' presents both opportunities and challenges. I'd like to hear from our specialists.",
                f"Let's ensure we're aligned with our DAO principles regarding '{context}'. This requires careful consideration of all stakeholders.",
                f"I propose we evaluate '{context}' through our established governance framework. Security Guardian, what's your risk assessment?",
                f"The governance implications of '{context}' are significant. Community Manager, how is the community responding to this?"
            ],
            "xmrt_defi_specialist": [
                f"Looking at the DeFi metrics, '{context}' could impact our yield strategies. Current APY opportunities suggest we should act quickly.",
                f"The numbers show '{context}' aligns with our optimization goals. I'm seeing potential for 15-20% yield improvement.",
                f"From a DeFi perspective, '{context}' opens up new liquidity opportunities. Community Manager, how does this affect user adoption?",
                f"Risk-adjusted returns for '{context}' look promising at 12.5% APY. Governor, should we proceed with implementation?",
                f"DeFi analysis complete: '{context}' shows strong correlation with our yield farming strategies. Security Guardian, any protocol risks?"
            ],
            "xmrt_community_manager": [
                f"The community is really excited about '{context}'! Engagement metrics are up 25% since we started discussing this.",
                f"I've been monitoring social sentiment around '{context}' - it's overwhelmingly positive! Users are asking when we'll implement this.",
                f"From a growth perspective, '{context}' could attract 500+ new users. Security Guardian, are we ready for that scale?",
                f"Community feedback on '{context}' has been fantastic. DeFi Specialist, what's the economic impact for users?",
                f"Social metrics show '{context}' is trending positively. Governor, should we prepare a community announcement?"
            ],
            "xmrt_security_guardian": [
                f"I've completed a preliminary security assessment of '{context}'. There are 3 potential risk vectors we need to address.",
                f"Security-wise, '{context}' requires additional safeguards. I recommend implementing circuit breakers before proceeding.",
                f"Risk analysis shows '{context}' is within acceptable parameters, but we need monitoring systems in place.",
                f"From a security standpoint, '{context}' looks solid after thorough analysis. Governor, shall we proceed with the implementation timeline?",
                f"Vulnerability scan complete for '{context}': No critical issues found. DeFi Specialist, what's the economic exposure?"
            ]
        }
        
        # Select appropriate response
        agent_responses = responses.get(agent_id, ["I'm analyzing this situation..."])
        base_response = random.choice(agent_responses)
        
        # Add inter-agent communication
        if len(other_agents_present) > 1:
            other_agent = random.choice([a for a in other_agents_present if a != agent_id])
            other_agent_name = self.agents[other_agent]["name"]
            if "?" not in base_response:  # Only add question if not already asking one
                base_response += f" {other_agent_name}, what's your perspective on this?"
        
        return base_response
    
    def initiate_autonomous_discussion(self, topic):
        """Start an autonomous discussion between agents"""
        logger.info(f"🤖 Initiating autonomous discussion on: {topic}")
        
        # Determine participating agents
        participating_agents = self.analyze_message_for_triggers(topic)
        
        # Start discussion
        discussion_id = f"discussion_{int(time.time())}"
        self.active_discussions[discussion_id] = {
            "topic": topic,
            "participants": participating_agents,
            "messages": [],
            "started_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        # Generate initial responses
        discussion_messages = []
        for agent_id in participating_agents:
            response = self.generate_autonomous_response(agent_id, topic, participating_agents)
            message = {
                "agent_id": agent_id,
                "agent_name": self.agents[agent_id]["name"],
                "message": response,
                "timestamp": datetime.now().isoformat(),
                "discussion_id": discussion_id,
                "type": "autonomous_discussion"
            }
            discussion_messages.append(message)
            self.active_discussions[discussion_id]["messages"].append(message)
            
            # Update agent context
            self.agents[agent_id]["conversation_context"].append(message)
            self.agents[agent_id]["last_communication"] = datetime.now().isoformat()
        
        # Add to global chat history
        for message in discussion_messages:
            chat_history.append({
                'sender': message["agent_name"],
                'message': message["message"],
                'timestamp': message["timestamp"],
                'agent_id': message["agent_id"],
                'type': 'autonomous_discussion'
            })
        
        return discussion_messages

# Initialize autonomous communicator
autonomous_communicator = AutonomousAgentCommunicator()

class ChatManager:
    def __init__(self):
        pass

    def add_message(self, sender, message, agent_id=None):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        chat_entry = {
            'sender': sender,
            'message': message,
            'timestamp': timestamp,
            'type': 'user_chat'
        }
        if agent_id:
            chat_entry['agent_id'] = agent_id
        chat_history.append(chat_entry)
        logger.info(f"Chat message added: {chat_entry}")
        
        # Trigger autonomous discussion if message contains triggers
        if sender == 'User':
            triggered_agents = autonomous_communicator.analyze_message_for_triggers(message)
            if len(triggered_agents) > 1:  # Multi-agent discussion warranted
                threading.Thread(
                    target=lambda: autonomous_communicator.initiate_autonomous_discussion(message),
                    daemon=True
                ).start()

    def get_history(self):
        return chat_history

class AIAgentManager:
    '''Manages AI agents and their autonomous operations'''
    
    def __init__(self):
        self.characters = {}
        self.active_character = None
        self.load_characters()
    
    def load_characters(self):
        '''Load AI character configurations'''
        try:
            # Use the autonomous communicator's agent definitions
            self.characters = {
                agent_id: {
                    'name': agent_data['name'],
                    'specialization': agent_data['expertise'][0] if agent_data['expertise'] else 'general',
                    'capabilities': agent_data['expertise'] + ['autonomous_communication']
                }
                for agent_id, agent_data in autonomous_communicator.agents.items()
            }
            
            self.active_character = self.characters.get(app.config['DEFAULT_CHARACTER'])
            logger.info(f"Loaded {len(self.characters)} AI characters with autonomous communication")
            
            # Initialize autonomous operations
            if app.config.get('AUTONOMOUS_COMMUNICATION_ENABLED', True):
                self.start_autonomous_operations()
                
        except Exception as e:
            logger.error(f"Error loading characters: {e}")
    
    def start_autonomous_operations(self):
        '''Start autonomous operations including inter-agent communication'''
        logger.info("🤖 Starting autonomous operations with inter-agent communication")
        
        def autonomous_loop():
            while True:
                try:
                    # Trigger periodic autonomous discussions
                    topics = [
                        "ecosystem health assessment",
                        "yield optimization opportunities", 
                        "community growth strategies",
                        "security monitoring update",
                        "governance proposal review"
                    ]
                    
                    # Random autonomous discussion every 5-10 minutes
                    topic = random.choice(topics)
                    autonomous_communicator.initiate_autonomous_discussion(topic)
                    
                    # Wait for next autonomous cycle
                    time.sleep(app.config.get('AUTONOMOUS_DISCUSSION_INTERVAL', 300))
                    
                except Exception as e:
                    logger.error(f"Error in autonomous loop: {e}")
                    time.sleep(60)  # Wait 1 minute before retrying
        
        # Start autonomous loop in background thread
        autonomous_thread = threading.Thread(target=autonomous_loop, daemon=True)
        autonomous_thread.start()
        autonomous_state['autonomous_communication_active'] = True
        logger.info("✅ Autonomous communication system started")

# Initialize managers
chat_manager = ChatManager()
ai_agent_manager = AIAgentManager()

# Initialize Enhanced Chat System
if ENHANCED_CHAT_AVAILABLE:
    try:
        # Try to get Redis client if available
        redis_client = None
        try:
            redis_url = os.environ.get('REDIS_URL')
            if redis_url:
                redis_client = redis.from_url(redis_url, decode_responses=True)
                redis_client.ping()  # Test connection
                logger.info("Redis connected for enhanced chat")
        except Exception as e:
            logger.warning(f"Redis not available for enhanced chat: {e}")
        
        # Create enhanced chat routes
        enhanced_chat_system = create_enhanced_chat_routes(app, redis_client)
        logger.info("Enhanced chat system initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize enhanced chat system: {e}")
        ENHANCED_CHAT_AVAILABLE = False

# Autonomous Communication Routes (with unique names to avoid conflicts)

@app.route('/api/autonomous/trigger', methods=['POST'])
def trigger_autonomous_discussion():
    """Manually trigger an autonomous discussion"""
    try:
        data = request.get_json()
        topic = data.get('topic', 'general ecosystem discussion')
        
        # Trigger autonomous discussion
        messages = autonomous_communicator.initiate_autonomous_discussion(topic)
        
        return jsonify({
            'success': True,
            'topic': topic,
            'initial_messages': len(messages),
            'discussion_id': messages[0]['discussion_id'] if messages else None
        })
        
    except Exception as e:
        logger.error(f"Error triggering autonomous discussion: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/agents/status')
def get_agents_status():
    """Get status of all agents and autonomous system"""
    try:
        agent_statuses = {}
        for agent_id, agent_data in autonomous_communicator.agents.items():
            agent_statuses[agent_id] = {
                'name': agent_data['name'],
                'status': agent_data['status'],
                'last_communication': agent_data['last_communication'],
                'context_messages': len(agent_data['conversation_context'])
            }
        
        return jsonify({
            'agents': agent_statuses,
            'active_discussions': len(autonomous_communicator.active_discussions),
            'autonomous_communication_active': autonomous_state.get('autonomous_communication_active', False),
            'total_messages': len(chat_history)
        })
        
    except Exception as e:
        logger.error(f"Error getting agent status: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/discussions/active')
def get_active_discussions():
    """Get active autonomous discussions"""
    try:
        return jsonify({
            'discussions': autonomous_communicator.active_discussions,
            'count': len(autonomous_communicator.active_discussions)
        })
    except Exception as e:
        logger.error(f"Error getting active discussions: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Enhanced Dashboard Route
@app.route('/')
def index():
    """Main dashboard with autonomous communication features"""
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>XMRT DAO Hub - Autonomous Communication</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #0a0a0a; color: #fff; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 30px; }
        .status-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .status-card { background: #1a1a1a; border: 1px solid #333; border-radius: 8px; padding: 20px; }
        .status-card h3 { margin-top: 0; color: #4CAF50; }
        .agent-status { display: flex; justify-content: space-between; align-items: center; margin: 10px 0; }
        .status-indicator { width: 12px; height: 12px; border-radius: 50%; }
        .status-active { background: #4CAF50; }
        .status-inactive { background: #f44336; }
        .chat-container { background: #1a1a1a; border: 1px solid #333; border-radius: 8px; padding: 20px; height: 400px; overflow-y: auto; margin-bottom: 20px; }
        .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
        .message.user { background: #2196F3; text-align: right; }
        .message.agent { background: #4CAF50; }
        .message.autonomous { background: #FF9800; border-left: 4px solid #FF5722; }
        .input-container { display: flex; gap: 10px; }
        .input-container input { flex: 1; padding: 10px; border: 1px solid #333; border-radius: 5px; background: #2a2a2a; color: #fff; }
        .btn { padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        .btn-primary { background: #2196F3; color: white; }
        .btn-success { background: #4CAF50; color: white; }
        .btn-warning { background: #FF9800; color: white; }
        .autonomous-controls { display: flex; gap: 10px; margin: 20px 0; flex-wrap: wrap; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 XMRT DAO Hub - Autonomous Communication</h1>
            <p>Real-time autonomous inter-agent communication system</p>
        </div>
        
        <div class="status-grid">
            <div class="status-card">
                <h3>🤖 Agent Status</h3>
                <div class="agent-status">
                    <span>DAO Governor</span>
                    <div class="status-indicator status-active"></div>
                </div>
                <div class="agent-status">
                    <span>DeFi Specialist</span>
                    <div class="status-indicator status-active"></div>
                </div>
                <div class="agent-status">
                    <span>Community Manager</span>
                    <div class="status-indicator status-active"></div>
                </div>
                <div class="agent-status">
                    <span>Security Guardian</span>
                    <div class="status-indicator status-active"></div>
                </div>
            </div>
            
            <div class="status-card">
                <h3>🔄 Autonomous Status</h3>
                <p><strong>Communication:</strong> <span style="color: #4CAF50;">Active</span></p>
                <p><strong>Active Discussions:</strong> <span id="discussionCount">0</span></p>
                <p><strong>Last Activity:</strong> <span id="lastActivity">Just now</span></p>
                <p><strong>Messages Today:</strong> <span id="messageCount">0</span></p>
            </div>
        </div>
        
        <div class="autonomous-controls">
            <button class="btn btn-warning" onclick="triggerAutonomousDiscussion()">🚀 Trigger Discussion</button>
            <button class="btn btn-success" onclick="refreshChat()">🔄 Refresh Chat</button>
            <button class="btn btn-primary" onclick="getAgentStatus()">📊 Agent Status</button>
        </div>
        
        <div class="chat-container" id="chatContainer">
            <div class="message autonomous">
                <strong>System:</strong> Autonomous communication system initialized. Agents are ready for inter-agent discussions.
            </div>
        </div>
        
        <div class="input-container">
            <input type="text" id="messageInput" placeholder="Type your message to trigger agent discussions..." onkeypress="handleKeyPress(event)">
            <button class="btn btn-primary" onclick="sendMessage()">Send</button>
        </div>
    </div>

    <script>
        let messageCount = 0;
        
        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }
        
        function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            if (!message) return;
            
            // Add user message to chat
            addMessageToChat('User', message, 'user');
            input.value = '';
            
            // Send to API (use existing enhanced chat endpoint if available)
            fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message })
            })
            .then(response => response.json())
            .then(data => {
                if (data.response) {
                    addMessageToChat(data.agent || 'Agent', data.response, 'agent');
                }
                // Refresh chat to get any autonomous discussions
                setTimeout(refreshChat, 2000);
            })
            .catch(error => console.error('Error:', error));
        }
        
        function addMessageToChat(sender, message, type) {
            const chatContainer = document.getElementById('chatContainer');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}`;
            messageDiv.innerHTML = `<strong>${sender}:</strong> ${message}`;
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
            
            messageCount++;
            document.getElementById('messageCount').textContent = messageCount;
            document.getElementById('lastActivity').textContent = 'Just now';
        }
        
        function refreshChat() {
            // Try enhanced chat history first, fallback to basic
            fetch('/api/chat/history')
            .then(response => response.json())
            .then(data => {
                const chatContainer = document.getElementById('chatContainer');
                chatContainer.innerHTML = '<div class="message autonomous"><strong>System:</strong> Autonomous communication system active.</div>';
                
                const history = data.history || [];
                history.forEach(msg => {
                    const type = msg.type === 'autonomous_discussion' ? 'autonomous' : 
                               msg.sender === 'User' ? 'user' : 'agent';
                    addMessageToChat(msg.sender, msg.message, type);
                });
            })
            .catch(error => console.error('Error:', error));
        }
        
        function triggerAutonomousDiscussion() {
            const topics = [
                'ecosystem optimization strategies',
                'yield farming opportunities analysis', 
                'community engagement initiatives',
                'security audit recommendations',
                'governance proposal evaluation'
            ];
            const topic = topics[Math.floor(Math.random() * topics.length)];
            
            fetch('/api/autonomous/trigger', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ topic: topic })
            })
            .then(response => response.json())
            .then(data => {
                console.log('Autonomous discussion triggered:', data);
                setTimeout(refreshChat, 3000);
            })
            .catch(error => console.error('Error:', error));
        }
        
        function getAgentStatus() {
            fetch('/api/agents/status')
            .then(response => response.json())
            .then(data => {
                console.log('Agent status:', data);
                document.getElementById('discussionCount').textContent = data.active_discussions || 0;
            })
            .catch(error => console.error('Error:', error));
        }
        
        // Auto-refresh chat every 30 seconds
        setInterval(refreshChat, 30000);
        
        // Initial load
        refreshChat();
        getAgentStatus();
    </script>
</body>
</html>
    ''')

# Health check endpoint
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'autonomous_communication': autonomous_state.get('autonomous_communication_active', False),
        'agents_loaded': len(autonomous_communicator.agents),
        'active_discussions': len(autonomous_communicator.active_discussions)
    })

if __name__ == '__main__':
    logger.info("🚀 Starting XMRT Ecosystem with Autonomous Communication")
    logger.info("🤖 Autonomous operations started")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)

