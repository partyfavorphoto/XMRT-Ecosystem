#!/usr/bin/env python3
# Ultra-Simple Eliza Orchestrator for Render Deployment

import os
import sys
from datetime import datetime

# Only use built-in Python modules
try:
    from flask import Flask, jsonify
except ImportError:
    print("Flask not available")
    sys.exit(1)

app = Flask(__name__)

# Global state
start_time = datetime.now()

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'xmrt-eliza',
        'version': '1.0.0-minimal',
        'timestamp': datetime.now().isoformat(),
        'uptime_seconds': int((datetime.now() - start_time).total_seconds())
    })

@app.route('/')
def root():
    return jsonify({
        'message': 'XMRT Eliza is running (minimal mode)',
        'status': 'operational',
        'mode': 'minimal',
        'endpoints': ['/health', '/status']
    })

@app.route('/status')
def status():
    return jsonify({
        'service': 'xmrt-eliza',
        'status': 'running',
        'mode': 'minimal',
        'uptime_seconds': int((datetime.now() - start_time).total_seconds()),
        'python_version': sys.version,
        'components': {
            'web_server': 'active',
            'health_check': 'active'
        }
    })

@app.route('/api/health')
def api_health():
    return health_check()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    print(f"Starting XMRT Eliza minimal orchestrator on port {port}")
    print(f"Python version: {sys.version}")
    print(f"Start time: {start_time}")
    
    app.run(host='0.0.0.0', port=port, debug=False)
