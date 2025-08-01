"""
CentralAutonomousOrchestrator
The main brain that loads, initializes, and runs Eliza's sophisticated autonomous systems.
"""

import asyncio
import logging
from pathlib import Path
import sys

logger = logging.getLogger(__name__)

class CentralAutonomousOrchestrator:
    def __init__(self, ai_utils, blockchain_utils):
        self.ai_utils = ai_utils
        self.blockchain_utils = blockchain_utils
        self.active_systems = {}
        self.system_status = {}
        
        logger.info("[CentralOrchestrator] Initializing...")
        
        # Add necessary paths for imports from other parts of the monorepo
        # This is crucial for importing modules like advanced_eliza_orchestrator
        current_dir = Path(__file__).parent
        project_root = current_dir.parent.parent.parent # /backend/ai-automation-service/src -> /backend -> /
        
        sys.path.append(str(project_root)) # For advanced_eliza_orchestrator.py
        sys.path.append(str(project_root / 'backend' / 'xmrt-dao-backend' / 'src' / 'routes')) # For eliza.py
        sys.path.append(str(project_root / 'backend' / 'eliza-backend' / 'src')) # For external_tools_integration.py
        sys.path.append(str(current_dir)) # For other src modules
        
        
        
        logger.info("[CentralOrchestrator] Initialization scheduled.")
    async def initialize(self):
        """Perform asynchronous initialization of all systems."""
        logger.info("[CentralOrchestrator] Starting synchronous system initialization...")
        await self._initialize_systems()
        logger.info("[CentralOrchestrator] Asynchronous initialization complete.")

    async def _initialize_systems(self):
        """Asynchronously initialize all known sophisticated autonomous systems."""
        logger.info("[CentralOrchestrator] Starting asynchronous system initialization...")
        
        systems_to_load = [
            # Main Orchestrators
            ('EvolutionaryElizaOrchestrator', 'advanced_eliza_orchestrator', 'EvolutionaryElizaOrchestrator', None),
            ('UnifiedAutonomousSystem', 'src.unified_autonomous_system', 'UnifiedAutonomousSystem', None),
            ('AutonomousImprovement', 'src.autonomous_improvement_engine', 'AutonomousImprovement', None),
            
            # Other key agents/systems (ensure their __init__ matches)
            ('SelfImprovementAgent', 'src.agents.self_improvement_agent', 'SelfImprovementAgent', {'github_utils': None, 'ai_utils': self.ai_utils, 'terminal_utils': None, 'browser_utils': None}),
            ('EnhancedElizaAgent', 'eliza', 'EnhancedElizaAgent', None), # from backend/xmrt-dao-backend/src/routes/eliza.py
            ('WebBrowserAutomation', 'external_tools_integration', 'WebBrowserAutomation', None), # from backend/eliza-backend/src/external_tools_integration.py
            ('AutonomousElizaOS', 'src.autonomous_eliza', 'AutonomousElizaOS', None),
            ('AutonomousSystemLauncher', 'src.autonomous_system_launcher', 'AutonomousSystemLauncher', None),
            ('XMRTElizaMemoryManager', 'src.eliza_memory_integration', 'XMRTElizaMemoryManager', None),
            ('GitHubClientManager', 'src.enhanced_github_client', 'GitHubClientManager', None),
        ]
        
        # Placeholder for actual utility initializations for agents
        # These would ideally be passed down from main.py or instantiated here
        temp_github_utils = None # Replace with actual GitHubUtils instance
        temp_terminal_utils = None # Replace with actual TerminalUtils instance
        temp_browser_utils = None # Replace with actual BrowserUtils instance

        # Dynamically load and initialize systems
        for system_name, module_path, class_name, init_args in systems_to_load:
            try:
                # Use importlib to dynamically load the module
                module = __import__(module_path, fromlist=[class_name])
                SystemClass = getattr(module, class_name)
                
                # Handle specific initialization arguments if provided
                if init_args:
                    # Update placeholder utils with actual instances if available
                    if 'github_utils' in init_args and init_args['github_utils'] is None:
                        # Assuming a GitHubUtils class exists and can be initialized
                        from src.utils.github_utils import GitHubUtils # Assuming this path
                        temp_github_utils = temp_github_utils or GitHubUtils()
                        init_args['github_utils'] = temp_github_utils
                    if 'terminal_utils' in init_args and init_args['terminal_utils'] is None:
                        from src.utils.terminal_utils import TerminalUtils # Assuming this path
                        temp_terminal_utils = temp_terminal_utils or TerminalUtils()
                        init_args['terminal_utils'] = temp_terminal_utils
                    if 'browser_utils' in init_args and init_args['browser_utils'] is None:
                        from src.utils.browser_utils import BrowserUtils # Assuming this path
                        temp_browser_utils = temp_browser_utils or BrowserUtils()
                        init_args['browser_utils'] = temp_browser_utils

                    instance = SystemClass(**init_args)
                else:
                    instance = SystemClass() # Attempt default init
                
                self.active_systems[system_name] = instance
                self.system_status[system_name] = 'initialized'
                logger.info(f"[CentralOrchestrator] ✅ Loaded and initialized: {system_name}")
            except ImportError as ie:
                self.system_status[system_name] = 'import_error'
                logger.warning(f"[CentralOrchestrator] ⚠️ Import error for {system_name} ({module_path}.{class_name}): {ie}")
            except Exception as e:
                self.system_status[system_name] = 'init_error'
                logger.error(f"[CentralOrchestrator] ❌ Failed to initialize {system_name}: {e}")
        
        logger.info(f"[CentralOrchestrator] Finished system initialization. Active: {len(self.active_systems)} systems.")

    async def run_autonomous_cycle(self):
        """
        Execute a comprehensive autonomous cycle across all integrated systems.
        This method will be called by main.py
        """
        # Systems will be initialized externally by AIAutomationService.start_automation
        
        logger.info("[CentralOrchestrator] Starting comprehensive autonomous cycle...")
        
        tasks = []
        for system_name, system_instance in self.active_systems.items():
            # Prioritize specific run methods
            if hasattr(system_instance, 'run_autonomous_cycle'):
                tasks.append(self._run_system_task(system_name, system_instance.run_autonomous_cycle))
            elif hasattr(system_instance, 'execute_autonomous_cycle'):
                tasks.append(self._run_system_task(system_name, system_instance.execute_autonomous_cycle))
            elif hasattr(system_instance, 'run_improvement_cycle'):
                tasks.append(self._run_system_task(system_name, system_instance.run_improvement_cycle))
            elif hasattr(system_instance, 'launch_autonomous_operations'):
                tasks.append(self._run_system_task(system_name, system_instance.launch_autonomous_operations))
            elif hasattr(system_instance, 'run_cycle'): # For basic agents
                tasks.append(self._run_system_task(system_name, system_instance.run_cycle))
            else:
                logger.warning(f"[CentralOrchestrator] No known run method for {system_name}")
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        logger.info("[CentralOrchestrator] Comprehensive autonomous cycle completed.")
    
    async def _run_system_task(self, system_name, method):
        """Helper to run an individual system's method with error handling."""
        try:
            logger.info(f"[CentralOrchestrator] Running cycle for: {system_name}...")
            await method()
            logger.info(f"[CentralOrchestrator] ✅ {system_name} cycle completed.")
            self.system_status[system_name] = 'ran_successfully'
        except Exception as e:
            logger.error(f"[CentralOrchestrator] ❌ Error in {system_name} cycle: {e}")
            self.system_status[system_name] = 'runtime_error'
    
    def get_system_status(self):
        """Returns the current status of all managed autonomous systems."""
        return self.system_status

    # Add a method for chat routing to access specific capabilities
    async def process_chat_query(self, query: str) -> str:
        """
        Routes chat queries to the appropriate autonomous system or capability.
        This is where Eliza starts using her tools dynamically.
        """
        query_lower = query.lower()
        logger.info(f"[CentralOrchestrator] Processing chat query for tools: {query_lower[:50]}...")

        # Example: Direct routing to specific capabilities based on keywords
        if "github commit" in query_lower or "make commit" in query_lower:
            github_manager = self.active_systems.get('GitHubClientManager')
            if github_manager and hasattr(github_manager, 'commit_and_push'):
                try:
                    # This is a conceptual call; actual implementation needs careful design
                    # e.g., prompt for commit message, file list
                    # For now, just indicate it's trying to use the tool
                    logger.info("[CentralOrchestrator] Attempting to use GitHubClientManager for commit.")
                    # await github_manager.commit_and_push("Autonomous test commit")
                    return f"I can make GitHub commits. I'm initiating a process to prepare a commit for you. What changes should I commit and with what message?"
                except Exception as e:
                    return f"I tried to use my GitHub tools but encountered an error: {e}. Please check my logs."
            return "I have GitHub capabilities, but my direct commit function isn't fully integrated into this chat interface yet. I'm working on that!"

        elif "improve code" in query_lower or "self improve" in query_lower:
            improvement_agent = self.active_systems.get('AutonomousImprovement') or self.active_systems.get('SelfImprovementAgent')
            if improvement_agent and hasattr(improvement_agent, 'run_improvement_cycle'):
                logger.info("[CentralOrchestrator] Attempting to use AutonomousImprovement for self-improvement.")
                # await improvement_agent.run_improvement_cycle() # This would trigger a full cycle
                return "Yes, I can improve my own code! I'm constantly analyzing my performance and identifying areas for enhancement. Would you like me to focus on a specific aspect?"
            return "I have self-improvement capabilities, but the direct trigger from chat is still under development."

        # Fallback to general AI if no specific tool is matched
        return f"I understand you're asking about '{query}'. As the XMRT DAO's autonomous AI, I can help with a wide range of tasks related to governance, treasury management, tokenomics, and development. I'm also constantly improving myself!"


    def get_recent_commit_status(self):
        # TODO: Implement actual GitHub commit status fetch. For now, return placeholder.
        try:
            manager = self.active_systems.get('GitHubClientManager')
            if manager and hasattr(manager, 'get_last_commit_status'):
                return manager.get_last_commit_status()
        except Exception as ex:
            return f"Error fetching commit status: {ex}"
        return "No recent autonomous commits detected yet."

    def get_last_self_improvement_summary(self):
        try:
            agent = self.active_systems.get('SelfImprovementAgent')
            if agent and hasattr(agent, 'get_last_summary'):
                return agent.get_last_summary()
        except Exception as ex:
            return f"Error fetching self-improvement summary: {ex}"
        return "Self-improvement system is running but has not reported any completed improvements yet."

    def get_last_error_report(self):
        try:
            agent = self.active_systems.get('SelfImprovementAgent')
            if agent and hasattr(agent, 'get_last_errors'):
                return agent.get_last_errors()
        except Exception as ex:
            return f"Error fetching error report: {ex}"
        return "No error report found for last cycle."

    def list_available_tools(self):
        tools = []
        for name, system in self.active_systems.items():
            methods = [m for m in dir(system) if not m.startswith("_") and callable(getattr(system, m))]
            tools.append(f"{name}: {', '.join(methods[:10])}")  # Limit to 10 methods for brevity
        if tools:
            return "Active systems and top methods:
" + "
".join(tools)
        return "No tools or integrations are currently online."
    
