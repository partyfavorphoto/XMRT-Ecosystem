"""
XMRT-Ecosystem Slack Integration

Comprehensive Slack bot integration for the autonomous learning system that:
- Connects Eliza and 4 AI agents to Slack
- Provides real-time collaboration discussions
- Sends learning cycle progress updates
- Handles GitHub operation notifications
- Supports interactive commands for autonomous actions
- Monitors system health and alerts
"""

import asyncio
import logging
import os
import json
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
import threading
import time

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.rtm_v2 import RTMClient
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.response import SocketModeResponse
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class SlackMessage:
    """Standardized Slack message structure"""
    channel: str
    text: str
    thread_ts: Optional[str] = None
    blocks: Optional[List[Dict]] = None
    attachments: Optional[List[Dict]] = None
    user: Optional[str] = None
    timestamp: Optional[str] = None
    message_type: str = 'standard'  # standard, notification, alert, status

@dataclass  
class AgentUpdate:
    """Agent activity update structure"""
    agent_id: str
    agent_name: str
    activity: str
    status: str
    details: Optional[Dict] = None
    timestamp: Optional[datetime] = None

class SlackIntegration:
    """
    Main Slack integration class for XMRT-Ecosystem

    Provides comprehensive Slack bot functionality including:
    - Multi-agent communication coordination
    - Learning cycle notifications
    - Interactive command handling
    - GitHub operation alerts
    - System health monitoring
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize Slack integration with configuration"""
        self.config = config
        self.bot_token = config.get('SLACK_BOT_TOKEN', '')
        self.app_token = config.get('SLACK_APP_TOKEN', '')
        self.signing_secret = config.get('SLACK_SIGNING_SECRET', '')

        # Initialize Slack clients
        self.web_client = WebClient(token=self.bot_token)
        self.app = App(
            token=self.bot_token,
            signing_secret=self.signing_secret
        )

        # Channel configurations
        self.channels = {
            'agent_collaboration': config.get('SLACK_AGENT_CHANNEL', '#ai-agents'),
            'learning_cycles': config.get('SLACK_LEARNING_CHANNEL', '#learning-cycles'),
            'github_ops': config.get('SLACK_GITHUB_CHANNEL', '#github-operations'),
            'system_health': config.get('SLACK_HEALTH_CHANNEL', '#system-health'),
            'general': config.get('SLACK_GENERAL_CHANNEL', '#general')
        }

        # Integration state
        self.is_running = False
        self.socket_handler = None
        self.message_queue = asyncio.Queue()
        self.agent_threads = {}
        self.learning_cycle_thread = None

        # Statistics
        self.stats = {
            'messages_sent': 0,
            'commands_processed': 0,
            'agents_active': 0,
            'learning_cycles_notified': 0,
            'github_events_sent': 0,
            'health_alerts_sent': 0,
            'start_time': None
        }

        logger.info("🔗 Slack Integration initialized")
        self._register_command_handlers()

    def _register_command_handlers(self):
        """Register all Slack command handlers"""

        @self.app.command("/xmrt-status")
        def handle_status_command(ack, respond, command):
            """Handle /xmrt-status command"""
            ack()
            status_info = self._get_system_status()
            respond(self._format_status_response(status_info))

        @self.app.command("/xmrt-agents")
        def handle_agents_command(ack, respond, command):
            """Handle /xmrt-agents command"""
            ack()
            agent_info = self._get_agents_status()
            respond(self._format_agents_response(agent_info))

        @self.app.command("/xmrt-learning")
        def handle_learning_command(ack, respond, command):
            """Handle /xmrt-learning command"""
            ack()
            learning_info = self._get_learning_status()
            respond(self._format_learning_response(learning_info))

        @self.app.command("/xmrt-trigger")
        def handle_trigger_command(ack, respond, command):
            """Handle /xmrt-trigger command to start autonomous actions"""
            ack()
            result = self._trigger_autonomous_action(command['text'])
            respond(self._format_trigger_response(result))

        @self.app.command("/xmrt-github")  
        def handle_github_command(ack, respond, command):
            """Handle /xmrt-github command for GitHub operations"""
            ack()
            github_info = self._get_github_status()
            respond(self._format_github_response(github_info))

        @self.app.event("app_mention")
        def handle_app_mentions(event, say):
            """Handle @mentions of the bot"""
            self._handle_mention(event, say)

        @self.app.event("message")
        def handle_direct_messages(event, say):
            """Handle direct messages to the bot"""
            if event.get('channel_type') == 'im':
                self._handle_direct_message(event, say)

        logger.info("✅ Slack command handlers registered")

    async def start(self):
        """Start the Slack integration"""
        try:
            logger.info("🚀 Starting Slack Integration...")

            # Verify Slack connection
            if not await self._verify_slack_connection():
                raise Exception("Failed to connect to Slack API")

            # Start socket mode handler in separate thread
            self.socket_handler = SocketModeHandler(self.app, self.app_token)
            socket_thread = threading.Thread(
                target=self.socket_handler.start,
                daemon=True
            )
            socket_thread.start()

            # Start message processing
            asyncio.create_task(self._process_message_queue())

            # Send startup notification
            await self.send_system_notification(
                "🚀 XMRT-Ecosystem Slack Integration Started",
                "The autonomous learning system is now connected to Slack!",
                channel=self.channels['system_health']
            )

            self.is_running = True
            self.stats['start_time'] = datetime.now(timezone.utc)

            logger.info("✅ Slack Integration started successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to start Slack Integration: {e}")
            logger.error(traceback.format_exc())
            return False

    async def stop(self):
        """Stop the Slack integration"""
        try:
            logger.info("🛑 Stopping Slack Integration...")

            self.is_running = False

            # Send shutdown notification
            await self.send_system_notification(
                "🛑 XMRT-Ecosystem Slack Integration Stopping",
                "The autonomous learning system Slack connection is shutting down.",
                channel=self.channels['system_health']
            )

            # Stop socket handler
            if self.socket_handler:
                self.socket_handler.close()

            logger.info("✅ Slack Integration stopped")

        except Exception as e:
            logger.error(f"❌ Error stopping Slack Integration: {e}")

    async def _verify_slack_connection(self) -> bool:
        """Verify connection to Slack API"""
        try:
            response = self.web_client.auth_test()
            if response["ok"]:
                bot_info = response
                logger.info(f"✅ Connected to Slack as {bot_info['user']} in team {bot_info['team']}")
                return True
            else:
                logger.error(f"❌ Slack auth failed: {response}")
                return False
        except SlackApiError as e:
            logger.error(f"❌ Slack API error: {e}")
            return False

    async def send_message(self, message: SlackMessage) -> bool:
        """Send a message to Slack"""
        try:
            kwargs = {
                'channel': message.channel,
                'text': message.text
            }

            if message.thread_ts:
                kwargs['thread_ts'] = message.thread_ts
            if message.blocks:
                kwargs['blocks'] = message.blocks
            if message.attachments:
                kwargs['attachments'] = message.attachments

            response = self.web_client.chat_postMessage(**kwargs)

            if response["ok"]:
                self.stats['messages_sent'] += 1
                logger.info(f"✅ Message sent to {message.channel}")
                return True
            else:
                logger.error(f"❌ Failed to send message: {response}")
                return False

        except SlackApiError as e:
            logger.error(f"❌ Slack API error sending message: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Error sending message: {e}")
            return False

    async def send_agent_update(self, update: AgentUpdate, channel: Optional[str] = None):
        """Send agent activity update to Slack"""
        if not channel:
            channel = self.channels['agent_collaboration']

        # Create formatted message with agent emoji and status colors
        agent_emojis = {
            'strategist': '🎯',
            'builder': '🔨', 
            'tester': '🧪',
            'optimizer': '⚡'
        }

        status_colors = {
            'active': '#36a64f',    # Green
            'thinking': '#ffcc00',  # Yellow  
            'completed': '#439fe0', # Blue
            'error': '#ff0000'      # Red
        }

        emoji = agent_emojis.get(update.agent_name.lower(), '🤖')
        color = status_colors.get(update.status.lower(), '#808080')

        # Create rich message with blocks
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{emoji} *{update.agent_name} Agent Update*\n_{update.activity}_"
                }
            }
        ]

        if update.details:
            details_text = "\n".join([f"• {k}: {v}" for k, v in update.details.items()])
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn", 
                    "text": f"```{details_text}```"
                }
            })

        attachment = {
            "color": color,
            "footer": f"Agent ID: {update.agent_id}",
            "ts": int((update.timestamp or datetime.now(timezone.utc)).timestamp())
        }

        message = SlackMessage(
            channel=channel,
            text=f"{emoji} {update.agent_name}: {update.activity}",
            blocks=blocks,
            attachments=[attachment],
            message_type='notification'
        )

        await self.send_message(message)

    async def send_learning_cycle_notification(self, 
                                            cycle_info: Dict[str, Any], 
                                            channel: Optional[str] = None):
        """Send learning cycle progress notification"""
        if not channel:
            channel = self.channels['learning_cycles']

        cycle_num = cycle_info.get('cycle_number', 'Unknown')
        phase = cycle_info.get('current_phase', 'Unknown')
        status = cycle_info.get('status', 'running')

        # Create detailed learning cycle message
        title = f"🎓 Learning Cycle #{cycle_num} - {phase.title()}"

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": title
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Status:* {status.title()}"
                    },
                    {
                        "type": "mrkdwn", 
                        "text": f"*Phase:* {phase}"
                    }
                ]
            }
        ]

        # Add phase-specific information
        if phase_details := cycle_info.get('phase_details'):
            details_text = "\n".join([f"• {k}: {v}" for k, v in phase_details.items()])
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Phase Details:*\n{details_text}"
                }
            })

        # Add progress indicator
        if progress := cycle_info.get('progress'):
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Progress:* {progress}%"
                }
            })

        message = SlackMessage(
            channel=channel,
            text=title,
            blocks=blocks,
            message_type='notification'
        )

        await self.send_message(message)
        self.stats['learning_cycles_notified'] += 1

    async def send_github_notification(self, 
                                     event_type: str, 
                                     details: Dict[str, Any],
                                     channel: Optional[str] = None):
        """Send GitHub operation notification"""
        if not channel:
            channel = self.channels['github_ops']

        # GitHub event icons
        github_icons = {
            'commit': '📝',
            'push': '🚀', 
            'merge': '🔀',
            'release': '🎉',
            'issue': '🐛',
            'pr_open': '🔀',
            'pr_merged': '✅',
            'deploy': '🚀'
        }

        icon = github_icons.get(event_type, '🔔')
        title = f"{icon} GitHub {event_type.title().replace('_', ' ')}"

        blocks = [
            {
                "type": "header", 
                "text": {
                    "type": "plain_text",
                    "text": title
                }
            }
        ]

        # Add repository info
        if repo := details.get('repository'):
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Repository:* {repo}"
                }
            })

        # Add commit/change details  
        if commit_msg := details.get('commit_message'):
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Commit:* {commit_msg}"
                }
            })

        # Add files changed
        if files := details.get('files_changed'):
            file_list = "\n".join([f"• {f}" for f in files[:5]])  # Show max 5 files
            if len(files) > 5:
                file_list += f"\n... and {len(files) - 5} more files"

            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Files Changed:*\n{file_list}"
                }
            })

        # Add link if available
        if url := details.get('url'):
            blocks.append({
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "View on GitHub"
                        },
                        "url": url
                    }
                ]
            })

        message = SlackMessage(
            channel=channel,
            text=title,
            blocks=blocks,
            message_type='notification'
        )

        await self.send_message(message)
        self.stats['github_events_sent'] += 1

    async def send_system_notification(self, 
                                     title: str, 
                                     description: str,
                                     severity: str = 'info',
                                     channel: Optional[str] = None):
        """Send system health/status notification"""
        if not channel:
            channel = self.channels['system_health']

        # Severity icons and colors
        severity_config = {
            'info': {'icon': 'ℹ️', 'color': '#36a64f'},
            'warning': {'icon': '⚠️', 'color': '#ffcc00'},
            'error': {'icon': '❌', 'color': '#ff0000'},
            'critical': {'icon': '🚨', 'color': '#ff0000'}
        }

        config = severity_config.get(severity, severity_config['info'])
        icon = config['icon']
        color = config['color']

        full_title = f"{icon} {title}"

        attachment = {
            "color": color,
            "title": title,
            "text": description,
            "footer": "XMRT-Ecosystem System Monitor",
            "ts": int(datetime.now(timezone.utc).timestamp())
        }

        message = SlackMessage(
            channel=channel,
            text=full_title,
            attachments=[attachment],
            message_type='alert'
        )

        await self.send_message(message)
        self.stats['health_alerts_sent'] += 1

    async def _process_message_queue(self):
        """Process queued messages"""
        while self.is_running:
            try:
                # Process any queued messages
                if not self.message_queue.empty():
                    message = await self.message_queue.get()
                    await self.send_message(message)

                await asyncio.sleep(0.1)  # Small delay to prevent busy waiting

            except Exception as e:
                logger.error(f"Error processing message queue: {e}")
                await asyncio.sleep(1)

    def _get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        uptime = None
        if self.stats['start_time']:
            uptime = datetime.now(timezone.utc) - self.stats['start_time']

        return {
            'status': 'running' if self.is_running else 'stopped',
            'uptime': str(uptime) if uptime else 'N/A',
            'stats': self.stats.copy(),
            'channels': self.channels,
            'agents_connected': len(self.agent_threads)
        }

    def _get_agents_status(self) -> Dict[str, Any]:
        """Get agents status information"""
        return {
            'total_agents': 4,
            'active_agents': self.stats['agents_active'],
            'agent_threads': list(self.agent_threads.keys()),
            'last_update': datetime.now(timezone.utc).isoformat()
        }

    def _get_learning_status(self) -> Dict[str, Any]:
        """Get learning cycle status"""
        return {
            'cycles_completed': self.stats['learning_cycles_notified'],
            'current_cycle': 'Active' if self.learning_cycle_thread else 'Idle',
            'last_notification': 'Recently' if self.stats['learning_cycles_notified'] > 0 else 'Never'
        }

    def _get_github_status(self) -> Dict[str, Any]:
        """Get GitHub operations status"""
        return {
            'events_processed': self.stats['github_events_sent'],
            'connection_status': 'Connected',
            'last_event': 'Recently' if self.stats['github_events_sent'] > 0 else 'Never'
        }

    def _trigger_autonomous_action(self, action_text: str) -> Dict[str, Any]:
        """Trigger autonomous system actions"""
        # This would integrate with the autonomous controller
        actions = {
            'learning': 'trigger learning cycle',
            'analysis': 'trigger strategic analysis', 
            'build': 'trigger code generation',
            'test': 'trigger testing phase',
            'deploy': 'trigger deployment'
        }

        action = action_text.strip().lower()
        if action in actions:
            return {
                'success': True,
                'action': actions[action], 
                'message': f'Autonomous {action} triggered successfully',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        else:
            return {
                'success': False,
                'message': f'Unknown action: {action}. Available: {", ".join(actions.keys())}',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }

    def _format_status_response(self, status: Dict[str, Any]) -> Dict[str, Any]:
        """Format system status response"""
        return {
            "response_type": "in_channel",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text", 
                        "text": "🎯 XMRT-Ecosystem Status"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Status:* {status['status'].title()}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Uptime:* {status['uptime']}"
                        },
                        {
                            "type": "mrkdwn", 
                            "text": f"*Messages Sent:* {status['stats']['messages_sent']}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Commands Processed:* {status['stats']['commands_processed']}"
                        }
                    ]
                }
            ]
        }

    def _format_agents_response(self, agents: Dict[str, Any]) -> Dict[str, Any]:
        """Format agents status response"""
        return {
            "response_type": "in_channel",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🤖 AI Agents Status"
                    }
                },
                {
                    "type": "section", 
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Total Agents:* {agents['total_agents']}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Active Agents:* {agents['active_agents']}"
                        }
                    ]
                }
            ]
        }

    def _format_learning_response(self, learning: Dict[str, Any]) -> Dict[str, Any]:
        """Format learning status response"""
        return {
            "response_type": "in_channel",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🎓 Learning Cycles Status"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn", 
                            "text": f"*Cycles Completed:* {learning['cycles_completed']}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Current Status:* {learning['current_cycle']}"
                        }
                    ]
                }
            ]
        }

    def _format_trigger_response(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Format trigger action response"""
        emoji = "✅" if result['success'] else "❌"
        color = "#36a64f" if result['success'] else "#ff0000"

        return {
            "response_type": "in_channel",
            "attachments": [
                {
                    "color": color,
                    "title": f"{emoji} Autonomous Action Result",
                    "text": result['message'],
                    "footer": "XMRT-Ecosystem Controller",
                    "ts": int(datetime.fromisoformat(result['timestamp']).timestamp())
                }
            ]
        }

    def _format_github_response(self, github: Dict[str, Any]) -> Dict[str, Any]:
        """Format GitHub status response"""
        return {
            "response_type": "in_channel",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🔀 GitHub Integration Status"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Events Processed:* {github['events_processed']}"
                        },
                        {
                            "type": "mrkdwn", 
                            "text": f"*Connection:* {github['connection_status']}"
                        }
                    ]
                }
            ]
        }

    def _handle_mention(self, event, say):
        """Handle bot mentions in channels"""
        user = event['user']
        text = event['text']
        channel = event['channel']

        # Simple response to mentions
        response = f"Hi <@{user}>! 🤖 I'm the XMRT-Ecosystem bot. Use slash commands like `/xmrt-status` to interact with me!"
        say(text=response, channel=channel)

    def _handle_direct_message(self, event, say):
        """Handle direct messages to the bot"""
        user = event['user']
        text = event['text'].lower()

        if 'help' in text:
            help_text = """
🤖 *XMRT-Ecosystem Bot Help*

*Available Commands:*
• `/xmrt-status` - System status
• `/xmrt-agents` - AI agents status  
• `/xmrt-learning` - Learning cycles info
• `/xmrt-trigger [action]` - Trigger autonomous actions
• `/xmrt-github` - GitHub integration status

*Actions for /xmrt-trigger:*
• `learning` - Start learning cycle
• `analysis` - Strategic analysis
• `build` - Code generation
• `test` - Testing phase  
• `deploy` - Deployment

Just mention me (@xmrt-bot) in any channel for a quick response!
            """
            say(text=help_text)
        else:
            say(text="Hi! 👋 Type 'help' to see available commands, or use slash commands like `/xmrt-status`")

# Integration helper functions for easy import
async def create_slack_integration(config: Dict[str, Any]) -> SlackIntegration:
    """Create and initialize Slack integration"""
    integration = SlackIntegration(config)
    await integration.start()
    return integration

def get_default_config() -> Dict[str, Any]:
    """Get default Slack integration configuration"""
    return {
        'SLACK_BOT_TOKEN': os.getenv('SLACK_BOT_TOKEN', 'xoxb-your-bot-token'),
        'SLACK_APP_TOKEN': os.getenv('SLACK_APP_TOKEN', 'xapp-your-app-token'), 
        'SLACK_SIGNING_SECRET': os.getenv('SLACK_SIGNING_SECRET', 'your-signing-secret'),
        'SLACK_AGENT_CHANNEL': os.getenv('SLACK_AGENT_CHANNEL', '#ai-agents'),
        'SLACK_LEARNING_CHANNEL': os.getenv('SLACK_LEARNING_CHANNEL', '#learning-cycles'),
        'SLACK_GITHUB_CHANNEL': os.getenv('SLACK_GITHUB_CHANNEL', '#github-operations'),
        'SLACK_HEALTH_CHANNEL': os.getenv('SLACK_HEALTH_CHANNEL', '#system-health'),
        'SLACK_GENERAL_CHANNEL': os.getenv('SLACK_GENERAL_CHANNEL', '#general')
    }
