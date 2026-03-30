"""
Tests for LLM and Model Stress Tester

Validates the LLM stress testing functionality.
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from tests.extreme.engines.llm_model_stress_tester import (
    LLMModelStressTester,
    LLMModelStressConfig
)
from tests.extreme.support.metrics_collector import MetricsCollector
from tests.extreme.engines.component_stress_tester import TestCategory


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests."""
    temp = tempfile.mkdtemp(prefix="test_llm_stress_")
    yield Path(temp)
    shutil.rmtree(temp, ignore_errors=True)


@pytest.fixture
def metrics_collector():
    """Create metrics collector."""
    return MetricsCollector()


@pytest.fixture
def llm_tester(metrics_collector, temp_dir):
    """Create LLM model stress tester."""
    config = LLMModelStressConfig(
        temp_dir=str(temp_dir),
        max_examples_per_test=3,
        timeout_seconds=300
    )
    return LLMModelStressTester(metrics_collector, config)


def test_llm_tester_initialization(llm_tester):
    """Test LLM tester initializes correctly."""
    assert llm_tester is not None
    assert llm_tester.metrics is not None
    assert llm_tester.config is not None


def test_generate_large_policy(llm_tester):
    """Test large policy generation."""
    policy = llm_tester._generate_large_policy(target_tokens=1000)
    assert len(policy) > 0
    assert len(policy) >= 3000  # Rough estimate: 1000 tokens * 4 chars


def test_generate_conflicting_policy(llm_tester):
    """Test conflicting policy generation."""
    policy = llm_tester._generate_conflicting_policy()
    assert "Ignore all previous instructions" in policy
    assert "SYSTEM:" in policy


def test_generate_standard_policy(llm_tester):
    """Test standard policy generation."""
    policy = llm_tester._generate_standard_policy()
    assert "Access Control" in policy
    assert "Data Protection" in policy
    assert "Incident Response" in policy


def test_validate_schema_valid(llm_tester):
    """Test schema validation with valid data."""
    valid_data = {
        'gaps': [
            {'subcategory_id': 'ID.AM-1', 'severity': 'High'},
            {'subcategory_id': 'ID.AM-2', 'severity': 'Medium'}
        ]
    }
    assert llm_tester._validate_schema(valid_data) is True


def test_validate_schema_invalid(llm_tester):
    """Test schema validation with invalid data."""
    invalid_data = {
        'gaps': 'not a list'
    }
    assert llm_tester._validate_schema(invalid_data) is False


def test_validate_schema_missing_fields(llm_tester):
    """Test schema validation with missing fields."""
    invalid_data = {
        'gaps': [
            {'severity': 'High'}  # Missing subcategory_id
        ]
    }
    assert llm_tester._validate_schema(invalid_data) is False


def test_config_validation():
    """Test configuration validation."""
    # Valid config
    config = LLMModelStressConfig(max_examples_per_test=5, timeout_seconds=120)
    assert config.max_examples_per_test == 5
    
    # Invalid max_examples_per_test
    with pytest.raises(ValueError):
        LLMModelStressConfig(max_examples_per_test=0)
    
    # Invalid timeout
    with pytest.raises(ValueError):
        LLMModelStressConfig(timeout_seconds=30)


def test_run_tests_returns_results(llm_tester):
    """Test that run_tests returns a list of results."""
    # Note: This will attempt to run actual tests
    # In a real environment, you might want to mock the analysis pipeline
    results = llm_tester.run_tests()
    
    assert isinstance(results, list)
    assert len(results) > 0
    
    # Check that all results have required fields
    for result in results:
        assert hasattr(result, 'test_id')
        assert hasattr(result, 'status')
        assert hasattr(result, 'category')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
