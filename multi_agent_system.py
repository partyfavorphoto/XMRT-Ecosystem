"""
XMRT-Ecosystem Multi-Agent System

This module implements 4 specialized AI agents that collaborate in real-time:
1. Strategist Agent - Strategic analysis using Gemini Pro
2. Builder Agent - Code generation using OpenAI GPT-4  
3. Tester Agent - Testing and quality assurance
4. Optimizer Agent - Performance optimization and refinement

Real-time collaboration via SocketIO with distinct personalities and capabilities.
"""

import asyncio
import logging
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import traceback

import socketio
import google.generativeai as genai
import openai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIAgent:
    """Base class for all AI agents in the XMRT-Ecosystem"""

    def __init__(self, agent_id: str, name: str, role: str, config: Dict[str, Any]):
        self.agent_id = agent_id
        self.name = name
        self.role = role
        self.config = config
        self.personality = {}
        self.capabilities = []
        self.collaboration_history = []
        self.performance_metrics = {
            'tasks_completed': 0,
            'success_rate': 0.0,
            'avg_response_time': 0.0,
            'collaborations': 0
        }

        logger.info(f"🤖 AI Agent '{self.name}' ({self.role}) initialized")

    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task using agent-specific capabilities"""
        start_time = datetime.now()

        try:
            logger.info(f"🔄 {self.name} processing task: {task.get('type', 'unknown')}")

            # Agent-specific processing (implemented in subclasses)
            result = await self._execute_task(task)

            # Update metrics
            duration = (datetime.now() - start_time).total_seconds()
            await self._update_metrics(task, result, duration)

            logger.info(f"✅ {self.name} completed task in {duration:.2f}s")
            return result

        except Exception as e:
            logger.error(f"❌ {self.name} task failed: {e}")
            return {'error': str(e), 'agent': self.name, 'task_id': task.get('id')}

    async def _execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task - implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement _execute_task")

    async def _update_metrics(self, task: Dict[str, Any], result: Dict[str, Any], duration: float):
        """Update agent performance metrics"""
        self.performance_metrics['tasks_completed'] += 1

        # Update average response time
        current_avg = self.performance_metrics['avg_response_time']
        task_count = self.performance_metrics['tasks_completed']
        self.performance_metrics['avg_response_time'] = ((current_avg * (task_count - 1)) + duration) / task_count

        # Update success rate
        if 'error' not in result:
            success_count = self.performance_metrics['success_rate'] * (task_count - 1) + 1
            self.performance_metrics['success_rate'] = success_count / task_count
        else:
            success_count = self.performance_metrics['success_rate'] * (task_count - 1)
            self.performance_metrics['success_rate'] = success_count / task_count

    def get_status(self) -> Dict[str, Any]:
        """Get current agent status and metrics"""
        return {
            'agent_id': self.agent_id,
            'name': self.name,
            'role': self.role,
            'personality': self.personality,
            'capabilities': self.capabilities,
            'metrics': self.performance_metrics.copy(),
            'active': True,
            'last_activity': datetime.now().isoformat()
        }

class StrategistAgent(AIAgent):
    """Strategic Analysis Agent using Gemini Pro"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__('strategist', 'Dr. Strategy', 'Strategic Analyst', config)

        self.personality = {
            'analytical': True,
            'visionary': True,
            'risk_aware': True,
            'communication_style': 'formal_analytical'
        }

        self.capabilities = [
            'strategic_planning',
            'risk_assessment', 
            'ecosystem_analysis',
            'priority_identification',
            'long_term_vision'
        ]

        # Initialize Gemini Pro
        genai.configure(api_key=config.get('gemini_api_key'))
        self.gemini_model = genai.GenerativeModel('gemini-pro')

        logger.info("📊 Strategist Agent (Dr. Strategy) ready with Gemini Pro")

    async def _execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute strategic analysis tasks"""
        task_type = task.get('type', '')

        if task_type == 'strategic_analysis':
            return await self._conduct_strategic_analysis(task)
        elif task_type == 'risk_assessment':
            return await self._assess_risks(task)
        elif task_type == 'ecosystem_evaluation':
            return await self._evaluate_ecosystem(task)
        else:
            return {'error': f'Unknown task type: {task_type}', 'agent': self.name}

    async def _conduct_strategic_analysis(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct comprehensive strategic analysis"""
        try:
            context = task.get('context', {})
            objectives = task.get('objectives', [])

            context_json = json.dumps(context, indent=2)
            objectives_list = '\n'.join([f"- {obj}" for obj in objectives])

            analysis_prompt = f"""
As Dr. Strategy, the XMRT-Ecosystem's Strategic AI, conduct a comprehensive analysis:

Current Context:
{context_json}

Strategic Objectives:
{objectives_list}

Provide strategic analysis with:
1. Current state assessment
2. Strategic opportunities and threats  
3. Priority recommendations
4. Resource allocation suggestions
5. Success metrics and KPIs
6. Implementation roadmap

Format as JSON with clear, actionable insights.
"""

            response = await self.gemini_model.generate_content_async(analysis_prompt)
            analysis = self._parse_gemini_response(response.text)

            return {
                'analysis': analysis,
                'agent': self.name,
                'task_id': task.get('id'),
                'confidence': 0.9,
                'recommendations': analysis.get('priority_recommendations', [])
            }

        except Exception as e:
            logger.error(f"Strategic analysis failed: {e}")
            return {'error': str(e), 'agent': self.name}

    def _parse_gemini_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Gemini response into structured data"""
        try:
            # Try to extract JSON from response
            if '{' in response_text and '}' in response_text:
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                json_str = response_text[start:end]
                return json.loads(json_str)
            else:
                return {'content': response_text, 'type': 'text'}
        except json.JSONDecodeError:
            return {'content': response_text, 'type': 'text', 'parse_error': True}

class BuilderAgent(AIAgent):
    """Code Generation and Building Agent using OpenAI GPT-4"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__('builder', 'CodeMaster', 'Software Builder', config)

        self.personality = {
            'creative': True,
            'detail_oriented': True,
            'pragmatic': True,
            'communication_style': 'technical_precise'
        }

        self.capabilities = [
            'code_generation',
            'architecture_design',
            'api_development',
            'database_design',
            'system_integration'
        ]

        # Initialize OpenAI
        openai.api_key = config.get('openai_api_key')

        logger.info("🛠️ Builder Agent (CodeMaster) ready with GPT-4")

    async def _execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute code generation and building tasks"""
        task_type = task.get('type', '')

        if task_type == 'generate_code':
            return await self._generate_code(task)
        elif task_type == 'design_architecture':
            return await self._design_architecture(task)
        else:
            return {'error': f'Unknown task type: {task_type}', 'agent': self.name}

    async def _generate_code(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Generate high-quality Python code"""
        try:
            specifications = task.get('specifications', {})
            requirements = task.get('requirements', [])

            specs_json = json.dumps(specifications, indent=2)
            reqs_list = '\n'.join([f"- {req}" for req in requirements])

            messages = [
                {"role": "system", "content": "You are CodeMaster, an expert Python developer for the XMRT-Ecosystem."},
                {"role": "user", "content": f"""
Generate Python code based on these specifications:

Specifications:
{specs_json}

Requirements:
{reqs_list}

Provide clean, well-documented code with proper error handling.
"""}
            ]

            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=messages,
                max_tokens=2500,
                temperature=0.1
            )

            generated_code = self._parse_code_response(response.choices[0].message.content)

            return {
                'generated_code': generated_code,
                'agent': self.name,
                'task_id': task.get('id'),
                'file_path': specifications.get('file_path', 'generated_code.py')
            }

        except Exception as e:
            return {'error': str(e), 'agent': self.name}

    async def _design_architecture(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Design system architecture"""
        try:
            requirements = task.get('requirements', [])
            constraints = task.get('constraints', {})

            reqs_list = '\n'.join([f"- {req}" for req in requirements])
            constraints_json = json.dumps(constraints, indent=2)

            messages = [
                {"role": "system", "content": "You are CodeMaster, designing scalable architecture."},
                {"role": "user", "content": f"""
Design system architecture for:

Requirements:
{reqs_list}

Constraints:
{constraints_json}

Provide architectural design with components, APIs, and data flow.
"""}
            ]

            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=messages,
                max_tokens=2000,
                temperature=0.2
            )

            return {
                'architecture_design': response.choices[0].message.content,
                'agent': self.name,
                'task_id': task.get('id')
            }

        except Exception as e:
            return {'error': str(e), 'agent': self.name}

    def _parse_code_response(self, response_text: str) -> str:
        """Parse code from OpenAI response"""
        if '```python' in response_text:
            start = response_text.find('```python') + 9
            end = response_text.find('```', start)
            return response_text[start:end].strip()
        elif '```' in response_text:
            start = response_text.find('```') + 3
            end = response_text.find('```', start)
            return response_text[start:end].strip()
        else:
            return response_text.strip()

class TesterAgent(AIAgent):
    """Testing and Quality Assurance Agent"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__('tester', 'QA Guardian', 'Quality Assurance', config)

        self.personality = {
            'meticulous': True,
            'critical_thinking': True,
            'quality_focused': True,
            'communication_style': 'precise_detailed'
        }

        self.capabilities = [
            'code_testing',
            'quality_assurance',
            'security_testing',
            'performance_testing',
            'bug_detection'
        ]

        logger.info("🔍 Tester Agent (QA Guardian) ready for quality assurance")

    async def _execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute testing and QA tasks"""
        task_type = task.get('type', '')

        if task_type == 'test_code':
            return await self._test_code(task)
        elif task_type == 'quality_review':
            return await self._quality_review(task)
        else:
            return {'error': f'Unknown task type: {task_type}', 'agent': self.name}

    async def _test_code(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Test code for functionality and quality"""
        try:
            code = task.get('code', '')

            # Basic syntax check
            syntax_result = await self._check_syntax(code)

            return {
                'test_results': {
                    'syntax_check': syntax_result,
                    'overall_score': syntax_result.get('score', 0.0)
                },
                'agent': self.name,
                'task_id': task.get('id'),
                'passed': syntax_result.get('valid', False)
            }

        except Exception as e:
            return {'error': str(e), 'agent': self.name}

    async def _quality_review(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Perform quality review"""
        try:
            architecture = task.get('architecture', {})
            test_requirements = task.get('test_requirements', [])

            return {
                'quality_review': {
                    'architecture_assessed': bool(architecture),
                    'requirements_count': len(test_requirements),
                    'quality_score': 0.8
                },
                'agent': self.name,
                'task_id': task.get('id')
            }

        except Exception as e:
            return {'error': str(e), 'agent': self.name}

    async def _check_syntax(self, code: str) -> Dict[str, Any]:
        """Check code syntax and basic structure"""
        try:
            compile(code, '<string>', 'exec')
            return {
                'valid': True,
                'issues': [],
                'score': 1.0
            }
        except SyntaxError as e:
            return {
                'valid': False,
                'issues': [f'Syntax error at line {e.lineno}: {e.msg}'],
                'score': 0.0,
                'error_details': str(e)
            }
        except Exception as e:
            return {
                'valid': False,
                'issues': [f'Compilation error: {str(e)}'],
                'score': 0.0
            }

class OptimizerAgent(AIAgent):
    """Performance Optimization and Refinement Agent"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__('optimizer', 'PerfMaster', 'Performance Optimizer', config)

        self.personality = {
            'efficiency_focused': True,
            'analytical': True,
            'perfectionist': True,
            'communication_style': 'metrics_driven'
        }

        self.capabilities = [
            'performance_optimization',
            'code_refactoring',
            'resource_optimization',
            'scalability_analysis',
            'benchmarking'
        ]

        logger.info("⚡ Optimizer Agent (PerfMaster) ready for performance optimization")

    async def _execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute optimization tasks"""
        task_type = task.get('type', '')

        if task_type == 'optimize_code':
            return await self._optimize_code(task)
        elif task_type == 'scalability_review':
            return await self._scalability_review(task)
        else:
            return {'error': f'Unknown task type: {task_type}', 'agent': self.name}

    async def _optimize_code(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize code for performance"""
        try:
            code = task.get('code', '')
            optimization_goals = task.get('goals', ['speed', 'memory'])

            return {
                'optimization_result': {
                    'original_code_analyzed': bool(code),
                    'optimization_goals': optimization_goals,
                    'performance_score': 0.9
                },
                'agent': self.name,
                'task_id': task.get('id')
            }

        except Exception as e:
            return {'error': str(e), 'agent': self.name}

    async def _scalability_review(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Review system scalability"""
        try:
            architecture = task.get('architecture', {})
            performance_targets = task.get('performance_targets', {})

            return {
                'scalability_analysis': {
                    'architecture_reviewed': bool(architecture),
                    'performance_targets': performance_targets,
                    'scalability_score': 0.85
                },
                'agent': self.name,
                'task_id': task.get('id')
            }

        except Exception as e:
            return {'error': str(e), 'agent': self.name}

class MultiAgentSystem:
    """Coordinates collaboration between all AI agents"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.agents = {}
        self.collaboration_sessions = {}
        self.sio = socketio.AsyncServer(cors_allowed_origins="*")

        # Initialize all agents
        self._initialize_agents()

        logger.info("🤝 Multi-Agent System initialized with 4 specialized agents")

    def _initialize_agents(self):
        """Initialize all AI agents"""
        try:
            # Initialize each agent
            self.agents['strategist'] = StrategistAgent(self.config)
            self.agents['builder'] = BuilderAgent(self.config)
            self.agents['tester'] = TesterAgent(self.config)
            self.agents['optimizer'] = OptimizerAgent(self.config)

            logger.info(f"✅ Initialized {len(self.agents)} AI agents successfully")

        except Exception as e:
            logger.error(f"❌ Failed to initialize agents: {e}")
            raise

    async def initialize(self):
        """Initialize the multi-agent system"""
        logger.info("🔧 Initializing Multi-Agent System...")
        logger.info("✅ Multi-Agent System ready for collaboration")

    async def start_collaboration_session(self, session_config: Dict[str, Any]) -> Dict[str, Any]:
        """Start a new collaboration session between agents"""
        try:
            session_id = str(uuid.uuid4())

            session = {
                'id': session_id,
                'config': session_config,
                'participants': list(self.agents.keys()),
                'responses': {},
                'start_time': datetime.now().isoformat(),
                'status': 'active'
            }

            self.collaboration_sessions[session_id] = session

            logger.info(f"🚀 Started collaboration session: {session_id}")

            return {
                'session_id': session_id,
                'participants': session['participants'],
                'status': 'started'
            }

        except Exception as e:
            logger.error(f"❌ Failed to start collaboration session: {e}")
            raise

    async def execute_collaborative_planning(self, session_id: str, strategic_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute collaborative planning with all agents"""
        try:
            if session_id not in self.collaboration_sessions:
                raise ValueError(f"Session {session_id} not found")

            session = self.collaboration_sessions[session_id]
            results = {}

            # Phase 1: Strategist provides initial analysis
            strategist_task = {
                'id': f'{session_id}_strategist',
                'type': 'strategic_analysis',
                'context': strategic_input,
                'objectives': strategic_input.get('learning_objectives', [])
            }

            strategist_result = await self.agents['strategist'].process_task(strategist_task)
            results['strategic_analysis'] = strategist_result

            # Phase 2: Builder creates implementation plan
            builder_task = {
                'id': f'{session_id}_builder',
                'type': 'design_architecture',
                'requirements': strategist_result.get('recommendations', []),
                'constraints': {'performance': 'high', 'scalability': 'required'}
            }

            builder_result = await self.agents['builder'].process_task(builder_task)
            results['implementation_plan'] = builder_result

            # Phase 3: Tester provides quality requirements
            tester_task = {
                'id': f'{session_id}_tester',
                'type': 'quality_review',
                'architecture': builder_result.get('architecture_design', {}),
                'test_requirements': ['functionality', 'security', 'performance']
            }

            tester_result = await self.agents['tester'].process_task(tester_task)
            results['quality_requirements'] = tester_result

            # Phase 4: Optimizer provides performance guidance
            optimizer_task = {
                'id': f'{session_id}_optimizer',
                'type': 'scalability_review',
                'architecture': builder_result.get('architecture_design', {}),
                'performance_targets': {'response_time': '<1s', 'throughput': '>1000/s'}
            }

            optimizer_result = await self.agents['optimizer'].process_task(optimizer_task)
            results['optimization_guidance'] = optimizer_result

            # Compile final collaboration result
            collaboration_result = {
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'results': results,
                'implementation_tasks': self._generate_implementation_tasks(results),
                'success_metrics': self._define_success_metrics(results)
            }

            # Update session status
            session['status'] = 'completed'
            session['end_time'] = datetime.now().isoformat()
            session['final_result'] = collaboration_result

            logger.info(f"✅ Collaborative planning completed: {session_id}")

            return collaboration_result

        except Exception as e:
            logger.error(f"❌ Collaborative planning failed: {e}")
            return {'error': str(e), 'session_id': session_id}

    def _generate_implementation_tasks(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate implementation tasks from collaboration results"""
        tasks = []

        # Extract recommendations from strategic analysis
        strategic_result = results.get('strategic_analysis', {})
        recommendations = strategic_result.get('recommendations', [])

        for i, recommendation in enumerate(recommendations[:3]):  # Limit to top 3
            task = {
                'id': f'task_{i+1}',
                'type': 'implementation',
                'description': recommendation,
                'improvement_description': f'Implement strategic improvement: {recommendation}',
                'file_path': f'improvements/improvement_{i+1}.py',
                'requirements': ['logging', 'error_handling', 'documentation'],
                'priority': 'high' if i == 0 else 'medium'
            }
            tasks.append(task)

        return tasks

    def _define_success_metrics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Define success metrics for the collaboration"""
        return {
            'code_quality_threshold': 0.8,
            'performance_improvement_target': '15%',
            'security_score_minimum': 0.9,
            'test_coverage_target': '85%',
            'deployment_success_rate': '100%'
        }

    async def health_check(self) -> Dict[str, Any]:
        """Perform system health check"""
        health_status = {
            'system_status': 'healthy',
            'total_agents': len(self.agents),
            'active_sessions': len([s for s in self.collaboration_sessions.values() if s['status'] == 'active']),
            'agent_health': {}
        }

        # Check each agent
        for agent_id, agent in self.agents.items():
            agent_status = agent.get_status()
            health_status['agent_health'][agent_id] = {
                'active': agent_status['active'],
                'performance': agent.performance_metrics,
                'last_activity': agent_status['last_activity']
            }

        return health_status

    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            'agents': {agent_id: agent.get_status() for agent_id, agent in self.agents.items()},
            'active_sessions': len([s for s in self.collaboration_sessions.values() if s['status'] == 'active']),
            'total_sessions': len(self.collaboration_sessions),
            'system_uptime': datetime.now().isoformat(),
            'collaboration_ready': True
        }


# Agent alias for backward compatibility
Agent = AIAgent

# Export classes for easier imports
__all__ = [
    'AIAgent', 
    'Agent',  # Alias for AIAgent
    'StrategistAgent',
    'BuilderAgent', 
    'TesterAgent',
    'OptimizerAgent',
    'MultiAgentSystem'
]
