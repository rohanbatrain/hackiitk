"""
Test suite for PipelineFaultInjector

This module tests the PipelineFaultInjector class to ensure all pipeline
fault injection functionality works correctly.
"""

import pytest
import logging
from pathlib import Path
import tempfile

from tests.extreme.engines.pipeline_fault_injector import PipelineFaultInjector
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
            categories=['pipeline_fault_injection'],
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
def pipeline_fault_injector(test_config, fault_injector, metrics_collector, test_data_generator):
    """Create pipeline fault injector."""
    return PipelineFaultInjector(
        config=test_config,
        fault_injector=fault_injector,
        metrics_collector=metrics_collector,
        test_data_generator=test_data_generator,
        logger=logging.getLogger(__name__)
    )


def test_pipeline_fault_injector_initialization(pipeline_fault_injector):
    """Test PipelineFaultInjector initialization."""
    assert pipeline_fault_injector is not None
    assert pipeline_fault_injector.fault_injector is not None
    assert pipeline_fault_injector.metrics_collector is not None
    assert pipeline_fault_injector.test_data_generator is not None
    assert len(pipeline_fault_injector.PIPELINE_STAGES) >= 10


def test_single_stage_failures(pipeline_fault_injector):
    """Test single stage failures."""
    results = pipeline_fault_injector.test_single_stage_failures()
    
    # Should have results for each pipeline stage
    assert len(results) >= 10
    assert all(r.category == "pipeline_fault_injection" for r in results)
    assert all(r.status in [TestStatus.PASS, TestStatus.SKIP, TestStatus.FAIL] for r in results)


def test_multiple_simultaneous_failures(pipeline_fault_injector):
    """Test multiple simultaneous failures."""
    results = pipeline_fault_injector.test_multiple_simultaneous_failures()
    
    assert len(results) > 0
    assert all(r.category == "pipeline_fault_injection" for r in results)
    assert all(r.status in [TestStatus.PASS, TestStatus.SKIP, TestStatus.FAIL] for r in results)


def test_error_logging_validation(pipeline_fault_injector):
    """Test error logging validation."""
    results = pipeline_fault_injector.test_error_logging_validation()
    
    assert len(results) > 0
    assert all(r.category == "pipeline_fault_injection" for r in results)


def test_cleanup_validation(pipeline_fault_injector):
    """Test cleanup validation."""
    results = pipeline_fault_injector.test_cleanup_validation()
    
    assert len(results) > 0
    assert all(r.category == "pipeline_fault_injection" for r in results)


def test_actionable_error_messages(pipeline_fault_injector):
    """Test actionable error messages."""
    results = pipeline_fault_injector.test_actionable_error_messages()
    
    assert len(results) > 0
    assert all(r.category == "pipeline_fault_injection" for r in results)


def test_run_all_tests(pipeline_fault_injector):
    """Test running all pipeline fault injection tests."""
    results = pipeline_fault_injector.run_tests()
    
    # Should have results from all test categories
    assert len(results) > 0
    assert all(r.category == "pipeline_fault_injection" for r in results)
    
    # Count tests by requirement
    requirement_counts = {}
    for result in results:
        for req_id in result.requirement_id.split(','):
            requirement_counts[req_id] = requirement_counts.get(req_id, 0) + 1
    
    # Verify we have tests for key requirements
    assert '63.1' in requirement_counts  # Single stage failures
    assert '63.2' in requirement_counts  # Error logging
    assert '63.3' in requirement_counts  # Cleanup
    assert '63.4' in requirement_counts  # Multiple failures
    assert '63.5' in requirement_counts  # Actionable errors


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
