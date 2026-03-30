"""
Test Configuration Management for Extreme Testing Framework

This module provides configuration management for all extreme test categories,
including test execution parameters, resource limits, and reporting options.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from pathlib import Path
import os


@dataclass
class TestConfig:
    """Configuration for test execution."""
    
    # Test selection
    categories: List[str] = field(default_factory=lambda: [
        'stress', 'chaos', 'adversarial', 'boundary', 'performance', 'property'
    ])
    requirements: List[str] = field(default_factory=list)  # Specific requirement IDs to test
    
    # Execution parameters
    concurrency: int = 4  # Number of concurrent test workers
    timeout_seconds: int = 3600  # Timeout for individual tests (1 hour)
    verbose: bool = False  # Enable verbose logging
    fail_fast: bool = False  # Stop on first failure
    
    # Directory configuration
    output_dir: str = field(default_factory=lambda: str(Path("test_outputs/extreme")))
    baseline_dir: str = field(default_factory=lambda: str(Path("test_outputs/baselines")))
    oracle_dir: str = field(default_factory=lambda: str(Path("tests/extreme/oracles")))
    test_data_dir: str = field(default_factory=lambda: str(Path("test_outputs/test_data")))
    
    # Stress testing parameters
    max_document_pages: int = 100
    max_document_words: int = 500000
    max_chunk_count: int = 10000
    max_concurrent_operations: int = 5
    resource_leak_iterations: int = 100
    
    # Chaos testing parameters
    fault_injection_points: int = 50
    chaos_integration_runs: int = 100
    
    # Adversarial testing parameters
    malicious_pdf_samples: int = 20
    prompt_injection_patterns: int = 15
    path_traversal_patterns: int = 10
    
    # Boundary testing parameters
    encoding_languages: int = 10
    similarity_score_combinations: int = 200
    
    # Performance profiling parameters
    performance_baseline_pages: List[int] = field(default_factory=lambda: [10, 50, 100])
    performance_degradation_alert_threshold: float = 0.20  # 20% degradation
    
    # Property testing parameters
    property_test_multiplier: int = 10  # Multiply existing test cases by this factor
    hypothesis_max_examples: int = 1000
    hypothesis_deadline_ms: Optional[int] = None  # No deadline
    
    # Reporting parameters
    generate_html_report: bool = True
    generate_json_report: bool = True
    generate_junit_xml: bool = True
    
    def __post_init__(self):
        """Create directories if they don't exist."""
        for dir_path in [self.output_dir, self.baseline_dir, self.oracle_dir, self.test_data_dir]:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'TestConfig':
        """Create TestConfig from dictionary."""
        return cls(**{k: v for k, v in config_dict.items() if k in cls.__dataclass_fields__})
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert TestConfig to dictionary."""
        return {
            'categories': self.categories,
            'requirements': self.requirements,
            'concurrency': self.concurrency,
            'timeout_seconds': self.timeout_seconds,
            'verbose': self.verbose,
            'fail_fast': self.fail_fast,
            'output_dir': self.output_dir,
            'baseline_dir': self.baseline_dir,
            'oracle_dir': self.oracle_dir,
            'test_data_dir': self.test_data_dir,
            'max_document_pages': self.max_document_pages,
            'max_document_words': self.max_document_words,
            'max_chunk_count': self.max_chunk_count,
            'max_concurrent_operations': self.max_concurrent_operations,
            'resource_leak_iterations': self.resource_leak_iterations,
            'fault_injection_points': self.fault_injection_points,
            'chaos_integration_runs': self.chaos_integration_runs,
            'malicious_pdf_samples': self.malicious_pdf_samples,
            'prompt_injection_patterns': self.prompt_injection_patterns,
            'path_traversal_patterns': self.path_traversal_patterns,
            'encoding_languages': self.encoding_languages,
            'similarity_score_combinations': self.similarity_score_combinations,
            'performance_baseline_pages': self.performance_baseline_pages,
            'performance_degradation_alert_threshold': self.performance_degradation_alert_threshold,
            'property_test_multiplier': self.property_test_multiplier,
            'hypothesis_max_examples': self.hypothesis_max_examples,
            'hypothesis_deadline_ms': self.hypothesis_deadline_ms,
            'generate_html_report': self.generate_html_report,
            'generate_json_report': self.generate_json_report,
            'generate_junit_xml': self.generate_junit_xml,
        }


# Default configuration instance
DEFAULT_CONFIG = TestConfig()
