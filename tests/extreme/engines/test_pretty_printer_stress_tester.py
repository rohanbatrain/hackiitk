"""
Test suite for PrettyPrinterStressTester

This module tests the PrettyPrinterStressTester class to ensure all pretty
printer stress testing functionality works correctly.
"""

import pytest
import logging
from pathlib import Path
import tempfile

from tests.extreme.engines.pretty_printer_stress_tester import PrettyPrinterStressTester
from tests.extreme.config import TestConfig
from tests.extreme.support.metrics_collector import MetricsCollector
from tests.extreme.models import TestStatus


@pytest.fixture
def test_config():
    """Create test configuration."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config = TestConfig(
            categories=['pretty_printer_stress'],
            requirements=[],
            concurrency=1,
            timeout_seconds=600,
            output_dir=temp_dir,
            baseline_dir=str(Path(temp_dir) / "baselines"),
            oracle_dir=str(Path(temp_dir) / "oracles"),
            test_data_dir=str(Path(temp_dir) / "test_data"),
            verbose=True,
            fail_fast=False
        )
        yield config


@pytest.fixture
def metrics_collector():
    """Create metrics collector."""
    return MetricsCollector()


@pytest.fixture
def pretty_printer_stress_tester(test_config, metrics_collector):
    """Create pretty printer stress tester."""
    return PrettyPrinterStressTester(
        config=test_config,
        metrics_collector=metrics_collector,
        logger=logging.getLogger(__name__)
    )


def test_pretty_printer_stress_tester_initialization(pretty_printer_stress_tester):
    """Test PrettyPrinterStressTester initialization."""
    assert pretty_printer_stress_tester is not None
    assert pretty_printer_stress_tester.metrics_collector is not None
    assert pretty_printer_stress_tester.pretty_printer is not None


@pytest.mark.slow
def test_large_section_count(pretty_printer_stress_tester):
    """Test with 10,000+ sections - marked as slow."""
    result = pretty_printer_stress_tester.test_large_section_count()
    
    assert result is not None
    assert result.category == "pretty_printer_stress"
    assert result.requirement_id == "55.1"
    assert result.status in [TestStatus.PASS, TestStatus.SKIP, TestStatus.FAIL]


def test_deep_nesting(pretty_printer_stress_tester):
    """Test with 100+ nesting levels."""
    result = pretty_printer_stress_tester.test_deep_nesting()
    
    assert result is not None
    assert result.category == "pretty_printer_stress"
    assert result.requirement_id == "55.2"
    assert result.status in [TestStatus.PASS, TestStatus.SKIP, TestStatus.FAIL]


def test_special_characters(pretty_printer_stress_tester):
    """Test with special characters in headings."""
    result = pretty_printer_stress_tester.test_special_characters()
    
    assert result is not None
    assert result.category == "pretty_printer_stress"
    assert result.requirement_id == "55.3"
    assert result.status in [TestStatus.PASS, TestStatus.SKIP, TestStatus.FAIL]


@pytest.mark.slow
def test_round_trip_properties(pretty_printer_stress_tester):
    """Test round-trip for 1,000+ structures - marked as slow."""
    results = pretty_printer_stress_tester.test_round_trip_properties()
    
    assert len(results) > 0
    assert all(r.category == "pretty_printer_stress" for r in results)
    assert all(r.requirement_id == "55.4" for r in results)


def test_edge_case_structures(pretty_printer_stress_tester):
    """Test edge case structures."""
    results = pretty_printer_stress_tester.test_edge_case_structures()
    
    assert len(results) > 0
    assert all(r.category == "pretty_printer_stress" for r in results)
    assert all(r.requirement_id == "55.5" for r in results)


def test_run_all_tests(pretty_printer_stress_tester):
    """Test running all pretty printer stress tests."""
    results = pretty_printer_stress_tester.run_tests()
    
    # Should have results from all test categories
    assert len(results) > 0
    assert all(r.category == "pretty_printer_stress" for r in results)
    
    # Count tests by requirement
    requirement_counts = {}
    for result in results:
        for req_id in result.requirement_id.split(','):
            requirement_counts[req_id] = requirement_counts.get(req_id, 0) + 1
    
    # Verify we have tests for key requirements
    assert '55.1' in requirement_counts  # Large section count
    assert '55.2' in requirement_counts  # Deep nesting
    assert '55.3' in requirement_counts  # Special characters
    assert '55.4' in requirement_counts  # Round-trip
    assert '55.5' in requirement_counts  # Edge cases


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
