"""
Data Models for Extreme Testing Framework

This module defines data structures used throughout the testing framework
for test results, metrics, breaking points, and reports.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class TestStatus(Enum):
    """Test execution status."""
    PASS = "pass"
    FAIL = "fail"
    SKIP = "skip"
    ERROR = "error"


class FailureCategory(Enum):
    """Categories of failure modes."""
    CRASH = "crash"
    DATA_CORRUPTION = "data_corruption"
    INCORRECT_OUTPUT = "incorrect_output"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    TIMEOUT = "timeout"
    RESOURCE_EXHAUSTION = "resource_exhaustion"


@dataclass
class Metrics:
    """Performance and resource metrics."""
    duration_seconds: float
    memory_peak_mb: float
    memory_average_mb: float
    cpu_peak_percent: float
    cpu_average_percent: float
    disk_read_mb: float
    disk_write_mb: float
    file_handles_peak: int
    thread_count_peak: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'duration_seconds': self.duration_seconds,
            'memory_peak_mb': self.memory_peak_mb,
            'memory_average_mb': self.memory_average_mb,
            'cpu_peak_percent': self.cpu_peak_percent,
            'cpu_average_percent': self.cpu_average_percent,
            'disk_read_mb': self.disk_read_mb,
            'disk_write_mb': self.disk_write_mb,
            'file_handles_peak': self.file_handles_peak,
            'thread_count_peak': self.thread_count_peak,
        }


@dataclass
class TestResult:
    """Result from a single test execution."""
    test_id: str
    requirement_id: str
    category: str
    status: TestStatus
    duration_seconds: float
    error_message: Optional[str] = None
    metrics: Optional[Metrics] = None
    artifacts: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'test_id': self.test_id,
            'requirement_id': self.requirement_id,
            'category': self.category,
            'status': self.status.value,
            'duration_seconds': self.duration_seconds,
            'error_message': self.error_message,
            'metrics': self.metrics.to_dict() if self.metrics else None,
            'artifacts': self.artifacts,
            'timestamp': self.timestamp.isoformat(),
        }


@dataclass
class BreakingPoint:
    """Identified breaking point for a dimension."""
    dimension: str  # 'document_size', 'chunk_count', 'concurrency', etc.
    maximum_viable_value: Any
    failure_mode: FailureCategory
    error_message: str
    metrics_at_failure: Optional[Metrics] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'dimension': self.dimension,
            'maximum_viable_value': str(self.maximum_viable_value),
            'failure_mode': self.failure_mode.value,
            'error_message': self.error_message,
            'metrics_at_failure': self.metrics_at_failure.to_dict() if self.metrics_at_failure else None,
        }


@dataclass
class OracleTestCase:
    """Known-good test case with expected output."""
    test_id: str
    policy_document: str
    expected_gaps: List[str]  # CSF subcategory IDs
    expected_covered: List[str]  # CSF subcategory IDs
    expected_gap_count: int
    tolerance: float = 0.05  # 5% tolerance
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'test_id': self.test_id,
            'policy_document': self.policy_document,
            'expected_gaps': self.expected_gaps,
            'expected_covered': self.expected_covered,
            'expected_gap_count': self.expected_gap_count,
            'tolerance': self.tolerance,
            'description': self.description,
        }


@dataclass
class ValidationResult:
    """Result from oracle validation."""
    test_case_id: str
    passed: bool
    accuracy: float  # Percentage of correct classifications
    false_positives: List[str] = field(default_factory=list)  # Gaps detected but not expected
    false_negatives: List[str] = field(default_factory=list)  # Expected gaps not detected
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'test_case_id': self.test_case_id,
            'passed': self.passed,
            'accuracy': self.accuracy,
            'false_positives': self.false_positives,
            'false_negatives': self.false_negatives,
            'error_message': self.error_message,
        }


@dataclass
class FailureMode:
    """Documented failure mode discovered during testing."""
    failure_id: str
    category: FailureCategory
    trigger: str  # Conditions that trigger the failure
    impact: str  # Impact on system behavior
    mitigation: str  # Recommended mitigation
    discovered_date: datetime
    test_id: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'failure_id': self.failure_id,
            'category': self.category.value,
            'trigger': self.trigger,
            'impact': self.impact,
            'mitigation': self.mitigation,
            'discovered_date': self.discovered_date.isoformat(),
            'test_id': self.test_id,
        }


@dataclass
class CategoryReport:
    """Report for a test category."""
    category: str
    total_tests: int
    passed: int
    failed: int
    skipped: int
    errors: int
    duration_seconds: float
    test_results: List[TestResult] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'category': self.category,
            'total_tests': self.total_tests,
            'passed': self.passed,
            'failed': self.failed,
            'skipped': self.skipped,
            'errors': self.errors,
            'duration_seconds': self.duration_seconds,
            'test_results': [r.to_dict() for r in self.test_results],
        }


@dataclass
class RequirementReport:
    """Report for a specific requirement."""
    requirement_id: str
    total_tests: int
    passed: int
    failed: int
    test_results: List[TestResult] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'requirement_id': self.requirement_id,
            'total_tests': self.total_tests,
            'passed': self.passed,
            'failed': self.failed,
            'test_results': [r.to_dict() for r in self.test_results],
        }


@dataclass
class TestReport:
    """Comprehensive test execution report."""
    execution_date: datetime
    total_tests: int
    passed: int
    failed: int
    skipped: int
    errors: int
    duration_seconds: float
    category_results: Dict[str, CategoryReport] = field(default_factory=dict)
    requirement_results: Dict[str, RequirementReport] = field(default_factory=dict)
    breaking_points: List[BreakingPoint] = field(default_factory=list)
    failure_modes: List[FailureMode] = field(default_factory=list)
    performance_baselines: Dict[str, Metrics] = field(default_factory=dict)
    artifacts_dir: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'execution_date': self.execution_date.isoformat(),
            'total_tests': self.total_tests,
            'passed': self.passed,
            'failed': self.failed,
            'skipped': self.skipped,
            'errors': self.errors,
            'duration_seconds': self.duration_seconds,
            'category_results': {k: v.to_dict() for k, v in self.category_results.items()},
            'requirement_results': {k: v.to_dict() for k, v in self.requirement_results.items()},
            'breaking_points': [bp.to_dict() for bp in self.breaking_points],
            'failure_modes': [fm.to_dict() for fm in self.failure_modes],
            'performance_baselines': {k: v.to_dict() for k, v in self.performance_baselines.items()},
            'artifacts_dir': self.artifacts_dir,
        }
