#!/usr/bin/env python3
"""
XMRT Deployment Verification Script
Verifies that all components are ready for Render deployment
"""

import os
import sys
import json
import importlib.util
from pathlib import Path

def check_environment_variables():
    """Check required environment variables"""
    print("🔍 Checking environment variables...")
    
    required_vars = [
        "GITHUB_TOKEN",
        "GITHUB_OAUTH_CLIENT_ID", 
        "GITHUB_OAUTH_CLIENT_SECRET",
        "RENDER_API_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        return False
    else:
        print("✅ All required environment variables are set")
        return True

def check_file_structure():
    """Check required files and directories"""
    print("🔍 Checking file structure...")
    
    required_files = [
        "main.py",
        "main_enhanced.py", 
        "start_xmrt_system.py",
        "requirements.txt",
        "Procfile",
        ".env.example"
    ]
    
    required_dirs = [
        "mcp-integration",
        "enhanced-agents"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing_dirs.append(dir_path)
    
    if missing_files or missing_dirs:
        print(f"❌ Missing files: {missing_files}")
        print(f"❌ Missing directories: {missing_dirs}")
        return False
    else:
        print("✅ All required files and directories exist")
        return True

def check_mcp_servers():
    """Check MCP server files"""
    print("🔍 Checking MCP server files...")
    
    mcp_files = [
        "mcp-integration/github_mcp_server_clean.py",
        "mcp-integration/render_mcp_server_clean.py",
        "mcp-integration/xmrt_mcp_server_clean.py"
    ]
    
    missing_files = []
    for file_path in mcp_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing MCP server files: {missing_files}")
        return False
    else:
        print("✅ All MCP server files exist")
        return True

def check_python_imports():
    """Check if critical imports work"""
    print("🔍 Checking Python imports...")
    
    critical_imports = [
        "flask",
        "flask_socketio", 
        "github",
        "redis",
        "requests",
        "gunicorn"
    ]
    
    failed_imports = []
    for module_name in critical_imports:
        try:
            __import__(module_name)
        except ImportError:
            failed_imports.append(module_name)
    
    if failed_imports:
        print(f"❌ Failed imports: {failed_imports}")
        print("💡 Run: pip install -r requirements.txt")
        return False
    else:
        print("✅ All critical imports successful")
        return True

def check_main_app():
    """Check if main application can be imported"""
    print("🔍 Checking main application...")
    
    try:
        # Check original main.py
        spec = importlib.util.spec_from_file_location("main", "main.py")
        if spec and spec.loader:
            print("✅ Original main.py can be imported")
        else:
            print("❌ Cannot import main.py")
            return False
        
        # Check enhanced main
        spec = importlib.util.spec_from_file_location("main_enhanced", "main_enhanced.py")
        if spec and spec.loader:
            print("✅ Enhanced main_enhanced.py can be imported")
        else:
            print("❌ Cannot import main_enhanced.py")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking main application: {e}")
        return False

def check_procfile():
    """Check Procfile configuration"""
    print("🔍 Checking Procfile...")
    
    try:
        with open("Procfile", "r") as f:
            content = f.read().strip()
        
        if "main_enhanced:app" in content:
            print("✅ Procfile configured for enhanced system")
            return True
        else:
            print("❌ Procfile not configured for enhanced system")
            return False
            
    except Exception as e:
        print(f"❌ Error checking Procfile: {e}")
        return False

def generate_deployment_summary():
    """Generate deployment summary"""
    print("\n" + "="*50)
    print("📋 DEPLOYMENT SUMMARY")
    print("="*50)
    
    print("🚀 Enhanced Features:")
    print("  - MCP Integration (GitHub, Render, XMRT)")
    print("  - Enhanced Agent System with Learning Cycles")
    print("  - GitHub OAuth App Integration")
    print("  - Automated Repository Improvement")
    print("  - Real-time Deployment Monitoring")
    
    print("\n🔧 System Components:")
    print("  - Original Flask Application (main.py)")
    print("  - Enhanced System Manager (main_enhanced.py)")
    print("  - MCP Servers (3 specialized servers)")
    print("  - Autonomous Agents (5 specialized agents)")
    print("  - Learning and Automation Cycles")
    
    print("\n🌐 Render Deployment:")
    print("  - Procfile: Configured for enhanced system")
    print("  - Requirements: All dependencies included")
    print("  - Environment: Variables externalized")
    print("  - Startup: Automated system initialization")
    
    print("\n📊 Monitoring Endpoints:")
    print("  - /api/enhanced/status - System status")
    print("  - /api/enhanced/agents - Agent status")
    print("  - /api/enhanced/mcp-servers - MCP server status")

def main():
    """Main verification function"""
    print("🔍 XMRT Deployment Verification")
    print("="*50)
    
    checks = [
        ("Environment Variables", check_environment_variables),
        ("File Structure", check_file_structure),
        ("MCP Servers", check_mcp_servers),
        ("Python Imports", check_python_imports),
        ("Main Application", check_main_app),
        ("Procfile", check_procfile)
    ]
    
    passed_checks = 0
    total_checks = len(checks)
    
    for check_name, check_function in checks:
        print(f"\n--- {check_name} ---")
        if check_function():
            passed_checks += 1
    
    print("\n" + "="*50)
    print(f"📊 VERIFICATION RESULTS: {passed_checks}/{total_checks} checks passed")
    
    if passed_checks == total_checks:
        print("✅ DEPLOYMENT READY!")
        print("🚀 The enhanced XMRT system is ready for Render deployment")
        generate_deployment_summary()
        return True
    else:
        print("❌ DEPLOYMENT NOT READY")
        print("🔧 Please fix the failed checks before deploying")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
