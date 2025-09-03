"""
XMRT-Ecosystem Slack Integration Main Module

This is the main entry point for the complete Slack integration system.
It orchestrates all components and provides a simple API for integration.
"""

import asyncio
import logging
import os
import sys
from typing import Dict, Any, Optional
from pathlib import Path

# Add current directory to Python path for imports
sys.path.append(str(Path(__file__).parent))

from slack_integration import SlackIntegration, get_default_config
from multi_agent_slack_bridge import MultiAgentSlackBridge
from enhanced_autonomous_controller import EnhancedAutonomousController

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class XMRTSlackOrchestrator:
    """
    Main orchestrator for XMRT-Ecosystem Slack integration

    This class manages all Slack integration components:
    - Core Slack bot functionality
    - Multi-agent communication bridge
    - Enhanced autonomous controller
    - System health monitoring
    """

    def __init__(self, config_file: Optional[str] = None):
        """Initialize the Slack orchestrator"""
        self.config = self._load_config(config_file)
        self.slack_integration = None
        self.agent_bridge = None
        self.enhanced_controller = None
        self.is_running = False

        logger.info("🎼 XMRT Slack Orchestrator initialized")

    def _load_config(self, config_file: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from environment or file"""
        config = {}

        # Load from environment variables
        for key in os.environ:
            if any(key.startswith(prefix) for prefix in ['SLACK_', 'OPENAI_', 'GOOGLE_', 'GITHUB_', 'SUPABASE_']):
                config[key] = os.environ[key]

        # Add default values for missing Slack configs
        slack_defaults = get_default_config()
        for key, value in slack_defaults.items():
            if key not in config:
                config[key] = value

        # Add other required configs with defaults
        config.setdefault('FLASK_ENV', 'production')
        config.setdefault('SECRET_KEY', 'your-secret-key-here')

        logger.info(f"📋 Configuration loaded with {len(config)} variables")
        return config

    async def start_all_systems(self):
        """Start all Slack integration systems"""
        try:
            logger.info("🚀 Starting all XMRT Slack integration systems...")

            # 1. Initialize core Slack integration
            logger.info("1️⃣ Starting core Slack integration...")
            self.slack_integration = SlackIntegration(self.config)
            await self.slack_integration.start()

            # 2. Initialize multi-agent bridge
            logger.info("2️⃣ Starting multi-agent Slack bridge...")
            self.agent_bridge = MultiAgentSlackBridge(self.slack_integration)
            await self.agent_bridge.start()

            # 3. Initialize enhanced autonomous controller
            logger.info("3️⃣ Starting enhanced autonomous controller...")
            self.enhanced_controller = EnhancedAutonomousController(self.config)
            await self.enhanced_controller._initialize_systems()

            # Connect systems together
            if hasattr(self.enhanced_controller, 'agent_bridge') and self.agent_bridge:
                self.enhanced_controller.agent_bridge = self.agent_bridge
            if hasattr(self.enhanced_controller, 'slack_integration') and self.slack_integration:
                self.enhanced_controller.slack_integration = self.slack_integration

            # 4. Start autonomous learning
            logger.info("4️⃣ Starting autonomous learning system...")
            await self.enhanced_controller.start_autonomous_learning()

            self.is_running = True

            # Send comprehensive startup notification
            await self._send_startup_notification()

            logger.info("✅ All XMRT Slack integration systems started successfully!")

        except Exception as e:
            logger.error(f"❌ Failed to start XMRT Slack systems: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise

    async def stop_all_systems(self):
        """Stop all Slack integration systems"""
        try:
            logger.info("🛑 Stopping all XMRT Slack integration systems...")

            # Stop in reverse order
            if self.enhanced_controller:
                await self.enhanced_controller.stop_autonomous_learning()

            if self.agent_bridge:
                await self.agent_bridge.stop()

            if self.slack_integration:
                await self.slack_integration.stop()

            self.is_running = False

            logger.info("✅ All XMRT Slack integration systems stopped")

        except Exception as e:
            logger.error(f"❌ Error stopping XMRT Slack systems: {e}")

    async def _send_startup_notification(self):
        """Send comprehensive startup notification to Slack"""
        if self.slack_integration:

            startup_message = """
🚀 **XMRT-Ecosystem Slack Integration Fully Online**

All systems are now connected and operational:

🔗 **Core Slack Integration**
• Bot commands active (`/xmrt-status`, `/xmrt-agents`, etc.)
• Real-time notifications enabled
• Interactive command processing

🤖 **Multi-Agent Bridge**  
• 4 AI agents connected to Slack
• Real-time collaboration visibility
• Agent status updates and notifications

🎓 **Enhanced Autonomous Controller**
• Hourly learning cycles with Slack notifications
• GitHub operation alerts
• System health monitoring

🔧 **Available Commands:**
• `/xmrt-status` - System status
• `/xmrt-agents` - AI agents info
• `/xmrt-learning` - Learning cycles
• `/xmrt-trigger learning` - Start learning cycle
• `/xmrt-github` - GitHub operations

The XMRT autonomous learning ecosystem is now fully integrated with Slack! 🎉
            """

            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🚀 XMRT-Ecosystem Slack Integration Online"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": startup_message
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "🎯 *Ready for autonomous learning and collaboration!*"
                    }
                }
            ]

            from slack_integration import SlackMessage
            message = SlackMessage(
                channel=self.slack_integration.channels['general'],
                text="🚀 XMRT-Ecosystem Slack Integration Online",
                blocks=blocks,
                message_type='system'
            )

            await self.slack_integration.send_message(message)

    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        status = {
            'orchestrator_running': self.is_running,
            'timestamp': asyncio.get_event_loop().time(),
            'systems': {}
        }

        if self.slack_integration:
            status['systems']['slack_integration'] = {
                'running': self.slack_integration.is_running,
                'stats': self.slack_integration.stats
            }

        if self.agent_bridge:
            status['systems']['agent_bridge'] = {
                'running': self.agent_bridge.is_running,
                'stats': self.agent_bridge.get_stats()
            }

        if self.enhanced_controller:
            status['systems']['enhanced_controller'] = self.enhanced_controller.get_status()

        return status

# Convenience functions for easy integration

async def start_xmrt_slack_integration(config_file: Optional[str] = None) -> XMRTSlackOrchestrator:
    """Start the complete XMRT Slack integration"""
    orchestrator = XMRTSlackOrchestrator(config_file)
    await orchestrator.start_all_systems()
    return orchestrator

async def main():
    """Main entry point for standalone execution"""
    logger.info("🎯 Starting XMRT-Ecosystem Slack Integration...")

    try:
        # Check for required environment variables
        required_vars = ['SLACK_BOT_TOKEN', 'SLACK_APP_TOKEN', 'SLACK_SIGNING_SECRET']
        missing_vars = [var for var in required_vars if not os.getenv(var) or os.getenv(var) == f'{var.lower().replace("_", "-")}-your-token-here']

        if missing_vars:
            logger.error(f"❌ Missing required environment variables: {missing_vars}")
            logger.error("Please set up your Slack app credentials in the environment or .env file")
            return

        # Start the integration
        orchestrator = await start_xmrt_slack_integration()

        # Keep running
        logger.info("🔄 XMRT Slack Integration running... Press Ctrl+C to stop")
        try:
            while True:
                await asyncio.sleep(60)  # Check every minute
                if not orchestrator.is_running:
                    break
        except KeyboardInterrupt:
            logger.info("⚡ Keyboard interrupt received")

        # Cleanup
        await orchestrator.stop_all_systems()
        logger.info("👋 XMRT Slack Integration stopped")

    except Exception as e:
        logger.error(f"💥 Critical error in XMRT Slack Integration: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(main())
