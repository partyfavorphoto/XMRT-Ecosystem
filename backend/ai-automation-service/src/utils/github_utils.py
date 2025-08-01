"""
GitHub utilities for autonomous code management
"""

import os
import subprocess
import asyncio
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class GitHubUtils:
    def __init__(self):
        self.token = os.getenv('GITHUB_TOKEN')
        self.username = os.getenv('GITHUB_USERNAME', 'DevGruGold')
        self.repo = os.getenv('GITHUB_REPO', 'xmrt-ecosystem')
        
    async def commit_changes(self, message, files):
        """Commit changes to GitHub"""
        try:
            # Add files
            subprocess.run(['git', 'add', '.'], check=True)
            
            # Commit
            subprocess.run(['git', 'commit', '-m', message], check=True)
            
            # Push
            subprocess.run(['git', 'push', 'origin', 'main'], check=True)
            
            logger.info(f"[GitHub] Successfully committed: {message[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"[GitHub] Commit error: {e}")
            return False
    
    async def create_branch(self, branch_name):
        """Create a new branch for experimental changes"""
        try:
            subprocess.run(['git', 'checkout', '-b', branch_name], check=True)
            return True
        except Exception as e:
            logger.error(f"[GitHub] Branch creation error: {e}")
            return False
