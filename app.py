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
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'xmrt-ecosystem-secret-key-2024')

# Initialize SocketIO with gevent support for Render
socketio = SocketIO(app, 
                   cors_allowed_origins="*",
                   async_mode='gevent',
                   logger=True, 
                   engineio_logger=True)

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
<html>
<head>
    <title>XMRT-Ecosystem Autonomous Learning System</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                 color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        .status-card { background: white; padding: 20px; border-radius: 10px; 
                      box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .status-green { color: #28a745; font-weight: bold; }
        .status-red { color: #dc3545; font-weight: bold; }
        .status-yellow { color: #ffc107; font-weight: bold; }
        .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; }
        .metric { background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; }
        .log-container { background: #1e1e1e; color: #00ff00; padding: 15px; 
                        border-radius: 8px; height: 300px; overflow-y: auto; font-family: monospace; }
        .refresh-btn { background: #007bff; color: white; padding: 10px 20px; 
                      border: none; border-radius: 5px; cursor: pointer; }
        .refresh-btn:hover { background: #0056b3; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 XMRT-Ecosystem Autonomous Learning System</h1>
            <p>Real-time monitoring of the autonomous AI agents continuously improving the XMRT ecosystem</p>
        </div>

        <div class="status-card">
            <h2>System Status</h2>
            <div class="metrics">
                <div class="metric">
                    <h3>System Status</h3>
                    <div id="system-status" class="status-yellow">Initializing...</div>
                </div>
                <div class="metric">
                    <h3>Learning Cycles</h3>
                    <div id="total-cycles">0</div>
                </div>
                <div class="metric">
                    <h3>Repositories Managed</h3>
                    <div id="repos-managed">0</div>
                </div>
                <div class="metric">
                    <h3>Last Activity</h3>
                    <div id="last-activity">Never</div>
                </div>
            </div>
        </div>

        <div class="status-card">
            <h2>Live System Log</h2>
            <button class="refresh-btn" onclick="refreshStatus()">Refresh Status</button>
            <div id="system-log" class="log-container">
                <div>🚀 XMRT Autonomous Learning System starting...</div>
                <div>📡 Connecting to real-time updates...</div>
            </div>
        </div>

        <div class="status-card">
            <h2>About This System</h2>
            <ul>
                <li><strong>Hourly Learning Cycles:</strong> System learns and improves every hour</li>
                <li><strong>Multi-Agent Collaboration:</strong> 4 AI agents work together via SocketIO</li>
                <li><strong>Real GitHub Integration:</strong> Actually creates commits and repositories</li>
                <li><strong>Persistent Memory:</strong> Learns from past actions using Supabase</li>
                <li><strong>Self-Evolution:</strong> Continuously improves its own code</li>
            </ul>
        </div>
    </div>

    <script>
        const socket = io();

        socket.on('system_update', function(data) {
            updateSystemStatus(data);
            logMessage(data.message || 'System update received');
        });

        socket.on('learning_cycle', function(data) {
            logMessage(`🔄 Learning cycle ${data.cycle}: ${data.phase}`);
            document.getElementById('total-cycles').textContent = data.cycle;
        });

        function updateSystemStatus(data) {
            const statusEl = document.getElementById('system-status');
            const status = data.status || 'unknown';

            statusEl.textContent = status.charAt(0).toUpperCase() + status.slice(1);
            statusEl.className = status === 'running' ? 'status-green' : 
                               status === 'error' ? 'status-red' : 'status-yellow';

            if (data.total_cycles) {
                document.getElementById('total-cycles').textContent = data.total_cycles;
            }
            if (data.repositories_managed) {
                document.getElementById('repos-managed').textContent = data.repositories_managed;
            }
            if (data.last_cycle) {
                document.getElementById('last-activity').textContent = new Date(data.last_cycle).toLocaleString();
            }
        }

        function logMessage(message) {
            const log = document.getElementById('system-log');
            const timestamp = new Date().toLocaleTimeString();
            const logEntry = document.createElement('div');
            logEntry.innerHTML = `[${timestamp}] ${message}`;
            log.appendChild(logEntry);
            log.scrollTop = log.scrollHeight;
        }

        function refreshStatus() {
            fetch('/status')
                .then(response => response.json())
                .then(data => updateSystemStatus(data))
                .catch(error => logMessage('❌ Error fetching status: ' + error));
        }

        // Initial status fetch
        setTimeout(refreshStatus, 1000);
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

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    emit('system_update', system_status)
    logger.info("Client connected to monitoring dashboard")

@socketio.on('request_status')
def handle_status_request():
    """Handle status request from client"""
    emit('system_update', system_status)

if __name__ == '__main__':
    # Initialize autonomous system in background thread
    init_thread = threading.Thread(target=initialize_autonomous_system, daemon=True)
    init_thread.start()

    # Get port from environment (Render sets PORT)
    port = int(os.environ.get('PORT', 5000))

    # Run the Flask-SocketIO app
    logger.info(f"🚀 Starting XMRT-Ecosystem Autonomous Learning System on port {port}")
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
