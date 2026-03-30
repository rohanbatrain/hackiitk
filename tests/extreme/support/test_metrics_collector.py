"""
Unit Tests for MetricsCollector

Tests the MetricsCollector class for resource monitoring functionality.
"""

import pytest
import time
import psutil
from tests.extreme.support.metrics_collector import (
    MetricsCollector, 
    DiskIOMetrics, 
    ResourceLeak
)
from tests.extreme.models import Metrics


class TestMetricsCollector:
    """Test suite for MetricsCollector class."""
    
    def test_initialization(self):
        """Test MetricsCollector initialization."""
        collector = MetricsCollector()
        assert collector.active_sessions == {}
        assert collector.baselines == {}
        assert isinstance(collector.process, psutil.Process)
    
    def test_collect_memory_usage(self):
        """Test memory usage collection."""
        collector = MetricsCollector()
        memory_mb = collector.collect_memory_usage()
        
        assert isinstance(memory_mb, float)
        assert memory_mb > 0  # Should have some memory usage
        assert memory_mb < 100000  # Sanity check: less than 100GB
    
    def test_collect_cpu_usage(self):
        """Test CPU usage collection."""
        collector = MetricsCollector()
        cpu_percent = collector.collect_cpu_usage()
        
        assert isinstance(cpu_percent, float)
        assert cpu_percent >= 0
        assert cpu_percent <= 100  # CPU percentage should be 0-100
    
    def test_collect_disk_io(self):
        """Test disk I/O metrics collection."""
        collector = MetricsCollector()
        disk_io = collector.collect_disk_io()
        
        assert isinstance(disk_io, DiskIOMetrics)
        assert disk_io.read_mb >= 0
        assert disk_io.write_mb >= 0
        assert disk_io.read_count >= 0
        assert disk_io.write_count >= 0
    
    def test_start_collection(self):
        """Test starting metrics collection."""
        collector = MetricsCollector()
        test_id = "test_001"
        
        collector.start_collection(test_id)
        
        assert test_id in collector.active_sessions
        session = collector.active_sessions[test_id]
        assert session.test_id == test_id
        assert session.start_time > 0
        assert session.start_memory_mb > 0
        assert len(session.memory_samples) == 1
        assert len(session.cpu_samples) == 1
    
    def test_start_collection_duplicate_raises_error(self):
        """Test that starting collection twice for same test_id raises error."""
        collector = MetricsCollector()
        test_id = "test_001"
        
        collector.start_collection(test_id)
        
        with pytest.raises(ValueError, match="Collection already active"):
            collector.start_collection(test_id)
    
    def test_stop_collection(self):
        """Test stopping metrics collection."""
        collector = MetricsCollector()
        test_id = "test_002"
        
        collector.start_collection(test_id)
        
        # Do some work to generate metrics
        time.sleep(0.1)
        _ = [i ** 2 for i in range(1000)]
        
        metrics = collector.stop_collection(test_id)
        
        assert isinstance(metrics, Metrics)
        assert metrics.duration_seconds > 0
        assert metrics.memory_peak_mb > 0
        assert metrics.memory_average_mb > 0
        assert metrics.cpu_peak_percent >= 0
        assert metrics.cpu_average_percent >= 0
        assert test_id not in collector.active_sessions
    
    def test_stop_collection_without_start_raises_error(self):
        """Test that stopping collection without starting raises error."""
        collector = MetricsCollector()
        test_id = "test_003"
        
        with pytest.raises(ValueError, match="No active collection"):
            collector.stop_collection(test_id)
    
    def test_metrics_collection_tracks_duration(self):
        """Test that metrics collection accurately tracks duration."""
        collector = MetricsCollector()
        test_id = "test_004"
        
        collector.start_collection(test_id)
        time.sleep(0.2)  # Sleep for 200ms
        metrics = collector.stop_collection(test_id)
        
        # Duration should be approximately 0.2 seconds (with some tolerance)
        assert 0.15 <= metrics.duration_seconds <= 0.3
    
    def test_store_and_retrieve_baseline(self):
        """Test storing and retrieving baseline metrics."""
        collector = MetricsCollector()
        baseline_name = "baseline_001"
        
        # Create sample metrics
        baseline_metrics = Metrics(
            duration_seconds=10.0,
            memory_peak_mb=100.0,
            memory_average_mb=90.0,
            cpu_peak_percent=50.0,
            cpu_average_percent=40.0,
            disk_read_mb=10.0,
            disk_write_mb=5.0,
            file_handles_peak=20,
            thread_count_peak=5
        )
        
        collector.store_baseline(baseline_name, baseline_metrics)
        
        retrieved = collector.get_baseline(baseline_name)
        assert retrieved is not None
        assert retrieved.memory_average_mb == 90.0
        assert retrieved.cpu_peak_percent == 50.0
    
    def test_get_baseline_nonexistent_returns_none(self):
        """Test that getting nonexistent baseline returns None."""
        collector = MetricsCollector()
        result = collector.get_baseline("nonexistent")
        assert result is None
    
    def test_detect_memory_leak(self):
        """Test detection of memory leak."""
        collector = MetricsCollector()
        
        baseline = Metrics(
            duration_seconds=10.0,
            memory_peak_mb=100.0,
            memory_average_mb=100.0,
            cpu_peak_percent=50.0,
            cpu_average_percent=40.0,
            disk_read_mb=10.0,
            disk_write_mb=5.0,
            file_handles_peak=20,
            thread_count_peak=5
        )
        
        # Current metrics with 20% memory increase (above 5% threshold)
        current = Metrics(
            duration_seconds=10.0,
            memory_peak_mb=120.0,
            memory_average_mb=120.0,
            cpu_peak_percent=50.0,
            cpu_average_percent=40.0,
            disk_read_mb=10.0,
            disk_write_mb=5.0,
            file_handles_peak=20,
            thread_count_peak=5
        )
        
        leak = collector.detect_resource_leak(baseline, current)
        
        assert leak is not None
        assert leak.resource_type == 'memory'
        assert leak.baseline_value == 100.0
        assert leak.current_value == 120.0
        assert leak.increase_percent == 20.0
    
    def test_detect_file_handle_leak(self):
        """Test detection of file handle leak."""
        collector = MetricsCollector()
        
        baseline = Metrics(
            duration_seconds=10.0,
            memory_peak_mb=100.0,
            memory_average_mb=100.0,
            cpu_peak_percent=50.0,
            cpu_average_percent=40.0,
            disk_read_mb=10.0,
            disk_write_mb=5.0,
            file_handles_peak=20,
            thread_count_peak=5
        )
        
        # Current metrics with 50% file handle increase
        current = Metrics(
            duration_seconds=10.0,
            memory_peak_mb=100.0,
            memory_average_mb=100.0,
            cpu_peak_percent=50.0,
            cpu_average_percent=40.0,
            disk_read_mb=10.0,
            disk_write_mb=5.0,
            file_handles_peak=30,
            thread_count_peak=5
        )
        
        leak = collector.detect_resource_leak(baseline, current)
        
        assert leak is not None
        assert leak.resource_type == 'file_handles'
        assert leak.baseline_value == 20.0
        assert leak.current_value == 30.0
        assert leak.increase_percent == 50.0
    
    def test_detect_thread_leak(self):
        """Test detection of thread leak."""
        collector = MetricsCollector()
        
        baseline = Metrics(
            duration_seconds=10.0,
            memory_peak_mb=100.0,
            memory_average_mb=100.0,
            cpu_peak_percent=50.0,
            cpu_average_percent=40.0,
            disk_read_mb=10.0,
            disk_write_mb=5.0,
            file_handles_peak=20,
            thread_count_peak=10
        )
        
        # Current metrics with 30% thread increase
        current = Metrics(
            duration_seconds=10.0,
            memory_peak_mb=100.0,
            memory_average_mb=100.0,
            cpu_peak_percent=50.0,
            cpu_average_percent=40.0,
            disk_read_mb=10.0,
            disk_write_mb=5.0,
            file_handles_peak=20,
            thread_count_peak=13
        )
        
        leak = collector.detect_resource_leak(baseline, current)
        
        assert leak is not None
        assert leak.resource_type == 'threads'
        assert leak.baseline_value == 10.0
        assert leak.current_value == 13.0
        assert leak.increase_percent == 30.0
    
    def test_no_leak_detected_within_tolerance(self):
        """Test that no leak is detected when increase is within tolerance."""
        collector = MetricsCollector()
        
        baseline = Metrics(
            duration_seconds=10.0,
            memory_peak_mb=100.0,
            memory_average_mb=100.0,
            cpu_peak_percent=50.0,
            cpu_average_percent=40.0,
            disk_read_mb=10.0,
            disk_write_mb=5.0,
            file_handles_peak=20,
            thread_count_peak=5
        )
        
        # Current metrics with only 3% memory increase (below 5% threshold)
        current = Metrics(
            duration_seconds=10.0,
            memory_peak_mb=103.0,
            memory_average_mb=103.0,
            cpu_peak_percent=50.0,
            cpu_average_percent=40.0,
            disk_read_mb=10.0,
            disk_write_mb=5.0,
            file_handles_peak=20,
            thread_count_peak=5
        )
        
        leak = collector.detect_resource_leak(baseline, current)
        
        assert leak is None
    
    def test_custom_tolerance_threshold(self):
        """Test resource leak detection with custom tolerance."""
        collector = MetricsCollector()
        
        baseline = Metrics(
            duration_seconds=10.0,
            memory_peak_mb=100.0,
            memory_average_mb=100.0,
            cpu_peak_percent=50.0,
            cpu_average_percent=40.0,
            disk_read_mb=10.0,
            disk_write_mb=5.0,
            file_handles_peak=20,
            thread_count_peak=5
        )
        
        # 8% increase
        current = Metrics(
            duration_seconds=10.0,
            memory_peak_mb=108.0,
            memory_average_mb=108.0,
            cpu_peak_percent=50.0,
            cpu_average_percent=40.0,
            disk_read_mb=10.0,
            disk_write_mb=5.0,
            file_handles_peak=20,
            thread_count_peak=5
        )
        
        # With 5% tolerance, should detect leak
        leak = collector.detect_resource_leak(baseline, current, tolerance_percent=5.0)
        assert leak is not None
        
        # With 10% tolerance, should not detect leak
        leak = collector.detect_resource_leak(baseline, current, tolerance_percent=10.0)
        assert leak is None
    
    def test_resource_leak_string_representation(self):
        """Test ResourceLeak string representation."""
        leak = ResourceLeak(
            resource_type='memory',
            baseline_value=100.0,
            current_value=120.0,
            increase_percent=20.0,
            threshold_percent=5.0
        )
        
        leak_str = str(leak)
        assert 'memory' in leak_str
        assert '100.00' in leak_str
        assert '120.00' in leak_str
        assert '20.0%' in leak_str
    
    def test_disk_io_metrics_during_collection(self):
        """Test that disk I/O metrics are tracked correctly."""
        collector = MetricsCollector()
        test_id = "test_disk_io"
        
        collector.start_collection(test_id)
        
        # Perform some disk I/O (write to a temp file)
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', delete=True) as f:
            f.write("test data" * 1000)
            f.flush()
        
        metrics = collector.stop_collection(test_id)
        
        # Disk I/O should be tracked (may be 0 on some platforms)
        assert metrics.disk_read_mb >= 0
        assert metrics.disk_write_mb >= 0
    
    def test_multiple_concurrent_collections(self):
        """Test that multiple collections can be active simultaneously."""
        collector = MetricsCollector()
        
        collector.start_collection("test_1")
        collector.start_collection("test_2")
        collector.start_collection("test_3")
        
        assert len(collector.active_sessions) == 3
        
        metrics_1 = collector.stop_collection("test_1")
        assert len(collector.active_sessions) == 2
        
        metrics_2 = collector.stop_collection("test_2")
        assert len(collector.active_sessions) == 1
        
        metrics_3 = collector.stop_collection("test_3")
        assert len(collector.active_sessions) == 0
        
        assert all(isinstance(m, Metrics) for m in [metrics_1, metrics_2, metrics_3])
    
    def test_detect_performance_degradation(self):
        """Test detection of performance degradation."""
        collector = MetricsCollector()
        
        baseline = Metrics(
            duration_seconds=10.0,
            memory_peak_mb=100.0,
            memory_average_mb=100.0,
            cpu_peak_percent=50.0,
            cpu_average_percent=40.0,
            disk_read_mb=10.0,
            disk_write_mb=5.0,
            file_handles_peak=20,
            thread_count_peak=5
        )
        
        # Current metrics with 30% duration increase (above 20% threshold)
        current = Metrics(
            duration_seconds=13.0,
            memory_peak_mb=100.0,
            memory_average_mb=100.0,
            cpu_peak_percent=50.0,
            cpu_average_percent=40.0,
            disk_read_mb=10.0,
            disk_write_mb=5.0,
            file_handles_peak=20,
            thread_count_peak=5
        )
        
        degradation = collector.detect_performance_degradation(baseline, current)
        
        assert degradation is not None
        assert degradation.resource_type == 'performance'
        assert degradation.baseline_value == 10.0
        assert degradation.current_value == 13.0
        assert degradation.increase_percent == 30.0
        assert degradation.threshold_percent == 20.0
    
    def test_no_performance_degradation_within_threshold(self):
        """Test that no degradation is detected when increase is within threshold."""
        collector = MetricsCollector()
        
        baseline = Metrics(
            duration_seconds=10.0,
            memory_peak_mb=100.0,
            memory_average_mb=100.0,
            cpu_peak_percent=50.0,
            cpu_average_percent=40.0,
            disk_read_mb=10.0,
            disk_write_mb=5.0,
            file_handles_peak=20,
            thread_count_peak=5
        )
        
        # Current metrics with only 15% duration increase (below 20% threshold)
        current = Metrics(
            duration_seconds=11.5,
            memory_peak_mb=100.0,
            memory_average_mb=100.0,
            cpu_peak_percent=50.0,
            cpu_average_percent=40.0,
            disk_read_mb=10.0,
            disk_write_mb=5.0,
            file_handles_peak=20,
            thread_count_peak=5
        )
        
        degradation = collector.detect_performance_degradation(baseline, current)
        
        assert degradation is None
    
    def test_custom_performance_degradation_threshold(self):
        """Test performance degradation detection with custom threshold."""
        collector = MetricsCollector()
        
        baseline = Metrics(
            duration_seconds=10.0,
            memory_peak_mb=100.0,
            memory_average_mb=100.0,
            cpu_peak_percent=50.0,
            cpu_average_percent=40.0,
            disk_read_mb=10.0,
            disk_write_mb=5.0,
            file_handles_peak=20,
            thread_count_peak=5
        )
        
        # 15% increase
        current = Metrics(
            duration_seconds=11.5,
            memory_peak_mb=100.0,
            memory_average_mb=100.0,
            cpu_peak_percent=50.0,
            cpu_average_percent=40.0,
            disk_read_mb=10.0,
            disk_write_mb=5.0,
            file_handles_peak=20,
            thread_count_peak=5
        )
        
        # With 20% threshold, should not detect degradation
        degradation = collector.detect_performance_degradation(baseline, current, threshold_percent=20.0)
        assert degradation is None
        
        # With 10% threshold, should detect degradation
        degradation = collector.detect_performance_degradation(baseline, current, threshold_percent=10.0)
        assert degradation is not None
        assert degradation.increase_percent == 15.0
