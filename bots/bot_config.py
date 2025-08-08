#!/usr/bin/env python3
'''
XMRT Ecosystem Bot Configuration
Centralized configuration for multi-platform bots
'''

import os
from typing import Dict, List, Any

class BotConfig:
    '''Centralized bot configuration'''
    
    # Platform Settings
    DISCORD_CONFIG = {
        'token': os.environ.get('DISCORD_BOT_TOKEN'),
        'guild_id': os.environ.get('DISCORD_GUILD_ID'),
        'channels': {
            'general': os.environ.get('DISCORD_GENERAL_CHANNEL'),
            'governance': os.environ.get('DISCORD_GOVERNANCE_CHANNEL'),
            'defi': os.environ.get('DISCORD_DEFI_CHANNEL'),
            'security': os.environ.get('DISCORD_SECURITY_CHANNEL')
        },
        'enabled': bool(os.environ.get('DISCORD_BOT_TOKEN')),
        'auto_post_interval': 3600,  # 1 hour
        'response_delay': 1  # 1 second
    }
    
    TELEGRAM_CONFIG = {
        'token': os.environ.get('TELEGRAM_BOT_TOKEN'),
        'chat_id': os.environ.get('TELEGRAM_CHAT_ID'),
        'enabled': bool(os.environ.get('TELEGRAM_BOT_TOKEN')),
        'auto_post_interval': 1800,  # 30 minutes
        'response_delay': 2  # 2 seconds
    }
    
    TWITTER_CONFIG = {
        'api_key': os.environ.get('TWITTER_API_KEY'),
        'api_secret': os.environ.get('TWITTER_API_SECRET'),
        'access_token': os.environ.get('TWITTER_ACCESS_TOKEN'),
        'access_token_secret': os.environ.get('TWITTER_ACCESS_TOKEN_SECRET'),
        'bearer_token': os.environ.get('TWITTER_BEARER_TOKEN'),
        'enabled': bool(os.environ.get('TWITTER_API_KEY')),
        'auto_post_interval': 7200,  # 2 hours
        'response_delay': 5,  # 5 seconds
        'max_tweet_length': 280
    }
    
    # Agent Assignment Rules
    AGENT_PLATFORM_MAPPING = {
        'xmrt_dao_governor': ['discord', 'telegram', 'twitter'],
        'xmrt_defi_specialist': ['discord', 'telegram', 'twitter'],
        'xmrt_community_manager': ['discord', 'telegram', 'twitter'],
        'xmrt_security_guardian': ['discord', 'telegram']  # No Twitter for security
    }
    
    # Message Routing Rules
    MESSAGE_ROUTING = {
        'governance_keywords': ['governance', 'proposal', 'vote', 'dao', 'treasury'],
        'defi_keywords': ['defi', 'yield', 'liquidity', 'farming', 'staking', 'apy'],
        'security_keywords': ['security', 'audit', 'threat', 'vulnerability', 'hack'],
        'community_keywords': ['community', 'event', 'welcome', 'help', 'support']
    }
    
    # Autonomous Posting Schedule
    POSTING_SCHEDULE = {
        'governance_updates': {
            'interval': 3600,  # 1 hour
            'platforms': ['discord', 'telegram', 'twitter'],
            'agent': 'xmrt_dao_governor'
        },
        'defi_insights': {
            'interval': 1800,  # 30 minutes
            'platforms': ['discord', 'telegram', 'twitter'],
            'agent': 'xmrt_defi_specialist'
        },
        'community_updates': {
            'interval': 2700,  # 45 minutes
            'platforms': ['discord', 'telegram', 'twitter'],
            'agent': 'xmrt_community_manager'
        },
        'security_alerts': {
            'interval': 900,   # 15 minutes
            'platforms': ['discord', 'telegram'],
            'agent': 'xmrt_security_guardian'
        }
    }
    
    # Response Templates
    RESPONSE_TEMPLATES = {
        'greeting': {
            'discord': "👋 Welcome to the XMRT ecosystem! I'm {agent_name}, here to help with {specialization}.",
            'telegram': "🤖 Hello! I'm {agent_name}, your {specialization} assistant.",
            'twitter': "👋 Hi! I'm {agent_name} from @XMRTEcosystem, specializing in {specialization}."
        },
        'error': {
            'discord': "❌ I encountered an error processing your request. Please try again.",
            'telegram': "⚠️ Something went wrong. Please try again later.",
            'twitter': "❌ Error processing request. Please try again."
        },
        'maintenance': {
            'discord': "🔧 I'm currently undergoing maintenance. Please check back soon!",
            'telegram': "🛠 Maintenance in progress. Back soon!",
            'twitter': "🔧 Maintenance mode. Back soon!"
        }
    }
    
    # Rate Limiting
    RATE_LIMITS = {
        'discord': {
            'messages_per_minute': 30,
            'messages_per_hour': 1000
        },
        'telegram': {
            'messages_per_minute': 20,
            'messages_per_hour': 500
        },
        'twitter': {
            'tweets_per_hour': 50,
            'dms_per_hour': 100
        }
    }
    
    # Monitoring and Alerts
    MONITORING_CONFIG = {
        'health_check_interval': 300,  # 5 minutes
        'error_threshold': 10,  # Max errors before alert
        'response_time_threshold': 5000,  # 5 seconds
        'alert_channels': {
            'discord': os.environ.get('DISCORD_ALERT_CHANNEL'),
            'telegram': os.environ.get('TELEGRAM_ALERT_CHAT')
        }
    }
    
    @classmethod
    def get_platform_config(cls, platform: str) -> Dict[str, Any]:
        '''Get configuration for specific platform'''
        configs = {
            'discord': cls.DISCORD_CONFIG,
            'telegram': cls.TELEGRAM_CONFIG,
            'twitter': cls.TWITTER_CONFIG
        }
        return configs.get(platform, {})
    
    @classmethod
    def get_agent_platforms(cls, agent_id: str) -> List[str]:
        '''Get platforms where agent is active'''
        return cls.AGENT_PLATFORM_MAPPING.get(agent_id, [])
    
    @classmethod
    def get_posting_config(cls, post_type: str) -> Dict[str, Any]:
        '''Get posting configuration for specific type'''
        return cls.POSTING_SCHEDULE.get(post_type, {})
    
    @classmethod
    def is_platform_enabled(cls, platform: str) -> bool:
        '''Check if platform is enabled'''
        config = cls.get_platform_config(platform)
        return config.get('enabled', False)
    
    @classmethod
    def get_enabled_platforms(cls) -> List[str]:
        '''Get list of enabled platforms'''
        platforms = []
        for platform in ['discord', 'telegram', 'twitter']:
            if cls.is_platform_enabled(platform):
                platforms.append(platform)
        return platforms
