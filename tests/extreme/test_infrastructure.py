"""
Test Infrastructure Validation

This module contains tests to verify the extreme testing framework
infrastructure is properly set up and functional.
"""

import pytest
from pathlib import Path

from .config import TestConfig, DEFAULT_CONFIG
from .models import (
    TestResult, TestStatus, Metrics, BreakingPoint, FailureCategory,
    OracleTestCase, ValidationResult, TestReport, CategoryReport
)
from .base import BaseTestEngine, TestIsolation, TestDataHelper
from .runner import MasterTestRunner
from .reporter import ExtremeTestReporter


class TestConfiguration:
    """Test configuration management."""
    
    def test_default_config_creation(self):
        """Test that default configuration can be created."""
        config = TestConfig()
        assert config is not None
        assert len(config.categories) > 0
        assert config.concurrency > 0
        assert config.timeout_seconds > 0
    
    def test_config_from_dict(self):
        """Test configuration creation from dictionary."""
        config_dict = {
            'categories': ['stress', 'chaos'],
            'concurrency': 8,
            'verbose': True
        }
        config = TestConfig.from_dict(config_dict)
        assert config.categories == ['stress', 'chaos']
        assert config.concurrency == 8
        assert config.verbose is True
    
    def test_config_to_dict(self):
        """Test configuration conversion to dictionary."""
        config = TestConfig(categories=['stress'], concurrency=4)
        config_dict = config.to_dict()
        assert isinstance(config_dict, dict)
        assert config_dict['categories'] == ['stress']
        assert config_dict['concurrency'] == 4
    
    def test_config_creates_directories(self):
        """Test that configuration creates required directories."""
        import tempfile
        import shutil
        
        temp_dir = Path(tempfile.mkdtemp())
        try:
            config = TestConfig(
                output_dir=str(temp_dir / "output"),
                baseline_dir=str(temp_dir / "baseline"),
                oracle_dir=str(temp_dir / "oracle"),
                test_data_dir=str(temp_dir / "test_data")
            )
            
            assert Path(config.output_dir).exists()
            assert Path(config.baseline_dir).exists()
            assert Path(config.oracle_dir).exists()
            assert Path(config.test_data_dir).exists()
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestModels:
    """Test data models."""
    
    def test_metrics_creation(self):
        """Test Metrics model creation."""
        metrics = Metrics(
            duration_seconds=10.5,
            memory_peak_mb=512.0,
            memory_average_mb=256.0,
            cpu_peak_percent=80.0,
            cpu_average_percent=50.0,
            disk_read_mb=100.0,
            disk_write_mb=50.0,
            file_handles_peak=10,
            thread_count_peak=5
        )
        assert metrics.duration_seconds == 10.5
        assert metrics.memory_peak_mb == 512.0
    
    def test_metrics_to_dict(self):
        """Test Metrics conversion to dictionary."""
        metrics = Metrics(
            duration_seconds=10.5,
            memory_peak_mb=512.0,
            memory_average_mb=256.0,
            cpu_peak_percent=80.0,
            cpu_average_percent=50.0,
            disk_read_mb=100.0,
            disk_write_mb=50.0,
            file_handles_peak=10,
            thread_count_peak=5
        )
        metrics_dict = metrics.to_dict()
        assert isinstance(metrics_dict, dict)
        assert metrics_dict['duration_seconds'] == 10.5
    
    def test_test_result_creation(self):
        """Test TestResult model creation."""
        result = TestResult(
            test_id="test_001",
            requirement_id="1.1",
            category="stress",
            status=TestStatus.PASS,
            duration_seconds=5.0
        )
        assert result.test_id == "test_001"
        assert result.status == TestStatus.PASS
    
    def test_breaking_point_creation(self):
        """Test BreakingPoint model creation."""
        bp = BreakingPoint(
            dimension="document_size",
            maximum_viable_value=100,
            failure_mode=FailureCategory.TIMEOUT,
            error_message="Test timeout"
        )
        assert bp.dimension == "document_size"
        assert bp.failure_mode == FailureCategory.TIMEOUT


class TestBaseClasses:
    """Test base classes and utilities."""
    
    def test_test_isolation_temporary_directory(self):
        """Test temporary directory creation and cleanup."""
        with TestIsolation.temporary_directory() as temp_dir:
            assert temp_dir.exists()
            test_file = temp_dir / "test.txt"
            test_file.write_text("test")
            assert test_file.exists()
        
        # Directory should be cleaned up
        assert not temp_dir.exists()
    
    def test_test_data_helper_generate_text(self):
        """Test text generation."""
        text = TestDataHelper.generate_text(100, "test")
        words = text.split()
        assert len(words) == 100
        assert all(word.startswith("test") for word in words)
    
    def test_test_data_helper_generate_policy_text(self):
        """Test policy text generation."""
        policy_text = TestDataHelper.generate_policy_text(
            sections=5,
            words_per_section=50,
            include_csf_keywords=True
        )
        assert len(policy_text) > 0
        assert "Section" in policy_text
        assert "##" in policy_text


class TestRunner:
    """Test master test runner."""
    
    def test_runner_creation(self):
        """Test runner can be created."""
        config = TestConfig(categories=['stress'])
        runner = MasterTestRunner(config)
        assert runner is not None
        assert runner.config == config
    
    def test_runner_initialize_engines(self):
        """Test engine initialization."""
        config = TestConfig(categories=['stress', 'chaos'])
        runner = MasterTestRunner(config)
        runner.initialize_engines()
        # Should not raise any errors


class InfrastructureTestReporter:
    """Test report generation."""
    
    def test_reporter_creation(self):
        """Test reporter can be created."""
        import tempfile
        temp_dir = tempfile.mkdtemp()
        reporter = ExtremeTestReporter(temp_dir)
        assert reporter is not None
        assert Path(reporter.output_dir).exists()
    
    def test_report_generation(self):
        """Test report generation."""
        import tempfile
        import shutil
        from datetime import datetime
        
        temp_dir = Path(tempfile.mkdtemp())
        try:
            reporter = ExtremeTestReporter(str(temp_dir))
            
            # Create a simple test report
            report = TestReport(
                execution_date=datetime.now(),
                total_tests=10,
                passed=8,
                failed=2,
                skipped=0,
                errors=0,
                duration_seconds=60.0,
                artifacts_dir=str(temp_dir)
            )
            
            report_files = reporter.generate_report(report)
            
            assert 'json' in report_files
            assert 'html' in report_files
            assert 'junit_xml' in report_files
            
            # Verify files exist
            assert Path(report_files['json']).exists()
            assert Path(report_files['html']).exists()
            assert Path(report_files['junit_xml']).exists()
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
