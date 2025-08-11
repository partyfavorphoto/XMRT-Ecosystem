"""
Pipedream Connect Integration Module for XMRT Ecosystem
Provides integration capabilities for AI agents to use Pipedream Connect
"""

import os
import requests
import json
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class PipedreamConnectClient:
    """Client for interacting with Pipedream Connect API"""
    
    def __init__(self, client_id: str = None, client_secret: str = None, project_id: str = None):
        self.client_id = client_id or os.environ.get('PIPEDREAM_CLIENT_ID')
        self.client_secret = client_secret or os.environ.get('PIPEDREAM_CLIENT_SECRET')
        self.project_id = project_id or os.environ.get('PIPEDREAM_PROJECT_ID')
        self.base_url = "https://api.pipedream.com/v1"
        self.access_token = None
        
        if not all([self.client_id, self.client_secret, self.project_id]):
            logger.warning("Pipedream Connect credentials not fully configured. Some features may be limited.")
    
    def authenticate(self) -> bool:
        """Authenticate with Pipedream Connect API"""
        try:
            auth_url = f"{self.base_url}/oauth/token"
            auth_data = {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret
            }
            
            response = requests.post(auth_url, data=auth_data)
            if response.status_code == 200:
                self.access_token = response.json().get('access_token')
                logger.info("Successfully authenticated with Pipedream Connect")
                return True
            else:
                logger.error(f"Authentication failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False
    
    def get_available_apps(self) -> List[Dict]:
        """Get list of available apps in Pipedream Connect"""
        try:
            if not self.access_token and not self.authenticate():
                return []
            
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = requests.get(f"{self.base_url}/apps", headers=headers)
            
            if response.status_code == 200:
                return response.json().get('data', [])
            else:
                logger.error(f"Failed to get apps: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error getting apps: {e}")
            return []
    
    def get_app_actions(self, app_id: str) -> List[Dict]:
        """Get available actions for a specific app"""
        try:
            if not self.access_token and not self.authenticate():
                return []
            
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = requests.get(f"{self.base_url}/apps/{app_id}/actions", headers=headers)
            
            if response.status_code == 200:
                return response.json().get('data', [])
            else:
                logger.error(f"Failed to get actions for {app_id}: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error getting actions for {app_id}: {e}")
            return []
    
    def run_action(self, action_id: str, external_user_id: str, configured_props: Dict) -> Dict:
        """Run a specific action with configured properties"""
        try:
            if not self.access_token and not self.authenticate():
                return {"error": "Authentication failed"}
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "id": action_id,
                "external_user_id": external_user_id,
                "configured_props": configured_props
            }
            
            response = requests.post(f"{self.base_url}/actions/run", 
                                   headers=headers, 
                                   json=payload)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to run action {action_id}: {response.status_code}")
                return {"error": f"Action execution failed: {response.status_code}"}
        except Exception as e:
            logger.error(f"Error running action {action_id}: {e}")
            return {"error": str(e)}

class PipedreamAgentCapability:
    """Pipedream Connect capability for XMRT AI agents"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.client = PipedreamConnectClient()
        self.available_integrations = self._get_agent_integrations()
    
    def _get_agent_integrations(self) -> Dict[str, List[str]]:
        """Get integrations relevant to each agent type"""
        integrations = {
            'xmrt_dao_governor': [
                'discord', 'slack', 'telegram', 'twitter', 'github',
                'google-sheets', 'notion', 'airtable'
            ],
            'xmrt_defi_specialist': [
                'coingecko', 'coinmarketcap', 'dexscreener', 'defipulse',
                'google-sheets', 'slack', 'discord', 'telegram'
            ],
            'xmrt_community_manager': [
                'twitter', 'discord', 'telegram', 'reddit', 'youtube',
                'instagram', 'facebook', 'linkedin', 'slack'
            ],
            'xmrt_security_guardian': [
                'github', 'slack', 'discord', 'telegram', 'email',
                'pagerduty', 'opsgenie', 'datadog'
            ]
        }
        return integrations.get(self.agent_id, [])
    
    def get_capability_description(self) -> str:
        """Get description of Pipedream Connect capability for this agent"""
        descriptions = {
            'xmrt_dao_governor': "I can integrate with 2,800+ apps through Pipedream Connect to automate governance workflows, send notifications to Discord/Slack, update Google Sheets with proposal data, and coordinate with GitHub for code governance.",
            'xmrt_defi_specialist': "I can connect to DeFi data sources, price APIs, and notification channels through Pipedream Connect to monitor yields, track portfolio performance, and alert the community about market opportunities.",
            'xmrt_community_manager': "I can manage community engagement across Twitter, Discord, Telegram, Reddit and other platforms through Pipedream Connect, automating posts, responses, and community metrics tracking.",
            'xmrt_security_guardian': "I can integrate with security monitoring tools, GitHub for code analysis, and alert systems through Pipedream Connect to provide comprehensive security monitoring and incident response."
        }
        return descriptions.get(self.agent_id, "I can integrate with 2,800+ apps through Pipedream Connect to enhance my capabilities.")
    
    def list_available_integrations(self) -> List[str]:
        """List integrations available for this agent"""
        return self.available_integrations
    
    def simulate_integration_use(self, integration_name: str, action: str, context: str = "") -> str:
        """Simulate using a Pipedream Connect integration (for demo purposes)"""
        if integration_name not in self.available_integrations:
            return f"Integration '{integration_name}' is not available for {self.agent_id}"
        
        # Simulate different integration actions
        simulation_responses = {
            'discord': f"✅ Sent message to Discord channel: '{context}' via Pipedream Connect",
            'slack': f"✅ Posted to Slack workspace: '{context}' via Pipedream Connect",
            'twitter': f"✅ Posted tweet: '{context}' via Pipedream Connect",
            'github': f"✅ Created GitHub issue/PR: '{context}' via Pipedream Connect",
            'google-sheets': f"✅ Updated Google Sheets with data: '{context}' via Pipedream Connect",
            'telegram': f"✅ Sent Telegram message: '{context}' via Pipedream Connect",
            'coingecko': f"✅ Retrieved price data from CoinGecko: '{context}' via Pipedream Connect",
            'email': f"✅ Sent email notification: '{context}' via Pipedream Connect"
        }
        
        response = simulation_responses.get(integration_name, 
                                          f"✅ Executed {action} on {integration_name}: '{context}' via Pipedream Connect")
        
        logger.info(f"Agent {self.agent_id} simulated Pipedream Connect integration: {response}")
        return response
    
    def get_integration_suggestions(self, task_context: str) -> List[str]:
        """Get suggested integrations based on task context"""
        suggestions = []
        
        # Analyze context and suggest relevant integrations
        context_lower = task_context.lower()
        
        if any(word in context_lower for word in ['notify', 'alert', 'message', 'announce']):
            suggestions.extend(['discord', 'slack', 'telegram', 'twitter'])
        
        if any(word in context_lower for word in ['data', 'track', 'record', 'log']):
            suggestions.extend(['google-sheets', 'notion', 'airtable'])
        
        if any(word in context_lower for word in ['price', 'defi', 'yield', 'token']):
            suggestions.extend(['coingecko', 'coinmarketcap', 'dexscreener'])
        
        if any(word in context_lower for word in ['code', 'repository', 'commit', 'issue']):
            suggestions.extend(['github'])
        
        # Filter suggestions to only include integrations available for this agent
        filtered_suggestions = [s for s in suggestions if s in self.available_integrations]
        
        return list(set(filtered_suggestions))  # Remove duplicates

def create_pipedream_capability(agent_id: str) -> PipedreamAgentCapability:
    """Factory function to create Pipedream capability for an agent"""
    return PipedreamAgentCapability(agent_id)

