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

# Chat history storage
chat_history = []

class ChatManager:
    def __init__(self):
        pass

    def add_message(self, sender, message, agent_id=None):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        chat_entry = {
            'sender': sender,
            'message': message,
            'timestamp': timestamp
        }
        if agent_id:
            chat_entry['agent_id'] = agent_id
        chat_history.append(chat_entry)
        logger.info(f"Chat message added: {chat_entry}")

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
            # In production, this would load from the characters directory
            # For now, we'll use a simplified version
            self.characters = {
                'xmrt_dao_governor': {
                    'name': 'XMRT DAO Governor',
                    'specialization': 'governance',
                    'capabilities': ['proposal_analysis', 'voting_coordination', 'treasury_management', 'pipedream_connect']
                },
                'xmrt_defi_specialist': {
                    'name': 'XMRT DeFi Specialist', 
                    'specialization': 'defi',
                    'capabilities': ['yield_optimization', 'liquidity_management', 'risk_analysis', 'pipedream_connect']
                },
                'xmrt_community_manager': {
                    'name': 'XMRT Community Manager',
                    'specialization': 'community',
                    'capabilities': ['engagement_tracking', 'event_coordination', 'sentiment_analysis', 'pipedream_connect']
                },
                'xmrt_security_guardian': {
                    'name': 'XMRT Security Guardian',
                    'specialization': 'security', 
                    'capabilities': ['threat_detection', 'vulnerability_scanning', 'incident_response', 'pipedream_connect']
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
chat_manager = ChatManager()

# Routes
@app.route('/')
def home():
    '''Enhanced home page with autonomous status and chatroom'''
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
        .chat-container { margin-top: 30px; border-top: 1px solid #eee; padding-top: 20px; }
        .chat-box { border: 1px solid #ccc; height: 300px; overflow-y: scroll; padding: 10px; background: #fff; margin-bottom: 10px; }
        .chat-input { display: flex; margin-bottom: 10px; }
        .chat-input input { flex-grow: 1; padding: 10px; border: 1px solid #ccc; border-radius: 5px 0 0 5px; }
        .chat-input button { padding: 10px 15px; background: #007bff; color: white; border: none; border-radius: 0 5px 5px 0; cursor: pointer; }
        .chat-message { margin-bottom: 8px; }
        .chat-message.user { text-align: right; color: #007bff; }
        .chat-message.agent { text-align: left; color: #28a745; }
        .chat-message .timestamp { font-size: 0.7em; color: #999; }
        
        /* NEW: Affiliate System Styles */
        .affiliate-section { background: #e8f4fd; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #17a2b8; }
        .affiliate-stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 15px 0; }
        .affiliate-stat { background: white; padding: 15px; border-radius: 6px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .affiliate-stat .number { font-size: 1.8em; font-weight: bold; color: #17a2b8; }
        .affiliate-stat .label { font-size: 0.9em; color: #666; margin-top: 5px; }
        .referral-link { background: #f8f9fa; padding: 15px; border-radius: 6px; margin: 15px 0; border: 1px solid #dee2e6; }
        .referral-link input { width: 100%; padding: 10px; border: 1px solid #ced4da; border-radius: 4px; font-family: monospace; }
        .referral-actions { margin-top: 10px; }
        .referral-actions button { margin-right: 10px; padding: 8px 16px; background: #17a2b8; color: white; border: none; border-radius: 4px; cursor: pointer; }
        .referral-actions button:hover { background: #138496; }
        .affiliate-form { background: white; padding: 20px; border-radius: 6px; margin: 15px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: bold; color: #495057; }
        .form-group input, .form-group select { width: 100%; padding: 10px; border: 1px solid #ced4da; border-radius: 4px; }
        .form-group button { background: #28a745; color: white; padding: 12px 24px; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; }
        .form-group button:hover { background: #218838; }
        .alert { padding: 12px; border-radius: 4px; margin: 10px 0; }
        .alert-success { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; }
        .alert-error { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }
        .hidden { display: none; }
        .tab-container { margin: 20px 0; }
        .tab-buttons { display: flex; border-bottom: 1px solid #dee2e6; }
        .tab-button { padding: 12px 24px; background: none; border: none; cursor: pointer; border-bottom: 2px solid transparent; }
        .tab-button.active { border-bottom-color: #17a2b8; color: #17a2b8; font-weight: bold; }
        .tab-content { padding: 20px 0; }
        .recent-referrals { max-height: 200px; overflow-y: auto; }
        .referral-item { background: #f8f9fa; padding: 10px; border-radius: 4px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center; }
        .status-pending { color: #ffc107; font-weight: bold; }
        .status-converted { color: #28a745; font-weight: bold; }
        .status-cancelled { color: #dc3545; font-weight: bold; }
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
        
        <!-- NEW: Affiliate Marketing Section -->
        <div class="affiliate-section">
            <h2>🚀 Affiliate Program - Earn XMRT Tokens</h2>
            <p>Join our evangelist program and earn rewards for bringing new users to the XMRT ecosystem!</p>
            
            <div class="tab-container">
                <div class="tab-buttons">
                    <button class="tab-button active" onclick="showTab('join')">Join Program</button>
                    <button class="tab-button" onclick="showTab('dashboard')" id="dashboardTab" style="display: none;">My Dashboard</button>
                </div>
                
                <!-- Join Program Tab -->
                <div id="joinTab" class="tab-content">
                    <div class="affiliate-form">
                        <h3>Become an Evangelist</h3>
                        <form id="affiliateRegistrationForm">
                            <div class="form-group">
                                <label for="evangelistName">Name:</label>
                                <input type="text" id="evangelistName" name="name" placeholder="Enter your name" required>
                            </div>
                            <div class="form-group">
                                <label for="evangelistType">Type:</label>
                                <select id="evangelistType" name="type" required>
                                    <option value="">Select type</option>
                                    <option value="human">Human Evangelist</option>
                                    <option value="ai_agent">AI Agent</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="evangelistEmail">Email (optional):</label>
                                <input type="email" id="evangelistEmail" name="email" placeholder="Enter your email">
                            </div>
                            <div class="form-group">
                                <label for="evangelistWallet">Wallet Address (optional):</label>
                                <input type="text" id="evangelistWallet" name="wallet" placeholder="Enter your wallet address">
                            </div>
                            <div class="form-group">
                                <button type="submit">Join Affiliate Program</button>
                            </div>
                        </form>
                    </div>
                </div>
                
                <!-- Dashboard Tab -->
                <div id="dashboardTab" class="tab-content hidden">
                    <div class="affiliate-stats">
                        <div class="affiliate-stat">
                            <div class="number" id="totalReferrals">0</div>
                            <div class="label">Total Referrals</div>
                        </div>
                        <div class="affiliate-stat">
                            <div class="number" id="totalConversions">0</div>
                            <div class="label">Conversions</div>
                        </div>
                        <div class="affiliate-stat">
                            <div class="number" id="conversionRate">0%</div>
                            <div class="label">Conversion Rate</div>
                        </div>
                        <div class="affiliate-stat">
                            <div class="number" id="totalEarnings">0</div>
                            <div class="label">XMRT Earned</div>
                        </div>
                    </div>
                    
                    <div class="referral-link">
                        <h4>Your Referral Link:</h4>
                        <input type="text" id="referralLinkInput" readonly>
                        <div class="referral-actions">
                            <button onclick="copyReferralLink()">Copy Link</button>
                            <button onclick="shareReferralLink()">Share</button>
                        </div>
                    </div>
                    
                    <div class="recent-referrals">
                        <h4>Recent Referrals:</h4>
                        <div id="recentReferralsList">
                            <p>Loading...</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <div id="affiliateAlerts"></div>
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
                <li><strong>GET /api/chat/history</strong> - Get chat history</li>
                <li><strong>GET /api/agents</strong> - List available agents</li>
                <li><strong>POST /api/governance</strong> - DAO governance operations</li>
                <li><strong>POST /api/defi</strong> - DeFi operations and analysis</li>
                <li><strong>GET /api/security</strong> - Security status and alerts</li>
                <li><strong>GET /api/community</strong> - Community metrics and events</li>
                <!-- NEW: Affiliate API endpoints -->
                <li><strong>POST /api/affiliate/register</strong> - Register as evangelist</li>
                <li><strong>GET /api/affiliate/dashboard/{id}</strong> - Get evangelist dashboard</li>
                <li><strong>POST /api/affiliate/track_referral</strong> - Track referral</li>
                <li><strong>GET /api/affiliate/stats</strong> - System affiliate stats</li>
            </ul>
        </div>

        <div class="chat-container">
            <h2>💬 Agent Chatroom</h2>
            <div class="chat-box" id="chatBox"></div>
            <div class="chat-input">
                <input type="text" id="chatMessage" placeholder="Type your message..." onkeypress="handleKeyPress(event)">
                <button onclick="sendMessage()">Send</button>
            </div>
            <select id="agentSelect">
                <option value="">Select Agent (Optional)</option>
                {% for agent_id, agent in agents.items() %}
                <option value="{{ agent_id }}">{{ agent.name }}</option>
                {% endfor %}
            </select>
        </div>
    </div>
    <script>
        // Existing chat functionality
        async function fetchChatHistory() {
            try {
                const response = await fetch("/api/chat/history");
                const data = await response.json();
                const chatBox = document.getElementById("chatBox");
                chatBox.innerHTML = "";
                data.chat_history.forEach(msg => {
                    const msgDiv = document.createElement("div");
                    msgDiv.classList.add("chat-message");
                    msgDiv.classList.add(msg.sender === "User" ? "user" : "agent");
                    msgDiv.innerHTML = `<strong>${msg.sender}:</strong> ${msg.message} <span class="timestamp">(${msg.timestamp})</span>`;
                    chatBox.appendChild(msgDiv);
                });
                chatBox.scrollTop = chatBox.scrollHeight;
            } catch (error) {
                console.error("Error fetching chat history:", error);
            }
        }

        async function sendMessage() {
            const chatMessageInput = document.getElementById("chatMessage");
            const agentSelect = document.getElementById("agentSelect");
            const message = chatMessageInput.value.trim();
            const character_id = agentSelect.value;

            if (!message) return;

            chatMessageInput.value = "";

            try {
                const response = await fetch("/api/chat", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ message, character_id })
                });
                const data = await response.json();
                console.log(data);
                fetchChatHistory();
            } catch (error) {
                console.error("Error sending message:", error);
            }
        }

        function handleKeyPress(event) {
            if (event.key === "Enter") {
                sendMessage();
            }
        }

        // NEW: Affiliate System JavaScript
        let currentEvangelistId = localStorage.getItem('evangelistId');
        
        // Check if user is already registered
        if (currentEvangelistId) {
            document.getElementById('dashboardTab').style.display = 'block';
            showTab('dashboard');
            loadAffiliateDashboard();
        }
        
        // Tab switching
        function showTab(tabName) {
            const tabs = ['join', 'dashboard'];
            tabs.forEach(tab => {
                const tabContent = document.getElementById(tab + 'Tab');
                const tabButton = document.querySelector(`[onclick="showTab('${tab}')"]`);
                if (tab === tabName) {
                    tabContent.classList.remove('hidden');
                    tabButton.classList.add('active');
                } else {
                    tabContent.classList.add('hidden');
                    tabButton.classList.remove('active');
                }
            });
        }
        
        // Affiliate registration
        document.getElementById('affiliateRegistrationForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(e.target);
            const data = {
                name: formData.get('name'),
                type: formData.get('type'),
                email: formData.get('email') || null,
                wallet_address: formData.get('wallet') || null
            };

            try {
                const response = await fetch('/api/affiliate/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                });

                const result = await response.json();

                if (response.ok) {
                    currentEvangelistId = result.evangelist_id;
                    localStorage.setItem('evangelistId', currentEvangelistId);
                    showAffiliateAlert('Registration successful! Welcome to the XMRT Affiliate Program!', 'success');
                    document.getElementById('dashboardTab').style.display = 'block';
                    showTab('dashboard');
                    loadAffiliateDashboard();
                } else {
                    showAffiliateAlert(result.error || 'Registration failed', 'error');
                }
            } catch (error) {
                showAffiliateAlert('Network error: ' + error.message, 'error');
            }
        });
        
        // Load affiliate dashboard
        async function loadAffiliateDashboard() {
            if (!currentEvangelistId) return;
            
            try {
                const response = await fetch(`/api/affiliate/dashboard/${currentEvangelistId}`);
                const data = await response.json();

                if (response.ok) {
                    updateAffiliateDashboard(data);
                } else {
                    showAffiliateAlert(data.error || 'Failed to load dashboard', 'error');
                    if (response.status === 404) {
                        localStorage.removeItem('evangelistId');
                        currentEvangelistId = null;
                        document.getElementById('dashboardTab').style.display = 'none';
                        showTab('join');
                    }
                }
            } catch (error) {
                showAffiliateAlert('Network error: ' + error.message, 'error');
            }
        }
        
        // Update dashboard with data
        function updateAffiliateDashboard(data) {
            const stats = data.stats;
            
            document.getElementById('totalReferrals').textContent = stats.total_referrals;
            document.getElementById('totalConversions').textContent = stats.total_conversions;
            document.getElementById('conversionRate').textContent = stats.conversion_rate.toFixed(1) + '%';
            document.getElementById('totalEarnings').textContent = stats.total_earnings.toFixed(2);
            
            document.getElementById('referralLinkInput').value = data.referral_link;
            
            const recentReferralsList = document.getElementById('recentReferralsList');
            if (data.recent_referrals && data.recent_referrals.length > 0) {
                recentReferralsList.innerHTML = data.recent_referrals.map(referral => `
                    <div class="referral-item">
                        <span>${new Date(referral.created_at).toLocaleDateString()}</span>
                        <span class="status-${referral.status}">${referral.status.toUpperCase()}</span>
                        <span>${referral.conversion_value} XMRT</span>
                    </div>
                `).join('');
            } else {
                recentReferralsList.innerHTML = '<p>No referrals yet. Start sharing your link!</p>';
            }
        }
        
        // Copy referral link
        function copyReferralLink() {
            const linkInput = document.getElementById('referralLinkInput');
            linkInput.select();
            document.execCommand('copy');
            showAffiliateAlert('Referral link copied to clipboard!', 'success');
        }
        
        // Share referral link
        function shareReferralLink() {
            const link = document.getElementById('referralLinkInput').value;
            
            if (navigator.share) {
                navigator.share({
                    title: 'Join XMRT Ecosystem',
                    text: 'Join the XMRT DAO ecosystem and earn rewards!',
                    url: link
                });
            } else {
                copyReferralLink();
            }
        }
        
        // Show affiliate alerts
        function showAffiliateAlert(message, type) {
            const alertsDiv = document.getElementById('affiliateAlerts');
            const alert = document.createElement('div');
            alert.className = `alert alert-${type}`;
            alert.textContent = message;
            
            alertsDiv.appendChild(alert);
            
            setTimeout(() => {
                alert.remove();
            }, 5000);
        }
        
        // Handle referral tracking on page load
        const urlParams = new URLSearchParams(window.location.search);
        const refCode = urlParams.get('ref');
        
        if (refCode && !localStorage.getItem('referralTracked')) {
            fetch('/api/affiliate/track_referral', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    referral_code: refCode,
                    metadata: {
                        page: window.location.pathname,
                        timestamp: new Date().toISOString()
                    }
                })
            }).then(response => {
                if (response.ok) {
                    localStorage.setItem('referralTracked', 'true');
                    localStorage.setItem('referralCode', refCode);
                    showAffiliateAlert('Welcome! You were referred by an XMRT evangelist.', 'success');
                }
            }).catch(error => {
                console.error('Failed to track referral:', error);
            });
        }
        
        // Auto-refresh dashboard every 30 seconds
        if (currentEvangelistId) {
            setInterval(() => {
                if (!document.getElementById('dashboardTab').classList.contains('hidden')) {
                    loadAffiliateDashboard();
                }
            }, 30000);
        }

        // Fetch history on page load and every few seconds
        fetchChatHistory();
        setInterval(fetchChatHistory, 3000);
    </script>
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

@app.route("/api/chat", methods=["POST"])
def api_chat():
    '''Chat with AI agents'''
    data = request.get_json()
    user_message = data.get("message")
    character_id = data.get("character_id")

    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    chat_manager.add_message("User", user_message)

    if character_id:
        ai_response = agent_manager.get_character_response(character_id, user_message)
        chat_manager.add_message(character_id, ai_response, agent_id=character_id)
    else:
        ai_response = "Please specify a character_id to chat with a specific agent."
        chat_manager.add_message("System", ai_response)

    return jsonify({"user_message": user_message, "ai_response": ai_response})

@app.route("/api/chat/history")
def api_chat_history():
    '''Get chat history'''
    return jsonify({"chat_history": chat_manager.get_history()})

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
        'agents': list(agent_manager.characters.keys()),
        'metrics': {
            'active_agents': len(agent_manager.characters),
            'task_queue_length': len(autonomous_state.get('task_queue', [])),
            'security_alerts': len(autonomous_state.get('security_alerts', [])),
            'community_events': len(autonomous_state.get('community_events', []))
        },
        'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
    })

@app.route('/api/agents')
def api_agents():
    '''List available AI agents'''
    return jsonify({
        'agents': agent_manager.characters,
        'active_character': app.config['DEFAULT_CHARACTER']
    })

# Start autonomous operations when the app starts
autonomous_ops.start_autonomous_operations()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

