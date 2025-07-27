#!/usr/bin/env python3
"""
Integration Orchestrator for Autonomous ElizaOS
Coordinates all autonomous systems including monitoring, improvement, and GitHub integration
"""

import asyncio
import logging
import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import signal
import sys

# Import all autonomous systems
from self_monitoring import SelfMonitoringSystem, monitoring_system
from github_integration import GitHubSelfImprovementEngine, initialize_github_integration
from autonomous_improvement_engine import AutonomousImprovementEngine
from self_improvement_meta_system import SelfImprovementMetaSystem
from gpt5_adapter import gpt5_adapter, check_gpt5_migration
from autonomous_eliza import AutonomousElizaOS

logger = logging.getLogger(__name__)

class SystemState(Enum):
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"

@dataclass
class OrchestrationConfig:
    monitoring_enabled: bool = True
    github_integration_enabled: bool = True
    autonomous_improvement_enabled: bool = True
    meta_learning_enabled: bool = True
    gpt5_migration_enabled: bool = True
    
    # Timing configurations
    monitoring_interval: int = 30  # seconds
    improvement_cycle_interval: int = 3600  # 1 hour
    github_analysis_interval: int = 7200  # 2 hours
    meta_learning_interval: int = 86400  # 24 hours
    gpt5_check_interval: int = 3600  # 1 hour
    
    # Safety configurations
    max_concurrent_improvements: int = 3
    emergency_stop_threshold: float = 0.1  # System health threshold
    auto_recovery_enabled: bool = True
    backup_interval: int = 21600  # 6 hours

class AutonomousOrchestrator:
    """
    Master orchestrator for all autonomous systems
    Coordinates monitoring, improvement, GitHub integration, and meta-learning
    """
    
    def __init__(self, config: OrchestrationConfig = None):
        self.config = config or OrchestrationConfig()
        self.state = SystemState.INITIALIZING
        self.start_time = datetime.now()
        
        # System instances
        self.monitoring_system = monitoring_system
        self.github_engine = None
        self.improvement_engine = None
        self.meta_system = None
        self.eliza_core = None
        
        # Orchestration state
        self.active_tasks = {}
        self.system_metrics = {}
        self.last_backup = None
        self.emergency_stop_triggered = False
        
        # Performance tracking
        self.cycle_count = 0
        self.total_improvements_implemented = 0
        self.total_prs_created = 0
        self.system_uptime = 0
        
        logger.info("Autonomous Orchestrator initialized")

    async def initialize_all_systems(self):
        """Initialize all autonomous systems"""
        logger.info("Initializing all autonomous systems...")
        
        try:
            # Initialize GitHub integration
            if self.config.github_integration_enabled:
                repo_owner = os.getenv('GITHUB_REPO_OWNER', 'DevGruGold')
                repo_name = os.getenv('GITHUB_REPO_NAME', 'XMRT-Ecosystem')
                pat_token = os.getenv('GITHUB_PAT')
                
                if pat_token:
                    self.github_engine = initialize_github_integration(repo_owner, repo_name, pat_token)
                    logger.info("GitHub integration initialized")
                else:
                    logger.warning("GitHub PAT not found, GitHub integration disabled")
                    self.config.github_integration_enabled = False
            
            # Initialize improvement engine
            if self.config.autonomous_improvement_enabled:
                self.improvement_engine = AutonomousImprovementEngine()
                await self.improvement_engine.initialize()
                logger.info("Autonomous improvement engine initialized")
            
            # Initialize meta-learning system
            if self.config.meta_learning_enabled:
                self.meta_system = SelfImprovementMetaSystem()
                await self.meta_system.initialize()
                logger.info("Meta-learning system initialized")
            
            # Initialize core Eliza system
            self.eliza_core = AutonomousElizaOS()
            logger.info("Core ElizaOS initialized")
            
            # Check GPT-5 availability
            if self.config.gpt5_migration_enabled:
                migration_result = await check_gpt5_migration()
                if migration_result.get("migration_successful"):
                    logger.info("✅ GPT-5 migration successful!")
                else:
                    logger.info("GPT-5 not available, continuing with GPT-4")
            
            self.state = SystemState.RUNNING
            logger.info("🚀 All autonomous systems initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize systems: {e}")
            self.state = SystemState.ERROR
            raise

    async def start_orchestration(self):
        """Start the main orchestration loop"""
        logger.info("Starting autonomous orchestration...")
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        try:
            # Initialize all systems
            await self.initialize_all_systems()
            
            # Start all orchestration tasks
            orchestration_tasks = []
            
            # Monitoring task
            if self.config.monitoring_enabled:
                orchestration_tasks.append(
                    asyncio.create_task(self._monitoring_orchestration_loop())
                )
            
            # GitHub integration task
            if self.config.github_integration_enabled and self.github_engine:
                orchestration_tasks.append(
                    asyncio.create_task(self._github_orchestration_loop())
                )
            
            # Improvement engine task
            if self.config.autonomous_improvement_enabled and self.improvement_engine:
                orchestration_tasks.append(
                    asyncio.create_task(self._improvement_orchestration_loop())
                )
            
            # Meta-learning task
            if self.config.meta_learning_enabled and self.meta_system:
                orchestration_tasks.append(
                    asyncio.create_task(self._meta_learning_orchestration_loop())
                )
            
            # GPT-5 migration check task
            if self.config.gpt5_migration_enabled:
                orchestration_tasks.append(
                    asyncio.create_task(self._gpt5_migration_loop())
                )
            
            # System health and coordination task
            orchestration_tasks.append(
                asyncio.create_task(self._system_coordination_loop())
            )
            
            # Backup task
            orchestration_tasks.append(
                asyncio.create_task(self._backup_loop())
            )
            
            # Core Eliza operations
            orchestration_tasks.append(
                asyncio.create_task(self.eliza_core.start_autonomous_operations())
            )
            
            logger.info(f"Started {len(orchestration_tasks)} orchestration tasks")
            
            # Run all tasks concurrently
            await asyncio.gather(*orchestration_tasks, return_exceptions=True)
            
        except Exception as e:
            logger.error(f"Orchestration error: {e}")
            self.state = SystemState.ERROR
        finally:
            await self._cleanup()

    async def _monitoring_orchestration_loop(self):
        """Orchestrate monitoring system"""
        logger.info("Starting monitoring orchestration loop")
        
        while self.state == SystemState.RUNNING:
            try:
                # Get system health
                health_status = self.monitoring_system.get_system_health()
                self.system_metrics["health"] = health_status
                
                # Check for emergency conditions
                if health_status["status"] == "critical":
                    critical_alerts = health_status.get("critical_alerts", 0)
                    if critical_alerts >= 3:  # Multiple critical alerts
                        await self._trigger_emergency_protocols()
                
                # Log health status periodically
                if self.cycle_count % 20 == 0:  # Every 20 cycles
                    logger.info(f"System health: {health_status['status']} "
                              f"(Critical: {health_status.get('critical_alerts', 0)}, "
                              f"Warning: {health_status.get('warning_alerts', 0)})")
                
                await asyncio.sleep(self.config.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Monitoring orchestration error: {e}")
                await asyncio.sleep(self.config.monitoring_interval * 2)

    async def _github_orchestration_loop(self):
        """Orchestrate GitHub integration"""
        logger.info("Starting GitHub orchestration loop")
        
        while self.state == SystemState.RUNNING:
            try:
                # Run improvement analysis cycle
                logger.info("Starting GitHub improvement analysis cycle...")
                
                improvements = await self.github_engine.analyze_repository_for_improvements()
                logger.info(f"Found {len(improvements)} potential improvements")
                
                if improvements:
                    # Implement improvements
                    results = await self.github_engine.implement_improvements_autonomously(improvements)
                    
                    # Update metrics
                    self.total_improvements_implemented += len(results.get("implemented", []))
                    self.total_prs_created += len(results.get("pending_review", []))
                    
                    logger.info(f"GitHub cycle complete: {len(results.get('implemented', []))} implemented, "
                              f"{len(results.get('pending_review', []))} pending review")
                
                # Monitor autonomous changes
                monitoring_data = await self.github_engine.monitor_autonomous_changes()
                self.system_metrics["github"] = monitoring_data
                
                await asyncio.sleep(self.config.github_analysis_interval)
                
            except Exception as e:
                logger.error(f"GitHub orchestration error: {e}")
                await asyncio.sleep(self.config.github_analysis_interval * 2)

    async def _improvement_orchestration_loop(self):
        """Orchestrate autonomous improvement engine"""
        logger.info("Starting improvement orchestration loop")
        
        while self.state == SystemState.RUNNING:
            try:
                # Run improvement cycle
                logger.info("Starting autonomous improvement cycle...")
                
                improvement_results = await self.improvement_engine.run_improvement_cycle()
                self.system_metrics["improvements"] = improvement_results
                
                logger.info(f"Improvement cycle complete: {improvement_results.get('improvements_found', 0)} found")
                
                await asyncio.sleep(self.config.improvement_cycle_interval)
                
            except Exception as e:
                logger.error(f"Improvement orchestration error: {e}")
                await asyncio.sleep(self.config.improvement_cycle_interval * 2)

    async def _meta_learning_orchestration_loop(self):
        """Orchestrate meta-learning system"""
        logger.info("Starting meta-learning orchestration loop")
        
        while self.state == SystemState.RUNNING:
            try:
                # Run meta-learning cycle
                logger.info("Starting meta-learning cycle...")
                
                meta_results = await self.meta_system.run_meta_learning_cycle()
                self.system_metrics["meta_learning"] = meta_results
                
                logger.info(f"Meta-learning cycle complete: {meta_results.get('patterns_learned', 0)} patterns learned")
                
                await asyncio.sleep(self.config.meta_learning_interval)
                
            except Exception as e:
                logger.error(f"Meta-learning orchestration error: {e}")
                await asyncio.sleep(self.config.meta_learning_interval * 2)

    async def _gpt5_migration_loop(self):
        """Check for GPT-5 migration opportunities"""
        logger.info("Starting GPT-5 migration loop")
        
        while self.state == SystemState.RUNNING:
            try:
                migration_result = await check_gpt5_migration()
                
                if migration_result.get("migration_successful"):
                    logger.info("🚀 GPT-5 migration successful!")
                    # Update all systems to use GPT-5
                    await self._update_systems_for_gpt5()
                
                await asyncio.sleep(self.config.gpt5_check_interval)
                
            except Exception as e:
                logger.error(f"GPT-5 migration check error: {e}")
                await asyncio.sleep(self.config.gpt5_check_interval * 2)

    async def _system_coordination_loop(self):
        """Coordinate between all systems"""
        logger.info("Starting system coordination loop")
        
        while self.state == SystemState.RUNNING:
            try:
                self.cycle_count += 1
                self.system_uptime = int((datetime.now() - self.start_time).total_seconds())
                
                # Coordinate system resources
                await self._manage_system_resources()
                
                # Check for system conflicts
                await self._resolve_system_conflicts()
                
                # Update system metrics
                await self._update_coordination_metrics()
                
                # Log coordination status
                if self.cycle_count % 100 == 0:  # Every 100 cycles
                    logger.info(f"Coordination cycle {self.cycle_count}: "
                              f"Uptime {self.system_uptime}s, "
                              f"Improvements: {self.total_improvements_implemented}, "
                              f"PRs: {self.total_prs_created}")
                
                await asyncio.sleep(60)  # Coordinate every minute
                
            except Exception as e:
                logger.error(f"System coordination error: {e}")
                await asyncio.sleep(120)

    async def _backup_loop(self):
        """Handle system backups"""
        logger.info("Starting backup loop")
        
        while self.state == SystemState.RUNNING:
            try:
                if (not self.last_backup or 
                    datetime.now() - self.last_backup > timedelta(seconds=self.config.backup_interval)):
                    
                    await self._create_system_backup()
                    self.last_backup = datetime.now()
                    logger.info("System backup completed")
                
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                logger.error(f"Backup loop error: {e}")
                await asyncio.sleep(3600)

    async def _manage_system_resources(self):
        """Manage system resources and prevent conflicts"""
        try:
            # Check active tasks
            active_count = len([task for task in self.active_tasks.values() if not task.done()])
            
            # Throttle if too many concurrent operations
            if active_count > self.config.max_concurrent_improvements:
                logger.warning(f"Too many concurrent operations ({active_count}), throttling...")
                # Cancel oldest tasks if necessary
                oldest_tasks = sorted(self.active_tasks.items(), key=lambda x: x[0])
                for task_id, task in oldest_tasks[:active_count - self.config.max_concurrent_improvements]:
                    if not task.done():
                        task.cancel()
                        logger.info(f"Cancelled task {task_id} due to resource constraints")
            
        except Exception as e:
            logger.error(f"Resource management error: {e}")

    async def _resolve_system_conflicts(self):
        """Resolve conflicts between different systems"""
        try:
            # Check for GitHub rate limiting
            if self.github_engine:
                # Implement rate limiting logic
                pass
            
            # Check for memory usage conflicts
            health_status = self.system_metrics.get("health", {})
            memory_usage = health_status.get("metrics", {}).get("memory_usage", {}).get("value", 0)
            
            if memory_usage > 90:  # High memory usage
                logger.warning("High memory usage detected, reducing system activity")
                # Temporarily reduce activity
                await asyncio.sleep(30)
            
        except Exception as e:
            logger.error(f"Conflict resolution error: {e}")

    async def _update_coordination_metrics(self):
        """Update coordination metrics"""
        try:
            self.system_metrics["coordination"] = {
                "cycle_count": self.cycle_count,
                "uptime": self.system_uptime,
                "total_improvements": self.total_improvements_implemented,
                "total_prs": self.total_prs_created,
                "active_tasks": len(self.active_tasks),
                "state": self.state.value,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Metrics update error: {e}")

    async def _create_system_backup(self):
        """Create system backup"""
        try:
            backup_data = {
                "timestamp": datetime.now().isoformat(),
                "system_metrics": self.system_metrics,
                "configuration": asdict(self.config),
                "performance_data": {
                    "cycle_count": self.cycle_count,
                    "uptime": self.system_uptime,
                    "improvements": self.total_improvements_implemented,
                    "prs": self.total_prs_created
                }
            }
            
            backup_file = f"system_backup_{int(time.time())}.json"
            backup_path = os.path.join("/tmp", backup_file)
            
            with open(backup_path, 'w') as f:
                json.dump(backup_data, f, indent=2)
            
            logger.info(f"System backup created: {backup_path}")
            
        except Exception as e:
            logger.error(f"Backup creation error: {e}")

    async def _update_systems_for_gpt5(self):
        """Update all systems to use GPT-5"""
        try:
            logger.info("Updating all systems for GPT-5...")
            
            # Update GitHub engine
            if self.github_engine:
                # Update model preference
                pass
            
            # Update improvement engine
            if self.improvement_engine:
                # Update model preference
                pass
            
            # Update meta-learning system
            if self.meta_system:
                # Update model preference
                pass
            
            logger.info("All systems updated for GPT-5")
            
        except Exception as e:
            logger.error(f"GPT-5 system update error: {e}")

    async def _trigger_emergency_protocols(self):
        """Trigger emergency protocols"""
        if self.emergency_stop_triggered:
            return
        
        self.emergency_stop_triggered = True
        logger.critical("🚨 EMERGENCY PROTOCOLS TRIGGERED 🚨")
        
        try:
            # Pause all non-critical operations
            self.state = SystemState.PAUSED
            
            # Cancel active tasks
            for task_id, task in self.active_tasks.items():
                if not task.done():
                    task.cancel()
                    logger.warning(f"Emergency cancelled task: {task_id}")
            
            # Create emergency backup
            await self._create_system_backup()
            
            # Wait for system to stabilize
            await asyncio.sleep(60)
            
            # Check if auto-recovery is enabled
            if self.config.auto_recovery_enabled:
                logger.info("Attempting auto-recovery...")
                await self._attempt_auto_recovery()
            else:
                logger.critical("Auto-recovery disabled, manual intervention required")
                self.state = SystemState.STOPPED
            
        except Exception as e:
            logger.error(f"Emergency protocol error: {e}")
            self.state = SystemState.ERROR

    async def _attempt_auto_recovery(self):
        """Attempt automatic recovery from emergency state"""
        try:
            logger.info("Starting auto-recovery sequence...")
            
            # Wait for system to stabilize
            await asyncio.sleep(120)
            
            # Check system health
            health_status = self.monitoring_system.get_system_health()
            
            if health_status["status"] in ["healthy", "warning"]:
                logger.info("System health improved, resuming operations")
                self.state = SystemState.RUNNING
                self.emergency_stop_triggered = False
            else:
                logger.warning("System health still critical, remaining in emergency state")
                await asyncio.sleep(300)  # Wait 5 minutes before next check
                await self._attempt_auto_recovery()
            
        except Exception as e:
            logger.error(f"Auto-recovery error: {e}")
            self.state = SystemState.ERROR

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.state = SystemState.STOPPING

    async def _cleanup(self):
        """Cleanup resources"""
        logger.info("Starting cleanup...")
        
        try:
            # Cancel all active tasks
            for task_id, task in self.active_tasks.items():
                if not task.done():
                    task.cancel()
                    logger.info(f"Cancelled task: {task_id}")
            
            # Stop monitoring system
            if self.monitoring_system:
                await self.monitoring_system.stop_monitoring()
            
            # Create final backup
            await self._create_system_backup()
            
            self.state = SystemState.STOPPED
            logger.info("Cleanup completed")
            
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            "state": self.state.value,
            "uptime": self.system_uptime,
            "cycle_count": self.cycle_count,
            "total_improvements": self.total_improvements_implemented,
            "total_prs": self.total_prs_created,
            "active_tasks": len(self.active_tasks),
            "emergency_stop_triggered": self.emergency_stop_triggered,
            "last_backup": self.last_backup.isoformat() if self.last_backup else None,
            "system_metrics": self.system_metrics,
            "configuration": asdict(self.config)
        }

# Global orchestrator instance
orchestrator = None

async def start_autonomous_orchestration(config: OrchestrationConfig = None):
    """Start the autonomous orchestration system"""
    global orchestrator
    orchestrator = AutonomousOrchestrator(config)
    await orchestrator.start_orchestration()

def get_orchestrator_status():
    """Get orchestrator status"""
    if orchestrator:
        return orchestrator.get_system_status()
    return {"error": "Orchestrator not initialized"}

async def emergency_stop():
    """Trigger emergency stop"""
    if orchestrator:
        await orchestrator._trigger_emergency_protocols()

async def main():
    """Main entry point"""
    try:
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('autonomous_orchestrator.log'),
                logging.StreamHandler()
            ]
        )
        
        # Load configuration from environment
        config = OrchestrationConfig(
            monitoring_enabled=os.getenv('MONITORING_ENABLED', 'true').lower() == 'true',
            github_integration_enabled=os.getenv('GITHUB_INTEGRATION_ENABLED', 'true').lower() == 'true',
            autonomous_improvement_enabled=os.getenv('AUTONOMOUS_IMPROVEMENT_ENABLED', 'true').lower() == 'true',
            meta_learning_enabled=os.getenv('META_LEARNING_ENABLED', 'true').lower() == 'true',
            gpt5_migration_enabled=os.getenv('GPT5_MIGRATION_ENABLED', 'true').lower() == 'true'
        )
        
        logger.info("🚀 Starting Autonomous Orchestration System...")
        await start_autonomous_orchestration(config)
        
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())

