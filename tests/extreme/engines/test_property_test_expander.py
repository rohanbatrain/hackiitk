"""
Unit Tests for Property Test Expander

Tests the PropertyTestExpander class and its methods.
"""

import pytest
import tempfile
import json
from pathlib import Path

from tests.extreme.engines.property_test_expander import PropertyTestExpander
from tests.extreme.config import TestConfig
from tests.extreme.models import TestStatus
from tests.extreme.support.oracle_validator import OracleValidator


@pytest.fixture
def test_config():
    """Create test configuration."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = TestConfig(
            categories=["property"],
            requirements=[],
            concurrency=1,
            timeout_seconds=300,
            output_dir=tmpdir,
            baseline_dir=str(Path(tmpdir) / "baselines"),
            oracle_dir=str(Path(tmpdir) / "oracles"),
            test_data_dir=str(Path(tmpdir) / "test_data"),
            verbose=False,
            fail_fast=False
        )
        yield config


@pytest.fixture
def property_expander(test_config):
    """Create PropertyTestExpander instance."""
    return PropertyTestExpander(test_config)


def test_property_expander_initialization(property_expander):
    """Test PropertyTestExpander initialization."""
    assert property_expander is not None
    assert property_expander.failing_examples_dir.exists()
    assert property_expander.example_db_path.exists()


def test_expand_existing_properties(property_expander):
    """Test expanding existing properties with 10x multiplier."""
    result = property_expander.expand_existing_properties(multiplier=10)
    
    assert result is not None
    assert result.test_id == "property_expansion"
    assert result.requirement_id == "17.1,17.2"
    assert result.category == "property"
    assert result.status == TestStatus.PASS
    assert result.duration_seconds < 300  # Should complete within 5 minutes


def test_invariant_testing(property_expander):
    """Test system invariant testing."""
    result = property_expander.test_invariants()
    
    assert result is not None
    assert result.test_id == "invariant_testing"
    assert result.requirement_id == "17.3,70.1,70.2,70.3,70.4,70.5,70.6"
    assert result.category == "property"
    assert result.status == TestStatus.PASS
    
    # Verify results file was created
    results_file = property_expander.failing_examples_dir / "invariant_results.json"
    assert results_file.exists()
    
    # Verify results content
    with open(results_file) as f:
        results = json.load(f)
    
    assert len(results) == 4  # 4 invariants tested
    assert all("invariant" in r for r in results)
    assert all("passed" in r for r in results)


def test_round_trip_properties(property_expander):
    """Test round-trip property testing."""
    result = property_expander.test_round_trip_properties()
    
    assert result is not None
    assert result.test_id == "round_trip_properties"
    assert result.requirement_id == "17.4"
    assert result.category == "property"
    assert result.status == TestStatus.PASS
    
    # Verify results file was created
    results_file = property_expander.failing_examples_dir / "round_trip_results.json"
    assert results_file.exists()


def test_metamorphic_properties(property_expander):
    """Test metamorphic property testing."""
    result = property_expander.test_metamorphic_properties()
    
    assert result is not None
    assert result.test_id == "metamorphic_properties"
    assert result.requirement_id == "18.1,18.2,18.3,18.4,18.5,18.6"
    assert result.category == "property"
    assert result.status == TestStatus.PASS
    
    # Verify results file was created
    results_file = property_expander.failing_examples_dir / "metamorphic_results.json"
    assert results_file.exists()
    
    # Verify results content
    with open(results_file) as f:
        results = json.load(f)
    
    assert len(results) == 5  # 5 metamorphic properties tested
    assert all("property" in r for r in results)
    assert all("passed" in r for r in results)


def test_save_failing_examples(property_expander):
    """Test saving failing examples."""
    property_name = "test_property"
    examples = [
        {"input": 1, "expected": 2, "actual": 3},
        {"input": 5, "expected": 10, "actual": 15}
    ]
    
    property_expander.save_failing_examples(property_name, examples)
    
    # Verify file was created
    examples_file = property_expander.failing_examples_dir / f"{property_name}_failures.json"
    assert examples_file.exists()
    
    # Verify content
    with open(examples_file) as f:
        data = json.load(f)
    
    assert data["property"] == property_name
    assert len(data["examples"]) == 2
    assert "timestamp" in data


def test_chunk_count_preservation_invariant(property_expander):
    """Test chunk count preservation invariant."""
    result = property_expander._test_chunk_count_preservation()
    
    assert result["invariant"] == "chunk_count_preservation"
    assert result["passed"] is True
    assert result["test_cases"] == 3


def test_gap_coverage_completeness_invariant(property_expander):
    """Test gap coverage completeness invariant."""
    result = property_expander._test_gap_coverage_completeness()
    
    assert result["invariant"] == "gap_coverage_completeness"
    assert result["passed"] is True
    assert result["test_cases"] == 3


def test_audit_log_consistency_invariant(property_expander):
    """Test audit log consistency invariant."""
    result = property_expander._test_audit_log_consistency()
    
    assert result["invariant"] == "audit_log_consistency"
    assert result["passed"] is True
    assert result["test_cases"] == 3


def test_output_file_determinism_invariant(property_expander):
    """Test output file determinism invariant."""
    result = property_expander._test_output_file_determinism()
    
    assert result["invariant"] == "output_file_determinism"
    assert result["passed"] is True
    assert result["test_cases"] == 3


def test_document_extension_property(property_expander):
    """Test document extension metamorphic property."""
    result = property_expander._test_document_extension_property()
    
    assert result["property"] == "document_extension"
    assert result["passed"] is True
    assert result["test_cases"] == 3


def test_document_reduction_property(property_expander):
    """Test document reduction metamorphic property."""
    result = property_expander._test_document_reduction_property()
    
    assert result["property"] == "document_reduction"
    assert result["passed"] is True
    assert result["test_cases"] == 3


def test_formatting_invariance_property(property_expander):
    """Test formatting invariance metamorphic property."""
    result = property_expander._test_formatting_invariance_property()
    
    assert result["property"] == "formatting_invariance"
    assert result["passed"] is True
    assert result["test_cases"] == 3


def test_determinism_property(property_expander):
    """Test determinism metamorphic property."""
    result = property_expander._test_determinism_property()
    
    assert result["property"] == "determinism"
    assert result["passed"] is True
    assert result["test_cases"] == 3


def test_keyword_addition_property(property_expander):
    """Test keyword addition metamorphic property."""
    result = property_expander._test_keyword_addition_property()
    
    assert result["property"] == "keyword_addition"
    assert result["passed"] is True
    assert result["test_cases"] == 3


def test_run_all_tests(property_expander):
    """Test running all property tests."""
    results = property_expander.run_tests()
    
    assert len(results) == 4  # 4 test categories
    assert all(r.category == "property" for r in results)
    assert all(r.status in [TestStatus.PASS, TestStatus.FAIL] for r in results)


def test_property_expander_with_oracle_validator(test_config):
    """Test PropertyTestExpander with oracle validator."""
    # Create oracle validator
    oracle_validator = OracleValidator(test_config.oracle_dir)
    
    # Create property expander with oracle validator
    expander = PropertyTestExpander(test_config, oracle_validator)
    
    assert expander.oracle_validator is not None
    assert expander.oracle_validator == oracle_validator


def test_completion_within_time_limit(property_expander):
    """Test that property tests complete within 5 minutes."""
    import time
    
    start_time = time.time()
    results = property_expander.run_tests()
    duration = time.time() - start_time
    
    # Should complete within 5 minutes (300 seconds)
    assert duration < 300, f"Property tests took {duration:.1f}s (>5 minutes)"
    
    # Verify all tests completed
    assert len(results) == 4
    assert all(r.duration_seconds < 300 for r in results)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
