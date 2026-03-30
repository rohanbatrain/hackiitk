"""
Unit Tests for Performance Profiler

Tests the PerformanceProfiler class that measures performance degradation
curves and identifies bottlenecks.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import json

from tests.extreme.engines.performance_profiler import (
    PerformanceProfiler,
    PerformanceDataPoint,
    PerformanceReport,
    Bottleneck,
    BaselineMetrics
)
from tests.extreme.config import TestConfig
from tests.extreme.support.metrics_collector import MetricsCollector
from tests.extreme.data_generator import TestDataGenerator
from tests.extreme.models import TestStatus, Metrics


def is_chromadb_available():
    """Check if ChromaDB is available and compatible."""
    try:
        import chromadb
        return True
    except Exception:
        return False


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def test_config(temp_dir):
    """Create test configuration."""
    return TestConfig(
        categories=['performance'],
        requirements=[],
        concurrency=1,
        timeout_seconds=300,
        output_dir=str(temp_dir / "output"),
        baseline_dir=str(temp_dir / "baselines"),
        oracle_dir=str(temp_dir / "oracles"),
        test_data_dir=str(temp_dir / "test_data"),
        verbose=True,
        fail_fast=False
    )


@pytest.fixture
def metrics_collector():
    """Create metrics collector."""
    return MetricsCollector()


@pytest.fixture
def test_data_generator(temp_dir):
    """Create test data generator."""
    return TestDataGenerator(cache_dir=temp_dir / "cache")


@pytest.fixture
def performance_profiler(test_config, metrics_collector, test_data_generator):
    """Create performance profiler instance."""
    return PerformanceProfiler(
        config=test_config,
        metrics_collector=metrics_collector,
        test_data_generator=test_data_generator
    )


class TestPerformanceDataPoint:
    """Test PerformanceDataPoint data model."""
    
    def test_create_data_point(self):
        """Test creating a performance data point."""
        dp = PerformanceDataPoint(
            dimension_value="10 pages",
            duration_seconds=5.5,
            memory_peak_mb=150.0,
            memory_average_mb=120.0,
            cpu_peak_percent=80.0,
            cpu_average_percent=60.0
        )
        
        assert dp.dimension_value == "10 pages"
        assert dp.duration_seconds == 5.5
        assert dp.memory_peak_mb == 150.0
    
    def test_to_dict(self):
        """Test converting data point to dictionary."""
        dp = PerformanceDataPoint(
            dimension_value="10 pages",
            duration_seconds=5.5,
            memory_peak_mb=150.0,
            memory_average_mb=120.0,
            cpu_peak_percent=80.0,
            cpu_average_percent=60.0
        )
        
        data = dp.to_dict()
        assert data['dimension_value'] == "10 pages"
        assert data['duration_seconds'] == 5.5
        assert data['memory_peak_mb'] == 150.0


class TestPerformanceReport:
    """Test PerformanceReport data model."""
    
    def test_create_report(self):
        """Test creating a performance report."""
        report = PerformanceReport(
            dimension='document_size',
            data_points=[],
            bottlenecks=[],
            performance_cliff=None
        )
        
        assert report.dimension == 'document_size'
        assert len(report.data_points) == 0
    
    def test_to_dict(self):
        """Test converting report to dictionary."""
        dp = PerformanceDataPoint(
            dimension_value="10 pages",
            duration_seconds=5.5,
            memory_peak_mb=150.0,
            memory_average_mb=120.0,
            cpu_peak_percent=80.0,
            cpu_average_percent=60.0
        )
        
        report = PerformanceReport(
            dimension='document_size',
            data_points=[dp],
            bottlenecks=['stage1'],
            performance_cliff="Cliff detected"
        )
        
        data = report.to_dict()
        assert data['dimension'] == 'document_size'
        assert len(data['data_points']) == 1
        assert data['performance_cliff'] == "Cliff detected"


class TestBottleneck:
    """Test Bottleneck data model."""
    
    def test_create_bottleneck(self):
        """Test creating a bottleneck."""
        bottleneck = Bottleneck(
            stage='llm_inference',
            duration_seconds=20.5,
            percentage_of_total=45.0,
            description='LLM inference is the primary bottleneck'
        )
        
        assert bottleneck.stage == 'llm_inference'
        assert bottleneck.duration_seconds == 20.5
        assert bottleneck.percentage_of_total == 45.0
    
    def test_to_dict(self):
        """Test converting bottleneck to dictionary."""
        bottleneck = Bottleneck(
            stage='llm_inference',
            duration_seconds=20.5,
            percentage_of_total=45.0,
            description='LLM inference is the primary bottleneck'
        )
        
        data = bottleneck.to_dict()
        assert data['stage'] == 'llm_inference'
        assert data['duration_seconds'] == 20.5


class TestBaselineMetrics:
    """Test BaselineMetrics data model."""
    
    def test_create_baseline(self):
        """Test creating baseline metrics."""
        metrics = Metrics(
            duration_seconds=10.0,
            memory_peak_mb=200.0,
            memory_average_mb=150.0,
            cpu_peak_percent=80.0,
            cpu_average_percent=60.0,
            disk_read_mb=10.0,
            disk_write_mb=5.0,
            file_handles_peak=50,
            thread_count_peak=10
        )
        
        baseline = BaselineMetrics(
            name='10-page',
            metrics=metrics,
            timestamp='2024-01-01T00:00:00',
            hardware_info={'cpu_count': 4}
        )
        
        assert baseline.name == '10-page'
        assert baseline.metrics.duration_seconds == 10.0
        assert baseline.hardware_info['cpu_count'] == 4
    
    def test_to_dict(self):
        """Test converting baseline to dictionary."""
        metrics = Metrics(
            duration_seconds=10.0,
            memory_peak_mb=200.0,
            memory_average_mb=150.0,
            cpu_peak_percent=80.0,
            cpu_average_percent=60.0,
            disk_read_mb=10.0,
            disk_write_mb=5.0,
            file_handles_peak=50,
            thread_count_peak=10
        )
        
        baseline = BaselineMetrics(
            name='10-page',
            metrics=metrics,
            timestamp='2024-01-01T00:00:00',
            hardware_info={'cpu_count': 4}
        )
        
        data = baseline.to_dict()
        assert data['name'] == '10-page'
        assert data['timestamp'] == '2024-01-01T00:00:00'
        assert 'metrics' in data


class TestPerformanceProfiler:
    """Test PerformanceProfiler class."""
    
    def test_initialization(self, performance_profiler):
        """Test profiler initialization."""
        assert performance_profiler is not None
        assert len(performance_profiler.performance_reports) == 0
        assert len(performance_profiler.bottlenecks) == 0
        assert len(performance_profiler.baselines) == 0
    
    def test_detect_performance_cliff_no_cliff(self, performance_profiler):
        """Test cliff detection with linear growth."""
        data_points = [
            PerformanceDataPoint("1", 1.0, 100, 90, 50, 40),
            PerformanceDataPoint("2", 2.0, 110, 100, 55, 45),
            PerformanceDataPoint("3", 3.0, 120, 110, 60, 50),
        ]
        
        cliff = performance_profiler._detect_performance_cliff(data_points)
        assert cliff is None
    
    def test_detect_performance_cliff_with_cliff(self, performance_profiler):
        """Test cliff detection with non-linear growth."""
        data_points = [
            PerformanceDataPoint("1", 1.0, 100, 90, 50, 40),
            PerformanceDataPoint("2", 2.0, 110, 100, 55, 45),
            PerformanceDataPoint("3", 10.0, 200, 180, 90, 80),  # Cliff here
        ]
        
        cliff = performance_profiler._detect_performance_cliff(data_points)
        assert cliff is not None
        assert "Performance cliff detected" in cliff
    
    def test_detect_performance_cliff_insufficient_data(self, performance_profiler):
        """Test cliff detection with insufficient data points."""
        data_points = [
            PerformanceDataPoint("1", 1.0, 100, 90, 50, 40),
        ]
        
        cliff = performance_profiler._detect_performance_cliff(data_points)
        assert cliff is None
    
    def test_analyze_pipeline_bottlenecks(self, performance_profiler):
        """Test bottleneck analysis."""
        metrics = Metrics(
            duration_seconds=100.0,
            memory_peak_mb=500.0,
            memory_average_mb=400.0,
            cpu_peak_percent=90.0,
            cpu_average_percent=70.0,
            disk_read_mb=50.0,
            disk_write_mb=25.0,
            file_handles_peak=100,
            thread_count_peak=20
        )
        
        bottlenecks = performance_profiler._analyze_pipeline_bottlenecks(metrics, None)
        
        # Should identify multiple bottlenecks for a 100s execution
        assert len(bottlenecks) > 0
        
        # Check that bottlenecks have required fields
        for bottleneck in bottlenecks:
            assert bottleneck.stage
            assert bottleneck.duration_seconds > 0
            assert bottleneck.percentage_of_total > 0
            assert bottleneck.description
    
    def test_collect_hardware_info(self, performance_profiler):
        """Test hardware info collection."""
        hardware_info = performance_profiler._collect_hardware_info()
        
        assert 'platform' in hardware_info
        assert 'processor' in hardware_info
        assert 'cpu_count' in hardware_info
        assert 'total_memory_gb' in hardware_info
        assert 'python_version' in hardware_info
        
        # Verify values are reasonable
        assert hardware_info['cpu_count'] > 0
        assert hardware_info['total_memory_gb'] > 0
    
    def test_generate_csv_data(self, performance_profiler, temp_dir):
        """Test CSV data generation."""
        data_points = [
            PerformanceDataPoint("10 pages", 5.0, 150, 120, 70, 50),
            PerformanceDataPoint("20 pages", 10.0, 200, 160, 75, 55),
        ]
        
        report = PerformanceReport(
            dimension='document_size',
            data_points=data_points
        )
        
        output_path = temp_dir / "test.csv"
        performance_profiler._generate_csv_data(report, output_path)
        
        assert output_path.exists()
        
        content = output_path.read_text()
        assert 'dimension_value,duration_seconds' in content
        assert '10 pages,5.0' in content
        assert '20 pages,10.0' in content
    
    def test_generate_text_visualization(self, performance_profiler, temp_dir):
        """Test text visualization generation."""
        data_points = [
            PerformanceDataPoint("10 pages", 5.0, 150, 120, 70, 50),
            PerformanceDataPoint("20 pages", 10.0, 200, 160, 75, 55),
        ]
        
        report = PerformanceReport(
            dimension='document_size',
            data_points=data_points,
            performance_cliff="Test cliff"
        )
        
        output_path = temp_dir / "test_viz.txt"
        performance_profiler._generate_text_visualization(report, output_path)
        
        assert output_path.exists()
        
        content = output_path.read_text()
        assert 'Performance Profile: document_size' in content
        assert '10 pages' in content
        assert '20 pages' in content
        assert 'Performance Cliff Detected' in content
    
    def test_generate_performance_comparison_report(self, performance_profiler):
        """Test performance comparison report generation."""
        # Add some test data
        data_points = [
            PerformanceDataPoint("10 pages", 5.0, 150, 120, 70, 50),
            PerformanceDataPoint("20 pages", 10.0, 200, 160, 75, 55),
        ]
        
        report = PerformanceReport(
            dimension='document_size',
            data_points=data_points
        )
        performance_profiler.performance_reports['document_size'] = report
        
        markdown = performance_profiler._generate_performance_comparison_report()
        
        assert '# Performance Comparison Report' in markdown
        assert 'Document Size' in markdown
        assert 'Data points: 2' in markdown
    
    def test_generate_trends_report(self, performance_profiler):
        """Test trends report generation."""
        # Add some test data
        data_points = [
            PerformanceDataPoint("10 pages", 5.0, 150, 120, 70, 50),
            PerformanceDataPoint("20 pages", 10.0, 200, 160, 75, 55),
        ]
        
        report = PerformanceReport(
            dimension='document_size',
            data_points=data_points
        )
        performance_profiler.performance_reports['document_size'] = report
        
        trends = performance_profiler._generate_trends_report()
        
        assert 'timestamp' in trends
        assert 'dimensions' in trends
        assert 'baselines' in trends
        assert 'bottlenecks' in trends
        
        assert 'document_size' in trends['dimensions']
        assert trends['dimensions']['document_size']['data_point_count'] == 2
        assert trends['dimensions']['document_size']['min_duration'] == 5.0
        assert trends['dimensions']['document_size']['max_duration'] == 10.0


class TestPerformanceProfilerIntegration:
    """Integration tests for PerformanceProfiler."""
    
    @pytest.mark.slow
    @pytest.mark.skipif(not is_chromadb_available(), reason="ChromaDB not available")
    def test_profile_document_size_scaling(self, performance_profiler):
        """Test document size scaling profile (integration test)."""
        # This is a slow test that actually runs the profiler
        result = performance_profiler.profile_document_size_scaling()
        
        assert result.status == TestStatus.PASS
        assert result.category == "performance"
        assert len(result.artifacts) > 0
        
        # Check that report was created
        assert 'document_size' in performance_profiler.performance_reports
        report = performance_profiler.performance_reports['document_size']
        assert len(report.data_points) > 0
    
    @pytest.mark.slow
    @pytest.mark.skipif(not is_chromadb_available(), reason="ChromaDB not available")
    def test_identify_bottlenecks(self, performance_profiler):
        """Test bottleneck identification (integration test)."""
        result = performance_profiler.identify_bottlenecks()
        
        assert result.status == TestStatus.PASS
        assert result.category == "performance"
        assert result.metrics is not None
        
        # Check that bottlenecks were identified
        assert len(performance_profiler.bottlenecks) > 0
    
    @pytest.mark.slow
    @pytest.mark.skipif(not is_chromadb_available(), reason="ChromaDB not available")
    def test_establish_baselines(self, performance_profiler):
        """Test baseline establishment (integration test)."""
        result = performance_profiler.establish_baselines()
        
        assert result.status == TestStatus.PASS
        assert result.category == "performance"
        
        # Check that baselines were established
        assert len(performance_profiler.baselines) > 0
        assert '10-page' in performance_profiler.baselines
    
    def test_generate_degradation_graphs(self, performance_profiler):
        """Test degradation graph generation."""
        # Add some test data first
        data_points = [
            PerformanceDataPoint("10 pages", 5.0, 150, 120, 70, 50),
            PerformanceDataPoint("20 pages", 10.0, 200, 160, 75, 55),
        ]
        
        report = PerformanceReport(
            dimension='document_size',
            data_points=data_points
        )
        performance_profiler.performance_reports['document_size'] = report
        
        result = performance_profiler.generate_degradation_graphs()
        
        assert result.status == TestStatus.PASS
        assert result.category == "performance"
        assert len(result.artifacts) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
