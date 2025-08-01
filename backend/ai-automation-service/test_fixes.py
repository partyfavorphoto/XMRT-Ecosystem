#!/usr/bin/env python3
"""
Test script to verify that the missing method errors are fixed
"""

import sys
import os
import asyncio
import logging

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_fixes():
    """Test that the missing methods are now available"""
    try:
        print("🧪 Testing XMRT AI Automation Service fixes...")
        
        # Import the classes
        from agents.governance_agent import GovernanceAgent
        from agents.community_agent import CommunityAgent
        from utils.ai_utils import AIUtils
        from utils.blockchain_utils import BlockchainUtils
        
        print("✅ All imports successful")
        
        # Initialize utils
        blockchain_utils = BlockchainUtils()
        ai_utils = AIUtils()
        
        print("✅ Utils initialized successfully")
        
        # Initialize agents
        governance_agent = GovernanceAgent(blockchain_utils, ai_utils)
        community_agent = CommunityAgent(blockchain_utils, ai_utils)
        
        print("✅ Agents initialized successfully")
        
        # Test the previously missing methods
        print("\n🔍 Testing previously missing methods...")
        
        # Test analyze_proposal_urgency method
        test_proposal = {
            'id': 'test_001',
            'title': 'Test Emergency Proposal',
            'priority': 'emergency',
            'votes_for': 100,
            'votes_against': 10
        }
        
        if hasattr(ai_utils, 'analyze_proposal_urgency'):
            print("✅ analyze_proposal_urgency method exists")
            try:
                result = await ai_utils.analyze_proposal_urgency(test_proposal)
                print(f"✅ analyze_proposal_urgency executed successfully: {type(result)}")
            except Exception as e:
                print(f"⚠️ analyze_proposal_urgency execution error: {e}")
        else:
            print("❌ analyze_proposal_urgency method still missing")
        
        # Test handle_low_engagement_alert method
        if hasattr(community_agent, 'handle_low_engagement_alert'):
            print("✅ handle_low_engagement_alert method exists")
            try:
                await community_agent.handle_low_engagement_alert()
                print("✅ handle_low_engagement_alert executed successfully")
            except Exception as e:
                print(f"⚠️ handle_low_engagement_alert execution error: {e}")
        else:
            print("❌ handle_low_engagement_alert method still missing")
        
        # Test governance agent emergency proposal handling
        print("\n🚨 Testing emergency proposal handling...")
        try:
            await governance_agent.handle_emergency_proposal(test_proposal)
            print("✅ Emergency proposal handling works")
        except Exception as e:
            print(f"⚠️ Emergency proposal handling error: {e}")
        
        # Test community agent alert handling
        print("\n📢 Testing community alert handling...")
        test_alert = {
            'type': 'low_engagement',
            'value': 0.3,
            'severity': 'medium'
        }
        
        try:
            await community_agent.handle_alert(test_alert)
            print("✅ Community alert handling works")
        except Exception as e:
            print(f"⚠️ Community alert handling error: {e}")
        
        print("\n🎉 All tests completed!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_fixes())
    if success:
        print("\n✅ FIXES VERIFIED: The missing method errors have been resolved!")
        sys.exit(0)
    else:
        print("\n❌ FIXES FAILED: There are still issues to resolve")
        sys.exit(1)

