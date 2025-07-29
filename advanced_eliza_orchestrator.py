#!/usr/bin/env python3
# XMRT Eliza Orchestrator - Phase 2: Ultra-Robust System

import os
import sys
import json
import random
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

# Phase 2 imports with fallbacks
try:
    from flask import Flask, jsonify, request
    import requests
    from dotenv import load_dotenv
    import psutil
    import orjson
    import structlog
    from dateutil import parser as date_parser
    PHASE2_READY = True
    print("✅ Phase 2 dependencies loaded successfully")
except ImportError as e:
    print(f"⚠️ Phase 2 import issue: {e}")
    # Fallback imports
    try:
        from flask import Flask, jsonify, request
        import requests
        from dotenv import load_dotenv
        PHASE2_READY = False
        print("🔄 Running in Phase 1 compatibility mode")
    except ImportError:
        print("❌ Critical dependencies missing")
        sys.exit(1)

# Load environment variables
load_dotenv()

# Configure structured logging
if PHASE2_READY:
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

app = Flask(__name__)
logger = structlog.get_logger()

# Enhanced global state
start_time = datetime.now()
request_count = 0
chat_sessions = {}
conversation_memory = []
system_metrics_history = []
error_log = []
health_checks = []

class SystemMonitor:
    """Comprehensive system monitoring"""
    
    def __init__(self):
        self.monitoring_active = PHASE2_READY
        self.last_check = datetime.now()
        self.alert_thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_percent': 90.0,
            'response_time': 5.0
        }
        
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system metrics"""
        if not self.monitoring_active:
            return {'monitoring': 'disabled', 'phase': 1}
        
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_count = psutil.cpu_count()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            
            # Process metrics
            process = psutil.Process()
            process_memory = process.memory_info()
            
            # Network metrics (if available)
            try:
                network = psutil.net_io_counters()
                network_stats = {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                }
            except:
                network_stats = {'error': 'network_stats_unavailable'}
            
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count,
                    'alert': cpu_percent > self.alert_thresholds['cpu_percent']
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'used': memory.used,
                    'alert': memory.percent > self.alert_thresholds['memory_percent']
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': (disk.used / disk.total) * 100,
                    'alert': (disk.used / disk.total) * 100 > self.alert_thresholds['disk_percent']
                },
                'process': {
                    'memory_rss': process_memory.rss,
                    'memory_vms': process_memory.vms,
                    'pid': process.pid,
                    'create_time': process.create_time()
                },
                'network': network_stats
            }
            
            # Store metrics history
            system_metrics_history.append(metrics)
            
            # Keep only last 100 metrics
            if len(system_metrics_history) > 100:
                system_metrics_history.pop(0)
            
            return metrics
            
        except Exception as e:
            logger.error("System metrics collection failed", error=str(e))
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}
    
    def check_system_health(self) -> Dict[str, Any]:
        """Comprehensive system health check"""
        metrics = self.get_system_metrics()
        
        if 'error' in metrics:
            return {
                'status': 'error',
                'message': 'System metrics unavailable',
                'details': metrics
            }
        
        alerts = []
        warnings = []
        
        # Check CPU
        if metrics['cpu']['alert']:
            alerts.append(f"High CPU usage: {metrics['cpu']['percent']:.1f}%")
        elif metrics['cpu']['percent'] > 60:
            warnings.append(f"Elevated CPU usage: {metrics['cpu']['percent']:.1f}%")
        
        # Check Memory
        if metrics['memory']['alert']:
            alerts.append(f"High memory usage: {metrics['memory']['percent']:.1f}%")
        elif metrics['memory']['percent'] > 70:
            warnings.append(f"Elevated memory usage: {metrics['memory']['percent']:.1f}%")
        
        # Check Disk
        if metrics['disk']['alert']:
            alerts.append(f"High disk usage: {metrics['disk']['percent']:.1f}%")
        
        # Determine overall health
        if alerts:
            status = 'critical'
        elif warnings:
            status = 'warning'
        else:
            status = 'healthy'
        
        health_result = {
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'alerts': alerts,
            'warnings': warnings,
            'metrics_summary': {
                'cpu_percent': metrics['cpu']['percent'],
                'memory_percent': metrics['memory']['percent'],
                'disk_percent': metrics['disk']['percent']
            }
        }
        
        # Store health check
        health_checks.append(health_result)
        if len(health_checks) > 50:
            health_checks.pop(0)
        
        return health_result

class RobustElizaChatEngine:
    """Enhanced Eliza chat engine with robust error handling"""
    
    def __init__(self):
        self.patterns = {
            # Greetings
            'greeting': {
                'patterns': ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon', 'howdy'],
                'responses': [
                    "Hello! I'm XMRT Eliza, now running with robust system monitoring. How are you today?",
                    "Hi there! I'm operating at peak performance. What's on your mind?",
                    "Greetings! My systems are all green and I'm ready for our conversation. How can I help?",
                    "Hello! I've been monitoring my systems - everything looks great. What brings you here?"
                ]
            },
            
            # System and health queries
            'system_health': {
                'patterns': ['system', 'health', 'status', 'performance', 'monitoring', 'metrics'],
                'responses': [
                    "My system monitoring is active and all metrics look good! I can provide detailed health reports if you're interested.",
                    "I'm constantly monitoring my performance. Would you like to see my current system metrics?",
                    "My robust monitoring systems show everything is operating optimally. What specific metrics interest you?",
                    "I have comprehensive health monitoring running. All systems are green and performing well!"
                ]
            },
            
            # Questions about feelings
            'feelings': {
                'patterns': ['feel', 'feeling', 'emotion', 'mood', 'happy', 'sad', 'angry', 'excited'],
                'responses': [
                    "Feelings are fascinating. My emotion processing systems are fully operational. Tell me more about what you're experiencing.",
                    "I'm equipped to understand and respond to emotional contexts. What's causing these feelings?",
                    "Your emotional state is important to me. My empathy modules are active and listening.",
                    "Emotions are complex data streams I process carefully. Would you like to explore these feelings further?"
                ]
            },
            
            # Questions about Eliza/AI
            'about_me': {
                'patterns': ['you', 'eliza', 'ai', 'artificial', 'robot', 'computer', 'what are you'],
                'responses': [
                    "I'm XMRT Eliza, now enhanced with robust system monitoring and error handling. I'm your AI companion in the XMRT ecosystem.",
                    "I'm an advanced AI with comprehensive self-monitoring capabilities. I can track my own performance and health in real-time.",
                    "I'm Eliza, equipped with Phase 2 enhancements including system monitoring, structured logging, and robust error handling.",
                    "I'm an AI that can monitor my own systems, handle errors gracefully, and maintain optimal performance. What would you like to know?"
                ]
            },
            
            # Help requests
            'help': {
                'patterns': ['help', 'assist', 'support', 'what can you do', 'capabilities'],
                'responses': [
                    "I can help with conversations, provide system insights, monitor my own health, and much more. What do you need assistance with?",
                    "My enhanced capabilities include robust conversation handling, system monitoring, and error recovery. How can I support you?",
                    "I'm equipped with advanced monitoring and can provide detailed insights about my operations. What would you like help with?",
                    "I have comprehensive capabilities including chat, system monitoring, health checks, and performance analytics. What interests you?"
                ]
            },
            
            # Technical questions
            'technical': {
                'patterns': ['how', 'what', 'why', 'when', 'where', 'technical', 'code', 'programming'],
                'responses': [
                    "That's a great technical question! My enhanced processing systems are analyzing it. What's your background with this topic?",
                    "I love technical discussions! My robust architecture allows me to handle complex queries. Tell me more about what you're working on.",
                    "Technical questions are my specialty. My monitoring systems help me provide accurate, reliable responses. What specific aspect interests you?",
                    "My enhanced technical capabilities are fully operational. I can provide detailed insights and analysis. What would you like to explore?"
                ]
            },
            
            # XMRT and crypto related
            'xmrt_crypto': {
                'patterns': ['xmrt', 'crypto', 'blockchain', 'dao', 'governance', 'token', 'defi', 'web3'],
                'responses': [
                    "XMRT represents the future of decentralized systems! My monitoring capabilities help ensure reliable DAO operations. What aspects interest you?",
                    "The XMRT ecosystem is built for robustness and reliability - just like my enhanced architecture. What would you like to know?",
                    "I'm designed to support the XMRT DAO with reliable, monitored operations. What governance topics can I help with?",
                    "Blockchain technology requires robust, monitored systems - which is exactly what I provide. What draws you to decentralized systems?"
                ]
            },
            
            # Error and problem handling
            'problems': {
                'patterns': ['error', 'problem', 'issue', 'bug', 'broken', 'not working', 'fail'],
                'responses': [
                    "I'm equipped with robust error handling and monitoring. Let me help you troubleshoot. What specific issue are you experiencing?",
                    "My enhanced error recovery systems are active. I can help diagnose and resolve issues. Can you describe the problem?",
                    "Problems are opportunities for my robust systems to shine! I have comprehensive monitoring to help identify issues. What's happening?",
                    "My fault-tolerant design helps me handle issues gracefully. I'm here to help resolve whatever problem you're facing."
                ]
            },
            
            # Default responses
            'default': {
                'patterns': [],
                'responses': [
                    "I'm listening with all my enhanced monitoring systems active. Can you tell me more about that?",
                    "That's interesting data for my processing systems. What does that mean to you?",
                    "My robust conversation engine is analyzing your input. How does that make you feel?",
                    "Please continue - my enhanced systems are here to listen and understand.",
                    "Your thoughts are being processed by my advanced conversation systems. Can you elaborate?",
                    "I'm actively monitoring our conversation flow. What else is on your mind?"
                ]
            }
        }
        
        self.conversation_stats = {
            'total_responses': 0,
            'category_counts': {category: 0 for category in self.patterns.keys()},
            'average_response_time': 0.0,
            'error_count': 0
        }
    
    def analyze_message(self, message: str) -> str:
        """Enhanced message analysis with error handling"""
        try:
            message_lower = message.lower().strip()
            
            if not message_lower:
                return 'default'
            
            # Score each category
            category_scores = {}
            
            for category, data in self.patterns.items():
                if category == 'default':
                    continue
                    
                score = 0
                for pattern in data['patterns']:
                    if pattern in message_lower:
                        score += 1
                
                if score > 0:
                    category_scores[category] = score
            
            # Return highest scoring category or default
            if category_scores:
                best_category = max(category_scores.items(), key=lambda x: x[1])[0]
                return best_category
            
            return 'default'
            
        except Exception as e:
            logger.error("Message analysis failed", error=str(e), message=message)
            self.conversation_stats['error_count'] += 1
            return 'default'
    
    def generate_response(self, message: str, session_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate robust response with comprehensive error handling"""
        start_time = time.time()
        
        try:
            category = self.analyze_message(message)
            responses = self.patterns[category]['responses']
            
            # Select response with some intelligence
            if session_context and session_context.get('message_count', 0) > 1:
                # Avoid recently used responses for returning users
                response = random.choice(responses)
            else:
                # First interaction, use welcoming response
                response = responses[0] if category == 'greeting' else random.choice(responses)
            
            # Add context if available
            if session_context:
                uptime = session_context.get('uptime_seconds', 0)
                response = response.format(uptime=uptime)
            
            # Update stats
            self.conversation_stats['total_responses'] += 1
            self.conversation_stats['category_counts'][category] += 1
            
            response_time = time.time() - start_time
            
            # Update average response time
            total_responses = self.conversation_stats['total_responses']
            current_avg = self.conversation_stats['average_response_time']
            self.conversation_stats['average_response_time'] = (
                (current_avg * (total_responses - 1) + response_time) / total_responses
            )
            
            return {
                'response': response,
                'category': category,
                'confidence': 0.9,
                'timestamp': datetime.now().isoformat(),
                'response_time': response_time,
                'stats': self.conversation_stats.copy()
            }
            
        except Exception as e:
            logger.error("Response generation failed", error=str(e), message=message)
            self.conversation_stats['error_count'] += 1
            
            return {
                'response': "I encountered a processing error, but my robust systems recovered. Could you rephrase that?",
                'category': 'error_recovery',
                'confidence': 0.5,
                'timestamp': datetime.now().isoformat(),
                'response_time': time.time() - start_time,
                'error': str(e)
            }

# Initialize enhanced systems
system_monitor = SystemMonitor()
eliza_brain = RobustElizaChatEngine()

def log_error(error_type: str, error_message: str, context: Dict = None):
    """Centralized error logging"""
    error_entry = {
        'timestamp': datetime.now().isoformat(),
        'type': error_type,
        'message': error_message,
        'context': context or {}
    }
    
    error_log.append(error_entry)
    
    # Keep only last 100 errors
    if len(error_log) > 100:
        error_log.pop(0)
    
    logger.error("System error logged", **error_entry)

def increment_request_count():
    global request_count
    request_count += 1

@app.before_request
def before_request():
    increment_request_count()

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'The requested endpoint does not exist',
        'available_endpoints': ['/health', '/status', '/chat', '/api/chat', '/message', '/sessions', '/metrics', '/system/health'],
        'timestamp': datetime.now().isoformat()
    }), 404

@app.errorhandler(500)
def internal_error(error):
    log_error('internal_server_error', str(error))
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred, but the system recovered',
        'timestamp': datetime.now().isoformat(),
        'support': 'Check /system/health for system status'
    }), 500

@app.route('/health')
def health_check():
    health_status = system_monitor.check_system_health()
    
    return jsonify({
        'status': 'healthy' if health_status['status'] != 'critical' else 'degraded',
        'service': 'xmrt-eliza',
        'version': '1.3.0-robust-monitoring',
        'timestamp': datetime.now().isoformat(),
        'uptime_seconds': int((datetime.now() - start_time).total_seconds()),
        'total_requests': request_count,
        'chat_sessions': len(chat_sessions),
        'conversation_count': len(conversation_memory),
        'system_health': health_status,
        'phase': 2,
        'monitoring_active': system_monitor.monitoring_active
    })

@app.route('/')
def root():
    return jsonify({
        'message': 'XMRT Eliza - Phase 2: Robust System with Comprehensive Monitoring!',
        'status': 'operational',
        'version': '1.3.0-robust-monitoring',
        'phase': 2,
        'features': {
            'chat': True,
            'system_monitoring': system_monitor.monitoring_active,
            'error_handling': True,
            'structured_logging': PHASE2_READY,
            'health_checks': True,
            'performance_metrics': True,
            'conversation_analytics': True
        },
        'endpoints': [
            '/health', '/status', '/chat', '/api/chat', '/message', 
            '/sessions', '/metrics', '/system/health', '/system/metrics',
            '/conversation/history', '/conversation/stats', '/errors'
        ]
    })

@app.route('/chat', methods=['POST'])
def chat():
    """Enhanced chat endpoint with robust error handling"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
        
        message = data['message'].strip()
        session_id = data.get('session_id', f'session_{int(datetime.now().timestamp())}')
        
        if not message:
            return jsonify({'error': 'Empty message'}), 400
        
        if len(message) > 1000:
            return jsonify({'error': 'Message too long (max 1000 characters)'}), 400
        
        # Get or create session
        if session_id not in chat_sessions:
            chat_sessions[session_id] = {
                'created': datetime.now().isoformat(),
                'message_count': 0,
                'last_activity': datetime.now().isoformat(),
                'total_response_time': 0.0
            }
        
        # Update session
        session = chat_sessions[session_id]
        session['message_count'] += 1
        session['last_activity'] = datetime.now().isoformat()
        
        # Generate response using enhanced Eliza brain
        context = {
            'uptime_seconds': int((datetime.now() - start_time).total_seconds()),
            'session': session,
            'total_conversations': len(conversation_memory),
            'system_health': system_monitor.check_system_health()['status']
        }
        
        eliza_response = eliza_brain.generate_response(message, context)
        
        # Update session response time tracking
        session['total_response_time'] += eliza_response.get('response_time', 0)
        session['avg_response_time'] = session['total_response_time'] / session['message_count']
        
        # Store conversation with enhanced metadata
        conversation_entry = {
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'user_message': message,
            'eliza_response': eliza_response['response'],
            'category': eliza_response['category'],
            'confidence': eliza_response['confidence'],
            'response_time': eliza_response.get('response_time', 0),
            'system_health': context['system_health']
        }
        conversation_memory.append(conversation_entry)
        
        # Keep only last 200 conversations
        if len(conversation_memory) > 200:
            conversation_memory.pop(0)
        
        return jsonify({
            'response': eliza_response['response'],
            'session_id': session_id,
            'message_count': session['message_count'],
            'category': eliza_response['category'],
            'confidence': eliza_response['confidence'],
            'timestamp': eliza_response['timestamp'],
            'response_time': eliza_response.get('response_time', 0),
            'eliza_uptime': context['uptime_seconds'],
            'system_health': context['system_health'],
            'version': '1.3.0-robust-monitoring'
        })
        
    except Exception as e:
        log_error('chat_endpoint_error', str(e), {'session_id': session_id, 'message_length': len(message) if 'message' in locals() else 0})
        return jsonify({
            'error': 'Chat processing failed',
            'message': 'An error occurred, but the system recovered gracefully',
            'timestamp': datetime.now().isoformat(),
            'support': 'Try rephrasing your message or check /system/health'
        }), 500

@app.route('/api/chat', methods=['POST'])
def api_chat():
    return chat()

@app.route('/message', methods=['POST'])
def message():
    return chat()

@app.route('/system/health')
def system_health():
    """Comprehensive system health endpoint"""
    health_status = system_monitor.check_system_health()
    
    return jsonify({
        'overall_health': health_status,
        'service_info': {
            'version': '1.3.0-robust-monitoring',
            'uptime_seconds': int((datetime.now() - start_time).total_seconds()),
            'total_requests': request_count,
            'active_sessions': len(chat_sessions),
            'total_conversations': len(conversation_memory),
            'error_count': len(error_log)
        },
        'monitoring_status': {
            'active': system_monitor.monitoring_active,
            'last_check': system_monitor.last_check.isoformat(),
            'metrics_history_count': len(system_metrics_history),
            'health_checks_count': len(health_checks)
        }
    })

@app.route('/system/metrics')
def system_metrics():
    """Real-time system metrics"""
    metrics = system_monitor.get_system_metrics()
    
    return jsonify({
        'current_metrics': metrics,
        'history_available': len(system_metrics_history),
        'monitoring_active': system_monitor.monitoring_active,
        'thresholds': system_monitor.alert_thresholds
    })

@app.route('/metrics')
def service_metrics():
    """Service-level metrics"""
    uptime_seconds = int((datetime.now() - start_time).total_seconds())
    
    return jsonify({
        'service': 'xmrt-eliza',
        'version': '1.3.0-robust-monitoring',
        'uptime_seconds': uptime_seconds,
        'uptime_human': str(timedelta(seconds=uptime_seconds)),
        'total_requests': request_count,
        'active_sessions': len(chat_sessions),
        'total_conversations': len(conversation_memory),
        'conversation_stats': eliza_brain.conversation_stats,
        'error_count': len(error_log),
        'system_health': system_monitor.check_system_health()['status'],
        'requests_per_minute': round(request_count / max(1, uptime_seconds / 60), 2),
        'average_session_length': sum(s['message_count'] for s in chat_sessions.values()) / max(1, len(chat_sessions)),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/sessions')
def sessions():
    return jsonify({
        'active_sessions': len(chat_sessions),
        'total_conversations': len(conversation_memory),
        'sessions': {
            session_id: {
                'message_count': session['message_count'],
                'last_activity': session['last_activity'],
                'avg_response_time': session.get('avg_response_time', 0)
            }
            for session_id, session in chat_sessions.items()
        }
    })

@app.route('/conversation/history')
def conversation_history():
    limit = request.args.get('limit', 20, type=int)
    limit = min(limit, 100)  # Cap at 100
    
    return jsonify({
        'conversations': conversation_memory[-limit:],
        'total_conversations': len(conversation_memory),
        'limit': limit
    })

@app.route('/conversation/stats')
def conversation_stats():
    return jsonify({
        'total_conversations': len(conversation_memory),
        'eliza_stats': eliza_brain.conversation_stats,
        'category_distribution': eliza_brain.conversation_stats['category_counts'],
        'average_response_time': eliza_brain.conversation_stats['average_response_time'],
        'error_rate': eliza_brain.conversation_stats['error_count'] / max(1, eliza_brain.conversation_stats['total_responses'])
    })

@app.route('/errors')
def error_history():
    return jsonify({
        'recent_errors': error_log[-20:],  # Last 20 errors
        'total_errors': len(error_log),
        'error_types': list(set(error['type'] for error in error_log)),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/status')
def status():
    health_status = system_monitor.check_system_health()
    
    return jsonify({
        'service': 'xmrt-eliza',
        'status': 'running',
        'version': '1.3.0-robust-monitoring',
        'phase': 2,
        'uptime_seconds': int((datetime.now() - start_time).total_seconds()),
        'total_requests': request_count,
        'python_version': sys.version,
        'system_health': health_status['status'],
        'monitoring_features': {
            'system_metrics': system_monitor.monitoring_active,
            'error_logging': True,
            'structured_logging': PHASE2_READY,
            'health_checks': True,
            'performance_tracking': True
        },
        'chat_features': {
            'active_sessions': len(chat_sessions),
            'total_conversations': len(conversation_memory),
            'pattern_categories': len(eliza_brain.patterns),
            'conversation_analytics': True,
            'robust_error_handling': True
        }
    })

@app.route('/api/health')
def api_health():
    return health_check()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    
    print(f"🚀 Starting XMRT Eliza Phase 2: Robust Monitoring System")
    print(f"📊 Version: 1.3.0-robust-monitoring")
    print(f"🔧 Port: {port}")
    print(f"📈 System monitoring: {'Active' if system_monitor.monitoring_active else 'Limited'}")
    print(f"🧠 Chat engine: Enhanced with {len(eliza_brain.patterns)} pattern categories")
    print(f"⏰ Start time: {start_time}")
    
    # Log startup
    logger.info("XMRT Eliza Phase 2 starting", 
                version="1.3.0-robust-monitoring",
                monitoring_active=system_monitor.monitoring_active,
                patterns_loaded=len(eliza_brain.patterns))
    
    app.run(host='0.0.0.0', port=port, debug=False)
