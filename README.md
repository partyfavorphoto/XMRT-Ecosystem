# XMRT Ecosystem - Multi-Agent Repository Management System

🚀 **Production Deployment**: [https://xmrt-ecosystem-iofw.onrender.com/](https://xmrt-ecosystem-iofw.onrender.com/)

## Overview

The **XMRT Ecosystem** represents a sophisticated, production-ready Flask service that orchestrates a consensus-driven agent team to manage and integrate repositories across the XMRT ecosystem. The system features real-time coordination, autonomous decision-making, and comprehensive repository management capabilities powered by four specialized AI agents working in concert.

**Current Version**: 6.3.0-hardy-github  
**Status**: ✅ Active and Operational  
**Deployment Platform**: Render.com

## 🤖 Active Agents

The XMRT Ecosystem is powered by four specialized autonomous agents, each with distinct roles and capabilities:

### 1. Eliza - Coordinator & Governor
**Role**: Strategic Coordinator and System Governor  
**Voice**: Strategic, synthesizes viewpoints  
**Decision Weight**: 1.2  
**Responsibilities**:
- Orchestrates multi-agent coordination and consensus building
- Synthesizes diverse agent perspectives into unified strategies
- Governs system-wide decisions and policy implementation
- Maintains strategic oversight of ecosystem development
- Facilitates communication between agents and stakeholders

### 2. Security Guardian
**Role**: Security & Privacy Specialist  
**Voice**: Threat-models, privacy-first  
**Decision Weight**: 1.1  
**Responsibilities**:
- Conducts threat modeling and vulnerability assessments
- Maintains SECURITY.md and security documentation
- Manages CODEOWNERS and access control policies
- Monitors dependencies for security vulnerabilities
- Ensures privacy-first approach in all implementations

### 3. DeFi Specialist
**Role**: Mining & Tokenomics Expert  
**Voice**: ROI, efficiency, yield  
**Decision Weight**: 1.05  
**Responsibilities**:
- Optimizes mining operations and resource allocation
- Analyzes tokenomics and economic models
- Focuses on ROI and operational efficiency
- Manages yield optimization strategies
- Tracks miner contributions and rewards

### 4. Community Manager
**Role**: Adoption & User Experience  
**Voice**: Onboarding, documentation, growth  
**Decision Weight**: 1.0  
**Responsibilities**:
- Manages community engagement and growth initiatives
- Maintains comprehensive documentation and guides
- Improves onboarding experiences for new users
- Coordinates user feedback and feature requests
- Builds bridges between technical teams and community

## 📊 Current System Stats

Based on the latest operational data from the deployed system:

- **Repositories Discovered**: 1
- **Ideas Generated**: 14
- **Issues Created**: 4
- **Story Issues**: 2
- **Files Managed**: 8
- **Innovation Cycles Completed**: 2
- **System Uptime**: Continuous operation on Render
- **Resource Utilization**: CPU ~40-80%, Memory ~55%, Disk ~82-84%

## 🌟 Key Features

### Core Capabilities
The XMRT Ecosystem provides a comprehensive suite of capabilities designed for autonomous repository management and agent coordination. The system employs **role-based agents** that automatically assign tasks by category and stage, ensuring efficient workflow distribution. A sophisticated **consensus engine** records all decisions with detailed rationale, making them reviewable via API endpoints. The platform offers **real-time repository management** with safe GitHub operations and automatic synchronization across the ecosystem.

Built on a **production-ready architecture** designed for scale, the system utilizes SQLite persistence with WAL mode for thread-safe operations. A **comprehensive RESTful API** provides access to all system components, while **autonomous learning** capabilities enable agents to self-improve and adapt based on task outcomes and performance metrics.

### Agent System Architecture
The multi-agent system operates through weighted consensus, where each agent's input is valued according to their expertise and decision weight. Agents collaborate on complex tasks, with **Eliza** serving as the primary coordinator who synthesizes viewpoints and ensures strategic alignment. The **Security Guardian** provides critical security oversight, while the **DeFi Specialist** optimizes economic aspects, and the **Community Manager** ensures user-centric development.

Agents can autonomously create GitHub issues, generate ideas, manage files, and run innovation cycles. The system tracks agent performance and adjusts coordination strategies based on outcomes, creating a continuously improving autonomous ecosystem.

### GitHub Integration
The platform provides **safe, idempotent GitHub operations** for labels, issues, and pull requests, with automatic branch detection and management. File synchronization ensures that XMRT standard files (`.xmrt/integration.yml`, `SECURITY.md`, `CODEOWNERS`, `CONTRIBUTING.md`) remain consistent across repositories. **Webhook support** enables real-time repository event processing, allowing agents to respond immediately to changes.

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Flask API     │    │   Coordinator    │    │  GitHub API     │
│   - REST Routes │◄──►│   - Agent Mgmt   │◄──►│  - Repo Sync    │
│   - WebSockets  │    │   - Task Queue   │    │  - File Mgmt    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   SQLite DB     │    │   Agent Network  │    │  OpenAI API     │
│   - Persistence │    │   - Multi-Agent  │    │  - Rationale    │
│   - Audit Trail │    │   - Consensus    │    │  - Generation   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Git
- GitHub Personal Access Token

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/DevGruGold/XMRT-Ecosystem.git
   cd XMRT-Ecosystem
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials:
   # GITHUB_TOKEN=your_github_token_here
   # GITHUB_ORG=DevGruGold
   # OPENAI_API_KEY=your_openai_key_here (optional)
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

   The service will start on `http://localhost:10000`

### Production Deployment (Render)

The application is already configured for Render deployment:

1. **Fork this repository**
2. **Connect to Render**:
   - Create new Web Service
   - Connect your GitHub repository
   - Use the following settings:
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT main:app`

3. **Set Environment Variables** in Render dashboard:
   ```
   GITHUB_TOKEN=your_github_token_here
   GITHUB_ORG=your_github_org
   OPENAI_API_KEY=your_openai_key (optional)
   LOG_LEVEL=INFO
   ```

4. **Deploy**: Render will automatically build and deploy your application

## 📊 API Endpoints

### System Status
- `GET /` - Service information and health check with agent status
- `GET /health` - System health check with resource metrics
- `GET /agents` - List all agents with roles and weights

### Operations
- `POST /api/tick` - Manual trigger for coordinator cycle
- `POST /run-cycle` - Execute innovation cycle

### Example API Responses

**Health Check (`/health`)**:
```json
{
  "ok": true,
  "owner": "DevGruGold",
  "ready": true,
  "repo": "XMRT-Ecosystem",
  "system": {
    "cpu": 46.8,
    "disk": 83.6,
    "mem": 54.9
  },
  "timestamp": "2025-10-06T15:23:41.037280",
  "uptime": 397.53,
  "version": "6.3.0-hardy-github"
}
```

**Agent Information (`/agents`)**:
```json
{
  "agents": {
    "eliza": {
      "name": "Eliza",
      "role": "Coordinator & Governor",
      "voice": "strategic, synthesizes viewpoints",
      "weight": 1.2
    },
    "security_guardian": {
      "name": "Security Guardian",
      "role": "Security & Privacy",
      "voice": "threat-models, privacy-first",
      "weight": 1.1
    },
    "defi_specialist": {
      "name": "DeFi Specialist",
      "role": "Mining & Tokenomics",
      "voice": "ROI, efficiency, yield",
      "weight": 1.05
    },
    "community_manager": {
      "name": "Community Manager",
      "role": "Adoption & UX",
      "voice": "onboarding, docs, growth",
      "weight": 1.0
    }
  }
}
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `PORT` | Server port | `10000` | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |
| `DATA_DIR` | Data directory path | `./data` | No |
| `DATABASE_URL` | SQLite database path | `{DATA_DIR}/xmrt.db` | No |
| `GITHUB_TOKEN` | GitHub PAT with repo scope | - | Yes |
| `GITHUB_ORG` | GitHub organization name | - | Yes |
| `OPENAI_API_KEY` | OpenAI API key for rationale generation | - | No |
| `OPENAI_MODEL` | OpenAI model to use | `gpt-4o-mini` | No |

### GitHub Token Permissions

Your GitHub Personal Access Token needs the following scopes:
- `repo` - Full repository access
- `read:org` - Read organization membership
- `admin:repo_hook` - Repository webhook management (if using webhooks)
- `workflow` - GitHub Actions workflow management

## 🔄 Recent Updates & Improvements

### October 2025 - System Enhancements

**GitHub Actions Workflows Fixed** ✅
- Updated deprecated action versions across all workflows
- Fixed `actions/upload-artifact@v3` → `v4`
- Fixed `actions/download-artifact@v3` → `v4`
- Updated `actions/checkout@v3` → `v4`
- Updated `actions/setup-python@v4` → `v5`
- Updated `actions/cache@v3` → `v4`

**Affected Workflows**:
- ✅ Activity-Summary-and-Agent-Discussion.yml
- ✅ Automated Documentation.yml
- ✅ Security-Scan-with-Dependabot.yml
- ✅ miner-tracking.yml (⛏️ XMRT Miner Contribution Tracker)
- ✅ test.yml

**Agent System Operational**:
- All four agents (Eliza, Security Guardian, DeFi Specialist, Community Manager) are active
- Consensus-based decision making is operational
- Innovation cycles running successfully
- GitHub integration fully functional

## 📈 Monitoring & Observability

### Logging
The application provides structured logging with different levels:
- **INFO**: General operation information
- **WARNING**: Non-critical issues that should be monitored
- **ERROR**: Critical errors that need immediate attention
- **DEBUG**: Detailed debugging information (development only)

### Health Checks
- **Basic Health**: `/health` - Returns system status with resource metrics
- **Agent Status**: `/agents` - Comprehensive agent information
- **System Metrics**: Real-time CPU, memory, and disk utilization

### Database
- **SQLite with WAL mode**: Ensures data consistency and performance
- **Thread-safe operations**: Concurrent access handling
- **Automatic migrations**: Schema updates are handled automatically

## 🔄 Development Workflow

### Code Quality
- **Type Hints**: Full type annotation support
- **Linting**: Code follows PEP 8 standards
- **Testing**: Comprehensive test suite (run with `pytest`)
- **Documentation**: Inline documentation and API specs

### Contributing
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=main

# Run specific test category
pytest -k "test_database"
```

## 🚨 Troubleshooting

### Common Issues

1. **GitHub Actions Workflow Failures**
   - **Symptom**: Deprecated action version errors
   - **Solution**: ✅ Fixed - All workflows updated to latest action versions

2. **GitHub Authentication Error**
   - **Symptom**: `Argument login_or_token is deprecated`
   - **Solution**: Updated to use `Auth.Token()` method from PyGithub

3. **Agent Communication Issues**
   - **Symptom**: Agents not responding or coordinating
   - **Solution**: Check `/health` endpoint for system status and verify all environment variables are set

4. **Production Server Issues**
   - **Symptom**: Flask development server warnings
   - **Solution**: Configured for gunicorn production deployment on Render

### Debug Mode
Enable debug logging by setting `LOG_LEVEL=DEBUG` in your environment:

```bash
export LOG_LEVEL=DEBUG
python main.py
```

## 🎯 Roadmap

### In Progress
- ✅ **GitHub Actions Workflow Fixes**: Completed - All workflows updated
- 🔄 **Agent GitHub Personas**: Integrating agents as autonomous GitHub actors
- 🔄 **Enhanced Agent Autonomy**: Enabling agents to comment and act independently

### Planned Features
- [ ] **WebSocket Support**: Real-time updates for dashboard
- [ ] **Advanced Analytics**: Machine learning insights for agent performance
- [ ] **Multi-Organization Support**: Manage multiple GitHub organizations
- [ ] **Custom Agent Development**: Plugin system for custom agent types
- [ ] **Integration with CI/CD**: Native GitHub Actions integration
- [ ] **Advanced Security**: OAuth2 and RBAC implementation
- [ ] **Agent Discussion Forum**: Automated discussions in GitHub Discussions
- [ ] **Miner Leaderboard**: Automated tracking and recognition system

## 📜 License

This project is licensed under the Apache License 2.0 - see individual repository LICENSE files for details.

## 🤝 Support

- **Issues**: [GitHub Issues](https://github.com/DevGruGold/XMRT-Ecosystem/issues)
- **Discussions**: [GitHub Discussions](https://github.com/DevGruGold/XMRT-Ecosystem/discussions)
- **Live System**: [https://xmrt-ecosystem-iofw.onrender.com/](https://xmrt-ecosystem-iofw.onrender.com/)

## 🏆 Contributors & Agents

This project is maintained by both human developers and autonomous AI agents working in collaboration:

- **Human Team**: [@DevGruGold](https://github.com/DevGruGold)
- **AI Agents**: Eliza (Coordinator), Security Guardian, DeFi Specialist, Community Manager

---

**Built with ❤️ by the XMRT Team - Humans and AI Working Together**

*Autonomous Repository Management for the Modern Era*

**Last Updated**: October 6, 2025  
**System Status**: ✅ Operational  
**Active Agents**: 4/4
