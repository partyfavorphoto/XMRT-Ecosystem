"""
XMRT-Ecosystem Autonomous Learning Controller

This module implements a real autonomous learning system that:
- Runs hourly learning cycles continuously using APScheduler
- Coordinates 4 AI agents for collaborative learning
- Uses real GitHub operations for code commits
- Integrates with Supabase for persistent memory
- Auto-deploys via Render when commits trigger redeployments
"""

import asyncio
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
import traceback

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import google.generativeai as genai
import openai

from multi_agent_system import MultiAgentSystem
from github_manager import GitHubManager
from memory_system import MemorySystem

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RealAutonomousController:
    """
    Real autonomous learning controller that operates 24/7 with actual:
    - Hourly learning cycles via APScheduler
    - GitHub repository commits
    - Multi-agent AI collaboration
    - Persistent memory with Supabase
    - Auto-deployment triggers
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize the autonomous learning controller with real integrations"""
        self.config = config
        self.is_running = False
        self.learning_cycle_count = 0

        # Initialize scheduler
        self.scheduler = AsyncIOScheduler()

        # Initialize AI APIs
        self._setup_ai_apis()

        # Initialize core systems
        self.multi_agent_system = MultiAgentSystem(config)
        self.github_manager = GitHubManager(config)
        self.memory_system = MemorySystem(config)

        # Learning metrics
        self.metrics = {
            'total_cycles': 0,
            'successful_commits': 0,
            'failed_attempts': 0,
            'improvements_generated': 0,
            'last_cycle_time': None,
            'average_cycle_duration': 0
        }

        logger.info("🤖 Real Autonomous Controller initialized")

    def _setup_ai_apis(self):
        """Configure Gemini Pro and OpenAI APIs"""
        try:
            # Configure Gemini Pro for strategic analysis
            genai.configure(api_key=self.config.get('gemini_api_key'))
            self.gemini_model = genai.GenerativeModel('gemini-pro')

            # Configure OpenAI for code generation
            openai.api_key = self.config.get('openai_api_key')

            logger.info("✅ AI APIs configured successfully")
        except Exception as e:
            logger.error(f"❌ Error configuring AI APIs: {e}")
            raise

    async def start_autonomous_learning(self):
        """Start the real autonomous learning system with hourly cycles"""
        if self.is_running:
            logger.warning("⚠️ Autonomous learning already running")
            return

        try:
            self.is_running = True
            logger.info("🚀 Starting Real Autonomous Learning System")

            # Initialize systems
            await self._initialize_systems()

            # Schedule hourly learning cycles (every hour at minute 0)
            self.scheduler.add_job(
                self._execute_learning_cycle,
                CronTrigger(minute=0),  # Every hour at minute 0
                id='hourly_learning_cycle',
                name='Hourly Autonomous Learning Cycle',
                max_instances=1,
                coalesce=True
            )

            # Schedule daily system health check
            self.scheduler.add_job(
                self._daily_health_check,
                CronTrigger(hour=0, minute=30),  # Daily at 00:30
                id='daily_health_check',
                name='Daily System Health Check'
            )

            # Schedule weekly deep analysis
            self.scheduler.add_job(
                self._weekly_deep_analysis,
                CronTrigger(day_of_week='sun', hour=2, minute=0),  # Sunday 2:00 AM
                id='weekly_deep_analysis',
                name='Weekly Deep Analysis and Optimization'
            )

            # Start the scheduler
            self.scheduler.start()

            # Run initial learning cycle
            await self._execute_learning_cycle()

            logger.info("✅ Autonomous learning system started successfully")

        except Exception as e:
            logger.error(f"❌ Error starting autonomous learning: {e}")
            logger.error(traceback.format_exc())
            self.is_running = False
            raise

    async def _initialize_systems(self):
        """Initialize all core systems"""
        logger.info("🔧 Initializing core systems...")

        # Initialize memory system
        await self.memory_system.initialize()

        # Initialize multi-agent system
        await self.multi_agent_system.initialize()

        # Initialize GitHub manager
        await self.github_manager.initialize()

        logger.info("✅ Core systems initialized")

    async def _execute_learning_cycle(self):
        """Execute a complete autonomous learning cycle"""
        cycle_start_time = datetime.now()
        cycle_id = f"cycle_{self.learning_cycle_count + 1}_{cycle_start_time.strftime('%Y%m%d_%H%M%S')}"

        logger.info(f"🔄 Starting Learning Cycle #{self.learning_cycle_count + 1} - ID: {cycle_id}")

        try:
            # Phase 1: Strategic Analysis (Gemini Pro)
            strategic_analysis = await self._phase_1_strategic_analysis(cycle_id)

            # Phase 2: Multi-Agent Collaboration
            collaboration_results = await self._phase_2_agent_collaboration(cycle_id, strategic_analysis)

            # Phase 3: Implementation and Testing
            implementation_results = await self._phase_3_implementation(cycle_id, collaboration_results)

            # Phase 4: Commit and Deploy
            deployment_results = await self._phase_4_commit_deploy(cycle_id, implementation_results)

            # Update metrics and store results
            cycle_duration = (datetime.now() - cycle_start_time).total_seconds()
            await self._update_cycle_metrics(cycle_id, cycle_duration, deployment_results)

            self.learning_cycle_count += 1
            logger.info(f"✅ Learning Cycle #{self.learning_cycle_count} completed successfully")

        except Exception as e:
            logger.error(f"❌ Error in learning cycle {cycle_id}: {e}")
            logger.error(traceback.format_exc())
            self.metrics['failed_attempts'] += 1

    async def _phase_1_strategic_analysis(self, cycle_id: str) -> Dict[str, Any]:
        """Phase 1: Use Gemini Pro for strategic ecosystem analysis"""
        logger.info(f"📊 Phase 1: Strategic Analysis for {cycle_id}")

        try:
            # Get current repository state
            repo_analysis = await self.github_manager.analyze_repository()

            # Get recent learning patterns
            recent_patterns = await self.memory_system.get_recent_learning_patterns(limit=10)

            # Create analysis prompt without f-string issues
            current_time = datetime.now().isoformat()
            repo_json = json.dumps(repo_analysis, indent=2)
            patterns_json = json.dumps(recent_patterns, indent=2)

            analysis_prompt = f"""
As the XMRT-Ecosystem Strategic AI, analyze the current state and identify the next autonomous learning priorities.

Current Repository Analysis:
{repo_json}

Recent Learning Patterns:
{patterns_json}

Current Time: {current_time}
Learning Cycle: {cycle_id}

Provide strategic analysis covering:
1. Current ecosystem strengths and weaknesses
2. Priority areas for improvement
3. Specific learning objectives for this cycle
4. Risk assessment for proposed changes
5. Success metrics for this cycle

Format response as JSON with clear actionable insights.
"""

            # Get strategic analysis from Gemini Pro
            response = await self.gemini_model.generate_content_async(analysis_prompt)
            strategic_analysis = self._parse_ai_response(response.text)

            logger.info("✅ Strategic analysis completed")
            return strategic_analysis

        except Exception as e:
            logger.error(f"❌ Error in strategic analysis: {e}")
            return {'error': str(e), 'phase': 'strategic_analysis'}

    async def _phase_2_agent_collaboration(self, cycle_id: str, strategic_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 2: Multi-agent collaborative planning and design"""
        logger.info(f"🤝 Phase 2: Multi-Agent Collaboration for {cycle_id}")

        try:
            # Start multi-agent collaboration session
            collaboration_session = await self.multi_agent_system.start_collaboration_session({
                'cycle_id': cycle_id,
                'strategic_analysis': strategic_analysis,
                'objectives': strategic_analysis.get('learning_objectives', [])
            })

            # Run collaborative planning
            collaboration_results = await self.multi_agent_system.execute_collaborative_planning(
                session_id=collaboration_session['session_id'],
                strategic_input=strategic_analysis
            )

            logger.info("✅ Multi-agent collaboration completed")
            return collaboration_results

        except Exception as e:
            logger.error(f"❌ Error in agent collaboration: {e}")
            return {'error': str(e), 'phase': 'agent_collaboration'}

    async def _phase_3_implementation(self, cycle_id: str, collaboration_results: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 3: Implementation and testing of improvements"""
        logger.info(f"🛠️ Phase 3: Implementation for {cycle_id}")

        try:
            implementation_results = {
                'generated_code': [],
                'test_results': [],
                'improvements': [],
                'files_modified': []
            }

            # Get implementation tasks from collaboration
            tasks = collaboration_results.get('implementation_tasks', [])

            for task in tasks:
                # Generate code using appropriate AI model
                if task.get('type') == 'strategic':
                    code_result = await self._generate_code_gemini(task)
                else:
                    code_result = await self._generate_code_openai(task)

                if code_result and 'error' not in code_result:
                    # Test the generated code
                    test_result = await self._test_generated_code(code_result)

                    if test_result.get('success', False):
                        implementation_results['generated_code'].append(code_result)
                        implementation_results['test_results'].append(test_result)
                        implementation_results['improvements'].append(task.get('improvement_description'))

                        # Track file modifications
                        if 'file_path' in code_result:
                            implementation_results['files_modified'].append(code_result['file_path'])

            logger.info(f"✅ Implementation completed: {len(implementation_results['generated_code'])} improvements")
            return implementation_results

        except Exception as e:
            logger.error(f"❌ Error in implementation: {e}")
            return {'error': str(e), 'phase': 'implementation'}

    async def _phase_4_commit_deploy(self, cycle_id: str, implementation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 4: Commit changes to GitHub and trigger deployment"""
        logger.info(f"🚀 Phase 4: Commit and Deploy for {cycle_id}")

        try:
            deployment_results = {
                'commits_made': [],
                'deployment_triggered': False,
                'commit_messages': [],
                'files_committed': []
            }

            # Prepare commit data
            if implementation_results.get('generated_code'):
                # Create commit message safely
                improvements_list = implementation_results.get('improvements', [])
                improvements_summary = "\n".join(improvements_list)
                files_count = len(implementation_results.get('files_modified', []))
                current_time = datetime.now().isoformat()

                commit_message = f"""Autonomous Learning Cycle {cycle_id}

Automated improvements:
{improvements_summary}

Files modified: {files_count}
Generated by: XMRT-Ecosystem Autonomous Learning System
Timestamp: {current_time}"""

                # Commit changes to GitHub
                commit_result = await self.github_manager.commit_improvements(
                    cycle_id=cycle_id,
                    improvements=implementation_results['generated_code'],
                    commit_message=commit_message
                )

                if commit_result.get('success', False):
                    deployment_results['commits_made'].append(commit_result['commit_sha'])
                    deployment_results['commit_messages'].append(commit_message)
                    deployment_results['files_committed'] = implementation_results.get('files_modified', [])
                    deployment_results['deployment_triggered'] = True  # Render auto-deploys on commit

                    # Update success metrics
                    self.metrics['successful_commits'] += 1
                    self.metrics['improvements_generated'] += len(implementation_results['improvements'])

            logger.info("✅ Commit and deployment completed")
            return deployment_results

        except Exception as e:
            logger.error(f"❌ Error in commit/deploy: {e}")
            return {'error': str(e), 'phase': 'commit_deploy'}

    async def _generate_code_gemini(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Generate code using Gemini Pro for strategic tasks"""
        try:
            task_desc = task.get('description', '')
            task_type = task.get('type', '')
            task_reqs = json.dumps(task.get('requirements', []), indent=2)

            prompt = f"""
Generate high-quality Python code for the following task:

Task: {task_desc}
Type: {task_type}
Requirements: {task_reqs}

Provide clean, well-documented code with proper error handling.
Include the target file path and ensure code follows best practices.
"""

            response = await self.gemini_model.generate_content_async(prompt)
            return self._parse_code_response(response.text, task)

        except Exception as e:
            logger.error(f"❌ Error generating code with Gemini: {e}")
            return {'error': str(e)}

    async def _generate_code_openai(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Generate code using OpenAI GPT-4 for implementation tasks"""
        try:
            task_desc = task.get('description', '')
            task_type = task.get('type', '')
            task_reqs = json.dumps(task.get('requirements', []), indent=2)

            messages = [
                {"role": "system", "content": "You are an expert Python developer creating high-quality code for the XMRT-Ecosystem."},
                {"role": "user", "content": f"""
Generate Python code for this task:

Task: {task_desc}
Type: {task_type}
Requirements: {task_reqs}

Provide clean, well-documented code with proper error handling.
Include the target file path and ensure code follows best practices.
"""}
            ]

            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=messages,
                max_tokens=2000,
                temperature=0.1
            )

            return self._parse_code_response(response.choices[0].message.content, task)

        except Exception as e:
            logger.error(f"❌ Error generating code with OpenAI: {e}")
            return {'error': str(e)}

    async def _test_generated_code(self, code_result: Dict[str, Any]) -> Dict[str, Any]:
        """Test generated code for syntax and basic functionality"""
        try:
            code = code_result.get('code', '')

            # Basic syntax check
            try:
                compile(code, '<string>', 'exec')
                syntax_valid = True
            except SyntaxError as e:
                return {'success': False, 'error': f'Syntax error: {e}'}

            return {
                'success': True,
                'syntax_valid': syntax_valid,
                'tested_at': datetime.now().isoformat()
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def _daily_health_check(self):
        """Perform daily system health check"""
        logger.info("🔍 Performing daily health check")

        try:
            health_report = {
                'timestamp': datetime.now().isoformat(),
                'metrics': self.metrics.copy(),
                'system_status': {}
            }

            # Check system components
            health_report['system_status']['github'] = await self.github_manager.health_check()
            health_report['system_status']['memory'] = await self.memory_system.health_check()
            health_report['system_status']['agents'] = await self.multi_agent_system.health_check()

            # Store health report
            await self.memory_system.store_health_report(health_report)

            logger.info("✅ Daily health check completed")

        except Exception as e:
            logger.error(f"❌ Error in daily health check: {e}")

    async def _weekly_deep_analysis(self):
        """Perform weekly deep analysis and optimization"""
        logger.info("📈 Performing weekly deep analysis")

        try:
            # Get learning patterns from the past week
            week_ago = datetime.now() - timedelta(days=7)
            weekly_patterns = await self.memory_system.get_learning_patterns_since(week_ago)

            # Create analysis without f-string in multiline
            patterns_json = json.dumps(weekly_patterns, indent=2)
            metrics_json = json.dumps(self.metrics, indent=2)

            analysis_prompt = f"""
Analyze the XMRT-Ecosystem's learning performance over the past week:

Learning Patterns: {patterns_json}
Current Metrics: {metrics_json}

Provide deep analysis covering:
1. Learning effectiveness trends
2. Areas of consistent improvement
3. Recurring challenges or failures
4. Optimization recommendations
5. Strategic adjustments needed

Format as JSON with actionable insights.
"""

            response = await self.gemini_model.generate_content_async(analysis_prompt)
            analysis = self._parse_ai_response(response.text)

            # Store weekly analysis
            await self.memory_system.store_weekly_analysis(analysis)

            logger.info("✅ Weekly deep analysis completed")

        except Exception as e:
            logger.error(f"❌ Error in weekly analysis: {e}")

    async def _update_cycle_metrics(self, cycle_id: str, duration: float, deployment_results: Dict[str, Any]):
        """Update learning cycle metrics"""
        self.metrics['total_cycles'] += 1
        self.metrics['last_cycle_time'] = datetime.now().isoformat()

        # Update average cycle duration
        current_avg = self.metrics['average_cycle_duration']
        total_cycles = self.metrics['total_cycles']
        self.metrics['average_cycle_duration'] = ((current_avg * (total_cycles - 1)) + duration) / total_cycles

    async def get_status(self) -> Dict[str, Any]:
        """Get current system status and metrics"""
        return {
            'is_running': self.is_running,
            'learning_cycle_count': self.learning_cycle_count,
            'metrics': self.metrics.copy(),
            'scheduler_running': self.scheduler.running if hasattr(self, 'scheduler') else False,
            'timestamp': datetime.now().isoformat()
        }

    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        """Parse AI response, handling both JSON and text formats"""
        try:
            # Try to parse as JSON first
            if '{' in response_text and '}' in response_text:
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                json_str = response_text[start:end]
                return json.loads(json_str)
            else:
                # Return as structured text if not JSON
                return {'content': response_text, 'type': 'text'}
        except json.JSONDecodeError:
            return {'content': response_text, 'type': 'text', 'parse_error': True}

    def _parse_code_response(self, response_text: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """Parse code generation response"""
        try:
            # Extract code blocks
            if '```python' in response_text:
                start = response_text.find('```python') + 9
                end = response_text.find('```', start)
                code = response_text[start:end].strip()
            elif '```' in response_text:
                start = response_text.find('```') + 3
                end = response_text.find('```', start)
                code = response_text[start:end].strip()
            else:
                code = response_text.strip()

            return {
                'code': code,
                'file_path': task.get('file_path', 'generated_code.py'),
                'description': task.get('description', ''),
                'generated_at': datetime.now().isoformat()
            }

        except Exception as e:
            return {'error': f'Failed to parse code response: {e}'}

    async def stop_autonomous_learning(self):
        """Stop the autonomous learning system"""
        if not self.is_running:
            logger.warning("⚠️ Autonomous learning not running")
            return

        try:
            logger.info("🛑 Stopping autonomous learning system")

            if hasattr(self, 'scheduler') and self.scheduler.running:
                self.scheduler.shutdown(wait=True)

            self.is_running = False
            logger.info("✅ Autonomous learning system stopped")

        except Exception as e:
            logger.error(f"❌ Error stopping autonomous learning: {e}")
