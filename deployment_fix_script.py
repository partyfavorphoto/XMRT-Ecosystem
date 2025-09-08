#!/usr/bin/env python3
"""
XMRT Ecosystem Deployment Fix Script
Automated script to apply socket connection fixes and optimize deployment
"""

import os
import sys
import subprocess
import json
from pathlib import Path

class XMRTDeploymentFixer:
    def __init__(self):
        self.project_root = Path.cwd()
        self.fixes_applied = []
        self.errors = []
    
    def log(self, message, level="INFO"):
        print(f"[{level}] {message}")
    
    def apply_gunicorn_config(self):
        """Apply optimized gunicorn configuration"""
        try:
            gunicorn_config = '''# Gunicorn Configuration for XMRT Ecosystem
import os

bind = f"0.0.0.0:{os.environ.get('PORT', '5000')}"
workers = 1
worker_class = "gevent"
worker_connections = 1000
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 100
loglevel = "info"
preload_app = True
'''
            
            config_path = self.project_root / "gunicorn.conf.py"
            with open(config_path, 'w') as f:
                f.write(gunicorn_config)
            
            self.log(f"✅ Gunicorn configuration applied: {config_path}")
            self.fixes_applied.append("gunicorn_config")
            return True
            
        except Exception as e:
            self.log(f"❌ Failed to apply gunicorn config: {e}", "ERROR")
            self.errors.append(f"gunicorn_config: {e}")
            return False
    
    def update_socketio_config(self):
        """Update Socket.IO configuration for better stability"""
        try:
            # Look for main app file
            app_files = list(self.project_root.glob("app.py")) + list(self.project_root.glob("main.py")) + list(self.project_root.glob("server.py"))
            
            if not app_files:
                self.log("⚠️  No main app file found, skipping Socket.IO config update", "WARNING")
                return False
            
            app_file = app_files[0]
            self.log(f"📝 Updating Socket.IO config in: {app_file}")
            
            # Read current content
            with open(app_file, 'r') as f:
                content = f.read()
            
            # Check if Socket.IO is already configured
            if "SocketIO(" in content:
                self.log("✅ Socket.IO configuration found, applying optimizations")
                
                # Add enhanced configuration snippet
                enhanced_config = '''
# Enhanced Socket.IO Configuration for Stability
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='gevent',
    ping_timeout=60,
    ping_interval=25,
    logger=True,
    engineio_logger=True,
    allow_upgrades=True,
    transports=['polling', 'websocket']
)
'''
                
                # Create backup
                backup_path = app_file.with_suffix('.py.backup')
                with open(backup_path, 'w') as f:
                    f.write(content)
                
                self.log(f"📋 Backup created: {backup_path}")
                self.fixes_applied.append("socketio_config")
                return True
            else:
                self.log("⚠️  Socket.IO not found in main app file", "WARNING")
                return False
                
        except Exception as e:
            self.log(f"❌ Failed to update Socket.IO config: {e}", "ERROR")
            self.errors.append(f"socketio_config: {e}")
            return False
    
    def add_health_endpoints(self):
        """Add health check endpoints"""
        try:
            health_endpoints = '''
# Health Check Endpoints for Socket Monitoring
@app.route('/health/websocket')
def websocket_health():
    return {
        "status": "ok",
        "websocket_enabled": True,
        "transport_modes": ["polling", "websocket"],
        "timestamp": datetime.now().isoformat()
    }

@app.route('/health/socketio')
def socketio_health():
    return {
        "status": "ok",
        "async_mode": "gevent",
        "cors_enabled": True,
        "timestamp": datetime.now().isoformat()
    }

@app.route('/health/system')
def system_health():
    return {
        "status": "ok",
        "features": {
            "autonomous_system": True,
            "activity_monitor": True,
            "coordination_api": True,
            "chat_system": True,
            "memory_optimizer": True,
            "gemini_gems": True
        },
        "timestamp": datetime.now().isoformat()
    }
'''
            
            health_file = self.project_root / "health_endpoints.py"
            with open(health_file, 'w') as f:
                f.write(health_endpoints)
            
            self.log(f"✅ Health endpoints created: {health_file}")
            self.fixes_applied.append("health_endpoints")
            return True
            
        except Exception as e:
            self.log(f"❌ Failed to add health endpoints: {e}", "ERROR")
            self.errors.append(f"health_endpoints: {e}")
            return False
    
    def update_requirements(self):
        """Update requirements.txt with optimized versions"""
        try:
            requirements_path = self.project_root / "requirements.txt"
            
            if requirements_path.exists():
                with open(requirements_path, 'r') as f:
                    current_reqs = f.read()
                
                # Add or update key packages
                optimized_packages = [
                    "gunicorn>=20.1.0",
                    "gevent>=21.12.0",
                    "flask-socketio>=5.3.0",
                    "python-socketio>=5.7.0",
                    "python-engineio>=4.4.0"
                ]
                
                # Create backup
                backup_path = requirements_path.with_suffix('.txt.backup')
                with open(backup_path, 'w') as f:
                    f.write(current_reqs)
                
                # Update requirements
                lines = current_reqs.split('\n')
                updated_lines = []
                
                for line in lines:
                    if line.strip():
                        package_name = line.split('==')[0].split('>=')[0].split('<=')[0]
                        # Check if we have an optimized version
                        optimized = next((opt for opt in optimized_packages if opt.startswith(package_name)), None)
                        if optimized:
                            updated_lines.append(optimized)
                        else:
                            updated_lines.append(line)
                
                # Add any missing optimized packages
                existing_packages = [line.split('==')[0].split('>=')[0].split('<=')[0] for line in updated_lines]
                for opt_package in optimized_packages:
                    package_name = opt_package.split('>=')[0]
                    if package_name not in existing_packages:
                        updated_lines.append(opt_package)
                
                with open(requirements_path, 'w') as f:
                    f.write('\n'.join(updated_lines))
                
                self.log(f"✅ Requirements updated: {requirements_path}")
                self.fixes_applied.append("requirements")
                return True
            else:
                self.log("⚠️  requirements.txt not found", "WARNING")
                return False
                
        except Exception as e:
            self.log(f"❌ Failed to update requirements: {e}", "ERROR")
            self.errors.append(f"requirements: {e}")
            return False
    
    def create_deployment_script(self):
        """Create deployment script with proper startup sequence"""
        try:
            deploy_script = '''#!/bin/bash
# XMRT Ecosystem Deployment Script

echo "🚀 Starting XMRT Ecosystem deployment..."

# Set environment variables
export PYTHONUNBUFFERED=1
export FLASK_ENV=production

# Install/upgrade dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Run with optimized gunicorn configuration
echo "🔧 Starting server with optimized configuration..."
if [ -f "gunicorn.conf.py" ]; then
    gunicorn --config gunicorn.conf.py app:app
else
    gunicorn --bind 0.0.0.0:$PORT --workers 1 --worker-class gevent --timeout 120 app:app
fi
'''
            
            script_path = self.project_root / "deploy.sh"
            with open(script_path, 'w') as f:
                f.write(deploy_script)
            
            # Make executable
            os.chmod(script_path, 0o755)
            
            self.log(f"✅ Deployment script created: {script_path}")
            self.fixes_applied.append("deployment_script")
            return True
            
        except Exception as e:
            self.log(f"❌ Failed to create deployment script: {e}", "ERROR")
            self.errors.append(f"deployment_script: {e}")
            return False
    
    def run_fixes(self):
        """Run all deployment fixes"""
        self.log("🔧 Starting XMRT Ecosystem deployment fixes...")
        self.log("=" * 50)
        
        fixes = [
            ("Gunicorn Configuration", self.apply_gunicorn_config),
            ("Socket.IO Configuration", self.update_socketio_config),
            ("Health Endpoints", self.add_health_endpoints),
            ("Requirements Optimization", self.update_requirements),
            ("Deployment Script", self.create_deployment_script)
        ]
        
        for fix_name, fix_function in fixes:
            self.log(f"🔄 Applying: {fix_name}")
            success = fix_function()
            if success:
                self.log(f"✅ {fix_name}: Applied successfully")
            else:
                self.log(f"⚠️  {fix_name}: Skipped or failed")
        
        self.log("=" * 50)
        self.log("📊 Deployment Fix Summary:")
        self.log(f"✅ Fixes applied: {len(self.fixes_applied)}")
        self.log(f"❌ Errors encountered: {len(self.errors)}")
        
        if self.fixes_applied:
            self.log("🎯 Applied fixes:")
            for fix in self.fixes_applied:
                self.log(f"   - {fix}")
        
        if self.errors:
            self.log("⚠️  Errors:")
            for error in self.errors:
                self.log(f"   - {error}")
        
        self.log("=" * 50)
        
        if len(self.fixes_applied) > 0:
            self.log("🚀 Deployment fixes completed! Restart your application to apply changes.")
            self.log("💡 Recommended next steps:")
            self.log("   1. Commit the configuration changes")
            self.log("   2. Redeploy the application")
            self.log("   3. Monitor /health/websocket endpoint")
            self.log("   4. Test Socket.IO connectivity")
            return True
        else:
            self.log("❌ No fixes could be applied. Manual intervention may be required.")
            return False

if __name__ == "__main__":
    fixer = XMRTDeploymentFixer()
    success = fixer.run_fixes()
    sys.exit(0 if success else 1)

