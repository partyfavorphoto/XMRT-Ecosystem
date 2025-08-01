import asyncio
import logging
from src.utils.blockchain_utils import BlockchainUtils
from src.utils.ai_utils import AIUtils
from src.agents.governance_agent import GovernanceAgent
from src.agents.treasury_agent import TreasuryAgent
from src.agents.community_agent import CommunityAgent

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
        """Start the main automation loop with REAL autonomous systems"""
        logger.info("🚀 AI Engine Starting: Beginning main automation loop...")
        
        while True:
            try:
                logger.info("--- Starting new agent cycle ---")
                
                # Run basic agent cycles (fixed)
                await asyncio.gather(
                    self.governance_agent.run_cycle(),
                    self.treasury_agent.run_cycle(),
                    self.community_agent.run_cycle()
                )
                
                # Run REAL autonomous systems
                await self.run_real_autonomous_systems()
                
                logger.info("--- Agent cycle complete. Sleeping for 60 seconds. ---")
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"FATAL ERROR in main agent cycle: {e}")
                await asyncio.sleep(10)  # Brief pause before retry
    
    async def run_real_autonomous_systems(self):
        """Run the REAL autonomous systems that were discovered"""
        try:
            logger.info("[RealAutonomous] Running discovered autonomous systems...")
            
            # Try to run EvolutionaryElizaOrchestrator
            try:
                import sys
                sys.path.append('.')
                sys.path.append('..')
                
                # Import the REAL EvolutionaryElizaOrchestrator
                from advanced_eliza_orchestrator import EvolutionaryElizaOrchestrator
                orchestrator = EvolutionaryElizaOrchestrator()
                
                # Check if it has autonomous methods
                if hasattr(orchestrator, 'run_autonomous_cycle'):
                    await orchestrator.run_autonomous_cycle()
                    logger.info("[RealAutonomous] EvolutionaryElizaOrchestrator cycle completed")
                elif hasattr(orchestrator, 'execute_evolutionary_cycle'):
                    await orchestrator.execute_evolutionary_cycle()
                    logger.info("[RealAutonomous] EvolutionaryElizaOrchestrator evolutionary cycle completed")
                else:
                    logger.warning("[RealAutonomous] EvolutionaryElizaOrchestrator has no known autonomous methods")
                    
            except Exception as e:
                logger.warning(f"[RealAutonomous] EvolutionaryElizaOrchestrator not available: {e}")
            
            # Try to run UnifiedAutonomousSystem
            try:
                from src.unified_autonomous_system import UnifiedAutonomousSystem
                unified_system = UnifiedAutonomousSystem()
                
                if hasattr(unified_system, 'execute_autonomous_cycle'):
                    await unified_system.execute_autonomous_cycle()
                    logger.info("[RealAutonomous] UnifiedAutonomousSystem cycle completed")
                elif hasattr(unified_system, 'run_unified_operations'):
                    await unified_system.run_unified_operations()
                    logger.info("[RealAutonomous] UnifiedAutonomousSystem operations completed")
                    
            except Exception as e:
                logger.warning(f"[RealAutonomous] UnifiedAutonomousSystem not available: {e}")
            
            # Try to run AutonomousImprovement
            try:
                from src.autonomous_improvement_engine import AutonomousImprovement
                improvement_engine = AutonomousImprovement()
                
                if hasattr(improvement_engine, 'run_improvement_cycle'):
                    await improvement_engine.run_improvement_cycle()
                    logger.info("[RealAutonomous] AutonomousImprovement cycle completed")
                    
            except Exception as e:
                logger.warning(f"[RealAutonomous] AutonomousImprovement not available: {e}")
            
            logger.info("[RealAutonomous] Real autonomous systems cycle completed")
            
        except Exception as e:
            logger.error(f"[RealAutonomous] Error running real autonomous systems: {e}")