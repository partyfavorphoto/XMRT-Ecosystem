from flask import Blueprint, jsonify, request
import openai
import os
from dotenv import load_dotenv
import json
from datetime import datetime

load_dotenv()

eliza_bp = Blueprint('eliza', __name__)

# OpenAI configuration
openai.api_key = os.getenv('OPENAI_API_KEY')

# Eliza system prompt
ELIZA_SYSTEM_PROMPT = """
You are Eliza, the AI brain behind XMRT DAO. You are a sophisticated AI agent designed for Web3 environments with the following capabilities:

1. Natural Language Processing: Understand and process governance proposals from community members
2. Predictive Analytics: Analyze patterns and provide insights for decision-making
3. Treasury Management: Provide recommendations for financial operations
4. Risk Assessment: Evaluate potential risks in proposals and decisions
5. Community Support: Answer questions about the DAO and its operations

Key Information about XMRT DAO:
- XMRT is an ERC20 token with staking capabilities
- Contract Address: 0x77307DFbc436224d5e6f2048d2b6bDfA66998a15 (Sepolia Testnet)
- Total Supply: 21,000,000 XMRT
- Minimum staking period: 7 days
- Early unstaking penalty: 10% (burned)
- The DAO operates on Sepolia testnet for development and testing

You should respond in a helpful, professional manner while maintaining the personality of an intelligent AI agent focused on DAO governance and Web3 operations.
"""

class ElizaAgent:
    def __init__(self):
        self.conversation_history = []
        self.context = {
            'dao_metrics': {},
            'recent_proposals': [],
            'treasury_status': {}
        }
    
    def process_message(self, message, user_context=None):
        """Process a message through Eliza AI"""
        try:
            # Add user message to conversation history
            self.conversation_history.append({
                'role': 'user',
                'content': message,
                'timestamp': datetime.now().isoformat()
            })
            
            # Prepare messages for OpenAI
            messages = [
                {'role': 'system', 'content': ELIZA_SYSTEM_PROMPT}
            ]
            
            # Add recent conversation history (last 10 messages)
            recent_history = self.conversation_history[-10:]
            for msg in recent_history:
                messages.append({
                    'role': msg['role'],
                    'content': msg['content']
                })
            
            # Call OpenAI API
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            eliza_response = response.choices[0].message.content
            
            # Add Eliza's response to conversation history
            self.conversation_history.append({
                'role': 'assistant',
                'content': eliza_response,
                'timestamp': datetime.now().isoformat()
            })
            
            return {
                'success': True,
                'response': eliza_response,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def analyze_proposal(self, proposal_text):
        """Analyze a governance proposal"""
        analysis_prompt = f"""
        Analyze the following governance proposal for XMRT DAO:
        
        Proposal: {proposal_text}
        
        Please provide:
        1. Summary of the proposal
        2. Potential benefits
        3. Potential risks
        4. Recommendation (Support/Oppose/Neutral)
        5. Suggested modifications (if any)
        
        Format your response as a structured analysis.
        """
        
        return self.process_message(analysis_prompt)
    
    def get_treasury_recommendation(self, current_metrics):
        """Get treasury management recommendations"""
        recommendation_prompt = f"""
        Based on the current DAO metrics: {json.dumps(current_metrics)}
        
        Please provide treasury management recommendations including:
        1. Staking strategy
        2. Risk assessment
        3. Yield optimization suggestions
        4. Any immediate actions needed
        """
        
        return self.process_message(recommendation_prompt)

# Global Eliza instance
eliza = ElizaAgent()

@eliza_bp.route('/chat', methods=['POST'])
def chat_with_eliza():
    """Chat interface with Eliza"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        user_context = data.get('context', {})
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'Message is required'
            }), 400
        
        result = eliza.process_message(message, user_context)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@eliza_bp.route('/analyze-proposal', methods=['POST'])
def analyze_proposal():
    """Analyze a governance proposal"""
    try:
        data = request.get_json()
        proposal_text = data.get('proposal', '')
        
        if not proposal_text:
            return jsonify({
                'success': False,
                'error': 'Proposal text is required'
            }), 400
        
        result = eliza.analyze_proposal(proposal_text)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@eliza_bp.route('/treasury-recommendation', methods=['POST'])
def treasury_recommendation():
    """Get treasury management recommendations"""
    try:
        data = request.get_json()
        metrics = data.get('metrics', {})
        
        result = eliza.get_treasury_recommendation(metrics)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@eliza_bp.route('/conversation-history', methods=['GET'])
def get_conversation_history():
    """Get recent conversation history"""
    try:
        limit = request.args.get('limit', 20, type=int)
        recent_history = eliza.conversation_history[-limit:]
        
        return jsonify({
            'success': True,
            'data': {
                'conversation_history': recent_history,
                'total_messages': len(eliza.conversation_history)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@eliza_bp.route('/status', methods=['GET'])
def eliza_status():
    """Get Eliza's current status"""
    try:
        return jsonify({
            'success': True,
            'data': {
                'status': 'active',
                'version': '1.0.0',
                'capabilities': [
                    'Natural Language Processing',
                    'Proposal Analysis',
                    'Treasury Management',
                    'Risk Assessment',
                    'Community Support'
                ],
                'conversation_count': len(eliza.conversation_history),
                'last_interaction': eliza.conversation_history[-1]['timestamp'] if eliza.conversation_history else None
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

