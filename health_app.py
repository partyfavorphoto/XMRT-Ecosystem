#!/usr/bin/env python3
from flask import Flask, jsonify
import os
import sys
import logging
from datetime import datetime

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'xmrt-eliza',
        'version': '1.0.0',
        'timestamp': str(datetime.utcnow())
    })

@app.route('/')
def root():
    return jsonify({
        'message': 'XMRT Eliza is running',
        'status': 'operational'
    })

@app.route('/status')
def status():
    return jsonify({
        'service': 'xmrt-eliza',
        'status': 'running'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    logger.info(f"Starting health server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
