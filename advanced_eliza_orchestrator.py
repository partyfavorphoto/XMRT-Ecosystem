#!/usr/bin/env python3
# XMRT Eliza Orchestrator - Phase 3 Lite with Web Chat Interface

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

# Phase 3 Lite imports - simplified
try:
    from flask import Flask, jsonify, request, render_template_string, send_from_directory
    import requests
    from dotenv import load_dotenv
    import psutil
    import orjson
    import structlog
    from dateutil import parser as date_parser
    from pydantic import BaseModel, Field
    import openai
    PHASE3_LITE_READY = True
    print("✅ Phase 3 Lite: Simplified AI dependencies loaded successfully")
except ImportError as e:
    print(f"⚠️ Phase 3 Lite import issue: {e}")
    # Fallback to Phase 2
    try:
        from flask import Flask, jsonify, request, render_template_string
        import requests
        from dotenv import load_dotenv
        import psutil
        import orjson
        import structlog
        PHASE3_LITE_READY = False
        print("🔄 Running in Phase 2 compatibility mode")
    except ImportError:
        print("❌ Critical dependencies missing")
        sys.exit(1)

# Load environment variables
load_dotenv()

# Configure structured logging
if PHASE3_LITE_READY:
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

# Web Chat Interface HTML Template
CHAT_INTERFACE_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>XMRT Eliza - AI Chat Interface</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .chat-container {
            width: 90%;
            max-width: 800px;
            height: 90vh;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .chat-header {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            padding: 20px;
            text-align: center;
            position: relative;
        }
        
        .chat-header h1 {
            font-size: 24px;
            margin-bottom: 5px;
        }
        
        .chat-header .subtitle {
            font-size: 14px;
            opacity: 0.9;
        }
        
        .status-indicator {
            position: absolute;
            top: 20px;
            right: 20px;
            width: 12px;
            height: 12px;
            background: #4CAF50;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .chat-messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            background: #f8f9fa;
        }
        
        .message {
            margin-bottom: 15px;
            display: flex;
            align-items: flex-start;
        }
        
        .message.user {
            justify-content: flex-end;
        }
        
        .message.eliza {
            justify-content: flex-start;
        }
        
        .message-content {
            max-width: 70%;
            padding: 12px 16px;
            border-radius: 18px;
            font-size: 14px;
            line-height: 1.4;
        }
        
        .message.user .message-content {
            background: #007bff;
            color: white;
            border-bottom-right-radius: 4px;
        }
        
        .message.eliza .message-content {
            background: white;
            color: #333;
            border: 1px solid #e0e0e0;
            border-bottom-left-radius: 4px;
        }
        
        .message-meta {
            font-size: 11px;
            opacity: 0.7;
            margin-top: 4px;
        }
        
        .ai-indicator {
            display: inline-block;
            background: #4CAF50;
            color: white;
            font-size: 10px;
            padding: 2px 6px;
            border-radius: 10px;
            margin-left: 8px;
        }
        
        .chat-input-container {
            padding: 20px;
            background: white;
            border-top: 1px solid #e0e0e0;
        }
        
        .chat-input-form {
            display: flex;
            gap: 10px;
        }
        
        .chat-input {
            flex: 1;
            padding: 12px 16px;
            border: 2px solid #e0e0e0;
            border-radius: 25px;
            font-size: 14px;
            outline: none;
            transition: border-color 0.3s;
        }
        
        .chat-input:focus {
            border-color: #007bff;
        }
        
        .send-button {
            padding: 12px 20px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.3s;
        }
        
        .send-button:hover {
            background: #0056b3;
        }
        
        .send-button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        
        .typing-indicator {
            display: none;
            padding: 10px 16px;
            font-style: italic;
            color: #666;
            font-size: 13px;
        }
        
        .welcome-message {
            text-align: center;
            padding: 40px 20px;
            color: #666;
        }
        
        .welcome-message h3 {
            color: #333;
            margin-bottom: 10px;
        }
        
        .system-info {
            position: absolute;
            top: 20px;
            left: 20px;
            font-size: 12px;
            opacity: 0.8;
        }
        
        @media (max-width: 600px) {
            .chat-container {
                width: 100%;
                height: 100vh;
                border-radius: 0;
            }
            
            .message-content {
                max-width: 85%;
            }
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <div class="system-info">
                <div id="version">Loading...</div>
                <div id="ai-status">Checking AI...</div>
            </div>
            <h1>🤖 XMRT Eliza</h1>
            <div class="subtitle">AI-Powered Conversational Assistant</div>
            <div class="status-indicator" id="status-indicator"></div>
        </div>
        
        <div class="chat-messages" id="chat-messages">
            <div class="welcome-message">
                <h3>Welcome to XMRT Eliza! 👋</h3>
                <p>I'm your AI assistant with advanced reasoning capabilities.</p>
                <p>Ask me about AI, blockchain, XMRT ecosystem, or anything else!</p>
            </div>
        </div>
        
        <div class="typing-indicator" id="typing-indicator">
            Eliza is thinking...
        </div>
        
        <div class="chat-input-container">
            <form class="chat-input-form" id="chat-form">
                <input 
                    type="text" 
                    class="chat-input" 
                    id="message-input" 
                    placeholder="Type your message here..." 
                    autocomplete="off"
                    maxlength="2000"
                >
                <button type="submit" class="send-button" id="send-button">Send</button>
            </form>
        </div>
    </div>

    <script>
        class ElizaChat {
            constructor() {
                this.sessionId = 'web_session_' + Date.now();
                this.messagesContainer = document.getElementById('chat-messages');
                this.messageInput = document.getElementById('message-input');
                this.sendButton = document.getElementById('send-button');
                this.chatForm = document.getElementById('chat-form');
                this.typingIndicator = document.getElementById('typing-indicator');
                
                this.initializeEventListeners();
                this.loadSystemInfo();
                this.messageInput.focus();
            }
            
            initializeEventListeners() {
                this.chatForm.addEventListener('submit', (e) => {
                    e.preventDefault();
                    this.sendMessage();
                });
                
                this.messageInput.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        this.sendMessage();
                    }
                });
            }
            
            async loadSystemInfo() {
                try {
                    const response = await fetch('/health');
                    const data = await response.json();
                    
                    document.getElementById('version').textContent = `v${data.version || 'unknown'}`;
                    
                    // Check AI status
                    const aiResponse = await fetch('/ai/status');
                    const aiData = await aiResponse.json();
                    
                    const aiConnected = aiData.openai_connected;
                    document.getElementById('ai-status').textContent = aiConnected ? 'AI: Connected' : 'AI: Fallback Mode';
                    
                    // Update status indicator color
                    const indicator = document.getElementById('status-indicator');
                    indicator.style.background = aiConnected ? '#4CAF50' : '#FF9800';
                    
                } catch (error) {
                    console.error('Failed to load system info:', error);
                    document.getElementById('version').textContent = 'v1.4.1-ai-lite';
                    document.getElementById('ai-status').textContent = 'AI: Unknown';
                }
            }
            
            async sendMessage() {
                const message = this.messageInput.value.trim();
                if (!message) return;
                
                // Add user message to chat
                this.addMessage(message, 'user');
                
                // Clear input and show typing
                this.messageInput.value = '';
                this.setLoading(true);
                
                try {
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            message: message,
                            session_id: this.sessionId
                        })
                    });
                    
                    if (response.ok) {
                        const data = await response.json();
                        
                        // Add Eliza's response
                        this.addMessage(data.response, 'eliza', {
                            ai_powered: data.ai_powered,
                            category: data.category,
                            confidence: data.confidence,
                            response_time: data.response_time,
                            tokens_used: data.tokens_used,
                            model_used: data.model_used
                        });
                        
                    } else {
                        this.addMessage('Sorry, I encountered an error. Please try again.', 'eliza');
                    }
                    
                } catch (error) {
                    console.error('Chat error:', error);
                    this.addMessage('Connection error. Please check your internet connection.', 'eliza');
                } finally {
                    this.setLoading(false);
                    this.messageInput.focus();
                }
            }
            
            addMessage(content, sender, metadata = {}) {
                // Remove welcome message if it exists
                const welcomeMessage = this.messagesContainer.querySelector('.welcome-message');
                if (welcomeMessage) {
                    welcomeMessage.remove();
                }
                
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${sender}`;
                
                const contentDiv = document.createElement('div');
                contentDiv.className = 'message-content';
                contentDiv.textContent = content;
                
                messageDiv.appendChild(contentDiv);
                
                // Add metadata for Eliza messages
                if (sender === 'eliza' && Object.keys(metadata).length > 0) {
                    const metaDiv = document.createElement('div');
                    metaDiv.className = 'message-meta';
                    
                    let metaText = '';
                    if (metadata.ai_powered) {
                        metaText += `<span class="ai-indicator">AI</span>`;
                    }
                    if (metadata.response_time) {
                        metaText += ` ${(metadata.response_time * 1000).toFixed(0)}ms`;
                    }
                    if (metadata.confidence) {
                        metaText += ` • ${(metadata.confidence * 100).toFixed(0)}% confidence`;
                    }
                    if (metadata.tokens_used) {
                        metaText += ` • ${metadata.tokens_used} tokens`;
                    }
                    
                    metaDiv.innerHTML = metaText;
                    messageDiv.appendChild(metaDiv);
                }
                
                this.messagesContainer.appendChild(messageDiv);
                this.scrollToBottom();
            }
            
            setLoading(loading) {
                this.sendButton.disabled = loading;
                this.messageInput.disabled = loading;
                this.typingIndicator.style.display = loading ? 'block' : 'none';
                
                if (loading) {
                    this.sendButton.textContent = 'Sending...';
                    this.scrollToBottom();
                } else {
                    this.sendButton.textContent = 'Send';
                }
            }
            
            scrollToBottom() {
                this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
            }
        }
        
        // Initialize chat when page loads
        document.addEventListener('DOMContentLoaded', () => {
            new ElizaChat();
        });
    </script>
</body>
</html>
'''

class AIConfig(BaseModel):
    """Configuration for AI features"""
    openai_api_key: Optional[str] = Field(default=None)
    model_name: str = Field(default="gpt-3.5-turbo")
    max_tokens: int = Field(default=150)
    temperature: float = Field(default=0.7)
    fallback_mode: bool = Field(default=True)

class SimplifiedAIEngine:
    """Simplified AI engine with OpenAI integration (no tiktoken)"""
    
    def __init__(self):
        self.ai_available = PHASE3_LITE_READY
        self.config = AIConfig()
        self.openai_client = None
        
        # Initialize AI services
        self._initialize_ai_services()
        
        # Enhanced conversation patterns
        self.enhanced_patterns = {
            'ai_technical': {
                'patterns': ['ai', 'artificial intelligence', 'machine learning', 'neural network', 'gpt', 'openai'],
                'ai_prompt': "You are XMRT Eliza, an advanced AI with deep knowledge of artificial intelligence and technology. Provide insightful, technical responses while maintaining a conversational tone."
            },
            'xmrt_ecosystem': {
                'patterns': ['xmrt', 'dao', 'governance', 'blockchain', 'defi', 'crypto', 'token'],
                'ai_prompt': "You are XMRT Eliza, an AI assistant for the XMRT ecosystem. You understand decentralized governance and blockchain technology. Provide helpful insights about XMRT."
            },
            'complex_reasoning': {
                'patterns': ['analyze', 'explain', 'compare', 'evaluate', 'strategy', 'solution'],
                'ai_prompt': "You are XMRT Eliza with advanced reasoning capabilities. Provide thoughtful analysis and clear explanations. Break down complex topics systematically."
            },
            'creative_thinking': {
                'patterns': ['create', 'design', 'innovative', 'brainstorm', 'idea', 'creative'],
                'ai_prompt': "You are XMRT Eliza with enhanced creative thinking. Generate innovative ideas and creative solutions while remaining practical."
            },
            'problem_solving': {
                'patterns': ['problem', 'issue', 'challenge', 'troubleshoot', 'debug', 'fix'],
                'ai_prompt': "You are XMRT Eliza, an expert problem solver. Analyze issues systematically and provide step-by-step solutions."
            }
        }
        
        # Fallback patterns
        self.fallback_patterns = {
            'greeting': {
                'patterns': ['hello', 'hi', 'hey', 'greetings'],
                'responses': [
                    "Hello! I'm XMRT Eliza with AI capabilities. How can I assist you today?",
                    "Hi there! I'm equipped with intelligent features. What would you like to explore?",
                    "Greetings! My AI systems are ready to help. What's on your mind?"
                ]
            },
            'default': {
                'patterns': [],
                'responses': [
                    "I'm processing your message with my AI systems. Can you tell me more?",
                    "That's interesting. My intelligent systems are analyzing your input. Please elaborate.",
                    "I'm using my reasoning capabilities to understand. What else would you like to discuss?"
                ]
            }
        }
    
    def _initialize_ai_services(self):
        """Initialize OpenAI services (simplified)"""
        if not self.ai_available:
            logger.info("AI services not available - running in fallback mode")
            return
        
        try:
            # Get API key from environment
            api_key = os.getenv('OPENAI_API_KEY')
            
            if api_key:
                # Initialize OpenAI client
                self.openai_client = openai.OpenAI(api_key=api_key)
                
                logger.info("AI services initialized successfully", model=self.config.model_name)
                print(f"🤖 AI Engine: OpenAI {self.config.model_name} ready")
                
            else:
                logger.warning("No OpenAI API key found - using fallback mode")
                print("⚠️ AI Engine: No API key - using enhanced fallback mode")
                
        except Exception as e:
            logger.error("AI services initialization failed", error=str(e))
            print(f"⚠️ AI Engine: Initialization failed - {str(e)}")
    
    def estimate_tokens(self, text: str) -> int:
        """Rough token estimation without tiktoken"""
        # Rough estimation: ~4 characters per token
        return len(text) // 4
    
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
    
    def generate_ai_response(self, message: str, category: str, context: Dict) -> Dict[str, Any]:
        """Generate response using OpenAI (simplified)"""
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
                for hist_msg in context['recent_history'][-2:]:  # Last 2 exchanges
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
            
            # Estimate tokens used
            input_tokens = self.estimate_tokens(message)
            output_tokens = self.estimate_tokens(ai_response)
            
            # Track AI interaction
            ai_interaction = {
                'timestamp': datetime.now().isoformat(),
                'category': category,
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
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
                'tokens_used': input_tokens + output_tokens
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
                "I'd love to discuss AI with you! While I'm in enhanced mode, I can share insights about artificial intelligence and technology. What specific aspect interests you?",
                "AI is fascinating! I'm equipped with advanced reasoning capabilities. What would you like to explore about AI or technology?",
                "That's a great technical question! My enhanced systems are designed for these discussions. Can you tell me more?"
            ],
            'xmrt_ecosystem': [
                "The XMRT ecosystem is built for decentralized governance! I'm designed to help with DAO operations and blockchain questions. What aspects interest you?",
                "XMRT represents innovation in decentralized systems! I can help with governance and tokenomics. What would you like to know?",
                "I'm part of the XMRT ecosystem and understand decentralized governance. How can I help with your XMRT questions?"
            ],
            'complex_reasoning': [
                "That requires analytical thinking! My enhanced reasoning systems are processing your question. Let me work through this systematically.",
                "Excellent question for analysis! I'm equipped with problem-solving capabilities. Let me break this down step by step.",
                "I love complex challenges! My AI architecture is designed for reasoning. What specific aspect should we focus on?"
            ],
            'default': [
                "I'm listening with my AI capabilities. While in enhanced mode, I can provide thoughtful responses. Tell me more!",
                "That's interesting! My intelligent systems are analyzing your input. Please elaborate on what you're thinking.",
                "My AI features are processing your message. I'm designed for meaningful conversations - what else would you like to explore?"
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
    
    def generate_response(self, message: str, context: Dict) -> Dict[str, Any]:
        """Main response generation with AI integration"""
        
        # Determine if we should use AI
        ai_category = self.determine_ai_category(message)
        
        if ai_category and self.openai_client:
            # Use AI for advanced response
            return self.generate_ai_response(message, ai_category, context)
        else:
            # Use enhanced fallback
            start_time = time.time()
            category = ai_category or 'default'
            return self._generate_fallback_response(message, category, context, start_time)

class SystemMonitor:
    """System monitoring with AI metrics"""
    
    def __init__(self):
        self.monitoring_active = True
        self.last_check = datetime.now()
        self.alert_thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_percent': 90.0,
            'response_time': 5.0,
            'ai_response_time': 10.0
        }
        
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics including AI stats"""
        try:
            # Standard system metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # AI-specific metrics
            ai_metrics = {
                'total_ai_interactions': len(ai_interactions),
                'ai_available': PHASE3_LITE_READY and ai_engine.openai_client is not None,
                'recent_ai_response_time': 0,
                'total_tokens_used': 0
            }
            
            if ai_interactions:
                recent_interactions = ai_interactions[-10:]
                ai_metrics['recent_ai_response_time'] = sum(i['response_time'] for i in recent_interactions) / len(recent_interactions)
                ai_metrics['total_tokens_used'] = sum(i.get('input_tokens', 0) + i.get('output_tokens', 0) for i in ai_interactions)
            
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

# Initialize systems
system_monitor = SystemMonitor()
ai_engine = SimplifiedAIEngine()

def log_error(error_type: str, error_message: str, context: Dict = None):
    """Enhanced error logging"""
    error_entry = {
        'timestamp': datetime.now().isoformat(),
        'type': error_type,
        'message': error_message,
        'context': context or {},
        'phase': '3-lite-web'
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
            '/', '/chat', '/health', '/ai/status', '/metrics'
        ],
        'timestamp': datetime.now().isoformat(),
        'phase': '3-lite-web'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    log_error('internal_server_error', str(error))
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred, but the system recovered',
        'timestamp': datetime.now().isoformat(),
        'support': 'Check /system/health for system status',
        'phase': '3-lite-web'
    }), 500

@app.route('/')
def web_chat_interface():
    """Serve the web chat interface"""
    return render_template_string(CHAT_INTERFACE_HTML)

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'xmrt-eliza',
        'version': '1.4.2-web-chat',
        'phase': '3-lite-web',
        'timestamp': datetime.now().isoformat(),
        'uptime_seconds': int((datetime.now() - start_time).total_seconds()),
        'total_requests': request_count,
        'chat_sessions': len(chat_sessions),
        'conversation_count': len(conversation_memory),
        'ai_interactions': len(ai_interactions),
        'ai_available': PHASE3_LITE_READY and ai_engine.openai_client is not None,
        'monitoring_active': system_monitor.monitoring_active,
        'web_interface': True
    })

@app.route('/chat', methods=['POST'])
def chat():
    """Enhanced chat endpoint with simplified AI integration"""
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
        
        # Generate response using simplified AI engine
        eliza_response = ai_engine.generate_response(message, context)
        
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
        
        if len(conversation_memory) > 500:
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
            'version': '1.4.2-web-chat',
            'phase': '3-lite-web'
        })
        
    except Exception as e:
        log_error('chat_endpoint_error', str(e), {'session_id': session_id if 'session_id' in locals() else 'unknown'})
        return jsonify({
            'error': 'Chat processing failed',
            'message': 'An error occurred, but the system recovered gracefully',
            'timestamp': datetime.now().isoformat(),
            'support': 'Try rephrasing your message or check /system/health',
            'phase': '3-lite-web'
        }), 500

@app.route('/ai/status')
def ai_status():
    """AI system status endpoint"""
    return jsonify({
        'ai_available': PHASE3_LITE_READY,
        'openai_connected': ai_engine.openai_client is not None,
        'simplified_mode': True,
        'model_name': ai_engine.config.model_name,
        'total_ai_interactions': len(ai_interactions),
        'recent_interactions': len([i for i in ai_interactions if datetime.fromisoformat(i['timestamp']) > datetime.now() - timedelta(hours=1)]),
        'configuration': {
            'max_tokens': ai_engine.config.max_tokens,
            'temperature': ai_engine.config.temperature,
            'fallback_mode': ai_engine.config.fallback_mode
        },
        'build_optimizations': {
            'tiktoken_removed': True,
            'langchain_removed': True,
            'lightweight_mode': True
        },
        'web_interface': True,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/metrics')
def service_metrics():
    """Enhanced service metrics with AI stats"""
    uptime_seconds = int((datetime.now() - start_time).total_seconds())
    
    ai_stats = {
        'total_ai_interactions': len(ai_interactions),
        'ai_response_rate': len([c for c in conversation_memory if c.get('ai_powered')]) / max(1, len(conversation_memory)),
        'total_tokens_used': sum(i.get('input_tokens', 0) + i.get('output_tokens', 0) for i in ai_interactions),
        'avg_ai_response_time': sum(i['response_time'] for i in ai_interactions) / max(1, len(ai_interactions)),
        'lite_mode': True
    }
    
    return jsonify({
        'service': 'xmrt-eliza',
        'version': '1.4.2-web-chat',
        'phase': '3-lite-web',
        'uptime_seconds': uptime_seconds,
        'uptime_human': str(timedelta(seconds=uptime_seconds)),
        'total_requests': request_count,
        'active_sessions': len(chat_sessions),
        'total_conversations': len(conversation_memory),
        'ai_statistics': ai_stats,
        'error_count': len(error_log),
        'requests_per_minute': round(request_count / max(1, uptime_seconds / 60), 2),
        'web_interface_enabled': True,
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    
    print(f"🚀 Starting XMRT Eliza Phase 3 Lite: Web Chat Interface")
    print(f"🌐 Version: 1.4.2-web-chat")
    print(f"🔧 Port: {port}")
    print(f"🧠 AI Integration: {'Active' if PHASE3_LITE_READY else 'Fallback Mode'}")
    print(f"🔗 OpenAI: {'Connected' if ai_engine.openai_client else 'API Key Required'}")
    print(f"📊 System monitoring: {'Active' if system_monitor.monitoring_active else 'Limited'}")
    print(f"🌐 Web Interface: Enabled")
    print(f"⚡ Build optimized: Removed tiktoken and complex dependencies")
    print(f"⏰ Start time: {start_time}")
    
    # Log startup
    logger.info("XMRT Eliza Phase 3 Lite Web starting", 
                version="1.4.2-web-chat",
                ai_available=PHASE3_LITE_READY,
                openai_connected=ai_engine.openai_client is not None,
                lite_mode=True,
                web_interface=True)
    
    app.run(host='0.0.0.0', port=port, debug=False)
