# main.py - The Core Autonomous Agent Service
# This file contains the "engine" of Eliza's AI operations.
# It is started as a background task by launcher.py.

import asyncio
import logging
import os
import sys
import time
from datetime import datetime
from typing import Dict, Any

# The 'schedule' library is removed as it's not compatible with a modern asyncio event loop.
# We will use pure asyncio for more robust and predictable task execution.

from web3 import Web3
import openai
from dotenv import load_dotenv

# --- Setup ---
# This ensures that your agent and util files can be found
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
load_dotenv()

# We assume these are your correct import paths
from agents.governance_agent import GovernanceAgent
from agents.treasury_agent import TreasuryAgent
from agents.community_agent import CommunityAgent
from utils.blockchain_utils import BlockchainUtils
from utils.ai_utils import AIUtils

# --- Logging and API Key Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()] # Log directly to the console for Render to capture
)
logger = logging.getLogger(__name__)

# --- FIX for OpenAI Key ---
# Explicitly load the API key from environment variables.
# This ensures your key is loaded correctly in Render's environment.
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    logger.error("CRITICAL: OPENAI_API_KEY environment variable not found! AI features will fail.")

class AIAutomationService:
    """
    This class orchestrates all the autonomous AI agents.
    It's the heart of your application's logic.
    """
    def __init__(self):
        self.blockchain_utils = BlockchainUtils()
        self.ai_utils = AIUtils()
        self.governance_agent = GovernanceAgent(self.blockchain_utils, self.ai_utils)
        self.treasury_agent = TreasuryAgent(self.blockchain_utils, self.ai_utils)
        self.community_agent = CommunityAgent(self.blockchain_utils, self.ai_utils)
        self.running = False
        logger.info("AIAutomationService engine initialized and ready.")

    async def start_automation(self):
        """Starts the main automation loop using pure asyncio."""
        logger.info("🚀 AI Engine Starting: Beginning main automation loop...")
        self.running = True
        self.start_time = time.time()

        while self.running:
            try:
                logger.info("--- Starting new agent cycle ---")
                # This runs all your agent tasks concurrently, which is highly efficient.
                await asyncio.gather(
                    self.governance_agent.run_cycle(),
                    self.treasury_agent.run_cycle(),
                    self.community_agent.run_cycle()
                )
                logger.info("--- Agent cycle complete. Sleeping for 60 seconds. ---")
                await asyncio.sleep(60)

            except Exception as e:
                logger.error(f"FATAL ERROR in main agent cycle: {e}", exc_info=True)
                await asyncio.sleep(120) # Wait longer after a major error to allow for recovery

    # --- Your other methods remain here ---
    def stop_automation(self):
        logger.info("🛑 Stopping AI Automation Service...")
        self.running = False

    def enable_automation(self):
        # ... your existing code ...

    def disable_automation(self):
        # ... your existing code ...

    async def execute_manual_action(self, agent_name: str, action: str, params: Dict[str, Any]):
        # ... your existing code ...

    def get_system_status(self):
        # ... your existing code ...

# We have removed the `if __name__ == '__main__':` block.
# This is because main.py is no longer the script you run directly.
# It's now a module that launcher.py imports and uses.
