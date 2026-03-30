"""
Metrics Collector for Resource Monitoring

This module provides the MetricsCollector class for tracking system resource
usage during test execution, including memory, CPU, and disk I/O metrics.
"""

import time
import psutil
from typing import Optional, Dict
from dataclasses import dataclass, field
from datetime import datetime

from ..models import Metrics


@dataclass
class DiskIOMetrics:
    """Disk I/O metrics."""
    read_mb: float
    write_mb: float
    read_count: int
    write_count: int


@dataclass
class ResourceLeak:
    """Detected resource leak information."""
    resource_type: str  # 'memory', 'file_handles', 'threads'
    baseline_value: float
    current_value: float
    increase_percent: float
    threshold_percent: float = 5.0  # 5% tolerance
    
    def __str__(self) -> str:
        return (
            f"Resource leak detected: {self.resource_type} "
            f"increased from {self.baseline_value:.2f} to {self.current_value:.2f} "
            f"({self.increase_percent:.1f}% increase, threshold: {self.threshold_percent}%)"
        )


@dataclass
class CollectionSession:
    """Active metrics collection session."""
    test_id: str
    start_time: float
    start_memory_mb: float
    start_cpu_percent: float
    start_disk_io: DiskIOMetrics
    start_file_handles: int
    start_threads: int
    
    # Track peak and average values during collection
    memory_samples: list = field(default_factory=list)
    cpu_samples: list = field(default_factory=list)


class MetricsCollector:
    """
    Collects and stores performance metrics for test execution.
    
    Uses psutil for cross-platform resource monitoring to track:
    - Memory usage (peak and average)
    - CPU usage (peak and average)
    - Disk I/O (read/write bytes and operations)
    - File handle count
    - Thread count
    """
    
    def __init__(self):
        """Initialize metrics collector."""
        self.active_sessions: Dict[str, CollectionSession] = {}
        self.baselines: Dict[str, Metrics] = {}
        self.process = psutil.Process()
    
    def start_collection(self, test_id: str) -> None:
        """
        Start collecting metrics for a test.
        
        Args:
            test_id: Unique test identifier
        """
        if test_id in self.active_sessions:
            raise ValueError(f"Collection already active for test_id: {test_id}")
        
        # Collect initial metrics
        start_memory = self.collect_memory_usage()
        start_cpu = self.collect_cpu_usage()
        start_disk_io = self.collect_disk_io()
        start_file_handles = self._get_file_handle_count()
        start_threads = self._get_thread_count()
        
        # Create collection session
        session = CollectionSession(
            test_id=test_id,
            start_time=time.time(),
            start_memory_mb=start_memory,
            start_cpu_percent=start_cpu,
            start_disk_io=start_disk_io,
            start_file_handles=start_file_handles,
            start_threads=start_threads,
            memory_samples=[start_memory],
            cpu_samples=[start_cpu]
        )
        
        self.active_sessions[test_id] = session
    
    def stop_collection(self, test_id: str) -> Metrics:
        """
        Stop collecting metrics and return results.
        
        Args:
            test_id: Unique test identifier
            
        Returns:
            Metrics object with collected data
            
        Raises:
            ValueError: If no active collection for test_id
        """
        if test_id not in self.active_sessions:
            raise ValueError(f"No active collection for test_id: {test_id}")
        
        session = self.active_sessions[test_id]
        
        # Collect final metrics
        end_time = time.time()
        end_memory = self.collect_memory_usage()
        end_cpu = self.collect_cpu_usage()
        end_disk_io = self.collect_disk_io()
        end_file_handles = self._get_file_handle_count()
        end_threads = self._get_thread_count()
        
        # Add final samples
        session.memory_samples.append(end_memory)
        session.cpu_samples.append(end_cpu)
        
        # Calculate metrics
        duration = end_time - session.start_time
        memory_peak = max(session.memory_samples)
        memory_average = sum(session.memory_samples) / len(session.memory_samples)
        cpu_peak = max(session.cpu_samples)
        cpu_average = sum(session.cpu_samples) / len(session.cpu_samples)
        
        # Calculate disk I/O delta
        disk_read_mb = end_disk_io.read_mb - session.start_disk_io.read_mb
        disk_write_mb = end_disk_io.write_mb - session.start_disk_io.write_mb
        
        # Create metrics object
        metrics = Metrics(
            duration_seconds=duration,
            memory_peak_mb=memory_peak,
            memory_average_mb=memory_average,
            cpu_peak_percent=cpu_peak,
            cpu_average_percent=cpu_average,
            disk_read_mb=disk_read_mb,
            disk_write_mb=disk_write_mb,
            file_handles_peak=end_file_handles,
            thread_count_peak=end_threads
        )
        
        # Clean up session
        del self.active_sessions[test_id]
        
        return metrics
    
    def collect_memory_usage(self) -> float:
        """
        Collect current memory usage in MB.
        
        Returns:
            Memory usage in megabytes
        """
        try:
            memory_info = self.process.memory_info()
            # Return RSS (Resident Set Size) in MB
            return memory_info.rss / (1024 * 1024)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return 0.0
    
    def collect_cpu_usage(self) -> float:
        """
        Collect current CPU usage percentage.
        
        Returns:
            CPU usage as percentage (0-100)
        """
        try:
            # Get CPU percent with a short interval for accuracy
            # interval=0.1 means measure over 100ms
            return self.process.cpu_percent(interval=0.1)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return 0.0
    
    def collect_disk_io(self) -> DiskIOMetrics:
        """
        Collect disk I/O metrics.
        
        Returns:
            DiskIOMetrics object with read/write statistics
        """
        try:
            io_counters = self.process.io_counters()
            return DiskIOMetrics(
                read_mb=io_counters.read_bytes / (1024 * 1024),
                write_mb=io_counters.write_bytes / (1024 * 1024),
                read_count=io_counters.read_count,
                write_count=io_counters.write_count
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
            # AttributeError can occur on some platforms where io_counters is not available
            return DiskIOMetrics(read_mb=0.0, write_mb=0.0, read_count=0, write_count=0)
    
    def detect_resource_leak(
        self, 
        baseline: Metrics, 
        current: Metrics,
        tolerance_percent: float = 5.0
    ) -> Optional[ResourceLeak]:
        """
        Detect resource leaks by comparing metrics.
        
        Args:
            baseline: Baseline metrics
            current: Current metrics
            tolerance_percent: Acceptable increase percentage (default 5%)
            
        Returns:
            ResourceLeak object if leak detected, None otherwise
        """
        # Check memory leak
        if baseline.memory_average_mb > 0:
            memory_increase = (
                (current.memory_average_mb - baseline.memory_average_mb) 
                / baseline.memory_average_mb * 100
            )
            if memory_increase > tolerance_percent:
                return ResourceLeak(
                    resource_type='memory',
                    baseline_value=baseline.memory_average_mb,
                    current_value=current.memory_average_mb,
                    increase_percent=memory_increase,
                    threshold_percent=tolerance_percent
                )
        
        # Check file handle leak
        if baseline.file_handles_peak > 0:
            handle_increase = (
                (current.file_handles_peak - baseline.file_handles_peak)
                / baseline.file_handles_peak * 100
            )
            if handle_increase > tolerance_percent:
                return ResourceLeak(
                    resource_type='file_handles',
                    baseline_value=float(baseline.file_handles_peak),
                    current_value=float(current.file_handles_peak),
                    increase_percent=handle_increase,
                    threshold_percent=tolerance_percent
                )
        
        # Check thread leak
        if baseline.thread_count_peak > 0:
            thread_increase = (
                (current.thread_count_peak - baseline.thread_count_peak)
                / baseline.thread_count_peak * 100
            )
            if thread_increase > tolerance_percent:
                return ResourceLeak(
                    resource_type='threads',
                    baseline_value=float(baseline.thread_count_peak),
                    current_value=float(current.thread_count_peak),
                    increase_percent=thread_increase,
                    threshold_percent=tolerance_percent
                )
        
        return None
    
    def detect_performance_degradation(
        self,
        baseline: Metrics,
        current: Metrics,
        threshold_percent: float = 20.0
    ) -> Optional[ResourceLeak]:
        """
        Detect performance degradation by comparing metrics.
        
        Checks if performance (duration) has degraded more than the threshold
        percentage compared to baseline. This is used for regression detection.
        
        Args:
            baseline: Baseline metrics
            current: Current metrics
            threshold_percent: Acceptable degradation percentage (default 20%)
            
        Returns:
            ResourceLeak object if degradation detected, None otherwise
        """
        if baseline.duration_seconds > 0:
            duration_increase = (
                (current.duration_seconds - baseline.duration_seconds)
                / baseline.duration_seconds * 100
            )
            if duration_increase > threshold_percent:
                return ResourceLeak(
                    resource_type='performance',
                    baseline_value=baseline.duration_seconds,
                    current_value=current.duration_seconds,
                    increase_percent=duration_increase,
                    threshold_percent=threshold_percent
                )
        
        return None
    
    def store_baseline(self, name: str, metrics: Metrics) -> None:
        """
        Store baseline metrics for regression detection.
        
        Args:
            name: Baseline name/identifier
            metrics: Metrics to store as baseline
        """
        self.baselines[name] = metrics
    
    def get_baseline(self, name: str) -> Optional[Metrics]:
        """
        Retrieve stored baseline metrics.
        
        Args:
            name: Baseline name/identifier
            
        Returns:
            Stored metrics or None if not found
        """
        return self.baselines.get(name)
    
    def _get_file_handle_count(self) -> int:
        """
        Get current file handle count.
        
        Returns:
            Number of open file handles
        """
        try:
            return self.process.num_fds() if hasattr(self.process, 'num_fds') else len(self.process.open_files())
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return 0
    
    def _get_thread_count(self) -> int:
        """
        Get current thread count.
        
        Returns:
            Number of threads
        """
        try:
            return self.process.num_threads()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return 0
