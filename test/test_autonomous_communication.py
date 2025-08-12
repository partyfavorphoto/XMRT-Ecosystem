#!/usr/bin/env python3
"""
Test Enhanced Autonomous Communication System
"""

import asyncio
import json
from enhanced_coordination_api import AutonomousAgentOrchestrator

async def test_autonomous_communication():
    """Test autonomous inter-agent communication"""
    
    orchestrator = AutonomousAgentOrchestrator()
    
    # Test scenarios
    test_scenarios = [
        "New DeFi yield farming opportunity detected",
        "Community proposal for governance changes",
        "Security vulnerability found in smart contract",
        "Treasury optimization strategy needed"
    ]
    
    for scenario in test_scenarios:
        print(f"\n🧪 Testing scenario: {scenario}")
        responses = await orchestrator.initiate_autonomous_communication(scenario)
        
        for response in responses:
            agent_name = response['agent_id'].replace('xmrt_', '').replace('_', ' ').title()
            print(f"  🤖 {agent_name}: {response['message']}")
        
        print(f"  ✅ {len(responses)} agents participated autonomously")

if __name__ == "__main__":
    asyncio.run(test_autonomous_communication())
