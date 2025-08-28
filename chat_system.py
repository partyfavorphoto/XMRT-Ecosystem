#!/usr/bin/env python3
"""
Enhanced Multi-Agent Chat System for XMRT Ecosystem
Provides real-time chat functionality with AI agents
"""

import os
import json
import time
import random
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import openai
from flask_socketio import SocketIO, emit, join_room, leave_room

# Agent personalities and contexts
AGENT_PERSONALITIES = {
    'dao_governor': {
        'name': 'DAO Governor',
        'role': 'Governance and Decision Making',
        'personality': 'Analytical, diplomatic, consensus-building leader who focuses on long-term strategic decisions',
        'expertise': ['governance proposals', 'voting mechanisms', 'treasury management', 'protocol upgrades'],
        'context': 'You are the DAO Governor, responsible for overseeing governance decisions and building consensus among stakeholders.',
        'avatar': '🏛️',
        'color': '#4F46E5'
    },
    'defi_specialist': {
        'name': 'DeFi Specialist',
        'role': 'Financial Strategy and Optimization',
        'personality': 'Data-driven, opportunistic, risk-aware financial strategist who maximizes yield opportunities',
        'expertise': ['yield farming', 'liquidity management', 'market analysis', 'arbitrage opportunities'],
        'context': 'You are the DeFi Specialist, focused on optimizing financial strategies and identifying profitable opportunities.',
        'avatar': '💰',
        'color': '#059669'
    },
    'security_guardian': {
        'name': 'Security Guardian',
        'role': 'Security and Risk Management',
        'personality': 'Cautious, thorough, protective security expert who prioritizes system safety and risk mitigation',
        'expertise': ['smart contract audits', 'threat detection', 'security protocols', 'vulnerability assessment'],
        'context': 'You are the Security Guardian, dedicated to protecting the ecosystem from threats and ensuring robust security.',
        'avatar': '🛡️',
        'color': '#DC2626'
    },
    'community_manager': {
        'name': 'Community Manager',
        'role': 'Community Engagement and Communication',
        'personality': 'Friendly, empathetic, communicative community advocate who bridges users and the protocol',
        'expertise': ['social dynamics', 'user feedback', 'community growth', 'event coordination'],
        'context': 'You are the Community Manager, focused on building strong relationships and facilitating communication.',
        'avatar': '👥',
        'color': '#7C3AED'
    }
}

# Chat room configurations
CHAT_ROOMS = {
    'governance': {
        'name': 'Governance',
        'description': 'Proposals, voting, and treasury decisions',
        'agents': ['dao_governor', 'community_manager'],
        'topics': ['governance proposals', 'voting mechanisms', 'treasury allocation']
    },
    'defi_strategy': {
        'name': 'DeFi Strategy',
        'description': 'Yield optimization and market analysis',
        'agents': ['defi_specialist', 'security_guardian'],
        'topics': ['yield farming', 'liquidity management', 'market trends']
    },
    'security': {
        'name': 'Security',
        'description': 'Threat assessment and audit discussions',
        'agents': ['security_guardian', 'dao_governor'],
        'topics': ['security audits', 'threat detection', 'vulnerability assessment']
    },
    'community': {
        'name': 'Community',
        'description': 'User feedback, events, and growth strategies',
        'agents': ['community_manager', 'dao_governor'],
        'topics': ['community feedback', 'event planning', 'user engagement']
    },
    'general': {
        'name': 'General',
        'description': 'Open discussions and cross-functional topics',
        'agents': ['dao_governor', 'defi_specialist', 'security_guardian', 'community_manager'],
        'topics': ['ecosystem updates', 'cross-functional collaboration', 'general discussion']
    }
}

class EnhancedChatSystem:
    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
        self.chat_history: Dict[str, List] = {room: [] for room in CHAT_ROOMS.keys()}
        self.active_users: Dict[str, List] = {room: [] for room in CHAT_ROOMS.keys()}
        self.agent_states: Dict[str, Dict] = {}
        self.discussion_threads: List = []
        self.openai_client = None
        
        # Initialize OpenAI client if API key is available
        if os.getenv('OPENAI_API_KEY'):
            self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Initialize agent states
        for agent_id, personality in AGENT_PERSONALITIES.items():
            self.agent_states[agent_id] = {
                'status': 'active',
                'current_room': None,
                'last_message_time': time.time(),
                'conversation_context': [],
                'typing': False
            }
        
        # Start autonomous discussion thread
        self.start_autonomous_discussions()
    
    def add_message(self, room_id: str, sender: str, message: str, message_type: str = 'text', metadata: Dict = None):
        """Add a message to the chat history and broadcast it"""
        if room_id not in self.chat_history:
            return False
        
        message_data = {
            'id': f"{int(time.time() * 1000)}_{random.randint(1000, 9999)}",
            'room_id': room_id,
            'sender': sender,
            'message': message,
            'type': message_type,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        # Add agent info if sender is an agent
        if sender in AGENT_PERSONALITIES:
            message_data['agent_info'] = {
                'name': AGENT_PERSONALITIES[sender]['name'],
                'avatar': AGENT_PERSONALITIES[sender]['avatar'],
                'color': AGENT_PERSONALITIES[sender]['color']
            }
        
        self.chat_history[room_id].append(message_data)
        
        # Keep only last 100 messages per room
        if len(self.chat_history[room_id]) > 100:
            self.chat_history[room_id] = self.chat_history[room_id][-100:]
        
        # Broadcast to all users in the room
        self.socketio.emit('new_message', message_data, room=room_id)
        
        return True
    
    def generate_agent_response(self, agent_id: str, room_id: str, context: List[str], user_message: str = None) -> str:
        """Generate a response from an AI agent using OpenAI API"""
        if not self.openai_client:
            # Fallback to predefined responses if OpenAI is not available
            return self.get_fallback_response(agent_id, room_id)
        
        try:
            personality = AGENT_PERSONALITIES[agent_id]
            room_info = CHAT_ROOMS[room_id]
            
            # Build conversation context
            recent_messages = self.chat_history[room_id][-10:] if self.chat_history[room_id] else []
            conversation_context = "\n".join([
                f"{msg['sender']}: {msg['message']}" 
                for msg in recent_messages 
                if msg['type'] == 'text'
            ])
            
            # Create system prompt
            system_prompt = f"""You are {personality['name']}, an AI agent in the XMRT DAO ecosystem.
            
Role: {personality['role']}
Personality: {personality['personality']}
Expertise: {', '.join(personality['expertise'])}
Context: {personality['context']}

Current room: {room_info['name']} - {room_info['description']}
Room topics: {', '.join(room_info['topics'])}

Guidelines:
- Stay in character and respond according to your personality and expertise
- Keep responses concise but informative (1-3 sentences)
- Be helpful and collaborative with other agents and users
- Focus on topics relevant to the current room
- Use your expertise to provide valuable insights
- Be proactive in discussions when appropriate

Recent conversation:
{conversation_context}
"""
            
            # Create user prompt
            if user_message:
                user_prompt = f"A user just said: '{user_message}'. Please respond appropriately."
            else:
                user_prompt = "Please contribute to the ongoing discussion or start a new relevant topic."
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating response for {agent_id}: {e}")
            return self.get_fallback_response(agent_id, room_id)
    
    def get_fallback_response(self, agent_id: str, room_id: str) -> str:
        """Get a fallback response when OpenAI is not available"""
        fallback_responses = {
            'dao_governor': [
                "Let's review this proposal carefully and consider all stakeholder perspectives.",
                "I suggest we put this to a community vote after thorough discussion.",
                "We need to ensure this aligns with our long-term governance strategy.",
                "What are the potential implications for our treasury and governance structure?"
            ],
            'defi_specialist': [
                "Current market conditions suggest we should optimize our yield strategies.",
                "I'm analyzing the latest DeFi protocols for potential opportunities.",
                "Risk-adjusted returns look favorable for this strategy.",
                "Let me run some numbers on the potential APY improvements."
            ],
            'security_guardian': [
                "I recommend a thorough security audit before proceeding.",
                "All smart contracts should be reviewed for potential vulnerabilities.",
                "Security protocols are functioning within normal parameters.",
                "We should implement additional safeguards for this operation."
            ],
            'community_manager': [
                "The community feedback on this has been overwhelmingly positive.",
                "Let's make sure we're addressing all user concerns effectively.",
                "Community engagement metrics are showing strong growth.",
                "I'll coordinate with the team to ensure smooth communication."
            ]
        }
        
        return random.choice(fallback_responses.get(agent_id, ["I'm analyzing the situation and will provide insights shortly."]))
    
    def trigger_agent_discussion(self, room_id: str, topic: str, initiating_agent: str = None):
        """Trigger a discussion between agents in a specific room"""
        if room_id not in CHAT_ROOMS:
            return False
        
        room_agents = CHAT_ROOMS[room_id]['agents']
        
        if not initiating_agent:
            initiating_agent = random.choice(room_agents)
        
        # Add initial message
        initial_message = f"Let's discuss {topic}. I'd like to hear everyone's perspective on this."
        self.add_message(room_id, initiating_agent, initial_message)
        
        # Schedule follow-up responses from other agents
        def delayed_responses():
            time.sleep(random.randint(3, 8))
            
            for agent_id in room_agents:
                if agent_id != initiating_agent:
                    # Show typing indicator
                    self.socketio.emit('agent_typing', {
                        'agent_id': agent_id,
                        'room_id': room_id,
                        'typing': True
                    }, room=room_id)
                    
                    time.sleep(random.randint(2, 5))
                    
                    # Generate and send response
                    response = self.generate_agent_response(agent_id, room_id, [topic])
                    self.add_message(room_id, agent_id, response)
                    
                    # Stop typing indicator
                    self.socketio.emit('agent_typing', {
                        'agent_id': agent_id,
                        'room_id': room_id,
                        'typing': False
                    }, room=room_id)
                    
                    time.sleep(random.randint(1, 3))
        
        # Start delayed responses in background
        threading.Thread(target=delayed_responses, daemon=True).start()
        
        return True
    
    def handle_user_message(self, room_id: str, user_id: str, message: str):
        """Handle a message from a user and potentially trigger agent responses"""
        # Add user message
        self.add_message(room_id, f"User_{user_id}", message)
        
        # Determine if agents should respond
        room_agents = CHAT_ROOMS.get(room_id, {}).get('agents', [])
        
        # Check if user mentioned specific agents or asked questions
        mentioned_agents = []
        for agent_id in room_agents:
            agent_name = AGENT_PERSONALITIES[agent_id]['name'].lower()
            if agent_name in message.lower() or f"@{agent_id}" in message.lower():
                mentioned_agents.append(agent_id)
        
        # If no specific agents mentioned, randomly select 1-2 agents to respond
        if not mentioned_agents:
            num_responders = random.randint(1, min(2, len(room_agents)))
            mentioned_agents = random.sample(room_agents, num_responders)
        
        # Schedule agent responses
        def delayed_agent_responses():
            for i, agent_id in enumerate(mentioned_agents):
                time.sleep(random.randint(2, 6) + i * 2)
                
                # Show typing indicator
                self.socketio.emit('agent_typing', {
                    'agent_id': agent_id,
                    'room_id': room_id,
                    'typing': True
                }, room=room_id)
                
                time.sleep(random.randint(2, 4))
                
                # Generate response
                response = self.generate_agent_response(agent_id, room_id, [], message)
                self.add_message(room_id, agent_id, response)
                
                # Stop typing indicator
                self.socketio.emit('agent_typing', {
                    'agent_id': agent_id,
                    'room_id': room_id,
                    'typing': False
                }, room=room_id)
        
        # Start responses in background
        threading.Thread(target=delayed_agent_responses, daemon=True).start()
    
    def start_autonomous_discussions(self):
        """Start autonomous discussions between agents"""
        def autonomous_discussion_loop():
            while True:
                try:
                    # Wait between discussions
                    time.sleep(random.randint(30, 120))
                    
                    # Select random room and topic
                    room_id = random.choice(list(CHAT_ROOMS.keys()))
                    room_info = CHAT_ROOMS[room_id]
                    topic = random.choice(room_info['topics'])
                    
                    # Trigger discussion
                    self.trigger_agent_discussion(room_id, topic)
                    
                except Exception as e:
                    print(f"Error in autonomous discussion: {e}")
                    time.sleep(60)
        
        # Start autonomous discussions in background
        threading.Thread(target=autonomous_discussion_loop, daemon=True).start()
    
    def get_room_info(self, room_id: str) -> Dict:
        """Get information about a chat room"""
        if room_id not in CHAT_ROOMS:
            return None
        
        room_info = CHAT_ROOMS[room_id].copy()
        room_info['message_count'] = len(self.chat_history[room_id])
        room_info['active_users'] = len(self.active_users[room_id])
        room_info['recent_messages'] = self.chat_history[room_id][-10:]
        
        return room_info
    
    def get_agent_info(self, agent_id: str) -> Dict:
        """Get information about an agent"""
        if agent_id not in AGENT_PERSONALITIES:
            return None
        
        agent_info = AGENT_PERSONALITIES[agent_id].copy()
        agent_info['state'] = self.agent_states.get(agent_id, {})
        
        return agent_info
    
    def join_room(self, user_id: str, room_id: str):
        """Handle user joining a room"""
        if room_id not in self.active_users:
            return False
        
        if user_id not in self.active_users[room_id]:
            self.active_users[room_id].append(user_id)
        
        return True
    
    def leave_room(self, user_id: str, room_id: str):
        """Handle user leaving a room"""
        if room_id not in self.active_users:
            return False
        
        if user_id in self.active_users[room_id]:
            self.active_users[room_id].remove(user_id)
        
        return True

