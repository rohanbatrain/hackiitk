"""
Performance optimization utilities for the Offline Policy Gap Analyzer.

This module provides utilities for profiling, monitoring, and optimizing
performance across the analysis pipeline.
"""

import time
import psutil
import logging
from typing import Callable, Any, Dict, Optional
from functools import wraps
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Monitor and log performance metrics during analysis."""
    
    def __init__(self):
        """Initialize performance monitor."""
        self.metrics: Dict[str, Dict[str, Any]] = {}
        self.start_time: Optional[float] = None
    
    def start(self) -> None:
        """Start monitoring."""
        self.start_time = time.time()
        self.metrics.clear()
    
    def record_operation(
        self,
        operation_name: str,
        duration: float,
        items_processed: int = 0,
        memory_used_mb: float = 0.0
    ) -> None:
        """Record metrics for an operation.
        
        Args:
            operation_name: Name of the operation
            duration: Duration in seconds
            items_processed: Number of items processed
            memory_used_mb: Memory used in MB
        """
        if operation_name not in self.metrics:
            self.metrics[operation_name] = {
                'count': 0,
                'total_duration': 0.0,
                'total_items': 0,
                'total_memory_mb': 0.0
            }
        
        self.metrics[operation_name]['count'] += 1
        self.metrics[operation_name]['total_duration'] += duration
        self.metrics[operation_name]['total_items'] += items_processed
        self.metrics[operation_name]['total_memory_mb'] += memory_used_mb
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary.
        
        Returns:
            Dictionary with performance metrics
        """
        if not self.start_time:
            return {}
        
        total_time = time.time() - self.start_time
        
        summary = {
            'total_time_seconds': total_time,
            'operations': {}
        }
        
        for op_name, metrics in self.metrics.items():
            avg_duration = metrics['total_duration'] / metrics['count'] if metrics['count'] > 0 else 0
            throughput = metrics['total_items'] / metrics['total_duration'] if metrics['total_duration'] > 0 else 0
            
            summary['operations'][op_name] = {
                'count': metrics['count'],
                'total_duration': metrics['total_duration'],
                'avg_duration': avg_duration,
                'items_processed': metrics['total_items'],
                'throughput_per_sec': throughput,
                'memory_used_mb': metrics['total_memory_mb']
            }
        
        return summary
    
    def log_summary(self) -> None:
        """Log performance summary."""
        summary = self.get_summary()
        
        logger.info("=== Performance Summary ===")
        logger.info(f"Total time: {summary.get('total_time_seconds', 0):.2f}s")
        
        for op_name, metrics in summary.get('operations', {}).items():
            logger.info(
                f"{op_name}: {metrics['count']} calls, "
                f"{metrics['total_duration']:.2f}s total, "
                f"{metrics['avg_duration']:.3f}s avg, "
                f"{metrics['throughput_per_sec']:.1f} items/sec"
            )


@contextmanager
def profile_operation(operation_name: str, monitor: Optional[PerformanceMonitor] = None):
    """Context manager for profiling an operation.
    
    Args:
        operation_name: Name of the operation
        monitor: Optional performance monitor to record metrics
        
    Yields:
        Dictionary to store operation metadata
    """
    start_time = time.time()
    process = psutil.Process()
    memory_before = process.memory_info().rss / (1024 * 1024)  # MB
    
    metadata = {'items_processed': 0}
    
    try:
        yield metadata
    finally:
        duration = time.time() - start_time
        memory_after = process.memory_info().rss / (1024 * 1024)  # MB
        memory_used = memory_after - memory_before
        
        logger.debug(
            f"{operation_name}: {duration:.3f}s, "
            f"{metadata.get('items_processed', 0)} items, "
            f"{memory_used:.1f}MB"
        )
        
        if monitor:
            monitor.record_operation(
                operation_name=operation_name,
                duration=duration,
                items_processed=metadata.get('items_processed', 0),
                memory_used_mb=memory_used
            )


def timed_operation(operation_name: str):
    """Decorator for timing operations.
    
    Args:
        operation_name: Name of the operation
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.debug(f"{operation_name} completed in {duration:.3f}s")
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"{operation_name} failed after {duration:.3f}s: {e}")
                raise
        return wrapper
    return decorator


class BatchProcessor:
    """Utility for processing items in optimized batches."""
    
    @staticmethod
    def process_in_batches(
        items: list,
        process_func: Callable,
        batch_size: int = 64,
        show_progress: bool = False
    ) -> list:
        """Process items in batches for optimal throughput.
        
        Args:
            items: List of items to process
            process_func: Function to process each batch
            batch_size: Size of each batch
            show_progress: Whether to log progress
            
        Returns:
            List of processed results
        """
        results = []
        total_batches = (len(items) + batch_size - 1) // batch_size
        
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            batch_num = i // batch_size + 1
            
            if show_progress:
                logger.info(f"Processing batch {batch_num}/{total_batches}")
            
            batch_results = process_func(batch)
            results.extend(batch_results)
        
        return results
    
    @staticmethod
    def optimal_batch_size(
        item_size_bytes: int,
        available_memory_mb: float = 1000.0,
        safety_factor: float = 0.5
    ) -> int:
        """Calculate optimal batch size based on memory constraints.
        
        Args:
            item_size_bytes: Estimated size of each item in bytes
            available_memory_mb: Available memory in MB
            safety_factor: Safety factor (0.0-1.0) to avoid OOM
            
        Returns:
            Optimal batch size
        """
        available_bytes = available_memory_mb * 1024 * 1024 * safety_factor
        batch_size = int(available_bytes / item_size_bytes)
        
        # Clamp to reasonable range
        return max(8, min(batch_size, 256))


class MemoryMonitor:
    """Monitor memory usage and trigger warnings."""
    
    def __init__(self, threshold: float = 0.9):
        """Initialize memory monitor.
        
        Args:
            threshold: Memory usage threshold (0.0-1.0) to trigger warnings
        """
        self.threshold = threshold
    
    def check_memory(self) -> float:
        """Check current memory usage.
        
        Returns:
            Memory usage as percentage (0.0-1.0)
        """
        memory = psutil.virtual_memory()
        return memory.percent / 100.0
    
    def is_memory_critical(self) -> bool:
        """Check if memory usage is critical.
        
        Returns:
            True if memory usage exceeds threshold
        """
        return self.check_memory() >= self.threshold
    
    def log_memory_status(self) -> None:
        """Log current memory status."""
        memory = psutil.virtual_memory()
        logger.info(
            f"Memory: {memory.percent:.1f}% used "
            f"({memory.used / (1024**3):.2f}GB / {memory.total / (1024**3):.2f}GB)"
        )
    
    def get_available_memory_mb(self) -> float:
        """Get available memory in MB.
        
        Returns:
            Available memory in MB
        """
        memory = psutil.virtual_memory()
        return memory.available / (1024 * 1024)


def estimate_processing_time(
    items_count: int,
    items_per_second: float,
    overhead_seconds: float = 0.0
) -> float:
    """Estimate processing time for a batch of items.
    
    Args:
        items_count: Number of items to process
        items_per_second: Processing throughput
        overhead_seconds: Fixed overhead time
        
    Returns:
        Estimated time in seconds
    """
    if items_per_second <= 0:
        return float('inf')
    
    return (items_count / items_per_second) + overhead_seconds


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"
