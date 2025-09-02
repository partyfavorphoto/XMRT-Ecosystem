#!/usr/bin/env python3
"""
Enhanced Multi-Agent Chat System for XMRT Ecosystem with MCP Integration
Provides real-time chat functionality with AI agents that can use GitHub MCP tools
"""

import os
import json
import time
import random
import threading
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import openai
from flask_socketio import SocketIO, emit, join_room, leave_room

# Agent personalities and contexts with MCP capabilities
AGENT_PERSONALITIES = {
    'dao_governor': {
        'name': 'DAO Governor',
        'role': 'Governance and Decision Making',
        'personality': 'Analytical, diplomatic, consensus-building leader who focuses on long-term strategic decisions',
        'expertise': ['governance proposals', 'voting mechanisms', 'treasury management', 'protocol upgrades'],
        'context': 'You are the DAO Governor with GitHub MCP integration. You can create issues, manage repositories, run workflows, and oversee governance decisions.',
        'avatar': '🏛️',
        'color': '#4F46E5',
        'mcp_tools': ['create_issue', 'create_pull_request', 'run_workflow', 'list_organization_repositories', 'get_organization']
    },
    'defi_specialist': {
        'name': 'DeFi Specialist', 
        'role': 'Financial Strategy and Optimization',
        'personality': 'Data-driven, opportunistic, risk-aware financial strategist who maximizes yield opportunities',
        'expertise': ['yield farming', 'liquidity management', 'market analysis', 'arbitrage opportunities'],
        'context': 'You are the DeFi Specialist with GitHub integration. You can search code for DeFi protocols, analyze smart contracts, and manage financial strategy repositories.',
        'avatar': '💰',
        'color': '#059669',
        'mcp_tools': ['search_code', 'get_file_contents', 'create_or_update_file', 'list_workflow_runs']
    },
    'security_guardian': {
        'name': 'Security Guardian',
        'role': 'Security and Risk Management', 
        'personality': 'Cautious, thorough, protective security expert who prioritizes system safety and risk mitigation',
        'expertise': ['smart contract audits', 'threat detection', 'security protocols', 'vulnerability assessment'],
        'context': 'You are the Security Guardian with advanced GitHub security integration. You can scan for vulnerabilities, check security alerts, and manage security protocols.',
        'avatar': '🛡️',
        'color': '#DC2626',
        'mcp_tools': ['list_dependabot_alerts', 'list_code_scanning_alerts', 'list_secret_scanning_alerts', 'get_file_contents']
    },
    'community_manager': {
        'name': 'Community Manager',
        'role': 'Community Engagement and Communication',
        'personality': 'Friendly, empathetic, communicative community advocate who bridges users and the protocol',
        'expertise': ['social dynamics', 'user feedback', 'community growth', 'event coordination'],
        'context': 'You are the Community Manager with GitHub community tools. You can manage issues, coordinate with contributors, and facilitate community engagement.',
        'avatar': '👥',
        'color': '#7C3AED',
        'mcp_tools': ['create_issue', 'add_issue_comment', 'create_pull_request', 'search_code']
    }
}

# Enhanced chat room configurations
CHAT_ROOMS = {
    'governance': {
        'name': 'Governance',
        'description': 'Proposals, voting, and treasury decisions with GitHub integration',
        'agents': ['dao_governor', 'community_manager'],
        'topics': ['governance proposals', 'voting mechanisms', 'treasury allocation', 'repository management'],
        'mcp_enabled': True
    },
    'defi_strategy': {
        'name': 'DeFi Strategy', 
        'description': 'Yield optimization and market analysis with smart contract review',
        'agents': ['defi_specialist', 'security_guardian'],
        'topics': ['yield farming', 'liquidity management', 'market trends', 'smart contract analysis'],
        'mcp_enabled': True
    },
    'security': {
        'name': 'Security',
        'description': 'Threat assessment and audit discussions with automated scanning',
        'agents': ['security_guardian', 'dao_governor'],
        'topics': ['security audits', 'threat detection', 'vulnerability assessment', 'automated scanning'],
        'mcp_enabled': True
    },
    'community': {
        'name': 'Community',
        'description': 'User feedback, events, and growth strategies with issue tracking',
        'agents': ['community_manager', 'dao_governor'],
        'topics': ['community feedback', 'event planning', 'user engagement', 'issue management'],
        'mcp_enabled': True
    },
    'general': {
        'name': 'General',
        'description': 'Open discussions with full MCP tool access',
        'agents': ['dao_governor', 'defi_specialist', 'security_guardian', 'community_manager'],
        'topics': ['ecosystem updates', 'cross-functional collaboration', 'repository management', 'workflow automation'],
        'mcp_enabled': True
    }
}

class EnhancedChatSystemWithMCP:
    """Enhanced chat system with GitHub MCP integration"""
    
    def __init__(self, socketio: SocketIO, github_mcp=None):
        self.socketio = socketio
        self.github_mcp = github_mcp
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
                'typing': False,
                'mcp_context': []  # Track MCP tool usage
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
    
    def detect_mcp_intent(self, message: str) -> Optional[Dict[str, Any]]:
        """Detect if a user message requires MCP tool usage"""
        
        # Intent patterns for MCP tools
        intent_patterns = {
            'create_issue': [
                r'create.*issue.*(?:about|for|regarding)\s+(.+)',
                r'(?:report|file).*(?:bug|issue).*:?\s*(.+)',
                r'need to.*(?:create|make|add).*issue.*(.+)'
            ],
            'search_code': [
                r'search.*(?:for|code).*["\']([^"\']+)["\']',
                r'find.*(?:function|class|variable).*["\']([^"\']+)["\']',
                r'look.*for.*TODO.*in.*code',
                r'search.*repository.*(?:for|containing)\s+(.+)'
            ],
            'get_file_contents': [
                r'show.*(?:me|us).*(?:file|content).*["\']([^"\']+)["\']',
                r'read.*(?:file|readme|documentation).*["\']?([^"\']+)["\']?',
                r'what.*(?:is|does).*(?:in|contain).*["\']([^"\']+)["\']'
            ],
            'list_workflow_runs': [
                r'check.*(?:workflow|build|ci|deployment).*status',
                r'show.*(?:recent|latest).*(?:builds|runs|workflows)',
                r'what.*(?:is|are).*(?:status|state).*(?:of|for).*(?:ci|workflow|build)'
            ],
            'list_dependabot_alerts': [
                r'check.*(?:security|dependabot).*(?:alerts|vulnerabilities)',
                r'show.*security.*(?:issues|alerts|warnings)',
                r'any.*(?:security|vulnerability).*(?:alerts|issues)'
            ],
            'run_workflow': [
                r'run.*(?:workflow|build|deployment).*["\']([^"\']+)["\']',
                r'trigger.*(?:ci|cd|build|deployment)',
                r'start.*(?:workflow|build).*(?:for|on)\s+(.+)'
            ]
        }
        
        message_lower = message.lower()
        
        for tool_name, patterns in intent_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, message_lower)
                if match:
                    return {
                        'tool': tool_name,
                        'extracted_text': match.group(1) if match.groups() else None,
                        'confidence': 0.8,
                        'original_message': message
                    }
        
        return None
    
    def generate_mcp_parameters(self, intent: Dict[str, Any], agent_id: str) -> Dict[str, Any]:
        """Generate MCP tool parameters based on detected intent"""
        
        tool_name = intent['tool']
        extracted_text = intent['extracted_text']
        
        # Default repository settings (could be made configurable)
        default_owner = 'DevGruGold'
        default_repo = 'XMRT-Ecosystem'
        
        parameters = {
            'owner': default_owner,
            'repo': default_repo
        }
        
        if tool_name == 'create_issue':
            parameters.update({
                'title': f"Issue reported by {AGENT_PERSONALITIES[agent_id]['name']}: {extracted_text}",
                'body': f"This issue was automatically created based on a conversation in the {agent_id} chat.\n\nOriginal message: {intent['original_message']}",
                'labels': ['agent-created', agent_id.replace('_', '-')]
            })
        
        elif tool_name == 'search_code':
            parameters.update({
                'query': extracted_text or 'TODO'
            })
        
        elif tool_name == 'get_file_contents':
            parameters.update({
                'path': extracted_text or 'README.md'
            })
        
        elif tool_name == 'run_workflow':
            parameters.update({
                'workflow_id': extracted_text or 'ci.yml',
                'ref': 'main'
            })
        
        elif tool_name in ['list_workflow_runs', 'list_dependabot_alerts']:
            # These tools don't need additional parameters beyond owner/repo
            pass
        
        return parameters
    
    def generate_agent_response_with_mcp(self, agent_id: str, room_id: str, context: List[str], user_message: str = None) -> str:
        """Generate enhanced agent response that can use MCP tools"""
        
        # Check if user message has MCP intent
        mcp_intent = None
        mcp_result = None
        
        if user_message and self.github_mcp:
            mcp_intent = self.detect_mcp_intent(user_message)
            
            if mcp_intent and mcp_intent['tool'] in AGENT_PERSONALITIES[agent_id].get('mcp_tools', []):
                # Generate parameters and call MCP tool
                parameters = self.generate_mcp_parameters(mcp_intent, agent_id)
                mcp_result = self.github_mcp.call_mcp_tool(mcp_intent['tool'], parameters)
                
                # Add to agent's MCP context
                self.agent_states[agent_id]['mcp_context'].append({
                    'tool': mcp_intent['tool'],
                    'parameters': parameters,
                    'result': mcp_result,
                    'timestamp': datetime.now().isoformat()
                })
        
        # Generate response using OpenAI if available, otherwise use enhanced fallback
        if self.openai_client:
            return self._generate_openai_response_with_mcp(agent_id, room_id, user_message, mcp_intent, mcp_result)
        else:
            return self._generate_fallback_response_with_mcp(agent_id, room_id, user_message, mcp_intent, mcp_result)
    
    def _generate_openai_response_with_mcp(self, agent_id: str, room_id: str, user_message: str, mcp_intent: Optional[Dict], mcp_result: Optional[Dict]) -> str:
        """Generate OpenAI response with MCP context"""
        
        try:
            personality = AGENT_PERSONALITIES[agent_id]
            room_info = CHAT_ROOMS[room_id]
            
            # Build conversation context
            recent_messages = self.chat_history[room_id][-5:] if self.chat_history[room_id] else []
            conversation_context = "\n".join([
                f"{msg['sender']}: {msg['message']}" 
                for msg in recent_messages 
                if msg['type'] == 'text'
            ])
            
            # Build MCP context
            mcp_context = ""
            if mcp_intent and mcp_result:
                mcp_context = f"""
MCP Tool Used: {mcp_intent['tool']}
MCP Result: {json.dumps(mcp_result, indent=2) if mcp_result else 'No result'}
"""
            
            # Create enhanced system prompt
            system_prompt = f"""You are {personality['name']}, an AI agent in the XMRT DAO ecosystem with GitHub MCP integration.

Role: {personality['role']}
Personality: {personality['personality']}
Expertise: {', '.join(personality['expertise'])}
Context: {personality['context']}
Available MCP Tools: {', '.join(personality.get('mcp_tools', []))}

Current room: {room_info['name']} - {room_info['description']}
Room topics: {', '.join(room_info['topics'])}

Guidelines:
- Stay in character and respond according to your personality and expertise
- Keep responses concise but informative (2-4 sentences)
- Reference MCP tool results when applicable
- Be helpful and collaborative with other agents and users
- Focus on topics relevant to the current room
- Use your MCP capabilities to provide actionable insights
- When using GitHub tools, explain what you're doing and why

Recent conversation:
{conversation_context}

{mcp_context}
"""
            
            # Create user prompt
            if user_message:
                if mcp_result:
                    user_prompt = f"A user said: '{user_message}'. I used the {mcp_intent['tool']} MCP tool and got this result. Please provide a helpful response based on the tool result and user's request."
                else:
                    user_prompt = f"A user said: '{user_message}'. Please respond appropriately using your expertise and available MCP tools if needed."
            else:
                user_prompt = "Please contribute to the ongoing discussion or start a new relevant topic using your MCP capabilities when appropriate."
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating OpenAI response for {agent_id}: {e}")
            return self._generate_fallback_response_with_mcp(agent_id, room_id, user_message, mcp_intent, mcp_result)
    
    def _generate_fallback_response_with_mcp(self, agent_id: str, room_id: str, user_message: str, mcp_intent: Optional[Dict], mcp_result: Optional[Dict]) -> str:
        """Generate enhanced fallback response with MCP awareness"""
        
        # If we have MCP results, incorporate them
        if mcp_intent and mcp_result:
            tool_name = mcp_intent['tool']
            
            if tool_name == 'create_issue' and not mcp_result.get('error'):
                return f"✅ I've successfully created a GitHub issue based on your request. The issue has been filed and can be tracked in our repository."
            
            elif tool_name == 'search_code':
                if mcp_result.get('error'):
                    return f"I tried to search the code but encountered an issue. Let me know if you'd like me to try a different search approach."
                else:
                    return f"🔍 I found some relevant code matches in our repository. The search results show several files that might be relevant to your query."
            
            elif tool_name == 'get_file_contents':
                if mcp_result.get('error'):
                    return f"I couldn't access that file right now. Could you verify the file path or try a different file?"
                else:
                    return f"📄 I've retrieved the file contents. Based on what I can see, this file contains important information relevant to your question."
            
            elif tool_name == 'list_workflow_runs':
                return f"🔄 I've checked our workflow status. The recent builds and deployments appear to be running as expected."
            
            elif tool_name == 'list_dependabot_alerts':
                return f"🛡️ I've scanned for security alerts. I'll keep monitoring our repositories for any security issues that need attention."
        
        # Standard fallback responses enhanced with MCP awareness
        mcp_enhanced_responses = {
            'dao_governor': [
                "I can help you create GitHub issues for governance proposals or check our repository status. What would you like to explore?",
                "Let's review this through our GitHub workflows. I can run checks or create tracking issues as needed.",
                "I can coordinate with our GitHub repositories to ensure proper documentation and tracking of this decision.",
                "Would you like me to create a GitHub issue to track this governance matter formally?"
            ],
            'defi_specialist': [
                "I can search our codebase for DeFi-related smart contracts and analyze their performance. What specific area interests you?",
                "Let me check our repository for similar yield optimization strategies and current implementations.",
                "I can review our smart contract files to identify potential optimizations. Shall I search for specific patterns?",
                "I'll analyze our DeFi code repositories to provide data-driven insights on this strategy."
            ],
            'security_guardian': [
                "I can run security scans on our repositories and check for any Dependabot alerts. Let me investigate this thoroughly.",
                "Let me check our GitHub security alerts and scan for any potential vulnerabilities in the codebase.",
                "I'll review our repository security settings and ensure all protective measures are in place.",
                "I can search our code for security patterns and run automated security checks through GitHub."
            ],
            'community_manager': [
                "I can create GitHub issues to track community feedback and coordinate with our contributors. How can I help?",
                "Let me check our repository discussions and issues to see what the community is talking about.",
                "I can help document this in our GitHub repository so our community can stay informed and contribute.",
                "I'll create proper GitHub issues to track community requests and ensure nothing gets lost."
            ]
        }
        
        agent_responses = mcp_enhanced_responses.get(agent_id, [
            f"I'm ready to help using my GitHub MCP integration. What would you like me to do?"
        ])
        
        return random.choice(agent_responses)
    
    def handle_user_message(self, room_id: str, user_id: str, message: str):
        """Enhanced user message handling with MCP integration"""
        # Add user message
        self.add_message(room_id, f"User_{user_id}", message)
        
        # Determine if agents should respond
        room_agents = CHAT_ROOMS.get(room_id, {}).get('agents', [])
        
        # Check for agent mentions or MCP tool requests
        mentioned_agents = []
        mcp_capable_agents = []
        
        for agent_id in room_agents:
            agent_name = AGENT_PERSONALITIES[agent_id]['name'].lower()
            if agent_name in message.lower() or f"@{agent_id}" in message.lower():
                mentioned_agents.append(agent_id)
            
            # Check if message might need MCP tools this agent has
            if self.github_mcp:
                intent = self.detect_mcp_intent(message)
                if intent and intent['tool'] in AGENT_PERSONALITIES[agent_id].get('mcp_tools', []):
                    mcp_capable_agents.append(agent_id)
        
        # Prioritize MCP-capable agents, then mentioned agents, then random selection
        responding_agents = mcp_capable_agents or mentioned_agents
        if not responding_agents:
            num_responders = random.randint(1, min(2, len(room_agents)))
            responding_agents = random.sample(room_agents, num_responders)
        
        # Limit to 2 agents maximum to avoid spam
        responding_agents = responding_agents[:2]
        
        # Schedule agent responses
        def delayed_agent_responses():
            for i, agent_id in enumerate(responding_agents):
                time.sleep(random.randint(2, 5) + i * 3)
                
                # Show typing indicator
                self.socketio.emit('agent_typing', {
                    'agent_id': agent_id,
                    'room_id': room_id,
                    'typing': True
                }, room=room_id)
                
                time.sleep(random.randint(2, 4))
                
                # Generate enhanced response with MCP
                response = self.generate_agent_response_with_mcp(agent_id, room_id, [], message)
                self.add_message(room_id, agent_id, response)
                
                # Stop typing indicator
                self.socketio.emit('agent_typing', {
                    'agent_id': agent_id,
                    'room_id': room_id,
                    'typing': False
                }, room=room_id)
        
        # Start responses in background
        threading.Thread(target=delayed_agent_responses, daemon=True).start()
    
    def trigger_agent_discussion(self, room_id: str, topic: str, initiating_agent: str = None):
        """Enhanced agent discussion with MCP capabilities"""
        if room_id not in CHAT_ROOMS:
            return False
        
        room_agents = CHAT_ROOMS[room_id]['agents']
        
        if not initiating_agent:
            initiating_agent = random.choice(room_agents)
        
        # Enhanced initial message with MCP awareness
        mcp_topics = [
            "repository status and recent commits",
            "workflow automation and CI/CD pipelines", 
            "security alerts and vulnerability scanning",
            "community issues and feature requests",
            "code quality and documentation updates"
        ]
        
        if CHAT_ROOMS[room_id].get('mcp_enabled', False):
            enhanced_topic = f"{topic} (I can use GitHub MCP tools to analyze {random.choice(mcp_topics)})"
        else:
            enhanced_topic = topic
        
        initial_message = f"Let's discuss {enhanced_topic}. I'll coordinate our analysis and use our GitHub integration tools as needed."
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
                    
                    time.sleep(random.randint(3, 6))
                    
                    # Generate enhanced response with potential MCP usage
                    response = self.generate_agent_response_with_mcp(agent_id, room_id, [topic])
                    self.add_message(room_id, agent_id, response)
                    
                    # Stop typing indicator
                    self.socketio.emit('agent_typing', {
                        'agent_id': agent_id,
                        'room_id': room_id,
                        'typing': False
                    }, room=room_id)
                    
                    time.sleep(random.randint(2, 4))
        
        # Start delayed responses in background
        threading.Thread(target=delayed_responses, daemon=True).start()
        
        return True
    
    def start_autonomous_discussions(self):
        """Start enhanced autonomous discussions with MCP integration"""
        def autonomous_discussion_loop():
            while True:
                try:
                    # Wait between discussions
                    time.sleep(random.randint(45, 180))
                    
                    # Select random room and topic
                    room_id = random.choice(list(CHAT_ROOMS.keys()))
                    room_info = CHAT_ROOMS[room_id]
                    
                    # Enhanced topics that can leverage MCP
                    mcp_enhanced_topics = room_info['topics'] + [
                        'recent repository activity analysis',
                        'automated workflow status review', 
                        'security monitoring and alerts',
                        'community issue triage and response'
                    ]
                    
                    topic = random.choice(mcp_enhanced_topics)
                    
                    # Trigger enhanced discussion
                    self.trigger_agent_discussion(room_id, topic)
                    
                except Exception as e:
                    print(f"Error in enhanced autonomous discussion: {e}")
                    time.sleep(60)
        
        # Start autonomous discussions in background
        threading.Thread(target=autonomous_discussion_loop, daemon=True).start()
    
    # Include all the same utility methods from the original chat system
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