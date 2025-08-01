import asyncio
import logging
from src.utils.blockchain_utils import BlockchainUtils
from src.utils.ai_utils import AIUtils
from src.agents.governance_agent import GovernanceAgent
from src.agents.treasury_agent import TreasuryAgent
from src.agents.community_agent import CommunityAgent
from src.central_autonomous_orchestrator import CentralAutonomousOrchestrator

logger = logging.getLogger(__name__)

class AIAutomationService:
    def __init__(self):
        logger.info("Initializing AI Automation Service...")
        
        # Initialize utilities
        blockchain_utils = BlockchainUtils()
        ai_utils = AIUtils()
        
        # Initialize agents
        self.governance_agent = GovernanceAgent(blockchain_utils, ai_utils)
        self.treasury_agent = TreasuryAgent(blockchain_utils, ai_utils)
        self.community_agent = CommunityAgent(blockchain_utils, ai_utils)
        # Initialize Central Autonomous Orchestrator
        self.central_orchestrator = CentralAutonomousOrchestrator(ai_utils, blockchain_utils)
        
        logger.info("AIAutomationService engine initialized and ready.")
    
    async def start_automation(self):
        """Start the main automation loop"""
        logger.info("🚀 AI Engine Starting: Beginning main automation loop...")
        
        while True:
            try:
                logger.info("--- Starting new agent cycle ---")
                
                # Run all agent cycles in parallel
                # Run comprehensive autonomous cycle using the Central Orchestrator
                await self.central_orchestrator.run_autonomous_cycle()
                
                logger.info("--- Agent cycle complete. Sleeping for 60 seconds. ---")
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"FATAL ERROR in main agent cycle: {e}")
                await asyncio.sleep(10)

# Create global instance for launcher
automation_service = AIAutomationService()
