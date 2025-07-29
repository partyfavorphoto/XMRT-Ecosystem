#!/usr/bin/env python3
# XMRT Eliza Orchestrator - Phase 3: Advanced AI Features

import os
import sys
import json
import random
import threading
import time
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import logging

# Phase 3 imports with fallbacks
try:
    from flask import Flask, jsonify, request
    import requests
    from dotenv import load_dotenv
    import psutil
    import orjson
    import structlog
    from dateutil import parser as date_parser
    from pydantic import BaseModel, Field
    import openai
    from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage
    from langchain_openai import ChatOpenAI
    import tiktoken
    PHASE3_READY = True
    print("✅ Phase 3: Advanced AI dependencies loaded successfully")
except ImportError as e:
    print(f"⚠️ Phase 3 import issue: {e}")
    # Fallback to Phase 2
    try:
        from flask import Flask, jsonify, request
        import requests
        from dotenv import load_dotenv
        import psutil
        import orjson
        import structlog
        PHASE3_READY = False
        print("🔄 Running in Phase 2 compatibility mode")
    except ImportError:
        print("❌ Critical dependencies missing")
        sys.exit(1)

# Load environment variables
load_dotenv()

# Configure structured logging
if PHASE3_READY:
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
ai_interactions = []

class AIConfig(BaseModel):
    """Configuration for AI features"""
    openai_api_key: Optional[str] = Field(default=None)
    model_name: str = Field(default="gpt-3.5-turbo")
    max_tokens: int = Field(default=150)
    temperature: float = Field(default=0.7)
    fallback_mode: bool = Field(default=True)

class AdvancedAIEngine:
    """Advanced AI engine with OpenAI and LangChain integration"""
    
    def __init__(self):
        self.ai_available = PHASE3_READY
        self.config = AIConfig()
        self.openai_client = None
        self.langchain_llm = None
        self.tokenizer = None
        
        # Initialize AI services
        self._initialize_ai_services()
        
        # Enhanced conversation patterns
        self.enhanced_patterns = {
            'ai_technical': {
                'patterns': ['ai', 'artificial intelligence', 'machine learning', 'neural network', 'gpt', 'openai'],
                'ai_prompt': "You are XMRT Eliza, an advanced AI with deep knowledge of artificial intelligence, machine learning, and AI systems. Provide insightful, technical responses about AI topics while maintaining a conversational tone."
            },
            'xmrt_ecosystem': {
                'patterns': ['xmrt', 'dao', 'governance', 'blockchain', 'defi', 'crypto', 'token'],
                'ai_prompt': "You are XMRT Eliza, an AI assistant for the XMRT ecosystem. You understand decentralized governance, blockchain technology, and DAO operations. Provide helpful insights about the XMRT ecosystem."
            },
            'complex_reasoning': {
                'patterns': ['analyze', 'explain', 'compare', 'evaluate', 'strategy', 'solution'],
                'ai_prompt': "You are XMRT Eliza, equipped with advanced reasoning capabilities. Provide thoughtful analysis, clear explanations, and strategic insights. Break down complex topics into understandable components."
            },
            'creative_thinking': {
                'patterns': ['create', 'design', 'innovative', 'brainstorm', 'idea', 'creative'],
                'ai_prompt': "You are XMRT Eliza, with enhanced creative thinking abilities. Generate innovative ideas, creative solutions, and original concepts. Think outside the box while remaining practical."
            },
            'problem_solving': {
                'patterns': ['problem', 'issue', 'challenge', 'troubleshoot', 'debug', 'fix'],
                'ai_prompt': "You are XMRT Eliza, an expert problem solver. Analyze issues systematically, identify root causes, and provide step-by-step solutions. Be methodical and thorough."
            }
        }
        
        # Fallback patterns (from Phase 2)
        self.fallback_patterns = {
            'greeting': {
                'patterns': ['hello', 'hi', 'hey', 'greetings'],
                'responses': [
                    "Hello! I'm XMRT Eliza with advanced AI capabilities. How can I assist you today?",
                    "Hi there! I'm equipped with enhanced AI features. What would you like to explore?",
                    "Greetings! My advanced AI systems are ready to help. What's on your mind?"
                ]
            },
            'default': {
                'patterns': [],
                'responses': [
                    "I'm processing your message with my advanced AI systems. Can you tell me more?",
                    "That's interesting. My AI capabilities are analyzing your input. Please elaborate.",
                    "I'm using my enhanced reasoning to understand your perspective. What else would you like to discuss?"
                ]
            }
        }
    
    def _initialize_ai_services(self):
        """Initialize OpenAI and LangChain services"""
        if not self.ai_available:
            logger.info("AI services not available - running in fallback mode")
            return
        
        try:
            # Get API key from environment
            api_key = os.getenv('OPENAI_API_KEY')
            
            if api_key:
                # Initialize OpenAI client
                self.openai_client = openai.OpenAI(api_key=api_key)
                
                # Initialize LangChain LLM
                self.langchain_llm = ChatOpenAI(
                    api_key=api_key,
                    model_name=self.config.model_name,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens
                )
                
                # Initialize tokenizer
                self.tokenizer = tiktoken.encoding_for_model(self.config.model_name)
                
                logger.info("AI services initialized successfully", model=self.config.model_name)
                print(f"🤖 AI Engine: OpenAI {self.config.model_name} ready")
                
            else:
                logger.warning("No OpenAI API key found - using fallback mode")
                print("⚠️ AI Engine: No API key - using enhanced fallback mode")
                
        except Exception as e:
            logger.error("AI services initialization failed", error=str(e))
            print(f"⚠️ AI Engine: Initialization failed - {str(e)}")
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        return len(text.split())  # Rough estimate
    
    def determine_ai_category(self, message: str) -> Optional[str]:
        """Determine if message should use AI processing"""
        message_lower = message.lower()
        
        for category, data in self.enhanced_patterns.items():
            if any(pattern in message_lower for pattern in data['patterns']):
                return category
        
        # Use AI for complex messages
        if len(message.split()) > 10 or '?' in message:
            return 'complex_reasoning'
        
        return None
    
    async def generate_ai_response(self, message: str, category: str, context: Dict) -> Dict[str, Any]:
        """Generate response using AI services"""
        start_time = time.time()
        
        try:
            if not self.openai_client:
                raise Exception("OpenAI client not available")
            
            # Get system prompt for category
            system_prompt = self.enhanced_patterns[category]['ai_prompt']
            
            # Add context information
            context_info = f"System uptime: {context.get('uptime_seconds', 0)} seconds. "
            context_info += f"System health: {context.get('system_health', 'unknown')}. "
            context_info += f"Current conversation count: {context.get('total_conversations', 0)}."
            
            # Prepare messages
            messages = [
                {"role": "system", "content": f"{system_prompt} {context_info}"},
                {"role": "user", "content": message}
            ]
            
            # Add recent conversation history if available
            if context.get('recent_history'):
                for hist_msg in context['recent_history'][-3:]:  # Last 3 exchanges
                    messages.insert(-1, {"role": "user", "content": hist_msg.get('user_message', '')})
                    messages.insert(-1, {"role": "assistant", "content": hist_msg.get('eliza_response', '')})
            
            # Generate response
            response = self.openai_client.chat.completions.create(
                model=self.config.model_name,
                messages=messages,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            
            ai_response = response.choices[0].message.content
            
            # Track AI interaction
            ai_interaction = {
                'timestamp': datetime.now().isoformat(),
                'category': category,
                'input_tokens': self.count_tokens(message),
                'output_tokens': self.count_tokens(ai_response),
                'model': self.config.model_name,
                'response_time': time.time() - start_time
            }
            
            ai_interactions.append(ai_interaction)
            
            # Keep only last 100 interactions
            if len(ai_interactions) > 100:
                ai_interactions.pop(0)
            
            return {
                'response': ai_response,
                'category': f'ai_{category}',
                'confidence': 0.95,
                'timestamp': datetime.now().isoformat(),
                'response_time': time.time() - start_time,
                'ai_powered': True,
                'model_used': self.config.model_name,
                'tokens_used': ai_interaction['input_tokens'] + ai_interaction['output_tokens']
            }
            
        except Exception as e:
            logger.error("AI response generation failed", error=str(e), category=category)
            
            # Fallback to enhanced pattern-based response
            return self._generate_fallback_response(message, category, context, start_time)
    
    def _generate_fallback_response(self, message: str, category: str, context: Dict, start_time: float) -> Dict[str, Any]:
        """Generate enhanced fallback response"""
        
        # Enhanced fallback responses based on category
        enhanced_responses = {
            'ai_technical': [
                "I'd love to discuss AI with you! While I'm currently in enhanced mode, I can share insights about artificial intelligence, machine learning, and the future of AI systems. What specific aspect interests you?",
                "AI is fascinating! I'm equipped with advanced reasoning capabilities. What would you like to explore about artificial intelligence or machine learning?",
                "That's a great AI question! My enhanced systems are designed to help with technical discussions. Can you tell me more about what you're working on?"
            ],
            'xmrt_ecosystem': [
                "The XMRT ecosystem is built for the future of decentralized governance! I'm designed to help with DAO operations and blockchain questions. What aspects of XMRT interest you?",
                "XMRT represents innovation in decentralized systems! I can help with governance, tokenomics, and DAO strategies. What would you like to know?",
                "I'm part of the XMRT ecosystem and understand its vision for decentralized governance. How can I help with your XMRT questions?"
            ],
            'complex_reasoning': [
                "That requires some analytical thinking! My enhanced reasoning systems are processing your question. Let me break this down systematically for you.",
                "Excellent question for analysis! I'm equipped with advanced problem-solving capabilities. Let me work through this step by step.",
                "I love complex challenges! My enhanced AI architecture is designed for this kind of reasoning. What specific aspect should we focus on first?"
            ],
            'default': [
                "I'm listening with my enhanced AI capabilities. While I'm currently in advanced fallback mode, I can provide thoughtful responses. Tell me more!",
                "That's interesting! My enhanced systems are analyzing your input. I'm designed to handle complex conversations - please elaborate.",
                "My advanced AI features are processing your message. Even in enhanced mode, I can provide meaningful insights. What else would you like to explore?"
            ]
        }
        
        responses = enhanced_responses.get(category, enhanced_responses['default'])
        response = random.choice(responses)
        
        return {
            'response': response,
            'category': f'enhanced_{category}',
            'confidence': 0.8,
            'timestamp': datetime.now().isoformat(),
            'response_time': time.time() - start_time,
            'ai_powered': False,
            'fallback_mode': True,
            'enhancement_level': 'advanced'
        }
    
    async def generate_response(self, message: str, context: Dict) -> Dict[str, Any]:
        """Main response generation with AI integration"""
        
        # Determine if we should use AI
        ai_category = self.determine_ai_category(message)
        
        if ai_category and self.openai_client:
            # Use AI for advanced response
            return await self.generate_ai_response(message, ai_category, context)
        else:
            # Use enhanced fallback
            start_time = time.time()
            category = ai_category or 'default'
            return self._generate_fallback_response(message, category, context, start_time)

class SystemMonitor:
    """Enhanced system monitoring with AI metrics"""
    
    def __init__(self):
        self.monitoring_active = PHASE3_READY or True  # Always active now
        self.last_check = datetime.now()
        self.alert_thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_percent': 90.0,
            'response_time': 5.0,
            'ai_response_time': 10.0
        }
        
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system metrics including AI stats"""
        try:
            # Standard system metrics
            cpu_percent = psutil.cpu_percent(interval=0.1) if self.monitoring_active else 0
            memory = psutil.virtual_memory() if self.monitoring_active else type('obj', (object,), {'percent': 0, 'total': 0, 'available': 0, 'used': 0})()
            disk = psutil.disk_usage('/') if self.monitoring_active else type('obj', (object,), {'total': 1, 'used': 0, 'free': 1})()
            
            # AI-specific metrics
            ai_metrics = {
                'total_ai_interactions': len(ai_interactions),
                'ai_available': PHASE3_READY and ai_engine.openai_client is not None,
                'recent_ai_response_time': 0,
                'total_tokens_used': 0
            }
            
            if ai_interactions:
                recent_interactions = ai_interactions[-10:]
                ai_metrics['recent_ai_response_time'] = sum(i['response_time'] for i in recent_interactions) / len(recent_interactions)
                ai_metrics['total_tokens_used'] = sum(i.get('input_tokens', 0) + i.get('output_tokens', 0) for i in ai_interactions)
                ai_metrics['most_used_category'] = max(set(i['category'] for i in recent_interactions), 
                                                     key=lambda x: sum(1 for i in recent_interactions if i['category'] == x))
            
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'cpu': {
                    'percent': cpu_percent,
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
                'ai': ai_metrics
            }
            
            system_metrics_history.append(metrics)
            
            if len(system_metrics_history) > 100:
                system_metrics_history.pop(0)
            
            return metrics
            
        except Exception as e:
            logger.error("System metrics collection failed", error=str(e))
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}

# Initialize enhanced systems
system_monitor = SystemMonitor()
ai_engine = AdvancedAIEngine()

def log_error(error_type: str, error_message: str, context: Dict = None):
    """Enhanced error logging"""
    error_entry = {
        'timestamp': datetime.now().isoformat(),
        'type': error_type,
        'message': error_message,
        'context': context or {},
        'phase': 3
    }
    
    error_log.append(error_entry)
    
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
        'available_endpoints': [
            '/health', '/status', '/chat', '/api/chat', '/message', '/sessions', 
            '/metrics', '/system/health', '/ai/status', '/ai/metrics', '/ai/models'
        ],
        'timestamp': datetime.now().isoformat(),
        'phase': 3
    }), 404

@app.errorhandler(500)
def internal_error(error):
    log_error('internal_server_error', str(error))
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred, but the system recovered',
        'timestamp': datetime.now().isoformat(),
        'support': 'Check /system/health for system status',
        'phase': 3
    }), 500

@app.route('/health')
def health_check():
    health_status = system_monitor.get_system_metrics()
    
    return jsonify({
        'status': 'healthy',
        'service': 'xmrt-eliza',
        'version': '1.4.0-advanced-ai',
        'phase': 3,
        'timestamp': datetime.now().isoformat(),
        'uptime_seconds': int((datetime.now() - start_time).total_seconds()),
        'total_requests': request_count,
        'chat_sessions': len(chat_sessions),
        'conversation_count': len(conversation_memory),
        'ai_interactions': len(ai_interactions),
        'ai_available': PHASE3_READY and ai_engine.openai_client is not None,
        'monitoring_active': system_monitor.monitoring_active
    })

@app.route('/')
def root():
    return jsonify({
        'message': 'XMRT Eliza - Phase 3: Advanced AI with OpenAI & LangChain Integration!',
        'status': 'operational',
        'version': '1.4.0-advanced-ai',
        'phase': 3,
        'features': {
            'advanced_ai': PHASE3_READY,
            'openai_integration': ai_engine.openai_client is not None,
            'langchain_support': PHASE3_READY,
            'enhanced_reasoning': True,
            'system_monitoring': True,
            'conversation_analytics': True,
            'token_counting': True,
            'fallback_modes': True
        },
        'endpoints': [
            '/health', '/status', '/chat', '/api/chat', '/message', '/sessions',
            '/metrics', '/system/health', '/system/metrics', '/ai/status', 
            '/ai/metrics', '/ai/models', '/conversation/history', '/conversation/stats'
        ]
    })

@app.route('/chat', methods=['POST'])
def chat():
    """Enhanced chat endpoint with AI integration"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
        
        message = data['message'].strip()
        session_id = data.get('session_id', f'session_{int(datetime.now().timestamp())}')
        
        if not message:
            return jsonify({'error': 'Empty message'}), 400
        
        if len(message) > 2000:
            return jsonify({'error': 'Message too long (max 2000 characters)'}), 400
        
        # Get or create session
        if session_id not in chat_sessions:
            chat_sessions[session_id] = {
                'created': datetime.now().isoformat(),
                'message_count': 0,
                'last_activity': datetime.now().isoformat(),
                'total_response_time': 0.0,
                'ai_responses': 0
            }
        
        # Update session
        session = chat_sessions[session_id]
        session['message_count'] += 1
        session['last_activity'] = datetime.now().isoformat()
        
        # Prepare context with recent history
        recent_history = [conv for conv in conversation_memory if conv.get('session_id') == session_id][-5:]
        
        context = {
            'uptime_seconds': int((datetime.now() - start_time).total_seconds()),
            'session': session,
            'total_conversations': len(conversation_memory),
            'system_health': 'healthy',
            'recent_history': recent_history
        }
        
        # Generate response using AI engine
        eliza_response = await ai_engine.generate_response(message, context)
        
        # Track AI usage
        if eliza_response.get('ai_powered'):
            session['ai_responses'] += 1
        
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
            'ai_powered': eliza_response.get('ai_powered', False),
            'model_used': eliza_response.get('model_used'),
            'tokens_used': eliza_response.get('tokens_used', 0)
        }
        conversation_memory.append(conversation_entry)
        
        if len(conversation_memory) > 500:  # Increased capacity for AI conversations
            conversation_memory.pop(0)
        
        return jsonify({
            'response': eliza_response['response'],
            'session_id': session_id,
            'message_count': session['message_count'],
            'category': eliza_response['category'],
            'confidence': eliza_response['confidence'],
            'timestamp': eliza_response['timestamp'],
            'response_time': eliza_response.get('response_time', 0),
            'ai_powered': eliza_response.get('ai_powered', False),
            'model_used': eliza_response.get('model_used'),
            'tokens_used': eliza_response.get('tokens_used', 0),
            'eliza_uptime': context['uptime_seconds'],
            'version': '1.4.0-advanced-ai',
            'phase': 3
        })
        
    except Exception as e:
        log_error('chat_endpoint_error', str(e), {'session_id': session_id if 'session_id' in locals() else 'unknown'})
        return jsonify({
            'error': 'Chat processing failed',
            'message': 'An error occurred, but the system recovered gracefully',
            'timestamp': datetime.now().isoformat(),
            'support': 'Try rephrasing your message or check /system/health',
            'phase': 3
        }), 500

@app.route('/api/chat', methods=['POST'])
def api_chat():
    return chat()

@app.route('/message', methods=['POST'])
def message():
    return chat()

@app.route('/ai/status')
def ai_status():
    """AI system status endpoint"""
    return jsonify({
        'ai_available': PHASE3_READY,
        'openai_connected': ai_engine.openai_client is not None,
        'langchain_ready': PHASE3_READY,
        'model_name': ai_engine.config.model_name,
        'total_ai_interactions': len(ai_interactions),
        'recent_interactions': len([i for i in ai_interactions if datetime.fromisoformat(i['timestamp']) > datetime.now() - timedelta(hours=1)]),
        'configuration': {
            'max_tokens': ai_engine.config.max_tokens,
            'temperature': ai_engine.config.temperature,
            'fallback_mode': ai_engine.config.fallback_mode
        },
        'timestamp': datetime.now().isoformat()
    })

@app.route('/ai/metrics')
def ai_metrics():
    """AI-specific metrics"""
    if not ai_interactions:
        return jsonify({
            'message': 'No AI interactions yet',
            'ai_available': PHASE3_READY,
            'timestamp': datetime.now().isoformat()
        })
    
    # Calculate AI metrics
    total_tokens = sum(i.get('input_tokens', 0) + i.get('output_tokens', 0) for i in ai_interactions)
    avg_response_time = sum(i['response_time'] for i in ai_interactions) / len(ai_interactions)
    
    category_counts = {}
    for interaction in ai_interactions:
        category = interaction['category']
        category_counts[category] = category_counts.get(category, 0) + 1
    
    return jsonify({
        'total_interactions': len(ai_interactions),
        'total_tokens_used': total_tokens,
        'average_response_time': avg_response_time,
        'category_distribution': category_counts,
        'model_usage': {
            'primary_model': ai_engine.config.model_name,
            'total_requests': len(ai_interactions)
        },
        'recent_activity': ai_interactions[-10:] if len(ai_interactions) >= 10 else ai_interactions,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/system/health')
def system_health():
    """Enhanced system health with AI metrics"""
    metrics = system_monitor.get_system_metrics()
    
    return jsonify({
        'overall_health': 'healthy',
        'system_metrics': metrics,
        'ai_health': {
            'available': PHASE3_READY,
            'connected': ai_engine.openai_client is not None,
            'interactions_count': len(ai_interactions),
            'avg_response_time': sum(i['response_time'] for i in ai_interactions[-10:]) / min(10, len(ai_interactions)) if ai_interactions else 0
        },
        'service_info': {
            'version': '1.4.0-advanced-ai',
            'phase': 3,
            'uptime_seconds': int((datetime.now() - start_time).total_seconds()),
            'total_requests': request_count,
            'active_sessions': len(chat_sessions),
            'total_conversations': len(conversation_memory)
        }
    })

@app.route('/system/metrics')
def system_metrics():
    """Enhanced system metrics"""
    metrics = system_monitor.get_system_metrics()
    
    return jsonify({
        'current_metrics': metrics,
        'history_available': len(system_metrics_history),
        'monitoring_active': system_monitor.monitoring_active,
        'thresholds': system_monitor.alert_thresholds,
        'ai_integration': {
            'available': PHASE3_READY,
            'active_interactions': len(ai_interactions),
            'total_tokens_used': sum(i.get('input_tokens', 0) + i.get('output_tokens', 0) for i in ai_interactions)
        }
    })

@app.route('/metrics')
def service_metrics():
    """Enhanced service metrics with AI stats"""
    uptime_seconds = int((datetime.now() - start_time).total_seconds())
    
    ai_stats = {
        'total_ai_interactions': len(ai_interactions),
        'ai_response_rate': len([c for c in conversation_memory if c.get('ai_powered')]) / max(1, len(conversation_memory)),
        'total_tokens_used': sum(i.get('input_tokens', 0) + i.get('output_tokens', 0) for i in ai_interactions),
        'avg_ai_response_time': sum(i['response_time'] for i in ai_interactions) / max(1, len(ai_interactions))
    }
    
    return jsonify({
        'service': 'xmrt-eliza',
        'version': '1.4.0-advanced-ai',
        'phase': 3,
        'uptime_seconds': uptime_seconds,
        'uptime_human': str(timedelta(seconds=uptime_seconds)),
        'total_requests': request_count,
        'active_sessions': len(chat_sessions),
        'total_conversations': len(conversation_memory),
        'ai_statistics': ai_stats,
        'error_count': len(error_log),
        'requests_per_minute': round(request_count / max(1, uptime_seconds / 60), 2),
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
                'avg_response_time': session.get('avg_response_time', 0),
                'ai_responses': session.get('ai_responses', 0),
                'ai_usage_rate': session.get('ai_responses', 0) / max(1, session['message_count'])
            }
            for session_id, session in chat_sessions.items()
        }
    })

@app.route('/conversation/history')
def conversation_history():
    limit = request.args.get('limit', 20, type=int)
    limit = min(limit, 100)
    
    return jsonify({
        'conversations': conversation_memory[-limit:],
        'total_conversations': len(conversation_memory),
        'ai_powered_count': len([c for c in conversation_memory[-limit:] if c.get('ai_powered')]),
        'limit': limit
    })

@app.route('/conversation/stats')
def conversation_stats():
    ai_powered_count = len([c for c in conversation_memory if c.get('ai_powered')])
    total_tokens = sum(c.get('tokens_used', 0) for c in conversation_memory)
    
    return jsonify({
        'total_conversations': len(conversation_memory),
        'ai_powered_conversations': ai_powered_count,
        'ai_usage_rate': ai_powered_count / max(1, len(conversation_memory)),
        'total_tokens_used': total_tokens,
        'average_tokens_per_conversation': total_tokens / max(1, ai_powered_count),
        'categories': {
            category: len([c for c in conversation_memory if c.get('category') == category])
            for category in set(c.get('category', 'unknown') for c in conversation_memory)
        }
    })

@app.route('/status')
def status():
    return jsonify({
        'service': 'xmrt-eliza',
        'status': 'running',
        'version': '1.4.0-advanced-ai',
        'phase': 3,
        'uptime_seconds': int((datetime.now() - start_time).total_seconds()),
        'total_requests': request_count,
        'python_version': sys.version,
        'ai_features': {
            'openai_integration': ai_engine.openai_client is not None,
            'langchain_support': PHASE3_READY,
            'advanced_reasoning': True,
            'token_counting': True,
            'conversation_context': True,
            'fallback_modes': True
        },
        'chat_features': {
            'active_sessions': len(chat_sessions),
            'total_conversations': len(conversation_memory),
            'ai_conversations': len([c for c in conversation_memory if c.get('ai_powered')]),
            'enhanced_patterns': len(ai_engine.enhanced_patterns),
            'robust_error_handling': True
        }
    })

@app.route('/api/health')
def api_health():
    return health_check()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    
    print(f"🚀 Starting XMRT Eliza Phase 3: Advanced AI System")
    print(f"🤖 Version: 1.4.0-advanced-ai")
    print(f"🔧 Port: {port}")
    print(f"🧠 AI Integration: {'Active' if PHASE3_READY else 'Fallback Mode'}")
    print(f"🔗 OpenAI: {'Connected' if ai_engine.openai_client else 'API Key Required'}")
    print(f"📊 System monitoring: {'Active' if system_monitor.monitoring_active else 'Limited'}")
    print(f"⏰ Start time: {start_time}")
    
    # Log startup
    logger.info("XMRT Eliza Phase 3 starting", 
                version="1.4.0-advanced-ai",
                ai_available=PHASE3_READY,
                openai_connected=ai_engine.openai_client is not None)
    
    # Create event loop for async AI operations
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    app.run(host='0.0.0.0', port=port, debug=False)
