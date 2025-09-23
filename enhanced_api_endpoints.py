"""
Enhanced API Endpoints for XMRT Ecosystem
New endpoints for DApp Factory, BrightData MCP, and AI Tool Management
"""

from flask import Blueprint, request, jsonify
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

# Import our new modules (these would be available after integration)
# from web3_dapp_factory import Web3DAppFactory, DAppConfig
# from brightdata_mcp_integration import BrightDataMCP, MCPRequest
# from ai_tool_framework import XMRTToolIntegration, ToolConfig, AgentBlueprint

logger = logging.getLogger(__name__)

# Create Blueprint for new API endpoints
xmrt_enhanced_api = Blueprint('xmrt_enhanced', __name__, url_prefix='/api/xmrt')

# Global instances (would be initialized in main app)
dapp_factory = None
mcp_client = None
tool_integration = None

def initialize_enhanced_services():
    """Initialize enhanced services for the API endpoints"""
    global dapp_factory, mcp_client, tool_integration

    try:
        # Initialize Web3 DApp Factory
        dapp_factory = Web3DAppFactory()
        logger.info("Web3 DApp Factory initialized")

        # Initialize BrightData MCP
        mcp_config = {
            "rate_limit": 10,
            "cache_ttl": 3600
        }
        mcp_client = BrightDataMCP(mcp_config)
        logger.info("BrightData MCP initialized")

        # Initialize AI Tool Integration
        tool_integration = XMRTToolIntegration()
        logger.info("AI Tool Integration initialized")

        return True
    except Exception as e:
        logger.error(f"Failed to initialize enhanced services: {e}")
        return False

@xmrt_enhanced_api.route('/status', methods=['GET'])
def get_enhanced_status():
    """Get status of all enhanced XMRT services"""
    try:
        status = {
            "services": {
                "dapp_factory": {
                    "active": dapp_factory is not None,
                    "deployed_dapps": len(dapp_factory.deployed_dapps) if dapp_factory else 0,
                    "supported_networks": ["ethereum", "polygon", "bsc", "arbitrum"]
                },
                "brightdata_mcp": {
                    "active": mcp_client is not None,
                    "cached_requests": len(mcp_client.request_cache) if mcp_client else 0,
                    "supported_protocols": ["ethereum", "polygon", "bsc"]
                },
                "ai_tool_integration": {
                    "active": tool_integration is not None,
                    "active_tools": len(tool_integration.tool_factory.active_tools) if tool_integration else 0,
                    "active_agents": len(tool_integration.agent_system.active_agents) if tool_integration else 0
                }
            },
            "system": {
                "version": "2.0.0-enhanced",
                "uptime": "continuous",
                "health_score": 95
            },
            "timestamp": datetime.now().isoformat()
        }

        return jsonify(status), 200

    except Exception as e:
        logger.error(f"Error getting enhanced status: {e}")
        return jsonify({"error": str(e)}), 500

# ============================================================================
# DApp Factory Endpoints
# ============================================================================

@xmrt_enhanced_api.route('/dapp/create', methods=['POST'])
def create_dapp():
    """Create a new DApp using the Web3 DApp Factory"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Create DApp configuration
        dapp_config = DAppConfig(
            name=data.get('name', 'Unnamed DApp'),
            description=data.get('description', 'A DApp created with XMRT Factory'),
            blockchain=data.get('blockchain', 'ethereum'),
            contract_type=data.get('contract_type', 'standard'),
            features=data.get('features', []),
            ai_agent_integration=data.get('ai_integration', True)
        )

        # Create DApp
        dapp_package = dapp_factory.create_dapp(dapp_config)

        # Create specialized AI agent if requested
        if dapp_config.ai_agent_integration:
            agent = tool_integration.create_specialized_dapp_agent({
                "name": dapp_config.name,
                "type": dapp_config.contract_type,
                "blockchain": dapp_config.blockchain,
                "features": dapp_config.features
            })
            dapp_package["ai_agent"] = agent

        return jsonify({
            "success": True,
            "dapp": {
                "name": dapp_config.name,
                "id": dapp_config.id,
                "contract_type": dapp_config.contract_type,
                "blockchain": dapp_config.blockchain,
                "features": dapp_config.features,
                "created_at": dapp_package["created_at"],
                "status": dapp_package["status"]
            },
            "message": f"DApp '{dapp_config.name}' created successfully"
        }), 201

    except Exception as e:
        logger.error(f"Error creating DApp: {e}")
        return jsonify({"error": str(e)}), 500

@xmrt_enhanced_api.route('/dapp/<dapp_name>/deploy', methods=['POST'])
def deploy_dapp(dapp_name):
    """Deploy a DApp to blockchain network"""
    try:
        data = request.get_json() or {}
        network = data.get('network', 'ethereum')

        # Deploy DApp
        deployment_result = dapp_factory.deploy_dapp(dapp_name, network)

        return jsonify({
            "success": True,
            "deployment": deployment_result,
            "message": f"DApp '{dapp_name}' deployed to {network}"
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error(f"Error deploying DApp: {e}")
        return jsonify({"error": str(e)}), 500

@xmrt_enhanced_api.route('/dapp/<dapp_name>/analytics', methods=['GET'])
def get_dapp_analytics(dapp_name):
    """Get analytics for a deployed DApp"""
    try:
        analytics = dapp_factory.get_dapp_analytics(dapp_name)
        return jsonify(analytics), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error(f"Error getting DApp analytics: {e}")
        return jsonify({"error": str(e)}), 500

@xmrt_enhanced_api.route('/dapp/list', methods=['GET'])
def list_dapps():
    """List all created DApps"""
    try:
        dapps = []
        for name, dapp in dapp_factory.deployed_dapps.items():
            dapps.append({
                "name": name,
                "status": dapp["status"],
                "blockchain": dapp["config"].blockchain,
                "contract_type": dapp["config"].contract_type,
                "created_at": dapp["created_at"],
                "ai_integration": dapp["config"].ai_agent_integration
            })

        return jsonify({
            "dapps": dapps,
            "total": len(dapps)
        }), 200

    except Exception as e:
        logger.error(f"Error listing DApps: {e}")
        return jsonify({"error": str(e)}), 500

# ============================================================================
# BrightData MCP Endpoints
# ============================================================================

@xmrt_enhanced_api.route('/mcp/scrape', methods=['POST'])
def scrape_url():
    """Scrape URL using BrightData MCP"""
    try:
        data = request.get_json()

        if not data or 'url' not in data:
            return jsonify({"error": "URL is required"}), 400

        # Create MCP request
        mcp_request = MCPRequest(
            method='GET',
            url=data['url'],
            params=data.get('params', {}),
            headers=data.get('headers', {}),
            timeout=data.get('timeout', 30)
        )

        # Execute request asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(mcp_client.fetch_url(mcp_request))
        loop.close()

        return jsonify({
            "success": response.success,
            "status_code": response.status_code,
            "content_length": len(response.content),
            "metadata": response.metadata,
            "timestamp": response.timestamp.isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error scraping URL: {e}")
        return jsonify({"error": str(e)}), 500

@xmrt_enhanced_api.route('/mcp/defi/<protocol>', methods=['GET'])
def get_defi_data(protocol):
    """Get DeFi protocol data"""
    try:
        data_type = request.args.get('type', 'tvl')

        # Fetch DeFi data asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        defi_data = loop.run_until_complete(mcp_client.scrape_defi_data(protocol, data_type))
        loop.close()

        return jsonify({
            "protocol": protocol,
            "data_type": data_type,
            "data": defi_data,
            "timestamp": datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error getting DeFi data: {e}")
        return jsonify({"error": str(e)}), 500

@xmrt_enhanced_api.route('/mcp/blockchain/<network>/analytics', methods=['GET'])
def get_blockchain_analytics(network):
    """Get blockchain analytics for specified network"""
    try:
        metrics = request.args.getlist('metrics') or None

        # Fetch blockchain analytics asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        analytics = loop.run_until_complete(mcp_client.fetch_blockchain_analytics(network, metrics))
        loop.close()

        return jsonify(analytics), 200

    except Exception as e:
        logger.error(f"Error getting blockchain analytics: {e}")
        return jsonify({"error": str(e)}), 500

@xmrt_enhanced_api.route('/mcp/contract/<contract_address>/monitor', methods=['GET'])
def monitor_contract(contract_address):
    """Monitor smart contract activity"""
    try:
        network = request.args.get('network', 'ethereum')

        # Monitor contract asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        contract_data = loop.run_until_complete(mcp_client.monitor_smart_contract(contract_address, network))
        loop.close()

        return jsonify(contract_data), 200

    except Exception as e:
        logger.error(f"Error monitoring contract: {e}")
        return jsonify({"error": str(e)}), 500

# ============================================================================
# AI Tool Framework Endpoints
# ============================================================================

@xmrt_enhanced_api.route('/tools/create', methods=['POST'])
def create_tool():
    """Create a new AI tool"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Create tool configuration
        tool_config = ToolConfig(
            name=data.get('name', 'Unnamed Tool'),
            description=data.get('description', 'A tool created with XMRT Framework'),
            tool_type=data.get('tool_type', 'custom'),
            parameters=data.get('parameters', {}),
            capabilities=data.get('capabilities', []),
            requirements=data.get('requirements', []),
            ai_integration=data.get('ai_integration', True)
        )

        # Create tool
        tool = tool_integration.tool_factory.create_tool(tool_config)

        return jsonify({
            "success": True,
            "tool": tool.get_metadata(),
            "message": f"Tool '{tool_config.name}' created successfully"
        }), 201

    except Exception as e:
        logger.error(f"Error creating tool: {e}")
        return jsonify({"error": str(e)}), 500

@xmrt_enhanced_api.route('/tools/list', methods=['GET'])
def list_tools():
    """List all available AI tools"""
    try:
        tools = tool_integration.tool_factory.list_tools()

        return jsonify({
            "tools": tools,
            "total": len(tools)
        }), 200

    except Exception as e:
        logger.error(f"Error listing tools: {e}")
        return jsonify({"error": str(e)}), 500

@xmrt_enhanced_api.route('/tools/<tool_name>/execute', methods=['POST'])
def execute_tool(tool_name):
    """Execute a specific AI tool"""
    try:
        data = request.get_json() or {}

        # Get tool
        tool = tool_integration.tool_factory.get_tool(tool_name)
        if not tool:
            return jsonify({"error": f"Tool '{tool_name}' not found"}), 404

        # Execute tool asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(tool.execute(**data))
        loop.close()

        return jsonify({
            "tool": tool_name,
            "result": result,
            "execution_time": datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error executing tool: {e}")
        return jsonify({"error": str(e)}), 500

@xmrt_enhanced_api.route('/agents/create', methods=['POST'])
def create_agent():
    """Create a new AI agent from blueprint"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        blueprint_id = data.get('blueprint_id')
        customizations = data.get('customizations', {})

        if not blueprint_id:
            return jsonify({"error": "Blueprint ID is required"}), 400

        # Clone agent
        agent = tool_integration.agent_system.clone_agent(blueprint_id, customizations)

        return jsonify({
            "success": True,
            "agent": agent,
            "message": f"Agent '{agent['name']}' created successfully"
        }), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error(f"Error creating agent: {e}")
        return jsonify({"error": str(e)}), 500

@xmrt_enhanced_api.route('/agents/list', methods=['GET'])
def list_agents():
    """List all active AI agents"""
    try:
        agents = []
        for agent_id, agent in tool_integration.agent_system.active_agents.items():
            agents.append({
                "id": agent_id,
                "name": agent["name"],
                "type": agent["agent_type"],
                "status": agent["status"],
                "capabilities": agent["capabilities"][:5],  # First 5 capabilities
                "created_at": agent["created_at"]
            })

        return jsonify({
            "agents": agents,
            "total": len(agents)
        }), 200

    except Exception as e:
        logger.error(f"Error listing agents: {e}")
        return jsonify({"error": str(e)}), 500

@xmrt_enhanced_api.route('/agents/<agent_id>/specialize', methods=['POST'])
def specialize_agent(agent_id):
    """Add specialization to an existing agent"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No specialization data provided"}), 400

        # Specialize agent
        agent = tool_integration.agent_system.specialize_agent(agent_id, data)

        return jsonify({
            "success": True,
            "agent": agent,
            "message": f"Agent '{agent['name']}' specialized successfully"
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error(f"Error specializing agent: {e}")
        return jsonify({"error": str(e)}), 500

@xmrt_enhanced_api.route('/agents/recommendations', methods=['POST'])
def get_agent_recommendations():
    """Get agent recommendations for a specific task"""
    try:
        data = request.get_json()

        if not data or 'task_description' not in data:
            return jsonify({"error": "Task description is required"}), 400

        task_description = data['task_description']

        # Get recommendations
        recommendations = tool_integration.agent_system.get_agent_recommendations(task_description)

        return jsonify({
            "task_description": task_description,
            "recommendations": recommendations,
            "total": len(recommendations)
        }), 200

    except Exception as e:
        logger.error(f"Error getting agent recommendations: {e}")
        return jsonify({"error": str(e)}), 500

# ============================================================================
# Integration Status and Management
# ============================================================================

@xmrt_enhanced_api.route('/integration/status', methods=['GET'])
def get_integration_status():
    """Get comprehensive integration status"""
    try:
        status = tool_integration.get_integration_status()

        # Add additional system information
        status["enhanced_features"] = {
            "dapp_factory": True,
            "brightdata_mcp": True,
            "ai_tool_framework": True,
            "dynamic_agent_cloning": True,
            "web3_interactions": True
        }

        return jsonify(status), 200

    except Exception as e:
        logger.error(f"Error getting integration status: {e}")
        return jsonify({"error": str(e)}), 500

@xmrt_enhanced_api.route('/integration/health', methods=['GET'])
def health_check():
    """Comprehensive health check for all enhanced services"""
    try:
        health_status = {
            "overall": "healthy",
            "services": {},
            "timestamp": datetime.now().isoformat()
        }

        # Check DApp Factory
        try:
            if dapp_factory and hasattr(dapp_factory, 'deployed_dapps'):
                health_status["services"]["dapp_factory"] = {
                    "status": "healthy",
                    "deployed_dapps": len(dapp_factory.deployed_dapps)
                }
            else:
                health_status["services"]["dapp_factory"] = {
                    "status": "unavailable",
                    "error": "Not initialized"
                }
        except Exception as e:
            health_status["services"]["dapp_factory"] = {
                "status": "error",
                "error": str(e)
            }

        # Check BrightData MCP
        try:
            if mcp_client:
                health_status["services"]["brightdata_mcp"] = {
                    "status": "healthy",
                    "cache_size": len(mcp_client.request_cache) if hasattr(mcp_client, 'request_cache') else 0
                }
            else:
                health_status["services"]["brightdata_mcp"] = {
                    "status": "unavailable",
                    "error": "Not initialized"
                }
        except Exception as e:
            health_status["services"]["brightdata_mcp"] = {
                "status": "error",
                "error": str(e)
            }

        # Check AI Tool Integration
        try:
            if tool_integration:
                health_status["services"]["ai_tool_integration"] = {
                    "status": "healthy",
                    "active_tools": len(tool_integration.tool_factory.active_tools),
                    "active_agents": len(tool_integration.agent_system.active_agents)
                }
            else:
                health_status["services"]["ai_tool_integration"] = {
                    "status": "unavailable",
                    "error": "Not initialized"
                }
        except Exception as e:
            health_status["services"]["ai_tool_integration"] = {
                "status": "error",
                "error": str(e)
            }

        # Determine overall health
        service_statuses = [svc["status"] for svc in health_status["services"].values()]
        if "error" in service_statuses:
            health_status["overall"] = "degraded"
        elif "unavailable" in service_statuses:
            health_status["overall"] = "partial"

        return jsonify(health_status), 200

    except Exception as e:
        logger.error(f"Error in health check: {e}")
        return jsonify({
            "overall": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

# ============================================================================
# Utility Functions for Integration
# ============================================================================

def register_enhanced_routes(app):
    """Register enhanced API routes with Flask app"""
    try:
        app.register_blueprint(xmrt_enhanced_api)

        # Initialize services
        success = initialize_enhanced_services()

        if success:
            logger.info("Enhanced XMRT API endpoints registered successfully")
        else:
            logger.warning("Enhanced API endpoints registered but services initialization failed")

        return success

    except Exception as e:
        logger.error(f"Failed to register enhanced routes: {e}")
        return False

def get_enhanced_api_documentation():
    """Get API documentation for enhanced endpoints"""
    return {
        "version": "2.0.0-enhanced",
        "base_url": "/api/xmrt",
        "endpoints": {
            "system": {
                "/status": {"methods": ["GET"], "description": "Get enhanced system status"},
                "/integration/status": {"methods": ["GET"], "description": "Get integration status"},
                "/integration/health": {"methods": ["GET"], "description": "Comprehensive health check"}
            },
            "dapp_factory": {
                "/dapp/create": {"methods": ["POST"], "description": "Create new DApp"},
                "/dapp/<name>/deploy": {"methods": ["POST"], "description": "Deploy DApp to blockchain"},
                "/dapp/<name>/analytics": {"methods": ["GET"], "description": "Get DApp analytics"},
                "/dapp/list": {"methods": ["GET"], "description": "List all DApps"}
            },
            "brightdata_mcp": {
                "/mcp/scrape": {"methods": ["POST"], "description": "Scrape URL using MCP"},
                "/mcp/defi/<protocol>": {"methods": ["GET"], "description": "Get DeFi protocol data"},
                "/mcp/blockchain/<network>/analytics": {"methods": ["GET"], "description": "Get blockchain analytics"},
                "/mcp/contract/<address>/monitor": {"methods": ["GET"], "description": "Monitor smart contract"}
            },
            "ai_tools": {
                "/tools/create": {"methods": ["POST"], "description": "Create new AI tool"},
                "/tools/list": {"methods": ["GET"], "description": "List all tools"},
                "/tools/<name>/execute": {"methods": ["POST"], "description": "Execute AI tool"}
            },
            "agents": {
                "/agents/create": {"methods": ["POST"], "description": "Create new AI agent"},
                "/agents/list": {"methods": ["GET"], "description": "List all agents"},
                "/agents/<id>/specialize": {"methods": ["POST"], "description": "Specialize agent"},
                "/agents/recommendations": {"methods": ["POST"], "description": "Get agent recommendations"}
            }
        },
        "authentication": "Optional API key authentication",
        "rate_limiting": "10 requests per second per IP",
        "response_format": "JSON"
    }

# Example usage and testing
if __name__ == "__main__":
    # This would be integrated into the main Flask app
    from flask import Flask

    app = Flask(__name__)

    # Register enhanced routes
    register_enhanced_routes(app)

    # Get API documentation
    docs = get_enhanced_api_documentation()
    print(f"Enhanced API Documentation: {docs}")
