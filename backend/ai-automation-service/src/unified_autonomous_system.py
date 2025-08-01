#!/usr/bin/env python3
"""
Unified Autonomous System
Integrates all autonomous components into a cohesive self-improving ecosystem
Coordinates between orchestrator, improvement engines, GitHub integration, and meta-learning
"""

import asyncio
import logging
import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import signal
import sys
from pathlib import Path

# Import all autonomous systems
try:
    from integration_orchestrator import AutonomousOrchestrator, OrchestrationConfig, SystemState
    from github_integration import GitHubSelfImprovementEngine, ImprovementPlan, CodeChange
    from self_monitoring import SelfMonitoringSystem, monitoring_system
    from autonomous_improvement_engine import AutonomousImprovementEngine, AutonomousImprovement
    from self_improvement_meta_system import SelfImprovementMetaSystem, SelfImprovementAction
    from enhanced_github_client import EnhancedGitHubClient, GitHubClientManager
    from autonomous_eliza import AutonomousElizaOS, autonomous_eliza
    from gpt5_adapter import gpt5_adapter, check_gpt5_migration
except ImportError as e:
    logging.error(f"Failed to import required modules: {e}")
    logger.error("UnifiedAutonomousSystem forced exit removed. Check logs for details.") # sys.exit(1) removed

class UnifiedSystemState(Enum):
    INITIALIZING = "initializing"
    RUNNING = "running"
    SELF_IMPROVING = "self_improving"
    LEARNING = "learning"
    OPTIMIZING = "optimizing"
    EMERGENCY = "emergency"
    STOPPING = "stopping"
    STOPPED = "stopped"

@dataclass
class SystemIntegrationConfig:
    # Core system enables
    orchestrator_enabled: bool = True
    github_integration_enabled: bool = True
    improvement_engine_enabled: bool = True
    meta_learning_enabled: bool = True
    monitoring_enabled: bool = True
    eliza_core_enabled: bool = True
    
    # Integration settings
    cross_system_learning: bool = True
    unified_decision_making: bool = True
    shared_memory_enabled: bool = True
    coordinated_improvements: bool = True
    
    # Performance settings
    max_concurrent_operations: int = 5
    system_sync_interval: int = 300  # 5 minutes
    cross_validation_enabled: bool = True
    unified_logging: bool = True
    
    # Safety settings
    emergency_coordination: bool = True
    unified_rollback: bool = True
    cross_system_validation: bool = True
    safety_threshold: float = 0.85

class UnifiedAutonomousSystem:
    """
    Master unified system that coordinates all autonomous components
    Provides seamless integration and cross-system learning capabilities
    """
    
    def __init__(self, config: SystemIntegrationConfig = None):
        self.config = config or SystemIntegrationConfig()
        self.state = UnifiedSystemState.INITIALIZING
        self.start_time = datetime.now()
        
        # Initialize logging
        self.setup_unified_logging()
        self.logger = logging.getLogger(__name__)
        
        # System components
        self.orchestrator = None
        self.github_engine = None
        self.improvement_engine = None
        self.meta_system = None
        self.monitoring_system = None
        self.eliza_core = None
        self.github_client_manager = None
        
        # Integration state
        self.system_metrics = {}
        self.shared_memory = {}
        self.cross_system_insights = []
        self.unified_improvement_queue = []
        
        # Performance tracking
        self.total_improvements = 0
        self.cross_system_learnings = 0
        self.unified_decisions = 0
        self.system_efficiency_score = 0.0
        
        self.logger.info("🌟 Unified Autonomous System Initializing")
    
    def setup_unified_logging(self):
        """Setup unified logging across all systems"""
        if self.config.unified_logging:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - [UNIFIED] %(message)s',
                handlers=[
                    logging.FileHandler('unified_autonomous_system.log'),
                    logging.FileHandler('cross_system_insights.log'),
                    logging.StreamHandler()
                ]
            )
    
    async def initialize_unified_system(self):
        """Initialize all system components with unified coordination"""
        self.logger.info("🚀 Initializing Unified Autonomous System")
        
        try:
            # Initialize GitHub credentials
            github_token = os.getenv("GITHUB_PAT")
            github_owner = os.getenv("GITHUB_USERNAME", "DevGruGold")
            github_repo = "XMRT-Ecosystem"
            
            if not github_token:
                self.logger.error("GitHub PAT not found in environment variables")
                return False
            
            # Initialize GitHub Client Manager
            if self.config.github_integration_enabled:
                self.github_client_manager = GitHubClientManager(
                    token=github_token,
                    repo_name=github_repo,
                    owner=github_owner
                )
                self.logger.info("✅ GitHub Client Manager initialized")
            
            # Initialize Orchestrator
            if self.config.orchestrator_enabled:
                orchestration_config = OrchestrationConfig(
                    monitoring_enabled=self.config.monitoring_enabled,
                    github_integration_enabled=self.config.github_integration_enabled,
                    autonomous_improvement_enabled=self.config.improvement_engine_enabled,
                    meta_learning_enabled=self.config.meta_learning_enabled
                )
                self.orchestrator = AutonomousOrchestrator(orchestration_config)
                await self.orchestrator.initialize_all_systems()
                self.logger.info("✅ Orchestrator initialized")
            
            # Initialize GitHub Integration Engine
            if self.config.github_integration_enabled:
                self.github_engine = GitHubSelfImprovementEngine(
                    repo_owner=github_owner,
                    repo_name=github_repo,
                    pat_token=github_token
                )
                self.logger.info("✅ GitHub Integration Engine initialized")
            
            # Initialize Autonomous Improvement Engine
            if self.config.improvement_engine_enabled:
                self.improvement_engine = AutonomousImprovementEngine(
                    github_client=self.github_client_manager.get_basic_client(),
                    project_root="/home/ubuntu/XMRT-Ecosystem"
                )
                self.logger.info("✅ Autonomous Improvement Engine initialized")
            
            # Initialize Meta-Learning System
            if self.config.meta_learning_enabled:
                self.meta_system = SelfImprovementMetaSystem([
                    "autonomous_improvement_engine",
                    "github_integration_engine",
                    "orchestrator",
                    "monitoring_system",
                    "unified_autonomous_system"
                ])
                self.logger.info("✅ Meta-Learning System initialized")
            
            # Initialize Monitoring System
            if self.config.monitoring_enabled:
                self.monitoring_system = monitoring_system
                self.logger.info("✅ Monitoring System initialized")
            
            # Initialize Eliza Core
            if self.config.eliza_core_enabled:
                self.eliza_core = autonomous_eliza
                self.logger.info("✅ Eliza Core initialized")
            
            self.state = UnifiedSystemState.RUNNING
            self.logger.info("🌟 Unified Autonomous System fully initialized and running")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize unified system: {e}")
            self.state = UnifiedSystemState.EMERGENCY
            return False
    
    async def start_unified_operations(self):
        """Start all unified autonomous operations"""
        self.logger.info("🚀 Starting Unified Autonomous Operations")
        
        if not await self.initialize_unified_system():
            self.logger.error("Failed to initialize system, aborting startup")
            return
        
        # Start all system tasks concurrently
        tasks = []
        
        # Core orchestration loop
        if self.orchestrator:
            tasks.append(self.orchestrator.start_orchestration())
        
        # Unified improvement coordination
        tasks.append(self.unified_improvement_coordinator())
        
        # Cross-system learning loop
        if self.config.cross_system_learning:
            tasks.append(self.cross_system_learning_loop())
        
        # Unified decision making
        if self.config.unified_decision_making:
            tasks.append(self.unified_decision_maker())
        
        # System synchronization
        tasks.append(self.system_synchronization_loop())
        
        # Performance optimization
        tasks.append(self.performance_optimization_loop())
        
        # Emergency coordination
        if self.config.emergency_coordination:
            tasks.append(self.emergency_coordination_loop())
        
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            self.logger.error(f"Error in unified operations: {e}")
            await self.emergency_shutdown()
    
    async def unified_improvement_coordinator(self):
        """Coordinate improvements across all systems"""
        while self.state in [UnifiedSystemState.RUNNING, UnifiedSystemState.SELF_IMPROVING]:
            try:
                self.logger.info("🔄 Starting unified improvement coordination cycle")
                
                # Collect improvement opportunities from all systems
                all_improvements = await self.collect_all_improvements()
                
                # Prioritize improvements using unified criteria
                prioritized_improvements = await self.prioritize_unified_improvements(all_improvements)
                
                # Execute coordinated improvements
                for improvement in prioritized_improvements[:self.config.max_concurrent_operations]:
                    await self.execute_coordinated_improvement(improvement)
                
                # Learn from results across systems
                await self.cross_system_learning_update()
                
                await asyncio.sleep(1800)  # 30 minutes between cycles
                
            except Exception as e:
                self.logger.error(f"Error in unified improvement coordinator: {e}")
                await asyncio.sleep(3600)
    
    async def collect_all_improvements(self) -> List[Dict[str, Any]]:
        """Collect improvement opportunities from all systems"""
        all_improvements = []
        
        try:
            # From GitHub Integration Engine
            if self.github_engine:
                github_improvements = await self.github_engine.analyze_repository_for_improvements()
                for improvement in github_improvements:
                    all_improvements.append({
                        "source": "github_engine",
                        "type": "repository_improvement",
                        "data": improvement,
                        "priority": improvement.priority if hasattr(improvement, 'priority') else "medium",
                        "confidence": getattr(improvement, 'estimated_impact', 0.5)
                    })
            
            # From Autonomous Improvement Engine
            if self.improvement_engine:
                code_analysis = await self.improvement_engine.analyze_entire_codebase()
                engine_improvements = await self.improvement_engine.identify_improvements(code_analysis)
                for improvement in engine_improvements:
                    all_improvements.append({
                        "source": "improvement_engine",
                        "type": "code_improvement",
                        "data": improvement,
                        "priority": improvement.priority.value if hasattr(improvement, 'priority') else "medium",
                        "confidence": improvement.confidence_score
                    })
            
            # From Meta-Learning System
            if self.meta_system:
                meta_analysis = await self.meta_system.perform_deep_self_analysis()
                meta_opportunities = await self.meta_system.identify_meta_improvements(meta_analysis)
                for opportunity in meta_opportunities:
                    all_improvements.append({
                        "source": "meta_system",
                        "type": "meta_improvement",
                        "data": opportunity,
                        "priority": opportunity.get("priority", "medium"),
                        "confidence": opportunity.get("confidence", 0.5)
                    })
            
            self.logger.info(f"📊 Collected {len(all_improvements)} improvement opportunities")
            return all_improvements
            
        except Exception as e:
            self.logger.error(f"Error collecting improvements: {e}")
            return []
    
    async def prioritize_unified_improvements(self, improvements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioritize improvements using unified criteria across all systems"""
        
        def unified_priority_score(improvement: Dict[str, Any]) -> float:
            # Base priority weights
            priority_weights = {
                "critical": 1.0,
                "high": 0.8,
                "medium": 0.6,
                "low": 0.4
            }
            
            # Source system weights
            source_weights = {
                "meta_system": 1.0,  # Highest priority for meta-improvements
                "improvement_engine": 0.9,
                "github_engine": 0.8,
                "monitoring_system": 0.7
            }
            
            # Type weights
            type_weights = {
                "meta_improvement": 1.0,
                "security_improvement": 0.95,
                "performance_optimization": 0.9,
                "code_improvement": 0.8,
                "repository_improvement": 0.7
            }
            
            base_score = (
                priority_weights.get(improvement.get("priority", "medium"), 0.6) * 0.4 +
                source_weights.get(improvement.get("source", "unknown"), 0.5) * 0.3 +
                type_weights.get(improvement.get("type", "unknown"), 0.5) * 0.2 +
                improvement.get("confidence", 0.5) * 0.1
            )
            
            return base_score
        
        # Sort by unified priority score
        sorted_improvements = sorted(improvements, key=unified_priority_score, reverse=True)
        
        # Filter by minimum confidence threshold
        high_confidence_improvements = [
            imp for imp in sorted_improvements
            if imp.get("confidence", 0.0) >= self.config.safety_threshold
        ]
        
        self.logger.info(f"🎯 Prioritized {len(high_confidence_improvements)} high-confidence improvements")
        return high_confidence_improvements
    
    async def execute_coordinated_improvement(self, improvement: Dict[str, Any]):
        """Execute improvement with coordination across systems"""
        try:
            self.logger.info(f"🔧 Executing coordinated improvement from {improvement['source']}")
            
            # Pre-execution validation across systems
            if self.config.cross_system_validation:
                validation_result = await self.cross_system_validation(improvement)
                if not validation_result["valid"]:
                    self.logger.warning(f"❌ Cross-system validation failed: {validation_result['reason']}")
                    return False
            
            # Execute based on source system
            source = improvement["source"]
            success = False
            
            if source == "github_engine" and self.github_engine:
                success = await self.execute_github_improvement(improvement)
            elif source == "improvement_engine" and self.improvement_engine:
                success = await self.execute_engine_improvement(improvement)
            elif source == "meta_system" and self.meta_system:
                success = await self.execute_meta_improvement(improvement)
            
            if success:
                self.total_improvements += 1
                await self.record_improvement_success(improvement)
                self.logger.info(f"✅ Successfully executed improvement from {source}")
            else:
                await self.record_improvement_failure(improvement)
                self.logger.error(f"❌ Failed to execute improvement from {source}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error executing coordinated improvement: {e}")
            return False
    
    async def execute_github_improvement(self, improvement: Dict[str, Any]) -> bool:
        """Execute GitHub-based improvement"""
        try:
            improvement_plan = improvement["data"]
            
            # Use GitHub engine to implement the improvement
            if hasattr(improvement_plan, 'changes'):
                for change in improvement_plan.changes:
                    # Create branch and implement change
                    branch_name = f"unified-improvement-{int(time.time())}"
                    
                    # Use enhanced GitHub client for implementation
                    enhanced_client = self.github_client_manager.get_enhanced_client()
                    
                    # Create autonomous branch
                    branch_created = await enhanced_client.create_autonomous_branch(branch_name)
                    
                    if branch_created:
                        # Commit changes
                        file_changes = {change.file_path: change.new_content}
                        commit_success = await enhanced_client.commit_multiple_files(
                            branch_name,
                            file_changes,
                            f"🤖 Unified improvement: {improvement_plan.title}",
                            improvement_plan.description
                        )
                        
                        if commit_success:
                            # Create PR
                            pr_url = await enhanced_client.create_autonomous_pull_request(
                                improvement_plan.title,
                                improvement_plan.description,
                                branch_name,
                                auto_merge=change.confidence_score > 0.95,
                                confidence_score=change.confidence_score
                            )
                            
                            if pr_url:
                                self.logger.info(f"✅ Created PR for GitHub improvement: {pr_url}")
                                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error executing GitHub improvement: {e}")
            return False
    
    async def execute_engine_improvement(self, improvement: Dict[str, Any]) -> bool:
        """Execute improvement engine-based improvement"""
        try:
            improvement_data = improvement["data"]
            
            # Use improvement engine to implement
            if hasattr(improvement_data, 'improvement_id'):
                success = await self.improvement_engine.implement_autonomous_improvement(improvement_data)
                return success
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error executing engine improvement: {e}")
            return False
    
    async def execute_meta_improvement(self, improvement: Dict[str, Any]) -> bool:
        """Execute meta-system improvement"""
        try:
            improvement_data = improvement["data"]
            
            # Create meta-improvement action
            if isinstance(improvement_data, dict):
                from self_improvement_meta_system import SelfImprovementAction, MetaImprovementType
                
                action = SelfImprovementAction(
                    action_id=f"unified_{int(time.time())}",
                    improvement_type=MetaImprovementType.RECURSIVE_IMPROVEMENT,
                    target_system="unified_system",
                    current_performance=self.system_metrics,
                    expected_improvement=improvement_data.get("expected_improvement", {}),
                    implementation_strategy=improvement_data.get("strategy", ""),
                    risk_assessment=improvement_data.get("risk", 0.5),
                    confidence_score=improvement_data.get("confidence", 0.5),
                    meta_reasoning=improvement_data.get("reasoning", ""),
                    validation_criteria=improvement_data.get("validation", []),
                    rollback_strategy=improvement_data.get("rollback", ""),
                    created_at=datetime.now()
                )
                
                success = await self.meta_system.execute_self_improvement(action)
                return success
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error executing meta improvement: {e}")
            return False
    
    async def cross_system_validation(self, improvement: Dict[str, Any]) -> Dict[str, Any]:
        """Validate improvement across all systems"""
        try:
            validation_results = []
            
            # Validate with monitoring system
            if self.monitoring_system:
                monitor_validation = await self.validate_with_monitoring(improvement)
                validation_results.append(monitor_validation)
            
            # Validate with meta-system
            if self.meta_system:
                meta_validation = await self.validate_with_meta_system(improvement)
                validation_results.append(meta_validation)
            
            # Validate with orchestrator
            if self.orchestrator:
                orchestrator_validation = await self.validate_with_orchestrator(improvement)
                validation_results.append(orchestrator_validation)
            
            # Aggregate validation results
            all_valid = all(result.get("valid", False) for result in validation_results)
            
            return {
                "valid": all_valid,
                "reason": "Cross-system validation passed" if all_valid else "One or more systems rejected the improvement",
                "details": validation_results
            }
            
        except Exception as e:
            self.logger.error(f"Error in cross-system validation: {e}")
            return {"valid": False, "reason": f"Validation error: {e}"}
    
    async def cross_system_learning_loop(self):
        """Continuous cross-system learning and knowledge sharing"""
        while self.state == UnifiedSystemState.RUNNING:
            try:
                self.logger.info("🧠 Starting cross-system learning cycle")
                
                # Collect insights from all systems
                insights = await self.collect_cross_system_insights()
                
                # Analyze patterns across systems
                patterns = await self.analyze_cross_system_patterns(insights)
                
                # Share learnings across systems
                await self.share_learnings_across_systems(patterns)
                
                # Update unified knowledge base
                await self.update_unified_knowledge_base(patterns)
                
                self.cross_system_learnings += 1
                
                await asyncio.sleep(3600)  # Learn every hour
                
            except Exception as e:
                self.logger.error(f"Error in cross-system learning: {e}")
                await asyncio.sleep(1800)
    
    async def unified_decision_maker(self):
        """Unified decision making across all systems"""
        while self.state == UnifiedSystemState.RUNNING:
            try:
                # Collect pending decisions from all systems
                pending_decisions = await self.collect_pending_decisions()
                
                # Make unified decisions
                for decision in pending_decisions:
                    unified_decision = await self.make_unified_decision(decision)
                    await self.execute_unified_decision(unified_decision)
                    self.unified_decisions += 1
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error in unified decision making: {e}")
                await asyncio.sleep(600)
    
    async def system_synchronization_loop(self):
        """Synchronize state across all systems"""
        while self.state == UnifiedSystemState.RUNNING:
            try:
                # Synchronize system states
                await self.synchronize_system_states()
                
                # Update shared memory
                await self.update_shared_memory()
                
                # Coordinate system metrics
                await self.coordinate_system_metrics()
                
                await asyncio.sleep(self.config.system_sync_interval)
                
            except Exception as e:
                self.logger.error(f"Error in system synchronization: {e}")
                await asyncio.sleep(600)
    
    async def performance_optimization_loop(self):
        """Continuously optimize system performance"""
        while self.state == UnifiedSystemState.RUNNING:
            try:
                self.state = UnifiedSystemState.OPTIMIZING
                
                # Analyze system performance
                performance_analysis = await self.analyze_unified_performance()
                
                # Identify optimization opportunities
                optimizations = await self.identify_performance_optimizations(performance_analysis)
                
                # Apply optimizations
                for optimization in optimizations:
                    await self.apply_performance_optimization(optimization)
                
                # Update efficiency score
                self.system_efficiency_score = await self.calculate_efficiency_score()
                
                self.state = UnifiedSystemState.RUNNING
                
                await asyncio.sleep(7200)  # Optimize every 2 hours
                
            except Exception as e:
                self.logger.error(f"Error in performance optimization: {e}")
                self.state = UnifiedSystemState.RUNNING
                await asyncio.sleep(3600)
    
    async def emergency_coordination_loop(self):
        """Emergency coordination across all systems"""
        while self.state != UnifiedSystemState.STOPPED:
            try:
                # Check for emergency conditions
                emergency_status = await self.check_emergency_conditions()
                
                if emergency_status["emergency"]:
                    self.state = UnifiedSystemState.EMERGENCY
                    await self.coordinate_emergency_response(emergency_status)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Error in emergency coordination: {e}")
                await asyncio.sleep(300)
    
    def get_unified_system_status(self) -> Dict[str, Any]:
        """Get comprehensive status of the unified system"""
        return {
            "state": self.state.value,
            "uptime": (datetime.now() - self.start_time).total_seconds(),
            "total_improvements": self.total_improvements,
            "cross_system_learnings": self.cross_system_learnings,
            "unified_decisions": self.unified_decisions,
            "system_efficiency_score": self.system_efficiency_score,
            "active_systems": {
                "orchestrator": self.orchestrator is not None,
                "github_engine": self.github_engine is not None,
                "improvement_engine": self.improvement_engine is not None,
                "meta_system": self.meta_system is not None,
                "monitoring_system": self.monitoring_system is not None,
                "eliza_core": self.eliza_core is not None
            },
            "system_metrics": self.system_metrics,
            "shared_memory_size": len(self.shared_memory),
            "improvement_queue_size": len(self.unified_improvement_queue)
        }
    
    # Placeholder implementations for complex methods
    async def validate_with_monitoring(self, improvement: Dict[str, Any]) -> Dict[str, Any]:
        return {"valid": True, "source": "monitoring_system"}
    
    async def validate_with_meta_system(self, improvement: Dict[str, Any]) -> Dict[str, Any]:
        return {"valid": True, "source": "meta_system"}
    
    async def validate_with_orchestrator(self, improvement: Dict[str, Any]) -> Dict[str, Any]:
        return {"valid": True, "source": "orchestrator"}
    
    async def record_improvement_success(self, improvement: Dict[str, Any]):
        self.shared_memory[f"success_{int(time.time())}"] = improvement
    
    async def record_improvement_failure(self, improvement: Dict[str, Any]):
        self.shared_memory[f"failure_{int(time.time())}"] = improvement
    
    async def collect_cross_system_insights(self) -> List[Dict[str, Any]]:
        return []
    
    async def analyze_cross_system_patterns(self, insights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return []
    
    async def share_learnings_across_systems(self, patterns: List[Dict[str, Any]]):
        pass
    
    async def update_unified_knowledge_base(self, patterns: List[Dict[str, Any]]):
        pass
    
    async def collect_pending_decisions(self) -> List[Dict[str, Any]]:
        return []
    
    async def make_unified_decision(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        return decision
    
    async def execute_unified_decision(self, decision: Dict[str, Any]):
        pass
    
    async def synchronize_system_states(self):
        pass
    
    async def update_shared_memory(self):
        pass
    
    async def coordinate_system_metrics(self):
        pass
    
    async def analyze_unified_performance(self) -> Dict[str, Any]:
        return {}
    
    async def identify_performance_optimizations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        return []
    
    async def apply_performance_optimization(self, optimization: Dict[str, Any]):
        pass
    
    async def calculate_efficiency_score(self) -> float:
        return 0.85
    
    async def check_emergency_conditions(self) -> Dict[str, Any]:
        return {"emergency": False}
    
    async def coordinate_emergency_response(self, emergency_status: Dict[str, Any]):
        pass
    
    async def emergency_shutdown(self):
        """Emergency shutdown of all systems"""
        self.logger.warning("🚨 Emergency shutdown initiated")
        self.state = UnifiedSystemState.STOPPING
        
        # Stop all systems gracefully
        if self.orchestrator:
            await self.orchestrator.stop_orchestration()
        
        self.state = UnifiedSystemState.STOPPED
        self.logger.info("🛑 Emergency shutdown completed")

# Global unified system instance
unified_system = UnifiedAutonomousSystem()

async def main():
    """Main entry point for the unified autonomous system"""
    try:
        # Setup signal handlers for graceful shutdown
        def signal_handler(signum, frame):
            logging.info(f"Received signal {signum}, initiating graceful shutdown...")
            asyncio.create_task(unified_system.emergency_shutdown())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Start the unified system
        await unified_system.start_unified_operations()
        
    except KeyboardInterrupt:
        logging.info("Keyboard interrupt received, shutting down...")
        await unified_system.emergency_shutdown()
    except Exception as e:
        logging.error(f"Fatal error in unified system: {e}")
        await unified_system.emergency_shutdown()

if __name__ == "__main__":
    asyncio.run(main())

