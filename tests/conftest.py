#!/usr/bin/env python3
"""
pytest configuration and fixtures for SKOS MCP Classifier tests
"""
import pytest
import os
import sys
from unittest.mock import Mock, patch

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def mock_openai_response():
    """
    Mock OpenAI API response with realistic token usage data
    """
    return {
        "id": "chatcmpl-test123",
        "object": "chat.completion",
        "created": 1695465600,
        "model": "gpt-4o-mini-2024-07-18",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": '{"search_text": "yogur natural", "concept_uri": "https://treew.io/taxonomy/concept/111206", "prefLabel": "Yogur y sustitutos", "notation": "111206", "level": 1, "confidence": 1.0}'
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 1796,
            "completion_tokens": 160,
            "total_tokens": 1956
        }
    }

@pytest.fixture
def mock_openai_function_call_response():
    """
    Mock OpenAI API response with function calls (multi-step classification)
    """
    return {
        "id": "chatcmpl-func123",
        "object": "chat.completion",
        "created": 1695465600,
        "model": "gpt-4o-mini-2024-07-18",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": None,
                    "function_call": {
                        "name": "search_concepts",
                        "arguments": '{"search_text": "yogur"}'
                    }
                },
                "finish_reason": "function_call"
            }
        ],
        "usage": {
            "prompt_tokens": 900,
            "completion_tokens": 50,
            "total_tokens": 950
        }
    }

@pytest.fixture
def sample_classification_result():
    """
    Sample classification result with cost information
    """
    return {
        "search_text": "yogur natural griego",
        "concept_uri": "https://treew.io/taxonomy/concept/111206",
        "prefLabel": "Yogur y sustitutos",
        "notation": "111206",
        "level": 1,
        "confidence": 1.0,
        "product_id": "YOGUR001",
        "openai_cost": {
            "model": "gpt-4o-mini-2024-07-18",
            "usage": {
                "prompt_tokens": 1796,
                "completion_tokens": 160,
                "total_tokens": 1956
            },
            "cost_usd": {
                "prompt": 0.000269,
                "completion": 0.000096,
                "total": 0.000365
            },
            "cost_breakdown": {
                "base_model_for_pricing": "gpt-4o-mini",
                "prompt_cost_per_1m_tokens": 0.15,
                "completion_cost_per_1m_tokens": 0.6,
                "calculation_timestamp": "2025-09-23T12:05:16.227619"
            },
            "api_calls": 4
        }
    }

@pytest.fixture
def sample_product_requests():
    """
    Sample product request data for testing
    """
    return [
        {
            "text": "yogur natural griego 150g",
            "product_id": "YOGUR001"
        },
        {
            "text": "leche desnatada 1L",
            "product_id": "LECHE001"
        },
        {
            "text": "pan integral de centeno 500g",
            "product_id": "PAN001"
        }
    ]

@pytest.fixture
def mock_openai_client():
    """
    Mock OpenAI client for testing without making real API calls
    """
    with patch('openai.OpenAI') as mock_openai:
        mock_client = Mock()
        mock_openai.return_value = mock_client
        yield mock_client

@pytest.fixture
def mock_skos_database():
    """
    Mock SKOS database functions for testing classification logic
    """
    with patch('server.main.search_concepts') as mock_search, \
         patch('server.main.get_concept_context') as mock_context:
        
        mock_search.return_value = [
            {
                "concept_uri": "https://treew.io/taxonomy/concept/111206",
                "prefLabel": "Yogur y sustitutos",
                "notation": "111206",
                "level": 1,
                "score": 0.95
            }
        ]
        
        mock_context.return_value = {
            "concept_uri": "https://treew.io/taxonomy/concept/111206",
            "prefLabel": "Yogur y sustitutos",
            "notation": "111206",
            "level": 1,
            "definition": "Productos lácteos fermentados",
            "broader": [],
            "narrower": []
        }
        
        yield {
            "search": mock_search,
            "context": mock_context
        }

@pytest.fixture
def api_client():
    """
    FastAPI test client for API endpoint testing
    """
    from fastapi.testclient import TestClient
    from classification_api import app
    
    return TestClient(app)

# Test environment variables
@pytest.fixture(autouse=True)
def test_environment():
    """
    Set up test environment variables
    """
    original_env = os.environ.copy()
    
    # Set test environment variables
    os.environ["OPENAI_API_KEY"] = "test-api-key"
    os.environ["TESTING"] = "true"
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)

# Custom pytest markers
def pytest_configure(config):
    """
    Configure custom pytest markers
    """
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "api: mark test as an API test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )

# Test data constants
SAMPLE_COSTS = {
    "gpt-4o-mini": {
        "prompt": 0.15,
        "completion": 0.6
    },
    "gpt-4o": {
        "prompt": 5.0,
        "completion": 15.0
    }
}