# XMRT-Ecosystem DAO Prototype

A full-stack decentralized autonomous organization (DAO) prototype integrating Eliza AI agent framework for intelligent governance and treasury management.

## Overview

The XMRT-Ecosystem DAO represents the next evolution in decentralized governance, combining human decision-making with AI-powered intelligence. Built around the XMRT token smart contract on Sepolia testnet, this prototype demonstrates how AI agents can enhance DAO operations while maintaining decentralized control.

## Key Features

- **Eliza AI Integration**: Sophisticated AI agent framework for natural language proposal processing and predictive analytics
- **Smart Contract Interaction**: Direct integration with XMRT token contract for staking, unstaking, and governance operations
- **Multi-Agent Architecture**: Three AI agents with dedicated wallets for different operational roles
- **Cross-Platform Support**: Unified experience across web, Discord, Telegram, and Twitter
- **Treasury Management**: AI-driven yield optimization and automated rebalancing
- **Regulatory Compliance**: Transparent governance through public social media integration

## Architecture

### Frontend (React)
- User dashboard and governance portal
- Eliza chat interface for natural language interactions
- Wallet integration (MetaMask, WalletConnect)
- Real-time data visualization

### Backend (Flask)
- Eliza AI agent framework
- Blockchain interaction services
- API endpoints for frontend communication
- Database for off-chain data storage

### Smart Contracts
- XMRT ERC20 token with staking mechanisms
- Upgradeable architecture for future enhancements
- Role-based access control for AI agents

## Smart Contract Details

**Contract Address (Sepolia)**: `0x77307DFbc436224d5e6f2048d2b6bDfA66998a15`

**Key Features**:
- Total Supply: 21,000,000 XMRT
- Staking with 7-day minimum period
- 10% early unstaking penalty (burned)
- Upgradeable via UUPS proxy pattern
- Role-based access control

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.8+
- MetaMask or compatible Web3 wallet
- Sepolia testnet ETH

### Installation

1. Clone the repository:
```bash
git clone https://github.com/DevGruGold/XMRT-Ecosystem.git
cd XMRT-Ecosystem
```

2. Install frontend dependencies:
```bash
cd frontend/xmrt-dao-frontend
pnpm install
```

3. Install backend dependencies:
```bash
cd ../../backend/xmrt-dao-backend
source venv/bin/activate
pip install -r requirements.txt
```

### Running the Application

1. Start the backend:
```bash
cd backend/xmrt-dao-backend
source venv/bin/activate
python src/main.py
```

2. Start the frontend:
```bash
cd frontend/xmrt-dao-frontend
pnpm run dev --host
```

3. Access the application at `http://localhost:5173`

## AI Agent Configuration

The system includes three AI agents with specific roles:

1. **Governance Agent**: Processes proposals and manages voting
2. **Treasury Agent**: Handles financial operations and yield optimization
3. **Community Agent**: Manages cross-platform communication and support

Each agent has its own wallet configured with appropriate permissions on the XMRT smart contract.

## Contributing

This is a prototype implementation. Contributions are welcome through:

1. Fork the repository
2. Create a feature branch
3. Submit a pull request with detailed description

## Security Considerations

- This is a testnet prototype - do not use with real funds
- Smart contract has not been audited
- AI agent wallets use test keys only
- All transactions occur on Sepolia testnet

## License

MIT License - see LICENSE file for details

## Links

- **Website**: [XMRT.io](https://xmrt.io)
- **Discord**: [XMRT DAO Community](https://discord.gg/xmrtdao)
- **Twitter**: [@xmrtdao](https://twitter.com/xmrtdao)
- **Medium**: [josephandrewlee.medium.com](https://josephandrewlee.medium.com)

## Roadmap

- [ ] Phase 1: Basic Eliza integration and governance support
- [ ] Phase 2: Advanced treasury management and cross-platform integration
- [ ] Phase 3: Cross-DAO coordination and advanced security protocols
- [ ] Phase 4: Mainnet preparation and security audits

