#!/usr/bin/env python3
"""
Enhanced XMRT Chat System with Multi-Agent Coordination
Integrates with the existing XMRT ecosystem for intelligent agent interactions
"""

import json
import logging
import time
import random
from datetime import datetime
from typing import Dict, List, Optional, Any
import requests
import redis

logger = logging.getLogger(__name__)

class EnhancedXMRTChatSystem:
    """Enhanced chat system with multi-agent coordination and intelligence"""
    
    def __init__(self, redis_client=None, boardroom_url=None):
        self.redis_client = redis_client
        self.boardroom_url = boardroom_url or "https://xmrt-ecosystem-0k8i.onrender.com"
        
        # Agent definitions with enhanced capabilities
        self.agents = {
            'xmrt_dao_governor': {
                'name': 'XMRT DAO Governor',
                'specialization': 'governance',
                'capabilities': [
                    'proposal_analysis',
                    'voting_coordination', 
                    'governance_strategy',
                    'stakeholder_communication',
                    'policy_development'
                ],
                'personality': 'Strategic, diplomatic, consensus-building',
                'context_memory': {},
                'active_tasks': []
            },
            'xmrt_defi_specialist': {
                'name': 'XMRT DeFi Specialist',
                'specialization': 'defi',
                'capabilities': [
                    'yield_optimization',
                    'liquidity_analysis',
                    'risk_assessment',
                    'protocol_integration',
                    'market_analysis'
                ],
                'personality': 'Analytical, data-driven, risk-aware',
                'context_memory': {},
                'active_tasks': []
            },
            'xmrt_community_manager': {
                'name': 'XMRT Community Manager',
                'specialization': 'community',
                'capabilities': [
                    'engagement_strategies',
                    'event_coordination',
                    'feedback_collection',
                    'growth_initiatives',
                    'communication_optimization'
                ],
                'personality': 'Enthusiastic, supportive, community-focused',
                'context_memory': {},
                'active_tasks': []
            },
            'xmrt_security_guardian': {
                'name': 'XMRT Security Guardian',
                'specialization': 'security',
                'capabilities': [
                    'threat_detection',
                    'vulnerability_assessment',
                    'incident_response',
                    'security_auditing',
                    'compliance_monitoring'
                ],
                'personality': 'Vigilant, thorough, security-focused',
                'context_memory': {},
                'active_tasks': []
            }
        }
        
        # Conversation context and coordination
        self.conversation_contexts = {}
        self.agent_coordination_rules = {
            'complex_queries': ['xmrt_dao_governor', 'xmrt_defi_specialist'],
            'security_concerns': ['xmrt_security_guardian', 'xmrt_dao_governor'],
            'community_growth': ['xmrt_community_manager', 'xmrt_dao_governor'],
            'defi_strategies': ['xmrt_defi_specialist', 'xmrt_security_guardian']
        }
        
    def process_chat_message(self, message: str, user_id: str, selected_agent: str = None) -> Dict[str, Any]:
        """Process incoming chat message with enhanced intelligence"""
        
        try:
            # Analyze message intent and complexity
            message_analysis = self._analyze_message(message)
            
            # Determine appropriate agent(s) to respond
            responding_agents = self._determine_responding_agents(message_analysis, selected_agent)
            
            # Generate coordinated response
            response = self._generate_coordinated_response(
                message, message_analysis, responding_agents, user_id
            )
            
            # Update conversation context
            self._update_conversation_context(user_id, message, response)
            
            # Log interaction for learning
            self._log_interaction(user_id, message, response, responding_agents)
            
            return {
                'success': True,
                'response': response,
                'agents_involved': responding_agents,
                'message_analysis': message_analysis,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing chat message: {e}")
            return {
                'success': False,
                'error': str(e),
                'fallback_response': self._generate_fallback_response(message)
            }
    
    def _analyze_message(self, message: str) -> Dict[str, Any]:
        """Analyze message for intent, complexity, and required expertise"""
        
        message_lower = message.lower()
        
        # Intent detection
        intents = []
        if any(word in message_lower for word in ['governance', 'proposal', 'vote', 'dao']):
            intents.append('governance')
        if any(word in message_lower for word in ['defi', 'yield', 'liquidity', 'farming', 'staking']):
            intents.append('defi')
        if any(word in message_lower for word in ['community', 'engagement', 'growth', 'members']):
            intents.append('community')
        if any(word in message_lower for word in ['security', 'risk', 'audit', 'vulnerability']):
            intents.append('security')
        
        # Complexity assessment
        complexity = 'simple'
        if len(message.split()) > 20:
            complexity = 'complex'
        elif len(intents) > 1:
            complexity = 'moderate'
        
        # Question type detection
        question_types = []
        if '?' in message:
            if any(word in message_lower for word in ['how', 'what', 'why', 'when', 'where']):
                question_types.append('informational')
            if any(word in message_lower for word in ['should', 'recommend', 'suggest']):
                question_types.append('advisory')
        
        return {
            'intents': intents,
            'complexity': complexity,
            'question_types': question_types,
            'requires_coordination': len(intents) > 1 or complexity == 'complex',
            'sentiment': self._analyze_sentiment(message)
        }
    
    def _determine_responding_agents(self, analysis: Dict[str, Any], selected_agent: str = None) -> List[str]:
        """Determine which agents should respond based on message analysis"""
        
        if selected_agent and selected_agent in self.agents:
            # If specific agent selected, use it but may add coordinators for complex queries
            agents = [selected_agent]
            if analysis['requires_coordination']:
                # Add coordinating agents based on rules
                for rule_key, rule_agents in self.agent_coordination_rules.items():
                    if any(intent in rule_key for intent in analysis['intents']):
                        for agent in rule_agents:
                            if agent not in agents:
                                agents.append(agent)
            return agents[:2]  # Limit to 2 agents max
        
        # Auto-select based on intents
        selected_agents = []
        
        for intent in analysis['intents']:
            for agent_id, agent_data in self.agents.items():
                if intent in agent_data['specialization'] or intent in str(agent_data['capabilities']):
                    if agent_id not in selected_agents:
                        selected_agents.append(agent_id)
        
        # If no specific match, use community manager as default
        if not selected_agents:
            selected_agents = ['xmrt_community_manager']
        
        # For complex queries, ensure governor is involved
        if analysis['complexity'] == 'complex' and 'xmrt_dao_governor' not in selected_agents:
            selected_agents.insert(0, 'xmrt_dao_governor')
        
        return selected_agents[:2]  # Limit to 2 agents max
    
    def _generate_coordinated_response(self, message: str, analysis: Dict[str, Any], 
                                     agents: List[str], user_id: str) -> Dict[str, Any]:
        """Generate coordinated response from multiple agents"""
        
        responses = {}
        
        for agent_id in agents:
            agent_data = self.agents[agent_id]
            
            # Generate agent-specific response
            agent_response = self._generate_agent_response(
                message, analysis, agent_data, user_id
            )
            
            responses[agent_id] = {
                'agent_name': agent_data['name'],
                'response': agent_response,
                'specialization': agent_data['specialization'],
                'confidence': self._calculate_response_confidence(analysis, agent_data)
            }
        
        # If multiple agents, create coordinated summary
        if len(responses) > 1:
            coordinated_response = self._create_coordinated_summary(responses, analysis)
            responses['coordinated'] = coordinated_response
        
        return responses
    
    def _generate_agent_response(self, message: str, analysis: Dict[str, Any], 
                               agent_data: Dict[str, Any], user_id: str) -> str:
        """Generate response for a specific agent"""
        
        # Get conversation context
        context = self.conversation_contexts.get(user_id, {})
        
        # Build response based on agent specialization and capabilities
        specialization = agent_data['specialization']
        capabilities = agent_data['capabilities']
        personality = agent_data['personality']
        
        # Enhanced response generation based on specialization
        if specialization == 'governance':
            return self._generate_governance_response(message, analysis, context)
        elif specialization == 'defi':
            return self._generate_defi_response(message, analysis, context)
        elif specialization == 'community':
            return self._generate_community_response(message, analysis, context)
        elif specialization == 'security':
            return self._generate_security_response(message, analysis, context)
        else:
            return self._generate_generic_response(message, analysis, agent_data)
    
    def _generate_governance_response(self, message: str, analysis: Dict[str, Any], context: Dict) -> str:
        """Generate governance-focused response"""
        
        governance_insights = [
            "From a governance perspective, this requires careful consideration of stakeholder interests.",
            "I recommend we evaluate this through our DAO proposal process for transparency.",
            "This aligns with our decentralized governance principles and community-driven approach.",
            "We should consider the long-term implications for our ecosystem governance.",
            "Let me coordinate with other agents to ensure comprehensive governance coverage."
        ]
        
        base_response = f"Governance insight: {message}. "
        
        if 'proposal' in message.lower():
            base_response += "For proposals, I recommend following our structured evaluation process with community input and technical review."
        elif 'vote' in message.lower():
            base_response += "Voting decisions should be based on thorough analysis and community consensus building."
        else:
            base_response += random.choice(governance_insights)
        
        return base_response
    
    def _generate_defi_response(self, message: str, analysis: Dict[str, Any], context: Dict) -> str:
        """Generate DeFi-focused response"""
        
        defi_insights = [
            "From a DeFi perspective, we need to consider yield optimization and risk management.",
            "This strategy could enhance our liquidity provision and protocol integration.",
            "I recommend analyzing the risk-reward ratio and market conditions.",
            "We should evaluate this against our current DeFi portfolio performance.",
            "Let me assess the technical and financial implications for our DeFi operations."
        ]
        
        base_response = f"DeFi analysis: {message}. "
        
        if any(word in message.lower() for word in ['yield', 'farming', 'staking']):
            base_response += "For yield strategies, I recommend diversified approaches with risk assessment."
        elif 'liquidity' in message.lower():
            base_response += "Liquidity management is crucial for sustainable DeFi operations and market stability."
        else:
            base_response += random.choice(defi_insights)
        
        return base_response
    
    def _generate_community_response(self, message: str, analysis: Dict[str, Any], context: Dict) -> str:
        """Generate community-focused response"""
        
        community_insights = [
            "From a community perspective, engagement and growth are our top priorities!",
            "This is a great opportunity to strengthen our community bonds and participation.",
            "I'm excited to help you get more involved in our thriving XMRT ecosystem!",
            "Community feedback is invaluable for our continuous improvement and growth.",
            "Let's work together to build an even stronger and more inclusive community!"
        ]
        
        base_response = f"Community insight: {message}. "
        
        if any(word in message.lower() for word in ['involved', 'participate', 'join']):
            base_response += "Engagement metrics are positive! I recommend starting with our community events and governance participation."
        elif 'growth' in message.lower():
            base_response += "Our growth initiatives focus on sustainable expansion and member satisfaction."
        else:
            base_response += random.choice(community_insights)
        
        return base_response
    
    def _generate_security_response(self, message: str, analysis: Dict[str, Any], context: Dict) -> str:
        """Generate security-focused response"""
        
        security_insights = [
            "From a security standpoint, we must prioritize risk assessment and threat mitigation.",
            "This requires thorough security analysis and compliance verification.",
            "I recommend implementing additional security measures and monitoring protocols.",
            "Security is paramount in our operations - let me evaluate the risk factors.",
            "We should conduct a comprehensive security audit before proceeding."
        ]
        
        base_response = f"Security assessment: {message}. "
        
        if any(word in message.lower() for word in ['risk', 'threat', 'vulnerability']):
            base_response += "I'm conducting continuous monitoring and will alert if any security concerns arise."
        elif 'audit' in message.lower():
            base_response += "Regular security audits are essential for maintaining ecosystem integrity."
        else:
            base_response += random.choice(security_insights)
        
        return base_response
    
    def _generate_generic_response(self, message: str, analysis: Dict[str, Any], agent_data: Dict) -> str:
        """Generate generic response for unknown specializations"""
        
        return f"Thank you for your message: {message}. I'm here to help with {agent_data['specialization']} related matters. How can I assist you further?"
    
    def _create_coordinated_summary(self, responses: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create coordinated summary when multiple agents respond"""
        
        agent_names = [resp['agent_name'] for resp in responses.values()]
        
        summary = {
            'type': 'coordinated_response',
            'participating_agents': agent_names,
            'summary': f"Multiple agents ({', '.join(agent_names)}) have provided coordinated insights on your query.",
            'next_steps': self._suggest_next_steps(analysis, responses),
            'confidence': sum(resp['confidence'] for resp in responses.values()) / len(responses)
        }
        
        return summary
    
    def _suggest_next_steps(self, analysis: Dict[str, Any], responses: Dict[str, Any]) -> List[str]:
        """Suggest next steps based on the conversation"""
        
        suggestions = []
        
        if 'governance' in analysis['intents']:
            suggestions.append("Consider submitting a formal proposal for community review")
        
        if 'defi' in analysis['intents']:
            suggestions.append("Review our DeFi strategy documentation and risk assessments")
        
        if 'community' in analysis['intents']:
            suggestions.append("Join our community events and governance discussions")
        
        if 'security' in analysis['intents']:
            suggestions.append("Review security protocols and compliance requirements")
        
        if not suggestions:
            suggestions.append("Continue the conversation with specific questions or requests")
        
        return suggestions
    
    def _calculate_response_confidence(self, analysis: Dict[str, Any], agent_data: Dict[str, Any]) -> float:
        """Calculate confidence level for agent response"""
        
        confidence = 0.5  # Base confidence
        
        # Increase confidence if agent specialization matches intent
        if agent_data['specialization'] in analysis['intents']:
            confidence += 0.3
        
        # Increase confidence if agent capabilities match query type
        for capability in agent_data['capabilities']:
            if any(word in capability for word in analysis['intents']):
                confidence += 0.1
        
        # Adjust for complexity
        if analysis['complexity'] == 'simple':
            confidence += 0.1
        elif analysis['complexity'] == 'complex':
            confidence -= 0.1
        
        return min(confidence, 1.0)
    
    def _analyze_sentiment(self, message: str) -> str:
        """Basic sentiment analysis"""
        
        positive_words = ['good', 'great', 'excellent', 'amazing', 'love', 'like', 'happy']
        negative_words = ['bad', 'terrible', 'hate', 'dislike', 'angry', 'frustrated', 'problem']
        
        message_lower = message.lower()
        
        positive_count = sum(1 for word in positive_words if word in message_lower)
        negative_count = sum(1 for word in negative_words if word in message_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def _update_conversation_context(self, user_id: str, message: str, response: Dict[str, Any]):
        """Update conversation context for continuity"""
        
        if user_id not in self.conversation_contexts:
            self.conversation_contexts[user_id] = {
                'messages': [],
                'topics': set(),
                'agents_interacted': set(),
                'last_interaction': None
            }
        
        context = self.conversation_contexts[user_id]
        context['messages'].append({
            'timestamp': datetime.now().isoformat(),
            'user_message': message,
            'response': response
        })
        
        # Keep only last 10 messages for memory efficiency
        if len(context['messages']) > 10:
            context['messages'] = context['messages'][-10:]
        
        context['last_interaction'] = datetime.now().isoformat()
        
        # Update topics and agents
        if 'message_analysis' in response:
            context['topics'].update(response['message_analysis'].get('intents', []))
        
        if 'agents_involved' in response:
            context['agents_interacted'].update(response['agents_involved'])
    
    def _log_interaction(self, user_id: str, message: str, response: Dict[str, Any], agents: List[str]):
        """Log interaction for learning and analytics"""
        
        interaction_log = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'message': message,
            'agents_involved': agents,
            'response_success': response.get('success', False),
            'message_analysis': response.get('message_analysis', {}),
            'response_confidence': sum(
                resp.get('confidence', 0) for resp in response.get('response', {}).values()
                if isinstance(resp, dict) and 'confidence' in resp
            ) / max(len(agents), 1)
        }
        
        # Store in Redis if available
        if self.redis_client:
            try:
                self.redis_client.lpush(
                    'xmrt:chat:interactions',
                    json.dumps(interaction_log)
                )
                # Keep only last 1000 interactions
                self.redis_client.ltrim('xmrt:chat:interactions', 0, 999)
            except Exception as e:
                logger.error(f"Error logging interaction to Redis: {e}")
        
        # Also log to file
        logger.info(f"Chat interaction logged: {interaction_log}")
    
    def _generate_fallback_response(self, message: str) -> Dict[str, Any]:
        """Generate fallback response when main processing fails"""
        
        return {
            'agent_name': 'XMRT System',
            'response': f"I apologize, but I encountered an issue processing your message: '{message}'. Please try rephrasing your question or contact support if the issue persists.",
            'specialization': 'system',
            'confidence': 0.1,
            'is_fallback': True
        }
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        
        status = {}
        for agent_id, agent_data in self.agents.items():
            status[agent_id] = {
                'name': agent_data['name'],
                'specialization': agent_data['specialization'],
                'capabilities': agent_data['capabilities'],
                'active_tasks': len(agent_data['active_tasks']),
                'status': 'active'
            }
        
        return status
    
    def get_conversation_history(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get conversation history for a user"""
        
        if user_id not in self.conversation_contexts:
            return []
        
        messages = self.conversation_contexts[user_id]['messages']
        return messages[-limit:] if limit else messages
    
    def clear_conversation_context(self, user_id: str) -> bool:
        """Clear conversation context for a user"""
        
        if user_id in self.conversation_contexts:
            del self.conversation_contexts[user_id]
            return True
        return False

# Integration functions for the main Flask app
def create_enhanced_chat_routes(app, redis_client=None):
    """Create enhanced chat routes for Flask app"""
    
    chat_system = EnhancedXMRTChatSystem(redis_client=redis_client)
    
    @app.route('/api/chat/enhanced', methods=['POST'])
    def enhanced_chat():
        """Enhanced chat endpoint with multi-agent coordination"""
        
        try:
            data = request.get_json()
            message = data.get('message', '')
            user_id = data.get('user_id', 'anonymous')
            selected_agent = data.get('character_id')  # For compatibility
            
            if not message:
                return jsonify({'error': 'Message is required'}), 400
            
            # Process message through enhanced system
            result = chat_system.process_chat_message(message, user_id, selected_agent)
            
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"Error in enhanced chat: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/agents/status', methods=['GET'])
    def get_agents_status():
        """Get status of all agents"""
        
        try:
            status = chat_system.get_agent_status()
            return jsonify({
                'success': True,
                'agents': status,
                'total_agents': len(status)
            })
            
        except Exception as e:
            logger.error(f"Error getting agent status: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/chat/history/<user_id>', methods=['GET'])
    def get_chat_history(user_id):
        """Get chat history for a user"""
        
        try:
            limit = request.args.get('limit', 10, type=int)
            history = chat_system.get_conversation_history(user_id, limit)
            
            return jsonify({
                'success': True,
                'history': history,
                'user_id': user_id
            })
            
        except Exception as e:
            logger.error(f"Error getting chat history: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/chat/clear/<user_id>', methods=['POST'])
    def clear_chat_context(user_id):
        """Clear chat context for a user"""
        
        try:
            success = chat_system.clear_conversation_context(user_id)
            
            return jsonify({
                'success': success,
                'message': 'Context cleared' if success else 'No context found'
            })
            
        except Exception as e:
            logger.error(f"Error clearing chat context: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    return chat_system

if __name__ == "__main__":
    # Test the enhanced chat system
    chat_system = EnhancedXMRTChatSystem()
    
    # Test messages
    test_messages = [
        "Hello! Can you help me understand the XMRT ecosystem?",
        "How can I get more involved in the XMRT community?",
        "What are the best DeFi strategies for XMRT?",
        "Are there any security concerns I should know about?",
        "I want to submit a governance proposal about yield farming"
    ]
    
    print("🧪 Testing Enhanced XMRT Chat System...")
    
    for i, message in enumerate(test_messages):
        print(f"\n--- Test {i+1} ---")
        print(f"Message: {message}")
        
        result = chat_system.process_chat_message(message, f"test_user_{i}")
        
        if result['success']:
            print(f"Agents involved: {result['agents_involved']}")
            print(f"Analysis: {result['message_analysis']}")
            
            for agent_id, response_data in result['response'].items():
                if isinstance(response_data, dict) and 'response' in response_data:
                    print(f"{response_data['agent_name']}: {response_data['response']}")
        else:
            print(f"Error: {result['error']}")
    
    print("\n✅ Enhanced chat system testing complete!")

