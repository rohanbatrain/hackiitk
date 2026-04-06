"""
Unit tests for Master Test Runner
"""

import pytest
import tempfile
from pathlib import Path

from tests.extreme.runner import MasterTestRunner
from tests.extreme.config import TestConfig
from tests.extreme.models import TestStatus


def test_master_runner_initialization():
    """Test that MasterTestRunner initializes correctly."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config = TestConfig(
            categories=['stress'],
            requirements=[],
            concurrency=1,
            timeout_seconds=300,
            output_dir=temp_dir,
            baseline_dir=str(Path(temp_dir) / "baselines"),
            oracle_dir="tests/extreme/oracles",
            test_data_dir=str(Path(temp_dir) / "test_data"),
            verbose=False,
            fail_fast=False
        )
        
        runner = MasterTestRunner(config)
        
        assert runner.config == config
        assert runner.logger is not None
        assert runner.test_engines == {}
        assert runner.results == []
        assert runner._interrupted == False


def test_master_runner_category_execution_order():
    """Test that categories are executed in correct dependency order."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config = TestConfig(
            categories=['property', 'stress', 'boundary', 'chaos'],
            requirements=[],
            concurrency=1,
            timeout_seconds=300,
            output_dir=temp_dir,
            baseline_dir=str(Path(temp_dir) / "baselines"),
            oracle_dir="tests/extreme/oracles",
            test_data_dir=str(Path(temp_dir) / "test_data"),
            verbose=False,
            fail_fast=False
        )
        
        runner = MasterTestRunner(config)
        order = runner._get_category_execution_order()
        
        # Should be in dependency order
        assert order == ['stress', 'chaos', 'boundary', 'property']


def test_master_runner_cleanup_resources():
    """Test that resources are cleaned up properly."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config = TestConfig(
            categories=[],
            requirements=[],
            concurrency=1,
            timeout_seconds=300,
            output_dir=temp_dir,
            baseline_dir=str(Path(temp_dir) / "baselines"),
            oracle_dir="tests/extreme/oracles",
            test_data_dir=str(Path(temp_dir) / "test_data"),
            verbose=False,
            fail_fast=False
        )
        
        runner = MasterTestRunner(config)
        
        # Create some temporary directories
        temp_dir1 = Path(tempfile.mkdtemp(prefix="test_"))
        temp_dir2 = Path(tempfile.mkdtemp(prefix="test_"))
        runner._temp_dirs = [temp_dir1, temp_dir2]
        
        # Cleanup
        runner._cleanup_resources()
        
        # Verify cleanup
        assert not temp_dir1.exists()
        assert not temp_dir2.exists()
        assert runner._temp_dirs == []


def test_master_runner_test_isolation():
    """Test that test isolation context manager works."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config = TestConfig(
            categories=[],
            requirements=[],
            concurrency=1,
            timeout_seconds=300,
            output_dir=temp_dir,
            baseline_dir=str(Path(temp_dir) / "baselines"),
            oracle_dir="tests/extreme/oracles",
            test_data_dir=str(Path(temp_dir) / "test_data"),
            verbose=False,
            fail_fast=False
        )
        
        runner = MasterTestRunner(config)
        
        # Use test isolation
        with runner._test_isolation("test_123") as isolated_dir:
            assert isolated_dir.exists()
            assert "test_123" in str(isolated_dir)
            temp_path = isolated_dir
        
        # After context, directory should be cleaned up
        assert not temp_path.exists()


def test_master_runner_collect_breaking_points():
    """Test that breaking points are collected from engines."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config = TestConfig(
            categories=[],
            requirements=[],
            concurrency=1,
            timeout_seconds=300,
            output_dir=temp_dir,
            baseline_dir=str(Path(temp_dir) / "baselines"),
            oracle_dir="tests/extreme/oracles",
            test_data_dir=str(Path(temp_dir) / "test_data"),
            verbose=False,
            fail_fast=False
        )
        
        runner = MasterTestRunner(config)
        
        # Mock engine with breaking points
        from tests.extreme.models import BreakingPoint, FailureCategory
        from datetime import datetime
        
        class MockEngine:
            def __init__(self):
                self.breaking_points = [
                    BreakingPoint(
                        dimension="document_size",
                        maximum_viable_value=100,
                        failure_mode=FailureCategory.TIMEOUT,
                        error_message="Test error"
                    )
                ]
        
        runner.test_engines['mock'] = MockEngine()
        
        breaking_points = runner._collect_breaking_points()
        
        assert len(breaking_points) == 1
        assert breaking_points[0].dimension == "document_size"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
