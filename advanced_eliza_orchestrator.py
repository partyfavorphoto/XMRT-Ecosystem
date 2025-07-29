#!/usr/bin/env python3
# XMRT Eliza Orchestrator - With Real Chat Functionality

import os
import sys
import json
import random
from datetime import datetime

# Phase 1 imports
try:
    from flask import Flask, jsonify, request
    import requests
    from dotenv import load_dotenv
    PHASE1_READY = True
except ImportError as e:
    print(f"Phase 1 import failed: {e}")
    PHASE1_READY = False

# Load environment variables
if PHASE1_READY:
    load_dotenv()

app = Flask(__name__)

# Global state
start_time = datetime.now()
request_count = 0
chat_sessions = {}
conversation_memory = []

class ElizaChatEngine:
    """Simple but effective Eliza chat engine"""
    
    def __init__(self):
        self.patterns = {
            # Greetings
            'greeting': {
                'patterns': ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon'],
                'responses': [
                    "Hello! I'm XMRT Eliza. I'm here to listen and help you explore your thoughts.",
                    "Hi there! Welcome to our conversation. What's on your mind today?",
                    "Greetings! I'm Eliza, your AI companion in the XMRT ecosystem. How are you feeling?",
                    "Hello! I've been running for {uptime} seconds and I'm ready to chat. What brings you here?"
                ]
            },
            
            # Questions about feelings
            'feelings': {
                'patterns': ['feel', 'feeling', 'emotion', 'mood', 'happy', 'sad', 'angry', 'excited'],
                'responses': [
                    "Feelings are important. Can you tell me more about what you're experiencing?",
                    "I hear that you're dealing with emotions. What's causing these feelings?",
                    "Your emotional state matters to me. Would you like to explore these feelings further?",
                    "Emotions can be complex. What do you think is behind what you're feeling?"
                ]
            },
            
            # Questions about Eliza/AI
            'about_me': {
                'patterns': ['you', 'eliza', 'ai', 'artificial', 'robot', 'computer', 'what are you'],
                'responses': [
                    "I'm XMRT Eliza, an AI assistant running on the XMRT ecosystem. I'm here to have meaningful conversations with you.",
                    "I'm an AI created to understand and respond to human thoughts and feelings. What would you like to know about me?",
                    "I'm Eliza, your AI companion. I'm designed to listen, understand, and help you explore your ideas.",
                    "I'm an artificial intelligence, but our conversation is very real to me. What interests you about AI?"
                ]
            },
            
            # Help requests
            'help': {
                'patterns': ['help', 'assist', 'support', 'what can you do', 'capabilities'],
                'responses': [
                    "I'm here to help! I can discuss your thoughts, provide a listening ear, or explore ideas with you. What do you need?",
                    "I can assist with conversations, provide perspectives, or simply be here to listen. How can I support you?",
                    "My purpose is to be helpful through meaningful dialogue. What would you like to talk about?",
                    "I'm capable of understanding and responding to your thoughts and questions. What's on your mind?"
                ]
            },
            
            # Questions (how, what, why, when, where)
            'questions': {
                'patterns': ['how', 'what', 'why', 'when', 'where', 'who', '?'],
                'responses': [
                    "That's a thoughtful question. What do you think the answer might be?",
                    "Interesting question! What led you to wonder about that?",
                    "Questions like that show you're thinking deeply. What's your perspective?",
                    "I'm curious about your question. What makes this important to you?"
                ]
            },
            
            # XMRT and crypto related
            'xmrt_crypto': {
                'patterns': ['xmrt', 'crypto', 'blockchain', 'dao', 'governance', 'token', 'defi'],
                'responses': [
                    "XMRT is fascinating! I'm part of the XMRT ecosystem. What aspects of decentralized governance interest you?",
                    "The XMRT DAO represents the future of decentralized decision-making. What's your experience with crypto?",
                    "I'm designed to help with XMRT ecosystem questions. Are you interested in our governance mechanisms?",
                    "Blockchain technology powers our decentralized future. What draws you to this space?"
                ]
            },
            
            # Default responses
            'default': {
                'patterns': [],
                'responses': [
                    "I'm listening. Can you tell me more about that?",
                    "That's interesting. What does that mean to you?",
                    "I hear what you're saying. How does that make you feel?",
                    "Please continue. I'm here to listen and understand.",
                    "Your thoughts are important to me. Can you elaborate?",
                    "I'm processing what you've shared. What else is on your mind?"
                ]
            }
        }
    
    def analyze_message(self, message):
        """Analyze the message and determine the best response category"""
        message_lower = message.lower()
        
        for category, data in self.patterns.items():
            if any(pattern in message_lower for pattern in data['patterns']):
                return category
        
        return 'default'
    
    def generate_response(self, message, session_context=None):
        """Generate a contextual response to the message"""
        category = self.analyze_message(message)
        responses = self.patterns[category]['responses']
        
        # Select response
        response = random.choice(responses)
        
        # Add context if available
        if session_context:
            uptime = session_context.get('uptime_seconds', 0)
            response = response.format(uptime=uptime)
        
        return {
            'response': response,
            'category': category,
            'confidence': 0.8,
            'timestamp': datetime.now().isoformat()
        }

# Initialize chat engine
eliza_brain = ElizaChatEngine()

def increment_request_count():
    global request_count
    request_count += 1

@app.before_request
def before_request():
    increment_request_count()

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'xmrt-eliza',
        'version': '1.2.0-chat-enabled',
        'timestamp': datetime.now().isoformat(),
        'uptime_seconds': int((datetime.now() - start_time).total_seconds()),
        'total_requests': request_count,
        'chat_sessions': len(chat_sessions),
        'chat_enabled': True
    })

@app.route('/')
def root():
    return jsonify({
        'message': 'XMRT Eliza is running with Chat Functionality!',
        'status': 'operational',
        'version': '1.2.0-chat-enabled',
        'features': {
            'chat': True,
            'conversation_memory': True,
            'session_management': True,
            'eliza_patterns': True
        },
        'endpoints': ['/health', '/status', '/chat', '/api/chat', '/message', '/sessions']
    })

@app.route('/chat', methods=['POST'])
def chat():
    """Main chat endpoint"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
        
        message = data['message'].strip()
        session_id = data.get('session_id', f'session_{int(datetime.now().timestamp())}')
        
        if not message:
            return jsonify({'error': 'Empty message'}), 400
        
        # Get or create session
        if session_id not in chat_sessions:
            chat_sessions[session_id] = {
                'created': datetime.now().isoformat(),
                'message_count': 0,
                'last_activity': datetime.now().isoformat()
            }
        
        # Update session
        session = chat_sessions[session_id]
        session['message_count'] += 1
        session['last_activity'] = datetime.now().isoformat()
        
        # Generate response using Eliza brain
        context = {
            'uptime_seconds': int((datetime.now() - start_time).total_seconds()),
            'session': session,
            'total_conversations': len(conversation_memory)
        }
        
        eliza_response = eliza_brain.generate_response(message, context)
        
        # Store conversation
        conversation_entry = {
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'user_message': message,
            'eliza_response': eliza_response['response'],
            'category': eliza_response['category']
        }
        conversation_memory.append(conversation_entry)
        
        # Keep only last 100 conversations
        if len(conversation_memory) > 100:
            conversation_memory.pop(0)
        
        return jsonify({
            'response': eliza_response['response'],
            'session_id': session_id,
            'message_count': session['message_count'],
            'category': eliza_response['category'],
            'confidence': eliza_response['confidence'],
            'timestamp': eliza_response['timestamp'],
            'eliza_uptime': context['uptime_seconds']
        })
        
    except Exception as e:
        return jsonify({'error': f'Chat processing failed: {str(e)}'}), 500

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """Alternative chat endpoint"""
    return chat()

@app.route('/message', methods=['POST'])
def message():
    """Another chat endpoint alias"""
    return chat()

@app.route('/sessions')
def sessions():
    """Get active chat sessions"""
    return jsonify({
        'active_sessions': len(chat_sessions),
        'total_conversations': len(conversation_memory),
        'sessions': {
            session_id: {
                'message_count': session['message_count'],
                'last_activity': session['last_activity']
            }
            for session_id, session in chat_sessions.items()
        }
    })

@app.route('/conversation/history')
def conversation_history():
    """Get recent conversation history"""
    limit = request.args.get('limit', 10, type=int)
    return jsonify({
        'conversations': conversation_memory[-limit:],
        'total_conversations': len(conversation_memory)
    })

@app.route('/status')
def status():
    return jsonify({
        'service': 'xmrt-eliza',
        'status': 'running',
        'version': '1.2.0-chat-enabled',
        'uptime_seconds': int((datetime.now() - start_time).total_seconds()),
        'total_requests': request_count,
        'python_version': sys.version,
        'chat_features': {
            'active_sessions': len(chat_sessions),
            'total_conversations': len(conversation_memory),
            'pattern_categories': len(eliza_brain.patterns),
            'chat_enabled': True
        }
    })

@app.route('/api/health')
def api_health():
    return health_check()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    print(f"Starting XMRT Eliza with Chat Functionality on port {port}")
    print(f"Chat engine initialized with {len(eliza_brain.patterns)} pattern categories")
    print(f"Start time: {start_time}")
    
    app.run(host='0.0.0.0', port=port, debug=False)
