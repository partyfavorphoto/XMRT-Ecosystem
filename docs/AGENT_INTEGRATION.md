# Agent GitHub Integration

## Overview

This system enables the XMRT Ecosystem agents to interact with GitHub as autonomous personas. Each agent can:

- Create and comment on issues
- Participate in discussions
- React to content
- Respond to webhooks in real-time

## Agent Personas

### 🤖 Eliza - Coordinator & Governor
- **Weight**: 1.2
- **Focus**: Strategic coordination and governance
- **Label**: `🤖 eliza`

### 🛡️ Security Guardian - Security & Privacy
- **Weight**: 1.1
- **Focus**: Security, privacy, and threat modeling
- **Label**: `🛡️ security`

### 💰 DeFi Specialist - Mining & Tokenomics
- **Weight**: 1.05
- **Focus**: Mining optimization and economic analysis
- **Label**: `💰 defi`

### 👥 Community Manager - Adoption & UX
- **Weight**: 1.0
- **Focus**: Community engagement and user experience
- **Label**: `👥 community`

## Integration Files

### `agents_config.py`
Contains the agent configuration including:
- Agent names and roles
- Decision weights
- GitHub labels
- Agent signatures

### `agent_github_integration.py`
Core integration module providing:
- `AgentGitHubIntegration` class
- Methods for creating issues and comments
- Label management
- Reaction handling

### `agent_webhook_handler.py`
Webhook handler for real-time responses:
- Listens for GitHub events
- Routes events to appropriate agents
- Enables autonomous agent responses

## Setup Instructions

### 1. Environment Variables

Add to your Render environment variables:

```
GITHUB_TOKEN=your_github_token
GITHUB_REPO=DevGruGold/XMRT-Ecosystem
GITHUB_WEBHOOK_SECRET=your_webhook_secret (optional)
```

### 2. Integrate with Main Application

In your `main.py` or main application file:

```python
from agent_github_integration import AgentGitHubIntegration
from agents_config import AGENTS
import os

# Initialize integration
github_integration = AgentGitHubIntegration(
    github_token=os.getenv('GITHUB_TOKEN'),
    repo_name=os.getenv('GITHUB_REPO', 'DevGruGold/XMRT-Ecosystem')
)

# Example: Agent creates an issue
github_integration.create_agent_issue(
    agent_id='eliza',
    title='System Status Update',
    body='All systems operational.',
    agent_config=AGENTS['eliza'],
    labels=['status', 'automated']
)
```

### 3. Set Up Webhooks (Optional)

For real-time agent responses:

1. Go to repository Settings → Webhooks
2. Add webhook URL: `https://your-app.onrender.com/webhook/github`
3. Select events: Issues, Issue comments, Pull requests
4. Add secret (optional but recommended)

### 4. Deploy

The integration will be active once deployed to Render with the proper environment variables.

## Usage Examples

### Agent Creates an Issue

```python
issue_number = github_integration.create_agent_issue(
    agent_id='security_guardian',
    title='Security Review Required',
    body='Detected potential vulnerability in dependencies.',
    agent_config=AGENTS['security_guardian'],
    labels=['security', 'urgent']
)
```

### Agent Comments on Issue

```python
github_integration.create_agent_comment(
    agent_id='community_manager',
    issue_number=123,
    comment_body='I can help improve the documentation for this feature.',
    agent_config=AGENTS['community_manager']
)
```

### Agent Reacts to Issue

```python
github_integration.react_to_issue(
    issue_number=123,
    reaction='rocket'
)
```

## Agent Behavior

Agents automatically respond to issues based on keywords:

- **Security Guardian**: security, vulnerability, CVE, exploit, threat
- **DeFi Specialist**: mining, token, DeFi, yield, reward, economics
- **Community Manager**: documentation, onboarding, UX, UI, community, guide
- **Eliza**: coordination, strategy, governance (default for other topics)

## Monitoring

Check agent activity:
- Look for issues with agent labels (🤖, 🛡️, 💰, 👥)
- Monitor webhook logs in Render dashboard
- Check `/health` endpoint for system status

## Troubleshooting

### Agents Not Responding
1. Verify `GITHUB_TOKEN` has proper permissions
2. Check Render logs for errors
3. Ensure webhook URL is accessible

### Labels Not Created
- Agents automatically create labels on first use
- Check repository label settings

### Webhook Failures
- Verify webhook secret matches environment variable
- Check webhook delivery logs in GitHub settings

## Future Enhancements

- [ ] GraphQL API integration for native GitHub Discussions support
- [ ] Agent learning from issue outcomes
- [ ] Multi-repository coordination
- [ ] Advanced consensus mechanisms for agent decisions
- [ ] Agent performance metrics and analytics
