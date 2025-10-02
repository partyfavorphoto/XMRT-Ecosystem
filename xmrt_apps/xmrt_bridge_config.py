#!/usr/bin/env python3
"""
Config for XMRT Bridge
"""
import os
from datetime import datetime

class XMRTBridgeConfig:
    XMRT_REPOS = ['XMRT-Ecosystem', 'xmrtassistant', 'xmrtcash', 'assetverse-nexus', 'xmrt-signup', 'xmrt-test-env', 'eliza-xmrt-dao', 'xmrt-eliza-enhanced', 'xmrt-activepieces', 'xmrt-openai-agents-js', 'xmrt-agno', 'xmrt-rust', 'xmrt-rayhunter']
    VERSION = "1.0.0"
    DEBUG = os.environ.get('DEBUG', False)
    GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
    OPENAI_KEY = os.environ.get('OPENAI_API_KEY')
    MOBILE_MINING = {"enabled": True}
    CREATED_AT = datetime.now().isoformat()
    
config = XMRTBridgeConfig()
