"""
Pytest configuration and shared fixtures.
"""

import pytest
from pathlib import Path


@pytest.fixture
def test_data_dir():
    """Return path to test data directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_config():
    """Return sample configuration dictionary."""
    return {
        "chunking": {
            "chunk_size": 512,
            "overlap": 50
        },
        "retrieval": {
            "top_k": 5,
            "rerank_top_k": 3
        },
        "llm": {
            "temperature": 0.1,
            "max_tokens": 512,
            "model_name": "qwen2.5-3b-instruct",
            "backend": "ollama"
        },
        "analysis": {
            "covered_threshold": 0.8,
            "partial_threshold": 0.5,
            "ambiguous_threshold": 0.3
        }
    }


@pytest.fixture
def sample_policy_text():
    """Return sample policy text for testing."""
    return """
    Information Security Policy
    
    1. Purpose
    This policy establishes the framework for protecting organizational information assets.
    
    2. Scope
    This policy applies to all employees, contractors, and third parties.
    
    3. Risk Management
    The organization shall conduct regular risk assessments to identify threats.
    """
