"""
Test suite for IntegrationChaosTester

This module tests the IntegrationChaosTester class to ensure all chaos
integration testing functionality works correctly.
"""

import pytest
import logging
from pathlib import Path
import tempfile

from tests.extreme.engines.integration_chaos_tester import IntegrationChaosTester
from tests.extreme.config import TestConfig
from tests.extreme.support.fault_injector import FaultInjector
from tests.extreme.support.metrics_collector import MetricsCollector
from tests.extreme.data_generator import TestDataGenerator
from tests.extreme.models import TestStatus


@pytest.fixture
def test_config():
    """Create test configuration."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config = TestConfig(
            categories=['integration_chaos'],
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
def fault_injector():
    """Create fault injector."""
    return FaultInjector()


@pytest.fixture
def metrics_collector():
    """Create metrics collector."""
    return MetricsCollector()


@pytest.fixture
def test_data_generator(test_config):
    """Create test data generator."""
    return TestDataGenerator(
        cache_dir=Path(test_config.test_data_dir),
        logger=logging.getLogger(__name__)
    )


@pytest.fixture
def integration_chaos_tester(test_config, fault_injector, metrics_collector, test_data_generator):
    """Create integration chaos tester."""
    return IntegrationChaosTester(
        config=test_config,
        fault_injector=fault_injector,
        metrics_collector=metrics_collector,
        test_data_generator=test_data_generator,
        logger=logging.getLogger(__name__)
    )


def test_integration_chaos_tester_initialization(integration_chaos_tester):
    """Test IntegrationChaosTester initialization."""
    assert integration_chaos_tester is not None
    assert integration_chaos_tester.fault_injector is not None
    assert integration_chaos_tester.metrics_collector is not None
    assert integration_chaos_tester.test_data_generator is not None


def test_random_component_failures(integration_chaos_tester):
    """Test random component failures."""
    results = integration_chaos_tester.test_random_component_failures()
    
    assert len(results) > 0
    assert all(r.category == "integration_chaos" for r in results)
    assert all(r.status in [TestStatus.PASS, TestStatus.SKIP, TestStatus.FAIL] for r in results)


def test_random_delays(integration_chaos_tester):
    """Test random delays."""
    results = integration_chaos_tester.test_random_delays()
    
    assert len(results) > 0
    assert all(r.category == "integration_chaos" for r in results)
    assert all(r.status in [TestStatus.PASS, TestStatus.SKIP, TestStatus.FAIL] for r in results)


def test_memory_pressure(integration_chaos_tester):
    """Test memory pressure."""
    results = integration_chaos_tester.test_memory_pressure()
    
    assert len(results) > 0
    assert all(r.category == "integration_chaos" for r in results)
    assert all(r.status in [TestStatus.PASS, TestStatus.SKIP, TestStatus.FAIL] for r in results)


@pytest.mark.slow
def test_combined_chaos(integration_chaos_tester):
    """Test combined chaos (100+ runs) - marked as slow."""
    results = integration_chaos_tester.test_combined_chaos()
    
    # Should have 100+ individual results plus summary
    assert len(results) >= 100
    assert all(r.category == "integration_chaos" for r in results)
    
    # Find summary result
    summary = next((r for r in results if "summary" in r.test_id), None)
    assert summary is not None
    assert "50.4" in summary.requirement_id or "50.5" in summary.requirement_id


def test_run_all_tests(integration_chaos_tester):
    """Test running all integration chaos tests."""
    results = integration_chaos_tester.run_tests()
    
    # Should have results from all test categories
    assert len(results) > 0
    assert all(r.category == "integration_chaos" for r in results)
    
    # Count tests by requirement
    requirement_counts = {}
    for result in results:
        for req_id in result.requirement_id.split(','):
            requirement_counts[req_id] = requirement_counts.get(req_id, 0) + 1
    
    # Verify we have tests for key requirements
    assert '50.1' in requirement_counts  # Random component failures
    assert '50.2' in requirement_counts  # Random delays
    assert '50.3' in requirement_counts  # Memory pressure


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
