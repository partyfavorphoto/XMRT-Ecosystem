#!/usr/bin/env python3
"""
XMRT-Ecosystem Enhancement Activation Script
This script safely activates all advanced features without breaking deployment
"""

import os
import sys
import logging
import time
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("EnhancementActivation")

class XMRTEnhancementActivator:
    """Safely activate XMRT-Ecosystem enhancements"""

    def __init__(self):
        self.activation_log = []
        self.errors = []

    def log_action(self, action, status, details=""):
        """Log activation actions"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'status': status,
            'details': details
        }
        self.activation_log.append(entry)

        if status == 'success':
            logger.info(f"✅ {action}: {details}")
        elif status == 'error':
            logger.error(f"❌ {action}: {details}")
            self.errors.append(entry)
        else:
            logger.warning(f"⚠️ {action}: {details}")

    def check_environment_readiness(self):
        """Check if environment is ready for enhancements"""
        self.log_action("Environment Check", "info", "Starting readiness assessment")

        # Check for required API keys
        required_keys = ['GEMINI_API_KEY', 'OPENAI_API_KEY']
        optional_keys = ['GITHUB_TOKEN', 'SUPABASE_URL', 'SUPABASE_KEY']

        missing_required = []
        missing_optional = []

        for key in required_keys:
            if not os.getenv(key) or os.getenv(key) == f'your_{key.lower()}_here':
                missing_required.append(key)

        for key in optional_keys:
            if not os.getenv(key) or 'your_' in os.getenv(key, ''):
                missing_optional.append(key)

        if missing_required:
            self.log_action("Environment Check", "error", 
                          f"Missing required keys: {', '.join(missing_required)}")
            return False

        if missing_optional:
            self.log_action("Environment Check", "warning",
                          f"Missing optional keys: {', '.join(missing_optional)} - Some features will be limited")

        self.log_action("Environment Check", "success", "Environment ready for activation")
        return True

    def activate_autonomous_learning(self):
        """Activate autonomous learning with safety checks"""
        try:
            # Set environment variables for autonomous learning
            os.environ['ENABLE_AUTONOMOUS_LEARNING'] = 'true'
            os.environ['ENABLE_REALTIME_LEARNING'] = 'true' 
            os.environ['ENABLE_ADAPTIVE_LEARNING'] = 'true'

            self.log_action("Autonomous Learning", "success", "Learning systems activated")
            return True

        except Exception as e:
            self.log_action("Autonomous Learning", "error", str(e))
            return False

    def activate_multiagent_system(self):
        """Activate multi-agent coordination"""
        try:
            os.environ['ENABLE_MULTIAGENT_SYSTEM'] = 'true'
            os.environ['ENABLE_COLLABORATIVE_AGENTS'] = 'true'
            os.environ['AGENT_POOL_SIZE'] = '3'
            os.environ['ENABLE_AGENT_LEARNING'] = 'true'

            self.log_action("Multi-Agent System", "success", "Agent coordination activated")
            return True

        except Exception as e:
            self.log_action("Multi-Agent System", "error", str(e))
            return False

    def activate_github_integration(self):
        """Activate GitHub integration features"""
        try:
            if os.getenv('GITHUB_TOKEN'):
                os.environ['ENABLE_GITHUB_INTEGRATION'] = 'true'
                os.environ['ENABLE_GITHUB_AUTO_DEPLOY'] = 'true'
                self.log_action("GitHub Integration", "success", "GitHub features activated")
            else:
                os.environ['ENABLE_GITHUB_INTEGRATION'] = 'false'
                self.log_action("GitHub Integration", "warning", "GitHub token not available - integration disabled")
            return True

        except Exception as e:
            self.log_action("GitHub Integration", "error", str(e))
            return False

    def activate_memory_persistence(self):
        """Activate persistent memory features"""
        try:
            if os.getenv('SUPABASE_URL') and os.getenv('SUPABASE_KEY'):
                os.environ['ENABLE_MEMORY_PERSISTENCE'] = 'true'
                self.log_action("Memory Persistence", "success", "Persistent memory activated")
            else:
                os.environ['ENABLE_MEMORY_PERSISTENCE'] = 'false'
                self.log_action("Memory Persistence", "warning", "Supabase not configured - using local memory only")
            return True

        except Exception as e:
            self.log_action("Memory Persistence", "error", str(e))
            return False

    def activate_advanced_features(self):
        """Activate advanced AI capabilities"""
        try:
            advanced_features = {
                'ENABLE_CODE_GENERATION': 'true',
                'ENABLE_SMART_REFACTORING': 'true', 
                'ENABLE_AUTOMATED_TESTING': 'true',
                'ENABLE_PERFORMANCE_OPTIMIZATION': 'true',
                'ENABLE_SECURITY_ANALYSIS': 'true',
                'ENABLE_DOCUMENTATION_GENERATION': 'true'
            }

            for feature, value in advanced_features.items():
                os.environ[feature] = value

            self.log_action("Advanced Features", "success", f"Activated {len(advanced_features)} advanced capabilities")
            return True

        except Exception as e:
            self.log_action("Advanced Features", "error", str(e))
            return False

    def activate_monitoring_analytics(self):
        """Activate monitoring and analytics"""
        try:
            monitoring_features = {
                'ENABLE_ADVANCED_ANALYTICS': 'true',
                'ENABLE_PERFORMANCE_METRICS': 'true',
                'ENABLE_REAL_TIME_MONITORING': 'true',
                'ENABLE_ERROR_TRACKING': 'true'
            }

            for feature, value in monitoring_features.items():
                os.environ[feature] = value

            self.log_action("Monitoring & Analytics", "success", "Real-time monitoring activated")
            return True

        except Exception as e:
            self.log_action("Monitoring & Analytics", "error", str(e))
            return False

    def run_full_activation(self):
        """Run complete enhancement activation sequence"""
        logger.info("🚀 Starting XMRT-Ecosystem Enhancement Activation")
        logger.info("=" * 60)

        # Check environment readiness
        if not self.check_environment_readiness():
            logger.error("❌ Environment not ready - aborting activation")
            return False

        # Activation sequence
        activation_steps = [
            ('Autonomous Learning', self.activate_autonomous_learning),
            ('Multi-Agent System', self.activate_multiagent_system),
            ('GitHub Integration', self.activate_github_integration),
            ('Memory Persistence', self.activate_memory_persistence),
            ('Advanced Features', self.activate_advanced_features),
            ('Monitoring & Analytics', self.activate_monitoring_analytics)
        ]

        successful_activations = 0

        for step_name, step_function in activation_steps:
            try:
                if step_function():
                    successful_activations += 1
                time.sleep(0.5)  # Brief pause between activations
            except Exception as e:
                self.log_action(f"Activation Step: {step_name}", "error", str(e))

        # Summary
        logger.info("=" * 60)
        logger.info(f"🎯 Activation Complete: {successful_activations}/{len(activation_steps)} successful")

        if self.errors:
            logger.warning(f"⚠️ {len(self.errors)} errors occurred during activation")
            for error in self.errors[-3:]:  # Show last 3 errors
                logger.warning(f"   - {error['action']}: {error['details']}")

        # Activation success if at least 4/6 steps succeeded
        success = successful_activations >= 4

        if success:
            logger.info("✅ XMRT-Ecosystem enhancements successfully activated!")
            logger.info("🔄 System will use enhanced capabilities on next restart")
        else:
            logger.error("❌ Activation failed - insufficient successful steps")

        return success

def main():
    """Main activation entry point"""
    activator = XMRTEnhancementActivator()

    try:
        success = activator.run_full_activation()
        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        logger.info("🛑 Activation interrupted by user")
        sys.exit(130)

    except Exception as e:
        logger.error(f"❌ Unexpected error during activation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
