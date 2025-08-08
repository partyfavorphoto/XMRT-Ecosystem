from flask import Flask, jsonify, request
from web3 import Web3
import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Configuration for connecting to the Ethereum network
INFURA_URL = os.getenv('INFURA_URL')
PRIVATE_KEY = os.getenv('PRIVATE_KEY')
CONTRACT_ADDRESS = os.getenv('CONTRACT_ADDRESS')

# AI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
QWEN_API_KEY = os.getenv('QWEN_API_KEY')  # For Alibaba Qwen2.5
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')  # Backup option

with open(os.path.join(os.path.dirname(__file__), 'abi.json'), 'r') as f:
    CONTRACT_ABI = f.read()

w3 = Web3(Web3.HTTPProvider(INFURA_URL))

# AI Router Class
class XMRTAIRouter:
    def __init__(self):
        self.request_log = []
        self.cost_tracker = {
            'free_requests': 0,
            'nano_requests': 0, 
            'full_requests': 0,
            'total_cost': 0.0,
            'daily_savings': 0.0
        }
    
    def analyze_complexity(self, query, context=None):
        """Determine which AI model to use based on query complexity"""
        query_lower = query.lower()
        
        # Simple queries -> Free models (Qwen2.5)
        simple_patterns = [
            'hello', 'hi', 'what is', 'explain', 'define', 'summary',
            'list', 'show me', 'help', 'basic', 'simple', 'quick'
        ]
        
        # Blockchain/DAO specific medium complexity -> GPT-5 nano
        medium_patterns = [
            'contract', 'transaction', 'blockchain', 'ethereum', 'dao',
            'governance', 'token', 'wallet', 'gas', 'deploy'
        ]
        
        # Complex analysis -> GPT-5 full
        complex_patterns = [
            'analyze strategy', 'optimize', 'integrate complex', 'audit',
            'security analysis', 'advanced governance', 'cross-chain',
            'defi strategy', 'tokenomics'
        ]
        
        if any(pattern in query_lower for pattern in simple_patterns):
            return 'simple'
        elif any(pattern in query_lower for pattern in complex_patterns):
            return 'complex'
        elif any(pattern in query_lower for pattern in medium_patterns):
            return 'medium'
        else:
            # Default to medium for blockchain-related service
            return 'medium'
    
    def route_request(self, query, user_tier='basic', context=None):
        """Route request to appropriate AI model with cost optimization"""
        complexity = self.analyze_complexity(query, context)
        timestamp = datetime.now().isoformat()
        
        try:
            if complexity == 'simple':
                # Use free models (Qwen2.5)
                response = self.call_qwen_model(query)
                cost = 0.0
                model_used = 'qwen2.5-free'
                self.cost_tracker['free_requests'] += 1
                # Calculate savings vs GPT-5 nano
                saved_cost = self.estimate_nano_cost(query, response)
                self.cost_tracker['daily_savings'] += saved_cost
                
            elif complexity == 'medium':
                # Use GPT-5 nano for blockchain/DAO queries
                response = self.call_gpt5_nano(query, context)
                cost = self.calculate_nano_cost(query, response)
                model_used = 'gpt-5-nano'
                self.cost_tracker['nano_requests'] += 1
                
            else:  # complex
                # Use GPT-5 full only for premium users or critical analysis
                if user_tier in ['premium', 'enterprise']:
                    response = self.call_gpt5_full(query, context)
                    cost = self.calculate_full_cost(query, response)
                    model_used = 'gpt-5-full'
                    self.cost_tracker['full_requests'] += 1
                else:
                    # Fallback to nano for non-premium users
                    response = self.call_gpt5_nano(query + " (simplified analysis)", context)
                    cost = self.calculate_nano_cost(query, response)
                    model_used = 'gpt-5-nano-fallback'
                    self.cost_tracker['nano_requests'] += 1
            
            # Log the request
            self.request_log.append({
                'timestamp': timestamp,
                'query_preview': query[:50] + '...' if len(query) > 50 else query,
                'complexity': complexity,
                'model_used': model_used,
                'cost': cost,
                'user_tier': user_tier
            })
            
            self.cost_tracker['total_cost'] += cost
            
            return {
                'response': response,
                'model_used': model_used,
                'cost': round(cost, 4),
                'complexity': complexity,
                'savings': round(self.cost_tracker['daily_savings'], 4)
            }
            
        except Exception as e:
            # Always fallback to free model on any error
            try:
                response = self.call_qwen_model(f"Error occurred, providing basic response for: {query}")
                return {
                    'response': response,
                    'model_used': 'qwen2.5-fallback',
                    'cost': 0.0,
                    'complexity': 'fallback',
                    'error': str(e)
                }
            except:
                return {
                    'response': f"I apologize, but I'm experiencing technical difficulties. For the query '{query[:50]}...', please try again later or contact support.",
                    'model_used': 'static-fallback',
                    'cost': 0.0,
                    'complexity': 'error',
                    'error': str(e)
                }
    
    def call_qwen_model(self, query):
        """Call Qwen2.5 free model"""
        # This would integrate with Alibaba's Qwen API
        # For now, return a smart placeholder that indicates free model usage
        return f"[Qwen2.5 Free Response] {query} - This response cost you $0.00! Free AI model handling your request efficiently."
    
    def call_gpt5_nano(self, query, context=None):
        """Call GPT-5 nano ($0.05 input / $0.40 output)"""
        if not OPENAI_API_KEY:
            return self.call_qwen_model(query)
        
        # OpenAI API call would go here
        # Placeholder for now
        return f"[GPT-5 Nano] Analyzing blockchain query: {query} - Cost-optimized response for XMRT ecosystem."
    
    def call_gpt5_full(self, query, context=None):
        """Call GPT-5 full ($1.25 input / $10.00 output)"""
        if not OPENAI_API_KEY:
            return self.call_gpt5_nano(query, context)
        
        # OpenAI API call would go here
        # Placeholder for now
        return f"[GPT-5 Full] Deep analysis: {query} - Premium AI response with advanced reasoning."
    
    def calculate_nano_cost(self, query, response):
        """Calculate cost for GPT-5 nano"""
        input_tokens = len(query.split()) * 1.3  # Rough token estimate
        output_tokens = len(response.split()) * 1.3
        
        input_cost = (input_tokens / 1000) * 0.05
        output_cost = (output_tokens / 1000) * 0.40
        
        return input_cost + output_cost
    
    def calculate_full_cost(self, query, response):
        """Calculate cost for GPT-5 full"""
        input_tokens = len(query.split()) * 1.3
        output_tokens = len(response.split()) * 1.3
        
        input_cost = (input_tokens / 1000) * 1.25
        output_cost = (output_tokens / 1000) * 10.00
        
        return input_cost + output_cost
    
    def estimate_nano_cost(self, query, response):
        """Estimate what this would have cost with nano (for savings calculation)"""
        return self.calculate_nano_cost(query, response)

# Initialize AI Router
ai_router = XMRTAIRouter()

# Your existing routes (unchanged)
@app.route('/')
def hello_world():
    return 'Hello, XMRT Ecosystem Python Service with AI Router!'

@app.route('/interact_contract', methods=['POST'])
def interact_contract():
    if not w3.is_connected():
        return jsonify({'error': 'Not connected to Ethereum network'}), 500

    data = request.get_json()
    function_name = data.get('function_name')
    args = data.get('args', [])

    try:
        contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)
        # Example: Call a read-only function
        if function_name == 'getName':
            result = contract.functions.getName().call()
            return jsonify({'result': result})
        # Example: Send a transaction (requires private key and gas handling)
        elif function_name == 'setValue':
            # This is a simplified example. Real transactions need nonce, gas, etc.
            account = w3.eth.account.from_key(PRIVATE_KEY)
            tx = contract.functions.setValue(args[0]).build_transaction({
                'from': account.address,
                'nonce': w3.eth.get_transaction_count(account.address),
                'gas': 2000000, # Estimate gas or set appropriately
                'gasPrice': w3.to_wei('50', 'gwei')
            })
            signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            return jsonify({'tx_hash': tx_hash.hex()})
        else:
            return jsonify({'error': 'Function not supported'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# New AI Routes
@app.route('/ai/chat', methods=['POST'])
def ai_chat():
    """Main AI chat endpoint with intelligent cost-optimized routing"""
    data = request.get_json()
    
    if not data or 'query' not in data:
        return jsonify({'error': 'Missing query parameter'}), 400
    
    query = data.get('query')
    user_tier = data.get('user_tier', 'basic')
    context = data.get('context', None)
    
    # Add blockchain context for better routing
    if context is None and any(word in query.lower() for word in ['contract', 'transaction', 'blockchain']):
        context = {'service': 'xmrt-blockchain', 'network': 'ethereum'}
    
    result = ai_router.route_request(query, user_tier, context)
    
    return jsonify(result)

@app.route('/ai/analyze-contract', methods=['POST'])
def ai_analyze_contract():
    """AI-powered smart contract analysis"""
    data = request.get_json()
    
    if not data or 'contract_address' not in data:
        return jsonify({'error': 'Missing contract_address parameter'}), 400
    
    contract_address = data.get('contract_address')
    analysis_type = data.get('analysis_type', 'basic')
    user_tier = data.get('user_tier', 'basic')
    
    # Create analysis query
    query = f"Analyze smart contract at {contract_address} for {analysis_type} analysis"
    context = {
        'service': 'contract-analysis',
        'contract_address': contract_address,
        'analysis_type': analysis_type
    }
    
    result = ai_router.route_request(query, user_tier, context)
    
    return jsonify(result)

@app.route('/ai/stats', methods=['GET'])
def ai_stats():
    """Get AI usage statistics and cost tracking"""
    return jsonify({
        'cost_tracker': ai_router.cost_tracker,
        'recent_requests': ai_router.request_log[-5:],  # Last 5 requests
        'total_requests': len(ai_router.request_log),
        'cost_optimization': {
            'percentage_free': round((ai_router.cost_tracker['free_requests'] / max(len(ai_router.request_log), 1)) * 100, 2),
            'estimated_monthly_savings': round(ai_router.cost_tracker['daily_savings'] * 30, 2),
            'average_cost_per_request': round(ai_router.cost_tracker['total_cost'] / max(len(ai_router.request_log), 1), 4)
        }
    })

@app.route('/ai/health', methods=['GET'])
def ai_health():
    """Health check for AI routing system"""
    return jsonify({
        'ai_router_status': 'healthy',
        'models_available': {
            'qwen2.5': 'available' if QWEN_API_KEY else 'configured',
            'gpt5_nano': 'available' if OPENAI_API_KEY else 'needs_api_key',
            'gpt5_full': 'available' if OPENAI_API_KEY else 'needs_api_key'
        },
        'cost_optimization': 'active',
        'fallback_system': 'enabled'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=os.getenv('PORT', 5000))
