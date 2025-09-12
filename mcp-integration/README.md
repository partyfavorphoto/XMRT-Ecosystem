# XMRT MCP Integration

This directory contains the Model Context Protocol (MCP) integration for the XMRT ecosystem, providing autonomous agents with full-stack authority over repository management, deployment operations, and ecosystem coordination.

## Overview

The MCP integration consists of three specialized servers that work together to provide comprehensive automation capabilities:

- **GitHub MCP Server** (`github_mcp_server_clean.py`): Manages all GitHub operations including repository analysis, issue tracking, pull request management, and discussion automation
- **Render MCP Server** (`render_mcp_server_clean.py`): Handles deployment and infrastructure management on the Render platform
- **XMRT MCP Server** (`xmrt_mcp_server_clean.py`): Provides ecosystem-specific coordination and agent management

## Key Features

### 🔐 GitHub OAuth Integration
- **Client ID**: `Ov23ctotTxFlu68znTlF`
- Individual agent accounts with role-based permissions
- Secure, auditable access to GitHub resources

### 🚀 Full-Stack Automation
- Automated repository improvements and code quality enhancements
- Continuous deployment and infrastructure management
- Intelligent agent coordination and task distribution

### 📊 Comprehensive Monitoring
- Real-time ecosystem health monitoring
- Performance metrics and analytics
- Automated incident response and recovery

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install mcp-server PyGithub redis requests
   ```

2. **Set Environment Variables**:
   ```bash
   export GITHUB_TOKEN="your_github_token"
   export GITHUB_OAUTH_CLIENT_ID="Ov23ctotTxFlu68znTlF"
   export GITHUB_OAUTH_CLIENT_SECRET="your_oauth_secret"
   export RENDER_API_KEY="your_render_api_key"
   export REDIS_URL="redis://localhost:6379"
   ```

3. **Run Individual MCP Servers**:
   ```bash
   # GitHub MCP Server
   python3 github_mcp_server_clean.py
   
   # Render MCP Server  
   python3 render_mcp_server_clean.py
   
   # XMRT MCP Server
   python3 xmrt_mcp_server_clean.py
   ```

## Agent Configuration

The system supports five specialized agents, each with specific GitHub OAuth permissions:

- **Eliza** (Lead Coordinator): Full repository and discussion management
- **DAO Governor** (Governance Manager): Repository and governance operations
- **DeFi Specialist** (Financial Operations): Repository and financial integrations
- **Security Guardian** (Security Operations): Security monitoring and incident response
- **Community Manager** (Community Engagement): Discussion and community support

## Security

All sensitive credentials are externalized through environment variables:
- No hardcoded API keys or tokens in source code
- OAuth-based authentication for individual agent accounts
- Secure credential management through environment configuration

## Documentation

- [MCP Integration Guide](mcp_integration_guide.md) - Detailed implementation guide
- [Test Report](mcp_test_report.md) - Validation and testing results

## Support

This MCP integration provides the XMRT ecosystem with autonomous operation capabilities. For issues or questions, refer to the comprehensive documentation or create an issue in the repository.
