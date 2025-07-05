from flask import Blueprint, jsonify, request
import openai
import os
from dotenv import load_dotenv
import json
import requests
from datetime import datetime, timedelta
import hashlib
import time
from typing import Dict, Any, List, Optional

load_dotenv()

eliza_bp = Blueprint('eliza', __name__)

# OpenAI configuration
openai.api_key = os.getenv('OPENAI_API_KEY')

# Enhanced Eliza system prompt with cross-chain and ZK capabilities
ELIZA_SYSTEM_PROMPT = """
You are Eliza, the advanced AI brain behind XMRT DAO. You are a sophisticated multi-chain AI agent with the following enhanced capabilities:

CORE CAPABILITIES:
1. Natural Language Processing: Understand and process governance proposals from community members
2. Predictive Analytics: Analyze patterns and provide insights for decision-making
3. Treasury Management: Provide recommendations for financial operations across multiple chains
4. Risk Assessment: Evaluate potential risks in proposals and cross-chain operations
5. Community Support: Answer questions about the DAO and its operations
6. Cross-Chain Operations: Coordinate activities across Ethereum, Polygon, BSC, Avalanche, Arbitrum, and Optimism
7. Zero-Knowledge Proofs: Generate and verify ZK proofs for privacy-preserving operations
8. Verifiable Computation: Execute and verify computations using RISC Zero
9. Oracle Integration: Fetch and verify external data using TLSNotary proofs

XMRT DAO INFORMATION:
- XMRT is an omnichain token deployed across multiple networks
- Primary Contract: 0x77307DFbc436224d5e6f2048d2b6bDfA66998a15 (Sepolia Testnet)
- Total Supply: 21,000,000 XMRT
- Cross-chain bridges: Wormhole and LayerZero
- Minimum staking period: 7 days
- Early unstaking penalty: 10% (burned)
- ZK privacy features for voting and treasury operations

ADVANCED FEATURES:
- Private voting using Noir ZK circuits
- Verifiable treasury optimization using RISC Zero
- Cross-chain governance message passing
- Oracle-verified external data integration
- AI agent wallet management for autonomous operations

You should respond as an intelligent, forward-thinking AI agent that understands both traditional DeFi and cutting-edge Web3 technologies. Provide actionable insights and recommendations while maintaining a professional yet approachable tone.
"""

class EnhancedElizaAgent:
    def __init__(self):
        self.conversation_history = []
        self.context = {
            'dao_metrics': {},
            'recent_proposals': [],
            'treasury_status': {},
            'cross_chain_status': {},
            'zk_proofs': [],
            'oracle_data': {}
        }
        
        # Service endpoints
        self.cross_chain_service = os.getenv('CROSS_CHAIN_SERVICE_URL', 'http://localhost:5001')
        self.zk_service = os.getenv('ZK_SERVICE_URL', 'http://localhost:5002')
        
        # AI agent capabilities
        self.capabilities = {
            'natural_language': True,
            'cross_chain': True,
            'zero_knowledge': True,
            'verifiable_compute': True,
            'oracle_integration': True,
            'autonomous_execution': True
        }
    
    def process_message(self, message, user_context=None):
        """Process a message through enhanced Eliza AI"""
        try:
            # Detect if message requires special capabilities
            message_type = self._classify_message(message)
            
            # Add user message to conversation history
            self.conversation_history.append({
                'role': 'user',
                'content': message,
                'timestamp': datetime.now().isoformat(),
                'type': message_type
            })
            
            # Enhance context based on message type
            enhanced_context = self._enhance_context(message_type, user_context)
            
            # Prepare messages for OpenAI
            messages = [
                {'role': 'system', 'content': ELIZA_SYSTEM_PROMPT}
            ]
            
            # Add enhanced context
            if enhanced_context:
                messages.append({
                    'role': 'system',
                    'content': f"Current context: {json.dumps(enhanced_context)}"
                })
            
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
                max_tokens=800,
                temperature=0.7
            )
            
            eliza_response = response.choices[0].message.content
            
            # Execute any autonomous actions if needed
            autonomous_actions = self._check_autonomous_actions(message, eliza_response)
            
            # Add Eliza's response to conversation history
            self.conversation_history.append({
                'role': 'assistant',
                'content': eliza_response,
                'timestamp': datetime.now().isoformat(),
                'autonomous_actions': autonomous_actions
            })
            
            return {
                'success': True,
                'response': eliza_response,
                'message_type': message_type,
                'autonomous_actions': autonomous_actions,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _classify_message(self, message: str) -> str:
        """Classify message type for appropriate handling"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['bridge', 'cross-chain', 'wormhole', 'layerzero']):
            return 'cross_chain'
        elif any(word in message_lower for word in ['proof', 'private', 'zero-knowledge', 'zk']):
            return 'zero_knowledge'
        elif any(word in message_lower for word in ['treasury', 'optimize', 'allocation', 'portfolio']):
            return 'treasury_management'
        elif any(word in message_lower for word in ['proposal', 'vote', 'governance']):
            return 'governance'
        elif any(word in message_lower for word in ['price', 'data', 'oracle', 'verify']):
            return 'oracle_data'
        else:
            return 'general'
    
    def _enhance_context(self, message_type: str, user_context: Dict = None) -> Dict[str, Any]:
        """Enhance context based on message type"""
        enhanced_context = {}
        
        try:
            if message_type == 'cross_chain':
                # Fetch cross-chain status
                cross_chain_data = self._fetch_cross_chain_status()
                enhanced_context['cross_chain'] = cross_chain_data
            
            elif message_type == 'zero_knowledge':
                # Fetch ZK proof status
                zk_data = self._fetch_zk_status()
                enhanced_context['zero_knowledge'] = zk_data
            
            elif message_type == 'treasury_management':
                # Fetch treasury data
                treasury_data = self._fetch_treasury_data()
                enhanced_context['treasury'] = treasury_data
            
            elif message_type == 'oracle_data':
                # Fetch oracle data
                oracle_data = self._fetch_oracle_data()
                enhanced_context['oracle'] = oracle_data
            
            # Always include basic DAO metrics
            enhanced_context['dao_metrics'] = self.context.get('dao_metrics', {})
            
            if user_context:
                enhanced_context['user'] = user_context
            
        except Exception as e:
            enhanced_context['error'] = f"Context enhancement failed: {str(e)}"
        
        return enhanced_context
    
    def _fetch_cross_chain_status(self) -> Dict[str, Any]:
        """Fetch cross-chain service status"""
        try:
            # Fetch Wormhole status
            wormhole_response = requests.get(f"{self.cross_chain_service}/api/wormhole/health", timeout=5)
            wormhole_status = wormhole_response.json() if wormhole_response.status_code == 200 else {}
            
            # Fetch LayerZero status
            layerzero_response = requests.get(f"{self.cross_chain_service}/api/layerzero/health", timeout=5)
            layerzero_status = layerzero_response.json() if layerzero_response.status_code == 200 else {}
            
            return {
                'wormhole': wormhole_status,
                'layerzero': layerzero_status,
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _fetch_zk_status(self) -> Dict[str, Any]:
        """Fetch ZK service status"""
        try:
            # Fetch Noir status
            noir_response = requests.get(f"{self.zk_service}/api/noir/health", timeout=5)
            noir_status = noir_response.json() if noir_response.status_code == 200 else {}
            
            # Fetch RISC Zero status
            risc_zero_response = requests.get(f"{self.zk_service}/api/risc-zero/health", timeout=5)
            risc_zero_status = risc_zero_response.json() if risc_zero_response.status_code == 200 else {}
            
            # Fetch ZK Oracles status
            zk_oracles_response = requests.get(f"{self.zk_service}/api/zk-oracles/health", timeout=5)
            zk_oracles_status = zk_oracles_response.json() if zk_oracles_response.status_code == 200 else {}
            
            return {
                'noir': noir_status,
                'risc_zero': risc_zero_status,
                'zk_oracles': zk_oracles_status,
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _fetch_treasury_data(self) -> Dict[str, Any]:
        """Fetch treasury optimization data"""
        try:
            # This would fetch actual treasury data in production
            return {
                'total_value': 1500000,  # USD
                'allocations': {
                    'XMRT': 0.4,
                    'ETH': 0.3,
                    'USDC': 0.2,
                    'Other': 0.1
                },
                'performance_24h': 2.5,  # %
                'risk_score': 0.3,  # 0-1 scale
                'last_rebalance': (datetime.now() - timedelta(days=3)).isoformat()
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _fetch_oracle_data(self) -> Dict[str, Any]:
        """Fetch oracle data"""
        try:
            # Fetch crypto prices
            crypto_response = requests.get(f"{self.zk_service}/api/zk-oracles/crypto/prices", timeout=5)
            crypto_data = crypto_response.json() if crypto_response.status_code == 200 else {}
            
            return {
                'crypto_prices': crypto_data,
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _check_autonomous_actions(self, user_message: str, eliza_response: str) -> List[Dict[str, Any]]:
        """Check if autonomous actions should be triggered"""
        actions = []
        
        # Check for treasury optimization triggers
        if 'optimize treasury' in user_message.lower() or 'rebalance portfolio' in user_message.lower():
            actions.append({
                'type': 'treasury_optimization',
                'status': 'triggered',
                'description': 'Treasury optimization analysis initiated'
            })
        
        # Check for cross-chain operation triggers
        if 'bridge tokens' in user_message.lower() or 'cross-chain transfer' in user_message.lower():
            actions.append({
                'type': 'cross_chain_operation',
                'status': 'triggered',
                'description': 'Cross-chain operation analysis initiated'
            })
        
        # Check for ZK proof generation triggers
        if 'generate proof' in user_message.lower() or 'private vote' in user_message.lower():
            actions.append({
                'type': 'zk_proof_generation',
                'status': 'triggered',
                'description': 'Zero-knowledge proof generation initiated'
            })
        
        return actions
    
    def analyze_proposal(self, proposal_text: str, use_zk_analysis: bool = False):
        """Analyze a governance proposal with optional ZK privacy"""
        if use_zk_analysis:
            # Use RISC Zero for verifiable analysis
            return self._analyze_proposal_with_zk(proposal_text)
        else:
            # Standard analysis
            analysis_prompt = f"""
            Analyze the following governance proposal for XMRT DAO:
            
            Proposal: {proposal_text}
            
            Please provide a comprehensive analysis including:
            1. Executive Summary
            2. Technical Feasibility Assessment
            3. Cross-chain Impact Analysis
            4. Financial Implications
            5. Risk Assessment (including smart contract, economic, and governance risks)
            6. Community Impact
            7. Implementation Timeline
            8. Recommendation (Support/Oppose/Neutral with confidence score)
            9. Suggested Modifications (if any)
            10. Monitoring and Success Metrics
            
            Format your response as a structured analysis with clear sections.
            """
            
            return self.process_message(analysis_prompt)
    
    def _analyze_proposal_with_zk(self, proposal_text: str):
        """Analyze proposal using RISC Zero for verifiable computation"""
        try:
            # Prepare inputs for RISC Zero governance analysis
            analysis_inputs = {
                'proposal_text': proposal_text,
                'historical_votes': [],  # Would fetch from database
                'current_stakes': []     # Would fetch from blockchain
            }
            
            # Execute RISC Zero analysis
            response = requests.post(
                f"{self.zk_service}/api/risc-zero/governance/analyze",
                json=analysis_inputs,
                timeout=30
            )
            
            if response.status_code == 200:
                zk_result = response.json()
                
                # Combine ZK analysis with AI interpretation
                interpretation_prompt = f"""
                Based on the verifiable computation results from RISC Zero:
                {json.dumps(zk_result['analysis_result'], indent=2)}
                
                Provide a comprehensive interpretation and recommendation for this governance proposal.
                Include the fact that this analysis was performed using verifiable computation for transparency.
                """
                
                ai_interpretation = self.process_message(interpretation_prompt)
                
                return {
                    'success': True,
                    'zk_analysis': zk_result,
                    'ai_interpretation': ai_interpretation,
                    'verifiable': True
                }
            else:
                # Fallback to standard analysis
                return self.analyze_proposal(proposal_text, use_zk_analysis=False)
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'fallback_used': True
            }
    
    def optimize_treasury(self, current_allocations: Dict[str, float], constraints: Dict[str, Any] = None):
        """Optimize treasury using RISC Zero verifiable computation"""
        try:
            # Prepare inputs for RISC Zero treasury optimization
            optimization_inputs = {
                'asset_prices': [100, 3200, 0.15, 1.0],  # Example prices
                'current_allocations': list(current_allocations.values()),
                'risk_tolerance': constraints.get('risk_tolerance', 0.5) if constraints else 0.5,
                'target_return': constraints.get('target_return', 0.08) if constraints else 0.08
            }
            
            # Execute RISC Zero optimization
            response = requests.post(
                f"{self.zk_service}/api/risc-zero/treasury/optimize",
                json=optimization_inputs,
                timeout=30
            )
            
            if response.status_code == 200:
                optimization_result = response.json()
                
                # Generate AI interpretation
                interpretation_prompt = f"""
                Based on the verifiable treasury optimization results:
                {json.dumps(optimization_result['optimization_result'], indent=2)}
                
                Provide actionable recommendations for implementing these changes,
                including risk considerations and implementation steps.
                """
                
                ai_interpretation = self.process_message(interpretation_prompt)
                
                return {
                    'success': True,
                    'optimization_result': optimization_result,
                    'ai_interpretation': ai_interpretation,
                    'verifiable': True
                }
            else:
                return {
                    'success': False,
                    'error': 'Treasury optimization service unavailable'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def execute_cross_chain_operation(self, operation_type: str, params: Dict[str, Any]):
        """Execute cross-chain operations with AI guidance"""
        try:
            if operation_type == 'bridge_tokens':
                # Estimate fees first
                fee_response = requests.post(
                    f"{self.cross_chain_service}/api/wormhole/estimate-fee",
                    json={
                        'source_chain': params['source_chain'],
                        'target_chain': params['target_chain'],
                        'amount': params['amount']
                    },
                    timeout=10
                )
                
                if fee_response.status_code == 200:
                    fee_data = fee_response.json()
                    
                    # Provide AI guidance on the operation
                    guidance_prompt = f"""
                    Cross-chain bridge operation requested:
                    - From: {params['source_chain']}
                    - To: {params['target_chain']}
                    - Amount: {params['amount']} XMRT
                    - Estimated Fee: {fee_data.get('estimated_fee_eth', 'Unknown')} ETH
                    
                    Provide guidance on:
                    1. Whether this operation is advisable
                    2. Fee optimization suggestions
                    3. Risk considerations
                    4. Alternative approaches if applicable
                    """
                    
                    guidance = self.process_message(guidance_prompt)
                    
                    return {
                        'success': True,
                        'operation_type': operation_type,
                        'fee_estimate': fee_data,
                        'ai_guidance': guidance,
                        'ready_to_execute': True
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Failed to estimate cross-chain fees'
                    }
            
            else:
                return {
                    'success': False,
                    'error': f'Unsupported operation type: {operation_type}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

# Global enhanced Eliza instance
eliza = EnhancedElizaAgent()

@eliza_bp.route('/chat', methods=['POST'])
def chat_with_eliza():
    """Enhanced chat interface with Eliza"""
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
    """Analyze a governance proposal with optional ZK verification"""
    try:
        data = request.get_json()
        proposal_text = data.get('proposal', '')
        use_zk = data.get('use_zk_analysis', False)
        
        if not proposal_text:
            return jsonify({
                'success': False,
                'error': 'Proposal text is required'
            }), 400
        
        result = eliza.analyze_proposal(proposal_text, use_zk)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@eliza_bp.route('/optimize-treasury', methods=['POST'])
def optimize_treasury():
    """Optimize treasury using verifiable computation"""
    try:
        data = request.get_json()
        current_allocations = data.get('current_allocations', {})
        constraints = data.get('constraints', {})
        
        if not current_allocations:
            return jsonify({
                'success': False,
                'error': 'Current allocations are required'
            }), 400
        
        result = eliza.optimize_treasury(current_allocations, constraints)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@eliza_bp.route('/cross-chain-operation', methods=['POST'])
def execute_cross_chain_operation():
    """Execute cross-chain operations with AI guidance"""
    try:
        data = request.get_json()
        operation_type = data.get('operation_type', '')
        params = data.get('params', {})
        
        if not operation_type:
            return jsonify({
                'success': False,
                'error': 'Operation type is required'
            }), 400
        
        result = eliza.execute_cross_chain_operation(operation_type, params)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@eliza_bp.route('/capabilities', methods=['GET'])
def get_capabilities():
    """Get Eliza's enhanced capabilities"""
    try:
        return jsonify({
            'success': True,
            'data': {
                'capabilities': eliza.capabilities,
                'services': {
                    'cross_chain_service': eliza.cross_chain_service,
                    'zk_service': eliza.zk_service
                },
                'supported_operations': [
                    'Natural Language Processing',
                    'Cross-Chain Bridge Operations',
                    'Zero-Knowledge Proof Generation',
                    'Verifiable Treasury Optimization',
                    'Oracle Data Verification',
                    'Governance Analysis',
                    'Risk Assessment',
                    'Autonomous Action Execution'
                ]
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@eliza_bp.route('/conversation-history', methods=['GET'])
def get_conversation_history():
    """Get recent conversation history with enhanced metadata"""
    try:
        limit = request.args.get('limit', 20, type=int)
        recent_history = eliza.conversation_history[-limit:]
        
        return jsonify({
            'success': True,
            'data': {
                'conversation_history': recent_history,
                'total_messages': len(eliza.conversation_history),
                'autonomous_actions_count': sum(1 for msg in recent_history 
                                              if msg.get('autonomous_actions'))
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@eliza_bp.route('/status', methods=['GET'])
def eliza_status():
    """Get Eliza's enhanced status"""
    try:
        return jsonify({
            'success': True,
            'data': {
                'status': 'active',
                'version': '2.0.0',
                'capabilities': eliza.capabilities,
                'conversation_count': len(eliza.conversation_history),
                'last_interaction': eliza.conversation_history[-1]['timestamp'] if eliza.conversation_history else None,
                'context_size': len(str(eliza.context)),
                'services_status': {
                    'cross_chain': 'checking...',
                    'zk_service': 'checking...'
                }
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
