from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import time
import threading
import random
from datetime import datetime, timedelta
import requests

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global state for activity monitoring
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
    'system_active': True
}

# Sample activities for simulation
agent_actions = [
    "DAO Governor: Analyzing new governance proposal",
    "DeFi Specialist: Optimizing yield farming strategy", 
    "Security Guardian: Performing security audit",
    "Community Manager: Processing community feedback",
    "DAO Governor → DeFi Specialist: Requesting treasury analysis",
    "Security Guardian: Threat assessment completed",
    "Community Manager: Sentiment analysis updated",
    "DeFi Specialist: Liquidity rebalancing executed",
    "DAO Governor: Multi-signature transaction initiated",
    "Security Guardian: Vulnerability scan completed",
    "Community Manager: Event coordination in progress",
    "DeFi Specialist: Cross-chain bridge operation"
]

system_operations = [
    "Smart contract deployment successful",
    "Cross-chain bridge operation completed", 
    "Treasury rebalancing executed",
    "Automated backup completed",
    "Performance optimization applied",
    "Security scan completed - All clear",
    "Code improvement deployed",
    "Network synchronization completed",
    "Emergency circuit breaker tested",
    "Multi-chain governance sync completed",
    "Zero-knowledge proof verification successful",
    "Automated incident response triggered"
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
        # Keep only last 10 items
        activity_state['communications'] = activity_state['communications'][:10]
    elif activity_type == 'operation':
        activity_state['operations'].insert(0, item)
        # Keep only last 10 items
        activity_state['operations'] = activity_state['operations'][:10]

def simulate_activity():
    """Background thread to simulate agent activity"""
    while True:
        if activity_state['system_active']:
            # Add agent communication (50% chance)
            if random.random() > 0.5:
                action = random.choice(agent_actions)
                add_activity_item('communication', action)
            
            # Add system operation (30% chance)
            if random.random() > 0.7:
                operation = random.choice(system_operations)
                add_activity_item('operation', operation)
            
            # Update agent statuses occasionally
            if random.random() > 0.8:
                update_agent_statuses()
            
            # Update metrics occasionally
            if random.random() > 0.9:
                update_metrics()
        
        time.sleep(15)  # Wait 15 seconds between updates

def update_agent_statuses():
    """Update agent statuses with random activities"""
    statuses = ['Analyzing', 'Processing', 'Optimizing', 'Monitoring', 'Coordinating']
    
    for agent_id in activity_state['agents']:
        if random.random() > 0.7:  # 30% chance to update each agent
            agent = activity_state['agents'][agent_id]
            agent['last_action'] = f"{random.choice(statuses)}..."
            agent['last_update'] = time.time()

def update_metrics():
    """Update system metrics"""
    metrics = activity_state['metrics']
    
    # Occasionally increment community count
    if random.random() > 0.8:
        metrics['community_count'] += random.randint(1, 5)
    
    # Occasionally increment decisions made
    if random.random() > 0.9:
        metrics['decisions_made'] += 1

def check_external_service():
    """Check if the external XMRT service is active"""
    try:
        response = requests.get('https://xmrtnet-eliza.onrender.com/', timeout=5)
        return response.status_code == 200
    except:
        return False

@app.route('/api/status')
def get_status():
    """Get overall system status"""
    external_active = check_external_service()
    
    return jsonify({
        'active': activity_state['system_active'],
        'external_service_active': external_active,
        'agents': activity_state['agents'],
        'metrics': activity_state['metrics'],
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/activity/feed')
def get_activity_feed():
    """Get the current activity feed"""
    return jsonify({
        'communications': activity_state['communications'],
        'operations': activity_state['operations'],
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/trigger-discussion', methods=['POST'])
def trigger_discussion():
    """Trigger a new agent discussion"""
    data = request.get_json() or {}
    topic = data.get('topic', 'general_coordination')
    
    # Add discussion activities
    add_activity_item('communication', f'DAO Governor: Initiating multi-agent discussion on {topic.replace("_", " ")}')
    add_activity_item('communication', 'DeFi Specialist: Joining discussion with current yield analysis')
    add_activity_item('communication', 'Security Guardian: Providing security assessment for proposed changes')
    add_activity_item('communication', 'Community Manager: Contributing sentiment analysis data')
    
    # Try to trigger actual external service
    try:
        requests.post('https://xmrtnet-eliza.onrender.com/api/trigger-discussion', 
                     json={'topic': topic}, timeout=5)
        add_activity_item('operation', 'External AI service discussion triggered successfully')
    except:
        add_activity_item('operation', 'External AI service unavailable - using simulated discussion')
    
    activity_state['system_active'] = True
    
    return jsonify({
        'success': True,
        'message': f'Discussion on {topic} initiated',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/start-analysis', methods=['POST'])
def start_analysis():
    """Start a comprehensive analysis task"""
    data = request.get_json() or {}
    analysis_type = data.get('type', 'ecosystem_health')
    
    # Add analysis activities
    add_activity_item('operation', f'Analysis task initiated: {analysis_type.replace("_", " ")} check')
    add_activity_item('operation', 'Data collection started across all monitored protocols')
    add_activity_item('operation', 'Multi-agent coordination for comprehensive analysis')
    
    # Update agent statuses to show analysis work
    activity_state['agents']['dao_governor']['last_action'] = 'Coordinating analysis task'
    activity_state['agents']['defi_specialist']['last_action'] = 'Analyzing DeFi protocols'
    activity_state['agents']['security_guardian']['last_action'] = 'Security assessment in progress'
    activity_state['agents']['community_manager']['last_action'] = 'Community impact analysis'
    
    # Try to trigger actual external service
    try:
        requests.post('https://xmrtnet-eliza.onrender.com/api/start-analysis',
                     json={'type': analysis_type}, timeout=5)
        add_activity_item('operation', 'External AI service analysis started')
    except:
        add_activity_item('operation', 'External AI service unavailable - using simulated analysis')
    
    activity_state['system_active'] = True
    
    return jsonify({
        'success': True,
        'message': f'Analysis of {analysis_type} started',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/agents/<agent_id>/status')
def get_agent_status(agent_id):
    """Get status of a specific agent"""
    if agent_id in activity_state['agents']:
        return jsonify(activity_state['agents'][agent_id])
    else:
        return jsonify({'error': 'Agent not found'}), 404

@app.route('/api/metrics')
def get_metrics():
    """Get current system metrics"""
    return jsonify(activity_state['metrics'])

@app.route('/api/kickstart', methods=['POST'])
def kickstart_system():
    """Kickstart system activity if idle"""
    activity_state['system_active'] = True
    
    # Add kickstart activities
    add_activity_item('operation', 'System activity kickstarted - All agents reactivated')
    add_activity_item('communication', 'DAO Governor: System reactivation complete')
    add_activity_item('communication', 'All agents: Resuming autonomous operations')
    
    # Reset all agent statuses
    for agent_id in activity_state['agents']:
        activity_state['agents'][agent_id]['status'] = 'active'
        activity_state['agents'][agent_id]['last_update'] = time.time()
    
    return jsonify({
        'success': True,
        'message': 'System activity kickstarted',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'uptime': time.time() - start_time
    })

if __name__ == '__main__':
    start_time = time.time()
    
    # Initialize with some sample activities
    add_activity_item('communication', 'DAO Governor: System initialization complete')
    add_activity_item('operation', 'All systems online and monitoring active')
    add_activity_item('communication', 'Security Guardian: Initial security scan completed')
    
    # Start background activity simulation
    activity_thread = threading.Thread(target=simulate_activity, daemon=True)
    activity_thread.start()
    
    print("XMRT Activity Monitor API starting...")
    print("Available endpoints:")
    print("  GET  /api/status - System status")
    print("  GET  /api/activity/feed - Activity feed")
    print("  POST /api/trigger-discussion - Trigger discussion")
    print("  POST /api/start-analysis - Start analysis")
    print("  POST /api/kickstart - Kickstart system")
    print("  GET  /api/health - Health check")
    
    app.run(host='0.0.0.0', port=5001, debug=True)

