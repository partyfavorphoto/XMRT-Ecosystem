#!/usr/bin/env python3
"""
Vercel serverless function entry point for XMRT Ecosystem Enhanced Flask App
"""

import sys
import os
from flask import Flask, render_template, jsonify

# Add the parent directory to Python path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Create a simplified Flask app for Vercel deployment
app = Flask(__name__, 
            template_folder=os.path.join(parent_dir, 'templates'),
            static_folder=os.path.join(parent_dir, 'static'))

app.config['SECRET_KEY'] = 'xmrt-ecosystem-vercel-2025'

@app.route('/')
def index():
    """Serve the enhanced dashboard"""
    try:
        return render_template('enhanced_dashboard.html')
    except Exception as e:
        return f'''
        <h1>🚀 XMRT DAO Hub</h1>
        <p>Enhanced Multi-Agent System with GitHub MCP Integration</p>
        <p><strong>Status:</strong> Deployed on Vercel (Serverless Mode)</p>
        <p><strong>Note:</strong> Some features may be limited in serverless environment</p>
        <p><strong>Error:</strong> {str(e)}</p>
        <p><a href="/api/status">Check System Status</a></p>
        '''

@app.route('/api/status')
@app.route('/api/status/comprehensive')
def status():
    """Basic status endpoint for Vercel deployment"""
    return jsonify({
        'success': True,
        'deployment': 'vercel-serverless',
        'system': {
            'status': 'operational',
            'version': '2.0.0-vercel',
            'platform': 'serverless'
        },
        'features': {
            'frontend': 'active',
            'responsive_design': 'active',
            'mobile_first': 'active'
        },
        'note': 'Full features available in production environment',
        'timestamp': '2025-09-02T20:30:00Z'
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return {'status': 'healthy', 'platform': 'vercel'}

# For Vercel serverless functions
def handler(request, response):
    return app(request, response)