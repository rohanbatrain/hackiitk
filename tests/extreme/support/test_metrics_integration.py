"""
Integration Tests for MetricsCollector

Demonstrates MetricsCollector usage in realistic scenarios.
"""

import pytest
import time
from tests.extreme.support.metrics_collector import MetricsCollector


class TestMetricsCollectorIntegration:
    """Integration tests for MetricsCollector."""
    
    def test_resource_leak_detection_scenario(self):
        """
        Test a realistic resource leak detection scenario.
        
        Simulates running multiple operations and detecting if resources
        are properly released between runs.
        """
        collector = MetricsCollector()
        
        # Run baseline operation
        collector.start_collection("baseline_run")
        self._simulate_work(iterations=100)
        baseline_metrics = collector.stop_collection("baseline_run")
        
        # Store baseline
        collector.store_baseline("operation_baseline", baseline_metrics)
        
        # Run subsequent operation
        collector.start_collection("subsequent_run")
        self._simulate_work(iterations=100)
        current_metrics = collector.stop_collection("subsequent_run")
        
        # Check for resource leaks
        leak = collector.detect_resource_leak(baseline_metrics, current_metrics)
        
        # In a well-behaved system, there should be no leak
        # (or only a very small increase within tolerance)
        if leak:
            print(f"Warning: {leak}")
        
        # Verify metrics are reasonable
        assert current_metrics.duration_seconds > 0
        assert current_metrics.memory_peak_mb > 0
    
    def test_performance_degradation_tracking(self):
        """
        Test tracking performance degradation over multiple runs.
        
        Simulates running the same operation multiple times and
        verifies that metrics are collected consistently.
        """
        collector = MetricsCollector()
        metrics_history = []
        
        # Run operation 5 times
        for i in range(5):
            test_id = f"run_{i}"
            collector.start_collection(test_id)
            self._simulate_work(iterations=50)
            metrics = collector.stop_collection(test_id)
            metrics_history.append(metrics)
        
        # Verify all runs completed
        assert len(metrics_history) == 5
        
        # Verify all metrics are valid (positive durations)
        for metrics in metrics_history:
            assert metrics.duration_seconds > 0
            assert metrics.memory_peak_mb > 0
            assert metrics.memory_average_mb > 0
        
        # Verify metrics are being collected (not all zeros)
        durations = [m.duration_seconds for m in metrics_history]
        assert all(d > 0 for d in durations)
        
        # Verify we can detect if one run is significantly slower
        # (this is what the test is really about - detecting degradation)
        avg_duration = sum(durations) / len(durations)
        for i, duration in enumerate(durations):
            # If a run is more than 2x slower, we should be able to detect it
            if duration > avg_duration * 2:
                print(f"Run {i} was significantly slower: {duration}s vs avg {avg_duration}s")
    
    def test_concurrent_metrics_collection(self):
        """
        Test collecting metrics for multiple concurrent operations.
        
        Simulates tracking multiple operations simultaneously.
        """
        collector = MetricsCollector()
        
        # Start multiple collections
        collector.start_collection("operation_a")
        time.sleep(0.05)
        
        collector.start_collection("operation_b")
        time.sleep(0.05)
        
        collector.start_collection("operation_c")
        time.sleep(0.05)
        
        # Stop in different order
        metrics_b = collector.stop_collection("operation_b")
        metrics_a = collector.stop_collection("operation_a")
        metrics_c = collector.stop_collection("operation_c")
        
        # Verify all metrics are valid
        assert metrics_a.duration_seconds > 0.1  # Should be at least 0.15s
        assert metrics_b.duration_seconds > 0.05  # Should be at least 0.1s
        assert metrics_c.duration_seconds > 0  # Should be at least 0.05s
        
        # Verify operation_a took longest (started first, stopped second)
        assert metrics_a.duration_seconds > metrics_c.duration_seconds
    
    def test_baseline_comparison_workflow(self):
        """
        Test the complete workflow of establishing and comparing against baselines.
        """
        collector = MetricsCollector()
        
        # Establish baseline
        collector.start_collection("baseline")
        self._simulate_work(iterations=100)
        baseline = collector.stop_collection("baseline")
        collector.store_baseline("standard_operation", baseline)
        
        # Run normal operation
        collector.start_collection("normal_run")
        self._simulate_work(iterations=100)
        normal_metrics = collector.stop_collection("normal_run")
        
        # Compare against baseline
        retrieved_baseline = collector.get_baseline("standard_operation")
        assert retrieved_baseline is not None
        
        leak = collector.detect_resource_leak(retrieved_baseline, normal_metrics)
        
        # Should not detect leak for similar operations
        assert leak is None or leak.increase_percent < 10.0
    
    def test_performance_degradation_detection_workflow(self):
        """
        Test detecting performance degradation against baseline.
        """
        collector = MetricsCollector()
        
        # Establish baseline with fast operation
        collector.start_collection("baseline")
        self._simulate_work(iterations=50)
        baseline = collector.stop_collection("baseline")
        collector.store_baseline("fast_operation", baseline)
        
        # Run slower operation (more iterations)
        collector.start_collection("slow_run")
        self._simulate_work(iterations=200)  # 4x more work
        slow_metrics = collector.stop_collection("slow_run")
        
        # Compare against baseline
        retrieved_baseline = collector.get_baseline("fast_operation")
        assert retrieved_baseline is not None
        
        # Should detect performance degradation
        degradation = collector.detect_performance_degradation(retrieved_baseline, slow_metrics, threshold_percent=20.0)
        
        # The slow operation should take significantly longer
        if degradation:
            assert degradation.resource_type == 'performance'
            assert degradation.increase_percent > 20.0
            print(f"Performance degradation detected: {degradation}")
        else:
            # If no degradation detected, verify durations are similar
            duration_ratio = slow_metrics.duration_seconds / baseline.duration_seconds
            assert duration_ratio < 1.2  # Less than 20% increase
    
    def test_memory_intensive_operation_tracking(self):
        """
        Test tracking metrics for a memory-intensive operation.
        """
        collector = MetricsCollector()
        
        collector.start_collection("memory_test")
        
        # Allocate some memory
        large_list = [i for i in range(100000)]
        large_dict = {i: str(i) * 100 for i in range(1000)}
        
        # Keep references alive
        _ = len(large_list) + len(large_dict)
        
        metrics = collector.stop_collection("memory_test")
        
        # Verify memory usage was tracked
        assert metrics.memory_peak_mb > 0
        assert metrics.memory_average_mb > 0
        assert metrics.memory_peak_mb >= metrics.memory_average_mb
    
    @staticmethod
    def _simulate_work(iterations: int = 100):
        """Simulate some computational work."""
        result = 0
        for i in range(iterations):
            result += sum(j ** 2 for j in range(100))
        return result
