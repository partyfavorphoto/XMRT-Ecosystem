# XMRT Ecosystem Configuration Management

import os
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from pathlib import Path

@dataclass
class GitHubConfig:
    token: str
    owner: str
    repo: str
    webhook_secret: Optional[str] = None
    
    def __post_init__(self):
        if not self.token:
            raise ValueError("GitHub token is required")
        if not self.owner:
            raise ValueError("GitHub owner is required")
        if not self.repo:
            raise ValueError("GitHub repo is required")

@dataclass
class AIConfig:
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    gemini_api_key: Optional[str] = None
    gemini_model: str = "gemini-pro"
    temperature: float = 0.7
    max_tokens: int = 1200
    
    def has_openai(self) -> bool:
        return bool(self.openai_api_key)
    
    def has_gemini(self) -> bool:
        return bool(self.gemini_api_key)

@dataclass
class SecurityConfig:
    api_keys: List[str]
    webhook_secret: Optional[str] = None
    rate_limit_enabled: bool = True
    https_only: bool = True
    
    def __post_init__(self):
        if not self.api_keys:
            # Generate a default API key if none provided
            import secrets
            self.api_keys = [secrets.token_urlsafe(32)]
            print(f"⚠️  Generated default API key: {self.api_keys[0]}")

@dataclass
class DatabaseConfig:
    url: str = "sqlite:///data/xmrt.db"
    echo: bool = False
    pool_size: int = 10
    max_overflow: int = 20

@dataclass
class AppConfig:
    host: str = "0.0.0.0"
    port: int = 10000
    debug: bool = False
    log_level: str = "INFO"
    data_dir: str = "./data"
    
    github: GitHubConfig
    ai: AIConfig
    security: SecurityConfig
    database: DatabaseConfig
    
    @classmethod
    def from_env(cls) -> 'AppConfig':
        """Load configuration from environment variables"""
        
        # Ensure data directory exists
        data_dir = os.getenv("DATA_DIR", "./data")
        Path(data_dir).mkdir(exist_ok=True)
        
        github = GitHubConfig(
            token=os.getenv("GITHUB_TOKEN", ""),
            owner=os.getenv("GITHUB_OWNER", "DevGruGold"),
            repo=os.getenv("GITHUB_REPO", "XMRT-Ecosystem"),
            webhook_secret=os.getenv("GITHUB_WEBHOOK_SECRET")
        )
        
        ai = AIConfig(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            gemini_api_key=os.getenv("GEMINI_API_KEY"),
            gemini_model=os.getenv("GEMINI_MODEL", "gemini-pro"),
            temperature=float(os.getenv("AI_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("AI_MAX_TOKENS", "1200"))
        )
        
        security = SecurityConfig(
            api_keys=[k.strip() for k in os.getenv("API_KEYS", "").split(",") if k.strip()],
            webhook_secret=os.getenv("WEBHOOK_SECRET"),
            rate_limit_enabled=os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true",
            https_only=os.getenv("HTTPS_ONLY", "true").lower() == "true"
        )
        
        database = DatabaseConfig(
            url=os.getenv("DATABASE_URL", f"sqlite:///{data_dir}/xmrt.db"),
            echo=os.getenv("DB_ECHO", "false").lower() == "true",
            pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
            max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "20"))
        )
        
        return cls(
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", "10000")),
            debug=os.getenv("DEBUG", "false").lower() == "true",
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
            data_dir=data_dir,
            github=github,
            ai=ai,
            security=security,
            database=database
        )
    
    def validate(self) -> None:
        """Validate configuration"""
        if not self.github.token:
            raise ValueError("GitHub token is required")
        
        if not (self.ai.has_openai() or self.ai.has_gemini()):
            print("⚠️  Warning: No AI API keys configured. AI features will be limited.")
        
        if not self.security.api_keys:
            print("⚠️  Warning: No API keys configured. Using generated default.")
