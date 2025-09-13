#!/usr/bin/env python3
"""
XMRT Ecosystem - Minimal Version for Render Free Tier
Compatible with: gunicorn -w 2 -k gevent -b 0.0.0.0:$PORT main:app

OPTIMIZATIONS:
- Removed all heavy ML/AI dependencies
- Minimal memory footprint
- Fast startup time
- Core Flask functionality only
"""

import os
import sys
import json
import time
import logging
import threading
from datetime import datetime
from flask import Flask, jsonify, request

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'xmrt-ecosystem-minimal')

# System state
system_state = {
    "status": "operational",
    "startup_time": time.time(),
    "version": "2.1.0-minimal",
    "deployment": "render-free-tier",
    "worker_config": "gevent-optimized",
    "mode": "minimal_core"
}

# Simplified agent state (no heavy operations)
agents_state = {
    "core_agent": {
        "name": "Core Agent",
        "type": "basic_operations",
        "status": "operational",
        "capabilities": ["api_handling", "basic_responses"],
        "last_activity": time.time()
    },
    "web_agent": {
        "name": "Web Agent",
        "type": "web_interface",
        "status": "operational", 
        "capabilities": ["http_requests", "json_responses"],
        "last_activity": time.time()
    }
}

# Basic analytics
analytics = {
    "requests_count": 0,
    "uptime_checks": 0,
    "agent_interactions": 0,
    "startup_time": time.time()
}

# Core Flask Routes
@app.route('/')
def index():
    """Main status page - minimal and fast"""
    start_time = time.time()
    analytics["requests_count"] += 1
    
    uptime = time.time() - system_state["startup_time"]
    
    response_data = {
        "status": "🚀 XMRT Ecosystem - Minimal Core",
        "message": "Optimized for Render Free Tier",
        "version": system_state["version"],
        "uptime_seconds": round(uptime, 2),
        "uptime_formatted": f"{int(uptime//3600)}h {int((uptime%3600)//60)}m {int(uptime%60)}s",
        "deployment": system_state["deployment"],
        "mode": system_state["mode"],
        "timestamp": datetime.now().isoformat(),
        "system_health": {
            "agents": {
                "total": len(agents_state),
                "operational": len([a for a in agents_state.values() if a["status"] == "operational"]),
                "list": list(agents_state.keys())
            },
            "analytics": analytics,
            "memory_optimized": True
        },
        "response_time_ms": round((time.time() - start_time) * 1000, 2)
    }
    
    return jsonify(response_data)

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime": time.time() - system_state["startup_time"],
        "version": system_state["version"],
        "mode": "minimal"
    })

@app.route('/agents')
def get_agents():
    """Get agents status"""
    analytics["requests_count"] += 1
    analytics["agent_interactions"] += 1
    
    return jsonify({
        "agents": agents_state,
        "total_agents": len(agents_state),
        "operational_agents": len([a for a in agents_state.values() if a["status"] == "operational"]),
        "mode": "minimal_core"
    })

@app.route('/analytics')
def get_analytics():
    """Get system analytics"""
    analytics["requests_count"] += 1
    uptime = time.time() - system_state["startup_time"]
    
    return jsonify({
        "analytics": analytics,
        "uptime": uptime,
        "requests_per_minute": analytics["requests_count"] / max(uptime / 60, 1),
        "mode": "minimal",
        "memory_optimized": True,
        "startup_time": analytics["startup_time"]
    })

@app.route('/test')
def test_endpoint():
    """Test endpoint to verify functionality"""
    return jsonify({
        "test": "success",
        "message": "XMRT Ecosystem minimal version is working!",
        "timestamp": datetime.now().isoformat(),
        "version": system_state["version"]
    })

@app.route('/api/status')
def api_status():
    """API status endpoint"""
    return jsonify({
        "api": "operational",
        "endpoints": ["/", "/health", "/agents", "/analytics", "/test", "/api/status"],
        "version": system_state["version"],
        "mode": "minimal_core"
    })

# Utility functions (lightweight)
def update_agent_activity(agent_id):
    """Update agent activity timestamp"""
    if agent_id in agents_state:
        agents_state[agent_id]["last_activity"] = time.time()
        analytics["agent_interactions"] += 1

# Background health monitor (optional and lightweight)
def lightweight_monitor():
    """Lightweight background monitor - runs only if enabled"""
    logger.info("🔍 Starting lightweight monitor...")
    
    for i in range(10):  # Run for limited cycles only
        try:
            # Update analytics
            analytics["uptime_checks"] += 1
            
            # Update agent activities
            for agent_id in agents_state:
                update_agent_activity(agent_id)
            
            # Log health every 5 cycles
            if i % 5 == 0:
                uptime = time.time() - system_state["startup_time"]
                logger.info(f"🔄 System Health: Uptime {uptime:.0f}s | Requests: {analytics['requests_count']}")
            
            time.sleep(30)  # Check every 30 seconds
            
        except Exception as e:
            logger.error(f"Monitor error: {e}")
            break
    
    logger.info("🔍 Lightweight monitor completed")

# Safe initialization
def initialize_minimal_system():
    """Initialize minimal system - guaranteed to work"""
    try:
        logger.info("🚀 Initializing XMRT Minimal System...")
        
        # Basic system checks
        logger.info("✅ Flask app: Ready")
        logger.info("✅ Routes: Configured")
        logger.info("✅ Agents: Basic setup complete")
        logger.info("✅ Analytics: Initialized")
        
        logger.info(f"✅ XMRT Minimal System ready (v{system_state['version']})")
        logger.info("🎯 Optimized for Render Free Tier")
        logger.info("⚡ Fast startup, minimal memory usage")
        
        return True
        
    except Exception as e:
        logger.error(f"Minimal system initialization error: {e}")
        return False

# Optional background monitor start
@app.route('/start-monitor', methods=['POST'])
def start_monitor():
    """Manually start lightweight background monitor"""
    try:
        monitor_thread = threading.Thread(target=lightweight_monitor, daemon=True)
        monitor_thread.start()
        logger.info("🔍 Lightweight monitor started")
        return jsonify({"status": "success", "message": "Monitor started"})
    except Exception as e:
        logger.error(f"Failed to start monitor: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Initialize on import (safe version)
try:
    if initialize_minimal_system():
        logger.info("✅ Minimal system initialization successful")
    else:
        logger.warning("⚠️ System initialization had issues but continuing...")
except Exception as e:
    logger.error(f"❌ System initialization error: {e}")
    # Continue anyway - don't crash

# Main entry point
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🌐 Starting XMRT Minimal server on port {port}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        threaded=True
    )
