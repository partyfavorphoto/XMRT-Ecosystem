import asyncio
import logging
from utils.blockchain_utils import BlockchainUtils
from utils.ai_utils import AIUtils
from agents.governance_agent import GovernanceAgent
from agents.treasury_agent import TreasuryAgent
from agents.community_agent import CommunityAgent

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
        
        logger.info("AIAutomationService engine initialized and ready.")
    
    async def start_automation(self):
        """Start the main automation loop"""
        logger.info("🚀 AI Engine Starting: Beginning main automation loop...")
        
        while True:
            try:
                logger.info("--- Starting new agent cycle ---")
                
                # Run all agent cycles
                await asyncio.gather(
                    self.governance_agent.run_cycle(),
                    self.treasury_agent.run_cycle(),
                    self.community_agent.run_cycle()
                )
                
                # Run existing autonomous systems
                await self.run_existing_autonomous_systems()
                
                logger.info("--- Agent cycle complete. Sleeping for 60 seconds. ---")
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"FATAL ERROR in main agent cycle: {e}")
                await asyncio.sleep(10)  # Brief pause before retry
    
    async def run_existing_autonomous_systems(self):
        """Run Eliza's existing autonomous systems"""
        try:
            logger.info("[Main] Running existing autonomous systems...")
            
            # Try to run EvolutionaryElizaOrchestrator if available
            try:
                import sys
                sys.path.append('.')
                sys.path.append('..')
                from advanced_eliza_orchestrator import EvolutionaryElizaOrchestrator
                orchestrator = EvolutionaryElizaOrchestrator()
                if hasattr(orchestrator, 'run_autonomous_cycle'):
                    await orchestrator.run_autonomous_cycle()
                    logger.info("[Main] EvolutionaryElizaOrchestrator cycle completed")
            except Exception as e:
                logger.warning(f"[Main] EvolutionaryElizaOrchestrator not available: {e}")
            
            # Try to run UnifiedAutonomousSystem if available
            try:
                from src.unified_autonomous_system import UnifiedAutonomousSystem
                unified_system = UnifiedAutonomousSystem()
                if hasattr(unified_system, 'execute_autonomous_cycle'):
                    await unified_system.execute_autonomous_cycle()
                    logger.info("[Main] UnifiedAutonomousSystem cycle completed")
            except Exception as e:
                logger.warning(f"[Main] UnifiedAutonomousSystem not available: {e}")
            
            logger.info("[Main] Existing autonomous systems cycle completed")
            
        except Exception as e:
            logger.error(f"[Main] Error running existing autonomous systems: {e}")

# Create global instance
automation_service = AIAutomationService()
