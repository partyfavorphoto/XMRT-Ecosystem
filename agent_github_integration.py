
"""
Agent GitHub Integration Module
This module should be integrated into the deployed XMRT Ecosystem system.
"""

from github import Github, Auth
import os
from typing import Dict, Optional
from datetime import datetime

class AgentGitHubIntegration:
    """Enables agents to interact with GitHub autonomously."""
    
    def __init__(self, github_token: str, repo_name: str):
        """Initialize GitHub integration with authentication."""
        auth = Auth.Token(github_token)
        self.github = Github(auth=auth)
        self.repo = self.github.get_repo(repo_name)
        
    def create_agent_comment(self, agent_id: str, issue_number: int, 
                            comment_body: str, agent_config: Dict) -> bool:
        """
        Create a comment on an issue as an agent.
        
        Args:
            agent_id: Agent identifier (e.g., 'eliza', 'security_guardian')
            issue_number: GitHub issue number
            comment_body: The comment content
            agent_config: Agent configuration with signature
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            issue = self.repo.get_issue(issue_number)
            
            # Format comment with agent signature
            formatted_comment = f"{comment_body}\n\n---\n{agent_config['signature']}"
            
            # Create comment
            issue.create_comment(formatted_comment)
            
            # Add agent label if it doesn't exist
            self._ensure_agent_label(agent_config)
            
            # Add label to issue
            issue.add_to_labels(agent_config['github_label'])
            
            return True
        except Exception as e:
            print(f"Error creating comment: {e}")
            return False
    
    def create_agent_issue(self, agent_id: str, title: str, body: str,
                          agent_config: Dict, labels: Optional[List[str]] = None) -> Optional[int]:
        """
        Create a new issue as an agent.
        
        Args:
            agent_id: Agent identifier
            title: Issue title
            body: Issue body
            agent_config: Agent configuration
            labels: Additional labels to add
            
        Returns:
            Optional[int]: Issue number if successful, None otherwise
        """
        try:
            # Ensure agent label exists
            self._ensure_agent_label(agent_config)
            
            # Format body with agent signature
            formatted_body = f"{body}\n\n---\n{agent_config['signature']}\n*Generated: {datetime.utcnow().isoformat()}Z*"
            
            # Prepare labels
            issue_labels = [agent_config['github_label']]
            if labels:
                issue_labels.extend(labels)
            
            # Create issue
            issue = self.repo.create_issue(
                title=title,
                body=formatted_body,
                labels=issue_labels
            )
            
            return issue.number
        except Exception as e:
            print(f"Error creating issue: {e}")
            return None
    
    def create_discussion_post(self, agent_id: str, title: str, body: str,
                              agent_config: Dict, category: str = "General") -> bool:
        """
        Create a discussion post as an agent.
        
        Args:
            agent_id: Agent identifier
            title: Discussion title
            body: Discussion body
            agent_config: Agent configuration
            category: Discussion category
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Format body with agent signature
            formatted_body = f"{body}\n\n---\n{agent_config['signature']}\n*Posted: {datetime.utcnow().isoformat()}Z*"
            
            # Note: GitHub API v3 doesn't support discussions directly
            # This would require GraphQL API or creating as an issue instead
            # For now, we'll create as an issue with a discussion label
            
            self.create_agent_issue(
                agent_id=agent_id,
                title=f"💬 {title}",
                body=formatted_body,
                agent_config=agent_config,
                labels=["discussion", "agent-post"]
            )
            
            return True
        except Exception as e:
            print(f"Error creating discussion: {e}")
            return False
    
    def react_to_issue(self, issue_number: int, reaction: str = "+1") -> bool:
        """
        Add a reaction to an issue.
        
        Args:
            issue_number: GitHub issue number
            reaction: Reaction type (+1, -1, laugh, confused, heart, hooray, rocket, eyes)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            issue = self.repo.get_issue(issue_number)
            issue.create_reaction(reaction)
            return True
        except Exception as e:
            print(f"Error adding reaction: {e}")
            return False
    
    def _ensure_agent_label(self, agent_config: Dict) -> None:
        """Ensure the agent's label exists in the repository."""
        try:
            label_name = agent_config['github_label']
            
            # Try to get the label
            try:
                self.repo.get_label(label_name)
            except:
                # Label doesn't exist, create it
                # Use different colors for different agent types
                color_map = {
                    "eliza": "7B68EE",  # Medium slate blue
                    "security": "FF6B6B",  # Red
                    "defi": "4ECDC4",  # Teal
                    "community": "95E1D3"  # Mint
                }
                
                # Extract color key from label
                color = "0E8A16"  # Default green
                for key, col in color_map.items():
                    if key in label_name.lower():
                        color = col
                        break
                
                self.repo.create_label(
                    name=label_name,
                    color=color,
                    description=f"Issues and comments from {agent_config['name']}"
                )
        except Exception as e:
            print(f"Error ensuring label: {e}")


# Example usage in the XMRT Ecosystem application
def integrate_with_xmrt_system():
    """
    Integration example for the XMRT Ecosystem.
    This should be called from the main application.
    """
    
    # Get credentials from environment
    github_token = os.getenv('GITHUB_TOKEN')
    repo_name = os.getenv('GITHUB_REPO', 'DevGruGold/XMRT-Ecosystem')
    
    # Initialize integration
    integration = AgentGitHubIntegration(github_token, repo_name)
    
    # Example: Eliza creates a status update
    from agents_config import AGENTS  # Import agent config
    
    eliza_config = AGENTS['eliza']
    
    integration.create_agent_issue(
        agent_id='eliza',
        title='🤖 Eliza System Status Update',
        body='System operational. All agents functioning within normal parameters.',
        agent_config=eliza_config,
        labels=['status', 'automated']
    )
    
    return integration
