#!/usr/bin/env python3
"""
XMRT DAO Governance Agent
Autonomous governance operations for DAO
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json

logger = logging.getLogger(__name__)

class GovernanceAgent:
    """AI agent for autonomous governance operations"""

    def __init__(self, blockchain_utils, ai_utils):
        self.blockchain_utils = blockchain_utils
        self.ai_utils = ai_utils
        self.active = True
        self.last_check = None
        
        logger.info("Governance Agent initialized")

    async def check_proposals(self):
        """Check for new governance proposals"""
        try:
            logger.info("Checking governance proposals...")
            
            # Simulate proposal checking
            proposals = await self._fetch_proposals()
            
            for proposal in proposals:
                await self._analyze_proposal(proposal)
                
            self.last_check = datetime.now()
            return proposals
            
        except Exception as e:
            logger.error(f"Error checking proposals: {e}")
            return []

    async def analyze_sentiment(self):
        """Analyze community sentiment on proposals"""
        try:
            logger.info("Analyzing community sentiment...")
            
            # Simulate sentiment analysis
            sentiment_data = {
                'overall_sentiment': 'positive',
                'confidence': 0.75,
                'key_topics': ['treasury', 'governance', 'development'],
                'timestamp': datetime.now().isoformat()
            }
            
            return sentiment_data
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {}

    async def check_emergency_proposals(self):
        """Check for emergency proposals requiring immediate attention"""
        try:
            # Simulate emergency proposal check
            emergency_proposals = []
            
            # Check for time-sensitive proposals
            proposals = await self._fetch_proposals()
            for proposal in proposals:
                if proposal.get('priority') == 'emergency':
                    emergency_proposals.append(proposal)
                    
            return emergency_proposals
            
        except Exception as e:
            logger.error(f"Error checking emergency proposals: {e}")
            return []

    async def handle_emergency_proposal(self, proposal):
        """Handle emergency proposal with immediate action"""
        try:
            logger.warning(f"Handling emergency proposal: {proposal.get('id')}")
            
            # Analyze proposal urgency
            analysis = await self.ai_utils.analyze_proposal_urgency(proposal)
            
            # Take appropriate action based on analysis
            if analysis.get('requires_immediate_action'):
                await self._execute_emergency_response(proposal, analysis)
                
        except Exception as e:
            logger.error(f"Error handling emergency proposal: {e}")

    async def get_status(self):
        """Get current status of governance agent"""
        return {
            'active': self.active,
            'last_check': self.last_check.isoformat() if self.last_check else None,
            'agent_type': 'governance',
            'health': 'healthy'
        }

    def is_active(self):
        """Check if agent is active"""
        return self.active

    async def execute_action(self, action: str, params: Dict[str, Any]):
        """Execute a manual action"""
        try:
            if action == 'check_proposals':
                return await self.check_proposals()
            elif action == 'analyze_sentiment':
                return await self.analyze_sentiment()
            elif action == 'emergency_check':
                return await self.check_emergency_proposals()
            else:
                raise ValueError(f"Unknown action: {action}")
                
        except Exception as e:
            logger.error(f"Error executing action {action}: {e}")
            raise

    async def _fetch_proposals(self):
        """Fetch governance proposals from blockchain"""
        # Simulate proposal fetching
        return [
            {
                'id': 'prop_001',
                'title': 'Treasury Allocation Update',
                'status': 'active',
                'priority': 'normal',
                'votes_for': 150,
                'votes_against': 25,
                'end_time': (datetime.now() + timedelta(days=3)).isoformat()
            },
            {
                'id': 'prop_002', 
                'title': 'Emergency Security Patch',
                'status': 'active',
                'priority': 'emergency',
                'votes_for': 200,
                'votes_against': 5,
                'end_time': (datetime.now() + timedelta(hours=6)).isoformat()
            }
        ]

    async def _analyze_proposal(self, proposal):
        """Analyze individual proposal"""
        try:
            # Use AI to analyze proposal content and voting patterns
            analysis = await self.ai_utils.analyze_proposal(proposal)
            
            # Log analysis results
            logger.info(f"Proposal {proposal['id']} analysis: {analysis}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing proposal {proposal.get('id')}: {e}")
            return {}

    async def _execute_emergency_response(self, proposal, analysis):
        """Execute emergency response for critical proposals"""
        try:
            logger.critical(f"Executing emergency response for proposal {proposal['id']}")
            
            # Notify stakeholders
            await self._notify_stakeholders(proposal, analysis)
            
            # Execute automated voting if configured
            if analysis.get('auto_vote_recommended'):
                await self._execute_automated_vote(proposal, analysis)
                
        except Exception as e:
            logger.error(f"Error executing emergency response: {e}")

    async def _notify_stakeholders(self, proposal, analysis):
        """Notify key stakeholders about emergency proposal"""
        # Simulate stakeholder notification
        logger.info(f"Notifying stakeholders about emergency proposal {proposal['id']}")

    async def _execute_automated_vote(self, proposal, analysis):
        """Execute automated voting based on AI analysis"""
        # Simulate automated voting
        logger.info(f"Executing automated vote for proposal {proposal['id']}")

    async def run_cycle(self):
        """Execute a governance cycle - analyze proposals, update status, etc."""
        try:
            print(f"[{self.__class__.__name__}] Starting governance cycle...")
            
            # Use existing methods from your GovernanceAgent class
            await self.check_proposals()
            await self.analyze_sentiment()
            await self.check_emergency_proposals()
            
            print(f"[{self.__class__.__name__}] Governance cycle completed successfully")
            
        except Exception as e:
            print(f"[{self.__class__.__name__}] Error in governance cycle: {e}")
            # Don't re-raise - let the system continue with other agents


