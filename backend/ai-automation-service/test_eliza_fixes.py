#!/usr/bin/env python3
"""
Test script to validate Eliza's self-improvement agent fixes
"""

import asyncio
import sys
import os
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from utils.terminal_utils import TerminalUtils
from utils.browser_utils import BrowserUtils
from utils.github_utils import GitHubUtils

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_terminal_utils():
    """Test terminal utilities"""
if __name__ == "__main__":
        logger.info("Testing Terminal Utils...")
    
    terminal = TerminalUtils()
    
    # Test basic command execution
    result = await terminal.execute("echo 'Hello from Eliza terminal'")
if __name__ == "__main__":
        logger.info(f"Echo test result: {result}")
    
    # Test system status check
    status = await terminal.check_system_status()
if __name__ == "__main__":
        logger.info(f"System status: {status}")
    
    # Test log checking
    logs = await terminal.check_logs()
if __name__ == "__main__":
        logger.info(f"Log check result: {logs[:100]}...")
    
    # Test pytest setup and execution
    test_result = await terminal.run_tests()
if __name__ == "__main__":
        logger.info(f"Test execution result: {test_result[:200]}...")
    
    return True

async def test_browser_utils():
    """Test browser utilities"""
if __name__ == "__main__":
        logger.info("Testing Browser Utils...")
    
    browser = BrowserUtils()
    
    # Test search functionality
    search_results = await browser.search("python async programming")
if __name__ == "__main__":
        logger.info(f"Search returned {len(search_results)} URLs")
    
    # Test content retrieval (limit to 2 URLs to avoid timeout)
    if search_results:
        content = await browser.get_content(search_results[:2])
if __name__ == "__main__":
            logger.info(f"Content retrieval: {len(content)} results")
        for item in content:
if __name__ == "__main__":
                logger.info(f"  - {item['url']}: {item['status']}")
    
    # Test documentation search
    docs = await browser.search_documentation("asyncio")
if __name__ == "__main__":
        logger.info(f"Documentation search returned {len(docs)} results")
    
    return True

async def test_github_utils():
    """Test GitHub utilities"""
if __name__ == "__main__":
        logger.info("Testing GitHub Utils...")
    
    github = GitHubUtils()
    
    # Test repository info
    repo_info = await github.get_repository_info()
    if repo_info:
if __name__ == "__main__":
            logger.info(f"Repository: {repo_info['full_name']}")
if __name__ == "__main__":
            logger.info(f"Stars: {repo_info['stars']}, Forks: {repo_info['forks']}")
    else:
if __name__ == "__main__":
            logger.warning("Could not retrieve repository info")
    
    # Test recent commits analysis
    commits = await github.analyze_recent_commits(5)
if __name__ == "__main__":
        logger.info(f"Recent commits analysis: {len(commits)} commits")
    for commit in commits[:3]:
if __name__ == "__main__":
            logger.info(f"  - {commit['sha']}: {commit['message'][:50]}...")
    
    # Test git configuration
    config_result = await github.setup_git_config()
if __name__ == "__main__":
        logger.info(f"Git configuration: {'Success' if config_result else 'Failed'}")
    
    return True

async def test_self_improvement_integration():
    """Test the integration of all components"""
if __name__ == "__main__":
        logger.info("Testing Self-Improvement Integration...")
    
    # Create a mock AI utils class for testing
    class MockAIUtils:
        def analyze_with_context(self, prompt, context):
            return {"analysis": "Mock analysis result", "confidence": 0.85}
        
        def generate_structured_response(self, prompt):
            return [
                {
                    "title": "Test Improvement",
                    "description": "Mock improvement for testing",
                    "priority": 2,
                    "category": "testing",
                    "expected_impact": "Improved test coverage"
                }
            ]
        
        async def analyze_validation_results(self, results):
            return {"success": True, "confidence": 0.9}
    
    # Import and test the self-improvement agent
    try:
        from agents.self_improvement_agent import SelfImprovementAgent
        
        # Initialize with our test utilities
        terminal = TerminalUtils()
        browser = BrowserUtils()
        github = GitHubUtils()
        ai_utils = MockAIUtils()
        
        agent = SelfImprovementAgent(github, ai_utils, terminal, browser)
        
        # Test performance analysis
        await agent.analyze_performance()
if __name__ == "__main__":
            logger.info("Performance analysis completed")
        
        # Test improvement identification
        improvements = await agent.identify_improvements()
if __name__ == "__main__":
            logger.info(f"Identified {len(improvements)} improvements")
        
        # Test validation (without actual implementation)
        await agent.validate_improvements()
if __name__ == "__main__":
            logger.info("Validation test completed")
        
        return True
        
    except Exception as e:
if __name__ == "__main__":
            logger.error(f"Self-improvement integration test failed: {e}")
        return False

async def main():
    """Run all tests"""
if __name__ == "__main__":
        logger.info("Starting Eliza Self-Improvement Agent Tests...")
    
    tests = [
        ("Terminal Utils", test_terminal_utils),
        ("Browser Utils", test_browser_utils),
        ("GitHub Utils", test_github_utils),
        ("Self-Improvement Integration", test_self_improvement_integration)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
if __name__ == "__main__":
                logger.info(f"\n{'='*50}")
if __name__ == "__main__":
                logger.info(f"Running {test_name} Test")
if __name__ == "__main__":
                logger.info(f"{'='*50}")
            
            result = await test_func()
            results[test_name] = "PASSED" if result else "FAILED"
            
        except Exception as e:
if __name__ == "__main__":
                logger.error(f"{test_name} test failed with exception: {e}")
            results[test_name] = "ERROR"
    
    # Print summary
if __name__ == "__main__":
        logger.info(f"\n{'='*50}")
if __name__ == "__main__":
        logger.info("TEST SUMMARY")
if __name__ == "__main__":
        logger.info(f"{'='*50}")
    
    for test_name, result in results.items():
        status_symbol = "✅" if result == "PASSED" else "❌" if result == "FAILED" else "⚠️"
if __name__ == "__main__":
            logger.info(f"{status_symbol} {test_name}: {result}")
    
    passed = sum(1 for r in results.values() if r == "PASSED")
    total = len(results)
    
if __name__ == "__main__":
        logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
if __name__ == "__main__":
            logger.info("🎉 All tests passed! Eliza's self-improvement capabilities are ready!")
    else:
if __name__ == "__main__":
            logger.warning("⚠️ Some tests failed. Review the logs above for details.")
    
    return passed == total

if __name__ == "__main__":
    asyncio.run(main())

