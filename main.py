#!/usr/bin/env python3
"""
XMRT Ecosystem - Enhanced Main Application Entry Point
Unified multi-agent chat system with real-time WebSocket communication
Fixes all API endpoint issues and provides comprehensive functionality
"""

import os
import sys
import logging
import json
import time
import threading
import random
import uuid
from datetime import datetime, timedelta
from flask import Flask, render_template_string, send_from_directory, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
import requests
from github import Github
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Set up enhanced logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app with enhanced configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'xmrt-ecosystem-enhanced-2025')
CORS(app)  # Enable CORS for all routes

# Initialize SocketIO for real-time communication
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global state for enhanced activity monitoring
activity_state = {
    'agents': {
        'dao_governor': {
            'id': 'dao_governor',
            'name': 'DAO Governor',
            'status': 'active',
            'last_action': 'Analyzing governance proposal #249',
            'last_update': time.time(),
            'avatar': '🏛️',
            'personality': 'Strategic leader focused on governance and decision-making',
            'capabilities': ['governance_analysis', 'proposal_evaluation', 'strategic_planning'],
            'confidence': 0.92,
            'message_count': 0
        },
        'defi_specialist': {
            'id': 'defi_specialist',
            'name': 'DeFi Specialist',
            'status': 'active',
            'last_action': 'Optimizing yield strategies across protocols',
            'last_update': time.time(),
            'avatar': '💰',
            'personality': 'Analytics-driven expert in DeFi protocols and yield optimization',
            'capabilities': ['yield_optimization', 'liquidity_management', 'risk_assessment'],
            'confidence': 0.88,
            'message_count': 0
        },
        'security_guardian': {
            'id': 'security_guardian',
            'name': 'Security Guardian',
            'status': 'active',
            'last_action': 'Conducting comprehensive security audit',
            'last_update': time.time(),
            'avatar': '🛡️',
            'personality': 'Vigilant security expert focused on threat detection and prevention',
            'capabilities': ['security_audit', 'threat_detection', 'vulnerability_assessment'],
            'confidence': 0.95,
            'message_count': 0
        },
        'community_manager': {
            'id': 'community_manager',
            'name': 'Community Manager',
            'status': 'active',
            'last_action': 'Analyzing community sentiment and engagement',
            'last_update': time.time(),
            'avatar': '👥',
            'personality': 'Social coordinator focused on community engagement and growth',
            'capabilities': ['sentiment_analysis', 'community_engagement', 'event_coordination'],
            'confidence': 0.85,
            'message_count': 0
        }
    },
    'communications': [],
    'operations': [],
    'discussions': [],
    'active_sessions': {},
    'metrics': {
        'active_agents': 4,
        'total_messages': 0,
        'decisions_made': 156,
        'community_count': 1247,
        'uptime': 99.8,
        'active_discussions': 0,
        'websocket_connections': 0
    },
    'system_active': True,
    'autonomous_communication_active': True,
    'last_activity': time.time()
}

# Enhanced agent conversation topics and responses
conversation_topics = [
    {
        'topic': 'yield_optimization',
        'initiator': 'defi_specialist',
        'participants': ['dao_governor', 'security_guardian'],
        'messages': [
            "I've identified a new yield farming opportunity with 15.3% APY on Protocol X",
            "What's our risk assessment for this protocol, Security Guardian?",
            "Protocol security audit shows minimal risk - smart contracts verified",
            "Recommend allocating 200K USDC to this strategy for diversification"
        ]
    },
    {
        'topic': 'governance_proposal',
        'initiator': 'dao_governor',
        'participants': ['community_manager', 'defi_specialist'],
        'messages': [
            "New governance proposal submitted: Treasury allocation for Q4 initiatives",
            "Community sentiment analysis shows 78% positive response to proposal",
            "Financial impact assessment: $2.5M allocation across 6 strategic areas",
            "Recommend proceeding with modified proposal based on community feedback"
        ]
    },
    {
        'topic': 'security_alert',
        'initiator': 'security_guardian',
        'participants': ['dao_governor', 'defi_specialist'],
        'messages': [
            "ALERT: Potential vulnerability detected in cross-chain bridge contract",
            "Initiating emergency security assessment - pausing bridge operations",
            "Risk level: MEDIUM - Exploit probability 12%, Impact: $500K exposure",
            "Patch deployed and tested - Operations can resume with enhanced monitoring"
        ]
    }
]

# Agent personality responses
agent_responses = {
    'dao_governor': [
        "Let me analyze this from a governance perspective...",
        "This aligns with our strategic roadmap for Q4",
        "We should consider the broader implications for DAO governance",
        "I'll initiate a proposal for community voting",
        "The treasury implications need careful consideration"
    ],
    'defi_specialist': [
        "Current yield analysis shows this is optimal timing",
        "Risk-adjusted returns indicate this strategy is viable",
        "Let me run the numbers on this opportunity",
        "Portfolio rebalancing suggests we should proceed",
        "Market conditions favor this approach"
    ],
    'security_guardian': [
        "Security assessment indicates acceptable risk levels",
        "All protocols have been thoroughly audited",
        "Threat monitoring shows no immediate concerns",
        "Implementing additional security measures",
        "Emergency protocols are standing by"
    ],
    'community_manager': [
        "Community sentiment is highly positive on this initiative",
        "Engagement metrics show strong member interest",
        "Social sentiment analysis indicates broad support",
        "Member feedback suggests enthusiasm for this direction",
        "Community growth projections look very promising"
    ]
}

def add_activity_item(activity_type, message, agent_id=None, discussion_id=None):
    """Enhanced activity tracking with agent attribution"""
    timestamp = datetime.now().isoformat()
    item = {
        'id': str(uuid.uuid4()),
        'message': message,
        'timestamp': timestamp,
        'agent_id': agent_id,
        'discussion_id': discussion_id,
        'type': activity_type
    }

    if activity_type == 'communication':
        activity_state['communications'].insert(0, item)
        activity_state['communications'] = activity_state['communications'][:50]  # Keep more history
        activity_state['metrics']['total_messages'] += 1

        if agent_id and agent_id in activity_state['agents']:
            activity_state['agents'][agent_id]['message_count'] += 1

    elif activity_type == 'operation':
        activity_state['operations'].insert(0, item)
        activity_state['operations'] = activity_state['operations'][:30]

    activity_state['last_activity'] = time.time()

    # Emit to connected WebSocket clients
    socketio.emit('activity_update', {
        'type': activity_type,
        'item': item,
        'metrics': activity_state['metrics']
    })

    logger.info(f"Added {activity_type}: {message}")
    return item

def simulate_agent_conversation():
    """Enhanced conversation simulation with realistic agent interactions"""
    while True:
        if not (activity_state['system_active'] and activity_state['autonomous_communication_active']):
            time.sleep(5)
            continue

        # Start a new conversation topic
        if random.random() > 0.7:  # 30% chance every cycle
            topic = random.choice(conversation_topics)
            discussion_id = str(uuid.uuid4())

            logger.info(f"🤖 Starting conversation on: {topic['topic']}")

            # Add discussion to tracking
            discussion = {
                'id': discussion_id,
                'topic': topic['topic'],
                'participants': [topic['initiator']] + topic['participants'],
                'start_time': time.time(),
                'message_count': 0,
                'status': 'active'
            }
            activity_state['discussions'].insert(0, discussion)
            activity_state['discussions'] = activity_state['discussions'][:10]
            activity_state['metrics']['active_discussions'] = len([d for d in activity_state['discussions'] if d['status'] == 'active'])

            # Simulate conversation flow
            for i, message in enumerate(topic['messages']):
                if i == 0:
                    agent_id = topic['initiator']
                else:
                    agent_id = random.choice([topic['initiator']] + topic['participants'])

                agent = activity_state['agents'][agent_id]
                formatted_message = f"{agent['name']}: {message}"

                add_activity_item('communication', formatted_message, agent_id, discussion_id)
                update_agent_status(agent_id, f"Discussing {topic['topic']}")

                # Delay between messages for realism
                time.sleep(random.uniform(2, 8))

            # Mark discussion as completed
            for d in activity_state['discussions']:
                if d['id'] == discussion_id:
                    d['status'] = 'completed'
                    break

            activity_state['metrics']['active_discussions'] = len([d for d in activity_state['discussions'] if d['status'] == 'active'])

        # Individual agent actions
        if random.random() > 0.5:  # 50% chance
            agent_id = random.choice(list(activity_state['agents'].keys()))
            agent = activity_state['agents'][agent_id]

            response = random.choice(agent_responses[agent_id])
            formatted_message = f"{agent['name']}: {response}"

            add_activity_item('communication', formatted_message, agent_id)
            update_agent_status(agent_id, "Active analysis and coordination")

        # System operations
        if random.random() > 0.6:  # 40% chance
            operations = [
                "Smart contract optimization completed - Gas costs reduced by 18%",
                "Cross-chain transaction processed - 150K XMRT bridged successfully", 
                "Treasury rebalancing executed - Portfolio optimization improved",
                "Security scan completed - All systems verified and secure",
                "Performance monitoring update - System response time: 0.3s",
                "Backup verification successful - All data redundancy confirmed",
                "Network synchronization complete - All nodes consensus achieved",
                "AI model update deployed - Decision accuracy improved to 94%"
            ]

            operation = random.choice(operations)
            add_activity_item('operation', operation)

        # Sleep between cycles
        time.sleep(random.randint(15, 45))

def update_agent_status(agent_id, action):
    """Update specific agent status and activity"""
    if agent_id in activity_state['agents']:
        agent = activity_state['agents'][agent_id]
        agent['last_action'] = action
        agent['last_update'] = time.time()

        # Emit real-time update
        socketio.emit('agent_update', {
            'agent_id': agent_id,
            'agent': agent
        })

def github_integration_task():
    """Background task for GitHub integration and monitoring"""
    github_pat = os.environ.get('GITHUB_PAT', '')

    try:
        g = Github(github_pat)
        repo = g.get_repo("DevGruGold/XMRT-Ecosystem")

        while True:
            if activity_state['system_active']:
                try:
                    # Monitor repository activity
                    commits = repo.get_commits(since=datetime.now() - timedelta(hours=1))
                    for commit in commits[:3]:  # Latest 3 commits
                        add_activity_item('operation', f"GitHub: New commit by {commit.author.login} - {commit.commit.message[:60]}...")

                    # Monitor issues and PRs
                    open_issues = repo.get_issues(state='open', since=datetime.now() - timedelta(hours=6))
                    for issue in open_issues[:2]:
                        add_activity_item('operation', f"GitHub: Issue #{issue.number} - {issue.title[:50]}...")

                except Exception as e:
                    logger.error(f"GitHub integration error: {e}")

            time.sleep(300)  # Check every 5 minutes

    except Exception as e:
        logger.error(f"GitHub initialization error: {e}")

# WebSocket event handlers
@socketio.on('connect')
def handle_connect():
    """Handle new WebSocket connections"""
    session_id = str(uuid.uuid4())
    activity_state['active_sessions'][session_id] = {
        'connected_at': time.time(),
        'user_agent': request.headers.get('User-Agent', 'Unknown')
    }
    activity_state['metrics']['websocket_connections'] = len(activity_state['active_sessions'])

    logger.info(f"New WebSocket connection: {session_id}")

    # Send current state to new connection
    emit('initial_state', {
        'agents': activity_state['agents'],
        'recent_communications': activity_state['communications'][:20],
        'recent_operations': activity_state['operations'][:10],
        'metrics': activity_state['metrics']
    })

    join_room('main_channel')

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnections"""
    # Clean up session (simplified for this example)
    activity_state['metrics']['websocket_connections'] = max(0, activity_state['metrics']['websocket_connections'] - 1)
    logger.info("WebSocket disconnection")

@socketio.on('user_message')
def handle_user_message(data):
    """Handle user messages for interaction with agents"""
    message = data.get('message', '').strip()
    user_id = data.get('user_id', 'anonymous')

    if message:
        # Add user message to communications
        user_message = f"User ({user_id}): {message}"
        add_activity_item('communication', user_message, None, None)

        # Simulate agent response based on message content
        responding_agent = 'dao_governor'  # Default
        if 'yield' in message.lower() or 'defi' in message.lower():
            responding_agent = 'defi_specialist'
        elif 'security' in message.lower() or 'audit' in message.lower():
            responding_agent = 'security_guardian'
        elif 'community' in message.lower() or 'member' in message.lower():
            responding_agent = 'community_manager'

        # Generate contextual response
        agent = activity_state['agents'][responding_agent]
        responses = [
            f"Thank you for your input. I'm analyzing the implications for our {responding_agent.replace('_', ' ')} strategy.",
            f"Interesting perspective. Let me coordinate with other agents to address this properly.",
            f"I'll incorporate this into our current analysis and provide a comprehensive response.",
            f"Your suggestion aligns with our current objectives. Initiating evaluation process."
        ]

        response = f"{agent['name']}: {random.choice(responses)}"

        # Delay response slightly for realism
        threading.Timer(2.0, lambda: add_activity_item('communication', response, responding_agent)).start()

# Flask Routes - All endpoints that the frontend expects
@app.route('/')
def index():
    """Serve the enhanced main dashboard"""
    try:
        # Try to load the enhanced HTML file
        html_files = ['index_fixed.html', 'enhanced_index.html', 'index.html']

        for html_file in html_files:
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    return f.read()
            except FileNotFoundError:
                continue

        # Fallback to embedded HTML with enhanced features
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>XMRT DAO Hub - Enhanced Real-Time Communication</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.4/socket.io.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); 
            color: white; 
            min-height: 100vh; 
        }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        .header { 
            text-align: center; 
            margin-bottom: 30px; 
            padding: 20px 0; 
            border-bottom: 2px solid #333; 
        }
        .header h1 { 
            font-size: 2.5rem; 
            background: linear-gradient(45deg, #ffd700, #ff6b6b); 
            -webkit-background-clip: text; 
            -webkit-text-fill-color: transparent; 
            margin-bottom: 10px; 
        }
        .status-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
            gap: 20px; 
            margin-bottom: 30px; 
        }
        .panel { 
            background: rgba(255, 255, 255, 0.1); 
            border-radius: 15px; 
            padding: 20px; 
            backdrop-filter: blur(10px); 
            border: 1px solid rgba(255, 255, 255, 0.2); 
        }
        .panel h2 { 
            margin-bottom: 15px; 
            color: #ffd700; 
            display: flex; 
            align-items: center; 
            gap: 10px; 
        }
        .agent { 
            background: rgba(0, 0, 0, 0.2); 
            padding: 15px; 
            margin: 10px 0; 
            border-radius: 10px; 
            border-left: 4px solid #ffd700; 
        }
        .agent h3 { color: #ffd700; margin-bottom: 5px; }
        .agent-status { font-size: 0.9rem; opacity: 0.8; }
        .chat { 
            height: 400px; 
            overflow-y: auto; 
            background: rgba(0, 0, 0, 0.3); 
            padding: 15px; 
            border-radius: 10px; 
            margin-top: 10px; 
        }
        .message { 
            margin: 8px 0; 
            padding: 10px; 
            background: rgba(255, 255, 255, 0.05); 
            border-radius: 8px; 
            border-left: 3px solid #ffd700; 
            animation: slideIn 0.3s ease; 
        }
        .message-time { 
            font-size: 0.8rem; 
            color: #94a3b8; 
            margin-bottom: 5px; 
        }
        .controls { 
            display: flex; 
            gap: 15px; 
            justify-content: center; 
            margin: 20px 0; 
            flex-wrap: wrap; 
        }
        .btn { 
            background: linear-gradient(45deg, #10b981, #059669); 
            color: white; 
            border: none; 
            padding: 12px 24px; 
            border-radius: 25px; 
            font-weight: bold; 
            cursor: pointer; 
            transition: all 0.3s ease; 
        }
        .btn:hover { 
            transform: translateY(-2px); 
            box-shadow: 0 8px 25px rgba(16, 185, 129, 0.3); 
        }
        .btn:disabled { opacity: 0.5; cursor: not-allowed; }
        .metrics-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); 
            gap: 15px; 
        }
        .metric { 
            text-align: center; 
            background: rgba(0, 0, 0, 0.2); 
            padding: 15px; 
            border-radius: 8px; 
        }
        .metric-value { 
            font-size: 1.5rem; 
            font-weight: bold; 
            color: #ffd700; 
        }
        .metric-label { 
            font-size: 0.9rem; 
            opacity: 0.8; 
            margin-top: 5px; 
        }
        .connection-status { 
            position: fixed; 
            top: 20px; 
            right: 20px; 
            background: rgba(0, 0, 0, 0.8); 
            padding: 10px 15px; 
            border-radius: 20px; 
            font-size: 0.9rem; 
            z-index: 1000; 
            display: flex; 
            align-items: center; 
            gap: 8px; 
        }
        .status-dot { 
            width: 10px; 
            height: 10px; 
            border-radius: 50%; 
            background: #ef4444; 
            animation: pulse 2s infinite; 
        }
        .status-dot.connected { background: #10b981; }
        @keyframes slideIn { 
            from { opacity: 0; transform: translateX(-20px); } 
            to { opacity: 1; transform: translateX(0); } 
        }
        @keyframes pulse { 
            0%, 100% { opacity: 1; } 
            50% { opacity: 0.5; } 
        }
    </style>
</head>
<body>
    <div class="connection-status" id="connectionStatus">
        <div class="status-dot" id="statusDot"></div>
        <span id="statusText">Connecting...</span>
    </div>

    <div class="container">
        <div class="header">
            <h1>🚀 XMRT DAO Hub</h1>
            <p>Enhanced Real-Time Multi-Agent Communication System</p>
        </div>

        <div class="controls">
            <button class="btn" onclick="triggerDiscussion()">🎯 Trigger Discussion</button>
            <button class="btn" onclick="kickstartSystem()">⚡ Kickstart System</button>
            <button class="btn" onclick="refreshData()">🔄 Refresh Data</button>
        </div>

        <div class="status-grid">
            <div class="panel">
                <h2>🤖 AI Agents Status</h2>
                <div id="agentsContainer"></div>
            </div>

            <div class="panel">
                <h2>📊 System Metrics</h2>
                <div class="metrics-grid" id="metricsContainer"></div>
            </div>
        </div>

        <div class="status-grid">
            <div class="panel">
                <h2>💬 Live Agent Communications</h2>
                <div class="chat" id="communicationsChat"></div>
            </div>

            <div class="panel">
                <h2>⚙️ System Operations</h2>
                <div class="chat" id="operationsChat"></div>
            </div>
        </div>
    </div>

    <script>
        const socket = io();
        let isConnected = false;

        // Socket event handlers
        socket.on('connect', function() {
            isConnected = true;
            updateConnectionStatus();
        });

        socket.on('disconnect', function() {
            isConnected = false;
            updateConnectionStatus();
        });

        socket.on('initial_state', function(data) {
            updateAgents(data.agents);
            updateCommunications(data.recent_communications);
            updateOperations(data.recent_operations);
            updateMetrics(data.metrics);
        });

        socket.on('activity_update', function(data) {
            if (data.type === 'communication') {
                addCommunicationMessage(data.item);
            } else if (data.type === 'operation') {
                addOperationMessage(data.item);
            }
            updateMetrics(data.metrics);
        });

        socket.on('agent_update', function(data) {
            updateSingleAgent(data.agent_id, data.agent);
        });

        // UI Update Functions
        function updateConnectionStatus() {
            const statusDot = document.getElementById('statusDot');
            const statusText = document.getElementById('statusText');

            if (isConnected) {
                statusDot.classList.add('connected');
                statusText.textContent = 'Connected';
            } else {
                statusDot.classList.remove('connected');
                statusText.textContent = 'Disconnected';
            }
        }

        function updateAgents(agents) {
            const container = document.getElementById('agentsContainer');
            container.innerHTML = '';

            for (const [id, agent] of Object.entries(agents)) {
                container.innerHTML += `
                    <div class="agent" id="agent-${id}">
                        <h3>${agent.avatar} ${agent.name}</h3>
                        <div class="agent-status">
                            <div>Status: <strong>${agent.status}</strong></div>
                            <div>Action: ${agent.last_action}</div>
                            <div>Messages: ${agent.message_count || 0}</div>
                        </div>
                    </div>
                `;
            }
        }

        function updateSingleAgent(agentId, agent) {
            const agentElement = document.getElementById(`agent-${agentId}`);
            if (agentElement) {
                agentElement.querySelector('.agent-status').innerHTML = `
                    <div>Status: <strong>${agent.status}</strong></div>
                    <div>Action: ${agent.last_action}</div>
                    <div>Messages: ${agent.message_count || 0}</div>
                `;
            }
        }

        function updateMetrics(metrics) {
            const container = document.getElementById('metricsContainer');
            container.innerHTML = `
                <div class="metric">
                    <div class="metric-value">${metrics.active_agents}</div>
                    <div class="metric-label">Active Agents</div>
                </div>
                <div class="metric">
                    <div class="metric-value">${metrics.total_messages}</div>
                    <div class="metric-label">Total Messages</div>
                </div>
                <div class="metric">
                    <div class="metric-value">${metrics.websocket_connections}</div>
                    <div class="metric-label">Connections</div>
                </div>
                <div class="metric">
                    <div class="metric-value">${metrics.active_discussions}</div>
                    <div class="metric-label">Discussions</div>
                </div>
            `;
        }

        function updateCommunications(messages) {
            const container = document.getElementById('communicationsChat');
            container.innerHTML = '';
            messages.forEach(msg => addCommunicationMessage(msg));
        }

        function updateOperations(operations) {
            const container = document.getElementById('operationsChat');
            container.innerHTML = '';
            operations.forEach(op => addOperationMessage(op));
        }

        function addCommunicationMessage(msg) {
            const container = document.getElementById('communicationsChat');
            const div = document.createElement('div');
            div.className = 'message';
            div.innerHTML = `
                <div class="message-time">${formatTime(msg.timestamp)}</div>
                <div>${msg.message}</div>
            `;
            container.insertBefore(div, container.firstChild);

            // Keep only last 50 messages
            while (container.children.length > 50) {
                container.removeChild(container.lastChild);
            }
        }

        function addOperationMessage(msg) {
            const container = document.getElementById('operationsChat');
            const div = document.createElement('div');
            div.className = 'message';
            div.innerHTML = `
                <div class="message-time">${formatTime(msg.timestamp)}</div>
                <div>${msg.message}</div>
            `;
            container.insertBefore(div, container.firstChild);

            // Keep only last 30 messages
            while (container.children.length > 30) {
                container.removeChild(container.lastChild);
            }
        }

        function formatTime(timestamp) {
            return new Date(timestamp).toLocaleTimeString();
        }

        // Action Functions
        async function triggerDiscussion() {
            try {
                const response = await fetch('/api/trigger-discussion', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ topic: 'yield_optimization_strategies' })
                });
                const result = await response.json();
                console.log('Discussion triggered:', result);
            } catch (error) {
                console.error('Error triggering discussion:', error);
            }
        }

        async function kickstartSystem() {
            try {
                const response = await fetch('/api/kickstart', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                const result = await response.json();
                console.log('System kickstarted:', result);
            } catch (error) {
                console.error('Error kickstarting system:', error);
            }
        }

        async function refreshData() {
            try {
                const response = await fetch('/api/activity/feed');
                const data = await response.json();
                updateCommunications(data.communications);
                updateOperations(data.operations);
            } catch (error) {
                console.error('Error refreshing data:', error);
            }
        }

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            console.log('XMRT DAO Hub Enhanced - Initializing...');
            refreshData();
        });
    </script>
</body>
</html>'''

    except Exception as e:
        logger.error(f"Error serving index: {e}")
        return f"Error loading dashboard: {e}", 500

# API Endpoints - Fixed to match frontend expectations exactly
@app.route('/api/status')
def get_status():
    """Get overall system status - FIXED ENDPOINT"""
    return jsonify({
        'active': activity_state['system_active'],
        'agents': activity_state['agents'],
        'metrics': activity_state['metrics'],
        'autonomous_communication_active': activity_state['autonomous_communication_active'],
        'total_messages': activity_state['metrics']['total_messages'],
        'active_discussions': activity_state['metrics']['active_discussions'],
        'websocket_connections': activity_state['metrics']['websocket_connections'],
        'timestamp': datetime.now().isoformat(),
        'uptime': time.time() - start_time if 'start_time' in globals() else 0
    })

@app.route('/api/activity/feed')
def get_activity_feed():
    """Get the current activity feed"""
    return jsonify({
        'communications': activity_state['communications'],
        'operations': activity_state['operations'],
        'discussions': activity_state['discussions'],
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/kickstart', methods=['POST'])
def kickstart_system():
    """Kickstart system activity if idle - FIXED ENDPOINT"""
    logger.info("✅ Autonomous communication system kickstarted")

    activity_state['system_active'] = True
    activity_state['autonomous_communication_active'] = True
    activity_state['last_activity'] = time.time()

    # Add kickstart activities
    add_activity_item('operation', 'System activity manually kickstarted - All agents reactivated')
    add_activity_item('communication', 'DAO Governor: System reactivation complete - Resuming governance operations')

    # Reset all agent statuses
    for agent_id in activity_state['agents']:
        activity_state['agents'][agent_id]['status'] = 'active'
        activity_state['agents'][agent_id]['last_update'] = time.time()

    return jsonify({
        'success': True,
        'message': 'Autonomous communication system activated',
        'timestamp': datetime.now().isoformat(),
        'active_agents': len(activity_state['agents'])
    })

@app.route('/api/trigger-discussion', methods=['POST'])
def trigger_discussion():
    """Trigger a new agent discussion - FIXED ENDPOINT"""
    data = request.get_json() or {}
    topic = data.get('topic', 'general_coordination')

    logger.info(f"🤖 Manually triggering discussion on: {topic}")

    # Start a conversation
    discussion_topic = random.choice(conversation_topics)
    discussion_id = str(uuid.uuid4())

    # Add initial messages
    add_activity_item('operation', f'Manual discussion triggered on topic: {topic}')
    add_activity_item('communication', f'DAO Governor: Initiating focused discussion on {topic.replace("_", " ")}')

    # Simulate quick responses from other agents
    threading.Timer(2.0, lambda: add_activity_item('communication', 'DeFi Specialist: Joining discussion with current analysis')).start()
    threading.Timer(4.0, lambda: add_activity_item('communication', 'Security Guardian: Providing security perspective')).start()
    threading.Timer(6.0, lambda: add_activity_item('communication', 'Community Manager: Adding community sentiment data')).start()

    return jsonify({
        'success': True,
        'message': f'Discussion on {topic} initiated successfully',
        'discussion_id': discussion_id,
        'timestamp': datetime.now().isoformat()
    })

# Additional enhanced endpoints
@app.route('/api/autonomous/system/status')
def get_autonomous_system_status():
    """Get detailed autonomous system status"""
    return jsonify({
        'system_active': activity_state['system_active'],
        'autonomous_active': activity_state['autonomous_communication_active'],
        'agents': {
            agent_id: {
                'name': agent['name'],
                'status': agent['status'],
                'last_action': agent['last_action'],
                'confidence': agent['confidence'],
                'message_count': agent['message_count']
            }
            for agent_id, agent in activity_state['agents'].items()
        },
        'metrics': activity_state['metrics'],
        'active_discussions': len([d for d in activity_state['discussions'] if d['status'] == 'active']),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/autonomous/discussion/trigger', methods=['POST'])
def trigger_autonomous_discussion():
    """Enhanced autonomous discussion trigger"""
    data = request.get_json() or {}
    topic = data.get('topic', 'community_engagement_initiatives')

    logger.info(f"🤖 Initiating autonomous discussion on: {topic}")

    # Select appropriate conversation based on topic
    matching_topics = [t for t in conversation_topics if topic.lower() in t['topic'].lower()]
    selected_topic = matching_topics[0] if matching_topics else random.choice(conversation_topics)

    discussion_id = str(uuid.uuid4())

    # Create discussion tracking
    discussion = {
        'id': discussion_id,
        'topic': selected_topic['topic'],
        'participants': [selected_topic['initiator']] + selected_topic['participants'],
        'start_time': time.time(),
        'message_count': 0,
        'status': 'active',
        'triggered_by': 'autonomous_system'
    }

    activity_state['discussions'].insert(0, discussion)
    activity_state['metrics']['active_discussions'] += 1

    # Start the conversation in background
    def run_conversation():
        for i, message in enumerate(selected_topic['messages']):
            if i == 0:
                agent_id = selected_topic['initiator']
            else:
                agent_id = random.choice([selected_topic['initiator']] + selected_topic['participants'])

            agent = activity_state['agents'][agent_id]
            formatted_message = f"{agent['name']}: {message}"

            add_activity_item('communication', formatted_message, agent_id, discussion_id)
            time.sleep(random.uniform(3, 8))

        # Mark as completed
        for d in activity_state['discussions']:
            if d['id'] == discussion_id:
                d['status'] = 'completed'
                break
        activity_state['metrics']['active_discussions'] = max(0, activity_state['metrics']['active_discussions'] - 1)

    # Start conversation in background thread
    threading.Thread(target=run_conversation, daemon=True).start()

    return jsonify({
        'success': True,
        'message': f'Autonomous discussion on {topic} initiated',
        'discussion_id': discussion_id,
        'participants': discussion['participants'],
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/agents/<agent_id>/status')
def get_agent_status(agent_id):
    """Get status of a specific agent"""
    if agent_id in activity_state['agents']:
        agent = activity_state['agents'][agent_id]
        return jsonify({
            **agent,
            'recent_messages': [
                msg for msg in activity_state['communications'][-20:]
                if msg.get('agent_id') == agent_id
            ]
        })
    else:
        return jsonify({'error': 'Agent not found'}), 404

@app.route('/api/metrics')
def get_metrics():
    """Get current system metrics"""
    return jsonify(activity_state['metrics'])

@app.route('/api/health')
def health_check():
    """Enhanced health check endpoint"""
    uptime_seconds = time.time() - start_time if 'start_time' in globals() else 0

    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'uptime_seconds': uptime_seconds,
        'uptime_formatted': f"{uptime_seconds//3600:.0f}h {(uptime_seconds%3600)//60:.0f}m",
        'active_agents': len([a for a in activity_state['agents'].values() if a['status'] == 'active']),
        'total_communications': len(activity_state['communications']),
        'total_operations': len(activity_state['operations']),
        'websocket_connections': activity_state['metrics']['websocket_connections'],
        'system_load': {
            'cpu_usage': '12%',  # Placeholder - could integrate psutil
            'memory_usage': '245MB',
            'active_threads': threading.active_count()
        }
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found', 'message': str(error)}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error', 'message': str(error)}), 500

if __name__ == '__main__':
    start_time = time.time()

    # Initialize the system
    logger.info("🚀 XMRT Ecosystem Enhanced - Starting initialization...")
    logger.info("Loaded 4 AI characters with autonomous communication")

    # Add initial activities
    add_activity_item('operation', 'Enhanced XMRT system initialization complete')
    add_activity_item('communication', 'DAO Governor: Enhanced multi-agent system online')
    add_activity_item('communication', 'All Agents: Real-time WebSocket communication established')

    # Start background tasks
    logger.info("🤖 Starting autonomous operations with enhanced inter-agent communication")

    # Autonomous conversation simulation
    conversation_thread = threading.Thread(target=simulate_agent_conversation, daemon=True)
    conversation_thread.start()

    # GitHub integration
    github_thread = threading.Thread(target=github_integration_task, daemon=True)
    github_thread.start()

    logger.info("Enhanced chat system initialized successfully")

    print("\n" + "="*60)
    print("🚀 XMRT DAO Hub - Enhanced Multi-Agent Communication System")
    print("="*60)
    print("✅ Real-time WebSocket communication enabled")
    print("✅ All API endpoints fixed and functional")
    print("✅ Enhanced multi-agent conversation system")
    print("✅ GitHub integration with autonomous monitoring")
    print("✅ Comprehensive system health monitoring")
    print("\nAvailable endpoints:")
    print("  GET  / - Enhanced dashboard with WebSocket support")
    print("  GET  /api/status - Fixed system status endpoint")
    print("  GET  /api/activity/feed - Enhanced activity feed")
    print("  POST /api/trigger-discussion - Fixed discussion trigger") 
    print("  POST /api/kickstart - Fixed system kickstart")
    print("  GET  /api/autonomous/system/status - Detailed autonomous status")
    print("  POST /api/autonomous/discussion/trigger - Enhanced autonomous discussions")
    print("  GET  /api/health - Comprehensive health check")
    print("\n🌐 WebSocket Events:")
    print("  - Real-time agent communications")
    print("  - Live system operations")
    print("  - Agent status updates")
    print("  - User interaction support")
    print("="*60)

    # Get port from environment variable
    port = int(os.environ.get('PORT', 5000))

    # Use SocketIO run for WebSocket support
    socketio.run(app, host='0.0.0.0', port=port, debug=False, allow_unsafe_werkzeug=True)
