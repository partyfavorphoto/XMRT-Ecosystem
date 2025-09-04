"""
XMRT-Ecosystem Main Application - FULLY ACTIVATED
Enhanced Flask application integrating all advanced features:
- Real-time autonomous learning system (ACTIVATED)
- Multi-agent AI collaboration (ACTIVATED)
- GitHub integration for automated deployments (ACTIVATED)
- Persistent memory with Supabase (ACTIVATED)
- Advanced analytics and monitoring (ACTIVATED)
"""

import os
import asyncio
import threading
import logging
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv

# Enhanced imports for full feature activation
try:
    from autonomous_controller import RealAutonomousController
    from multi_agent_system import MultiAgentSystem
    from github_manager import GitHubManager
    from memory_system import MemorySystem
    AUTONOMOUS_SYSTEM_AVAILABLE = True
    print("✅ All autonomous systems loaded successfully")
except ImportError as e:
    print(f"⚠️ Some autonomous system components not available: {e}")
    AUTONOMOUS_SYSTEM_AVAILABLE = False

# Load environment variables
load_dotenv()

# Enhanced logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('xmrt_ecosystem.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app with enhanced configuration
app = Flask(__name__)
app.config.update({
    'SECRET_KEY': os.getenv('SECRET_KEY', 'xmrt-ecosystem-secret-key-2024'),
    'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 16MB max file upload
    'UPLOAD_FOLDER': os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads'),
    'AUTONOMOUS_LEARNING_ENABLED': os.getenv('AUTONOMOUS_LEARNING_ENABLED', 'true').lower() == 'true',
    'MULTI_AGENT_ENABLED': os.getenv('MULTI_AGENT_ENABLED', 'true').lower() == 'true',
    'GITHUB_INTEGRATION_ENABLED': os.getenv('GITHUB_INTEGRATION_ENABLED', 'true').lower() == 'true',
    'MEMORY_SYSTEM_ENABLED': os.getenv('MEMORY_SYSTEM_ENABLED', 'true').lower() == 'true'
})

# Enhanced CORS configuration
CORS(app, resources={
    r"/*": {
        "origins": ["*"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With", "X-Agent-ID"]
    }
})

# Initialize SocketIO with enhanced configuration
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='gevent',
    ping_timeout=60,
    ping_interval=25,
    max_http_buffer_size=1e8,  # 100MB for large data transfers
    logger=True,
    engineio_logger=True
)

# WSGI application - This is the correct WSGI callable for Gunicorn
application = app

# Global system instances - will be initialized based on environment configuration
autonomous_controller = None
multi_agent_system = None
github_manager = None
memory_system = None
system_stats = {
    'start_time': datetime.utcnow(),
    'requests_processed': 0,
    'learning_cycles_completed': 0,
    'agents_active': 0,
    'github_operations': 0,
    'memory_operations': 0
}

def create_upload_directory():
    """Ensure upload directory exists"""
    upload_dir = app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
        logger.info(f"Created upload directory: {upload_dir}")

def initialize_autonomous_systems():
    """Initialize all autonomous systems based on environment configuration"""
    global autonomous_controller, multi_agent_system, github_manager, memory_system

    if not AUTONOMOUS_SYSTEM_AVAILABLE:
        logger.warning("⚠️ Autonomous system components not available - running in basic mode")
        return False

    initialization_success = True

    try:
        # Initialize Memory System first (required by other systems)
        if app.config['MEMORY_SYSTEM_ENABLED']:
            logger.info("🧠 Initializing Memory System...")
            memory_system = MemorySystem({
                'supabase_url': os.getenv('SUPABASE_URL'),
                'supabase_key': os.getenv('SUPABASE_KEY'),
                'memory_retention_days': int(os.getenv('MEMORY_RETENTION_DAYS', '30')),
                'max_memory_entries': int(os.getenv('MAX_MEMORY_ENTRIES', '10000'))
            })
            if memory_system.initialize():
                logger.info("✅ Memory System initialized successfully")
                system_stats['memory_operations'] += 1
            else:
                logger.error("❌ Memory System initialization failed")
                initialization_success = False

        # Initialize GitHub Manager
        if app.config['GITHUB_INTEGRATION_ENABLED']:
            logger.info("🐙 Initializing GitHub Manager...")
            github_manager = GitHubManager({
                'github_token': os.getenv('GITHUB_TOKEN'),
                'github_owner': os.getenv('GITHUB_OWNER', 'DevGruGold'),
                'github_repo': os.getenv('GITHUB_REPO', 'XMRT-Ecosystem'),
                'webhook_secret': os.getenv('GITHUB_WEBHOOK_SECRET'),
                'auto_deploy': os.getenv('AUTO_DEPLOY', 'true').lower() == 'true'
            })
            if github_manager.initialize():
                logger.info("✅ GitHub Manager initialized successfully")
                system_stats['github_operations'] += 1
            else:
                logger.error("❌ GitHub Manager initialization failed")
                initialization_success = False

        # Initialize Multi-Agent System
        if app.config['MULTI_AGENT_ENABLED']:
            logger.info("🤖 Initializing Multi-Agent System...")
            multi_agent_system = MultiAgentSystem({
                'openai_api_key': os.getenv('OPENAI_API_KEY'),
                'gemini_api_key': os.getenv('GEMINI_API_KEY'),
                'anthropic_api_key': os.getenv('ANTHROPIC_API_KEY'),
                'max_agents': int(os.getenv('MAX_AGENTS', '5')),
                'agent_coordination_enabled': True,
                'memory_system': memory_system
            })
            if multi_agent_system.initialize():
                logger.info("✅ Multi-Agent System initialized successfully")
                system_stats['agents_active'] = multi_agent_system.get_active_agent_count()
            else:
                logger.error("❌ Multi-Agent System initialization failed")
                initialization_success = False

        # Initialize Autonomous Controller (orchestrates everything)
        if app.config['AUTONOMOUS_LEARNING_ENABLED']:
            logger.info("🧭 Initializing Autonomous Controller...")
            autonomous_controller = RealAutonomousController({
                'learning_rate': float(os.getenv('LEARNING_RATE', '0.1')),
                'adaptation_threshold': float(os.getenv('ADAPTATION_THRESHOLD', '0.8')),
                'memory_system': memory_system,
                'multi_agent_system': multi_agent_system,
                'github_manager': github_manager,
                'auto_improvement': os.getenv('AUTO_IMPROVEMENT', 'true').lower() == 'true'
            })
            if autonomous_controller.initialize():
                logger.info("✅ Autonomous Controller initialized successfully")
                # Start autonomous learning in background
                autonomous_controller.start_autonomous_cycle()
            else:
                logger.error("❌ Autonomous Controller initialization failed")
                initialization_success = False

        return initialization_success

    except Exception as e:
        logger.error(f"❌ Critical error during system initialization: {e}")
        return False

# Enhanced Flask Routes

@app.route('/')
def index():
    """Enhanced main dashboard with system status"""
    system_stats['requests_processed'] += 1

    status = {
        'autonomous_learning': autonomous_controller is not None,
        'multi_agent_system': multi_agent_system is not None,
        'github_integration': github_manager is not None,
        'memory_system': memory_system is not None,
        'stats': system_stats
    }

    return render_template('index.html', system_status=status)

@app.route('/api/status')
def api_status():
    """Comprehensive system status API"""
    system_stats['requests_processed'] += 1

    return jsonify({
        'status': 'active',
        'timestamp': datetime.utcnow().isoformat(),
        'systems': {
            'autonomous_learning': {
                'enabled': autonomous_controller is not None,
                'cycles_completed': system_stats['learning_cycles_completed']
            },
            'multi_agent': {
                'enabled': multi_agent_system is not None,
                'active_agents': system_stats['agents_active']
            },
            'github_integration': {
                'enabled': github_manager is not None,
                'operations': system_stats['github_operations']
            },
            'memory_system': {
                'enabled': memory_system is not None,
                'operations': system_stats['memory_operations']
            }
        },
        'performance': {
            'uptime_seconds': (datetime.utcnow() - system_stats['start_time']).total_seconds(),
            'requests_processed': system_stats['requests_processed']
        }
    })

@app.route('/api/learning/trigger', methods=['POST'])
def trigger_learning_cycle():
    """Manually trigger a learning cycle"""
    if autonomous_controller:
        try:
            result = autonomous_controller.trigger_manual_cycle()
            system_stats['learning_cycles_completed'] += 1
            return jsonify({
                'success': True,
                'result': result,
                'timestamp': datetime.utcnow().isoformat()
            })
        except Exception as e:
            logger.error(f"Learning cycle error: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    else:
        return jsonify({'success': False, 'error': 'Autonomous learning not available'}), 503

@app.route('/api/agents/status')
def agent_status():
    """Get multi-agent system status"""
    if multi_agent_system:
        return jsonify(multi_agent_system.get_system_status())
    else:
        return jsonify({'error': 'Multi-agent system not available'}), 503

@app.route('/api/github/sync', methods=['POST'])
def github_sync():
    """Trigger GitHub synchronization"""
    if github_manager:
        try:
            result = github_manager.sync_repository()
            system_stats['github_operations'] += 1
            return jsonify({
                'success': True,
                'result': result,
                'timestamp': datetime.utcnow().isoformat()
            })
        except Exception as e:
            logger.error(f"GitHub sync error: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    else:
        return jsonify({'success': False, 'error': 'GitHub integration not available'}), 503

@app.route('/api/memory/query', methods=['POST'])
def memory_query():
    """Query the memory system"""
    if memory_system:
        try:
            query = request.json.get('query', '')
            results = memory_system.query_memories(query)
            system_stats['memory_operations'] += 1
            return jsonify({
                'success': True,
                'results': results,
                'timestamp': datetime.utcnow().isoformat()
            })
        except Exception as e:
            logger.error(f"Memory query error: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    else:
        return jsonify({'success': False, 'error': 'Memory system not available'}), 503

# Enhanced SocketIO Events

@socketio.on('connect')
def handle_connect():
    """Enhanced connection handler with system info"""
    system_stats['requests_processed'] += 1
    logger.info(f"Client connected: {request.sid}")

    # Send system status to new client
    emit('system_status', {
        'autonomous_learning': autonomous_controller is not None,
        'multi_agent_system': multi_agent_system is not None,
        'github_integration': github_manager is not None,
        'memory_system': memory_system is not None,
        'stats': system_stats
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Enhanced disconnect handler"""
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('get_system_metrics')
def handle_system_metrics():
    """Real-time system metrics"""
    metrics = {
        'timestamp': datetime.utcnow().isoformat(),
        'uptime': (datetime.utcnow() - system_stats['start_time']).total_seconds(),
        'requests_processed': system_stats['requests_processed'],
        'learning_cycles': system_stats['learning_cycles_completed'],
        'active_agents': system_stats['agents_active'],
        'github_operations': system_stats['github_operations'],
        'memory_operations': system_stats['memory_operations']
    }

    if autonomous_controller:
        metrics['autonomous_status'] = autonomous_controller.get_status()

    if multi_agent_system:
        metrics['agent_coordination'] = multi_agent_system.get_coordination_status()

    emit('system_metrics', metrics)

@socketio.on('trigger_autonomous_action')
def handle_autonomous_action(data):
    """Trigger specific autonomous actions via WebSocket"""
    action = data.get('action')
    parameters = data.get('parameters', {})

    try:
        if action == 'learning_cycle' and autonomous_controller:
            result = autonomous_controller.trigger_manual_cycle()
            system_stats['learning_cycles_completed'] += 1
            emit('action_result', {
                'action': action,
                'success': True,
                'result': result
            })

        elif action == 'spawn_agent' and multi_agent_system:
            agent_id = multi_agent_system.spawn_agent(parameters)
            system_stats['agents_active'] = multi_agent_system.get_active_agent_count()
            emit('action_result', {
                'action': action,
                'success': True,
                'agent_id': agent_id
            })

        elif action == 'github_analysis' and github_manager:
            result = github_manager.analyze_repository()
            system_stats['github_operations'] += 1
            emit('action_result', {
                'action': action,
                'success': True,
                'result': result
            })

        else:
            emit('action_result', {
                'action': action,
                'success': False,
                'error': f'Action {action} not supported or system not available'
            })

    except Exception as e:
        logger.error(f"Autonomous action error: {e}")
        emit('action_result', {
            'action': action,
            'success': False,
            'error': str(e)
        })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

# Background tasks
def background_system_monitor():
    """Background monitoring of system health"""
    while True:
        try:
            # Update system statistics
            if autonomous_controller:
                system_stats['learning_cycles_completed'] = autonomous_controller.get_cycle_count()

            if multi_agent_system:
                system_stats['agents_active'] = multi_agent_system.get_active_agent_count()

            # Emit real-time updates to connected clients
            socketio.emit('system_update', {
                'timestamp': datetime.utcnow().isoformat(),
                'stats': system_stats
            })

            # Sleep for 30 seconds
            socketio.sleep(30)

        except Exception as e:
            logger.error(f"Background monitor error: {e}")
            socketio.sleep(60)  # Wait longer on error

def initialize_application():
    """Complete application initialization"""
    logger.info("🚀 Starting XMRT-Ecosystem Enhanced Application...")

    # Create necessary directories
    create_upload_directory()

    # Initialize all systems
    systems_initialized = initialize_autonomous_systems()

    if systems_initialized:
        logger.info("✅ All systems initialized successfully")

        # Start background monitoring
        socketio.start_background_task(background_system_monitor)
        logger.info("📊 Background system monitoring started")

    else:
        logger.warning("⚠️ Some systems failed to initialize - running in degraded mode")

    return systems_initialized

if __name__ == '__main__':
    # Initialize the complete application
    initialization_success = initialize_application()

    # Get configuration from environment
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')

    # Enhanced startup logging
    logger.info("🌐 XMRT-Ecosystem Enhanced Server Configuration:")
    logger.info(f"  🌍 Host: {host}:{port}")
    logger.info(f"  🐛 Debug Mode: {debug}")
    logger.info(f"  🤖 Autonomous Learning: {'✅ Enabled' if initialization_success else '❌ Disabled'}")
    logger.info(f"  🧠 Memory System: {'✅ Active' if memory_system else '❌ Inactive'}")
    logger.info(f"  👥 Multi-Agent System: {'✅ Active' if multi_agent_system else '❌ Inactive'}")
    logger.info(f"  🐙 GitHub Integration: {'✅ Active' if github_manager else '❌ Inactive'}")

    # Start the enhanced Flask-SocketIO application
    socketio.run(
        app,
        host=host,
        port=port,
        debug=debug,
        use_reloader=False,  # Disable reloader to prevent conflicts
        allow_unsafe_werkzeug=True  # Allow in production
    )
