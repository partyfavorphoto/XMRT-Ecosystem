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
import threading
from datetime import datetime, timedelta
import requests
import time
import random
import redis

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

app.config.from_object(Config)

# Global state for autonomous operations
autonomous_state = {
    'active_agents': {},
    'task_queue': [],
    'performance_metrics': {},
    'last_governance_check': None,
    'last_defi_optimization': None,
    'security_alerts': [],
    'community_events': []
}

class AIAgentManager:
    '''Manages AI agents and their autonomous operations'''
    
    def __init__(self):
        self.characters = {}
        self.active_character = None
        self.load_characters()
    
    def load_characters(self):
        '''Load AI character configurations'''
        try:
            # In production, this would load from the characters directory
            # For now, we'll use a simplified version
            self.characters = {
                'xmrt_dao_governor': {
                    'name': 'XMRT DAO Governor',
                    'specialization': 'governance',
                    'capabilities': ['proposal_analysis', 'voting_coordination', 'treasury_management']
                },
                'xmrt_defi_specialist': {
                    'name': 'XMRT DeFi Specialist', 
                    'specialization': 'defi',
                    'capabilities': ['yield_optimization', 'liquidity_management', 'risk_analysis']
                },
                'xmrt_community_manager': {
                    'name': 'XMRT Community Manager',
                    'specialization': 'community',
                    'capabilities': ['engagement_tracking', 'event_coordination', 'sentiment_analysis']
                },
                'xmrt_security_guardian': {
                    'name': 'XMRT Security Guardian',
                    'specialization': 'security', 
                    'capabilities': ['threat_detection', 'vulnerability_scanning', 'incident_response']
                }
            }
            self.active_character = self.characters.get(app.config['DEFAULT_CHARACTER'])
            logger.info(f"Loaded {len(self.characters)} AI characters")
        except Exception as e:
            logger.error(f"Error loading characters: {e}")
    
    def get_character_response(self, character_id, message, context=None):
        '''Generate AI response from specific character'''
        character = self.characters.get(character_id)
        if not character:
            return "Character not found"
        
        # Simplified AI response - in production this would use Eliza framework
        responses = {
            'xmrt_dao_governor': f"As the DAO Governor, I analyze that: {message}. Current governance status is optimal.",
            'xmrt_defi_specialist': f"DeFi analysis shows: {message}. Yield optimization opportunities detected.",
            'xmrt_community_manager': f"Community insight: {message}. Engagement metrics are positive!",
            'xmrt_security_guardian': f"Security assessment: {message}. No threats detected in current analysis."
        }
        
        return responses.get(character_id, "Processing your request...")
    
    def coordinate_agents(self, task_type):
        '''Coordinate multiple agents for complex tasks'''
        relevant_agents = []
        
        if task_type == 'governance':
            relevant_agents = ['xmrt_dao_governor', 'xmrt_security_guardian']
        elif task_type == 'defi':
            relevant_agents = ['xmrt_defi_specialist', 'xmrt_security_guardian']
        elif task_type == 'community':
            relevant_agents = ['xmrt_community_manager', 'xmrt_dao_governor']
        
        return relevant_agents

class AutonomousOperations:
    '''Handles autonomous ecosystem operations'''
    
    def __init__(self, agent_manager):
        self.agent_manager = agent_manager
        self.running = False
    
    def start_autonomous_operations(self):
        '''Start autonomous operation threads'''
        if self.running:
            return
        
        self.running = True
        
        # Start autonomous operation threads
        if app.config['AUTO_GOVERNANCE_ENABLED']:
            threading.Thread(target=self.governance_monitor, daemon=True).start()
        
        if app.config['AUTO_DEFI_ENABLED']:
            threading.Thread(target=self.defi_optimizer, daemon=True).start()
        
        if app.config['AUTO_SECURITY_MONITORING']:
            threading.Thread(target=self.security_monitor, daemon=True).start()
        
        if app.config['AUTO_COMMUNITY_MANAGEMENT']:
            threading.Thread(target=self.community_manager, daemon=True).start()
        
        logger.info("Autonomous operations started")
    
    def governance_monitor(self):
        '''Monitor and manage DAO governance autonomously'''
        while self.running:
            try:
                # Check for new proposals
                proposals = self.check_governance_proposals()
                
                for proposal in proposals:
                    # Analyze proposal with DAO Governor
                    analysis = self.agent_manager.get_character_response(
                        'xmrt_dao_governor', 
                        f"Analyze proposal: {proposal.get('description', '')}"
                    )
                    
                    # Log governance activity
                    autonomous_state['last_governance_check'] = datetime.now()
                    logger.info(f"Governance analysis: {analysis}")
                
                time.sleep(300)  # Check every 5 minutes
            except Exception as e:
                logger.error(f"Governance monitor error: {e}")
                time.sleep(60)
    
    def defi_optimizer(self):
        '''Optimize DeFi operations autonomously'''
        while self.running:
            try:
                # Check yield opportunities
                yield_data = self.check_yield_opportunities()
                
                if yield_data:
                    # Analyze with DeFi Specialist
                    optimization = self.agent_manager.get_character_response(
                        'xmrt_defi_specialist',
                        f"Optimize yields: {yield_data}"
                    )
                    
                    autonomous_state['last_defi_optimization'] = datetime.now()
                    logger.info(f"DeFi optimization: {optimization}")
                
                time.sleep(600)  # Check every 10 minutes
            except Exception as e:
                logger.error(f"DeFi optimizer error: {e}")
                time.sleep(120)
    
    def security_monitor(self):
        '''Monitor security threats autonomously'''
        while self.running:
            try:
                # Check for security threats
                threats = self.scan_security_threats()
                
                if threats:
                    # Analyze with Security Guardian
                    security_response = self.agent_manager.get_character_response(
                        'xmrt_security_guardian',
                        f"Security threats detected: {threats}"
                    )
                    
                    autonomous_state['security_alerts'].append({
                        'timestamp': datetime.now(),
                        'threats': threats,
                        'response': security_response
                    })
                    
                    logger.warning(f"Security alert: {security_response}")
                
                time.sleep(180)  # Check every 3 minutes
            except Exception as e:
                logger.error(f"Security monitor error: {e}")
                time.sleep(60)
    
    def community_manager(self):
        '''Manage community engagement autonomously'''
        while self.running:
            try:
                # Check community metrics
                metrics = self.check_community_metrics()
                
                if metrics:
                    # Analyze with Community Manager
                    engagement_strategy = self.agent_manager.get_character_response(
                        'xmrt_community_manager',
                        f"Community metrics: {metrics}"
                    )
                    
                    autonomous_state['community_events'].append({
                        'timestamp': datetime.now(),
                        'metrics': metrics,
                        'strategy': engagement_strategy
                    })
                    
                    logger.info(f"Community management: {engagement_strategy}")
                
                time.sleep(900)  # Check every 15 minutes
            except Exception as e:
                logger.error(f"Community manager error: {e}")
                time.sleep(180)
    
    def check_governance_proposals(self):
        '''Check for new governance proposals'''
        # Placeholder - would integrate with actual DAO contracts
        return [{'id': 1, 'description': 'Treasury allocation proposal', 'status': 'active'}]
    
    def check_yield_opportunities(self):
        '''Check for DeFi yield opportunities'''
        # Placeholder - would integrate with DeFi protocols
        return {'current_apy': 12.5, 'opportunities': ['Curve', 'Uniswap']}
    
    def scan_security_threats(self):
        '''Scan for security threats'''
        # Placeholder - would integrate with security monitoring tools
        return []
    
    def check_community_metrics(self):
        '''Check community engagement metrics'''
        # Placeholder - would integrate with social platforms
        return {'active_users': 1247, 'engagement_rate': 68, 'sentiment': 'positive'}

# Initialize AI Agent Manager and Autonomous Operations
agent_manager = AIAgentManager()
autonomous_ops = AutonomousOperations(agent_manager)

# Routes
@app.route('/')
def home():
    '''Enhanced home page with autonomous status'''
    html_template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>XMRT Ecosystem - Autonomous AI Service</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
            .header { text-align: center; margin-bottom: 30px; }
            .status-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0; }
            .status-card { background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #007bff; }
            .agent-list { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }
            .agent-card { background: #e9ecef; padding: 15px; border-radius: 6px; text-align: center; }
            .metrics { background: #d4edda; padding: 15px; border-radius: 6px; margin: 10px 0; }
            .api-section { background: #fff3cd; padding: 20px; border-radius: 8px; margin: 20px 0; }
            h1 { color: #333; }
            h2 { color: #666; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
            .status-active { color: #28a745; font-weight: bold; }
            .status-inactive { color: #dc3545; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 XMRT Ecosystem - Autonomous AI Service</h1>
                <p>Advanced AI-powered DAO management with multi-agent coordination</p>
            </div>
            
            <h2>🎯 Autonomous Operations Status</h2>
            <div class="status-grid">
                <div class="status-card">
                    <h3>🗳️ DAO Governance</h3>
                    <p class="status-active">ACTIVE</p>
                    <p>Last check: {{ governance_status }}</p>
                </div>
                <div class="status-card">
                    <h3>💰 DeFi Operations</h3>
                    <p class="status-active">ACTIVE</p>
                    <p>Last optimization: {{ defi_status }}</p>
                </div>
                <div class="status-card">
                    <h3>🛡️ Security Monitoring</h3>
                    <p class="status-active">ACTIVE</p>
                    <p>Alerts: {{ security_alerts }}</p>
                </div>
                <div class="status-card">
                    <h3>👥 Community Management</h3>
                    <p class="status-active">ACTIVE</p>
                    <p>Events: {{ community_events }}</p>
                </div>
            </div>
            
            <h2>🤖 AI Agents</h2>
            <div class="agent-list">
                {% for agent_id, agent in agents.items() %}
                <div class="agent-card">
                    <h4>{{ agent.name }}</h4>
                    <p>{{ agent.specialization }}</p>
                    <p><small>{{ agent.capabilities|length }} capabilities</small></p>
                </div>
                {% endfor %}
            </div>
            
            <div class="metrics">
                <h3>📊 System Metrics</h3>
                <p><strong>Active Agents:</strong> {{ agents|length }}</p>
                <p><strong>Tasks in Queue:</strong> {{ task_queue_length }}</p>
                <p><strong>Uptime:</strong> {{ uptime }}</p>
                <p><strong>Last Update:</strong> {{ last_update }}</p>
            </div>
            
            <div class="api-section">
                <h2>🔌 API Endpoints</h2>
                <ul>
                    <li><strong>GET /api/status</strong> - System status and metrics</li>
                    <li><strong>POST /api/chat</strong> - Chat with AI agents</li>
                    <li><strong>GET /api/agents</strong> - List available agents</li>
                    <li><strong>POST /api/governance</strong> - DAO governance operations</li>
                    <li><strong>POST /api/defi</strong> - DeFi operations and analysis</li>
                    <li><strong>GET /api/security</strong> - Security status and alerts</li>
                    <li><strong>GET /api/community</strong> - Community metrics and events</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    '''
    
    return render_template_string(html_template,
        agents=agent_manager.characters,
        governance_status=autonomous_state.get('last_governance_check', 'Never'),
        defi_status=autonomous_state.get('last_defi_optimization', 'Never'),
        security_alerts=len(autonomous_state.get('security_alerts', [])),
        community_events=len(autonomous_state.get('community_events', [])),
        task_queue_length=len(autonomous_state.get('task_queue', [])),
        uptime='Active',
        last_update=datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
    )

@app.route('/api/status')
def api_status():
    '''Get system status and metrics'''
    return jsonify({
        'status': 'active',
        'autonomous_operations': {
            'governance': app.config['AUTO_GOVERNANCE_ENABLED'],
            'defi': app.config['AUTO_DEFI_ENABLED'],
            'security': app.config['AUTO_SECURITY_MONITORING'],
            'community': app.config['AUTO_COMMUNITY_MANAGEMENT']
        },
        'agents': {
            'total': len(agent_manager.characters),
            'active': len([a for a in agent_manager.characters.values()]),
            'characters': list(agent_manager.characters.keys())
        },
        'metrics': autonomous_state,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/chat', methods=['POST'])
def api_chat():
    '''Chat with AI agents'''
    data = request.get_json()
    message = data.get('message', '')
    character_id = data.get('character', app.config['DEFAULT_CHARACTER'])
    
    if not message:
        return jsonify({'error': 'Message is required'}), 400
    
    response = agent_manager.get_character_response(character_id, message)
    
    return jsonify({
        'character': character_id,
        'message': message,
        'response': response,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/agents')
def api_agents():
    '''List available AI agents'''
    return jsonify({
        'agents': agent_manager.characters,
        'default': app.config['DEFAULT_CHARACTER'],
        'total': len(agent_manager.characters)
    })

@app.route('/api/governance', methods=['GET', 'POST'])
def api_governance():
    '''DAO governance operations'''
    if request.method == 'GET':
        return jsonify({
            'proposals': autonomous_ops.check_governance_proposals(),
            'last_check': autonomous_state.get('last_governance_check'),
            'auto_enabled': app.config['AUTO_GOVERNANCE_ENABLED']
        })
    
    # POST - trigger governance analysis
    data = request.get_json()
    proposal = data.get('proposal', '')
    
    analysis = agent_manager.get_character_response('xmrt_dao_governor', f"Analyze: {proposal}")
    
    return jsonify({
        'proposal': proposal,
        'analysis': analysis,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/defi', methods=['GET', 'POST'])
def api_defi():
    '''DeFi operations and analysis'''
    if request.method == 'GET':
        return jsonify({
            'opportunities': autonomous_ops.check_yield_opportunities(),
            'last_optimization': autonomous_state.get('last_defi_optimization'),
            'auto_enabled': app.config['AUTO_DEFI_ENABLED']
        })
    
    # POST - trigger DeFi analysis
    data = request.get_json()
    strategy = data.get('strategy', '')
    
    analysis = agent_manager.get_character_response('xmrt_defi_specialist', f"Analyze strategy: {strategy}")
    
    return jsonify({
        'strategy': strategy,
        'analysis': analysis,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/security')
def api_security():
    '''Security status and alerts'''
    return jsonify({
        'alerts': autonomous_state.get('security_alerts', []),
        'threats': autonomous_ops.scan_security_threats(),
        'auto_enabled': app.config['AUTO_SECURITY_MONITORING'],
        'last_scan': datetime.now().isoformat()
    })

@app.route('/api/community')
def api_community():
    '''Community metrics and events'''
    return jsonify({
        'metrics': autonomous_ops.check_community_metrics(),
        'events': autonomous_state.get('community_events', []),
        'auto_enabled': app.config['AUTO_COMMUNITY_MANAGEMENT'],
        'last_update': datetime.now().isoformat()
    })

@app.route('/api/coordinate', methods=['POST'])
def api_coordinate():
    '''Coordinate multiple agents for complex tasks'''
    data = request.get_json()
    task_type = data.get('task_type', '')
    task_description = data.get('description', '')
    
    relevant_agents = agent_manager.coordinate_agents(task_type)
    responses = {}
    
    for agent_id in relevant_agents:
        responses[agent_id] = agent_manager.get_character_response(agent_id, task_description)
    
    return jsonify({
        'task_type': task_type,
        'description': task_description,
        'coordinated_agents': relevant_agents,
        'responses': responses,
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    # Start autonomous operations
    autonomous_ops.start_autonomous_operations()
    
    # Run Flask app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)


# Redis configuration for chat history (optional, for persistence)
# r = redis.Redis(host=\'localhost\', port=6379, db=0)

chat_history = []

class ChatManager:
    def __init__(self):    def add_message(self, sender, message, agent_id=None):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        chat_entry = {
            'sender': sender,
            'message': message,
            'timestamp': timestamp
        }
        if agent_id:
            chat_entry['agent_id'] = agent_id
        chat_history.append(chat_entry)
        # Optional: Store in Redis for persistence
        # r.lpush('chat_messages', json.dumps(chat_entry))
        logger.info(f"Chat message added: {chat_entry}"):
        # Optional: Retrieve from Redis
        # return [json.loads(msg) for msg in r.lrange(\'chat_messages\', 0, -1)][::-1]
        return chat_history

chat_manager = ChatManager()




@app.route(\"/api/chat\", methods=[\"POST\"])
def api_chat():
    data = request.get_json()
    user_message = data.get(\"message\")
    character_id = data.get(\"character_id\")

    if not user_message:
        return jsonify({\"error\": \"Message is required\"}), 400

    chat_manager.add_message(\"User\", user_message)

    if character_id:
        ai_response = agent_manager.get_character_response(character_id, user_message)
        chat_manager.add_message(character_id, ai_response, agent_id=character_id)
    else:
        ai_response = \"Please specify a character_id to chat with a specific agent.\"
        chat_manager.add_message(\"System\", ai_response)

    return jsonify({\"user_message\": user_message, \"ai_response\": ai_response})

@app.route(\"/api/chat/history\")
def api_chat_history():
    return jsonify({\"chat_history\": chat_manager.get_history()})

@app.route(\"/\")
def home():
    html_template = \"\"\"\
    <!DOCTYPE html>
    <html>
    <head>
        <title>XMRT Ecosystem - Autonomous AI Service</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
            .header { text-align: center; margin-bottom: 30px; }
            .status-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0; }
            .status-card { background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #007bff; }
            .agent-list { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }
            .agent-card { background: #e9ecef; padding: 15px; border-radius: 6px; text-align: center; }
            .metrics { background: #d4edda; padding: 15px; border-radius: 6px; margin: 10px 0; }
            .api-section { background: #fff3cd; padding: 20px; border-radius: 8px; margin: 20px 0; }
            h1 { color: #333; }
            h2 { color: #666; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
            .status-active { color: #28a745; font-weight: bold; }
            .status-inactive { color: #dc3545; font-weight: bold; }
            .chat-container { margin-top: 30px; border-top: 1px solid #eee; padding-top: 20px; }
            .chat-box { border: 1px solid #ccc; height: 300px; overflow-y: scroll; padding: 10px; background: #fff; margin-bottom: 10px; }
            .chat-input { display: flex; }
            .chat-input input { flex-grow: 1; padding: 10px; border: 1px solid #ccc; border-radius: 5px 0 0 5px; }
            .chat-input button { padding: 10px 15px; background: #007bff; color: white; border: none; border-radius: 0 5px 5px 0; cursor: pointer; }
            .chat-message { margin-bottom: 8px; }
            .chat-message.user { text-align: right; color: #007bff; }
            .chat-message.agent { text-align: left; color: #28a745; }
            .chat-message .timestamp { font-size: 0.7em; color: #999; }
        </style>
    </head>
    <body>
        <div class=\"container\">
            <div class=\"header\">
                <h1>🤖 XMRT Ecosystem - Autonomous AI Service</h1>
                <p>Advanced AI-powered DAO management with multi-agent coordination</p>
            </div>
            
            <h2>🎯 Autonomous Operations Status</h2>
            <div class=\"status-grid\">
                <div class=\"status-card\">
                    <h3>🗳️ DAO Governance</h3>
                    <p class=\"status-active\">ACTIVE</p>
                    <p>Last check: {{ governance_status }}</p>
                </div>
                <div class=\"status-card\">
                    <h3>💰 DeFi Operations</h3>
                    <p class=\"status-active\">ACTIVE</p>
                    <p>Last optimization: {{ defi_status }}</p>
                </div>
                <div class=\"status-card\">
                    <h3>🛡️ Security Monitoring</h3>
                    <p class=\"status-active\">ACTIVE</p>
                    <p>Alerts: {{ security_alerts }}</p>
                </div>
                <div class=\"status-card\">
                    <h3>👥 Community Management</h3>
                    <p class=\"status-active\">ACTIVE</p>
                    <p>Events: {{ community_events }}</p>
                </div>
            </div>
            
            <h2>🤖 AI Agents</h2>
            <div class=\"agent-list\">
                {% for agent_id, agent in agents.items() %}
                <div class=\"agent-card\">
                    <h4>{{ agent.name }}</h4>
                    <p>{{ agent.specialization }}</p>
                    <p><small>{{ agent.capabilities|length }} capabilities</small></p>
                </div>
                {% endfor %}
            </div>
            
            <div class=\"metrics\">
                <h3>📊 System Metrics</h3>
                <p><strong>Active Agents:</strong> {{ agents|length }}</p>
                <p><strong>Tasks in Queue:</strong> {{ task_queue_length }}</p>
                <p><strong>Uptime:</strong> {{ uptime }}</p>
                <p><strong>Last Update:</strong> {{ last_update }}</p>
            </div>
            
            <div class=\"api-section\">
                <h2>🔌 API Endpoints</h2>
                <ul>
                    <li><strong>GET /api/status</strong> - System status and metrics</li>
                    <li><strong>POST /api/chat</strong> - Chat with AI agents</li>
                    <li><strong>GET /api/agents</strong> - List available agents</li>
                    <li><strong>POST /api/governance</strong> - DAO governance operations</li>
                    <li><strong>POST /api/defi</strong> - DeFi operations and analysis</li>
                    <li><strong>GET /api/security</strong> - Security status and alerts</li>
                    <li><strong>GET /api/community</strong> - Community metrics and events</li>
                </ul>
            </div>

            <div class=\"chat-container\">
                <h2>💬 Agent Chatroom</h2>
                <div class=\"chat-box\" id=\"chatBox\"></div>
                <div class=\"chat-input\">
                    <input type=\"text\" id=\"chatMessage\" placeholder=\"Type your message...\">
                    <button onclick=\"sendMessage()\">Send</button>
                </div>
                <select id=\"agentSelect\">
                    <option value=\"\">Select Agent (Optional)</option>
                    {% for agent_id, agent in agents.items() %}
                    <option value=\"{{ agent_id }}\">{{ agent.name }}</option>
                    {% endfor %}
                </select>
            </div>
        </div>
        <script>
            async function fetchChatHistory() {
                const response = await fetch(\"/api/chat/history\");
                const data = await response.json();
                const chatBox = document.getElementById(\"chatBox\");
                chatBox.innerHTML = \"\";
                data.chat_history.forEach(msg => {
                    const msgDiv = document.createElement(\"div\");
                    msgDiv.classList.add(\"chat-message\");
                    msgDiv.classList.add(msg.sender === \"User\" ? \"user\" : \"agent\");
                    msgDiv.innerHTML = `<strong>${msg.sender}:</strong> ${msg.message} <span class=\"timestamp\">(${msg.timestamp})</span>`;
                    chatBox.appendChild(msgDiv);
                });
                chatBox.scrollTop = chatBox.scrollHeight;
            }

            async function sendMessage() {
                const chatMessageInput = document.getElementById(\"chatMessage\");
                const agentSelect = document.getElementById(\"agentSelect\");
                const message = chatMessageInput.value;
                const character_id = agentSelect.value;

                if (!message) return;

                chatMessageInput.value = \"\";

                const response = await fetch(\"/api/chat\", {
                    method: \"POST\",
                    headers: {
                        \"Content-Type\": \"application/json\"
                    },
                    body: JSON.stringify({ message, character_id })
                });
                const data = await response.json();
                console.log(data);
                fetchChatHistory();
            }

            // Fetch history on page load and every few seconds
            fetchChatHistory();
            setInterval(fetchChatHistory, 3000);
        </script>
    </body>
    </html>
    \"\"\"
    
    return render_template_string(html_template,
        agents=agent_manager.characters,
        governance_status=autonomous_state.get(\'last_governance_check\', \'Never\'),
        defi_status=autonomous_state.get(\'last_defi_optimization\', \'Never\'),
        security_alerts=len(autonomous_state.get(\'security_alerts\', [])),
        community_events=len(autonomous_state.get(\'community_events\', [])),
        task_queue_length=len(autonomous_state.get(\'task_queue\', [])),
        uptime=\'Active\',
        last_update=datetime.now().strftime(\'%Y-%m-%d %H:%M:%S UTC\')
    )


