# Socket.IO Debug Configuration for XMRT Ecosystem
# Enhanced logging and error handling for WebSocket issues

import logging
from flask_socketio import SocketIO

# Configure detailed logging
logging.basicConfig(level=logging.DEBUG)
socketio_logger = logging.getLogger('socketio')
socketio_logger.setLevel(logging.DEBUG)
engineio_logger = logging.getLogger('engineio')
engineio_logger.setLevel(logging.DEBUG)

def create_enhanced_socketio(app):
    """
    Create Socket.IO instance with enhanced debugging and error handling
    """
    
    socketio = SocketIO(
        app,
        # CORS settings
        cors_allowed_origins="*",
        cors_credentials=True,
        
        # Transport settings
        async_mode='gevent',
        
        # Timing settings
        ping_timeout=60,
        ping_interval=25,
        
        # Logging
        logger=True,
        engineio_logger=True,
        
        # WebSocket settings
        allow_upgrades=True,
        transports=['polling', 'websocket'],
        
        # Error handling
        always_connect=False,
        
        # Performance settings
        max_http_buffer_size=1000000,
        
        # Debug settings
        debug=True
    )
    
    # Enhanced error handlers
    @socketio.on_error_default
    def default_error_handler(e):
        socketio_logger.error(f"Socket.IO error: {e}")
        return {"error": "Internal server error", "message": str(e)}
    
    @socketio.on('connect')
    def handle_connect(auth):
        socketio_logger.info(f"Client connected: {request.sid}")
        socketio_logger.info(f"Transport: {request.transport}")
        socketio_logger.info(f"User agent: {request.headers.get('User-Agent', 'Unknown')}")
        
        # Send enhanced connection response
        emit('connection_response', {
            'status': 'connected',
            'message': 'Connected to XMRT-Ecosystem Maximum Capacity System',
            'transport': request.transport,
            'features': {
                'autonomous_system': True,
                'activity_monitor': True,
                'coordination_api': True,
                'chat_system': True,
                'memory_optimizer': True,
                'gemini_gems': True  # New feature from our enhancement
            },
            'timestamp': datetime.now().isoformat()
        })
    
    @socketio.on('disconnect')
    def handle_disconnect():
        socketio_logger.info(f"Client disconnected: {request.sid}")
        socketio_logger.info(f"Disconnect reason: {request.disconnect_reason if hasattr(request, 'disconnect_reason') else 'Unknown'}")
    
    @socketio.on('connect_error')
    def handle_connect_error(data):
        socketio_logger.error(f"Connection error: {data}")
    
    # Health check event
    @socketio.on('health_check')
    def handle_health_check():
        socketio_logger.info(f"Health check from: {request.sid}")
        emit('health_response', {
            'status': 'healthy',
            'transport': request.transport,
            'timestamp': datetime.now().isoformat()
        })
    
    return socketio

# WebSocket connection monitoring
class WebSocketMonitor:
    def __init__(self):
        self.connections = {}
        self.failed_upgrades = 0
        self.successful_connections = 0
    
    def log_connection(self, sid, transport):
        self.connections[sid] = {
            'transport': transport,
            'connected_at': datetime.now(),
            'status': 'active'
        }
        self.successful_connections += 1
        socketio_logger.info(f"Connection logged: {sid} via {transport}")
    
    def log_disconnection(self, sid, reason=None):
        if sid in self.connections:
            self.connections[sid]['status'] = 'disconnected'
            self.connections[sid]['disconnected_at'] = datetime.now()
            self.connections[sid]['reason'] = reason
        socketio_logger.info(f"Disconnection logged: {sid}, reason: {reason}")
    
    def log_failed_upgrade(self, sid):
        self.failed_upgrades += 1
        socketio_logger.warning(f"Failed WebSocket upgrade: {sid}")
    
    def get_stats(self):
        active_connections = sum(1 for conn in self.connections.values() if conn['status'] == 'active')
        return {
            'active_connections': active_connections,
            'total_connections': len(self.connections),
            'successful_connections': self.successful_connections,
            'failed_upgrades': self.failed_upgrades,
            'upgrade_success_rate': (self.successful_connections - self.failed_upgrades) / max(self.successful_connections, 1) * 100
        }

# Error recovery utilities
def handle_socket_error(error, sid=None):
    """
    Enhanced error handling for socket errors
    """
    error_type = type(error).__name__
    error_message = str(error)
    
    socketio_logger.error(f"Socket error [{error_type}]: {error_message}")
    
    if "Bad file descriptor" in error_message:
        socketio_logger.error("File descriptor error detected - possible connection cleanup issue")
        # Attempt to clean up the connection
        if sid:
            try:
                # Force disconnect the problematic connection
                socketio.disconnect(sid)
            except Exception as cleanup_error:
                socketio_logger.error(f"Error during cleanup: {cleanup_error}")
    
    elif "Failed websocket upgrade" in error_message:
        socketio_logger.error("WebSocket upgrade failed - client will fall back to polling")
        # Log for monitoring
        monitor.log_failed_upgrade(sid)
    
    return {"error": error_type, "message": error_message, "handled": True}

# Initialize monitor
monitor = WebSocketMonitor()

# Health check endpoint for Socket.IO
def add_health_endpoints(app):
    """
    Add health check endpoints for monitoring socket connectivity
    """
    
    @app.route('/health/websocket')
    def websocket_health():
        stats = monitor.get_stats()
        return {
            "status": "ok" if stats['active_connections'] >= 0 else "degraded",
            "websocket_enabled": True,
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
    
    @app.route('/health/socketio')
    def socketio_health():
        return {
            "status": "ok",
            "transports": ["polling", "websocket"],
            "cors_enabled": True,
            "async_mode": "gevent",
            "timestamp": datetime.now().isoformat()
        }

# Usage example:
"""
from socket_debug_config import create_enhanced_socketio, add_health_endpoints, monitor

# In your main app file:
app = Flask(__name__)
socketio = create_enhanced_socketio(app)
add_health_endpoints(app)

# Run with enhanced configuration
if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
"""

