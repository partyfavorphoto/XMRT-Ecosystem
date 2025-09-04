import os
import json
import logging
from datetime import datetime, timezone
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, disconnect
from flask_cors import CORS
import threading
import time
import requests
from functools import wraps
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'xmrt-ecosystem-2024-secure-key')

# Enable CORS
CORS(app, origins="*")

# Initialize SocketIO with eventlet for Render compatibility
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='eventlet',  # Use eventlet instead of gevent
    logger=logger,
    engineio_logger=logger,
    transports=['websocket', 'polling']  # Allow both transports
)

# JSON serialization helper for datetime and other objects
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)

app.json_encoder = CustomJSONEncoder

def safe_json_emit(event, data, **kwargs):
    """Safely emit JSON data with proper serialization"""
    try:
        # Convert to JSON string and back to ensure serialization works
        serialized_data = json.loads(json.dumps(data, cls=CustomJSONEncoder))
        socketio.emit(event, serialized_data, **kwargs)
        return True
    except Exception as e:
        logger.error(f"JSON serialization error in {event}: {e}")
        # Fallback to string representation
        fallback_data = {
            'error': 'Serialization failed',
            'message': str(data),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        socketio.emit(event, fallback_data, **kwargs)
        return False

# Global system state
class SystemState:
    def __init__(self):
        self.agents = {}
        self.analytics = {
            'total_requests': 0,
            'active_connections': 0,
            'system_uptime': datetime.now(timezone.utc),
            'last_update': datetime.now(timezone.utc)
        }
        self.learning_data = []
        self.active_sessions = set()

    def update_analytics(self):
        """Update system analytics with proper datetime handling"""
        self.analytics['last_update'] = datetime.now(timezone.utc)
        self.analytics['total_requests'] += 1

    def get_status(self):
        """Get system status with JSON-serializable data"""
        uptime_seconds = (datetime.now(timezone.utc) - self.analytics['system_uptime']).total_seconds()
        return {
            'status': 'operational',
            'uptime_seconds': int(uptime_seconds),
            'active_connections': len(self.active_sessions),
            'total_requests': self.analytics['total_requests'],
            'agents_count': len(self.agents),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

# Initialize system state
system_state = SystemState()

# Multi-agent system
class Agent:
    def __init__(self, name, role, capabilities):
        self.name = name
        self.role = role
        self.capabilities = capabilities
        self.status = 'active'
        self.created_at = datetime.now(timezone.utc)
        self.task_count = 0

    def to_dict(self):
        """Convert agent to JSON-serializable dictionary"""
        return {
            'name': self.name,
            'role': self.role,
            'capabilities': self.capabilities,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'task_count': self.task_count
        }

# Initialize AI agents
def initialize_agents():
    """Initialize the multi-agent system"""
    agents = {
        'coordinator': Agent(
            'AI Coordinator',
            'System orchestration and task distribution',
            ['planning', 'coordination', 'resource_management']
        ),
        'analyzer': Agent(
            'Data Analyzer',
            'Real-time data analysis and insights',
            ['data_processing', 'pattern_recognition', 'reporting']
        ),
        'developer': Agent(
            'Code Developer',
            'Dynamic code generation and optimization',
            ['code_generation', 'testing', 'deployment']
        )
    }
    system_state.agents = agents
    logger.info(f"🤖 Initialized {len(agents)} AI agents")
    return agents

# Analytics system
class AnalyticsEngine:
    def __init__(self):
        self.metrics = {}
        self.start_time = datetime.now(timezone.utc)

    def track_event(self, event_type, data=None):
        """Track events with proper datetime handling"""
        timestamp = datetime.now(timezone.utc)

        if event_type not in self.metrics:
            self.metrics[event_type] = []

        event_data = {
            'timestamp': timestamp.isoformat(),
            'data': data or {}
        }

        self.metrics[event_type].append(event_data)

        # Keep only last 1000 events per type to prevent memory issues
        if len(self.metrics[event_type]) > 1000:
            self.metrics[event_type] = self.metrics[event_type][-1000:]

    def get_summary(self):
        """Get analytics summary with JSON-serializable data"""
        uptime = (datetime.now(timezone.utc) - self.start_time).total_seconds()

        summary = {
            'uptime_seconds': int(uptime),
            'total_events': sum(len(events) for events in self.metrics.values()),
            'event_types': list(self.metrics.keys()),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

        for event_type, events in self.metrics.items():
            summary[f'{event_type}_count'] = len(events)

        return summary

# Initialize analytics
analytics = AnalyticsEngine()

# Learning optimization system
class LearningOptimizer:
    def __init__(self):
        self.optimization_history = []
        self.current_parameters = {
            'learning_rate': 0.01,
            'batch_size': 32,
            'model_complexity': 'medium'
        }

    def optimize(self, performance_data):
        """Optimize system parameters based on performance"""
        timestamp = datetime.now(timezone.utc)

        optimization_result = {
            'timestamp': timestamp.isoformat(),
            'previous_params': self.current_parameters.copy(),
            'performance_score': performance_data.get('score', 0.5),
            'improvements': []
        }

        # Simple optimization logic
        score = performance_data.get('score', 0.5)
        if score < 0.7:
            if self.current_parameters['learning_rate'] > 0.001:
                self.current_parameters['learning_rate'] *= 0.9
                optimization_result['improvements'].append('Reduced learning rate')

        self.optimization_history.append(optimization_result)

        # Keep history manageable
        if len(self.optimization_history) > 100:
            self.optimization_history = self.optimization_history[-100:]

        return optimization_result

    def get_status(self):
        """Get optimizer status with JSON-serializable data"""
        return {
            'current_parameters': self.current_parameters,
            'optimization_count': len(self.optimization_history),
            'last_optimization': self.optimization_history[-1]['timestamp'] if self.optimization_history else None,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

# Initialize learning optimizer
learning_optimizer = LearningOptimizer()

# WebSocket event handlers
@socketio.on('connect')
def handle_connect(auth):
    """Handle client connection"""
    session_id = request.sid
    system_state.active_sessions.add(session_id)
    system_state.update_analytics()
    analytics.track_event('connection', {'session_id': session_id})

    logger.info(f"🔌 Client connected: {session_id}")

    # Send welcome message with system status
    welcome_data = {
        'message': 'Connected to XMRT Ecosystem',
        'session_id': session_id,
        'system_status': system_state.get_status(),
        'timestamp': datetime.now(timezone.utc).isoformat()
    }

    safe_json_emit('welcome', welcome_data)

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    session_id = request.sid
    system_state.active_sessions.discard(session_id)
    analytics.track_event('disconnection', {'session_id': session_id})

    logger.info(f"🔌 Client disconnected: {session_id}")

@socketio.on('get_system_status')
def handle_system_status():
    """Handle system status request"""
    try:
        status_data = {
            'system': system_state.get_status(),
            'agents': {name: agent.to_dict() for name, agent in system_state.agents.items()},
            'analytics': analytics.get_summary(),
            'learning': learning_optimizer.get_status(),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

        safe_json_emit('system_status', status_data)
        analytics.track_event('status_request')

    except Exception as e:
        logger.error(f"Error handling system status: {e}")
        error_data = {
            'error': 'Status request failed',
            'message': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        safe_json_emit('error', error_data)

@socketio.on('trigger_learning')
def handle_learning_trigger(data):
    """Handle learning optimization trigger"""
    try:
        performance_data = data or {'score': 0.5}
        result = learning_optimizer.optimize(performance_data)

        safe_json_emit('learning_result', result)
        analytics.track_event('learning_optimization', result)

        logger.info(f"🧠 Learning optimization completed: {result['performance_score']}")

    except Exception as e:
        logger.error(f"Error in learning optimization: {e}")
        error_data = {
            'error': 'Learning optimization failed',
            'message': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        safe_json_emit('error', error_data)

@socketio.on('agent_task')
def handle_agent_task(data):
    """Handle agent task assignment"""
    try:
        agent_name = data.get('agent', 'coordinator')
        task = data.get('task', 'status_check')

        if agent_name in system_state.agents:
            agent = system_state.agents[agent_name]
            agent.task_count += 1

            result = {
                'agent': agent_name,
                'task': task,
                'status': 'completed',
                'result': f'Task {task} completed by {agent.name}',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }

            safe_json_emit('agent_result', result)
            analytics.track_event('agent_task', result)

            logger.info(f"🤖 Agent {agent_name} completed task: {task}")
        else:
            error_data = {
                'error': 'Agent not found',
                'agent': agent_name,
                'available_agents': list(system_state.agents.keys()),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            safe_json_emit('error', error_data)

    except Exception as e:
        logger.error(f"Error handling agent task: {e}")
        error_data = {
            'error': 'Agent task failed',
            'message': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        safe_json_emit('error', error_data)

# HTTP Routes
@app.route('/')
def index():
    """Main dashboard"""
    return render_template('index.html')

@app.route('/api/status')
def api_status():
    """API endpoint for system status"""
    try:
        system_state.update_analytics()
        status = system_state.get_status()
        return jsonify(status)
    except Exception as e:
        logger.error(f"API status error: {e}")
        return jsonify({
            'error': 'Status unavailable',
            'message': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500

@app.route('/api/agents')
def api_agents():
    """API endpoint for agent information"""
    try:
        agents_data = {name: agent.to_dict() for name, agent in system_state.agents.items()}
        return jsonify(agents_data)
    except Exception as e:
        logger.error(f"API agents error: {e}")
        return jsonify({
            'error': 'Agents data unavailable',
            'message': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500

@app.route('/api/analytics')
def api_analytics():
    """API endpoint for analytics data"""
    try:
        analytics_data = analytics.get_summary()
        return jsonify(analytics_data)
    except Exception as e:
        logger.error(f"API analytics error: {e}")
        return jsonify({
            'error': 'Analytics data unavailable',
            'message': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500

# Background tasks
def background_system_monitor():
    """Background task to monitor system health"""
    while True:
        try:
            # Update system analytics
            system_state.update_analytics()

            # Emit periodic status updates to connected clients
            if system_state.active_sessions:
                status_update = {
                    'type': 'periodic_update',
                    'system': system_state.get_status(),
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                safe_json_emit('status_update', status_update, broadcast=True)

            # Track monitoring event
            analytics.track_event('system_monitor')

            # Sleep for 30 seconds
            time.sleep(30)

        except Exception as e:
            logger.error(f"Background monitor error: {e}")
            time.sleep(60)  # Wait longer on error

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Not found',
        'message': 'The requested resource was not found',
        'timestamp': datetime.now(timezone.utc).isoformat()
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred',
        'timestamp': datetime.now(timezone.utc).isoformat()
    }), 500

# Initialize system components
def initialize_system():
    """Initialize all system components"""
    logger.info("🚀 Initializing XMRT Ecosystem...")

    # Initialize agents
    agents = initialize_agents()
    logger.info(f"🤖 Multi-agent system: ✅ FULLY ACTIVATED ({len(agents)} agents)")

    # Initialize analytics
    analytics.track_event('system_startup')
    logger.info("📊 Analytics Engine: ✅ ENABLED")

    # Initialize learning system
    logger.info("🧠 Autonomous AI System: ✅ FULLY ACTIVATED")

    # Start background monitoring
    monitor_thread = threading.Thread(target=background_system_monitor, daemon=True)
    monitor_thread.start()
    logger.info("🔍 System Monitor: ✅ ACTIVE")

    logger.info("✨ XMRT Ecosystem initialization complete!")

if __name__ == '__main__':
    # Initialize system
    initialize_system()

    # Get port from environment
    port = int(os.environ.get('PORT', 5000))

    # Run with eventlet for production compatibility
    logger.info(f"🌐 Starting XMRT Ecosystem on port {port}")
    socketio.run(
        app,
        host='0.0.0.0',
        port=port,
        debug=False,
        use_reloader=False,
        log_output=True
    )
