#!/usr/bin/env python3
"""
GitHub MCP Server for XMRT Ecosystem
Provides comprehensive GitHub repository management capabilities through MCP
"""

import os
import json
import logging
import asyncio
import requests
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from pathlib import Path

from mcp.server import FastMCP
from mcp.types import Resource, Tool, Prompt
from github import Github, GithubException
from github.Repository import Repository
from github.Issue import Issue
from github.PullRequest import PullRequest
# Discussion functionality will be handled via GitHub API directly

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GitHubMCPServer:
    """GitHub MCP Server for XMRT ecosystem repository management"""
    
    def __init__(self, github_token: str, oauth_client_id: str = None, oauth_client_secret: str = None):
        self.github_token = github_token
        self.oauth_client_id = oauth_client_id
        self.oauth_client_secret = oauth_client_secret
        self.github = Github(github_token)
        
        # Initialize FastMCP
        self.mcp = FastMCP("GitHub-XMRT-Server")
        
        # XMRT repositories configuration
        self.xmrt_repositories = [
            "DevGruGold/XMRT-Ecosystem",
            "DevGruGold/XMRT-DAO-Ecosystem", 
            "DevGruGold/xmrt-eliza",
            "DevGruGold/xmrt-dao-eliza",
            "DevGruGold/xmrtnet",
            "DevGruGold/XMRT.io"
        ]
        
        # Agent OAuth configuration
        self.agent_oauth_config = {
            "eliza": {
                "username": "xmrt-eliza-agent",
                "scopes": ["repo", "write:discussion", "read:org"],
                "role": "lead_coordinator"
            },
            "dao_governor": {
                "username": "xmrt-dao-governor", 
                "scopes": ["repo", "write:discussion"],
                "role": "governance_manager"
            },
            "defi_specialist": {
                "username": "xmrt-defi-specialist",
                "scopes": ["repo", "read:org"],
                "role": "financial_operations"
            },
            "security_guardian": {
                "username": "xmrt-security-guardian",
                "scopes": ["repo", "security_events"],
                "role": "security_operations"
            },
            "community_manager": {
                "username": "xmrt-community-manager",
                "scopes": ["write:discussion", "repo"],
                "role": "community_engagement"
            }
        }
        
        # Register tools, resources, and prompts
        self._register_tools()
        self._register_resources()
        self._register_prompts()
        
        logger.info("GitHub MCP Server initialized")
    
    def run(self, transport: str = "stdio"):
        """Run the GitHub MCP server"""
        logger.info(f"Starting GitHub MCP Server with {transport} transport")
        self.mcp.run(transport=transport)

def main():
    """Main function to start the GitHub MCP server"""
    
    # Get credentials from environment
    github_token = os.getenv("GITHUB_TOKEN")
    oauth_client_id = os.getenv("GITHUB_OAUTH_CLIENT_ID")
    oauth_client_secret = os.getenv("GITHUB_OAUTH_CLIENT_SECRET")
    
    if not github_token:
        logger.error("GITHUB_TOKEN environment variable is required")
        return
    
    # Create and run server
    server = GitHubMCPServer(github_token, oauth_client_id, oauth_client_secret)
    server.run()

if __name__ == "__main__":
    main()
