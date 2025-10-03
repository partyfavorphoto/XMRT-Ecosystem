#!/usr/bin/env python3
"""
Test script to verify deployment fixes work correctly.
This script tests the key fixes implemented for Render deployment.
"""
import os
import sys
import sqlite3
import tempfile
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_database_schema():
    """Test that the database schema works without SQLite keyword issues."""
    print("🧪 Testing database schema...")
    
    # Import after adding to path
    from main import DB
    
    # Create temporary database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = Path(tmp.name)
    
    try:
        # Initialize database
        db = DB(db_path)
        
        # Test repo upsert (this was failing before)
        db.upsert_repo(
            name="test-repo",
            category="test",
            url="https://github.com/test/test-repo",
            is_fork=False,
            exists=True,
            default_branch="main"
        )
        
        # Test repo listing (this was also failing)
        repos = db.list_repos()
        assert len(repos) == 1
        assert repos[0]['name'] == 'test-repo'
        assert repos[0]['repo_exists'] == 1  # Should be using new column name
        
        print("✅ Database schema test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Database schema test failed: {e}")
        return False
    finally:
        # Clean up
        if db_path.exists():
            db_path.unlink()

def test_github_auth():
    """Test that GitHub authentication uses the new method."""
    print("🧪 Testing GitHub authentication...")
    
    try:
        from main import XMRTGitHub
        
        # Test with None token (should not crash)
        gh = XMRTGitHub(None, "test-org")
        assert gh._client is None
        
        # Test that the new auth method is used when Github and Auth are available
        try:
            from github import Github, Auth
            # This should work without deprecation warning
            fake_token = "fake_token_for_testing"
            gh = XMRTGitHub(fake_token, "test-org")
            # The client should be created (even if token is fake)
            assert gh._client is not None
        except ImportError:
            print("⚠️  PyGithub not available, skipping auth method test")
        
        print("✅ GitHub authentication test passed!")
        return True
        
    except Exception as e:
        print(f"❌ GitHub authentication test failed: {e}")
        return False

def test_flask_routes():
    """Test that Flask app can be created and routes are registered."""
    print("🧪 Testing Flask application routes...")
    
    try:
        # Set required environment variables
        os.environ.setdefault('GITHUB_ORG', 'test-org')
        
        from main import initialize_services
        
        # Initialize the Flask app
        app = initialize_services()
        
        # Test that routes are registered
        with app.test_client() as client:
            # Test root route (was missing before)
            response = client.get('/')
            assert response.status_code == 200
            data = response.get_json()
            assert data['service'] == 'xmrt-main'
            
            # Test health route
            response = client.get('/health')
            assert response.status_code == 200
            
            # Test coordination status route (was missing before)
            response = client.get('/api/coordination/status')
            assert response.status_code == 200
            data = response.get_json()
            assert 'coordination_health' in data
            assert 'system_metrics' in data
        
        print("✅ Flask routes test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Flask routes test failed: {e}")
        return False

def main():
    """Run all deployment fix tests."""
    print("🚀 Testing XMRT Ecosystem Deployment Fixes")
    print("=" * 50)
    
    tests = [
        test_database_schema,
        test_github_auth,
        test_flask_routes
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All deployment fixes are working correctly!")
        print("🚀 Ready for production deployment on Render!")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())