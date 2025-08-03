
from web3 import Web3

# Connect to Sepolia
RPC = 'https://sepolia.infura.io/v3/c843a693bc5d43d1aee471d2491f2414'
PRIVATE_KEY = 'c843a693bc5d43d1aee471d2491f2414'
ACCOUNT_ADDRESS = Web3().eth.account.from_key(PRIVATE_KEY).address

web3 = Web3(Web3.HTTPProvider(RPC))
if __name__ == "__main__":
    print('[web3] Connected:', web3.is_connected())

def get_balance():
    return web3.eth.get_balance(ACCOUNT_ADDRESS) / 1e18

def simulate_execute(data):
if __name__ == "__main__":
        print('[Simulated Tx] Would send:', data)
