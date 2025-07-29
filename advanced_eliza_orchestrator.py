# advanced_eliza_orchestrator.py
# Comprehensive startup orchestrator for the XMRT-Ecosystem Eliza system

import asyncio
import logging
import signal
import sys
import time
import threading
import subprocess
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import json
import redis
import requests
from concurrent.futures import ThreadPoolExecutor

# Import existing components from your ecosystem
sys.path.append('backend/ai-automation-service/src')
sys.path.append('backend/ai_agent_boardroom/src')
sys.path.append('backend/eliza_langgraph')

from autonomous_eliza import AutonomousElizaOS, ConfidenceManager, DecisionEvaluator, DecisionExplainer
from eliza_agent_patch import AgentState, parse_intent, execute_onchain
from confidence_manager import ConfidenceManager as StandaloneConfidenceManager
from self_monitoring import SelfMonitoringSystem
from integration_orchestrator import AutonomousOrchestrator
from memory_manager import MemoryManager
from eliza_memory_integration import XMRTElizaMemoryManager

class AdvancedElizaOrchestrator:
    """
    Advanced orchestrator that coordinates all Eliza components in the XMRT ecosystem
    """
    
    def __init__(self, config_path: str = "config/eliza_config.json"):
        self.config_path = config_path
        self.config = self.load_configuration()
        self.logger = self.setup_logging()
        
        # Component instances
        self.autonomous_eliza: Optional[AutonomousElizaOS] = None
        self.confidence_manager: Optional[ConfidenceManager] = None
        self.decision_evaluator: Optional[DecisionEvaluator] = None
        self.decision_explainer: Optional[DecisionExplainer] = None
        self.memory_manager: Optional[XMRTElizaMemoryManager] = None
        self.monitoring_system: Optional[SelfMonitoringSystem] = None
        self.orchestrator: Optional[AutonomousOrchestrator] = None
        
        # Service processes
        self.service_processes: Dict[str, subprocess.Popen] = {}
        self.service_health: Dict[str, bool] = {}
        
        # Threading
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.shutdown_event = threading.Event()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
    def load_configuration(self) -> Dict:
        """Load orchestrator configuration"""
        default_config = {
            "services": {
                "redis": {
                    "host": "localhost",
                    "port": 6379,
                    "enabled": True
                },
                "memory_api": {
                    "port": 5001,
                    "enabled": True
                },
                "eliza_api": {
                    "port": 5000,
                    "enabled": True
                },
                "frontend": {
                    "port": 3000,
                    "enabled": True
                }
            },
            "eliza": {
                "confidence_thresholds": {
                    "autonomous": 0.85,
                    "advisory": 0.60,
                    "emergency": 0.95
                },
                "memory": {
                    "semantic_search": True,
                    "embedding_model": "all-MiniLM-L6-v2"
                },
                "monitoring": {
                    "health_check_interval": 30,
                    "alert_threshold": 0.7
                }
            },
            "logging": {
                "level": "INFO",
                "file": "logs/eliza_orchestrator.log"
            }
        }
        
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    loaded_config = json.load(f)
                # Merge with defaults
                return {**default_config, **loaded_config}
            else:
                # Create default config file
                os.makedirs(Path(self.config_path).parent, exist_ok=True)
                with open(self.config_path, 'w') as f:
                    json.dump(default_config, f, indent=2)
                return default_config
        except Exception as e:
            print(f"⚠️ Error loading config, using defaults: {e}")
            return default_config
    
    def setup_logging(self) -> logging.Logger:
        """Setup comprehensive logging"""
        log_dir = Path(self.config['logging']['file']).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=getattr(logging, self.config['logging']['level']),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.config['logging']['file']),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        logger = logging.getLogger('ElizaOrchestrator')
        logger.info("🚀 Eliza Advanced Orchestrator initialized")
        return logger
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.info(f"📡 Received signal {signum}, initiating graceful shutdown...")
        self.shutdown_event.set()
        asyncio.create_task(self.shutdown())
    
    async def verify_dependencies(self) -> bool:
        """Verify all required dependencies are available"""
        self.logger.info("🔍 Verifying system dependencies...")
        
        dependencies = {
            "Redis": self.check_redis_connection,
            "Python Environment": self.check_python_environment,
            "Required Modules": self.check_required_modules,
            "File System": self.check_file_system_access
        }
        
        all_good = True
        for dep_name, check_func in dependencies.items():
            try:
                result = await check_func() if asyncio.iscoroutinefunction(check_func) else check_func()
                if result:
                    self.logger.info(f"✅ {dep_name}: OK")
                else:
                    self.logger.error(f"❌ {dep_name}: FAILED")
                    all_good = False
            except Exception as e:
                self.logger.error(f"❌ {dep_name}: ERROR - {str(e)}")
                all_good = False
        
        return all_good
    
    def check_redis_connection(self) -> bool:
        """Check Redis connectivity"""
        if not self.config['services']['redis']['enabled']:
            return True
        
        try:
            r = redis.Redis(
                host=self.config['services']['redis']['host'],
                port=self.config['services']['redis']['port'],
                socket_timeout=5
            )
            r.ping()
            return True
        except Exception:
            return False
    
    def check_python_environment(self) -> bool:
        """Check Python environment and version"""
        try:
            version = sys.version_info
            if version.major >= 3 and version.minor >= 8:
                return True
            return False
        except Exception:
            return False
    
    def check_required_modules(self) -> bool:
        """Check if all required modules are importable"""
        required_modules = [
            'redis', 'requests', 'asyncio', 'logging',
            'threading', 'subprocess', 'pathlib'
        ]
        
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                self.logger.error(f"Missing required module: {module}")
                return False
        return True
    
    def check_file_system_access(self) -> bool:
        """Check file system access for logs and data"""
        try:
            # Check log directory
            log_dir = Path(self.config['logging']['file']).parent
            log_dir.mkdir(parents=True, exist_ok=True)
            
            # Check data directory
            data_dir = Path("data")
            data_dir.mkdir(exist_ok=True)
            
            return True
        except Exception:
            return False
    
    async def initialize_core_components(self):
        """Initialize all core Eliza components"""
        self.logger.info("🧠 Initializing core Eliza components...")
        
        try:
            # Initialize Memory Manager
            self.logger.info("📚 Initializing Memory Manager...")
            self.memory_manager = XMRTElizaMemoryManager()
            await self.memory_manager._init_database()
            
            # Initialize Confidence Manager
            self.logger.info("📊 Initializing Confidence Manager...")
            self.confidence_manager = ConfidenceManager(self.memory_manager)
            
            # Initialize Decision Evaluator
            self.logger.info("⚖️ Initializing Decision Evaluator...")
            self.decision_evaluator = DecisionEvaluator()
            
            # Initialize Decision Explainer
            self.logger.info("💭 Initializing Decision Explainer...")
            self.decision_explainer = DecisionExplainer()
            
            # Initialize Monitoring System
            self.logger.info("📊 Initializing Self-Monitoring System...")
            self.monitoring_system = SelfMonitoringSystem()
            
            # Initialize Autonomous Eliza
            self.logger.info("🤖 Initializing Autonomous Eliza OS...")
            self.autonomous_eliza = AutonomousElizaOS(
                confidence_manager=self.confidence_manager,
                decision_evaluator=self.decision_evaluator,
                decision_explainer=self.decision_explainer,
                memory_manager=self.memory_manager
            )
            
            # Initialize Integration Orchestrator
            self.logger.info("🎭 Initializing Integration Orchestrator...")
            self.orchestrator = AutonomousOrchestrator()
            
            self.logger.info("✅ All core components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize core components: {str(e)}")
            raise
    
    async def start_services(self):
        """Start all required services"""
        self.logger.info("🚀 Starting system services...")
        
        services_to_start = [
            {
                "name": "memory_api",
                "command": ["python", "backend/ai_agent_boardroom/src/main.py"],
                "port": self.config['services']['memory_api']['port'],
                "enabled": self.config['services']['memory_api']['enabled']
            },
            {
                "name": "eliza_api", 
                "command": ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"],
                "port": self.config['services']['eliza_api']['port'],
                "enabled": self.config['services']['eliza_api']['enabled'],
                "env": {"FLASK_APP": "backend/ai-automation-service/src/autonomous_eliza.py"}
            }
        ]
        
        for service in services_to_start:
            if service['enabled']:
                await self.start_service(service)
    
    async def start_service(self, service_config: Dict):
        """Start an individual service"""
        service_name = service_config['name']
        
        try:
            self.logger.info(f"🔄 Starting {service_name}...")
            
            env = os.environ.copy()
            if 'env' in service_config:
                env.update(service_config['env'])
            
            process = subprocess.Popen(
                service_config['command'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                cwd=Path.cwd()
            )
            
            self.service_processes[service_name] = process
            
            # Wait a moment for the service to start
            await asyncio.sleep(2)
            
            # Check if service is running
            if process.poll() is None:
                # Try to verify the service is responding
                if 'port' in service_config:
                    health_check = await self.check_service_health(service_name, service_config['port'])
                    if health_check:
                        self.logger.info(f"✅ {service_name} started successfully on port {service_config['port']}")
                        self.service_health[service_name] = True
                    else:
                        self.logger.warning(f"⚠️ {service_name} started but health check failed")
                        self.service_health[service_name] = False
                else:
                    self.logger.info(f"✅ {service_name} started successfully")
                    self.service_health[service_name] = True
            else:
                stderr_output = process.stderr.read().decode() if process.stderr else "No error output"
                self.logger.error(f"❌ {service_name} failed to start: {stderr_output}")
                self.service_health[service_name] = False
                
        except Exception as e:
            self.logger.error(f"❌ Error starting {service_name}: {str(e)}")
            self.service_health[service_name] = False
    
    async def check_service_health(self, service_name: str, port: int) -> bool:
        """Check if a service is healthy"""
        try:
            response = requests.get(f"http://localhost:{port}/health", timeout=5)
            return response.status_code == 200
        except Exception:
            # Try alternative health check endpoints
            alternative_endpoints = ["/", "/status", "/api/health"]
            for endpoint in alternative_endpoints:
                try:
                    response = requests.get(f"http://localhost:{port}{endpoint}", timeout=5)
                    if response.status_code < 500:  # Accept anything that's not a server error
                        return True
                except Exception:
                    continue
            return False
    
    async def start_monitoring_loop(self):
        """Start the continuous monitoring loop"""
        self.logger.info("📊 Starting monitoring loop...")
        
        while not self.shutdown_event.is_set():
            try:
                # Check service health
                await self.monitor_services()
                
                # Check system resources
                await self.monitor_system_resources()
                
                # Check Eliza's cognitive state
                await self.monitor_eliza_state()
                
                # Wait for next check
                await asyncio.sleep(self.config['eliza']['monitoring']['health_check_interval'])
                
            except Exception as e:
                self.logger.error(f"❌ Error in monitoring loop: {str(e)}")
                await asyncio.sleep(10)  # Brief pause before retrying
    
    async def monitor_services(self):
        """Monitor the health of all services"""
        for service_name, process in self.service_processes.items():
            if process.poll() is not None:
                self.logger.warning(f"⚠️ Service {service_name} has stopped unexpectedly")
                self.service_health[service_name] = False
                # Attempt to restart
                await self.restart_service(service_name)
    
    async def monitor_system_resources(self):
        """Monitor system resources"""
        try:
            import psutil
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # Log warnings if resources are high
            if cpu_percent > 80:
                self.logger.warning(f"⚠️ High CPU usage: {cpu_percent}%")
            
            if memory_percent > 80:
                self.logger.warning(f"⚠️ High memory usage: {memory_percent}%")
            
            if disk_percent > 90:
                self.logger.warning(f"⚠️ High disk usage: {disk_percent}%")
                
        except ImportError:
            # psutil not available, skip resource monitoring
            pass
        except Exception as e:
            self.logger.error(f"❌ Error monitoring system resources: {str(e)}")
    
    async def monitor_eliza_state(self):
        """Monitor Eliza's cognitive and operational state"""
        try:
            if self.autonomous_eliza and self.monitoring_system:
                # Get system health from monitoring system
                health_status = self.monitoring_system.get_system_health()
                
                # Check if Eliza is responsive
                eliza_responsive = await self.check_eliza_responsiveness()
                
                # Log status
                if health_status and eliza_responsive:
                    self.logger.debug("🤖 Eliza is healthy and responsive")
                else:
                    self.logger.warning("⚠️ Eliza may be experiencing issues")
                    
        except Exception as e:
            self.logger.error(f"❌ Error monitoring Eliza state: {str(e)}")
    
    async def check_eliza_responsiveness(self) -> bool:
        """Check if Eliza is responding to queries"""
        try:
            # Try to send a test message to Eliza
            if self.autonomous_eliza:
                test_response = await self.autonomous_eliza.process_message("System health check")
                return test_response is not None
            return False
        except Exception:
            return False
    
    async def restart_service(self, service_name: str):
        """Restart a failed service"""
        self.logger.info(f"🔄 Attempting to restart {service_name}...")
        
        # Implementation would depend on having the original service config
        # For now, log the attempt
        self.logger.warning(f"⚠️ Service restart for {service_name} not yet implemented")
    
    async def run_interactive_mode(self):
        """Run interactive mode for testing and debugging"""
        self.logger.info("💬 Starting interactive mode...")
        
        print("\n🤖 Eliza Interactive Mode")
        print("=" * 40)
        print("Commands:")
        print("  /status - Show system status")
        print("  /health - Show health report")
        print("  /config - Show configuration")
        print("  /quit - Exit interactive mode")
        print("  Or just chat with Eliza!")
        print("=" * 40)
        
        while not self.shutdown_event.is_set():
            try:
                user_input = input("\n👤 You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input == "/quit":
                    break
                elif user_input == "/status":
                    await self.show_system_status()
                elif user_input == "/health":
                    await self.show_health_report()
                elif user_input == "/config":
                    self.show_configuration()
                else:
                    # Send to Eliza
                    if self.autonomous_eliza:
                        response = await self.autonomous_eliza.process_message(user_input)
                        print(f"🤖 Eliza: {response}")
                    else:
                        print("❌ Eliza is not available")
                        
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")
    
    async def show_system_status(self):
        """Show current system status"""
        print("\n📊 System Status:")
        print("-" * 20)
        
        # Service status
        print("Services:")
        for service_name, is_healthy in self.service_health.items():
            status = "🟢 Healthy" if is_healthy else "🔴 Unhealthy"
            print(f"  {service_name}: {status}")
        
        # Component status
        components = {
            "Autonomous Eliza": self.autonomous_eliza is not None,
            "Memory Manager": self.memory_manager is not None,
            "Confidence Manager": self.confidence_manager is not None,
            "Decision Evaluator": self.decision_evaluator is not None,
            "Monitoring System": self.monitoring_system is not None
        }
        
        print("\nComponents:")
        for component_name, is_initialized in components.items():
            status = "✅ Initialized" if is_initialized else "❌ Not initialized"
            print(f"  {component_name}: {status}")
    
    async def show_health_report(self):
        """Show detailed health report"""
        print("\n🏥 Health Report:")
        print("-" * 20)
        
        try:
            if self.monitoring_system:
                health_status = self.monitoring_system.get_system_health()
                print(f"Overall Health: {health_status}")
            else:
                print("Monitoring system not available")
                
        except Exception as e:
            print(f"Error generating health report: {str(e)}")
    
    def show_configuration(self):
        """Show current configuration"""
        print("\n⚙️ Configuration:")
        print("-" * 20)
        print(json.dumps(self.config, indent=2))
    
    async def shutdown(self):
        """Graceful shutdown of all components"""
        self.logger.info("🛑 Initiating graceful shutdown...")
        
        # Stop monitoring loop
        self.shutdown_event.set()
        
        # Shutdown services
        for service_name, process in self.service_processes.items():
            self.logger.info(f"🛑 Stopping {service_name}...")
            try:
                process.terminate()
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.logger.warning(f"⚠️ Force killing {service_name}")
                process.kill()
            except Exception as e:
                self.logger.error(f"❌ Error stopping {service_name}: {str(e)}")
        
        # Shutdown components
        if self.autonomous_eliza:
            self.logger.info("🛑 Shutting down Autonomous Eliza...")
            # Implement shutdown method if available
        
        if self.memory_manager:
            self.logger.info("🛑 Shutting down Memory Manager...")
            # Implement shutdown method if available
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        self.logger.info("✅ Graceful shutdown completed")
    
    async def run(self, interactive: bool = False):
        """Main orchestrator run method"""
        try:
            self.logger.info("🚀 Starting Advanced Eliza Orchestrator")
            
            # Verify dependencies
            if not await self.verify_dependencies():
                self.logger.error("❌ Dependency verification failed")
                return False
            
            # Initialize core components
            await self.initialize_core_components()
            
            # Start services
            await self.start_services()
            
            # Start monitoring
            monitoring_task = asyncio.create_task(self.start_monitoring_loop())
            
            if interactive:
                # Run interactive mode
                await self.run_interactive_mode()
            else:
                # Run in daemon mode
                self.logger.info("🔄 Running in daemon mode. Press Ctrl+C to stop.")
                try:
                    while not self.shutdown_event.is_set():
                        await asyncio.sleep(1)
                except KeyboardInterrupt:
                    pass
            
            # Cancel monitoring task
            monitoring_task.cancel()
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Fatal error in orchestrator: {str(e)}")
            return False
        finally:
            await self.shutdown()

async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Advanced Eliza Orchestrator")
    parser.add_argument("--config", default="config/eliza_config.json", 
                       help="Configuration file path")
    parser.add_argument("--interactive", action="store_true",
                       help="Run in interactive mode")
    parser.add_argument("--log-level", default="INFO",
                       choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       help="Logging level")
    
    args = parser.parse_args()
    
    # Create orchestrator
    orchestrator = AdvancedElizaOrchestrator(config_path=args.config)
    
    # Override log level if specified
    if args.log_level:
        orchestrator.config['logging']['level'] = args.log_level
        orchestrator.logger.setLevel(getattr(logging, args.log_level))
    
    # Run orchestrator
    success = await orchestrator.run(interactive=args.interactive)
    
    if success:
        print("✅ Eliza Orchestrator completed successfully")
        sys.exit(0)
    else:
        print("❌ Eliza Orchestrator failed")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
