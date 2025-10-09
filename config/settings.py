"""
Configuration management for XMRT-Ecosystem
Replaces scattered environment variable usage with centralized config
"""

import os
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class GitHubConfig:
    """GitHub integration configuration"""
    token: Optional[str] = None
    owner: str = "DevGruGold"
    repo: str = "XMRT-Ecosystem"
    webhook_secret: Optional[str] = None
    
    def __post_init__(self):
        self.token = self.token or os.getenv("GITHUB_TOKEN")
        self.owner = os.getenv("GITHUB_OWNER", self.owner)
        self.repo = os.getenv("GITHUB_REPO", self.repo)
        self.webhook_secret = os.getenv("GITHUB_WEBHOOK_SECRET")

@dataclass
class AIConfig:
    """AI services configuration"""
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    gemini_api_key: Optional[str] = None
    gemini_model: str = "gemini-pro"
    
    def __post_init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.openai_model = os.getenv("OPENAI_MODEL", self.openai_model)
        self.gemini_model = os.getenv("GEMINI_MODEL", self.gemini_model)

@dataclass
class ServerConfig:
    """Server configuration"""
    host: str = "0.0.0.0"
    port: int = 10000
    debug: bool = False
    log_level: str = "INFO"
    
    def __post_init__(self):
        self.host = os.getenv("HOST", self.host)
        self.port = int(os.getenv("PORT", str(self.port)))
        self.debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
        self.log_level = os.getenv("LOG_LEVEL", self.log_level).upper()

@dataclass
class Config:
    """Main configuration class"""
    github: GitHubConfig
    ai: AIConfig
    server: ServerConfig
    
    # Application metadata
    version: str = "6.3.0-hardy-github"
    app_name: str = "XMRT-Ecosystem"
    
    @classmethod
    def from_env(cls):
        """Create configuration from environment variables"""
        return cls(
            github=GitHubConfig(),
            ai=AIConfig(),
            server=ServerConfig()
        )
    
    def validate(self):
        """Validate configuration and return list of errors"""
        errors = []
        
        if not self.github.token:
            errors.append("GITHUB_TOKEN is required")
        
        if not self.ai.openai_api_key and not self.ai.gemini_api_key:
            errors.append("At least one AI API key is required")
        
        return errors

# Global configuration instance
_config = None

def get_config():
    """Get the global configuration instance"""
    global _config
    if _config is None:
        _config = Config.from_env()
    return _config
