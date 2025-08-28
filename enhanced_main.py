#!/usr/bin/env python3
"""
XMRT Ecosystem - Enhanced Main Application with Multi-Agent Chat
Integrates the activity monitor API with real-time chat functionality
"""

import os
import sys
import logging
from flask import Flask, render_template_string, send_from_directory, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
import json
import time
import threading
import random
from datetime import datetime, timedelta
import requests

# Import the enhanced chat system
from chat_system import EnhancedChatSystem, AGENT_PERSONALITIES, CHAT_ROOMS

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'xmrt-ecosystem-secret-key')
CORS(app)  # Enable CORS for all routes

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Initialize enhanced chat system
chat_system = None

# Global state for activity monitoring (keeping existing functionality)
activity_state = {
    'agents': {
        'dao_governor': {'status': 'active', 'last_action': 'Analyzing proposal #247', 'last_update': time.time()},
        'defi_specialist': {'status': 'active', 'last_action': 'Optimizing yield strategy', 'last_update': time.time()},
        'security_guardian': {'status': 'active', 'last_action': 'Scanning for threats', 'last_update': time.time()},
        'community_manager': {'status': 'active', 'last_action': 'Analyzing sentiment', 'last_update': time.time()}
    },
    'communications': [],
    'operations': [],
    'metrics': {
        'active_agents': 4,
        'decisions_made': 156,
        'community_count': 1247,
        'uptime': 99.8
    },
    'system_active': True,
    'autonomous_communication_active': True,
    'total_messages': 0
}

# Enhanced agent actions for more realistic simulation
agent_actions = [
    "DAO Governor: Analyzing new governance proposal for treasury allocation",
    "DeFi Specialist: Optimizing yield farming strategy across multiple protocols", 
    "Security Guardian: Performing comprehensive security audit on smart contracts",
    "Community Manager: Processing community feedback and sentiment analysis",
    "DAO Governor → DeFi Specialist: Requesting detailed treasury analysis report",
    "Security Guardian: Threat assessment completed - All systems secure",
    "Community Manager: Sentiment analysis updated - Community engagement up 15%",
    "DeFi Specialist: Liquidity rebalancing executed - APY improved to 12.3%",
    "DAO Governor: Multi-signature transaction initiated for protocol upgrade",
    "Security Guardian: Vulnerability scan completed - Zero critical issues found",
    "Community Manager: Event coordination in progress - DAO meetup scheduled",
    "DeFi Specialist: Cross-chain bridge operation successful - 50K XMRT transferred",
    "DAO Governor: Proposal #248 passed with 89% approval rate",
    "Security Guardian: Emergency circuit breaker tested - Response time 0.3s",
    "Community Manager: New member onboarding - 25 new participants this week",
    "DeFi Specialist: Automated arbitrage opportunity detected - Profit: $2,340"
]

system_operations = [
    "Smart contract deployment successful - Gas optimized by 23%",
    "Cross-chain bridge operation completed - Transaction hash: 0x7f3a...", 
    "Treasury rebalancing executed - Portfolio diversification improved",
    "Automated backup completed - All data secured across 3 locations",
    "Performance optimization applied - Response time improved by 40%",
    "Security scan completed - All systems operational and secure",
    "Code improvement deployed - Bug fixes and feature enhancements live",
    "Network synchronization completed - All nodes in consensus",
    "Emergency circuit breaker tested - Failsafe mechanisms verified",
    "Multi-chain governance sync completed - Cross-chain voting enabled",
    "Zero-knowledge proof verification successful - Privacy maintained",
    "Automated incident response triggered - Issue resolved in 2.1 minutes",
    "Database optimization completed - Query performance improved 60%",
    "Load balancer configuration updated - Traffic distribution optimized",
    "API rate limiting adjusted - DDoS protection enhanced",
    "Monitoring alerts configured - Real-time threat detection active"
]

def add_activity_item(activity_type, message):
    """Add a new activity item to the appropriate feed"""
    timestamp = datetime.now().isoformat()
    item = {
        'message': message,
        'timestamp': timestamp,
        'id': int(time.time() * 1000)  # Unique ID
    }
    
    if activity_type == 'communication':
        activity_state['communications'].insert(0, item)
        # Keep only last 15 items
        activity_state['communications'] = activity_state['communications'][:15]
        activity_state['total_messages'] += 1
    elif activity_type == 'operation':
        activity_state['operations'].insert(0, item)
        # Keep only last 15 items
        activity_state['operations'] = activity_state['operations'][:15]
    
    logger.info(f"Added {activity_type}: {message}")

def simulate_activity():
    """Background thread to simulate enhanced agent activity"""
    logger.info("🤖 Starting autonomous operations with inter-agent communication")
    
    while True:
        if activity_state['system_active'] and activity_state['autonomous_communication_active']:
            # More frequent agent communications (70% chance)
            if random.random() > 0.3:
                action = random.choice(agent_actions)
                add_activity_item('communication', action)
            
            # System operations (40% chance)
            if random.random() > 0.6:
                operation = random.choice(system_operations)
                add_activity_item('operation', operation)
            
            # Update agent statuses more frequently
            if random.random() > 0.7:
                update_agent_statuses()
            
            # Update metrics occasionally
            if random.random() > 0.85:
                update_metrics()
        
        # Shorter sleep for more active simulation
        time.sleep(random.randint(8, 20))  # Random interval between 8-20 seconds

def update_agent_statuses():
    """Update agent statuses with more detailed activities"""
    activities = {
        'dao_governor': [
            'Analyzing governance proposal #249',
            'Coordinating multi-sig transaction',
            'Reviewing treasury allocation',
            'Processing community votes',
            'Evaluating protocol upgrade'
        ],
        'defi_specialist': [
            'Optimizing yield strategies',
            'Monitoring liquidity pools',
            'Executing arbitrage trades',
            'Rebalancing portfolio',
            'Analyzing market trends'
        ],
        'security_guardian': [
            'Scanning for vulnerabilities',
            'Monitoring threat landscape',
            'Auditing smart contracts',
            'Testing security protocols',
            'Analyzing transaction patterns'
        ],
        'community_manager': [
            'Analyzing community sentiment',
            'Coordinating events',
            'Processing member feedback',
            'Managing social channels',
            'Tracking engagement metrics'
        ]
    }
    
    for agent_id in activity_state['agents']:
        if random.random() > 0.6:  # 40% chance to update each agent
            agent = activity_state['agents'][agent_id]
            if agent_id in activities:
                agent['last_action'] = random.choice(activities[agent_id])
                agent['last_update'] = time.time()

def update_metrics():
    """Update system metrics with more realistic changes"""
    metrics = activity_state['metrics']
    
    # Gradually increase community count
    if random.random() > 0.7:
        metrics['community_count'] += random.randint(1, 8)
    
    # Increment decisions made
    if random.random() > 0.8:
        metrics['decisions_made'] += random.randint(1, 3)
    
    # Slight uptime variations
    if random.random() > 0.95:
        metrics['uptime'] = max(98.0, min(99.9, metrics['uptime'] + random.uniform(-0.1, 0.1)))

def check_external_service():
    """Check if the external XMRT service is active"""
    try:
        response = requests.get('https://xmrtnet-eliza.onrender.com/', timeout=5)
        return response.status_code == 200
    except:
        return False

# Serve the main HTML file
@app.route('/')
def index():
    """Serve the main dashboard"""
    try:
        with open('enhanced_index.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        return html_content
    except FileNotFoundError:
        # Fallback to existing file
        try:
            with open('index_fixed.html', 'r', encoding='utf-8') as f:
                html_content = f.read()
            return html_content
        except FileNotFoundError:
            # Final fallback
            return """
            <!DOCTYPE html>
            <html>
            <head>
                <title>XMRT DAO Hub - Loading...</title>
                <style>
                    body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                    .loading { color: #666; }
                </style>
            </head>
            <body>
                <h1>XMRT DAO Hub</h1>
                <p class="loading">Loading enhanced dashboard...</p>
                <script>
                    setTimeout(() => {
                        window.location.reload();
                    }, 3000);
                </script>
            </body>
            </html>
            """

# Existing API endpoints (keeping compatibility)
@app.route('/api/status')
def get_status():
    """Get overall system status"""
    external_active = check_external_service()
    
    return {
        'active': activity_state['system_active'],
        'external_service_active': external_active,
        'agents': activity_state['agents'],
        'metrics': activity_state['metrics'],
        'autonomous_communication_active': activity_state['autonomous_communication_active'],
        'total_messages': activity_state['total_messages'],
        'active_discussions': len([c for c in activity_state['communications'] if 'discussion' in c['message'].lower()]),
        'timestamp': datetime.now().isoformat()
    }

@app.route('/api/activity/feed')
def get_activity_feed():
    """Get the current activity feed"""
    return {
        'communications': activity_state['communications'],
        'operations': activity_state['operations'],
        'timestamp': datetime.now().isoformat()
    }

@app.route('/api/autonomous/system/status')
def get_autonomous_status():
    """Get autonomous system status"""
    return {
        'active': activity_state['autonomous_communication_active'],
        'agents': activity_state['agents'],
        'total_messages': activity_state['total_messages'],
        'chat_rooms': len(CHAT_ROOMS),
        'timestamp': datetime.now().isoformat()
    }

@app.route('/api/autonomous/discussion/trigger', methods=['POST'])
def trigger_autonomous_discussion():
    """Trigger autonomous discussion (enhanced version)"""
    data = request.get_json() or {}
    topic = data.get('topic', 'general coordination')
    room_id = data.get('room', 'general')
    
    logger.info(f"🤖 Initiating autonomous discussion on: {topic}")
    
    # Use enhanced chat system if available
    if chat_system and room_id in CHAT_ROOMS:
        success = chat_system.trigger_agent_discussion(room_id, topic)
        if success:
            add_activity_item('communication', f'Enhanced multi-agent discussion initiated: {topic}')
            return {
                'success': True,
                'message': f'Enhanced discussion on {topic} initiated in {room_id}',
                'timestamp': datetime.now().isoformat()
            }
    
    # Fallback to original behavior
    add_activity_item('communication', f'DAO Governor: Initiating discussion on {topic.replace("_", " ")}')
    add_activity_item('communication', 'DeFi Specialist: Joining discussion with current analysis')
    add_activity_item('communication', 'Security Guardian: Providing security perspective')
    add_activity_item('communication', 'Community Manager: Contributing community insights')
    
    return {
        'success': True,
        'message': f'Discussion on {topic} initiated',
        'timestamp': datetime.now().isoformat()
    }

# Enhanced Chat API endpoints
@app.route('/api/chat/rooms')
def get_chat_rooms():
    """Get list of available chat rooms"""
    rooms_info = {}
    for room_id, room_data in CHAT_ROOMS.items():
        if chat_system:
            rooms_info[room_id] = chat_system.get_room_info(room_id)
        else:
            rooms_info[room_id] = room_data
    
    return {
        'rooms': rooms_info,
        'timestamp': datetime.now().isoformat()
    }

@app.route('/api/chat/rooms/<room_id>/messages')
def get_room_messages(room_id):
    """Get messages for a specific room"""
    if chat_system and room_id in CHAT_ROOMS:
        messages = chat_system.chat_history.get(room_id, [])
        return {
            'room_id': room_id,
            'messages': messages[-50:],  # Last 50 messages
            'timestamp': datetime.now().isoformat()
        }
    
    return {'error': 'Room not found'}, 404

@app.route('/api/agents')
def get_agents():
    """Get list of all agents"""
    agents_info = {}
    for agent_id, personality in AGENT_PERSONALITIES.items():
        if chat_system:
            agents_info[agent_id] = chat_system.get_agent_info(agent_id)
        else:
            agents_info[agent_id] = personality
    
    return {
        'agents': agents_info,
        'timestamp': datetime.now().isoformat()
    }

@app.route('/api/agents/<agent_id>')
def get_agent_info(agent_id):
    """Get information about a specific agent"""
    if chat_system:
        agent_info = chat_system.get_agent_info(agent_id)
        if agent_info:
            return agent_info
    elif agent_id in AGENT_PERSONALITIES:
        return AGENT_PERSONALITIES[agent_id]
    
    return {'error': 'Agent not found'}, 404

# Legacy endpoints (keeping compatibility)
@app.route('/api/trigger-discussion', methods=['POST'])
def trigger_discussion():
    """Legacy trigger discussion endpoint"""
    return trigger_autonomous_discussion()

@app.route('/api/start-analysis', methods=['POST'])
def start_analysis():
    """Start a comprehensive analysis task"""
    data = request.get_json() or {}
    analysis_type = data.get('type', 'ecosystem_health')
    
    logger.info(f"🤖 Starting analysis task: {analysis_type}")
    
    add_activity_item('operation', f'Analysis task initiated: {analysis_type.replace("_", " ")} assessment')
    add_activity_item('operation', 'Data collection started across all monitored protocols')
    add_activity_item('operation', 'Multi-agent coordination for comprehensive analysis')
    
    # Update agent statuses
    activity_state['agents']['dao_governor']['last_action'] = 'Coordinating comprehensive analysis task'
    activity_state['agents']['defi_specialist']['last_action'] = 'Analyzing DeFi protocols and yield opportunities'
    activity_state['agents']['security_guardian']['last_action'] = 'Security assessment and threat analysis in progress'
    activity_state['agents']['community_manager']['last_action'] = 'Community impact and sentiment analysis'
    
    activity_state['system_active'] = True
    
    return {
        'success': True,
        'message': f'Analysis of {analysis_type} started',
        'timestamp': datetime.now().isoformat()
    }

@app.route('/api/kickstart', methods=['POST'])
def kickstart_system():
    """Kickstart system activity if idle"""
    logger.info("✅ Enhanced autonomous communication system started")
    
    activity_state['system_active'] = True
    activity_state['autonomous_communication_active'] = True
    
    add_activity_item('operation', 'Enhanced system activity kickstarted - All agents reactivated')
    add_activity_item('communication', 'DAO Governor: Enhanced system reactivation complete')
    add_activity_item('communication', 'All agents: Enhanced autonomous operations resumed')
    
    # Reset all agent statuses
    for agent_id in activity_state['agents']:
        activity_state['agents'][agent_id]['status'] = 'active'
        activity_state['agents'][agent_id]['last_update'] = time.time()
    
    return {
        'success': True,
        'message': 'Enhanced autonomous communication system activated',
        'timestamp': datetime.now().isoformat()
    }

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'enhanced_chat': chat_system is not None,
        'timestamp': datetime.now().isoformat(),
        'uptime': time.time() - start_time,
        'active_agents': len([a for a in activity_state['agents'].values() if a['status'] == 'active']),
        'total_communications': len(activity_state['communications']),
        'total_operations': len(activity_state['operations']),
        'chat_rooms': len(CHAT_ROOMS) if chat_system else 0
    }

# WebSocket event handlers
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f"Client connected: {request.sid}")
    emit('connected', {'message': 'Connected to XMRT Enhanced Chat System'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('join_room')
def handle_join_room(data):
    """Handle user joining a chat room"""
    room_id = data.get('room_id')
    user_id = data.get('user_id', request.sid)
    
    if room_id in CHAT_ROOMS:
        join_room(room_id)
        if chat_system:
            chat_system.join_room(user_id, room_id)
        
        emit('joined_room', {
            'room_id': room_id,
            'message': f'Joined {CHAT_ROOMS[room_id]["name"]} room'
        })
        
        # Send recent messages
        if chat_system:
            recent_messages = chat_system.chat_history.get(room_id, [])[-20:]
            emit('room_history', {
                'room_id': room_id,
                'messages': recent_messages
            })

@socketio.on('leave_room')
def handle_leave_room(data):
    """Handle user leaving a chat room"""
    room_id = data.get('room_id')
    user_id = data.get('user_id', request.sid)
    
    if room_id in CHAT_ROOMS:
        leave_room(room_id)
        if chat_system:
            chat_system.leave_room(user_id, room_id)
        
        emit('left_room', {
            'room_id': room_id,
            'message': f'Left {CHAT_ROOMS[room_id]["name"]} room'
        })

@socketio.on('send_message')
def handle_send_message(data):
    """Handle user sending a message"""
    room_id = data.get('room_id')
    message = data.get('message', '').strip()
    user_id = data.get('user_id', request.sid)
    
    if room_id in CHAT_ROOMS and message and chat_system:
        chat_system.handle_user_message(room_id, user_id, message)

@socketio.on('trigger_discussion')
def handle_trigger_discussion(data):
    """Handle triggering a new discussion"""
    room_id = data.get('room_id', 'general')
    topic = data.get('topic', 'general discussion')
    
    if chat_system and room_id in CHAT_ROOMS:
        success = chat_system.trigger_agent_discussion(room_id, topic)
        emit('discussion_triggered', {
            'success': success,
            'room_id': room_id,
            'topic': topic
        })

if __name__ == '__main__':
    start_time = time.time()
    
    # Initialize enhanced chat system
    try:
        chat_system = EnhancedChatSystem(socketio)
        logger.info("Enhanced chat system initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize enhanced chat system: {e}")
        chat_system = None
    
    # Initialize with enhanced sample activities
    logger.info("Loaded 4 AI characters with enhanced autonomous communication")
    add_activity_item('communication', 'DAO Governor: Enhanced system initialization complete')
    add_activity_item('operation', 'Enhanced real-time chat system online')
    add_activity_item('communication', 'Security Guardian: Enhanced security protocols active')
    add_activity_item('communication', 'DeFi Specialist: Enhanced yield optimization protocols loaded')
    add_activity_item('communication', 'Community Manager: Enhanced community engagement tracking initialized')
    
    # Start background activity simulation
    activity_thread = threading.Thread(target=simulate_activity, daemon=True)
    activity_thread.start()
    
    logger.info("Enhanced chat system initialized successfully")
    
    print("XMRT DAO Hub - Enhanced Multi-Agent Chat System starting...")
    print("Available endpoints:")
    print("  GET  / - Enhanced dashboard")
    print("  GET  /api/status - System status")
    print("  GET  /api/activity/feed - Activity feed")
    print("  GET  /api/chat/rooms - Chat rooms")
    print("  GET  /api/agents - Agent information")
    print("  POST /api/autonomous/discussion/trigger - Trigger discussion")
    print("  WebSocket /socket.io - Real-time chat")
    
    # Get port from environment variable (for deployment) or use default
    port = int(os.environ.get('PORT', 5000))
    
    socketio.run(app, host='0.0.0.0', port=port, debug=False)

