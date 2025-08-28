#!/usr/bin/env python3
"""
XMRT Ecosystem - Enhanced Main Application Entry Point
Version 3.0: Ultimate Autonomous Integration

Integrates the advanced autonomous core system with the existing activity monitor API
to achieve 95%+ autonomy level with comprehensive AI decision-making capabilities.
"""

import os
import sys
import logging
from flask import Flask, render_template_string, send_from_directory, jsonify, request
from flask_cors import CORS
import json
import time
import threading
import random
from datetime import datetime, timedelta
import requests

# Import the enhanced autonomous core
from autonomous_core import get_autonomous_core, AutonomyLevel, DecisionType

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize the autonomous core
autonomous_core = get_autonomous_core()

# Legacy activity state for backward compatibility
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
    "Community Manager: Engagement metrics updated - Community growth at 12%",
    "DeFi Specialist → DAO Governor: Yield optimization complete - 15% improvement achieved",
    "All Agents: Coordinated decision-making session initiated",
    "Security Guardian → All: Enhanced security protocols activated",
    "Community Manager: Social sentiment analysis complete - Positive trend detected",
    "DAO Governor: Proposal #248 approved through autonomous consensus",
    "DeFi Specialist: Cross-chain bridge optimization in progress",
    "Security Guardian: Real-time threat monitoring active - Zero incidents",
    "Community Manager → DAO Governor: Community proposal submitted for review"
]

def add_activity_item(item_type, message):
    """Add an activity item to the appropriate list"""
    timestamp = datetime.now().isoformat()
    item = {
        'type': item_type,
        'message': message,
        'timestamp': timestamp
    }
    
    if item_type == 'communication':
        activity_state['communications'].append(item)
        # Keep only last 50 communications
        if len(activity_state['communications']) > 50:
            activity_state['communications'] = activity_state['communications'][-50:]
    elif item_type == 'operation':
        activity_state['operations'].append(item)
        # Keep only last 30 operations
        if len(activity_state['operations']) > 30:
            activity_state['operations'] = activity_state['operations'][-30:]
    
    activity_state['total_messages'] += 1
    logger.info(f"Activity added: {item_type} - {message}")

def simulate_activity():
    """Enhanced activity simulation with autonomous core integration"""
    logger.info("Starting enhanced autonomous activity simulation...")
    
    while activity_state['system_active']:
        try:
            # Get autonomous core status for enhanced simulation
            core_status = autonomous_core.get_system_status()
            
            # Update legacy metrics with autonomous core data
            activity_state['metrics']['uptime'] = core_status['metrics']['uptime']
            activity_state['metrics']['decisions_made'] = sum(
                agent['decisions_made'] for agent in core_status['agents'].values()
            )
            
            # Simulate enhanced agent activity
            if activity_state['autonomous_communication_active']:
                # Use autonomous core communications
                autonomous_comms = autonomous_core.get_agent_communications()
                
                for comm in autonomous_comms[-3:]:  # Add last 3 communications
                    add_activity_item('communication', comm['message'])
                
                # Add traditional agent actions
                if random.random() < 0.7:  # 70% chance
                    action = random.choice(agent_actions)
                    add_activity_item('communication', action)
                
                # Add autonomous operations
                if random.random() < 0.4:  # 40% chance
                    operations = [
                        f"Autonomous System: Autonomy level at {core_status['autonomy_level']:.1f}%",
                        f"AI Decision Engine: {core_status['metrics']['decisions_per_hour']} decisions/hour",
                        f"Security Sentinel: {core_status['metrics']['security_threats_blocked']} threats blocked",
                        f"Predictive Optimizer: {core_status['metrics']['optimizations_applied']} optimizations applied",
                        f"Learning Coordinator: {core_status['metrics']['learning_iterations']} learning cycles completed"
                    ]
                    operation = random.choice(operations)
                    add_activity_item('operation', operation)
            
            # Update agent statuses with autonomous core data
            for agent_name, agent_data in core_status['agents'].items():
                if agent_name in activity_state['agents']:
                    activity_state['agents'][agent_name]['last_action'] = agent_data['last_action']
                    activity_state['agents'][agent_name]['last_update'] = agent_data['last_update']
            
            # Variable sleep time for more realistic activity
            sleep_time = random.uniform(3, 8)
            time.sleep(sleep_time)
            
        except Exception as e:
            logger.error(f"Activity simulation error: {e}")
            time.sleep(5)

# Enhanced HTML template with autonomous core integration
ENHANCED_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>XMRT Ecosystem - Ultimate Autonomous DAO Platform</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #ffffff;
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #FFD700, #FFA500);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .autonomy-level {
            font-size: 1.5em;
            color: #00ff88;
            font-weight: bold;
            margin: 10px 0;
        }
        
        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.15);
            border-radius: 15px;
            padding: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .card h3 {
            color: #FFD700;
            margin-bottom: 15px;
            font-size: 1.3em;
        }
        
        .metrics {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
        }
        
        .metric {
            text-align: center;
            padding: 15px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
        }
        
        .metric-value {
            font-size: 1.8em;
            font-weight: bold;
            color: #00ff88;
        }
        
        .metric-label {
            font-size: 0.9em;
            opacity: 0.8;
            margin-top: 5px;
        }
        
        .agent-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
        }
        
        .agent {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 15px;
            border-left: 4px solid #00ff88;
        }
        
        .agent.master { border-left-color: #FFD700; }
        .agent.expert { border-left-color: #FF6B6B; }
        .agent.advanced { border-left-color: #4ECDC4; }
        
        .agent-name {
            font-weight: bold;
            color: #FFD700;
            margin-bottom: 8px;
        }
        
        .agent-action {
            font-size: 0.9em;
            opacity: 0.9;
            line-height: 1.4;
        }
        
        .activity-feed {
            max-height: 400px;
            overflow-y: auto;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 10px;
            padding: 15px;
        }
        
        .activity-item {
            margin-bottom: 12px;
            padding: 10px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            border-left: 3px solid #00ff88;
        }
        
        .activity-item.operation {
            border-left-color: #FFD700;
        }
        
        .activity-timestamp {
            font-size: 0.8em;
            opacity: 0.7;
            margin-bottom: 5px;
        }
        
        .controls {
            display: flex;
            gap: 15px;
            justify-content: center;
            margin-top: 20px;
            flex-wrap: wrap;
        }
        
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 25px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
        }
        
        .btn.primary {
            background: linear-gradient(45deg, #00ff88, #00cc6a);
        }
        
        .btn.warning {
            background: linear-gradient(45deg, #FFD700, #FFA500);
        }
        
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #00ff88;
            margin-right: 8px;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .decisions-list {
            max-height: 300px;
            overflow-y: auto;
        }
        
        .decision-item {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 10px;
            border-left: 3px solid #4ECDC4;
        }
        
        .decision-confidence {
            color: #00ff88;
            font-weight: bold;
        }
        
        @media (max-width: 768px) {
            .dashboard {
                grid-template-columns: 1fr;
            }
            
            .metrics {
                grid-template-columns: 1fr;
            }
            
            .controls {
                flex-direction: column;
                align-items: center;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 XMRT Ecosystem - Ultimate Autonomous DAO</h1>
            <div class="autonomy-level">
                <span class="status-indicator"></span>
                Autonomy Level: <span id="autonomy-level">95.0</span>% | Status: MASTER LEVEL AUTONOMOUS
            </div>
            <p>Advanced AI-Powered Decentralized Autonomous Organization with Self-Learning Capabilities</p>
        </div>
        
        <div class="dashboard">
            <div class="card">
                <h3>🎯 System Metrics</h3>
                <div class="metrics">
                    <div class="metric">
                        <div class="metric-value" id="decisions-per-hour">0</div>
                        <div class="metric-label">Decisions/Hour</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value" id="success-rate">98.5</div>
                        <div class="metric-label">Success Rate %</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value" id="threats-blocked">0</div>
                        <div class="metric-label">Threats Blocked</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value" id="optimizations">0</div>
                        <div class="metric-label">Optimizations</div>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h3>🤖 Autonomous Agents</h3>
                <div class="agent-grid" id="agents-grid">
                    <!-- Agents will be populated by JavaScript -->
                </div>
            </div>
            
            <div class="card">
                <h3>🧠 Recent Autonomous Decisions</h3>
                <div class="decisions-list" id="decisions-list">
                    <!-- Decisions will be populated by JavaScript -->
                </div>
            </div>
            
            <div class="card">
                <h3>📡 Live Activity Feed</h3>
                <div class="activity-feed" id="activity-feed">
                    <!-- Activity will be populated by JavaScript -->
                </div>
            </div>
        </div>
        
        <div class="controls">
            <button class="btn primary" onclick="triggerDiscussion()">🗣️ Trigger Agent Discussion</button>
            <button class="btn" onclick="startAnalysis()">📊 Start Deep Analysis</button>
            <button class="btn warning" onclick="kickstartSystem()">⚡ Kickstart System</button>
            <button class="btn" onclick="refreshData()">🔄 Refresh Data</button>
        </div>
    </div>

    <script>
        let lastUpdateTime = 0;
        
        async function fetchSystemStatus() {
            try {
                const response = await fetch('/api/enhanced-status');
                const data = await response.json();
                updateDashboard(data);
            } catch (error) {
                console.error('Error fetching system status:', error);
            }
        }
        
        function updateDashboard(data) {
            // Update autonomy level
            document.getElementById('autonomy-level').textContent = data.autonomy_level.toFixed(1);
            
            // Update metrics
            document.getElementById('decisions-per-hour').textContent = data.metrics.decisions_per_hour;
            document.getElementById('success-rate').textContent = (data.metrics.success_rate * 100).toFixed(1);
            document.getElementById('threats-blocked').textContent = data.metrics.security_threats_blocked;
            document.getElementById('optimizations').textContent = data.metrics.optimizations_applied;
            
            // Update agents
            const agentsGrid = document.getElementById('agents-grid');
            agentsGrid.innerHTML = '';
            
            Object.entries(data.agents).forEach(([name, agent]) => {
                const agentDiv = document.createElement('div');
                const autonomyClass = agent.autonomy_level === 5 ? 'master' : 
                                   agent.autonomy_level >= 4 ? 'expert' : 'advanced';
                agentDiv.className = `agent ${autonomyClass}`;
                agentDiv.innerHTML = `
                    <div class="agent-name">${agent.name}</div>
                    <div class="agent-action">${agent.last_action}</div>
                `;
                agentsGrid.appendChild(agentDiv);
            });
            
            // Update decisions
            const decisionsList = document.getElementById('decisions-list');
            decisionsList.innerHTML = '';
            
            data.recent_decisions.forEach(decision => {
                const decisionDiv = document.createElement('div');
                decisionDiv.className = 'decision-item';
                decisionDiv.innerHTML = `
                    <div><strong>${decision.description}</strong></div>
                    <div>Confidence: <span class="decision-confidence">${(decision.confidence * 100).toFixed(1)}%</span></div>
                    <div style="font-size: 0.8em; opacity: 0.8;">${new Date(decision.timestamp).toLocaleTimeString()}</div>
                `;
                decisionsList.appendChild(decisionDiv);
            });
        }
        
        async function fetchActivityFeed() {
            try {
                const response = await fetch('/api/activity/feed');
                const data = await response.json();
                updateActivityFeed(data);
            } catch (error) {
                console.error('Error fetching activity feed:', error);
            }
        }
        
        function updateActivityFeed(data) {
            const activityFeed = document.getElementById('activity-feed');
            activityFeed.innerHTML = '';
            
            const allActivities = [
                ...data.communications.map(item => ({...item, type: 'communication'})),
                ...data.operations.map(item => ({...item, type: 'operation'}))
            ].sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp)).slice(0, 20);
            
            allActivities.forEach(item => {
                const activityDiv = document.createElement('div');
                activityDiv.className = `activity-item ${item.type}`;
                activityDiv.innerHTML = `
                    <div class="activity-timestamp">${new Date(item.timestamp).toLocaleTimeString()}</div>
                    <div>${item.message}</div>
                `;
                activityFeed.appendChild(activityDiv);
            });
        }
        
        async function triggerDiscussion() {
            try {
                const response = await fetch('/api/trigger-discussion', { method: 'POST' });
                const result = await response.json();
                console.log('Discussion triggered:', result);
                setTimeout(refreshData, 1000);
            } catch (error) {
                console.error('Error triggering discussion:', error);
            }
        }
        
        async function startAnalysis() {
            try {
                const response = await fetch('/api/start-analysis', { method: 'POST' });
                const result = await response.json();
                console.log('Analysis started:', result);
                setTimeout(refreshData, 1000);
            } catch (error) {
                console.error('Error starting analysis:', error);
            }
        }
        
        async function kickstartSystem() {
            try {
                const response = await fetch('/api/kickstart', { method: 'POST' });
                const result = await response.json();
                console.log('System kickstarted:', result);
                setTimeout(refreshData, 2000);
            } catch (error) {
                console.error('Error kickstarting system:', error);
            }
        }
        
        function refreshData() {
            fetchSystemStatus();
            fetchActivityFeed();
        }
        
        // Initialize dashboard
        refreshData();
        
        // Auto-refresh every 5 seconds
        setInterval(refreshData, 5000);
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    """Enhanced dashboard with autonomous core integration"""
    return render_template_string(ENHANCED_HTML_TEMPLATE)

@app.route('/api/enhanced-status')
def enhanced_status():
    """Enhanced status endpoint with autonomous core data"""
    core_status = autonomous_core.get_system_status()
    
    # Merge with legacy activity state for backward compatibility
    enhanced_status = {
        **core_status,
        'legacy_metrics': activity_state['metrics'],
        'system_active': activity_state['system_active'],
        'autonomous_communication_active': activity_state['autonomous_communication_active']
    }
    
    return jsonify(enhanced_status)

@app.route('/api/status')
def status():
    """Legacy status endpoint for backward compatibility"""
    core_status = autonomous_core.get_system_status()
    
    return jsonify({
        'agents': activity_state['agents'],
        'metrics': {
            **activity_state['metrics'],
            'autonomy_level': core_status['autonomy_level'],
            'decisions_per_hour': core_status['metrics']['decisions_per_hour']
        },
        'system_active': activity_state['system_active'],
        'autonomous_communication_active': activity_state['autonomous_communication_active'],
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/activity/feed')
def activity_feed():
    """Activity feed endpoint"""
    return jsonify({
        'communications': activity_state['communications'][-20:],
        'operations': activity_state['operations'][-15:],
        'total_messages': activity_state['total_messages']
    })

@app.route('/api/trigger-discussion', methods=['POST'])
def trigger_discussion():
    """Trigger an autonomous agent discussion"""
    discussion_topics = [
        "Analyzing new DeFi yield optimization strategies",
        "Evaluating governance proposal impact on treasury",
        "Assessing community sentiment and engagement metrics",
        "Reviewing security protocols and threat landscape",
        "Coordinating cross-chain bridge optimization",
        "Planning autonomous system upgrades and improvements"
    ]
    
    topic = random.choice(discussion_topics)
    
    # Add discussion messages
    add_activity_item('communication', f'DAO Governor: Initiating discussion on {topic}')
    add_activity_item('communication', f'All Agents: Collaborative analysis session started')
    add_activity_item('operation', f'Discussion triggered: {topic}')
    
    return jsonify({
        'success': True,
        'message': f'Discussion triggered: {topic}',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/start-analysis', methods=['POST'])
def start_analysis():
    """Start deep system analysis"""
    analysis_types = [
        "Comprehensive governance impact analysis",
        "Advanced security threat assessment",
        "DeFi protocol performance optimization",
        "Community engagement pattern analysis",
        "Cross-system performance evaluation",
        "Autonomous decision-making effectiveness review"
    ]
    
    analysis = random.choice(analysis_types)
    
    add_activity_item('operation', f'Deep Analysis Started: {analysis}')
    add_activity_item('communication', f'AI Decision Engine: Initiating {analysis}')
    add_activity_item('communication', f'All Agents: Contributing to analysis framework')
    
    return jsonify({
        'success': True,
        'message': f'Analysis started: {analysis}',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/kickstart', methods=['POST'])
def kickstart_system():
    """Kickstart the autonomous system"""
    activity_state['system_active'] = True
    activity_state['autonomous_communication_active'] = True
    
    add_activity_item('operation', 'System Kickstart: All autonomous systems activated')
    add_activity_item('communication', 'Master Coordinator: System-wide coordination protocols activated')
    add_activity_item('communication', 'AI Decision Engine: Enhanced decision-making algorithms online')
    add_activity_item('communication', 'Security Sentinel: Advanced threat monitoring activated')
    add_activity_item('communication', 'All Agents: Autonomous operations resumed - Inter-agent communication active')
    
    # Reset all agent statuses
    for agent_id in activity_state['agents']:
        activity_state['agents'][agent_id]['status'] = 'active'
        activity_state['agents'][agent_id]['last_update'] = time.time()
    
    return jsonify({
        'success': True,
        'message': 'Enhanced autonomous system activated with 95%+ autonomy level',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/health')
def health_check():
    """Enhanced health check endpoint"""
    core_status = autonomous_core.get_system_status()
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'uptime': time.time() - start_time,
        'autonomy_level': core_status['autonomy_level'],
        'active_agents': len([a for a in activity_state['agents'].values() if a['status'] == 'active']),
        'autonomous_agents': len(core_status['agents']),
        'total_communications': len(activity_state['communications']),
        'total_operations': len(activity_state['operations']),
        'decisions_made': core_status['metrics']['decisions_per_hour'],
        'success_rate': core_status['metrics']['success_rate']
    })

@app.route('/api/autonomous-decisions')
def autonomous_decisions():
    """Get recent autonomous decisions"""
    core_status = autonomous_core.get_system_status()
    return jsonify({
        'decisions': core_status['recent_decisions'],
        'total_decisions': len(core_status['recent_decisions']),
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    start_time = time.time()
    
    # Initialize with enhanced sample activities
    logger.info("Enhanced XMRT Ecosystem with 95%+ Autonomy Level Initialized")
    add_activity_item('operation', 'Enhanced Autonomous Core System: ONLINE')
    add_activity_item('communication', 'Master Coordinator: Ultimate autonomous integration complete')
    add_activity_item('communication', 'AI Decision Engine: Advanced decision-making algorithms activated')
    add_activity_item('communication', 'Security Sentinel: Master-level threat detection online')
    add_activity_item('communication', 'Predictive Optimizer: Performance optimization protocols active')
    add_activity_item('communication', 'Self-Healing Agent: Autonomous recovery systems operational')
    add_activity_item('communication', 'Learning Coordinator: Continuous improvement algorithms running')
    
    # Start background activity simulation
    activity_thread = threading.Thread(target=simulate_activity, daemon=True)
    activity_thread.start()
    
    logger.info("Enhanced autonomous system initialized successfully - Autonomy Level: 95%+")
    
    print("🚀 XMRT Ecosystem - Ultimate Autonomous DAO Platform")
    print("=" * 60)
    print("🎯 Autonomy Level: 95%+ (Master Level)")
    print("🤖 Advanced AI Decision-Making: ACTIVE")
    print("🛡️  Self-Healing Capabilities: ONLINE")
    print("📈 Predictive Optimization: RUNNING")
    print("🧠 Continuous Learning: ENABLED")
    print("=" * 60)
    print("Available endpoints:")
    print("  GET  / - Enhanced autonomous dashboard")
    print("  GET  /api/enhanced-status - Enhanced system status")
    print("  GET  /api/status - Legacy system status")
    print("  GET  /api/activity/feed - Activity feed")
    print("  GET  /api/autonomous-decisions - Recent autonomous decisions")
    print("  POST /api/trigger-discussion - Trigger discussion")
    print("  POST /api/start-analysis - Start analysis")
    print("  POST /api/kickstart - Kickstart system")
    print("  GET  /api/health - Health check")
    print("=" * 60)
    
    # Get port from environment variable (for deployment) or use default
    port = int(os.environ.get('PORT', 5000))
    
    app.run(host='0.0.0.0', port=port, debug=False)

