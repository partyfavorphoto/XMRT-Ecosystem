#!/usr/bin/env python3
"""
Configuration for XMRT Ecosystem Dashboard
XMRT Ecosystem Application Configuration
"""

import os
from datetime import datetime

class XMRTEcosystemDashboardConfig:
    """Configuration class for XMRT Ecosystem Dashboard"""
    
    # XMRT Ecosystem Configuration
    XMRT_REPOSITORIES = ['XMRT-Ecosystem', 'xmrtassistant', 'xmrtcash', 'assetverse-nexus', 'xmrt-signup', 'xmrt-test-env', 'eliza-xmrt-dao', 'xmrt-eliza-enhanced', 'xmrt-activepieces', 'xmrt-openai-agents-js', 'xmrt-agno', 'xmrt-rust', 'xmrt-rayhunter']
    
    # API Endpoints
    GITHUB_API_BASE = "https://api.github.com"
    XMRT_API_BASE = "https://xmrt.vercel.app"
    MOBILE_MONERO_API = "https://mobilemonero.com/api"
    CASHDAPP_API = "https://cashdapp.vercel.app/api"
    MESHNET_API = "https://meshnet.xmrt.vercel.app/api"
    
    # Application Settings
    VERSION = "1.0.0"
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # GitHub Integration
    GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
    GITHUB_USERNAME = "DevGruGold"
    
    # OpenAI Integration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # XMRT DAO Configuration
    XMRT_DAO_MODE = True
    ECOSYSTEM_INTEGRATION = True
    MOBILE_MINING_ENABLED = True
    MESHNET_ENABLED = True
    CASHDAPP_ENABLED = True
    ELIZA_AI_ENABLED = True
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # XMRT Ecosystem Specific
    ECOSYSTEM_COMPONENTS = [
        "XMRT-Ecosystem",
        "MobileMonero.com", 
        "CashDapp",
        "MESHNET",
        "Eliza AI Governor",
        "XMRT Assistant",
        "Asset Verse Nexus"
    ]
    
    # Mobile Mining Configuration
    MOBILE_MINING_CONFIG = {
        "enabled": True,
        "optimization_level": "high",
        "battery_management": True,
        "network_efficiency": True,
        "meshnet_coordination": True
    }
    
    # Privacy and Security
    PRIVACY_SETTINGS = {
        "monero_integration": True,
        "no_kyc_policy": True,
        "privacy_first": True,
        "decentralized_banking": True
    }
    
    # Application Metadata
    CREATED_AT = datetime.now().isoformat()
    AUTHOR = "XMRT DAO Autonomous Agents"
    LICENSE = "MIT"
    ECOSYSTEM = "XMRT DAO"
    
    @classmethod
    def get_config_dict(cls):
        """Get configuration as dictionary"""
        return {
            "repositories": cls.XMRT_REPOSITORIES,
            "api_endpoints": {
                "github": cls.GITHUB_API_BASE,
                "xmrt": cls.XMRT_API_BASE,
                "mobile_monero": cls.MOBILE_MONERO_API,
                "cashdapp": cls.CASHDAPP_API,
                "meshnet": cls.MESHNET_API
            },
            "version": cls.VERSION,
            "ecosystem_components": cls.ECOSYSTEM_COMPONENTS,
            "mobile_mining": cls.MOBILE_MINING_CONFIG,
            "privacy_settings": cls.PRIVACY_SETTINGS,
            "created_at": cls.CREATED_AT,
            "xmrt_dao_mode": cls.XMRT_DAO_MODE
        }
    
    @classmethod
    def get_xmrt_ecosystem_status(cls):
        """Get XMRT ecosystem status"""
        return {
            "ecosystem": "XMRT DAO",
            "components_active": len(cls.ECOSYSTEM_COMPONENTS),
            "mobile_mining": cls.MOBILE_MINING_CONFIG["enabled"],
            "privacy_protection": cls.PRIVACY_SETTINGS["privacy_first"],
            "decentralized_governance": cls.ELIZA_AI_ENABLED,
            "offline_capability": cls.MESHNET_ENABLED,
            "financial_sovereignty": cls.CASHDAPP_ENABLED
        }

# Export configuration instance
config = XMRTEcosystemDashboardConfig()
