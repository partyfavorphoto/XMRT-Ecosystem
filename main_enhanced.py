#!/usr/bin/env python3
"""
Enhanced XMRT Ecosystem Main Application
Integrates the original Flask app with MCP servers and enhanced agents
"""

import os
import sys
import json
import time
import logging
import threading
from pathlib import Path

# Import the original main app
from main import app, socketio

# Import the enhanced system manager
from start_xmrt_system import XMRTSystemManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global system manager instance
system_manager = None

def initialize_enhanced_system():
    """Initialize the enhanced XMRT system alongside the Flask app"""
    global system_manager
    
    try:
        logger.info("Initializing enhanced XMRT system...")
        
        # Create system manager
        system_manager = XMRTSystemManager()
        
        # Start the enhanced system in a separate thread
        def start_enhanced_system():
            try:
                if system_manager.start_system():
                    logger.info("✅ Enhanced XMRT system started successfully")
                else:
                    logger.error("❌ Failed to start enhanced XMRT system")
            except Exception as e:
                logger.error(f"Error starting enhanced system: {e}")
        
        # Start enhanced system in background thread
        enhanced_thread = threading.Thread(target=start_enhanced_system, daemon=True)
        enhanced_thread.start()
        
        logger.info("Enhanced system initialization complete")
        
    except Exception as e:
        logger.error(f"Failed to initialize enhanced system: {e}")

# Add new routes for enhanced system status
@app.route('/api/enhanced/status')
def enhanced_status():
    """Get enhanced system status"""
    try:
        if system_manager:
            status = system_manager.get_system_status()
            return {
                "status": "success",
                "data": status,
                "enhanced_system": "active"
            }
        else:
            return {
                "status": "error",
                "message": "Enhanced system not initialized",
                "enhanced_system": "inactive"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "enhanced_system": "error"
        }

@app.route('/api/enhanced/agents')
def enhanced_agents():
    """Get enhanced agents status"""
    try:
        if system_manager:
            status = system_manager.get_system_status()
            return {
                "status": "success",
                "agents": status.get("agents", {}),
                "total_agents": len(status.get("agents", {}))
            }
        else:
            return {
                "status": "error",
                "message": "Enhanced system not initialized"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@app.route('/api/enhanced/mcp-servers')
def enhanced_mcp_servers():
    """Get MCP servers status"""
    try:
        if system_manager:
            status = system_manager.get_system_status()
            return {
                "status": "success",
                "mcp_servers": status.get("mcp_servers", {}),
                "total_servers": len(status.get("mcp_servers", {}))
            }
        else:
            return {
                "status": "error",
                "message": "Enhanced system not initialized"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

# Initialize enhanced system when the module is imported
initialize_enhanced_system()

# Export the app and socketio for gunicorn
if __name__ == '__main__':
    # Development server
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
else:
    # Production server (gunicorn)
    logger.info("Running in production mode with enhanced XMRT system")
