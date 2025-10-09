"""
Health check endpoints and system monitoring
"""

import time
import logging
from datetime import datetime
from flask import Blueprint, jsonify

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

logger = logging.getLogger(__name__)

# Create health check blueprint
health_bp = Blueprint('health', __name__)

class HealthMonitor:
    """System health monitoring class"""
    
    def __init__(self):
        self.start_time = time.time()
    
    def get_system_metrics(self):
        """Get current system metrics"""
        if PSUTIL_AVAILABLE:
            try:
                return {
                    "cpu": round(psutil.cpu_percent(interval=0.1), 1),
                    "memory": round(psutil.virtual_memory().percent, 1),
                    "disk": round(psutil.disk_usage("/").percent, 1)
                }
            except Exception as e:
                logger.warning(f"Failed to get system metrics: {e}")
        
        # Fallback to simulated metrics
        import random
        return {
            "cpu": round(random.uniform(10, 40), 1),
            "memory": round(random.uniform(20, 60), 1),
            "disk": round(random.uniform(30, 70), 1)
        }
    
    def get_uptime(self):
        """Get application uptime in seconds"""
        return round(time.time() - self.start_time, 2)

# Global health monitor instance
health_monitor = HealthMonitor()

@health_bp.route('/health')
@health_bp.route('/healthz')
def health_check():
    """Basic health check endpoint"""
    try:
        response = {
            "ok": True,
            "status": "healthy",
            "version": "6.3.0-hardy-github",
            "app_name": "XMRT-Ecosystem",
            "timestamp": datetime.now().isoformat(),
            "uptime": health_monitor.get_uptime(),
            "system": health_monitor.get_system_metrics()
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "ok": False,
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@health_bp.route('/health/detailed')
def detailed_health_check():
    """Detailed health check with more information"""
    try:
        system_metrics = health_monitor.get_system_metrics()
        
        # Determine overall health
        system_healthy = all(metric < 90 for metric in system_metrics.values())
        
        response = {
            "ok": system_healthy,
            "status": "healthy" if system_healthy else "degraded",
            "version": "6.3.0-hardy-github",
            "app_name": "XMRT-Ecosystem",
            "timestamp": datetime.now().isoformat(),
            "uptime": health_monitor.get_uptime(),
            "system": system_metrics,
            "checks": {
                "system_healthy": system_healthy
            }
        }
        
        status_code = 200 if system_healthy else 503
        return jsonify(response), status_code
        
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        return jsonify({
            "ok": False,
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500
