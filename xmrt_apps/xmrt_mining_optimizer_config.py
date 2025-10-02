#!/usr/bin/env python3
"""
Configuration module for XMRT Mining Optimizer
"""

import os
from datetime import datetime
from typing import Dict, List, Optional

class XMRTMiningOptimizerConfig:
    XMRT_REPOSITORIES = [
        "XMRT-Ecosystem",
        "xmrtassistant",
        "xmrtcash",
        "assetverse-nexus",
        "xmrt-signup",
        "xmrt-test-env",
        "eliza-xmrt-dao",
        "xmrt-eliza-enhanced",
        "xmrt-activepieces",
        "xmrt-openai-agents-js",
        "xmrt-agno",
        "xmrt-rust",
        "xmrt-rayhunter"
]
    VERSION = "1.0.0"
    APPLICATION_NAME = "XMRT Mining Optimizer"
    APPLICATION_TYPE = "mobile_app"
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    ENVIRONMENT = os.environ.get('ENVIRONMENT', 'production')
    GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
    GITHUB_API_URL = "https://api.github.com"
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    MOBILE_MINING = {"enabled": True, "auto_optimize": True, "power_efficient_mode": True, "max_cpu_usage": 80, "battery_threshold": 20}
    SECURITY_SETTINGS = {"encryption_enabled": True, "privacy_mode": True, "secure_communications": True, "audit_logging": True}
    PERFORMANCE_SETTINGS = {"cache_enabled": True, "async_operations": True, "batch_processing": True, "optimization_level": "high"}
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    CREATED_AT = datetime.now().isoformat()
    UPDATE_INTERVAL = 300
    HEALTH_CHECK_INTERVAL = 60
    INTEGRATIONS = {
        "github": {"enabled": True, "rate_limit": 5000},
        "discord": {"enabled": False, "webhook_url": None},
        "telegram": {"enabled": False, "bot_token": None}
    }

    @classmethod
    def get_config_dict(cls) -> Dict:
        return {
            "version": cls.VERSION,
            "application_name": cls.APPLICATION_NAME,
            "application_type": cls.APPLICATION_TYPE,
            "environment": cls.ENVIRONMENT,
            "debug": cls.DEBUG,
            "xmrt_repositories": cls.XMRT_REPOSITORIES,
            "mobile_mining": cls.MOBILE_MINING,
            "security_settings": cls.SECURITY_SETTINGS,
            "performance_settings": cls.PERFORMANCE_SETTINGS,
            "created_at": cls.CREATED_AT
        }

    @classmethod
    def validate_config(cls) -> bool:
        required_settings = ['VERSION', 'APPLICATION_NAME', 'XMRT_REPOSITORIES']
        for setting in required_settings:
            if not hasattr(cls, setting):
                return False
        return True

config = XMRTMiningOptimizerConfig()
if not config.validate_config():
    raise ValueError("Invalid configuration detected")
