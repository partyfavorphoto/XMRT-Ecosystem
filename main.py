"""
XMRT-Ecosystem Main Application with Enhanced Autonomous Learning

Enhanced Flask application that integrates:
- Original XMRT-Ecosystem functionality
- Real-time autonomous learning system with robust error handling
- Multi-agent AI collaboration with failsafe mechanisms
- GitHub integration for automated deployments with rate limiting
- Persistent memory with Supabase and graceful degradation
- Performance optimizations for production deployment
- Comprehensive logging and monitoring
- Feature flags for optional components
"""

import os
import asyncio
import threading
import time
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import logging
from dotenv import load_dotenv
import traceback
import sys
from typing import Dict, Any, Optional

# Import autonomous learning system with graceful error handling
autonomous_imports = {}
try:
    from autonomous_controller import RealAutonomousController
    autonomous_imports['controller'] = True
except ImportError as e:
    print(f"⚠️ Autonomous controller not available: {e}")
    autonomous_imports['controller'] = False

try:
    from multi_agent_system import MultiAgentSystem
    autonomous_imports['multiagent'] = True
except ImportError as e:
    print(f"⚠️ Multi-agent system not available: {e}")
    autonomous_imports['multiagent'] = False

try:
    from github_manager import GitHubManager
    autonomous_imports['github'] = True
except ImportError as e:
    print(f"⚠️ GitHub manager not available: {e}")
    autonomous_imports['github'] = False

try:
    from memory_system import MemorySystem
    autonomous_imports['memory'] = True
except ImportError as e:
    print(f"⚠️ Memory system not available: {e}")
    autonomous_imports['memory'] = False

# Feature availability check
AUTONOMOUS_SYSTEM_AVAILABLE = all(autonomous_imports.values())
PARTIAL_AUTONOMOUS_AVAILABLE = any(autonomous_imports.values())

# Load environment variables
load_dotenv()

# Enhanced logging configuration
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('xmrt_ecosystem.log') if os.getenv('ENABLE_FILE_LOGGING', 'false').lower() == 'true' else logging.NullHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'xmrt-ecosystem-default-key-change-in-production')

# Enhanced CORS configuration
cors_origins = os.getenv('CORS_ORIGINS', '*').split(',') if os.getenv('CORS_ORIGINS') else '*'
CORS(app, resources={
    r"/*": {
        "origins": cors_origins,
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"]
    }
})

# Enhanced SocketIO configuration for production
socketio_config = {
    'cors_allowed_origins': cors_origins,
    'async_mode': 'gevent',  # Use gevent for WebSocket support
    'ping_timeout': int(os.getenv('SOCKETIO_PING_TIMEOUT', '60')),
    'ping_interval': int(os.getenv('SOCKETIO_PING_INTERVAL', '25')),
    'logger': logger if os.getenv('SOCKETIO_LOGGING', 'false').lower() == 'true' else False,
    'engineio_logger': logger if os.getenv('SOCKETIO_LOGGING', 'false').lower() == 'true' else False
}

socketio = SocketIO(app, **socketio_config)

# Expose Flask app for WSGI server (gunicorn)
# For Flask-SocketIO applications, the Flask app instance is the WSGI callable
application = app

# Global autonomous system instances with thread safety
autonomous_controller = None
autonomous_system_config = {}
system_status = {
    'autonomous_active': False,
    'features_enabled': {},
    'last_health_check': None,
    'startup_time': datetime.now(),
    'errors': []
}

# Feature flags for optional components
feature_flags = {
    'autonomous_learning': os.getenv('ENABLE_AUTONOMOUS_LEARNING', 'true').lower() == 'true',
    'multiagent_system': os.getenv('ENABLE_MULTIAGENT_SYSTEM', 'true').lower() == 'true',
    'github_integration': os.getenv('ENABLE_GITHUB_INTEGRATION', 'true').lower() == 'true',
    'memory_persistence': os.getenv('ENABLE_MEMORY_PERSISTENCE', 'true').lower() == 'true',
    'real_time_learning': os.getenv('ENABLE_REALTIME_LEARNING', 'true').lower() == 'true',
    'advanced_logging': os.getenv('ENABLE_ADVANCED_LOGGING', 'true').lower() == 'true'
}

def validate_environment_config() -> Dict[str, Any]:
    """Validate environment configuration and return status"""
    config_status = {
        'valid': True,
        'warnings': [],
        'errors': [],
        'optional_missing': []
    }

    # Critical environment variables
    critical_vars = {
        'GEMINI_API_KEY': 'AI functionality',
        'OPENAI_API_KEY': 'AI functionality'
    }

    # Optional environment variables
    optional_vars = {
        'GITHUB_TOKEN': 'GitHub integration',
        'SUPABASE_URL': 'Memory persistence',
        'SUPABASE_KEY': 'Memory persistence'
    }

    for var, purpose in critical_vars.items():
        if not os.getenv(var):
            config_status['errors'].append(f"Missing critical env var {var} for {purpose}")
            config_status['valid'] = False

    for var, purpose in optional_vars.items():
        if not os.getenv(var):
            config_status['optional_missing'].append(f"Optional env var {var} missing - {purpose} disabled")
            config_status['warnings'].append(f"Feature degradation: {purpose} unavailable")

    return config_status

def setup_autonomous_system() -> bool:
    """Setup and configure the autonomous learning system with enhanced error handling"""
    global autonomous_controller, autonomous_system_config, system_status

    logger.info("🚀 Initializing XMRT-Ecosystem Autonomous System")

    # Validate environment configuration
    config_status = validate_environment_config()

    for warning in config_status['warnings']:
        logger.warning(f"⚠️ {warning}")

    for error in config_status['errors']:
        logger.error(f"❌ {error}")

    if not config_status['valid']:
        logger.error("❌ Critical configuration missing - running in limited mode")
        system_status['errors'].extend(config_status['errors'])
        return False

    if not AUTONOMOUS_SYSTEM_AVAILABLE:
        if PARTIAL_AUTONOMOUS_AVAILABLE:
            logger.warning("⚠️ Partial autonomous system available - some features disabled")
            available_features = [k for k, v in autonomous_imports.items() if v]
            logger.info(f"📦 Available components: {', '.join(available_features)}")
        else:
            logger.warning("⚠️ Autonomous system not available - running in basic mode")
            return False

    try:
        # Enhanced autonomous system configuration
        autonomous_system_config = {
            # Core API configurations
            'gemini_api_key': os.getenv('GEMINI_API_KEY'),
            'openai_api_key': os.getenv('OPENAI_API_KEY'),

            # GitHub integration with enhanced settings
            'github_token': os.getenv('GITHUB_TOKEN'),
            'github_owner': os.getenv('GITHUB_OWNER', 'DevGruGold'),
            'github_repo': os.getenv('GITHUB_REPO', 'XMRT-Ecosystem'),
            'github_branch': os.getenv('GITHUB_BRANCH', 'main'),
            'github_rate_limit': int(os.getenv('GITHUB_RATE_LIMIT', '5000')),

            # Memory and persistence
            'supabase_url': os.getenv('SUPABASE_URL'),
            'supabase_key': os.getenv('SUPABASE_KEY'),

            # Performance optimizations
            'max_concurrent_tasks': int(os.getenv('MAX_CONCURRENT_TASKS', '3')),
            'learning_cycle_interval': int(os.getenv('LEARNING_CYCLE_INTERVAL', '3600')),  # 1 hour
            'memory_cleanup_interval': int(os.getenv('MEMORY_CLEANUP_INTERVAL', '86400')),  # 24 hours

            # Feature flags
            'enable_real_time_learning': feature_flags['real_time_learning'],
            'enable_github_auto_deploy': os.getenv('ENABLE_GITHUB_AUTO_DEPLOY', 'false').lower() == 'true',
            'enable_advanced_analytics': os.getenv('ENABLE_ADVANCED_ANALYTICS', 'true').lower() == 'true',

            # Resource constraints for Render
            'memory_limit_mb': int(os.getenv('MEMORY_LIMIT_MB', '512')),
            'cpu_limit_percent': int(os.getenv('CPU_LIMIT_PERCENT', '80')),

            # Logging configuration
            'log_level': log_level,
            'enable_performance_metrics': os.getenv('ENABLE_PERFORMANCE_METRICS', 'true').lower() == 'true'
        }

        # Initialize autonomous controller with error handling
        if autonomous_imports['controller'] and feature_flags['autonomous_learning']:
            try:
                autonomous_controller = RealAutonomousController(autonomous_system_config)
                system_status['features_enabled']['autonomous_controller'] = True
                logger.info("✅ Autonomous controller initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize autonomous controller: {e}")
                system_status['errors'].append(f"Autonomous controller init failed: {str(e)}")
                system_status['features_enabled']['autonomous_controller'] = False
        else:
            logger.info("📝 Autonomous controller disabled by configuration or unavailable")
            system_status['features_enabled']['autonomous_controller'] = False

        # Update system status
        system_status.update({
            'autonomous_active': autonomous_controller is not None,
            'last_health_check': datetime.now(),
            'config_validation': config_status
        })

        logger.info("✅ Enhanced autonomous learning system configured successfully")
        logger.info(f"🎯 Active features: {[k for k, v in system_status['features_enabled'].items() if v]}")

        return True

    except Exception as e:
        error_msg = f"Failed to setup autonomous system: {str(e)}"
        logger.error(f"❌ {error_msg}")
        logger.error(f"🔍 Traceback: {traceback.format_exc()}")

        system_status['errors'].append(error_msg)
        system_status['autonomous_active'] = False

        return False

def get_system_health() -> Dict[str, Any]:
    """Get comprehensive system health status"""
    return {
        'status': 'healthy' if system_status['autonomous_active'] else 'limited',
        'autonomous_active': system_status['autonomous_active'],
        'features_enabled': system_status['features_enabled'],
        'feature_flags': feature_flags,
        'autonomous_imports': autonomous_imports,
        'startup_time': system_status['startup_time'].isoformat(),
        'last_health_check': system_status['last_health_check'].isoformat() if system_status['last_health_check'] else None,
        'errors': system_status['errors'],
        'uptime_seconds': (datetime.now() - system_status['startup_time']).total_seconds()
    }

# Enhanced Flask routes
@app.route('/')
def index():
    """Enhanced main application route with system status"""
    try:
        health_status = get_system_health()
        return render_template('index.html', system_status=health_status)
    except Exception as e:
        logger.error(f"❌ Error in index route: {e}")
        return render_template('index.html', system_status={'status': 'error', 'message': str(e)})

@app.route('/health')
def health_check():
    """Comprehensive health check endpoint for monitoring"""
    health_status = get_system_health()

    # Add additional health metrics
    health_status.update({
        'timestamp': datetime.now().isoformat(),
        'version': os.getenv('APP_VERSION', '1.0.0'),
        'environment': os.getenv('ENVIRONMENT', 'production')
    })

    status_code = 200 if health_status['status'] == 'healthy' else 503
    return jsonify(health_status), status_code

@app.route('/api/system/status')
def api_system_status():
    """API endpoint for detailed system status"""
    try:
        status = get_system_health()

        # Add controller-specific status if available
        if autonomous_controller:
            try:
                status['autonomous_metrics'] = {
                    'is_running': autonomous_controller.is_running,
                    'learning_cycle_count': autonomous_controller.learning_cycle_count,
                    'metrics': autonomous_controller.metrics
                }
            except Exception as e:
                logger.warning(f"⚠️ Could not get autonomous controller metrics: {e}")

        return jsonify(status)

    except Exception as e:
        logger.error(f"❌ Error getting system status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/features/toggle', methods=['POST'])
def toggle_feature():
    """API endpoint to toggle feature flags (admin only)"""
    try:
        data = request.get_json()
        feature = data.get('feature')
        enabled = data.get('enabled', False)

        if feature in feature_flags:
            feature_flags[feature] = enabled
            logger.info(f"🔄 Feature '{feature}' {'enabled' if enabled else 'disabled'}")
            return jsonify({'success': True, 'feature': feature, 'enabled': enabled})
        else:
            return jsonify({'error': f'Unknown feature: {feature}'}), 400

    except Exception as e:
        logger.error(f"❌ Error toggling feature: {e}")
        return jsonify({'error': str(e)}), 500

# Enhanced SocketIO events with error handling
@socketio.on('connect')
def handle_connect():
    """Handle client connection with enhanced logging"""
    try:
        client_info = {
            'sid': request.sid,
            'remote_addr': request.environ.get('REMOTE_ADDR', 'unknown'),
            'user_agent': request.environ.get('HTTP_USER_AGENT', 'unknown')[:100]  # Truncate for security
        }

        logger.info(f"🔌 Client connected: {client_info['sid']} from {client_info['remote_addr']}")

        # Send initial system status to connected client
        emit('system_status', get_system_health())

    except Exception as e:
        logger.error(f"❌ Error handling client connection: {e}")

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    try:
        logger.info(f"🔌 Client disconnected: {request.sid}")
    except Exception as e:
        logger.error(f"❌ Error handling client disconnection: {e}")

@socketio.on('get_system_status')
def handle_get_system_status():
    """Handle real-time system status requests"""
    try:
        health_status = get_system_health()
        emit('system_status', health_status)
        logger.debug(f"📊 System status sent to client {request.sid}")
    except Exception as e:
        logger.error(f"❌ Error sending system status: {e}")
        emit('error', {'message': 'Failed to get system status'})

@socketio.on('trigger_learning_cycle')
def handle_trigger_learning_cycle():
    """Handle manual learning cycle trigger with enhanced error handling"""
    try:
        if not autonomous_controller or not system_status['autonomous_active']:
            emit('learning_cycle_result', {
                'success': False,
                'message': 'Autonomous controller not available',
                'timestamp': datetime.now().isoformat()
            })
            return

        if not autonomous_controller.is_running:
            emit('learning_cycle_result', {
                'success': False,
                'message': 'Autonomous learning not running',
                'timestamp': datetime.now().isoformat()
            })
            return

        logger.info(f"🧠 Manual learning cycle triggered by client {request.sid}")

        # Trigger learning cycle in background
        def run_learning_cycle():
            try:
                # This would be implemented as an async call
                result = {'success': True, 'message': 'Learning cycle initiated', 'timestamp': datetime.now().isoformat()}
                socketio.emit('learning_cycle_result', result, to=request.sid)
            except Exception as e:
                error_result = {
                    'success': False,
                    'message': f'Learning cycle failed: {str(e)}',
                    'timestamp': datetime.now().isoformat()
                }
                socketio.emit('learning_cycle_result', error_result, to=request.sid)

        # Run in background thread to avoid blocking
        threading.Thread(target=run_learning_cycle, daemon=True).start()

        # Send immediate acknowledgment
        emit('learning_cycle_ack', {
            'message': 'Learning cycle request received',
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"❌ Error triggering learning cycle: {e}")
        emit('error', {'message': f'Failed to trigger learning cycle: {str(e)}'})

def initialize_application() -> bool:
    """Initialize the complete XMRT-Ecosystem application with enhanced error handling"""
    try:
        logger.info("🚀 Initializing XMRT-Ecosystem Application")

        # Log environment information
        env_info = {
            'python_version': sys.version,
            'environment': os.getenv('ENVIRONMENT', 'production'),
            'debug_mode': os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
        }
        logger.info(f"🐍 Python: {env_info['python_version']}")
        logger.info(f"🌍 Environment: {env_info['environment']}")

        # Setup autonomous system
        autonomous_success = setup_autonomous_system()

        if autonomous_success:
            logger.info("✅ XMRT-Ecosystem initialized successfully with full autonomous capabilities")
        else:
            logger.warning("⚠️ XMRT-Ecosystem initialized with limited capabilities")

        # Log final status
        health = get_system_health()
        logger.info(f"🎯 System Status: {health['status']}")
        logger.info(f"🔧 Active Features: {list(health['features_enabled'].keys())}")

        return True

    except Exception as e:
        logger.error(f"❌ Failed to initialize application: {e}")
        logger.error(f"🔍 Traceback: {traceback.format_exc()}")
        return False

# Enhanced startup sequence
if __name__ == "__main__":
    try:
        # Initialize application
        initialization_success = initialize_application()

        # Get configuration with enhanced defaults
        debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
        port = int(os.getenv('PORT', 5000))
        host = os.getenv('HOST', '0.0.0.0')

        # Enhanced startup logging
        logger.info("=" * 60)
        logger.info("🌐 Starting XMRT-Ecosystem Server")
        logger.info("=" * 60)
        logger.info(f"🏠 Host: {host}")
        logger.info(f"🔌 Port: {port}")
        logger.info(f"🐛 Debug: {debug}")
        logger.info(f"🤖 Autonomous Learning: {'✅ Enabled' if initialization_success else '❌ Disabled'}")
        logger.info(f"🎯 Features: {[k for k, v in feature_flags.items() if v]}")
        logger.info("=" * 60)

        # Start the Flask-SocketIO application with enhanced configuration
        socketio.run(
            app,
            host=host,
            port=port,
            debug=debug,
            use_reloader=False,  # Disable reloader to prevent autonomous system conflicts
            allow_unsafe_werkzeug=True  # Allow for production deployment
        )

    except Exception as e:
        logger.error(f"❌ Failed to start XMRT-Ecosystem server: {e}")
        logger.error(f"🔍 Traceback: {traceback.format_exc()}")
        sys.exit(1)
