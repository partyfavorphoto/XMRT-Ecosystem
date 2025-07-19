import requests
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import os
import base64
import hmac
import hashlib
import urllib.parse
import time
import secrets

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class XAPIService:
    """
    X (Twitter) API Service for managing Spaces and agent accounts.
    Handles authentication, Space creation/management, and posting to agent accounts.
    """
    
    def __init__(self):
        self.api_base_url = "https://api.x.com"
        self.api_version = "2"
        
    def _generate_oauth_signature(self, method: str, url: str, params: Dict[str, str], 
                                 consumer_secret: str, token_secret: str = "") -> str:
        """Generate OAuth 1.0a signature for API requests."""
        # Create parameter string
        sorted_params = sorted(params.items())
        param_string = "&".join([f"{k}={v}" for k, v in sorted_params])
        
        # Create signature base string
        base_string = f"{method.upper()}&{urllib.parse.quote(url, safe='')}&{urllib.parse.quote(param_string, safe='')}"
        
        # Create signing key
        signing_key = f"{urllib.parse.quote(consumer_secret, safe='')}&{urllib.parse.quote(token_secret, safe='')}"
        
        # Generate signature
        signature = base64.b64encode(
            hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha1).digest()
        ).decode()
        
        return signature
    
    def _get_oauth_header(self, method: str, url: str, consumer_key: str, consumer_secret: str,
                         access_token: str = "", access_token_secret: str = "") -> str:
        """Generate OAuth 1.0a authorization header."""
        oauth_params = {
            "oauth_consumer_key": consumer_key,
            "oauth_nonce": secrets.token_hex(16),
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_timestamp": str(int(time.time())),
            "oauth_version": "1.0"
        }
        
        if access_token:
            oauth_params["oauth_token"] = access_token
        
        # Generate signature
        signature = self._generate_oauth_signature(method, url, oauth_params, consumer_secret, access_token_secret)
        oauth_params["oauth_signature"] = signature
        
        # Create authorization header
        auth_header = "OAuth " + ", ".join([f'{k}="{urllib.parse.quote(str(v), safe="")}"' for k, v in sorted(oauth_params.items())])
        
        return auth_header
    
    def create_space(self, agent_credentials: Dict[str, str], title: str, description: str = "") -> Dict[str, Any]:
        """
        Create a new X Space for the boardroom session.
        
        Args:
            agent_credentials: Dictionary containing API keys for the agent
            title: Title of the Space
            description: Description of the Space
            
        Returns:
            Dictionary with Space information or error details
        """
        try:
            url = f"{self.api_base_url}/{self.api_version}/spaces"
            
            headers = {
                "Authorization": self._get_oauth_header(
                    "POST", url,
                    agent_credentials["consumer_key"],
                    agent_credentials["consumer_secret"],
                    agent_credentials["access_token"],
                    agent_credentials["access_token_secret"]
                ),
                "Content-Type": "application/json"
            }
            
            data = {
                "title": title,
                "description": description,
                "is_ticketed": False,
                "scheduled_start": None  # Start immediately
            }
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 201:
                space_data = response.json()
                logger.info(f"Successfully created Space: {space_data.get('data', {}).get('id')}")
                return {
                    "success": True,
                    "space_id": space_data.get("data", {}).get("id"),
                    "space_url": f"https://x.com/i/spaces/{space_data.get('data', {}).get('id')}",
                    "title": title,
                    "created_at": datetime.utcnow().isoformat()
                }
            else:
                logger.error(f"Failed to create Space: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"API Error: {response.status_code}",
                    "details": response.text
                }
                
        except Exception as e:
            logger.error(f"Error creating Space: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def end_space(self, agent_credentials: Dict[str, str], space_id: str) -> Dict[str, Any]:
        """
        End an active X Space.
        
        Args:
            agent_credentials: Dictionary containing API keys for the agent
            space_id: ID of the Space to end
            
        Returns:
            Dictionary with operation result
        """
        try:
            url = f"{self.api_base_url}/{self.api_version}/spaces/{space_id}/end"
            
            headers = {
                "Authorization": self._get_oauth_header(
                    "POST", url,
                    agent_credentials["consumer_key"],
                    agent_credentials["consumer_secret"],
                    agent_credentials["access_token"],
                    agent_credentials["access_token_secret"]
                )
            }
            
            response = requests.post(url, headers=headers)
            
            if response.status_code == 200:
                logger.info(f"Successfully ended Space: {space_id}")
                return {
                    "success": True,
                    "space_id": space_id,
                    "ended_at": datetime.utcnow().isoformat()
                }
            else:
                logger.error(f"Failed to end Space: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"API Error: {response.status_code}",
                    "details": response.text
                }
                
        except Exception as e:
            logger.error(f"Error ending Space: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_space_info(self, agent_credentials: Dict[str, str], space_id: str) -> Dict[str, Any]:
        """
        Get information about a specific Space.
        
        Args:
            agent_credentials: Dictionary containing API keys for the agent
            space_id: ID of the Space
            
        Returns:
            Dictionary with Space information
        """
        try:
            url = f"{self.api_base_url}/{self.api_version}/spaces/{space_id}"
            
            headers = {
                "Authorization": self._get_oauth_header(
                    "GET", url,
                    agent_credentials["consumer_key"],
                    agent_credentials["consumer_secret"],
                    agent_credentials["access_token"],
                    agent_credentials["access_token_secret"]
                )
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "data": response.json()
                }
            else:
                logger.error(f"Failed to get Space info: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"API Error: {response.status_code}",
                    "details": response.text
                }
                
        except Exception as e:
            logger.error(f"Error getting Space info: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def post_tweet(self, agent_credentials: Dict[str, str], content: str, 
                   space_id: str = None) -> Dict[str, Any]:
        """
        Post a tweet from an AI agent's account.
        
        Args:
            agent_credentials: Dictionary containing API keys for the agent
            content: Tweet content
            space_id: Optional Space ID to link the tweet to
            
        Returns:
            Dictionary with tweet information or error details
        """
        try:
            url = f"{self.api_base_url}/{self.api_version}/tweets"
            
            headers = {
                "Authorization": self._get_oauth_header(
                    "POST", url,
                    agent_credentials["consumer_key"],
                    agent_credentials["consumer_secret"],
                    agent_credentials["access_token"],
                    agent_credentials["access_token_secret"]
                ),
                "Content-Type": "application/json"
            }
            
            data = {
                "text": content
            }
            
            # Add Space link if provided
            if space_id:
                data["text"] += f" https://x.com/i/spaces/{space_id}"
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 201:
                tweet_data = response.json()
                logger.info(f"Successfully posted tweet: {tweet_data.get('data', {}).get('id')}")
                return {
                    "success": True,
                    "tweet_id": tweet_data.get("data", {}).get("id"),
                    "content": content,
                    "posted_at": datetime.utcnow().isoformat()
                }
            else:
                logger.error(f"Failed to post tweet: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"API Error: {response.status_code}",
                    "details": response.text
                }
                
        except Exception as e:
            logger.error(f"Error posting tweet: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def search_spaces(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """
        Search for Spaces by title or keywords.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            Dictionary with search results
        """
        try:
            # Note: This would require app-only authentication for public search
            url = f"{self.api_base_url}/{self.api_version}/spaces/search"
            
            params = {
                "query": query,
                "max_results": max_results
            }
            
            # For now, return a placeholder response
            # In production, implement proper app-only auth
            return {
                "success": True,
                "data": [],
                "message": "Space search functionality requires app-only authentication"
            }
            
        except Exception as e:
            logger.error(f"Error searching Spaces: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def validate_credentials(self, agent_credentials: Dict[str, str]) -> Dict[str, Any]:
        """
        Validate API credentials for an agent.
        
        Args:
            agent_credentials: Dictionary containing API keys for the agent
            
        Returns:
            Dictionary with validation result
        """
        try:
            url = f"{self.api_base_url}/{self.api_version}/users/me"
            
            headers = {
                "Authorization": self._get_oauth_header(
                    "GET", url,
                    agent_credentials["consumer_key"],
                    agent_credentials["consumer_secret"],
                    agent_credentials["access_token"],
                    agent_credentials["access_token_secret"]
                )
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                return {
                    "success": True,
                    "user_id": user_data.get("data", {}).get("id"),
                    "username": user_data.get("data", {}).get("username"),
                    "name": user_data.get("data", {}).get("name")
                }
            else:
                logger.error(f"Failed to validate credentials: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"API Error: {response.status_code}",
                    "details": response.text
                }
                
        except Exception as e:
            logger.error(f"Error validating credentials: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_agent_credentials(self, agent_id: int) -> Dict[str, str]:
        """
        Retrieve API credentials for a specific agent.
        This is a placeholder - in production, credentials should be securely stored.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            Dictionary with API credentials
        """
        # In production, retrieve from secure storage (e.g., encrypted database, vault)
        # For now, return placeholder structure
        return {
            "consumer_key": os.getenv(f"AGENT_{agent_id}_CONSUMER_KEY", ""),
            "consumer_secret": os.getenv(f"AGENT_{agent_id}_CONSUMER_SECRET", ""),
            "access_token": os.getenv(f"AGENT_{agent_id}_ACCESS_TOKEN", ""),
            "access_token_secret": os.getenv(f"AGENT_{agent_id}_ACCESS_TOKEN_SECRET", "")
        }

