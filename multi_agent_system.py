"""
Multi-Agent AI System for XMRT-Ecosystem
Enhanced with specialized agent types, advanced coordination, and autonomous learning
"""

import asyncio
import logging
import threading
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import time
import random
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentType(Enum):
    """Types of specialized agents"""
    COORDINATOR = "coordinator"
    ANALYZER = "analyzer" 
    DEVELOPER = "developer"
    MONITOR = "monitor"
    SECURITY = "security"

class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class TaskStatus(Enum):
    """Task execution states"""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class AgentCapability:
    """Agent capability definition"""
    name: str
    proficiency: float  # 0.0 - 1.0
    experience_count: int
    success_rate: float
    last_updated: datetime

@dataclass
class Task:
    """Enhanced task definition"""
    id: str
    type: str
    description: str
    priority: TaskPriority
    required_capabilities: List[str]
    created_at: datetime
    deadline: Optional[datetime] = None
    assigned_agent: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    progress: float = 0.0
    metadata: Dict[str, Any] = None
    dependencies: List[str] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.dependencies is None:
            self.dependencies = []

@dataclass
class AgentPerformance:
    """Agent performance tracking"""
    tasks_completed: int = 0
    tasks_failed: int = 0
    average_completion_time: float = 0.0
    success_rate: float = 0.0
    efficiency_score: float = 0.0
    learning_progress: float = 0.0
    collaboration_score: float = 0.0

class BaseAgent(ABC):
    """Abstract base agent class"""

    def __init__(self, agent_id: str, agent_type: AgentType):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.capabilities: Dict[str, AgentCapability] = {}
        self.performance = AgentPerformance()
        self.current_task: Optional[Task] = None
        self.task_history: List[Task] = []
        self.learning_rate = 0.1
        self.is_active = True
        self.last_activity = datetime.now()

    @abstractmethod
    async def execute_task(self, task: Task) -> Dict[str, Any]:
        """Execute assigned task"""
        pass

    @abstractmethod
    def can_handle_task(self, task: Task) -> float:
        """Return capability score for task (0.0 - 1.0)"""
        pass

    def update_capability(self, capability_name: str, success: bool):
        """Update agent capability based on task outcome"""
        if capability_name not in self.capabilities:
            self.capabilities[capability_name] = AgentCapability(
                name=capability_name,
                proficiency=0.5,
                experience_count=0,
                success_rate=0.5,
                last_updated=datetime.now()
            )

        cap = self.capabilities[capability_name]
        cap.experience_count += 1

        # Update success rate with exponential moving average
        if success:
            cap.success_rate = cap.success_rate * 0.9 + 0.1
            cap.proficiency = min(1.0, cap.proficiency + self.learning_rate * 0.1)
        else:
            cap.success_rate = cap.success_rate * 0.9
            cap.proficiency = max(0.1, cap.proficiency - self.learning_rate * 0.05)

        cap.last_updated = datetime.now()

    def update_performance(self, task: Task, success: bool, completion_time: float):
        """Update agent performance metrics"""
        if success:
            self.performance.tasks_completed += 1
        else:
            self.performance.tasks_failed += 1

        total_tasks = self.performance.tasks_completed + self.performance.tasks_failed
        self.performance.success_rate = self.performance.tasks_completed / total_tasks if total_tasks > 0 else 0

        # Update average completion time
        if self.performance.tasks_completed > 0:
            self.performance.average_completion_time = (
                (self.performance.average_completion_time * (self.performance.tasks_completed - 1) + completion_time) / 
                self.performance.tasks_completed
            )

        # Calculate efficiency score
        self.performance.efficiency_score = min(1.0, self.performance.success_rate * (1.0 / max(1.0, completion_time / 60.0)))

class CoordinatorAgent(BaseAgent):
    """Coordinator agent for task management and orchestration"""

    def __init__(self, agent_id: str):
        super().__init__(agent_id, AgentType.COORDINATOR)
        self.capabilities = {
            "task_planning": AgentCapability("task_planning", 0.8, 0, 0.8, datetime.now()),
            "resource_allocation": AgentCapability("resource_allocation", 0.7, 0, 0.7, datetime.now()),
            "coordination": AgentCapability("coordination", 0.9, 0, 0.9, datetime.now()),
            "optimization": AgentCapability("optimization", 0.6, 0, 0.6, datetime.now())
        }

    async def execute_task(self, task: Task) -> Dict[str, Any]:
        """Execute coordination task"""
        try:
            logger.info(f"Coordinator {self.agent_id} executing task: {task.description}")

            # Simulate coordination work
            await asyncio.sleep(random.uniform(0.5, 2.0))

            result = {
                "status": "completed",
                "coordination_plan": f"Optimized plan for {task.type}",
                "resource_allocation": {"cpu": 0.8, "memory": 0.6},
                "estimated_completion": datetime.now() + timedelta(minutes=30),
                "agent_id": self.agent_id
            }

            return result

        except Exception as e:
            logger.error(f"Coordinator task failed: {e}")
            return {"status": "failed", "error": str(e), "agent_id": self.agent_id}

    def can_handle_task(self, task: Task) -> float:
        """Evaluate capability to handle coordination tasks"""
        coordination_tasks = ["planning", "coordination", "optimization", "resource_management"]

        if any(task_type in task.type.lower() for task_type in coordination_tasks):
            base_score = 0.8
        else:
            base_score = 0.3

        # Factor in current workload
        workload_factor = 0.8 if self.current_task else 1.0

        # Factor in relevant capabilities
        capability_score = sum(
            cap.proficiency for cap_name, cap in self.capabilities.items()
            if cap_name in task.required_capabilities
        ) / len(task.required_capabilities) if task.required_capabilities else 0.7

        return min(1.0, base_score * workload_factor * capability_score)

class AnalyzerAgent(BaseAgent):
    """Analyzer agent for data analysis and pattern recognition"""

    def __init__(self, agent_id: str):
        super().__init__(agent_id, AgentType.ANALYZER)
        self.capabilities = {
            "data_analysis": AgentCapability("data_analysis", 0.9, 0, 0.9, datetime.now()),
            "pattern_recognition": AgentCapability("pattern_recognition", 0.8, 0, 0.8, datetime.now()),
            "statistical_modeling": AgentCapability("statistical_modeling", 0.7, 0, 0.7, datetime.now()),
            "visualization": AgentCapability("visualization", 0.6, 0, 0.6, datetime.now())
        }

    async def execute_task(self, task: Task) -> Dict[str, Any]:
        """Execute analysis task"""
        try:
            logger.info(f"Analyzer {self.agent_id} executing task: {task.description}")

            # Simulate analysis work
            await asyncio.sleep(random.uniform(1.0, 3.0))

            result = {
                "status": "completed",
                "analysis_results": {
                    "patterns_found": random.randint(3, 8),
                    "confidence_score": random.uniform(0.7, 0.95),
                    "anomalies_detected": random.randint(0, 2)
                },
                "recommendations": f"Based on analysis of {task.type}",
                "agent_id": self.agent_id
            }

            return result

        except Exception as e:
            logger.error(f"Analyzer task failed: {e}")
            return {"status": "failed", "error": str(e), "agent_id": self.agent_id}

    def can_handle_task(self, task: Task) -> float:
        """Evaluate capability to handle analysis tasks"""
        analysis_tasks = ["analysis", "pattern", "data", "statistics", "modeling"]

        if any(task_type in task.type.lower() for task_type in analysis_tasks):
            base_score = 0.9
        else:
            base_score = 0.2

        # Factor in current workload
        workload_factor = 0.7 if self.current_task else 1.0

        # Factor in relevant capabilities
        capability_score = sum(
            cap.proficiency for cap_name, cap in self.capabilities.items()
            if cap_name in task.required_capabilities
        ) / len(task.required_capabilities) if task.required_capabilities else 0.8

        return min(1.0, base_score * workload_factor * capability_score)

class DeveloperAgent(BaseAgent):
    """Developer agent for code generation and modification"""

    def __init__(self, agent_id: str):
        super().__init__(agent_id, AgentType.DEVELOPER)
        self.capabilities = {
            "code_generation": AgentCapability("code_generation", 0.8, 0, 0.8, datetime.now()),
            "code_review": AgentCapability("code_review", 0.7, 0, 0.7, datetime.now()),
            "debugging": AgentCapability("debugging", 0.75, 0, 0.75, datetime.now()),
            "optimization": AgentCapability("optimization", 0.6, 0, 0.6, datetime.now()),
            "testing": AgentCapability("testing", 0.65, 0, 0.65, datetime.now())
        }

    async def execute_task(self, task: Task) -> Dict[str, Any]:
        """Execute development task"""
        try:
            logger.info(f"Developer {self.agent_id} executing task: {task.description}")

            # Simulate development work
            await asyncio.sleep(random.uniform(2.0, 5.0))

            result = {
                "status": "completed",
                "code_changes": {
                    "files_modified": random.randint(1, 5),
                    "lines_added": random.randint(10, 100),
                    "lines_removed": random.randint(5, 50)
                },
                "test_results": {
                    "tests_passed": random.randint(8, 12),
                    "coverage": random.uniform(0.8, 0.95)
                },
                "agent_id": self.agent_id
            }

            return result

        except Exception as e:
            logger.error(f"Developer task failed: {e}")
            return {"status": "failed", "error": str(e), "agent_id": self.agent_id}

    def can_handle_task(self, task: Task) -> float:
        """Evaluate capability to handle development tasks"""
        dev_tasks = ["code", "develop", "implement", "debug", "test", "refactor"]

        if any(task_type in task.type.lower() for task_type in dev_tasks):
            base_score = 0.85
        else:
            base_score = 0.25

        # Factor in current workload
        workload_factor = 0.6 if self.current_task else 1.0

        # Factor in relevant capabilities
        capability_score = sum(
            cap.proficiency for cap_name, cap in self.capabilities.items()
            if cap_name in task.required_capabilities
        ) / len(task.required_capabilities) if task.required_capabilities else 0.75

        return min(1.0, base_score * workload_factor * capability_score)

class MultiAgentSystem:
    """Enhanced Multi-Agent System with specialized coordination"""

    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.task_queue: List[Task] = []
        self.completed_tasks: List[Task] = []
        self.is_running = False
        self.coordination_thread = None
        self.performance_metrics = {}
        self.task_assignment_strategy = "optimal"  # optimal, round_robin, random
        self.learning_enabled = True

        # Initialize default agents
        self._initialize_default_agents()

    def _initialize_default_agents(self):
        """Initialize default set of specialized agents"""
        self.add_agent(CoordinatorAgent("coord_001"))
        self.add_agent(AnalyzerAgent("analyzer_001"))
        self.add_agent(DeveloperAgent("dev_001"))

        logger.info(f"Initialized {len(self.agents)} default agents")

    def add_agent(self, agent: BaseAgent):
        """Add agent to the system"""
        self.agents[agent.agent_id] = agent
        logger.info(f"Added agent {agent.agent_id} of type {agent.agent_type.value}")

    def remove_agent(self, agent_id: str):
        """Remove agent from system"""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            if agent.current_task:
                # Reassign current task
                self.task_queue.insert(0, agent.current_task)
            del self.agents[agent_id]
            logger.info(f"Removed agent {agent_id}")

    def add_task(self, task: Task):
        """Add task to the queue"""
        self.task_queue.append(task)
        logger.info(f"Added task {task.id}: {task.description}")

    def create_task(self, task_type: str, description: str, priority: TaskPriority = TaskPriority.MEDIUM, 
                   required_capabilities: List[str] = None, deadline: datetime = None) -> Task:
        """Create and add a new task"""
        task = Task(
            id=f"task_{int(time.time())}_{random.randint(1000, 9999)}",
            type=task_type,
            description=description,
            priority=priority,
            required_capabilities=required_capabilities or [],
            created_at=datetime.now(),
            deadline=deadline
        )
        self.add_task(task)
        return task

    def _find_best_agent(self, task: Task) -> Optional[BaseAgent]:
        """Find best agent for task using current assignment strategy"""
        available_agents = [agent for agent in self.agents.values() 
                          if agent.is_active and agent.current_task is None]

        if not available_agents:
            return None

        if self.task_assignment_strategy == "optimal":
            # Find agent with highest capability score
            best_agent = None
            best_score = 0.0

            for agent in available_agents:
                score = agent.can_handle_task(task)
                if score > best_score:
                    best_score = score
                    best_agent = agent

            return best_agent if best_score > 0.3 else None

        elif self.task_assignment_strategy == "round_robin":
            # Simple round-robin assignment
            return available_agents[len(self.completed_tasks) % len(available_agents)]

        elif self.task_assignment_strategy == "random":
            return random.choice(available_agents)

        return None

    async def _assign_tasks(self):
        """Assign tasks to available agents"""
        # Sort tasks by priority and deadline
        self.task_queue.sort(key=lambda t: (t.priority.value, t.deadline or datetime.max), reverse=True)

        assigned_tasks = []
        for task in self.task_queue:
            if task.status == TaskStatus.PENDING:
                agent = self._find_best_agent(task)
                if agent:
                    task.assigned_agent = agent.agent_id
                    task.status = TaskStatus.ASSIGNED
                    agent.current_task = task
                    assigned_tasks.append(task)

                    logger.info(f"Assigned task {task.id} to agent {agent.agent_id}")

        # Remove assigned tasks from queue
        for task in assigned_tasks:
            self.task_queue.remove(task)

    async def _execute_agent_tasks(self):
        """Execute tasks for all agents with current assignments"""
        execution_tasks = []

        for agent in self.agents.values():
            if agent.current_task and agent.current_task.status == TaskStatus.ASSIGNED:
                execution_tasks.append(self._execute_single_task(agent))

        if execution_tasks:
            await asyncio.gather(*execution_tasks, return_exceptions=True)

    async def _execute_single_task(self, agent: BaseAgent):
        """Execute task for a single agent"""
        task = agent.current_task
        if not task:
            return

        start_time = time.time()
        task.status = TaskStatus.IN_PROGRESS

        try:
            result = await agent.execute_task(task)
            completion_time = time.time() - start_time

            if result.get("status") == "completed":
                task.status = TaskStatus.COMPLETED
                task.progress = 1.0
                success = True
            else:
                task.status = TaskStatus.FAILED
                success = False

            # Update agent performance and capabilities
            if self.learning_enabled:
                agent.update_performance(task, success, completion_time)
                for capability in task.required_capabilities:
                    agent.update_capability(capability, success)

            # Move task to completed
            agent.task_history.append(task)
            self.completed_tasks.append(task)
            agent.current_task = None

            logger.info(f"Task {task.id} completed by {agent.agent_id} in {completion_time:.2f}s")

        except Exception as e:
            task.status = TaskStatus.FAILED
            agent.current_task = None
            logger.error(f"Task {task.id} failed: {e}")

    async def _coordination_loop(self):
        """Main coordination loop"""
        while self.is_running:
            try:
                # Assign pending tasks
                await self._assign_tasks()

                # Execute assigned tasks
                await self._execute_agent_tasks()

                # Update system metrics
                self._update_metrics()

                # Brief pause between coordination cycles
                await asyncio.sleep(1.0)

            except Exception as e:
                logger.error(f"Coordination loop error: {e}")
                await asyncio.sleep(5.0)

    def _update_metrics(self):
        """Update system performance metrics"""
        total_tasks = len(self.completed_tasks)
        if total_tasks == 0:
            return

        completed_successfully = len([t for t in self.completed_tasks if t.status == TaskStatus.COMPLETED])

        self.performance_metrics = {
            "total_tasks_completed": total_tasks,
            "success_rate": completed_successfully / total_tasks,
            "active_agents": len([a for a in self.agents.values() if a.is_active]),
            "pending_tasks": len(self.task_queue),
            "average_agent_efficiency": sum(a.performance.efficiency_score for a in self.agents.values()) / len(self.agents),
            "last_updated": datetime.now()
        }

    def start(self):
        """Start the multi-agent system"""
        if not self.is_running:
            self.is_running = True
            self.coordination_thread = threading.Thread(target=self._run_coordination_loop)
            self.coordination_thread.daemon = True
            self.coordination_thread.start()
            logger.info("Multi-agent system started")

    def _run_coordination_loop(self):
        """Run coordination loop in thread"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._coordination_loop())

    def stop(self):
        """Stop the multi-agent system"""
        if self.is_running:
            self.is_running = False
            if self.coordination_thread:
                self.coordination_thread.join(timeout=10.0)
            logger.info("Multi-agent system stopped")

    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            "is_running": self.is_running,
            "agents": {
                agent_id: {
                    "type": agent.agent_type.value,
                    "active": agent.is_active,
                    "current_task": agent.current_task.id if agent.current_task else None,
                    "performance": asdict(agent.performance),
                    "capabilities": {name: asdict(cap) for name, cap in agent.capabilities.items()}
                }
                for agent_id, agent in self.agents.items()
            },
            "task_queue_size": len(self.task_queue),
            "completed_tasks": len(self.completed_tasks),
            "performance_metrics": self.performance_metrics,
            "assignment_strategy": self.task_assignment_strategy
        }

    def get_agent_recommendations(self, task_description: str) -> List[Dict[str, Any]]:
        """Get agent recommendations for a task"""
        # Create temporary task for evaluation
        temp_task = Task(
            id="temp",
            type="evaluation",
            description=task_description,
            priority=TaskPriority.MEDIUM,
            required_capabilities=[],
            created_at=datetime.now()
        )

        recommendations = []
        for agent in self.agents.values():
            score = agent.can_handle_task(temp_task)
            recommendations.append({
                "agent_id": agent.agent_id,
                "agent_type": agent.agent_type.value,
                "capability_score": score,
                "current_workload": agent.current_task is not None,
                "success_rate": agent.performance.success_rate,
                "efficiency": agent.performance.efficiency_score
            })

        # Sort by capability score
        recommendations.sort(key=lambda x: x["capability_score"], reverse=True)
        return recommendations

# Global multi-agent system instance
multi_agent_system = MultiAgentSystem()

def get_multi_agent_system() -> MultiAgentSystem:
    """Get global multi-agent system instance"""
    return multi_agent_system

def initialize_multi_agent_system():
    """Initialize and start the multi-agent system"""
    try:
        multi_agent_system.start()
        logger.info("Multi-agent system initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize multi-agent system: {e}")
        return False

def shutdown_multi_agent_system():
    """Shutdown the multi-agent system"""
    try:
        multi_agent_system.stop()
        logger.info("Multi-agent system shutdown successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to shutdown multi-agent system: {e}")
        return False


# Export aliases for main.py compatibility
Agent = BaseAgent  # Alias for backwards compatibility
AIAgent = BaseAgent  # Alternative alias

# Public API exports
__all__ = [
    'Agent',
    'AIAgent', 
    'BaseAgent',
    'CoordinatorAgent',
    'AnalyzerAgent', 
    'DeveloperAgent',
    'MultiAgentSystem',
    'AgentType',
    'TaskPriority',
    'TaskStatus',
    'AgentCapability',
    'Task',
    'AgentPerformance',
    'get_multi_agent_system',
    'initialize_multi_agent_system',
    'shutdown_multi_agent_system'
]
