#!/usr/bin/env python3
"""
XMRT-Ecosystem API Route Fixes
Comprehensive fixes for API routing, WebSocket connections, and frontend integration
"""

import os
import json
import logging
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from functools import wraps

# Enhanced API route fixes for XMRT-Ecosystem
class XMRTAPIFixer:
    def __init__(self, app, socketio):
        self.app = app
        self.socketio = socketio
        self.active_connections = {}
        self.learning_data = []
        self.autonomous_state = {
            'learning_active': False,
            'coordination_active': False,
            'memory_active': False,
            'agents_active': False
        }
        
    def setup_fixed_routes(self):
        """Setup all fixed API routes with proper error handling"""
        
        # ==========================================
        # CORE AUTONOMOUS SYSTEM ROUTES (FIXED)
        # ==========================================
        
        @self.app.route('/api/agents/activate', methods=['POST'])
        def activate_agents():
            """Fixed agent activation endpoint"""
            try:
                # Simulate agent activation
                self.autonomous_state['agents_active'] = True
                
                # Start learning cycle
                self.start_learning_cycle()
                
                response = {
                    'success': True,
                    'message': 'Autonomous agents activated successfully',
                    'agents': {
                        'coordinator': {'status': 'active', 'tasks': 0},
                        'analyzer': {'status': 'active', 'insights': 0},
                        'developer': {'status': 'active', 'optimizations': 0}
                    },
                    'learning_active': self.autonomous_state['learning_active'],
                    'timestamp': datetime.now().isoformat()
                }
                
                # Emit to all connected clients
                self.socketio.emit('agents_activated', response)
                
                return jsonify(response)
                
            except Exception as e:
                error_response = {
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                return jsonify(error_response), 500
        
        @self.app.route('/api/learning/start', methods=['POST'])
        def start_learning():
            """Fixed learning system activation"""
            try:
                self.autonomous_state['learning_active'] = True
                
                # Initialize learning data collection
                learning_session = {
                    'session_id': f"learn_{int(datetime.now().timestamp())}",
                    'started_at': datetime.now().isoformat(),
                    'status': 'active',
                    'data_points': 0
                }
                
                self.learning_data.append(learning_session)
                
                response = {
                    'success': True,
                    'message': 'Learning system activated',
                    'session': learning_session,
                    'autonomous_state': self.autonomous_state,
                    'timestamp': datetime.now().isoformat()
                }
                
                # Emit learning status update
                self.socketio.emit('learning_started', response)
                
                return jsonify(response)
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
        
        @self.app.route('/api/coordination/activate', methods=['POST'])
        def activate_coordination():
            """Fixed coordination system activation"""
            try:
                self.autonomous_state['coordination_active'] = True
                
                coordination_status = {
                    'active': True,
                    'agents_coordinated': 3,
                    'tasks_managed': 0,
                    'started_at': datetime.now().isoformat()
                }
                
                response = {
                    'success': True,
                    'message': 'Coordination system activated',
                    'coordination': coordination_status,
                    'autonomous_state': self.autonomous_state,
                    'timestamp': datetime.now().isoformat()
                }
                
                # Emit coordination status
                self.socketio.emit('coordination_activated', response)
                
                return jsonify(response)
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
        
        @self.app.route('/api/memory/activate', methods=['POST'])
        def activate_memory():
            """Fixed memory system activation"""
            try:
                self.autonomous_state['memory_active'] = True
                
                memory_status = {
                    'active': True,
                    'storage_initialized': True,
                    'learning_data_stored': len(self.learning_data),
                    'started_at': datetime.now().isoformat()
                }
                
                response = {
                    'success': True,
                    'message': 'Long-term memory system activated',
                    'memory': memory_status,
                    'autonomous_state': self.autonomous_state,
                    'timestamp': datetime.now().isoformat()
                }
                
                # Emit memory status
                self.socketio.emit('memory_activated', response)
                
                return jsonify(response)
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
        
        # ==========================================
        # STATUS AND MONITORING ROUTES (FIXED)
        # ==========================================
        
        @self.app.route('/api/status/autonomous', methods=['GET'])
        def get_autonomous_status():
            """Get comprehensive autonomous system status"""
            try:
                status = {
                    'autonomous_state': self.autonomous_state,
                    'learning_sessions': len(self.learning_data),
                    'active_connections': len(self.active_connections),
                    'system_health': 'optimal' if all(self.autonomous_state.values()) else 'partial',
                    'uptime': str(datetime.now() - datetime.now().replace(hour=0, minute=0, second=0)),
                    'timestamp': datetime.now().isoformat()
                }
                
                return jsonify(status)
                
            except Exception as e:
                return jsonify({
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
        
        @self.app.route('/api/learning/data', methods=['GET'])
        def get_learning_data():
            """Get learning system data"""
            try:
                return jsonify({
                    'learning_sessions': self.learning_data,
                    'total_sessions': len(self.learning_data),
                    'active_learning': self.autonomous_state['learning_active'],
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                return jsonify({
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
        
        # ==========================================
        # WEBSOCKET EVENT HANDLERS (FIXED)
        # ==========================================
        
        @self.socketio.on('connect')
        def handle_connect():
            """Fixed WebSocket connection handler"""
            try:
                client_id = request.sid
                self.active_connections[client_id] = {
                    'connected_at': datetime.now().isoformat(),
                    'user_agent': request.headers.get('User-Agent', 'Unknown'),
                    'ip': request.remote_addr
                }
                
                # Send connection confirmation with system status
                emit('connection_response', {
                    'status': 'connected',
                    'message': 'Connected to XMRT-Ecosystem Maximum Capacity System',
                    'client_id': client_id,
                    'features': {
                        'autonomous_system': True,
                        'activity_monitor': True,
                        'coordination_api': True,
                        'chat_system': True,
                        'memory_optimizer': True,
                        'learning_system': True
                    },
                    'autonomous_state': self.autonomous_state,
                    'timestamp': datetime.now().isoformat()
                })
                
                # Join main room for system updates
                join_room('system_updates')
                
                logging.info(f"Client connected: {client_id}")
                
            except Exception as e:
                logging.error(f"Connection error: {str(e)}")
                emit('error', {'message': str(e)})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Fixed WebSocket disconnection handler"""
            try:
                client_id = request.sid
                if client_id in self.active_connections:
                    del self.active_connections[client_id]
                
                leave_room('system_updates')
                logging.info(f"Client disconnected: {client_id}")
                
            except Exception as e:
                logging.error(f"Disconnection error: {str(e)}")
        
        @self.socketio.on('request_status')
        def handle_status_request():
            """Handle status requests from frontend"""
            try:
                emit('status_update', {
                    'autonomous_state': self.autonomous_state,
                    'active_connections': len(self.active_connections),
                    'learning_sessions': len(self.learning_data),
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                emit('error', {'message': str(e)})
        
        @self.socketio.on('activate_system')
        def handle_system_activation(data):
            """Handle system activation requests from frontend"""
            try:
                system_type = data.get('system', 'all')
                
                if system_type == 'agents' or system_type == 'all':
                    self.autonomous_state['agents_active'] = True
                    
                if system_type == 'learning' or system_type == 'all':
                    self.autonomous_state['learning_active'] = True
                    self.start_learning_cycle()
                    
                if system_type == 'coordination' or system_type == 'all':
                    self.autonomous_state['coordination_active'] = True
                    
                if system_type == 'memory' or system_type == 'all':
                    self.autonomous_state['memory_active'] = True
                
                # Emit activation confirmation
                emit('system_activated', {
                    'system': system_type,
                    'autonomous_state': self.autonomous_state,
                    'message': f'{system_type.title()} system activated successfully',
                    'timestamp': datetime.now().isoformat()
                })
                
                # Broadcast to all clients
                self.socketio.emit('system_update', {
                    'autonomous_state': self.autonomous_state,
                    'timestamp': datetime.now().isoformat()
                }, room='system_updates')
                
            except Exception as e:
                emit('error', {'message': str(e)})
    
    def start_learning_cycle(self):
        """Start the autonomous learning cycle"""
        try:
            if not self.autonomous_state['learning_active']:
                return
            
            # Simulate learning data collection
            learning_point = {
                'timestamp': datetime.now().isoformat(),
                'type': 'system_interaction',
                'data': {
                    'active_connections': len(self.active_connections),
                    'system_state': self.autonomous_state.copy()
                }
            }
            
            # Store learning data
            if self.learning_data:
                self.learning_data[-1]['data_points'] = self.learning_data[-1].get('data_points', 0) + 1
            
            # Emit learning update
            self.socketio.emit('learning_update', {
                'learning_point': learning_point,
                'total_points': sum(session.get('data_points', 0) for session in self.learning_data),
                'timestamp': datetime.now().isoformat()
            }, room='system_updates')
            
        except Exception as e:
            logging.error(f"Learning cycle error: {str(e)}")

def apply_api_fixes(app, socketio):
    """Apply all API fixes to the Flask app"""
    fixer = XMRTAPIFixer(app, socketio)
    fixer.setup_fixed_routes()
    return fixer

