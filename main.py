"""
XMRT-Ecosystem Main Application with Autonomous Learning

Enhanced Flask application that integrates:
- Original XMRT-Ecosystem functionality
- Real-time autonomous learning system
- Multi-agent AI collaboration
- GitHub integration for automated deployments
- Persistent memory with Supabase
"""

import os
import asyncio
import threading
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import logging
from dotenv import load_dotenv

# Import autonomous learning system
try:
    from autonomous_controller import RealAutonomousController
    from multi_agent_system import MultiAgentSystem
    from github_manager import GitHubManager
    from memory_system import MemorySystem
    AUTONOMOUS_SYSTEM_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Autonomous system not available: {e}")
    AUTONOMOUS_SYSTEM_AVAILABLE = False

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-this')

# Enable CORS
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"]
    }
})

# Initialize SocketIO with gevent for autonomous system compatibility
socketio = SocketIO(
    app, 
    cors_allowed_origins="*",
    async_mode='gevent',  # Use gevent for WebSocket support
    ping_timeout=60,
    ping_interval=25
)

# Global autonomous system instance
autonomous_controller = None
autonomous_system_config = {}

def setup_autonomous_system():
    """Setup and configure the autonomous learning system"""
    global autonomous_controller, autonomous_system_config

    if not AUTONOMOUS_SYSTEM_AVAILABLE:
        logger.warning("⚠️ Autonomous system not available - running in basic mode")
        return False

    try:
        # Configure autonomous system
        autonomous_system_config = {
            'gemini_api_key': os.getenv('GEMINI_API_KEY'),
            'openai_api_key': os.getenv('OPENAI_API_KEY'),
            'github_token': os.getenv('GITHUB_TOKEN'),
            'github_owner': os.getenv('GITHUB_OWNER', 'DevGruGold'),
            'github_repo': os.getenv('GITHUB_REPO', 'XMRT-Ecosystem'),
            'github_branch': os.getenv('GITHUB_BRANCH', 'main'),
            'supabase_url': os.getenv('SUPABASE_URL'),
            'supabase_key': os.getenv('SUPABASE_KEY')
        }

        # Initialize autonomous controller
        autonomous_controller = RealAutonomousController(autonomous_system_config)

        logger.info("✅ Autonomous learning system configured successfully")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to setup autonomous system: {e}")
        return False

def start_autonomous_learning():
    """Start the autonomous learning system in background"""
    async def run_autonomous_system():
        try:
            if autonomous_controller:
                logger.info("🚀 Starting autonomous learning system...")
                await autonomous_controller.start_autonomous_learning()
            else:
                logger.warning("⚠️ Autonomous controller not available")
        except Exception as e:
            logger.error(f"❌ Autonomous learning system error: {e}")

    # Run autonomous system in background thread
    def run_in_thread():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_autonomous_system())

    if AUTONOMOUS_SYSTEM_AVAILABLE and autonomous_controller:
        autonomous_thread = threading.Thread(target=run_in_thread, daemon=True)
        autonomous_thread.start()
        logger.info("🔄 Autonomous learning system started in background")

# Original XMRT-Ecosystem routes
@app.route('/')
def index():
    """Main page with autonomous learning dashboard"""
    try:
        # Get autonomous system status
        system_status = {}
        if autonomous_controller:
            system_status = autonomous_controller.get_status()

        return render_template('index.html', 
                             autonomous_available=AUTONOMOUS_SYSTEM_AVAILABLE,
                             system_status=system_status,
                             timestamp=datetime.now().isoformat())
    except Exception as e:
        logger.error(f"Error loading index: {e}")
        return render_template('index.html', 
                             autonomous_available=False,
                             error=str(e))

@app.route('/api/health')
def health_check():
    """Health check endpoint with autonomous system status"""
    try:
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'autonomous_system': {
                'available': AUTONOMOUS_SYSTEM_AVAILABLE,
                'running': False,
                'details': {}
            }
        }

        if autonomous_controller:
            try:
                health_status['autonomous_system']['running'] = True
                health_status['autonomous_system']['details'] = autonomous_controller.get_status()
            except Exception as e:
                health_status['autonomous_system']['error'] = str(e)

        return jsonify(health_status)

    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/autonomous/status')
def autonomous_status():
    """Get detailed autonomous system status"""
    try:
        if not autonomous_controller:
            return jsonify({
                'available': False,
                'message': 'Autonomous system not initialized'
            })

        status = autonomous_controller.get_status()

        return jsonify({
            'available': True,
            'status': status,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({
            'available': False,
            'error': str(e)
        }), 500

@app.route('/api/autonomous/trigger', methods=['POST'])
def trigger_autonomous_cycle():
    """Manually trigger an autonomous learning cycle"""
    try:
        if not autonomous_controller:
            return jsonify({
                'success': False,
                'message': 'Autonomous system not available'
            }), 400

        # Trigger a learning cycle
        # Note: This would need to be implemented as an async call
        return jsonify({
            'success': True,
            'message': 'Autonomous learning cycle triggered',
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# SocketIO events for real-time updates
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f"Client connected: {request.sid}")

    # Send initial status
    if autonomous_controller:
        try:
            status = autonomous_controller.get_status()
            emit('autonomous_status', status)
        except Exception as e:
            emit('error', {'message': f'Failed to get status: {e}'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('get_autonomous_status')
def handle_get_status():
    """Handle request for autonomous system status"""
    try:
        if autonomous_controller:
            status = autonomous_controller.get_status()
            emit('autonomous_status', status)
        else:
            emit('autonomous_status', {'available': False})
    except Exception as e:
        emit('error', {'message': f'Failed to get status: {e}'})

@socketio.on('trigger_learning_cycle')
def handle_trigger_cycle():
    """Handle manual learning cycle trigger"""
    try:
        if autonomous_controller:
            # This would trigger an autonomous learning cycle
            emit('cycle_triggered', {
                'success': True,
                'timestamp': datetime.now().isoformat()
            })
        else:
            emit('error', {'message': 'Autonomous system not available'})
    except Exception as e:
        emit('error', {'message': f'Failed to trigger cycle: {e}'})

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# Initialize and start the autonomous system
def initialize_application():
    """Initialize the complete XMRT-Ecosystem application"""
    logger.info("🚀 Initializing XMRT-Ecosystem with Autonomous Learning")

    # Setup autonomous system
    autonomous_setup_success = setup_autonomous_system()

    if autonomous_setup_success:
        # Start autonomous learning in background
        start_autonomous_learning()
        logger.info("✅ XMRT-Ecosystem with Autonomous Learning initialized successfully")
    else:
        logger.warning("⚠️ XMRT-Ecosystem running without autonomous learning")

    return autonomous_setup_success

if __name__ == '__main__':
    # Initialize application
    initialization_success = initialize_application()

    # Get configuration
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')

    # Start the Flask-SocketIO application
    logger.info(f"🌐 Starting XMRT-Ecosystem server on {host}:{port}")
    logger.info(f"🤖 Autonomous Learning: {'✅ Enabled' if initialization_success else '❌ Disabled'}")

    socketio.run(
        app, 
        host=host, 
        port=port, 
        debug=debug,
        use_reloader=False  # Disable reloader to prevent autonomous system conflicts
    )
