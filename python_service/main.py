from flask import Flask, jsonify, request
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Configuration for connecting to the Ethereum network
INFURA_URL = os.getenv('INFURA_URL')
PRIVATE_KEY = os.getenv('PRIVATE_KEY')
CONTRACT_ADDRESS = os.getenv('CONTRACT_ADDRESS')
with open(os.path.join(os.path.dirname(__file__), 'abi.json'), 'r') as f:
    CONTRACT_ABI = f.read()

w3 = Web3(Web3.HTTPProvider(INFURA_URL))

# Basic route
@app.route('/')
def hello_world():
    return 'Hello, XMRT Ecosystem Python Service!'

# Example route for interacting with a smart contract
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=os.getenv('PORT', 5000))

