# 🚀 XMRT Ecosystem Development Guide

## Quick Start for Developers

### Prerequisites
- Python 3.9+ (3.11 recommended)
- Git
- GitHub Personal Access Token with `repo` scope

### Development Setup

1. **Clone and setup**
   ```bash
   git clone https://github.com/DevGruGold/XMRT-Ecosystem.git
   cd XMRT-Ecosystem
   
   # Install development dependencies
   pip install -r requirements-dev.txt
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your GitHub token and other settings
   ```

3. **Set up pre-commit hooks**
   ```bash
   pre-commit install
   ```

4. **Run tests**
   ```bash
   pytest --cov=app
   ```

5. **Start development server**
   ```bash
   python main.py
   ```

## Code Quality Standards

### Automated Checks
- **Black** - Code formatting (line length: 127)
- **isort** - Import sorting
- **flake8** - Linting and style checks
- **mypy** - Type checking
- **bandit** - Security vulnerability scanning
- **pytest** - Testing with coverage >85%

### Manual Code Review
Before submitting a PR, ensure:
- [ ] All tests pass
- [ ] Code coverage maintained >85%
- [ ] Security scan passes
- [ ] Documentation updated
- [ ] Type hints added for new functions
- [ ] Error handling implemented

## Development Workflow

1. **Create feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Develop with quality checks**
   ```bash
   # Format code
   black .
   isort .
   
   # Run tests
   pytest --cov=app
   
   # Security check
   bandit -r .
   ```

3. **Commit changes** (pre-commit hooks will run automatically)
   ```bash
   git add .
   git commit -m "feat: your feature description"
   ```

4. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   # Create PR on GitHub
   ```

## Architecture Overview

### Current Structure (Single File)
```
main.py (2,800+ lines) - NEEDS REFACTORING
├── AI Processing
├── GitHub Integration  
├── Agent System
├── Flask Routes
└── Analytics
```

### Target Structure (Modular)
```
xmrt_ecosystem/
├── app/
│   ├── agents/          # AI agent implementations
│   ├── integrations/    # External service integrations
│   ├── api/            # Flask routes and endpoints
│   ├── models/         # Data models and schemas
│   └── utils/          # Utility functions
├── tests/              # Comprehensive test suite
├── docs/               # Documentation
└── config/             # Configuration files
```

## Key Improvement Areas

### 🔴 Critical (In Progress)
- [x] Issue tracking created (#1069-1073)
- [x] Development infrastructure setup
- [ ] Modular architecture refactor
- [ ] Comprehensive testing framework
- [ ] Security hardening

### 🟡 High Priority
- [ ] Database persistence layer
- [ ] Enhanced error handling
- [ ] Performance optimization
- [ ] Real-time monitoring

### 🟢 Medium Priority  
- [ ] AI agent learning capabilities
- [ ] Advanced analytics dashboard
- [ ] Plugin system architecture
- [ ] Multi-organization support

## Contributing

See our [Contributing Guide](CONTRIBUTING.md) for detailed information on:
- Code style guidelines
- Testing requirements
- PR submission process
- Security considerations

## Performance Targets

- **Response Time**: <200ms for API endpoints
- **Memory Usage**: <512MB on Render free tier
- **Test Coverage**: >85%
- **Security Score**: A+ rating
- **Uptime**: >99.5%

---

**Current Status**: ✅ Development infrastructure active, ready for collaborative improvement!
