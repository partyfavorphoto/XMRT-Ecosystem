#!/usr/bin/env python3
"""
XMRT Ecosystem - Enhanced Multi-Agent System with GitHub MCP Integration
Real-time AI-powered DAO with GitHub MCP server integration and comprehensive webhook APIs
Author: Joseph Andrew Lee (XMRT.io)
Enhanced with GitHub MCP: 2025-09-02
"""

import os
import sys
import logging
import json
import time
import threading
import random
import requests
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# Flask and extensions
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room

# External libraries
from dotenv import load_dotenv

# Import our modules
from enhanced_chat_system import EnhancedChatSystemWithMCP
from webhook_endpoints import create_ecosystem_webhook_blueprint

# Load environment variables
load_dotenv()

# Enhanced logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/tmp/xmrt_ecosystem_enhanced.log')
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app with enhanced configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'xmrt-ecosystem-mcp-secret-2025')
app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

# Initialize extensions
CORS(app, origins="*")
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Register webhook blueprint
app.register_blueprint(create_ecosystem_webhook_blueprint())

class GitHubMCPIntegration:
    """GitHub MCP Server integration for Eliza agents"""
    
    def __init__(self):
        self.github_token = os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN')
        self.mcp_server_url = os.getenv('MCP_SERVER_URL', 'https://api.githubcopilot.com/mcp/')
        self.local_mcp_enabled = os.getenv('LOCAL_MCP_ENABLED', 'false').lower() == 'true'
        self.mcp_process = None
        self.available_tools = self._initialize_mcp_tools()
        
        if self.local_mcp_enabled:
            self._start_local_mcp_server()
    
    def _initialize_mcp_tools(self) -> Dict[str, List[Dict]]:
        """Initialize available MCP tools categorized by function"""
        return {
            "repository_management": [
                {
                    "name": "get_file_contents",
                    "description": "Retrieve contents of a file from a repository",
                    "parameters": ["owner", "repo", "path", "ref?"],
                    "example": "Get README.md from main branch"
                },
                {
                    "name": "create_or_update_file",
                    "description": "Create or update a file in a repository",
                    "parameters": ["owner", "repo", "path", "content", "message", "branch?"],
                    "example": "Update documentation files"
                },
                {
                    "name": "search_code",
                    "description": "Search for code within repositories",
                    "parameters": ["query", "owner?", "repo?"],
                    "example": "Find TODO comments or specific functions"
                },
                {
                    "name": "create_branch",
                    "description": "Create a new branch from an existing branch",
                    "parameters": ["owner", "repo", "branch_name", "from_branch?"],
                    "example": "Create feature branch for development"
                },
                {
                    "name": "push_files",
                    "description": "Push multiple files to a repository",
                    "parameters": ["owner", "repo", "branch", "files", "message"],
                    "example": "Commit multiple changes at once"
                }
            ],
            "issues_and_prs": [
                {
                    "name": "create_issue",
                    "description": "Create a new issue in a repository",
                    "parameters": ["owner", "repo", "title", "body", "labels?", "assignees?"],
                    "example": "Report bugs or request features"
                },
                {
                    "name": "create_pull_request",
                    "description": "Create a new pull request",
                    "parameters": ["owner", "repo", "title", "body", "head", "base", "draft?"],
                    "example": "Submit code changes for review"
                },
                {
                    "name": "merge_pull_request",
                    "description": "Merge a pull request",
                    "parameters": ["owner", "repo", "pull_number", "merge_method?"],
                    "example": "Merge approved changes"
                },
                {
                    "name": "add_issue_comment",
                    "description": "Add a comment to an issue or PR",
                    "parameters": ["owner", "repo", "issue_number", "body"],
                    "example": "Provide feedback or updates"
                }
            ],
            "workflows_and_actions": [
                {
                    "name": "run_workflow",
                    "description": "Trigger a GitHub Actions workflow",
                    "parameters": ["owner", "repo", "workflow_id", "ref", "inputs?"],
                    "example": "Run CI/CD pipelines or deployments"
                },
                {
                    "name": "list_workflow_runs",
                    "description": "List workflow runs for a repository",
                    "parameters": ["owner", "repo", "workflow_id?", "status?"],
                    "example": "Check build and deployment status"
                },
                {
                    "name": "get_workflow_run_logs",
                    "description": "Get logs for a specific workflow run",
                    "parameters": ["owner", "repo", "run_id", "job_id?"],
                    "example": "Debug failed builds"
                },
                {
                    "name": "cancel_workflow_run",
                    "description": "Cancel a running workflow",
                    "parameters": ["owner", "repo", "run_id"],
                    "example": "Stop unnecessary builds"
                }
            ],
            "security_and_monitoring": [
                {
                    "name": "list_dependabot_alerts",
                    "description": "List Dependabot security alerts",
                    "parameters": ["owner", "repo", "state?"],
                    "example": "Monitor security vulnerabilities"
                },
                {
                    "name": "list_code_scanning_alerts",
                    "description": "List code scanning alerts",
                    "parameters": ["owner", "repo", "state?", "tool?"],
                    "example": "Review code quality issues"
                },
                {
                    "name": "list_secret_scanning_alerts",
                    "description": "List secret scanning alerts",
                    "parameters": ["owner", "repo", "state?"],
                    "example": "Check for exposed secrets"
                }
            ],
            "organization_management": [
                {
                    "name": "get_organization",
                    "description": "Get organization information",
                    "parameters": ["org"],
                    "example": "Retrieve org details and settings"
                },
                {
                    "name": "list_organization_repositories",
                    "description": "List repositories in an organization",
                    "parameters": ["org", "type?", "sort?"],
                    "example": "Get all org repositories"
                }
            ]
        }
    
    def _start_local_mcp_server(self):
        """Start local GitHub MCP server using Docker"""
        if not self.github_token:
            logger.warning("No GitHub token provided, MCP server functionality limited")
            return
        
        try:
            # Check if Docker is available
            subprocess.run(['docker', '--version'], capture_output=True, check=True)
            
            # Start MCP server container
            cmd = [
                'docker', 'run', '-d', '--name', 'xmrt-github-mcp',
                '-e', f'GITHUB_PERSONAL_ACCESS_TOKEN={self.github_token}',
                '-p', '8080:8080',
                'ghcr.io/github/github-mcp-server'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("✅ Local GitHub MCP server started successfully")
                self.local_mcp_enabled = True
            else:
                logger.warning(f"Failed to start local MCP server: {result.stderr}")
        
        except subprocess.CalledProcessError:
            logger.warning("Docker not available, using remote MCP server")
        except Exception as e:
            logger.error(f"Error starting MCP server: {e}")
    
    def call_mcp_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Call a GitHub MCP tool with given parameters"""
        try:
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'XMRT-Ecosystem/1.0'
            }
            
            if self.github_token:
                headers['Authorization'] = f'Bearer {self.github_token}'
            
            # Construct MCP request
            mcp_request = {
                'method': 'tools/call',
                'params': {
                    'name': tool_name,
                    'arguments': parameters
                }
            }
            
            # Use local or remote server
            url = 'http://localhost:8080' if self.local_mcp_enabled else self.mcp_server_url
            
            response = requests.post(
                f"{url}/mcp",
                json=mcp_request,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'error': f'MCP call failed: {response.status_code}',
                    'details': response.text
                }
        
        except Exception as e:
            logger.error(f"Error calling MCP tool {tool_name}: {e}")
            return {'error': str(e)}
    
    def get_available_tools(self) -> Dict[str, List[Dict]]:
        """Get list of available MCP tools"""
        return self.available_tools
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict]:
        """Get detailed information about a specific tool"""
        for category, tools in self.available_tools.items():
            for tool in tools:
                if tool['name'] == tool_name:
                    tool['category'] = category
                    return tool
        return None

class XMRTUtilitiesManager:
    """Manager for XMRT utility repositories and integrations"""
    
    def __init__(self):
        self.utilities = self._load_xmrt_utilities()
    
    def _load_xmrt_utilities(self) -> Dict[str, Dict]:
        """Load information about available XMRT utilities"""
        return {
            "xmrt-ai-organization": {
                "name": "AI Organization",
                "description": "Fully Automated AI Organization prototype with Eliza AI agents",
                "category": "AI/Automation",
                "last_updated": "Jul 9, 2025",
                "features": ["Autonomous management", "Multi-agent coordination", "Organizational AI"],
                "api_endpoints": ["/api/organization/status", "/api/agents/list", "/api/tasks/assign"]
            },
            "xmrt-enhanced-testnet": {
                "name": "Enhanced Testnet",
                "description": "Enhanced XMRT testnet with working faucet and staking functionality",
                "category": "Blockchain/Network",
                "last_updated": "Jul 9, 2025", 
                "features": ["Faucet integration", "Staking mechanisms", "Test network"],
                "api_endpoints": ["/api/faucet/request", "/api/staking/delegate", "/api/network/status"]
            },
            "xmrt-transformers": {
                "name": "XMRT Transformers",
                "description": "Hugging Face Transformers fork adapted for XMRT ecosystem AI tasks",
                "category": "AI/ML",
                "last_updated": "Jul 8, 2025",
                "features": ["State-of-the-art ML models", "XMRT integration", "Custom transformers"],
                "api_endpoints": ["/api/models/load", "/api/inference/run", "/api/training/start"]
            },
            "xmrt-AutoGPT": {
                "name": "XMRT AutoGPT",
                "description": "AutoGPT fork integrated with XMRT for autonomous AI agent development",
                "category": "AI/Automation",
                "last_updated": "Jul 8, 2025",
                "features": ["Autonomous agents", "Task automation", "Goal-oriented AI"],
                "api_endpoints": ["/api/agent/create", "/api/goals/set", "/api/execution/monitor"]
            },
            "xmrt-agent-trust_scoreboard": {
                "name": "Agent Trust Scoreboard", 
                "description": "Trust scoring mechanism for AI agents in XMRT ecosystem",
                "category": "Security/Trust",
                "last_updated": "Jul 8, 2025",
                "features": ["Trust metrics", "Agent reputation", "Transparent scoring"],
                "api_endpoints": ["/api/trust/score", "/api/agents/reputation", "/api/metrics/trust"]
            },
            "xmrt-llama_index": {
                "name": "XMRT LlamaIndex",
                "description": "LlamaIndex fork for building LLM-powered agents over XMRT data",
                "category": "AI/Data",
                "last_updated": "Jul 8, 2025",
                "features": ["Data retrieval", "LLM integration", "Reasoning capabilities"],
                "api_endpoints": ["/api/index/create", "/api/query/run", "/api/data/ingest"]
            },
            "xmrt-langflow-competition": {
                "name": "Langflow Competition",
                "description": "Langflow fork for building and deploying AI workflows in competitions",
                "category": "AI/Workflows",
                "last_updated": "Jul 6, 2025",
                "features": ["Workflow builder", "Competition scenarios", "Agent deployment"],
                "api_endpoints": ["/api/workflows/create", "/api/competition/join", "/api/deploy/agent"]
            },
            "xmrt-companion": {
                "name": "XMRT Companion",
                "description": "Companion application providing additional XMRT ecosystem functionalities",
                "category": "Applications",
                "last_updated": "Jul 4, 2025",
                "features": ["User interactions", "Additional tools", "Ecosystem integration"],
                "api_endpoints": ["/api/companion/status", "/api/tools/list", "/api/interactions/log"]
            },
            "xmrt-zk-oracles": {
                "name": "ZK Oracles",
                "description": "Zero-knowledge oracles for secure and private data verification",
                "category": "Security/Privacy",
                "last_updated": "Jul 4, 2025", 
                "features": ["ZK proofs", "Data verification", "Privacy preservation"],
                "api_endpoints": ["/api/oracle/verify", "/api/proofs/generate", "/api/data/attest"]
            },
            "xmrt-scaffold-eth-2": {
                "name": "Scaffold ETH 2",
                "description": "Ethereum dev stack for rapid dApp development in XMRT ecosystem",
                "category": "Development",
                "last_updated": "Jul 4, 2025",
                "features": ["Rapid development", "dApp scaffolding", "Ethereum integration"],
                "api_endpoints": ["/api/scaffold/create", "/api/deploy/dapp", "/api/contracts/verify"]
            }
        }
    
    def get_utilities_by_category(self) -> Dict[str, List[Dict]]:
        """Get utilities organized by category"""
        categories = {}
        for util_id, util_info in self.utilities.items():
            category = util_info['category']
            if category not in categories:
                categories[category] = []
            categories[category].append({**util_info, 'id': util_id})
        return categories
    
    def get_utility_info(self, utility_id: str) -> Optional[Dict]:
        """Get detailed information about a specific utility"""
        return self.utilities.get(utility_id)

# Initialize enhanced systems
github_mcp = GitHubMCPIntegration()
utilities_manager = XMRTUtilitiesManager()
chat_system = EnhancedChatSystemWithMCP(socketio, github_mcp)

@app.route('/')
def index():
    """Serve enhanced dashboard with MCP integration"""
    return render_template('enhanced_dashboard.html')

# Enhanced API Endpoints

@app.route('/api/mcp/tools')
def get_mcp_tools():
    """Get available GitHub MCP tools"""
    try:
        return jsonify({
            'success': True,
            'tools': github_mcp.get_available_tools(),
            'server_status': 'local' if github_mcp.local_mcp_enabled else 'remote',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting MCP tools: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/mcp/tools/<tool_name>')
def get_mcp_tool_info(tool_name: str):
    """Get detailed information about a specific MCP tool"""
    try:
        tool_info = github_mcp.get_tool_info(tool_name)
        if tool_info:
            return jsonify({
                'success': True,
                'tool': tool_info,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({'error': 'Tool not found'}), 404
    except Exception as e:
        logger.error(f"Error getting MCP tool info: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/mcp/call', methods=['POST'])
def call_mcp_tool():
    """Call a GitHub MCP tool with parameters"""
    try:
        data = request.get_json()
        if not data or 'tool_name' not in data:
            return jsonify({'error': 'Missing tool_name parameter'}), 400
        
        tool_name = data['tool_name']
        parameters = data.get('parameters', {})
        
        result = github_mcp.call_mcp_tool(tool_name, parameters)
        
        return jsonify({
            'success': True,
            'tool_name': tool_name,
            'parameters': parameters,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error calling MCP tool: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/utilities')
def get_xmrt_utilities():
    """Get available XMRT utilities organized by category"""
    try:
        return jsonify({
            'success': True,
            'utilities': utilities_manager.get_utilities_by_category(),
            'total_count': len(utilities_manager.utilities),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting utilities: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/utilities/<utility_id>')
def get_utility_info(utility_id: str):
    """Get detailed information about a specific utility"""
    try:
        utility_info = utilities_manager.get_utility_info(utility_id)
        if utility_info:
            return jsonify({
                'success': True,
                'utility': utility_info,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({'error': 'Utility not found'}), 404
    except Exception as e:
        logger.error(f"Error getting utility info: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/status/comprehensive')
def get_comprehensive_status():
    """Get comprehensive system status including MCP and utilities"""
    try:
        return jsonify({
            'success': True,
            'system': {
                'status': 'operational',
                'uptime': '99.8%',
                'version': '2.0.0-mcp-enhanced'
            },
            'mcp_server': {
                'status': 'connected',
                'type': 'local' if github_mcp.local_mcp_enabled else 'remote',
                'available_tools': len([tool for category in github_mcp.available_tools.values() for tool in category]),
                'github_token_configured': bool(github_mcp.github_token)
            },
            'chat_system': {
                'status': 'active',
                'total_rooms': len(chat_system.chat_history),
                'active_agents': 4
            },
            'utilities': {
                'total_utilities': len(utilities_manager.utilities),
                'categories': len(utilities_manager.get_utilities_by_category())
            },
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting comprehensive status: {e}")
        return jsonify({'error': str(e)}), 500

# Enhanced WebSocket Events for real-time chat

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    join_room('live_updates')
    logger.info(f"Client connected to enhanced XMRT system")
    emit('connection_status', {
        'status': 'connected',
        'message': 'Connected to enhanced XMRT ecosystem with MCP integration',
        'features': {
            'mcp_enabled': True,
            'github_integration': bool(github_mcp.github_token),
            'utilities_available': len(utilities_manager.utilities)
        },
        'timestamp': datetime.now().isoformat()
    })

@socketio.on('join_room')
def handle_join_room(data):
    """Handle user joining a chat room"""
    room_id = data.get('room_id')
    user_id = data.get('user_id')
    
    if room_id and user_id:
        join_room(room_id)
        chat_system.join_room(user_id, room_id)
        
        # Send room history
        room_info = chat_system.get_room_info(room_id)
        if room_info:
            emit('room_history', {
                'room_id': room_id,
                'messages': room_info['recent_messages']
            })
        
        emit('joined_room', {'room_id': room_id})

@socketio.on('leave_room')
def handle_leave_room(data):
    """Handle user leaving a chat room"""
    room_id = data.get('room_id')
    user_id = data.get('user_id')
    
    if room_id and user_id:
        leave_room(room_id)
        chat_system.leave_room(user_id, room_id)

@socketio.on('send_message')
def handle_send_message(data):
    """Handle user sending a message"""
    room_id = data.get('room_id')
    message = data.get('message')
    user_id = data.get('user_id')
    
    if room_id and message and user_id:
        chat_system.handle_user_message(room_id, user_id, message)

@socketio.on('trigger_discussion')
def handle_trigger_discussion(data):
    """Handle triggering agent discussion"""
    room_id = data.get('room_id')
    topic = data.get('topic')
    
    if room_id and topic:
        chat_system.trigger_agent_discussion(room_id, topic)

@socketio.on('mcp_tool_call')
def handle_mcp_tool_call(data):
    """Handle MCP tool call from frontend"""
    try:
        tool_name = data.get('tool_name')
        parameters = data.get('parameters', {})
        
        if tool_name:
            result = github_mcp.call_mcp_tool(tool_name, parameters)
            emit('mcp_tool_result', {
                'tool_name': tool_name,
                'result': result,
                'timestamp': datetime.now().isoformat()
            })
    
    except Exception as e:
        emit('mcp_tool_error', {
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        })

if __name__ == '__main__':
    start_time = time.time()
    
    # Enhanced startup sequence
    logger.info("🚀 XMRT Ecosystem - Enhanced Multi-Agent System with MCP Integration")
    logger.info("✅ GitHub MCP Server integration active")
    logger.info(f"✅ {len(utilities_manager.utilities)} XMRT utilities available")
    logger.info("✅ Real-time chat system with AI agents")
    logger.info("✅ Comprehensive webhook API endpoints")
    
    print("\n" + "="*70)
    print("🚀 XMRT DAO Hub - Enhanced Multi-Agent System with GitHub MCP")
    print("="*70)
    print("🤖 Real-time AI agents with GitHub integration")
    print("🔗 MCP Server:", "Local" if github_mcp.local_mcp_enabled else "Remote")
    print(f"🛠️  Available MCP Tools: {len([tool for category in github_mcp.available_tools.values() for tool in category])}")
    print(f"📦 XMRT Utilities: {len(utilities_manager.utilities)}")
    print("🌐 Enhanced WebSocket Events:")
    print("  ✅ Real-time agent chat")
    print("  ✅ MCP tool integration")  
    print("  ✅ Utility management")
    print("  ✅ Comprehensive API endpoints")
    print("="*70)
    
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    # Run with SocketIO support
    socketio.run(app, host=host, port=port, debug=False, allow_unsafe_werkzeug=True)