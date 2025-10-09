# Test Configuration for XMRT Ecosystem

import pytest
import os
from unittest.mock import MagicMock, patch
from github import Github

@pytest.fixture
def mock_github():
    """Mock GitHub client for testing"""
    with patch('github.Github') as mock:
        mock_repo = MagicMock()
        mock_repo.full_name = "DevGruGold/XMRT-Ecosystem"
        mock_repo.stargazers_count = 7
        mock_repo.open_issues_count = 572
        
        mock_client = MagicMock()
        mock_client.get_repo.return_value = mock_repo
        mock.return_value = mock_client
        
        yield mock_client

@pytest.fixture
def mock_openai():
    """Mock OpenAI client for testing"""
    with patch('openai.OpenAI') as mock:
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Test AI response"
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock.return_value = mock_client
        
        yield mock_client

@pytest.fixture
def app_config():
    """Test application configuration"""
    os.environ.update({
        'GITHUB_TOKEN': 'test_token',
        'GITHUB_OWNER': 'TestOwner',
        'GITHUB_REPO': 'TestRepo',
        'API_KEYS': 'test_key_1,test_key_2',
        'LOG_LEVEL': 'DEBUG',
        'TESTING': 'true'
    })
    
    from app.config import AppConfig
    return AppConfig.from_env()

class TestHelpers:
    """Helper functions for testing"""
    
    @staticmethod
    def create_mock_idea(title="Test Idea", impact=4, complexity=2):
        return {
            "title": title,
            "description": "Test description",
            "rationale": "Test rationale",
            "impact": impact,
            "complexity": complexity,
            "tags": ["test", "mock"]
        }
    
    @staticmethod
    def create_mock_agent_review(agent_id="test_agent", score=7.5):
        return {
            "agent_id": agent_id,
            "title": "Test Idea",
            "comment": "Test comment",
            "score": score
        }
