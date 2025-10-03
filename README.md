# XMRT Ecosystem - Multi-Agent Repository Management System

🚀 **Production Deployment**: [https://xmrt-ecosystem-iofw.onrender.com/](https://xmrt-ecosystem-iofw.onrender.com/)

## Overview

The XMRT Ecosystem is a sophisticated, production-ready Flask service that orchestrates a consensus-driven agent team to manage and integrate repositories across the XMRT ecosystem. It features real-time coordination, autonomous decision-making, and comprehensive repository management capabilities.

## 🌟 Key Features

### Core Capabilities
- **Multi-Agent Coordination**: Role-based agents that auto-assign tasks by category and stage
- **Consensus Engine**: Decisions are recorded with rationale and can be reviewed via API
- **Real-time Repository Management**: Safe GitHub operations with automatic synchronization
- **Production-Ready Architecture**: Built for scale with SQLite persistence and thread-safe operations
- **Comprehensive API**: RESTful endpoints for all system components
- **Autonomous Learning**: Self-improving agents that adapt based on task outcomes

### Agent System
- **Repository Specialists**: Handle code integration, documentation, and maintenance
- **Security Agents**: Manage SECURITY.md, CODEOWNERS, and vulnerability assessments
- **Integration Coordinators**: Oversee cross-repository dependencies and workflows
- **Quality Assurance**: Automated testing, code review, and compliance checking

### GitHub Integration
- **Safe Operations**: Idempotent GitHub operations (labels, issues, PRs)
- **Branch Management**: Automatic branch detection and management
- **File Synchronization**: Automated XMRT standard files (.xmrt/integration.yml, SECURITY.md, CODEOWNERS, CONTRIBUTING.md)
- **Webhook Support**: Real-time repository event processing

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
   git clone https://github.com/DevGruGold/xmrt-ecosystem.git
   cd xmrt-ecosystem
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
- `GET /` - Service information and health check
- `GET /health` - Simple health check
- `GET /api/status` - Detailed system status
- `GET /api/coordination/status` - Enhanced coordination metrics

### Data Management
- `GET /api/agents` - List all agents and their status
- `GET /api/repos` - List all managed repositories
- `GET /api/tasks?status=PENDING&limit=50` - List tasks with filtering
- `GET /api/decisions` - Get latest consensus decisions

### Operations
- `POST /api/tick` - Manual trigger for coordinator cycle

### Example API Response

```json
{
  "service": "xmrt-main",
  "status": "running",
  "coordination_health": "healthy",
  "system_metrics": {
    "total_agents": 12,
    "total_repos": 72,
    "pending_tasks": 8,
    "blocked_tasks": 2
  },
  "last_activity": "2025-10-03T12:00:00Z"
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

## 🧠 Agent System

### Agent Types

1. **Integration Specialist**
   - Handles repository merging and conflict resolution
   - Manages cross-repository dependencies
   - Coordinates with other agents for complex integrations

2. **Security Guardian**
   - Maintains security policies and documentation
   - Monitors for vulnerabilities and compliance issues
   - Updates SECURITY.md and CODEOWNERS files

3. **Documentation Curator**
   - Ensures comprehensive documentation
   - Maintains README files and API documentation
   - Coordinates documentation standards across repositories

4. **Quality Assurance Agent**
   - Runs automated tests and code quality checks
   - Manages CI/CD pipeline coordination
   - Ensures code standards compliance

### Agent Lifecycle

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   CREATED   │───▶│   ACTIVE    │───▶│  WORKING    │───▶│  COMPLETED  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       │                  │                  │                  │
       └──────────────────┼──────────────────┼──────────────────┤
                          ▼                  ▼                  ▼
                    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
                    │   BLOCKED   │    │    ERROR    │    │    IDLE     │
                    └─────────────┘    └─────────────┘    └─────────────┘
```

## 📈 Monitoring & Observability

### Logging
The application provides structured logging with different levels:
- **INFO**: General operation information
- **WARNING**: Non-critical issues that should be monitored
- **ERROR**: Critical errors that need immediate attention
- **DEBUG**: Detailed debugging information (development only)

### Health Checks
- **Basic Health**: `/health` - Returns 200 if service is running
- **Detailed Status**: `/api/status` - Comprehensive system metrics
- **Coordination Health**: `/api/coordination/status` - Agent and task metrics

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

1. **SQLite Syntax Error**
   - **Symptom**: `near "exists": syntax error`
   - **Solution**: Database schema has been updated to use `repo_exists` instead of reserved keyword

2. **GitHub Authentication Error**
   - **Symptom**: `Argument login_or_token is deprecated`
   - **Solution**: Updated to use `Auth.Token()` method from PyGithub

3. **404 Errors on Routes**
   - **Symptom**: Missing `/api/coordination/status` endpoint
   - **Solution**: Added comprehensive route handlers for all expected endpoints

4. **Production Server Issues**
   - **Symptom**: Flask development server warnings
   - **Solution**: Configured for gunicorn production deployment

### Debug Mode
Enable debug logging by setting `LOG_LEVEL=DEBUG` in your environment:

```bash
export LOG_LEVEL=DEBUG
python main.py
```

## 📜 License

This project is licensed under the Apache License 2.0 - see individual repository LICENSE files for details.

## 🤝 Support

- **Issues**: [GitHub Issues](https://github.com/DevGruGold/xmrt-ecosystem/issues)
- **Discussions**: [GitHub Discussions](https://github.com/DevGruGold/xmrt-ecosystem/discussions)
- **Documentation**: [Wiki](https://github.com/DevGruGold/xmrt-ecosystem/wiki)

## 🎯 Roadmap

- [ ] **WebSocket Support**: Real-time updates for dashboard
- [ ] **Advanced Analytics**: Machine learning insights for agent performance
- [ ] **Multi-Organization Support**: Manage multiple GitHub organizations
- [ ] **Custom Agent Development**: Plugin system for custom agent types
- [ ] **Integration with CI/CD**: Native GitHub Actions integration
- [ ] **Advanced Security**: OAuth2 and RBAC implementation

---

**Built with ❤️ by the XMRT Team**

*Autonomous Repository Management for the Modern Era*