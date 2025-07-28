#!/usr/bin/env python3
"""
Autonomous System Launcher
Production-ready launcher for the complete autonomous XMRT ecosystem
Handles initialization, monitoring, and graceful operation of all autonomous systems
"""

import asyncio
import logging
import os
import sys
import json
import time
import signal
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import subprocess
from dataclasses import dataclass, asdict

# Import all autonomous systems
try:
    from unified_autonomous_system import UnifiedAutonomousSystem, SystemIntegrationConfig, UnifiedSystemState
    from integration_orchestrator import AutonomousOrchestrator, OrchestrationConfig
    from github_integration import GitHubSelfImprovementEngine
    from self_monitoring import SelfMonitoringSystem, monitoring_system
    from autonomous_improvement_engine import AutonomousImprovementEngine
    from self_improvement_meta_system import SelfImprovementMetaSystem
    from enhanced_github_client import EnhancedGitHubClient, GitHubClientManager
    from autonomous_eliza import AutonomousElizaOS
    from gpt5_adapter import gpt5_adapter
except ImportError as e:
    print(f"Critical Error: Failed to import required autonomous systems: {e}")
    print("Please ensure all autonomous system modules are properly installed.")
    sys.exit(1)

@dataclass
class LauncherConfig:
    # System configuration
    auto_start_all_systems: bool = True
    enable_production_mode: bool = True
    enable_safety_monitoring: bool = True
    enable_performance_tracking: bool = True
    
    # GitHub configuration
    github_owner: str = "DevGruGold"
    github_repo: str = "XMRT-Ecosystem"
    github_pat: Optional[str] = None
    
    # Operational settings
    startup_delay: int = 30  # seconds
    health_check_interval: int = 60  # seconds
    auto_recovery_enabled: bool = True
    max_restart_attempts: int = 3
    
    # Logging configuration
    log_level: str = "INFO"
    log_to_file: bool = True
    log_rotation: bool = True
    
    # Performance settings
    max_memory_usage_mb: int = 2048
    max_cpu_usage_percent: int = 80
    performance_alert_threshold: float = 0.7

class AutonomousSystemLauncher:
    """
    Production launcher for the complete autonomous XMRT ecosystem
    Manages startup, monitoring, and operation of all autonomous systems
    """
    
    def __init__(self, config: LauncherConfig = None):
        self.config = config or LauncherConfig()
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # System state
        self.is_running = False
        self.start_time = None
        self.restart_attempts = 0
        self.system_health = {}
        self.performance_metrics = {}
        
        # Autonomous system instances
        self.unified_system = None
        self.orchestrator = None
        self.monitoring_system = None
        
        # Process management
        self.running_processes = {}
        self.shutdown_requested = False
        
        self.logger.info("🚀 Autonomous System Launcher initialized")
    
    def setup_logging(self):
        """Setup comprehensive logging for the launcher"""
        log_level = getattr(logging, self.config.log_level.upper(), logging.INFO)
        
        handlers = [logging.StreamHandler()]
        
        if self.config.log_to_file:
            handlers.append(logging.FileHandler('autonomous_launcher.log'))
            handlers.append(logging.FileHandler('system_health.log'))
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - [LAUNCHER] %(message)s',
            handlers=handlers
        )
    
    async def validate_environment(self) -> bool:
        """Validate the environment before starting autonomous systems"""
        self.logger.info("🔍 Validating environment for autonomous systems...")
        
        validation_results = []
        
        # Check GitHub credentials
        github_pat = os.getenv("GITHUB_PAT") or self.config.github_pat
        if not github_pat:
            validation_results.append("❌ GitHub PAT not found in environment variables")
        else:
            validation_results.append("✅ GitHub PAT found")
        
        # Check OpenAI credentials
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            validation_results.append("❌ OpenAI API key not found")
        else:
            validation_results.append("✅ OpenAI API key found")
        
        # Check repository access
        repo_path = "/home/ubuntu/XMRT-Ecosystem"
        if not Path(repo_path).exists():
            validation_results.append(f"❌ Repository path not found: {repo_path}")
        else:
            validation_results.append(f"✅ Repository path accessible: {repo_path}")
        
        # Check Python dependencies
        required_modules = [
            "openai", "github", "git", "asyncio", "logging", "json", "time"
        ]
        
        for module in required_modules:
            try:
                __import__(module)
                validation_results.append(f"✅ Module {module} available")
            except ImportError:
                validation_results.append(f"❌ Module {module} not available")
        
        # Check system resources
        try:
            import psutil
            memory = psutil.virtual_memory()
            cpu_count = psutil.cpu_count()
            
            if memory.available < (self.config.max_memory_usage_mb * 1024 * 1024):
                validation_results.append(f"⚠️ Low memory: {memory.available // (1024*1024)}MB available")
            else:
                validation_results.append(f"✅ Sufficient memory: {memory.available // (1024*1024)}MB available")
            
            validation_results.append(f"✅ CPU cores available: {cpu_count}")
            
        except ImportError:
            validation_results.append("⚠️ psutil not available for resource monitoring")
        
        # Log validation results
        for result in validation_results:
            if "❌" in result:
                self.logger.error(result)
            elif "⚠️" in result:
                self.logger.warning(result)
            else:
                self.logger.info(result)
        
        # Check if critical requirements are met
        critical_failures = [r for r in validation_results if "❌" in r]
        
        if critical_failures:
            self.logger.error(f"Environment validation failed with {len(critical_failures)} critical issues")
            return False
        
        self.logger.info("✅ Environment validation completed successfully")
        return True
    
    async def initialize_autonomous_systems(self) -> bool:
        """Initialize all autonomous systems"""
        self.logger.info("🔧 Initializing autonomous systems...")
        
        try:
            # Initialize system integration config
            integration_config = SystemIntegrationConfig(
                orchestrator_enabled=True,
                github_integration_enabled=True,
                improvement_engine_enabled=True,
                meta_learning_enabled=True,
                monitoring_enabled=True,
                eliza_core_enabled=True,
                cross_system_learning=True,
                unified_decision_making=True,
                emergency_coordination=True
            )
            
            # Initialize unified autonomous system
            self.unified_system = UnifiedAutonomousSystem(integration_config)
            self.logger.info("✅ Unified autonomous system initialized")
            
            # Initialize monitoring system
            self.monitoring_system = monitoring_system
            self.logger.info("✅ Monitoring system initialized")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize autonomous systems: {e}")
            return False
    
    async def start_autonomous_operations(self):
        """Start all autonomous operations"""
        self.logger.info("🚀 Starting autonomous operations...")
        
        try:
            # Start unified system
            if self.unified_system:
                unified_task = asyncio.create_task(
                    self.unified_system.start_unified_operations()
                )
                self.running_processes["unified_system"] = unified_task
                self.logger.info("✅ Unified autonomous system started")
            
            # Start monitoring
            if self.monitoring_system:
                monitoring_task = asyncio.create_task(
                    self.monitoring_system.start_monitoring()
                )
                self.running_processes["monitoring"] = monitoring_task
                self.logger.info("✅ Monitoring system started")
            
            # Start health monitoring
            health_task = asyncio.create_task(self.health_monitoring_loop())
            self.running_processes["health_monitor"] = health_task
            
            # Start performance tracking
            if self.config.enable_performance_tracking:
                performance_task = asyncio.create_task(self.performance_tracking_loop())
                self.running_processes["performance_tracker"] = performance_task
            
            self.logger.info("🌟 All autonomous operations started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start autonomous operations: {e}")
            raise
    
    async def health_monitoring_loop(self):
        """Continuous health monitoring of all systems"""
        while not self.shutdown_requested:
            try:
                # Check system health
                health_status = await self.check_system_health()
                self.system_health = health_status
                
                # Log health status
                if health_status["overall_health"] < 0.8:
                    self.logger.warning(f"⚠️ System health degraded: {health_status['overall_health']:.2f}")
                else:
                    self.logger.info(f"💚 System health good: {health_status['overall_health']:.2f}")
                
                # Check for auto-recovery needs
                if self.config.auto_recovery_enabled:
                    await self.check_auto_recovery(health_status)
                
                await asyncio.sleep(self.config.health_check_interval)
                
            except Exception as e:
                self.logger.error(f"Error in health monitoring: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def performance_tracking_loop(self):
        """Continuous performance tracking"""
        while not self.shutdown_requested:
            try:
                # Collect performance metrics
                metrics = await self.collect_performance_metrics()
                self.performance_metrics = metrics
                
                # Check performance thresholds
                if metrics.get("cpu_usage", 0) > self.config.max_cpu_usage_percent:
                    self.logger.warning(f"⚠️ High CPU usage: {metrics['cpu_usage']:.1f}%")
                
                if metrics.get("memory_usage_mb", 0) > self.config.max_memory_usage_mb:
                    self.logger.warning(f"⚠️ High memory usage: {metrics['memory_usage_mb']:.1f}MB")
                
                # Log performance summary
                self.logger.info(f"📊 Performance: CPU {metrics.get('cpu_usage', 0):.1f}%, "
                               f"Memory {metrics.get('memory_usage_mb', 0):.1f}MB, "
                               f"Efficiency {metrics.get('efficiency_score', 0):.2f}")
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error in performance tracking: {e}")
                await asyncio.sleep(600)
    
    async def check_system_health(self) -> Dict[str, Any]:
        """Check health of all autonomous systems"""
        health_data = {
            "timestamp": datetime.now().isoformat(),
            "uptime": (datetime.now() - self.start_time).total_seconds() if self.start_time else 0,
            "systems": {},
            "overall_health": 0.0
        }
        
        try:
            # Check unified system health
            if self.unified_system:
                unified_status = self.unified_system.get_unified_system_status()
                health_data["systems"]["unified_system"] = {
                    "status": unified_status.get("state", "unknown"),
                    "health_score": 1.0 if unified_status.get("state") == "running" else 0.5
                }
            
            # Check monitoring system health
            if self.monitoring_system:
                monitoring_status = await self.monitoring_system.get_system_status()
                health_data["systems"]["monitoring"] = {
                    "status": "healthy" if monitoring_status.get("is_running", False) else "unhealthy",
                    "health_score": 1.0 if monitoring_status.get("is_running", False) else 0.0
                }
            
            # Check running processes
            for name, task in self.running_processes.items():
                if task.done():
                    health_data["systems"][name] = {
                        "status": "stopped",
                        "health_score": 0.0
                    }
                else:
                    health_data["systems"][name] = {
                        "status": "running",
                        "health_score": 1.0
                    }
            
            # Calculate overall health
            if health_data["systems"]:
                total_score = sum(system["health_score"] for system in health_data["systems"].values())
                health_data["overall_health"] = total_score / len(health_data["systems"])
            
        except Exception as e:
            self.logger.error(f"Error checking system health: {e}")
            health_data["overall_health"] = 0.0
        
        return health_data
    
    async def collect_performance_metrics(self) -> Dict[str, Any]:
        """Collect comprehensive performance metrics"""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "cpu_usage": 0.0,
            "memory_usage_mb": 0.0,
            "efficiency_score": 0.0,
            "active_processes": len(self.running_processes),
            "system_load": 0.0
        }
        
        try:
            import psutil
            
            # CPU usage
            metrics["cpu_usage"] = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            metrics["memory_usage_mb"] = (memory.total - memory.available) / (1024 * 1024)
            metrics["memory_percent"] = memory.percent
            
            # System load
            if hasattr(psutil, 'getloadavg'):
                metrics["system_load"] = psutil.getloadavg()[0]
            
            # Efficiency score (based on resource usage vs performance)
            if self.unified_system:
                unified_status = self.unified_system.get_unified_system_status()
                metrics["efficiency_score"] = unified_status.get("system_efficiency_score", 0.0)
            
        except ImportError:
            self.logger.warning("psutil not available for detailed performance metrics")
        except Exception as e:
            self.logger.error(f"Error collecting performance metrics: {e}")
        
        return metrics
    
    async def check_auto_recovery(self, health_status: Dict[str, Any]):
        """Check if auto-recovery is needed and execute if necessary"""
        overall_health = health_status.get("overall_health", 1.0)
        
        if overall_health < self.config.performance_alert_threshold:
            self.logger.warning(f"🔄 Auto-recovery triggered due to low health: {overall_health:.2f}")
            
            # Check for stopped processes
            for name, system_health in health_status.get("systems", {}).items():
                if system_health.get("status") == "stopped" and name in self.running_processes:
                    await self.restart_system_component(name)
            
            # If still unhealthy and within restart limits, restart entire system
            if overall_health < 0.5 and self.restart_attempts < self.config.max_restart_attempts:
                await self.restart_autonomous_systems()
    
    async def restart_system_component(self, component_name: str):
        """Restart a specific system component"""
        self.logger.info(f"🔄 Restarting system component: {component_name}")
        
        try:
            # Cancel existing task
            if component_name in self.running_processes:
                task = self.running_processes[component_name]
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
            
            # Restart component based on type
            if component_name == "unified_system" and self.unified_system:
                new_task = asyncio.create_task(
                    self.unified_system.start_unified_operations()
                )
                self.running_processes[component_name] = new_task
                
            elif component_name == "monitoring" and self.monitoring_system:
                new_task = asyncio.create_task(
                    self.monitoring_system.start_monitoring()
                )
                self.running_processes[component_name] = new_task
            
            self.logger.info(f"✅ Successfully restarted {component_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to restart {component_name}: {e}")
    
    async def restart_autonomous_systems(self):
        """Restart all autonomous systems"""
        if self.restart_attempts >= self.config.max_restart_attempts:
            self.logger.error("Maximum restart attempts reached, manual intervention required")
            return
        
        self.restart_attempts += 1
        self.logger.warning(f"🔄 Restarting all autonomous systems (attempt {self.restart_attempts})")
        
        try:
            # Stop all systems
            await self.stop_autonomous_systems()
            
            # Wait for cleanup
            await asyncio.sleep(10)
            
            # Reinitialize and restart
            if await self.initialize_autonomous_systems():
                await self.start_autonomous_operations()
                self.logger.info("✅ Autonomous systems restarted successfully")
            else:
                self.logger.error("❌ Failed to restart autonomous systems")
                
        except Exception as e:
            self.logger.error(f"Error during system restart: {e}")
    
    async def stop_autonomous_systems(self):
        """Stop all autonomous systems gracefully"""
        self.logger.info("🛑 Stopping autonomous systems...")
        
        # Cancel all running tasks
        for name, task in self.running_processes.items():
            if not task.done():
                self.logger.info(f"Stopping {name}...")
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        self.running_processes.clear()
        
        # Stop unified system
        if self.unified_system:
            await self.unified_system.emergency_shutdown()
        
        self.logger.info("✅ All autonomous systems stopped")
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            self.shutdown_requested = True
            asyncio.create_task(self.graceful_shutdown())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def graceful_shutdown(self):
        """Perform graceful shutdown of all systems"""
        self.logger.info("🛑 Initiating graceful shutdown...")
        
        self.shutdown_requested = True
        
        # Stop autonomous systems
        await self.stop_autonomous_systems()
        
        # Final status report
        final_status = {
            "shutdown_time": datetime.now().isoformat(),
            "total_uptime": (datetime.now() - self.start_time).total_seconds() if self.start_time else 0,
            "restart_attempts": self.restart_attempts,
            "final_health": self.system_health,
            "final_performance": self.performance_metrics
        }
        
        self.logger.info(f"📊 Final system status: {json.dumps(final_status, indent=2)}")
        self.logger.info("✅ Graceful shutdown completed")
        
        self.is_running = False
    
    async def run(self):
        """Main run method for the autonomous system launcher"""
        try:
            self.logger.info("🌟 Starting Autonomous XMRT Ecosystem")
            
            # Setup signal handlers
            self.setup_signal_handlers()
            
            # Validate environment
            if not await self.validate_environment():
                self.logger.error("Environment validation failed, aborting startup")
                return False
            
            # Initialize systems
            if not await self.initialize_autonomous_systems():
                self.logger.error("System initialization failed, aborting startup")
                return False
            
            # Startup delay for system stabilization
            if self.config.startup_delay > 0:
                self.logger.info(f"⏳ Startup delay: {self.config.startup_delay} seconds")
                await asyncio.sleep(self.config.startup_delay)
            
            # Start autonomous operations
            self.start_time = datetime.now()
            self.is_running = True
            
            await self.start_autonomous_operations()
            
            # Keep running until shutdown requested
            while not self.shutdown_requested:
                await asyncio.sleep(1)
            
            return True
            
        except KeyboardInterrupt:
            self.logger.info("Keyboard interrupt received")
            await self.graceful_shutdown()
            return True
            
        except Exception as e:
            self.logger.error(f"Fatal error in autonomous system launcher: {e}")
            await self.graceful_shutdown()
            return False
    
    def get_launcher_status(self) -> Dict[str, Any]:
        """Get comprehensive launcher status"""
        return {
            "is_running": self.is_running,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "uptime": (datetime.now() - self.start_time).total_seconds() if self.start_time else 0,
            "restart_attempts": self.restart_attempts,
            "running_processes": list(self.running_processes.keys()),
            "system_health": self.system_health,
            "performance_metrics": self.performance_metrics,
            "config": asdict(self.config)
        }

# Global launcher instance
launcher = AutonomousSystemLauncher()

async def main():
    """Main entry point for the autonomous system launcher"""
    try:
        # Load configuration from environment
        config = LauncherConfig(
            github_owner=os.getenv("GITHUB_USERNAME", "DevGruGold"),
            github_repo=os.getenv("GITHUB_REPO", "XMRT-Ecosystem"),
            github_pat=os.getenv("GITHUB_PAT"),
            enable_production_mode=os.getenv("PRODUCTION_MODE", "true").lower() == "true",
            log_level=os.getenv("LOG_LEVEL", "INFO")
        )
        
        # Initialize launcher with config
        global launcher
        launcher = AutonomousSystemLauncher(config)
        
        # Run the autonomous system
        success = await launcher.run()
        
        if success:
            print("🌟 Autonomous XMRT Ecosystem completed successfully")
        else:
            print("❌ Autonomous XMRT Ecosystem failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

