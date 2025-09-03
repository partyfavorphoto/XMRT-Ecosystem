"""
XMRT-Ecosystem Multi-Agent Slack Communication Bridge

This module creates a communication bridge between the existing 4 AI agents 
(Strategist, Builder, Tester, Optimizer) and Slack channels, enabling:
- Real-time agent collaboration in Slack
- Agent status updates and notifications
- Inter-agent communication logging
- Collaborative decision-making transparency
"""

import asyncio
import logging
import json
import threading
import time
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor

from slack_integration import SlackIntegration, AgentUpdate, SlackMessage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class AgentCollaboration:
    """Structure for agent collaboration events"""
    initiator_agent: str
    target_agents: List[str]
    collaboration_type: str  # discussion, decision, review, consensus
    topic: str
    content: Dict[str, Any]
    timestamp: datetime
    status: str  # pending, active, completed
    thread_id: Optional[str] = None

class MultiAgentSlackBridge:
    """
    Bridge between XMRT-Ecosystem multi-agent system and Slack

    Connects the 4 AI agents to Slack channels for transparent collaboration:
    - Strategist Agent (🎯) - Strategic analysis and planning
    - Builder Agent (🔨) - Code generation and implementation
    - Tester Agent (🧪) - Quality assurance and testing  
    - Optimizer Agent (⚡) - Performance optimization and refinement
    """

    def __init__(self, slack_integration: SlackIntegration, multi_agent_system=None):
        """Initialize the multi-agent Slack bridge"""
        self.slack = slack_integration
        self.multi_agent_system = multi_agent_system

        # Agent configurations
        self.agent_configs = {
            'strategist': {
                'name': 'Strategist',
                'emoji': '🎯', 
                'color': '#4285F4',  # Blue
                'channel': self.slack.channels['agent_collaboration'],
                'specialties': ['strategic_analysis', 'planning', 'architecture']
            },
            'builder': {
                'name': 'Builder',
                'emoji': '🔨',
                'color': '#34A853',  # Green  
                'channel': self.slack.channels['agent_collaboration'],
                'specialties': ['code_generation', 'implementation', 'development']
            },
            'tester': {
                'name': 'Tester', 
                'emoji': '🧪',
                'color': '#FBBC04',  # Yellow
                'channel': self.slack.channels['agent_collaboration'],
                'specialties': ['quality_assurance', 'testing', 'validation']
            },
            'optimizer': {
                'name': 'Optimizer',
                'emoji': '⚡',
                'color': '#EA4335',  # Red
                'channel': self.slack.channels['agent_collaboration'], 
                'specialties': ['performance', 'optimization', 'refinement']
            }
        }

        # Communication state
        self.active_collaborations = {}
        self.agent_threads = {}
        self.collaboration_history = []
        self.message_queue = asyncio.Queue()

        # Statistics
        self.stats = {
            'total_collaborations': 0,
            'active_discussions': 0,
            'messages_sent': 0,
            'decisions_made': 0,
            'agent_interactions': 0
        }

        self.is_running = False
        self.executor = ThreadPoolExecutor(max_workers=4)

        logger.info("🌉 Multi-Agent Slack Bridge initialized")

    async def start(self):
        """Start the multi-agent Slack bridge"""
        try:
            logger.info("🚀 Starting Multi-Agent Slack Bridge...")

            self.is_running = True

            # Start message processing
            asyncio.create_task(self._process_collaboration_queue())

            # Send startup notification
            await self._announce_bridge_startup()

            logger.info("✅ Multi-Agent Slack Bridge started successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to start Multi-Agent Slack Bridge: {e}")
            return False

    async def stop(self):
        """Stop the multi-agent Slack bridge"""
        try:
            logger.info("🛑 Stopping Multi-Agent Slack Bridge...")

            self.is_running = False

            # Send shutdown notification
            await self._announce_bridge_shutdown()

            # Close executor
            self.executor.shutdown(wait=True)

            logger.info("✅ Multi-Agent Slack Bridge stopped")

        except Exception as e:
            logger.error(f"❌ Error stopping Multi-Agent Slack Bridge: {e}")

    async def agent_start_activity(self, agent_id: str, activity: str, details: Dict[str, Any] = None):
        """Notify Slack when an agent starts an activity"""
        agent_name = self._get_agent_name(agent_id)

        update = AgentUpdate(
            agent_id=agent_id,
            agent_name=agent_name,
            activity=f"Starting: {activity}",
            status="active",
            details=details or {},
            timestamp=datetime.now(timezone.utc)
        )

        await self.slack.send_agent_update(update)
        self.stats['agent_interactions'] += 1

        logger.info(f"🎬 {agent_name} started activity: {activity}")

    async def agent_complete_activity(self, agent_id: str, activity: str, result: Dict[str, Any] = None):
        """Notify Slack when an agent completes an activity"""
        agent_name = self._get_agent_name(agent_id)

        update = AgentUpdate(
            agent_id=agent_id,
            agent_name=agent_name,
            activity=f"Completed: {activity}",
            status="completed",
            details=result or {},
            timestamp=datetime.now(timezone.utc)
        )

        await self.slack.send_agent_update(update)
        self.stats['agent_interactions'] += 1

        logger.info(f"✅ {agent_name} completed activity: {activity}")

    async def agent_error(self, agent_id: str, activity: str, error: str):
        """Notify Slack when an agent encounters an error"""
        agent_name = self._get_agent_name(agent_id)

        update = AgentUpdate(
            agent_id=agent_id,
            agent_name=agent_name,
            activity=f"Error in: {activity}",
            status="error", 
            details={"error": error},
            timestamp=datetime.now(timezone.utc)
        )

        await self.slack.send_agent_update(update)

        # Also send as system alert
        await self.slack.send_system_notification(
            f"❌ {agent_name} Agent Error",
            f"Agent encountered error in {activity}: {error}",
            severity="error"
        )

        logger.error(f"❌ {agent_name} error in {activity}: {error}")

    async def start_collaboration(self, 
                                initiator_agent: str, 
                                target_agents: List[str],
                                collaboration_type: str,
                                topic: str,
                                content: Dict[str, Any]) -> str:
        """Start a collaboration between agents"""

        collaboration_id = f"collab_{int(time.time())}_{initiator_agent}"

        collaboration = AgentCollaboration(
            initiator_agent=initiator_agent,
            target_agents=target_agents,
            collaboration_type=collaboration_type,
            topic=topic,
            content=content,
            timestamp=datetime.now(timezone.utc),
            status="active"
        )

        self.active_collaborations[collaboration_id] = collaboration

        # Send collaboration start message to Slack
        await self._send_collaboration_message(collaboration_id, collaboration)

        self.stats['total_collaborations'] += 1
        self.stats['active_discussions'] += 1

        logger.info(f"🤝 Started collaboration: {collaboration_id} - {topic}")

        return collaboration_id

    async def add_collaboration_message(self, 
                                      collaboration_id: str,
                                      agent_id: str, 
                                      message: str,
                                      message_type: str = "discussion"):
        """Add a message to an ongoing collaboration"""

        if collaboration_id not in self.active_collaborations:
            logger.warning(f"⚠️ Collaboration {collaboration_id} not found")
            return

        collaboration = self.active_collaborations[collaboration_id]
        agent_name = self._get_agent_name(agent_id)
        config = self.agent_configs.get(agent_id.lower(), {})

        # Create threaded message in Slack
        thread_message = SlackMessage(
            channel=self.slack.channels['agent_collaboration'],
            text=f"{config.get('emoji', '🤖')} *{agent_name}*: {message}",
            thread_ts=collaboration.thread_id,
            message_type='collaboration'
        )

        await self.slack.send_message(thread_message)
        self.stats['messages_sent'] += 1

        logger.info(f"💬 {agent_name} added message to {collaboration_id}: {message[:50]}...")

    async def complete_collaboration(self, 
                                   collaboration_id: str, 
                                   result: Dict[str, Any],
                                   decision: Optional[str] = None):
        """Complete a collaboration with results"""

        if collaboration_id not in self.active_collaborations:
            logger.warning(f"⚠️ Collaboration {collaboration_id} not found")
            return

        collaboration = self.active_collaborations[collaboration_id]
        collaboration.status = "completed"

        # Send completion message
        await self._send_collaboration_completion(collaboration_id, result, decision)

        # Move to history
        self.collaboration_history.append(collaboration)
        del self.active_collaborations[collaboration_id]

        self.stats['active_discussions'] -= 1
        self.stats['decisions_made'] += 1

        logger.info(f"✅ Completed collaboration: {collaboration_id}")

    async def agent_thinking(self, agent_id: str, thought_process: str):
        """Share agent thinking process in Slack"""
        agent_name = self._get_agent_name(agent_id)
        config = self.agent_configs.get(agent_id.lower(), {})

        update = AgentUpdate(
            agent_id=agent_id,
            agent_name=agent_name,
            activity=f"Thinking: {thought_process}",
            status="thinking",
            details={"thought_process": thought_process},
            timestamp=datetime.now(timezone.utc)
        )

        await self.slack.send_agent_update(update)
        logger.info(f"🤔 {agent_name} thinking: {thought_process[:50]}...")

    async def send_agent_consensus(self, 
                                 agents: List[str], 
                                 topic: str, 
                                 consensus: str):
        """Send multi-agent consensus decision to Slack"""

        agent_names = [self._get_agent_name(agent_id) for agent_id in agents]
        agent_emojis = [self.agent_configs.get(agent_id.lower(), {}).get('emoji', '🤖') 
                       for agent_id in agents]

        consensus_message = f"""
🤝 **Multi-Agent Consensus Reached**

**Topic:** {topic}
**Participating Agents:** {' '.join(agent_emojis)} {', '.join(agent_names)}

**Consensus Decision:**
{consensus}

**Timestamp:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
        """

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🤝 Multi-Agent Consensus"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Topic:* {topic}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Agents:* {' '.join(agent_emojis)} {', '.join(agent_names)}"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Decision:*\n{consensus}"
                }
            }
        ]

        message = SlackMessage(
            channel=self.slack.channels['agent_collaboration'],
            text=consensus_message,
            blocks=blocks,
            message_type='consensus'
        )

        await self.slack.send_message(message)
        self.stats['decisions_made'] += 1

        logger.info(f"🤝 Sent consensus for topic: {topic}")

    async def _process_collaboration_queue(self):
        """Process collaboration message queue"""
        while self.is_running:
            try:
                await asyncio.sleep(0.1)  # Small delay to prevent busy waiting
            except Exception as e:
                logger.error(f"Error processing collaboration queue: {e}")
                await asyncio.sleep(1)

    async def _send_collaboration_message(self, collaboration_id: str, collaboration: AgentCollaboration):
        """Send initial collaboration message to Slack"""

        initiator_config = self.agent_configs.get(collaboration.initiator_agent.lower(), {})
        target_names = [self._get_agent_name(agent) for agent in collaboration.target_agents]
        target_emojis = [self.agent_configs.get(agent.lower(), {}).get('emoji', '🤖') 
                        for agent in collaboration.target_agents]

        title = f"🤝 {collaboration.collaboration_type.title()} Started"

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
                        "text": f"*Initiator:* {initiator_config.get('emoji', '🤖')} {collaboration.initiator_agent}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Participants:* {' '.join(target_emojis)} {', '.join(target_names)}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Topic:* {collaboration.topic}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Type:* {collaboration.collaboration_type}"
                    }
                ]
            }
        ]

        # Add content details if available
        if collaboration.content:
            content_text = "\n".join([f"• {k}: {v}" for k, v in collaboration.content.items()])
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Details:*\n{content_text}"
                }
            })

        message = SlackMessage(
            channel=self.slack.channels['agent_collaboration'],
            text=title,
            blocks=blocks,
            message_type='collaboration_start'
        )

        # Send message and capture thread timestamp
        response = await self.slack.send_message(message)
        if response:
            # In a real implementation, you'd capture the thread_ts from the response
            collaboration.thread_id = f"thread_{collaboration_id}"

    async def _send_collaboration_completion(self, 
                                           collaboration_id: str, 
                                           result: Dict[str, Any],
                                           decision: Optional[str]):
        """Send collaboration completion message"""

        collaboration = self.active_collaborations[collaboration_id]

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "✅ Collaboration Completed"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn", 
                        "text": f"*Topic:* {collaboration.topic}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Duration:* {self._format_duration(collaboration.timestamp)}"
                    }
                ]
            }
        ]

        if decision:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Decision:* {decision}"
                }
            })

        if result:
            result_text = "\n".join([f"• {k}: {v}" for k, v in result.items()])
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Results:*\n{result_text}"
                }
            })

        message = SlackMessage(
            channel=self.slack.channels['agent_collaboration'],
            text="✅ Collaboration Completed",
            blocks=blocks,
            thread_ts=collaboration.thread_id,
            message_type='collaboration_end'
        )

        await self.slack.send_message(message)

    async def _announce_bridge_startup(self):
        """Announce bridge startup to Slack"""
        agents_list = "\n".join([
            f"{config['emoji']} {config['name']} - {', '.join(config['specialties'])}"
            for config in self.agent_configs.values()
        ])

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🌉 Multi-Agent Bridge Online"
                }
            },
            {
                "type": "section", 
                "text": {
                    "type": "mrkdwn",
                    "text": "The XMRT-Ecosystem agents are now connected to Slack for real-time collaboration!"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Connected Agents:*\n{agents_list}"
                }
            }
        ]

        message = SlackMessage(
            channel=self.slack.channels['agent_collaboration'],
            text="🌉 Multi-Agent Bridge Online",
            blocks=blocks,
            message_type='system'
        )

        await self.slack.send_message(message)

    async def _announce_bridge_shutdown(self):
        """Announce bridge shutdown to Slack"""
        await self.slack.send_system_notification(
            "🌉 Multi-Agent Bridge Offline",
            f"Agent collaboration bridge is shutting down. Total collaborations: {self.stats['total_collaborations']}",
            severity="info",
            channel=self.slack.channels['agent_collaboration']
        )

    def _get_agent_name(self, agent_id: str) -> str:
        """Get formatted agent name"""
        config = self.agent_configs.get(agent_id.lower(), {})
        return config.get('name', agent_id.title())

    def _format_duration(self, start_time: datetime) -> str:
        """Format collaboration duration"""
        duration = datetime.now(timezone.utc) - start_time
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"

    def get_stats(self) -> Dict[str, Any]:
        """Get bridge statistics"""
        return {
            **self.stats,
            'active_collaborations': len(self.active_collaborations),
            'total_history': len(self.collaboration_history),
            'agents_configured': len(self.agent_configs)
        }

# Integration helper functions
def create_multi_agent_bridge(slack_integration: SlackIntegration, 
                            multi_agent_system=None) -> MultiAgentSlackBridge:
    """Create multi-agent Slack bridge"""
    return MultiAgentSlackBridge(slack_integration, multi_agent_system)
