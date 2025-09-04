#!/usr/bin/env python3
"""
Enhanced startup script for XMRT-Ecosystem with gevent WebSocket support
Ensures proper gevent configuration before starting the application
"""

import gevent.monkey
gevent.monkey.patch_all()

import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main application entry point with enhanced gevent support"""
    try:
        logger.info("🚀 Starting XMRT-Ecosystem with gevent WebSocket support")

        # Import the main application after gevent patching
        from main import app, socketio

        # Get port from environment
        port = int(os.environ.get('PORT', 5000))

        logger.info(f"🌐 Starting server on port {port}")
        logger.info("✅ Gevent monkey patching applied")
        logger.info("✅ WebSocket transport ready")

        # Run the application
        socketio.run(app, 
                    host='0.0.0.0', 
                    port=port,
                    debug=False,
                    use_reloader=False)

    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
