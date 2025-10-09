# 🚀 Getting Started with XMRT-Ecosystem

## 📋 Prerequisites

Before you begin, ensure you have the following installed:
- **Python 3.8+** (Python 3.11+ recommended)
- **Git** for version control
- **GitHub Personal Access Token** with appropriate permissions

## ⚡ Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/DevGruGold/XMRT-Ecosystem.git
cd XMRT-Ecosystem
```

### 2. Set Up Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables
```bash
# Create .env file
cp .env.example .env

# Edit .env with your credentials:
# GITHUB_TOKEN=your_github_token_here
# GITHUB_OWNER=your_github_username
# OPENAI_API_KEY=your_openai_key_here (optional)
# GEMINI_API_KEY=your_gemini_key_here (optional)
```

### 4. Run the Application
```bash
# Development mode
python main.py

# Production mode (recommended)
gunicorn --bind 0.0.0.0:10000 main:app
```

### 5. Access the Dashboard
Open your browser and navigate to:
- **Local**: http://localhost:10000
- **Health Check**: http://localhost:10000/health
- **Enhanced Dashboard**: http://localhost:10000/enhanced

## 🔑 GitHub Token Setup

### Required Permissions
Your GitHub Personal Access Token needs these scopes:
- ✅ `repo` - Full repository access
- ✅ `read:org` - Read organization membership
- ✅ `admin:repo_hook` - Repository webhook management (optional)
- ✅ `workflow` - GitHub Actions workflow management (optional)

### Creating a Token
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Click "Generate new token (classic)"
3. Select the required scopes above
4. Copy the token and add it to your `.env` file

## 🤖 AI Configuration

The system supports multiple AI providers:

### OpenAI (Recommended)
```bash
OPENAI_API_KEY=sk-your-openai-key
OPENAI_MODEL=gpt-4o-mini  # or gpt-4
```

### Google Gemini (Alternative)
```bash
GEMINI_API_KEY=your-gemini-key
GEMINI_MODEL=gemini-pro
```

*Note: At least one AI provider is required for the system to function.*

## 🚀 Production Deployment

### Render.com (Current Deployment)
The system is already configured for Render deployment:

1. **Fork this repository**
2. **Connect to Render**: Create new Web Service
3. **Configuration**:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn --bind 0.0.0.0:$PORT main:app`
4. **Environment Variables**:
   ```
   GITHUB_TOKEN=your_token
   GITHUB_OWNER=your_username
   OPENAI_API_KEY=your_key (optional)
   LOG_LEVEL=INFO
   ```

### Docker (Alternative)
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 10000
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "main:app"]
```

## 📊 System Overview

### Core Components
- **Flask Web Server**: REST API and web dashboard
- **AI Agents**: 4 specialized agents for consensus-based decisions
- **GitHub Integration**: Repository management and automation
- **Health Monitoring**: System metrics and status checks

### AI Agents
1. **Eliza** (Coordinator) - Weight: 1.2
2. **Security Guardian** - Weight: 1.1  
3. **DeFi Specialist** - Weight: 1.05
4. **Community Manager** - Weight: 1.0

### Key Endpoints
- `GET /` - Main dashboard
- `GET /health` - Health check
- `GET /agents` - Agent information
- `POST /api/run-innovation-cycle` - Trigger innovation cycle
- `POST /webhook/github` - GitHub webhook handler

## 🔧 Configuration

### Using the New Configuration System
```python
from config.settings import get_config

# Get configuration
config = get_config()

# Validate configuration
errors = config.validate()
if errors:
    print("Configuration errors:", errors)

# Access configuration values
print(f"GitHub Owner: {config.github.owner}")
print(f"AI Model: {config.ai.openai_model}")
print(f"Server Port: {config.server.port}")
```

### Health Monitoring
```python
from app.health import health_monitor

# Get system metrics
metrics = health_monitor.get_system_metrics()
print(f"CPU: {metrics['cpu']}%")
print(f"Memory: {metrics['memory']}%")
print(f"Disk: {metrics['disk']}%")

# Get uptime
uptime = health_monitor.get_uptime()
print(f"Uptime: {uptime} seconds")
```

## 🧪 Testing

### Running Tests (When Implemented)
```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test category
pytest -k "test_agents"
```

## 🔍 Monitoring & Debugging

### Logs
```bash
# View application logs
tail -f logs/xmrt-ecosystem.log

# View error logs
tail -f logs/xmrt-ecosystem-errors.log
```

### Health Checks
```bash
# Basic health check
curl http://localhost:10000/health

# Detailed health check
curl http://localhost:10000/health/detailed

# Metrics (Prometheus format)
curl http://localhost:10000/health/metrics
```

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python main.py
```

## 🆘 Troubleshooting

### Common Issues

#### 1. GitHub Authentication Error
**Problem**: `Argument login_or_token is deprecated`
**Solution**: Update to use `Auth.Token()` method (already fixed in current version)

#### 2. AI API Not Working
**Problem**: No AI responses or errors
**Solution**: 
- Check API keys in `.env` file
- Verify API key permissions
- Check API usage limits

#### 3. Port Already in Use
**Problem**: `Address already in use`
**Solution**:
```bash
# Find process using port 10000
lsof -i :10000

# Kill the process
kill -9 <process_id>

# Or use a different port
export PORT=10001
python main.py
```

#### 4. Module Import Errors
**Problem**: `ModuleNotFoundError`
**Solution**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Getting Help
- 📂 **Issues**: [GitHub Issues](https://github.com/DevGruGold/XMRT-Ecosystem/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/DevGruGold/XMRT-Ecosystem/discussions)
- 🌐 **Live System**: [https://xmrt-ecosystem-iofw.onrender.com/](https://xmrt-ecosystem-iofw.onrender.com/)

## 🚀 Next Steps

1. **Explore the Dashboard**: Navigate to the web interface
2. **Run an Innovation Cycle**: Test the AI agent system
3. **Check the Logs**: Monitor system behavior
4. **Customize Agents**: Modify agent weights and behaviors
5. **Contribute**: See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines

---

*Happy coding! 🚀*