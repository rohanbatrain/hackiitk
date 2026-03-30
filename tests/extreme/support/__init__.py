"""
Test Support Components

This package contains support components used by test engines:
- Fault Injector: Mechanisms for simulating system failures
- Test Data Generator: Diverse test data generation
- Metrics Collector: Performance and resource metrics collection
- Oracle Validator: Known-good test case validation
"""

from .metrics_collector import MetricsCollector, DiskIOMetrics, ResourceLeak
from .fault_injector import FaultInjector

__all__ = ['MetricsCollector', 'DiskIOMetrics', 'ResourceLeak', 'FaultInjector']
