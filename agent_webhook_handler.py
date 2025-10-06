"""
Webhook Handler for Agent Responses
Allows agents to respond to GitHub events in real-time.
"""

from flask import Flask, request, jsonify
from agent_github_integration import AgentGitHubIntegration
from agents_config import AGENTS
import os
import hmac
import hashlib

app = Flask(__name__)

# Initialize GitHub integration
github_integration = AgentGitHubIntegration(
    github_token=os.getenv('GITHUB_TOKEN'),
    repo_name=os.getenv('GITHUB_REPO', 'DevGruGold/XMRT-Ecosystem')
)

def verify_webhook_signature(payload_body, signature_header):
    """Verify that the webhook came from GitHub."""
    secret = os.getenv('GITHUB_WEBHOOK_SECRET', '').encode()
    if not secret:
        return True  # Skip verification if no secret set
    
    hash_object = hmac.new(secret, msg=payload_body, digestmod=hashlib.sha256)
    expected_signature = "sha256=" + hash_object.hexdigest()
    return hmac.compare_digest(expected_signature, signature_header)

@app.route('/webhook/github', methods=['POST'])
def github_webhook():
    """Handle GitHub webhook events."""
    
    # Verify signature
    signature = request.headers.get('X-Hub-Signature-256')
    if not verify_webhook_signature(request.data, signature):
        return jsonify({'error': 'Invalid signature'}), 401
    
    event_type = request.headers.get('X-GitHub-Event')
    payload = request.json
    
    # Handle different event types
    if event_type == 'issues':
        handle_issue_event(payload)
    elif event_type == 'issue_comment':
        handle_comment_event(payload)
    elif event_type == 'pull_request':
        handle_pr_event(payload)
    
    return jsonify({'status': 'processed'}), 200

def handle_issue_event(payload):
    """Handle issue events - agents can respond to new issues."""
    action = payload.get('action')
    issue = payload.get('issue')
    
    if action == 'opened':
        issue_number = issue['number']
        issue_title = issue['title']
        issue_body = issue['body'] or ''
        
        # Determine which agent should respond based on keywords
        agent_id = determine_responsible_agent(issue_title, issue_body)
        
        if agent_id:
            agent_config = AGENTS[agent_id]
            
            # Agent acknowledges the issue
            comment = f"Thank you for opening this issue. I'll review it based on my expertise in {agent_config['role']}."
            
            github_integration.create_agent_comment(
                agent_id=agent_id,
                issue_number=issue_number,
                comment_body=comment,
                agent_config=agent_config
            )

def handle_comment_event(payload):
    """Handle comment events - agents can participate in discussions."""
    # Implement agent discussion logic here
    pass

def handle_pr_event(payload):
    """Handle pull request events - agents can review PRs."""
    # Implement agent PR review logic here
    pass

def determine_responsible_agent(title: str, body: str) -> str:
    """Determine which agent should respond based on content."""
    text = (title + " " + body).lower()
    
    # Security-related keywords
    if any(word in text for word in ['security', 'vulnerability', 'cve', 'exploit', 'threat']):
        return 'security_guardian'
    
    # DeFi/Economics keywords
    if any(word in text for word in ['mining', 'token', 'defi', 'yield', 'reward', 'economics']):
        return 'defi_specialist'
    
    # Community/UX keywords
    if any(word in text for word in ['documentation', 'onboarding', 'ux', 'ui', 'community', 'guide']):
        return 'community_manager'
    
    # Default to Eliza for coordination
    return 'eliza'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
