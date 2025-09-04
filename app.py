"""
XMRT-Ecosystem Autonomous Learning System
Main Flask Application Entry Point

This is the main web application that hosts the autonomous learning system.
It provides a web interface to monitor the autonomous agents and their progress.
The actual autonomous learning runs in the background via APScheduler.
"""

import os
import logging
from flask import Flask, render_template_string, jsonify, request
from flask_socketio import SocketIO, emit
import threading
from datetime import datetime

# Import our autonomous system components
from autonomous_controller import AutonomousController
from multi_agent_system import MultiAgentSystem
from github_manager import GitHubManager
from memory_system import MemorySystem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app

import json
from datetime import datetime

class DateTimeJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime objects"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

def safe_json_serialize(data):
    """Safely serialize data to JSON, handling datetime objects"""
    return json.dumps(data, cls=DateTimeJSONEncoder)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'xmrt-ecosystem-secret-key-2024')

# Initialize SocketIO with gevent support for Render
# Initialize SocketIO with proper gevent configuration
try:
    # Try gevent mode first
    socketio = SocketIO(app, 
                       cors_allowed_origins="*",
                       async_mode='gevent',
                       logger=False,  # Reduce logging to avoid issues
                       engineio_logger=False)
    print("✅ SocketIO initialized with gevent mode")
except Exception as e:
    print(f"⚠️ Gevent mode failed: {e}")
    # Fallback to threading mode
    socketio = SocketIO(app, 
                       cors_allowed_origins="*",
                       async_mode='threading',
                       logger=False,
                       engineio_logger=False)
    print("✅ SocketIO initialized with threading mode (fallback)")

# Global autonomous system instance
autonomous_system = None
system_status = {
    'status': 'initializing',
    'last_cycle': None,
    'total_cycles': 0,
    'repositories_managed': 0,
    'last_commit': None,
    'agents_active': False
}

def initialize_autonomous_system():
    """Initialize the autonomous learning system"""
    global autonomous_system, system_status

    try:
        logger.info("🤖 Initializing XMRT Autonomous Learning System...")

        # Initialize components
        github_token = os.environ.get('GITHUB_TOKEN')
        if not github_token:
            logger.error("❌ GITHUB_TOKEN environment variable not set!")
            system_status['status'] = 'error'
            return

        # Create autonomous controller
        autonomous_system = AutonomousController(github_token)

        # Start the autonomous learning cycles
        autonomous_system.start_autonomous_learning()

        system_status.update({
            'status': 'running',
            'agents_active': True,
            'initialized_at': datetime.now().isoformat()
        })

        logger.info("✅ Autonomous learning system initialized and started!")

    except Exception as e:
        logger.error(f"❌ Error initializing autonomous system: {str(e)}")
        system_status['status'] = 'error'
        system_status['error'] = str(e)

# Web interface template
WEB_INTERFACE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧠 XMRT Autonomous AI Ecosystem - Live Dashboard</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.2/socket.io.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
            color: #ffffff;
            min-height: 100vh;
            overflow-x: hidden;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            text-align: center;
            margin-bottom: 30px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 30px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 10px;
            animation: pulse 2s infinite;
        }

        .status-active { background-color: #00ff88; }
        .status-initializing { background-color: #ffa500; }
        .status-error { background-color: #ff4444; }

        @keyframes pulse {
            0% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.1); opacity: 0.7; }
            100% { transform: scale(1); opacity: 1; }
        }

        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
        }

        .card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(0, 255, 136, 0.3);
        }

        .card-header {
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 15px;
            color: #00ff88;
            display: flex;
            align-items: center;
        }

        .metric {
            display: flex;
            justify-content: space-between;
            margin-bottom: 12px;
            padding: 8px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .metric-value {
            font-weight: bold;
            color: #00ff88;
        }

        .agents-container {
            display: grid;
            gap: 15px;
        }

        .agent {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 10px;
            padding: 15px;
            border-left: 4px solid #00ff88;
        }

        .agent.inactive {
            border-left-color: #666;
            opacity: 0.6;
        }

        .agent-name {
            font-weight: bold;
            color: #00ff88;
            margin-bottom: 8px;
        }

        .agent-type {
            font-size: 0.9em;
            color: #ccc;
            margin-bottom: 8px;
        }

        .capabilities {
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
            margin-top: 10px;
        }

        .capability {
            background: rgba(0, 255, 136, 0.2);
            color: #00ff88;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.8em;
        }

        .log-container {
            background: rgba(0, 0, 0, 0.5);
            border-radius: 15px;
            padding: 20px;
            max-height: 300px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .log-entry {
            margin-bottom: 8px;
            padding: 5px;
            border-radius: 5px;
        }

        .log-success { background: rgba(0, 255, 136, 0.1); color: #00ff88; }
        .log-error { background: rgba(255, 68, 68, 0.1); color: #ff4444; }
        .log-info { background: rgba(100, 149, 237, 0.1); color: #6495ed; }

        .connection-status {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 10px 15px;
            border-radius: 25px;
            font-size: 0.9em;
            font-weight: bold;
            z-index: 1000;
        }

        .connected {
            background: rgba(0, 255, 136, 0.2);
            color: #00ff88;
            border: 1px solid #00ff88;
        }

        .disconnected {
            background: rgba(255, 68, 68, 0.2);
            color: #ff4444;
            border: 1px solid #ff4444;
        }

        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }

        .feature {
            background: rgba(255, 255, 255, 0.05);
            padding: 20px;
            border-radius: 10px;
            border-left: 3px solid #00ff88;
        }

        .refresh-btn {
            background: linear-gradient(45deg, #00ff88, #00cc6a);
            color: #000;
            border: none;
            padding: 12px 25px;
            border-radius: 25px;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s;
            margin: 10px;
        }

        .refresh-btn:hover {
            transform: scale(1.05);
        }

        @media (max-width: 768px) {
            .dashboard-grid {
                grid-template-columns: 1fr;
            }
            .container {
                padding: 10px;
            }
        }
    </style>
</head>
<body>
    <div class="connection-status" id="connectionStatus">
        <span class="status-indicator status-initializing"></span>
        Connecting...
    </div>

    <div class="container">
        <div class="header">
            <h1>🧠 XMRT Autonomous AI Ecosystem</h1>
            <p style="margin: 10px 0; opacity: 0.8;">Real-time Multi-Agent Coordination & Learning Platform</p>
            <div>
                <span class="status-indicator" id="systemStatus"></span>
                <span id="systemStatusText">Initializing System...</span>
            </div>
            <button class="refresh-btn" onclick="requestStatus()">🔄 Refresh Status</button>
        </div>

        <div class="dashboard-grid">
            <div class="card">
                <div class="card-header">
                    <span>📊 System Metrics</span>
                </div>
                <div id="systemMetrics">
                    <div class="metric">
                        <span>Total Cycles:</span>
                        <span class="metric-value" id="totalCycles">0</span>
                    </div>
                    <div class="metric">
                        <span>Repositories Managed:</span>
                        <span class="metric-value" id="reposManaged">0</span>
                    </div>
                    <div class="metric">
                        <span>Last Cycle:</span>
                        <span class="metric-value" id="lastCycle">Never</span>
                    </div>
                    <div class="metric">
                        <span>Last Commit:</span>
                        <span class="metric-value" id="lastCommit">None</span>
                    </div>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <span>🤖 AI Agents Status</span>
                </div>
                <div class="agents-container" id="agentsContainer">
                    <div class="agent">
                        <div class="agent-name">System Initializing...</div>
                        <div class="agent-type">Please wait while agents come online</div>
                    </div>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <span>📈 Performance Analytics</span>
                </div>
                <div id="performanceMetrics">
                    <div class="metric">
                        <span>Task Queue:</span>
                        <span class="metric-value" id="taskQueue">0</span>
                    </div>
                    <div class="metric">
                        <span>Completed Tasks:</span>
                        <span class="metric-value" id="completedTasks">0</span>
                    </div>
                    <div class="metric">
                        <span>Success Rate:</span>
                        <span class="metric-value" id="successRate">--</span>
                    </div>
                </div>
            </div>
        </div>

        <div class="features-grid">
            <div class="feature">
                <h3>🔄 Autonomous Learning</h3>
                <p>AI agents continuously learn and adapt from interactions, improving performance over time through advanced machine learning algorithms.</p>
            </div>
            <div class="feature">
                <h3>🤝 Multi-Agent Collaboration</h3>
                <p>4 specialized AI agents (Coordinator, Analyzer, Developer, Manager) work together via real-time SocketIO communication.</p>
            </div>
            <div class="feature">
                <h3>📊 Real-time Analytics</h3>
                <p>Live performance monitoring, pattern recognition, and intelligent resource allocation with comprehensive metrics tracking.</p>
            </div>
            <div class="feature">
                <h3>🧠 Advanced Memory System</h3>
                <p>Persistent memory with cross-session learning, pattern recognition, and intelligent memory management for optimal performance.</p>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <span>📝 System Activity Log</span>
            </div>
            <div class="log-container" id="systemLog">
                <div class="log-entry log-info">System starting up...</div>
            </div>
        </div>
    </div>

    <script>
        const socket = io();
        let systemData = {};

        // Connection status handling
        const connectionStatus = document.getElementById('connectionStatus');

        socket.on('connect', function() {
            console.log('Connected to XMRT System');
            connectionStatus.innerHTML = '<span class="status-indicator status-active"></span>Connected';
            connectionStatus.className = 'connection-status connected';
            addLogEntry('Connected to XMRT System', 'success');
            requestStatus();
        });

        socket.on('disconnect', function() {
            console.log('Disconnected from XMRT System');
            connectionStatus.innerHTML = '<span class="status-indicator status-error"></span>Disconnected';
            connectionStatus.className = 'connection-status disconnected';
            addLogEntry('Disconnected from XMRT System', 'error');
        });

        // System status updates
        socket.on('system_update', function(data) {
            console.log('System update received:', data);
            systemData = data;
            updateDashboard(data);
        });

        function updateDashboard(data) {
            // Update system status indicator
            const statusIndicator = document.getElementById('systemStatus');
            const statusText = document.getElementById('systemStatusText');

            if (data.status === 'active') {
                statusIndicator.className = 'status-indicator status-active';
                statusText.textContent = 'System Active';
            } else if (data.status === 'initializing') {
                statusIndicator.className = 'status-indicator status-initializing';
                statusText.textContent = 'Initializing...';
            } else {
                statusIndicator.className = 'status-indicator status-error';
                statusText.textContent = 'System Error';
            }

            // Update metrics
            document.getElementById('totalCycles').textContent = data.total_cycles || 0;
            document.getElementById('reposManaged').textContent = data.repositories_managed || 0;
            document.getElementById('lastCycle').textContent = data.last_cycle || 'Never';
            document.getElementById('lastCommit').textContent = data.last_commit || 'None';

            // Update agents if available
            if (data.agents && typeof data.agents === 'object') {
                updateAgentsDisplay(data.agents);
            }

            // Update performance metrics
            document.getElementById('taskQueue').textContent = data.task_queue_size || 0;
            document.getElementById('completedTasks').textContent = data.completed_tasks || 0;

            const successRate = data.completed_tasks && data.total_cycles ? 
                Math.round((data.completed_tasks / data.total_cycles) * 100) + '%' : '--';
            document.getElementById('successRate').textContent = successRate;

            addLogEntry('System status updated successfully', 'success');
        }

        function updateAgentsDisplay(agents) {
            const container = document.getElementById('agentsContainer');
            container.innerHTML = '';

            Object.entries(agents).forEach(([agentId, agent]) => {
                const agentDiv = document.createElement('div');
                agentDiv.className = `agent ${agent.active ? '' : 'inactive'}`;

                let capabilities = '';
                if (agent.capabilities && typeof agent.capabilities === 'object') {
                    capabilities = Object.keys(agent.capabilities).map(cap => 
                        `<span class="capability">${cap}</span>`
                    ).join('');
                }

                agentDiv.innerHTML = `
                    <div class="agent-name">${agentId}</div>
                    <div class="agent-type">Type: ${agent.type || 'Unknown'}</div>
                    <div style="font-size: 0.9em; color: #ccc;">
                        Status: ${agent.active ? '🟢 Active' : '🔴 Inactive'}
                    </div>
                    <div class="capabilities">${capabilities}</div>
                `;
                container.appendChild(agentDiv);
            });

            if (Object.keys(agents).length === 0) {
                container.innerHTML = '<div class="agent"><div class="agent-name">No agents detected</div></div>';
            }
        }

        function addLogEntry(message, type = 'info') {
            const logContainer = document.getElementById('systemLog');
            const entry = document.createElement('div');
            entry.className = `log-entry log-${type}`;

            const timestamp = new Date().toLocaleTimeString();
            entry.innerHTML = `[${timestamp}] ${message}`;

            logContainer.appendChild(entry);
            logContainer.scrollTop = logContainer.scrollHeight;

            // Keep only last 50 entries
            while (logContainer.children.length > 50) {
                logContainer.removeChild(logContainer.firstChild);
            }
        }

        function requestStatus() {
            socket.emit('request_status');
            addLogEntry('Status refresh requested', 'info');
        }

        // Auto-refresh every 30 seconds
        setInterval(requestStatus, 30000);

        // Initial log entries
        addLogEntry('Dashboard initialized', 'info');
        addLogEntry('Attempting connection to XMRT System...', 'info');
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Main dashboard showing autonomous system status"""
    return render_template_string(WEB_INTERFACE)

@app.route('/status')
def status():
    """API endpoint for system status"""
    global system_status
    return jsonify(system_status)

@app.route('/health')
def health():
    """Health check endpoint for Render"""
    return jsonify({
        'status': 'healthy',
        'autonomous_system': autonomous_system is not None,
        'timestamp': datetime.now().isoformat()
    })



def clean_system_status_for_json(status):
    """Clean system status to make it JSON serializable"""
    import copy
    cleaned = copy.deepcopy(status)

    def clean_dict(d):
        if isinstance(d, dict):
            return {k: clean_dict(v) for k, v in d.items()}
        elif isinstance(d, list):
            return [clean_dict(item) for item in d]
        elif isinstance(d, datetime):
            return d.isoformat()
        elif hasattr(d, '__dict__'):
            # Convert objects to dict representation
            return clean_dict(d.__dict__)
        else:
            return d

    return clean_dict(cleaned)

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    emit('system_update', clean_system_status_for_json(system_status))
    logger.info("Client connected to monitoring dashboard")

@socketio.on('request_status')
def handle_status_request():
    """Handle status request from client"""
    emit('system_update', clean_system_status_for_json(system_status))

if __name__ == '__main__':
    # Initialize autonomous system in background thread
    init_thread = threading.Thread(target=initialize_autonomous_system, daemon=True)
    init_thread.start()

    # Get port from environment (Render sets PORT)
    port = int(os.environ.get('PORT', 5000))

    # Run the Flask-SocketIO app
    logger.info(f"🚀 Starting XMRT-Ecosystem Autonomous Learning System on port {port}")
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
