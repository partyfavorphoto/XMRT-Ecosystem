# XMRT-Ecosystem: Unified DAO Platform

## Overview

The XMRT-Ecosystem has been transformed into a unified, streamlined platform that consolidates all DAO functionalities into a single, cohesive application. This new architecture eliminates redundancy and provides users with an intuitive MobileMonero-based CashDapp interface, enhanced by AI-powered automation through Eliza.

## 🚀 Key Features

- **Unified CashDapp Frontend**: Single, responsive interface consolidating all DAO operations
- **AI-Enabled Eliza**: Integrated AI assistant for automated DAO operations and insights
- **Streamlined Backend**: Optimized microservices architecture with centralized API gateway
- **Cross-Chain Support**: Seamless multi-blockchain operations
- **Zero-Knowledge Privacy**: Enhanced privacy features through ZK proofs
- **Real-Time Governance**: Live proposal tracking and voting
- **Treasury Management**: AI-powered treasury optimization and monitoring

## 🏗️ Architecture

### Frontend (Unified CashDapp)
- **Location**: `frontend/xmrt-unified-cashdapp/`
- **Technology**: React + Vite, Tailwind CSS, shadcn/ui
- **Features**: 
  - Dashboard with balance, trading, and governance overview
  - Integrated Eliza AI chat interface
  - Quick access to Wallet, Trading, Governance, and Mining
  - Responsive design optimized for all devices

### Backend Services
- **API Gateway**: `backend/xmrt-unified-backend/` - Centralized API routing and authentication
- **AI Automation**: `backend/ai-automation-service/` - Eliza AI for DAO automation
- **DAO Core**: `backend/xmrt-dao-backend/` - Main DAO logic and operations
- **Cross-Chain**: `backend/cross-chain-service/` - Multi-blockchain support
- **ZK Service**: `backend/zk-service/` - Zero-knowledge proof functionality

### Smart Contracts
- **Location**: `contracts/`
- **Features**: Core DAO governance, token management, and dApp-specific logic

## 🛠️ Development Setup

### Prerequisites
- Node.js 18+ and pnpm
- Python 3.11+ and pip
- Git

### Frontend Development
```bash
cd frontend/xmrt-unified-cashdapp
pnpm install
pnpm run dev --host
```

### Backend Development
```bash
cd backend/xmrt-unified-backend
source venv/bin/activate
pip install -r requirements.txt
python src/main.py
```

### AI Automation Service
```bash
cd backend/ai-automation-service
pip install -r requirements.txt
python main.py
```

## 📱 User Interface

The unified CashDapp provides:

1. **Dashboard Overview**: Real-time balance, trading volume, and active proposals
2. **Eliza AI Chat**: Direct interaction with the AI assistant for DAO operations
3. **Quick Actions**: One-click access to core functionalities
4. **Responsive Design**: Optimized for desktop and mobile devices

## 🤖 Eliza AI Integration

Eliza provides intelligent automation for:
- **Governance**: Proposal analysis and voting recommendations
- **Treasury**: Portfolio optimization and risk management
- **Community**: Engagement monitoring and report generation
- **Operations**: Automated task execution and system monitoring

## 🔧 Configuration

### Environment Variables
Create `.env` files in respective service directories:

```bash
# AI Automation Service
OPENAI_API_KEY=your_openai_key
BLOCKCHAIN_RPC_URL=your_rpc_url
PRIVATE_KEY=your_private_key

# Backend Services
DATABASE_URL=your_database_url
JWT_SECRET=your_jwt_secret
```

## 🚀 Deployment

### Development
```bash
# Start all services
docker-compose up -d
```

### Production
```bash
# Build and deploy
docker-compose -f docker-compose.prod.yml up -d
```

## 📊 Monitoring

- **Health Checks**: `/health` endpoints on all services
- **Metrics**: Prometheus integration for performance monitoring
- **Logs**: Structured logging with correlation IDs

## 🔐 Security

- **Authentication**: JWT-based user authentication
- **Authorization**: Role-based access control
- **Privacy**: Zero-knowledge proofs for sensitive operations
- **Auditing**: Comprehensive audit trails for all operations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/DevGruGold/XMRT-Ecosystem/issues)
- **Community**: [Discord](https://discord.gg/xmrt-dao)

## 🗺️ Roadmap

- [ ] Mobile app development
- [ ] Advanced AI features
- [ ] Multi-chain expansion
- [ ] DeFi integrations
- [ ] NFT marketplace

---

**Built with ❤️ by the XMRT DAO Community**



## 🛡️ Most Recent Automated Audit
- Audit performed by automated script in Google Colab
- Date: **2025-07-24 17:11 UTC**
- Author: DevGruGold (joeyleepcs@gmail.com)
- Status: ✅ No critical issues detected, contracts compile successfully.


## 🛠️ CI Workflow Fix
- 2025-07-24 17:21 UTC
- Removed explicit 'version:' field from pnpm/action-setup to resolve version mismatch in GitHub Actions. Now uses only the version specified in package.json.