"""
Unit Tests for MetricsCollector

Tests metrics collection accuracy, resource leak detection, baseline storage
and comparison, and behavior with known workloads.

**Validates: Task 32.2**
"""

import pytest
import time
from tests.extreme.support.metrics_collector import MetricsCollector, ResourceLeak
from tests.extreme.models import Metrics


class TestMetricsCollector:
    """Unit tests for MetricsCollector component."""
    
    @pytest.fixture
    def collector(self):
        """Create MetricsCollector instance."""
        return MetricsCollector()
    
    # Test metrics collection accuracy
    
    def test_start_collection(self, collector):
        """Test starting metrics collection."""
        test_id = "test_001"
        
        collector.start_collection(test_id)
        
        assert test_id in collector.active_sessions
        session = collector.active_sessions[test_id]
        assert session.test_id == test_id
        assert session.start_time > 0
        assert session.start_memory_mb >= 0
        assert len(session.memory_samples) > 0
    
    def test_start_collection_duplicate_raises_error(self, collector):
        """Test starting collection with duplicate test_id raises error."""
        test_id = "test_duplicate"
        
        collector.start_collection(test_id)
        
        with pytest.raises(ValueError, match="Collection already active"):
            collector.start_collection(test_id)
    
    def test_stop_collection(self, collector):
        """Test stopping metrics collection."""
        test_id = "test_002"
        
        collector.start_collection(test_id)
        time.sleep(0.1)  # Small delay to ensure measurable duration
        metrics = collector.stop_collection(test_id)
        
        assert isinstance(metrics, Metrics)
        assert metrics.duration_seconds > 0
        assert metrics.memory_peak_mb >= 0
        assert metrics.memory_average_mb >= 0
        assert metrics.cpu_peak_percent >= 0
        assert metrics.cpu_average_percent >= 0
        assert test_id not in collector.active_sessions
    
    def test_stop_collection_nonexistent_raises_error(self, collector):
        """Test stopping collection for nonexistent test_id raises error."""
        with pytest.raises(ValueError, match="No active collection"):
            collector.stop_collection("nonexistent_test")
    
    def test_collect_memory_usage(self, collector):
        """Test memory usage collection."""
        memory_mb = collector.collect_memory_usage()
        
        assert isinstance(memory_mb, float)
        assert memory_mb >= 0
        # Should be reasonable for a Python process (typically > 10MB)
        assert memory_mb > 0
    
    def test_collect_cpu_usage(self, collector):
        """Test CPU usage collection."""
        cpu_percent = collector.collect_cpu_usage()
        
        assert isinstance(cpu_percent, float)
        assert cpu_percent >= 0
        # CPU percent should be between 0 and 100 (or slightly higher on multi-core)
        assert cpu_percent <= 200  # Allow for multi-core
    
    def test_collect_disk_io(self, collector):
        """Test disk I/O collection."""
        disk_io = collector.collect_disk_io()
        
        assert disk_io.read_mb >= 0
        assert disk_io.write_mb >= 0
        assert disk_io.read_count >= 0
        assert disk_io.write_count >= 0
    
    def test_metrics_collection_with_workload(self, collector):
        """Test metrics collection with a known workload."""
        test_id = "test_workload"
        
        collector.start_collection(test_id)
        
        # Simulate some work
        data = []
        for i in range(10000):
            data.append(i * 2)
        
        time.sleep(0.1)
        
        metrics = collector.stop_collection(test_id)
        
        assert metrics.duration_seconds > 0.05  # Should take at least 50ms
        assert metrics.memory_peak_mb > 0
        assert metrics.memory_average_mb > 0
    
    # Test resource leak detection
    
    def test_detect_resource_leak_memory(self, collector):
        """Test detecting memory leak."""
        baseline = Metrics(
            duration_seconds=1.0,
            memory_peak_mb=100.0,
            memory_average_mb=80.0,
            cpu_peak_percent=50.0,
            cpu_average_percent=30.0,
            disk_read_mb=10.0,
            disk_write_mb=5.0,
            file_handles_peak=10,
            thread_count_peak=5
        )
        
        # Current metrics with 20% memory increase (exceeds 5% tolerance)
        current = Metrics(
            duration_seconds=1.0,
            memory_peak_mb=120.0,
            memory_average_mb=96.0,  # 20% increase
            cpu_peak_percent=50.0,
            cpu_average_percent=30.0,
            disk_read_mb=10.0,
            disk_write_mb=5.0,
            file_handles_peak=10,
            thread_count_peak=5
        )
        
        leak = collector.detect_resource_leak(baseline, current, tolerance_percent=5.0)
        
        assert leak is not None
        assert leak.resource_type == "memory"
        assert leak.increase_percent == 20.0
        assert leak.baseline_value == 80.0
        assert leak.current_value == 96.0
    
    def test_detect_resource_leak_file_handles(self, collector):
        """Test detecting file handle leak."""
        baseline = Metrics(
            duration_seconds=1.0,
            memory_peak_mb=100.0,
            memory_average_mb=80.0,
            cpu_peak_percent=50.0,
            cpu_average_percent=30.0,
            disk_read_mb=10.0,
            disk_write_mb=5.0,
            file_handles_peak=10,
            thread_count_peak=5
        )
        
        # Current metrics with 50% file handle increase
        current = Metrics(
            duration_seconds=1.0,
            memory_peak_mb=100.0,
            memory_average_mb=80.0,
            cpu_peak_percent=50.0,
            cpu_average_percent=30.0,
            disk_read_mb=10.0,
            disk_write_mb=5.0,
            file_handles_peak=15,  # 50% increase
            thread_count_peak=5
        )
        
        leak = collector.detect_resource_leak(baseline, current, tolerance_percent=5.0)
        
        assert leak is not None
        assert leak.resource_type == "file_handles"
        assert leak.increase_percent == 50.0
    
    def test_detect_resource_leak_threads(self, collector):
        """Test detecting thread leak."""
        baseline = Metrics(
            duration_seconds=1.0,
            memory_peak_mb=100.0,
            memory_average_mb=80.0,
            cpu_peak_percent=50.0,
            cpu_average_percent=30.0,
            disk_read_mb=10.0,
            disk_write_mb=5.0,
            file_handles_peak=10,
            thread_count_peak=5
        )
        
        # Current metrics with 100% thread increase
        current = Metrics(
            duration_seconds=1.0,
            memory_peak_mb=100.0,
            memory_average_mb=80.0,
            cpu_peak_percent=50.0,
            cpu_average_percent=30.0,
            disk_read_mb=10.0,
            disk_write_mb=5.0,
            file_handles_peak=10,
            thread_count_peak=10  # 100% increase
        )
        
        leak = collector.detect_resource_leak(baseline, current, tolerance_percent=5.0)
        
        assert leak is not None
        assert leak.resource_type == "threads"
        assert leak.increase_percent == 100.0
    
    def test_detect_resource_leak_no_leak(self, collector):
        """Test no leak detected when within tolerance."""
        baseline = Metrics(
            duration_seconds=1.0,
            memory_peak_mb=100.0,
            memory_average_mb=80.0,
            cpu_peak_percent=50.0,
            cpu_average_percent=30.0,
            disk_read_mb=10.0,
            disk_write_mb=5.0,
            file_handles_peak=10,
            thread_count_peak=5
        )
        
        # Current metrics with only 3% increase (within 5% tolerance)
        current = Metrics(
            duration_seconds=1.0,
            memory_peak_mb=100.0,
            memory_average_mb=82.4,  # 3% increase
            cpu_peak_percent=50.0,
            cpu_average_percent=30.0,
            disk_read_mb=10.0,
            disk_write_mb=5.0,
            file_handles_peak=10,
            thread_count_peak=5
        )
        
        leak = collector.detect_resource_leak(baseline, current, tolerance_percent=5.0)
        
        assert leak is None
    
    def test_detect_performance_degradation(self, collector):
        """Test detecting performance degradation."""
        baseline = Metrics(
            duration_seconds=10.0,
            memory_peak_mb=100.0,
            memory_average_mb=80.0,
            cpu_peak_percent=50.0,
            cpu_average_percent=30.0,
            disk_read_mb=10.0,
            disk_write_mb=5.0,
            file_handles_peak=10,
            thread_count_peak=5
        )
        
        # Current metrics with 30% duration increase (exceeds 20% threshold)
        current = Metrics(
            duration_seconds=13.0,  # 30% increase
            memory_peak_mb=100.0,
            memory_average_mb=80.0,
            cpu_peak_percent=50.0,
            cpu_average_percent=30.0,
            disk_read_mb=10.0,
            disk_write_mb=5.0,
            file_handles_peak=10,
            thread_count_peak=5
        )
        
        degradation = collector.detect_performance_degradation(
            baseline, current, threshold_percent=20.0
        )
        
        assert degradation is not None
        assert degradation.resource_type == "performance"
        assert degradation.increase_percent == 30.0
    
    def test_detect_performance_degradation_no_degradation(self, collector):
        """Test no degradation detected when within threshold."""
        baseline = Metrics(
            duration_seconds=10.0,
            memory_peak_mb=100.0,
            memory_average_mb=80.0,
            cpu_peak_percent=50.0,
            cpu_average_percent=30.0,
            disk_read_mb=10.0,
            disk_write_mb=5.0,
            file_handles_peak=10,
            thread_count_peak=5
        )
        
        # Current metrics with only 10% increase (within 20% threshold)
        current = Metrics(
            duration_seconds=11.0,  # 10% increase
            memory_peak_mb=100.0,
            memory_average_mb=80.0,
            cpu_peak_percent=50.0,
            cpu_average_percent=30.0,
            disk_read_mb=10.0,
            disk_write_mb=5.0,
            file_handles_peak=10,
            thread_count_peak=5
        )
        
        degradation = collector.detect_performance_degradation(
            baseline, current, threshold_percent=20.0
        )
        
        assert degradation is None
    
    # Test baseline storage and comparison
    
    def test_store_baseline(self, collector):
        """Test storing baseline metrics."""
        baseline_name = "test_baseline_1"
        metrics = Metrics(
            duration_seconds=5.0,
            memory_peak_mb=150.0,
            memory_average_mb=120.0,
            cpu_peak_percent=60.0,
            cpu_average_percent=40.0,
            disk_read_mb=20.0,
            disk_write_mb=10.0,
            file_handles_peak=15,
            thread_count_peak=8
        )
        
        collector.store_baseline(baseline_name, metrics)
        
        assert baseline_name in collector.baselines
        stored_metrics = collector.baselines[baseline_name]
        assert stored_metrics.duration_seconds == 5.0
        assert stored_metrics.memory_peak_mb == 150.0
    
    def test_get_baseline_existing(self, collector):
        """Test retrieving existing baseline."""
        baseline_name = "test_baseline_2"
        metrics = Metrics(
            duration_seconds=3.0,
            memory_peak_mb=100.0,
            memory_average_mb=80.0,
            cpu_peak_percent=50.0,
            cpu_average_percent=30.0,
            disk_read_mb=10.0,
            disk_write_mb=5.0,
            file_handles_peak=10,
            thread_count_peak=5
        )
        
        collector.store_baseline(baseline_name, metrics)
        retrieved_metrics = collector.get_baseline(baseline_name)
        
        assert retrieved_metrics is not None
        assert retrieved_metrics.duration_seconds == 3.0
        assert retrieved_metrics.memory_peak_mb == 100.0
    
    def test_get_baseline_nonexistent(self, collector):
        """Test retrieving nonexistent baseline returns None."""
        retrieved_metrics = collector.get_baseline("nonexistent_baseline")
        
        assert retrieved_metrics is None
    
    def test_baseline_comparison_workflow(self, collector):
        """Test complete baseline comparison workflow."""
        # Establish baseline
        baseline_metrics = Metrics(
            duration_seconds=5.0,
            memory_peak_mb=100.0,
            memory_average_mb=80.0,
            cpu_peak_percent=50.0,
            cpu_average_percent=30.0,
            disk_read_mb=10.0,
            disk_write_mb=5.0,
            file_handles_peak=10,
            thread_count_peak=5
        )
        
        collector.store_baseline("workflow_baseline", baseline_metrics)
        
        # Collect current metrics
        test_id = "workflow_test"
        collector.start_collection(test_id)
        time.sleep(0.1)
        current_metrics = collector.stop_collection(test_id)
        
        # Compare against baseline
        baseline = collector.get_baseline("workflow_baseline")
        assert baseline is not None
        
        # Check for leaks (should be none with such a short test)
        leak = collector.detect_resource_leak(baseline, current_metrics, tolerance_percent=50.0)
        # With high tolerance, should not detect leak
        assert leak is None or leak.increase_percent < 100
    
    # Test with known workloads
    
    def test_metrics_with_memory_intensive_workload(self, collector):
        """Test metrics collection with memory-intensive workload."""
        test_id = "memory_intensive"
        
        collector.start_collection(test_id)
        
        # Allocate significant memory
        large_list = [i for i in range(100000)]
        time.sleep(0.1)
        
        metrics = collector.stop_collection(test_id)
        
        assert metrics.memory_peak_mb > 0
        assert metrics.duration_seconds > 0
        
        # Clean up
        del large_list
    
    def test_metrics_with_cpu_intensive_workload(self, collector):
        """Test metrics collection with CPU-intensive workload."""
        test_id = "cpu_intensive"
        
        collector.start_collection(test_id)
        
        # Perform CPU-intensive calculation
        result = sum(i * i for i in range(100000))
        time.sleep(0.1)
        
        metrics = collector.stop_collection(test_id)
        
        assert metrics.cpu_peak_percent >= 0
        assert metrics.duration_seconds > 0
        assert result > 0  # Use result to prevent optimization
    
    def test_multiple_sequential_collections(self, collector):
        """Test multiple sequential metric collections."""
        test_ids = ["seq_test_1", "seq_test_2", "seq_test_3"]
        all_metrics = []
        
        for test_id in test_ids:
            collector.start_collection(test_id)
            time.sleep(0.05)
            metrics = collector.stop_collection(test_id)
            all_metrics.append(metrics)
        
        # All collections should succeed
        assert len(all_metrics) == 3
        for metrics in all_metrics:
            assert metrics.duration_seconds > 0
            assert metrics.memory_peak_mb > 0
    
    def test_resource_leak_string_representation(self):
        """Test ResourceLeak string representation."""
        leak = ResourceLeak(
            resource_type="memory",
            baseline_value=100.0,
            current_value=120.0,
            increase_percent=20.0,
            threshold_percent=5.0
        )
        
        leak_str = str(leak)
        
        assert "memory" in leak_str
        assert "100.00" in leak_str
        assert "120.00" in leak_str
        assert "20.0%" in leak_str
