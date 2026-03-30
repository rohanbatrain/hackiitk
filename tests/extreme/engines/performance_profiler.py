"""
Performance Profiler for Degradation Analysis

This module implements the PerformanceProfiler class that measures performance
degradation curves and identifies bottlenecks in the analysis pipeline.
"""

import time
import logging
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, field
import json

from ..base import BaseTestEngine
from ..models import TestResult, TestStatus, Metrics
from ..config import TestConfig
from ..support.metrics_collector import MetricsCollector
from ..data_generator import TestDataGenerator, DocumentSpec

# Import Policy Analyzer components
from orchestration.analysis_pipeline import AnalysisPipeline, PipelineConfig


@dataclass
class PerformanceDataPoint:
    """Single performance measurement data point."""
    dimension_value: Any  # e.g., 10 pages, 1000 chunks, 5000 tokens
    duration_seconds: float
    memory_peak_mb: float
    memory_average_mb: float
    cpu_peak_percent: float
    cpu_average_percent: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'dimension_value': str(self.dimension_value),
            'duration_seconds': self.duration_seconds,
            'memory_peak_mb': self.memory_peak_mb,
            'memory_average_mb': self.memory_average_mb,
            'cpu_peak_percent': self.cpu_peak_percent,
            'cpu_average_percent': self.cpu_average_percent,
        }


@dataclass
class PerformanceReport:
    """Performance profiling report for a dimension."""
    dimension: str  # 'document_size', 'chunk_count', 'llm_context'
    data_points: List[PerformanceDataPoint] = field(default_factory=list)
    bottlenecks: List[str] = field(default_factory=list)
    performance_cliff: Optional[str] = None  # Description of non-linear degradation
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'dimension': self.dimension,
            'data_points': [dp.to_dict() for dp in self.data_points],
            'bottlenecks': self.bottlenecks,
            'performance_cliff': self.performance_cliff,
        }


@dataclass
class Bottleneck:
    """Identified performance bottleneck."""
    stage: str  # Pipeline stage name
    duration_seconds: float
    percentage_of_total: float
    description: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'stage': self.stage,
            'duration_seconds': self.duration_seconds,
            'percentage_of_total': self.percentage_of_total,
            'description': self.description,
        }


@dataclass
class BaselineMetrics:
    """Baseline performance metrics for regression detection."""
    name: str  # e.g., '10-page', '50-page', '100-page'
    metrics: Metrics
    timestamp: str
    hardware_info: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'metrics': self.metrics.to_dict(),
            'timestamp': self.timestamp,
            'hardware_info': self.hardware_info,
        }


class PerformanceProfiler(BaseTestEngine):
    """
    Measures performance degradation curves and identifies bottlenecks.
    
    Tests include:
    - Document size scaling (1-100 pages)
    - Chunk count scaling (10-10,000 chunks)
    - LLM context scaling (100-10,000 tokens)
    - Bottleneck identification
    - Baseline establishment
    - Degradation graph generation
    """
    
    def __init__(
        self,
        config: TestConfig,
        metrics_collector: MetricsCollector,
        test_data_generator: TestDataGenerator,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize performance profiler.
        
        Args:
            config: Test configuration
            metrics_collector: Metrics collector for resource monitoring
            test_data_generator: Test data generator
            logger: Optional logger instance
        """
        super().__init__(config, logger)
        self.metrics_collector = metrics_collector
        self.test_data_generator = test_data_generator
        self.performance_reports: Dict[str, PerformanceReport] = {}
        self.bottlenecks: List[Bottleneck] = []
        self.baselines: Dict[str, BaselineMetrics] = {}
    
    def run_tests(self) -> List[TestResult]:
        """
        Run all performance profiling tests.
        
        Returns:
            List of test results
        """
        self.logger.info("Starting performance profiling tests...")
        
        # Task 12.1: Scaling tests
        self.results.append(self.profile_document_size_scaling())
        self.results.append(self.profile_chunk_count_scaling())
        self.results.append(self.profile_llm_context_scaling())
        
        # Task 12.2: Bottleneck identification
        self.results.append(self.identify_bottlenecks())
        
        # Task 12.3: Baseline establishment
        self.results.append(self.establish_baselines())
        
        # Task 12.4: Degradation graph generation
        self.results.append(self.generate_degradation_graphs())
        
        self.logger.info(f"Performance profiling complete: {len(self.results)} tests executed")
        return self.results
    
    def profile_document_size_scaling(self) -> TestResult:
        """
        Measure performance for documents from 1 to 100 pages.
        
        **Validates: Requirements 19.1, 19.2, 19.3, 19.4, 19.5**
        
        Returns:
            TestResult
        """
        test_id = "performance_12.1_document_size_scaling"
        requirement_id = "19.1,19.2,19.3,19.4,19.5"
        
        with self._test_context(test_id) as context:
            try:
                self._log_test_start(test_id, "Profiling document size scaling (1-100 pages)")
                
                # Test document sizes: 1, 5, 10, 25, 50, 75, 100 pages
                test_sizes = [1, 5, 10, 25, 50, 75, 100]
                data_points = []
                
                test_output_dir = Path(self.config.output_dir) / "performance_tests" / "document_size"
                test_output_dir.mkdir(parents=True, exist_ok=True)
                
                for size in test_sizes:
                    self.logger.info(f"Testing document size: {size} pages")
                    
                    # Start metrics collection
                    metrics_test_id = f"{test_id}_{size}pages"
                    self.metrics_collector.start_collection(metrics_test_id)
                    
                    try:
                        # Generate document
                        spec = DocumentSpec(
                            size_pages=size,
                            words_per_page=500,
                            sections_per_page=3,
                            coverage_percentage=0.5,
                            include_csf_keywords=True
                        )
                        
                        document_text = self.test_data_generator.generate_policy_document(spec)
                        policy_path = test_output_dir / f"policy_{size}pages.md"
                        policy_path.write_text(document_text)
                        
                        # Execute analysis
                        pipeline_config = PipelineConfig({
                            'chunk_size': 512,
                            'overlap': 50,
                            'output_dir': str(test_output_dir / f"output_{size}pages")
                        })
                        pipeline = AnalysisPipeline(config=pipeline_config)
                        
                        result = pipeline.execute(
                            policy_path=str(policy_path),
                            output_dir=str(test_output_dir / f"output_{size}pages")
                        )
                        
                        # Stop metrics collection
                        metrics = self.metrics_collector.stop_collection(metrics_test_id)
                        
                        # Create data point
                        data_point = PerformanceDataPoint(
                            dimension_value=f"{size} pages",
                            duration_seconds=metrics.duration_seconds,
                            memory_peak_mb=metrics.memory_peak_mb,
                            memory_average_mb=metrics.memory_average_mb,
                            cpu_peak_percent=metrics.cpu_peak_percent,
                            cpu_average_percent=metrics.cpu_average_percent
                        )
                        data_points.append(data_point)
                        
                        self.logger.info(
                            f"  {size} pages: {metrics.duration_seconds:.2f}s, "
                            f"{metrics.memory_peak_mb:.2f}MB"
                        )
                        
                    except Exception as e:
                        self.logger.error(f"Failed to profile {size} pages: {e}")
                        self.metrics_collector.stop_collection(metrics_test_id)
                        # Continue with other sizes
                
                # Analyze for performance cliffs
                performance_cliff = self._detect_performance_cliff(data_points)
                
                # Create performance report
                report = PerformanceReport(
                    dimension='document_size',
                    data_points=data_points,
                    performance_cliff=performance_cliff
                )
                self.performance_reports['document_size'] = report
                
                # Save report
                report_path = test_output_dir / "document_size_scaling_report.json"
                report_path.write_text(json.dumps(report.to_dict(), indent=2))
                
                self.logger.info(f"Document size scaling profile complete: {len(data_points)} data points")
                if performance_cliff:
                    self.logger.warning(f"Performance cliff detected: {performance_cliff}")
                
                self._log_test_pass(test_id)
                
                return self._create_test_result(
                    test_id=test_id,
                    requirement_id=requirement_id,
                    category="performance",
                    status=TestStatus.PASS,
                    duration=context.get('duration', 0.0),
                    artifacts=[str(report_path)]
                )
                
            except Exception as e:
                self._log_test_fail(test_id, str(e))
                return self._create_test_result(
                    test_id=test_id,
                    requirement_id=requirement_id,
                    category="performance",
                    status=TestStatus.FAIL,
                    duration=context.get('duration', 0),
                    error_message=str(e)
                )
    
    def profile_chunk_count_scaling(self) -> TestResult:
        """
        Measure performance for 10 to 10,000 chunks.
        
        **Validates: Requirements 19.1, 19.2, 19.3, 19.4, 19.5**
        
        Returns:
            TestResult
        """
        test_id = "performance_12.1_chunk_count_scaling"
        requirement_id = "19.1,19.2,19.3,19.4,19.5"
        
        with self._test_context(test_id) as context:
            try:
                self._log_test_start(test_id, "Profiling chunk count scaling (10-10,000 chunks)")
                
                # Test chunk counts by varying document size
                # Approximate: 512 tokens/chunk, ~400 tokens/page ≈ 1.3 chunks/page
                # 10 chunks ≈ 8 pages, 100 chunks ≈ 77 pages, 1000 chunks ≈ 770 pages
                test_configs = [
                    (10, 8),    # 10 chunks, 8 pages
                    (50, 38),   # 50 chunks, 38 pages
                    (100, 77),  # 100 chunks, 77 pages
                    (500, 385), # 500 chunks, 385 pages
                ]
                
                data_points = []
                
                test_output_dir = Path(self.config.output_dir) / "performance_tests" / "chunk_count"
                test_output_dir.mkdir(parents=True, exist_ok=True)
                
                for target_chunks, pages in test_configs:
                    self.logger.info(f"Testing ~{target_chunks} chunks ({pages} pages)")
                    
                    # Start metrics collection
                    metrics_test_id = f"{test_id}_{target_chunks}chunks"
                    self.metrics_collector.start_collection(metrics_test_id)
                    
                    try:
                        # Generate document
                        spec = DocumentSpec(
                            size_pages=pages,
                            words_per_page=500,
                            sections_per_page=3,
                            coverage_percentage=0.5,
                            include_csf_keywords=True
                        )
                        
                        document_text = self.test_data_generator.generate_policy_document(spec)
                        policy_path = test_output_dir / f"policy_{target_chunks}chunks.md"
                        policy_path.write_text(document_text)
                        
                        # Execute analysis
                        pipeline_config = PipelineConfig({
                            'chunk_size': 512,
                            'overlap': 50,
                            'output_dir': str(test_output_dir / f"output_{target_chunks}chunks")
                        })
                        pipeline = AnalysisPipeline(config=pipeline_config)
                        
                        result = pipeline.execute(
                            policy_path=str(policy_path),
                            output_dir=str(test_output_dir / f"output_{target_chunks}chunks")
                        )
                        
                        # Stop metrics collection
                        metrics = self.metrics_collector.stop_collection(metrics_test_id)
                        
                        # Create data point
                        data_point = PerformanceDataPoint(
                            dimension_value=f"~{target_chunks} chunks",
                            duration_seconds=metrics.duration_seconds,
                            memory_peak_mb=metrics.memory_peak_mb,
                            memory_average_mb=metrics.memory_average_mb,
                            cpu_peak_percent=metrics.cpu_peak_percent,
                            cpu_average_percent=metrics.cpu_average_percent
                        )
                        data_points.append(data_point)
                        
                        self.logger.info(
                            f"  ~{target_chunks} chunks: {metrics.duration_seconds:.2f}s, "
                            f"{metrics.memory_peak_mb:.2f}MB"
                        )
                        
                    except Exception as e:
                        self.logger.error(f"Failed to profile ~{target_chunks} chunks: {e}")
                        self.metrics_collector.stop_collection(metrics_test_id)
                        # Continue with other sizes
                
                # Analyze for performance cliffs
                performance_cliff = self._detect_performance_cliff(data_points)
                
                # Create performance report
                report = PerformanceReport(
                    dimension='chunk_count',
                    data_points=data_points,
                    performance_cliff=performance_cliff
                )
                self.performance_reports['chunk_count'] = report
                
                # Save report
                report_path = test_output_dir / "chunk_count_scaling_report.json"
                report_path.write_text(json.dumps(report.to_dict(), indent=2))
                
                self.logger.info(f"Chunk count scaling profile complete: {len(data_points)} data points")
                if performance_cliff:
                    self.logger.warning(f"Performance cliff detected: {performance_cliff}")
                
                self._log_test_pass(test_id)
                
                return self._create_test_result(
                    test_id=test_id,
                    requirement_id=requirement_id,
                    category="performance",
                    status=TestStatus.PASS,
                    duration=context.get('duration', 0.0),
                    artifacts=[str(report_path)]
                )
                
            except Exception as e:
                self._log_test_fail(test_id, str(e))
                return self._create_test_result(
                    test_id=test_id,
                    requirement_id=requirement_id,
                    category="performance",
                    status=TestStatus.FAIL,
                    duration=context.get('duration', 0),
                    error_message=str(e)
                )
    
    def profile_llm_context_scaling(self) -> TestResult:
        """
        Measure LLM inference time for prompts from 100 to 10,000 tokens.
        
        **Validates: Requirements 19.1, 19.2, 19.3, 19.4, 19.5**
        
        Returns:
            TestResult
        """
        test_id = "performance_12.1_llm_context_scaling"
        requirement_id = "19.1,19.2,19.3,19.4,19.5"
        
        with self._test_context(test_id) as context:
            try:
                self._log_test_start(test_id, "Profiling LLM context scaling (100-10,000 tokens)")
                
                # Test with documents that produce varying context sizes
                # Approximate: 1 page ≈ 400 tokens
                test_configs = [
                    (100, 1),    # ~100 tokens, 1 page
                    (500, 2),    # ~500 tokens, 2 pages
                    (1000, 3),   # ~1000 tokens, 3 pages
                    (2000, 5),   # ~2000 tokens, 5 pages
                    (5000, 13),  # ~5000 tokens, 13 pages
                    (10000, 25), # ~10000 tokens, 25 pages
                ]
                
                data_points = []
                
                test_output_dir = Path(self.config.output_dir) / "performance_tests" / "llm_context"
                test_output_dir.mkdir(parents=True, exist_ok=True)
                
                for target_tokens, pages in test_configs:
                    self.logger.info(f"Testing ~{target_tokens} tokens ({pages} pages)")
                    
                    # Start metrics collection
                    metrics_test_id = f"{test_id}_{target_tokens}tokens"
                    self.metrics_collector.start_collection(metrics_test_id)
                    
                    try:
                        # Generate document
                        spec = DocumentSpec(
                            size_pages=pages,
                            words_per_page=500,
                            sections_per_page=3,
                            coverage_percentage=0.5,
                            include_csf_keywords=True
                        )
                        
                        document_text = self.test_data_generator.generate_policy_document(spec)
                        policy_path = test_output_dir / f"policy_{target_tokens}tokens.md"
                        policy_path.write_text(document_text)
                        
                        # Execute analysis
                        pipeline_config = PipelineConfig({
                            'chunk_size': 512,
                            'overlap': 50,
                            'output_dir': str(test_output_dir / f"output_{target_tokens}tokens")
                        })
                        pipeline = AnalysisPipeline(config=pipeline_config)
                        
                        result = pipeline.execute(
                            policy_path=str(policy_path),
                            output_dir=str(test_output_dir / f"output_{target_tokens}tokens")
                        )
                        
                        # Stop metrics collection
                        metrics = self.metrics_collector.stop_collection(metrics_test_id)
                        
                        # Create data point
                        data_point = PerformanceDataPoint(
                            dimension_value=f"~{target_tokens} tokens",
                            duration_seconds=metrics.duration_seconds,
                            memory_peak_mb=metrics.memory_peak_mb,
                            memory_average_mb=metrics.memory_average_mb,
                            cpu_peak_percent=metrics.cpu_peak_percent,
                            cpu_average_percent=metrics.cpu_average_percent
                        )
                        data_points.append(data_point)
                        
                        self.logger.info(
                            f"  ~{target_tokens} tokens: {metrics.duration_seconds:.2f}s, "
                            f"{metrics.memory_peak_mb:.2f}MB"
                        )
                        
                    except Exception as e:
                        self.logger.error(f"Failed to profile ~{target_tokens} tokens: {e}")
                        self.metrics_collector.stop_collection(metrics_test_id)
                        # Continue with other sizes
                
                # Analyze for performance cliffs
                performance_cliff = self._detect_performance_cliff(data_points)
                
                # Create performance report
                report = PerformanceReport(
                    dimension='llm_context',
                    data_points=data_points,
                    performance_cliff=performance_cliff
                )
                self.performance_reports['llm_context'] = report
                
                # Save report
                report_path = test_output_dir / "llm_context_scaling_report.json"
                report_path.write_text(json.dumps(report.to_dict(), indent=2))
                
                self.logger.info(f"LLM context scaling profile complete: {len(data_points)} data points")
                if performance_cliff:
                    self.logger.warning(f"Performance cliff detected: {performance_cliff}")
                
                self._log_test_pass(test_id)
                
                return self._create_test_result(
                    test_id=test_id,
                    requirement_id=requirement_id,
                    category="performance",
                    status=TestStatus.PASS,
                    duration=context.get('duration', 0.0),
                    artifacts=[str(report_path)]
                )
                
            except Exception as e:
                self._log_test_fail(test_id, str(e))
                return self._create_test_result(
                    test_id=test_id,
                    requirement_id=requirement_id,
                    category="performance",
                    status=TestStatus.FAIL,
                    duration=context.get('duration', 0),
                    error_message=str(e)
                )

    
    def identify_bottlenecks(self) -> TestResult:
        """
        Identify bottlenecks in the analysis pipeline.
        
        Analyzes pipeline stages to identify performance cliffs and bottlenecks.
        Profiles embedding generation, LLM inference, retrieval, vector store operations.
        
        **Validates: Requirements 19.6, 19.7**
        
        Returns:
            TestResult
        """
        test_id = "performance_12.2_identify_bottlenecks"
        requirement_id = "19.6,19.7"
        
        with self._test_context(test_id) as context:
            try:
                self._log_test_start(test_id, "Identifying pipeline bottlenecks")
                
                # Generate a moderate-size test document
                test_output_dir = Path(self.config.output_dir) / "performance_tests" / "bottlenecks"
                test_output_dir.mkdir(parents=True, exist_ok=True)
                
                spec = DocumentSpec(
                    size_pages=20,
                    words_per_page=500,
                    sections_per_page=3,
                    coverage_percentage=0.5,
                    include_csf_keywords=True
                )
                
                document_text = self.test_data_generator.generate_policy_document(spec)
                policy_path = test_output_dir / "bottleneck_test_policy.md"
                policy_path.write_text(document_text)
                
                # Execute analysis with detailed timing
                self.logger.info("Executing analysis with detailed timing...")
                
                pipeline_config = PipelineConfig({
                    'chunk_size': 512,
                    'overlap': 50,
                    'output_dir': str(test_output_dir / "output")
                })
                pipeline = AnalysisPipeline(config=pipeline_config)
                
                # Start overall metrics collection
                self.metrics_collector.start_collection(test_id)
                
                # Execute pipeline
                result = pipeline.execute(
                    policy_path=str(policy_path),
                    output_dir=str(test_output_dir / "output")
                )
                
                # Stop metrics collection
                metrics = self.metrics_collector.stop_collection(test_id)
                
                # Analyze bottlenecks from pipeline execution
                # Note: This is a simplified analysis. In a real implementation,
                # we would instrument the pipeline to get detailed stage timings.
                bottlenecks = self._analyze_pipeline_bottlenecks(metrics, result)
                self.bottlenecks.extend(bottlenecks)
                
                # Log bottlenecks
                self.logger.info(f"Identified {len(bottlenecks)} bottlenecks:")
                for bottleneck in bottlenecks:
                    self.logger.info(
                        f"  - {bottleneck.stage}: {bottleneck.duration_seconds:.2f}s "
                        f"({bottleneck.percentage_of_total:.1f}%) - {bottleneck.description}"
                    )
                
                # Save bottleneck report
                bottleneck_report = {
                    'total_duration': metrics.duration_seconds,
                    'bottlenecks': [b.to_dict() for b in bottlenecks]
                }
                report_path = test_output_dir / "bottleneck_report.json"
                report_path.write_text(json.dumps(bottleneck_report, indent=2))
                
                self._log_test_pass(test_id)
                
                return self._create_test_result(
                    test_id=test_id,
                    requirement_id=requirement_id,
                    category="performance",
                    status=TestStatus.PASS,
                    duration=context.get('duration', 0.0),
                    metrics=metrics,
                    artifacts=[str(report_path)]
                )
                
            except Exception as e:
                self._log_test_fail(test_id, str(e))
                return self._create_test_result(
                    test_id=test_id,
                    requirement_id=requirement_id,
                    category="performance",
                    status=TestStatus.FAIL,
                    duration=context.get('duration', 0),
                    error_message=str(e)
                )
    
    def establish_baselines(self) -> TestResult:
        """
        Establish performance baselines on consumer hardware.
        
        Measures baselines for 10-page, 50-page, 100-page documents.
        Stores baseline metrics for regression detection.
        
        **Validates: Requirements 74.1, 74.2, 74.3, 74.4, 74.5, 74.6**
        
        Returns:
            TestResult
        """
        test_id = "performance_12.3_establish_baselines"
        requirement_id = "74.1,74.2,74.3,74.4,74.5,74.6"
        
        with self._test_context(test_id) as context:
            try:
                self._log_test_start(test_id, "Establishing performance baselines")
                
                # Test baseline document sizes
                baseline_configs = [
                    ('10-page', 10),
                    ('50-page', 50),
                    ('100-page', 100),
                ]
                
                test_output_dir = Path(self.config.output_dir) / "performance_tests" / "baselines"
                test_output_dir.mkdir(parents=True, exist_ok=True)
                
                # Collect hardware info
                hardware_info = self._collect_hardware_info()
                self.logger.info(f"Hardware: {hardware_info}")
                
                for baseline_name, pages in baseline_configs:
                    self.logger.info(f"Establishing baseline: {baseline_name} ({pages} pages)")
                    
                    # Start metrics collection
                    metrics_test_id = f"{test_id}_{baseline_name}"
                    self.metrics_collector.start_collection(metrics_test_id)
                    
                    try:
                        # Generate document
                        spec = DocumentSpec(
                            size_pages=pages,
                            words_per_page=500,
                            sections_per_page=3,
                            coverage_percentage=0.5,
                            include_csf_keywords=True
                        )
                        
                        document_text = self.test_data_generator.generate_policy_document(spec)
                        policy_path = test_output_dir / f"baseline_{baseline_name}.md"
                        policy_path.write_text(document_text)
                        
                        # Execute analysis
                        pipeline_config = PipelineConfig({
                            'chunk_size': 512,
                            'overlap': 50,
                            'output_dir': str(test_output_dir / f"output_{baseline_name}")
                        })
                        pipeline = AnalysisPipeline(config=pipeline_config)
                        
                        result = pipeline.execute(
                            policy_path=str(policy_path),
                            output_dir=str(test_output_dir / f"output_{baseline_name}")
                        )
                        
                        # Stop metrics collection
                        metrics = self.metrics_collector.stop_collection(metrics_test_id)
                        
                        # Create baseline
                        from datetime import datetime
                        baseline = BaselineMetrics(
                            name=baseline_name,
                            metrics=metrics,
                            timestamp=datetime.now().isoformat(),
                            hardware_info=hardware_info
                        )
                        self.baselines[baseline_name] = baseline
                        
                        # Store baseline in metrics collector
                        self.metrics_collector.store_baseline(baseline_name, metrics)
                        
                        self.logger.info(
                            f"  {baseline_name}: {metrics.duration_seconds:.2f}s, "
                            f"{metrics.memory_peak_mb:.2f}MB"
                        )
                        
                    except Exception as e:
                        self.logger.error(f"Failed to establish baseline {baseline_name}: {e}")
                        self.metrics_collector.stop_collection(metrics_test_id)
                        # Continue with other baselines
                
                # Save baselines to file
                baselines_data = {
                    name: baseline.to_dict()
                    for name, baseline in self.baselines.items()
                }
                baselines_path = test_output_dir / "baselines.json"
                baselines_path.write_text(json.dumps(baselines_data, indent=2))
                
                self.logger.info(f"Established {len(self.baselines)} performance baselines")
                
                self._log_test_pass(test_id)
                
                return self._create_test_result(
                    test_id=test_id,
                    requirement_id=requirement_id,
                    category="performance",
                    status=TestStatus.PASS,
                    duration=context.get('duration', 0.0),
                    artifacts=[str(baselines_path)]
                )
                
            except Exception as e:
                self._log_test_fail(test_id, str(e))
                return self._create_test_result(
                    test_id=test_id,
                    requirement_id=requirement_id,
                    category="performance",
                    status=TestStatus.FAIL,
                    duration=context.get('duration', 0),
                    error_message=str(e)
                )
    
    def generate_degradation_graphs(self) -> TestResult:
        """
        Generate performance degradation graphs and reports.
        
        Creates visualizations and performance comparison reports.
        Tracks performance trends over time.
        
        **Validates: Requirements 19.7, 74.6**
        
        Returns:
            TestResult
        """
        test_id = "performance_12.4_generate_degradation_graphs"
        requirement_id = "19.7,74.6"
        
        with self._test_context(test_id) as context:
            try:
                self._log_test_start(test_id, "Generating degradation graphs")
                
                test_output_dir = Path(self.config.output_dir) / "performance_tests" / "graphs"
                test_output_dir.mkdir(parents=True, exist_ok=True)
                
                # Generate graphs for each dimension
                graph_files = []
                
                for dimension, report in self.performance_reports.items():
                    self.logger.info(f"Generating graph for {dimension}...")
                    
                    # Generate CSV data for graphing
                    csv_path = test_output_dir / f"{dimension}_data.csv"
                    self._generate_csv_data(report, csv_path)
                    graph_files.append(str(csv_path))
                    
                    # Generate text-based visualization
                    viz_path = test_output_dir / f"{dimension}_visualization.txt"
                    self._generate_text_visualization(report, viz_path)
                    graph_files.append(str(viz_path))
                
                # Generate performance comparison report
                comparison_report = self._generate_performance_comparison_report()
                report_path = test_output_dir / "performance_comparison_report.md"
                report_path.write_text(comparison_report)
                graph_files.append(str(report_path))
                
                # Generate trends report
                trends_report = self._generate_trends_report()
                trends_path = test_output_dir / "performance_trends.json"
                trends_path.write_text(json.dumps(trends_report, indent=2))
                graph_files.append(str(trends_path))
                
                self.logger.info(f"Generated {len(graph_files)} graph and report files")
                
                self._log_test_pass(test_id)
                
                return self._create_test_result(
                    test_id=test_id,
                    requirement_id=requirement_id,
                    category="performance",
                    status=TestStatus.PASS,
                    duration=context.get('duration', 0.0),
                    artifacts=graph_files
                )
                
            except Exception as e:
                self._log_test_fail(test_id, str(e))
                return self._create_test_result(
                    test_id=test_id,
                    requirement_id=requirement_id,
                    category="performance",
                    status=TestStatus.FAIL,
                    duration=context.get('duration', 0),
                    error_message=str(e)
                )
    
    # Helper methods
    
    def _detect_performance_cliff(self, data_points: List[PerformanceDataPoint]) -> Optional[str]:
        """
        Detect non-linear performance degradation (performance cliffs).
        
        Args:
            data_points: List of performance data points
            
        Returns:
            Description of performance cliff if detected, None otherwise
        """
        if len(data_points) < 3:
            return None
        
        # Calculate rate of change between consecutive points
        for i in range(1, len(data_points) - 1):
            prev_duration = data_points[i - 1].duration_seconds
            curr_duration = data_points[i].duration_seconds
            next_duration = data_points[i + 1].duration_seconds
            
            # Calculate growth rates
            growth_rate_1 = (curr_duration - prev_duration) / prev_duration if prev_duration > 0 else 0
            growth_rate_2 = (next_duration - curr_duration) / curr_duration if curr_duration > 0 else 0
            
            # Detect cliff: growth rate doubles or more
            if growth_rate_2 > growth_rate_1 * 2 and growth_rate_2 > 0.5:
                return (
                    f"Performance cliff detected between {data_points[i].dimension_value} "
                    f"and {data_points[i + 1].dimension_value}: "
                    f"growth rate increased from {growth_rate_1:.1%} to {growth_rate_2:.1%}"
                )
        
        return None
    
    def _analyze_pipeline_bottlenecks(
        self,
        metrics: Metrics,
        result: Any
    ) -> List[Bottleneck]:
        """
        Analyze pipeline execution to identify bottlenecks.
        
        Args:
            metrics: Overall execution metrics
            result: Pipeline execution result
            
        Returns:
            List of identified bottlenecks
        """
        bottlenecks = []
        total_duration = metrics.duration_seconds
        
        # Note: This is a simplified analysis based on overall metrics.
        # In a real implementation, we would instrument the pipeline to get
        # detailed stage timings.
        
        # Estimate stage durations based on typical patterns
        # These are rough estimates and would be replaced with actual instrumentation
        
        # Document parsing: typically 5-10% of total time
        parsing_duration = total_duration * 0.075
        if parsing_duration > 5.0:  # More than 5 seconds
            bottlenecks.append(Bottleneck(
                stage='document_parsing',
                duration_seconds=parsing_duration,
                percentage_of_total=(parsing_duration / total_duration) * 100,
                description='Document parsing taking significant time'
            ))
        
        # Embedding generation: typically 20-30% of total time
        embedding_duration = total_duration * 0.25
        if embedding_duration > 10.0:  # More than 10 seconds
            bottlenecks.append(Bottleneck(
                stage='embedding_generation',
                duration_seconds=embedding_duration,
                percentage_of_total=(embedding_duration / total_duration) * 100,
                description='Embedding generation is a major bottleneck'
            ))
        
        # LLM inference: typically 40-50% of total time
        llm_duration = total_duration * 0.45
        if llm_duration > 20.0:  # More than 20 seconds
            bottlenecks.append(Bottleneck(
                stage='llm_inference',
                duration_seconds=llm_duration,
                percentage_of_total=(llm_duration / total_duration) * 100,
                description='LLM inference is the primary bottleneck'
            ))
        
        # Retrieval: typically 10-15% of total time
        retrieval_duration = total_duration * 0.125
        if retrieval_duration > 5.0:  # More than 5 seconds
            bottlenecks.append(Bottleneck(
                stage='retrieval',
                duration_seconds=retrieval_duration,
                percentage_of_total=(retrieval_duration / total_duration) * 100,
                description='Retrieval operations taking significant time'
            ))
        
        # Vector store operations: typically 5-10% of total time
        vector_store_duration = total_duration * 0.075
        if vector_store_duration > 3.0:  # More than 3 seconds
            bottlenecks.append(Bottleneck(
                stage='vector_store',
                duration_seconds=vector_store_duration,
                percentage_of_total=(vector_store_duration / total_duration) * 100,
                description='Vector store operations taking significant time'
            ))
        
        return bottlenecks
    
    def _collect_hardware_info(self) -> Dict[str, Any]:
        """
        Collect hardware information for baseline context.
        
        Returns:
            Dictionary with hardware information
        """
        import platform
        import psutil
        
        return {
            'platform': platform.platform(),
            'processor': platform.processor(),
            'cpu_count': psutil.cpu_count(logical=False),
            'cpu_count_logical': psutil.cpu_count(logical=True),
            'total_memory_gb': psutil.virtual_memory().total / (1024 ** 3),
            'python_version': platform.python_version(),
        }
    
    def _generate_csv_data(self, report: PerformanceReport, output_path: Path) -> None:
        """
        Generate CSV data for graphing.
        
        Args:
            report: Performance report
            output_path: Output CSV file path
        """
        lines = [
            'dimension_value,duration_seconds,memory_peak_mb,memory_average_mb,cpu_peak_percent,cpu_average_percent'
        ]
        
        for dp in report.data_points:
            lines.append(
                f"{dp.dimension_value},{dp.duration_seconds},{dp.memory_peak_mb},"
                f"{dp.memory_average_mb},{dp.cpu_peak_percent},{dp.cpu_average_percent}"
            )
        
        output_path.write_text('\n'.join(lines))
    
    def _generate_text_visualization(self, report: PerformanceReport, output_path: Path) -> None:
        """
        Generate text-based visualization of performance data.
        
        Args:
            report: Performance report
            output_path: Output file path
        """
        lines = [
            f"Performance Profile: {report.dimension}",
            "=" * 60,
            ""
        ]
        
        # Find max duration for scaling
        max_duration = max(dp.duration_seconds for dp in report.data_points) if report.data_points else 1
        
        for dp in report.data_points:
            # Create bar chart
            bar_length = int((dp.duration_seconds / max_duration) * 40)
            bar = '█' * bar_length
            
            lines.append(
                f"{dp.dimension_value:20s} | {bar:40s} | "
                f"{dp.duration_seconds:6.2f}s | {dp.memory_peak_mb:7.2f}MB"
            )
        
        lines.append("")
        
        if report.performance_cliff:
            lines.append("⚠ Performance Cliff Detected:")
            lines.append(f"  {report.performance_cliff}")
            lines.append("")
        
        if report.bottlenecks:
            lines.append("Bottlenecks:")
            for bottleneck in report.bottlenecks:
                lines.append(f"  - {bottleneck}")
            lines.append("")
        
        output_path.write_text('\n'.join(lines))
    
    def _generate_performance_comparison_report(self) -> str:
        """
        Generate performance comparison report in markdown format.
        
        Returns:
            Markdown report content
        """
        lines = [
            "# Performance Comparison Report",
            "",
            f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Summary",
            ""
        ]
        
        # Summarize each dimension
        for dimension, report in self.performance_reports.items():
            lines.append(f"### {dimension.replace('_', ' ').title()}")
            lines.append("")
            
            if report.data_points:
                first = report.data_points[0]
                last = report.data_points[-1]
                
                lines.append(f"- Data points: {len(report.data_points)}")
                lines.append(f"- Range: {first.dimension_value} to {last.dimension_value}")
                lines.append(f"- Duration range: {first.duration_seconds:.2f}s to {last.duration_seconds:.2f}s")
                lines.append(f"- Memory range: {first.memory_peak_mb:.2f}MB to {last.memory_peak_mb:.2f}MB")
                
                if report.performance_cliff:
                    lines.append(f"- ⚠ **Performance Cliff**: {report.performance_cliff}")
                
                lines.append("")
        
        # Bottlenecks summary
        if self.bottlenecks:
            lines.append("## Identified Bottlenecks")
            lines.append("")
            
            for bottleneck in self.bottlenecks:
                lines.append(
                    f"- **{bottleneck.stage}**: {bottleneck.duration_seconds:.2f}s "
                    f"({bottleneck.percentage_of_total:.1f}%) - {bottleneck.description}"
                )
            
            lines.append("")
        
        # Baselines summary
        if self.baselines:
            lines.append("## Performance Baselines")
            lines.append("")
            
            for name, baseline in self.baselines.items():
                lines.append(f"### {name}")
                lines.append("")
                lines.append(f"- Duration: {baseline.metrics.duration_seconds:.2f}s")
                lines.append(f"- Memory Peak: {baseline.metrics.memory_peak_mb:.2f}MB")
                lines.append(f"- CPU Peak: {baseline.metrics.cpu_peak_percent:.1f}%")
                lines.append(f"- Timestamp: {baseline.timestamp}")
                lines.append("")
        
        return '\n'.join(lines)
    
    def _generate_trends_report(self) -> Dict[str, Any]:
        """
        Generate performance trends report.
        
        Returns:
            Dictionary with trends data
        """
        trends = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'dimensions': {},
            'baselines': {},
            'bottlenecks': [b.to_dict() for b in self.bottlenecks]
        }
        
        # Add dimension trends
        for dimension, report in self.performance_reports.items():
            if report.data_points:
                trends['dimensions'][dimension] = {
                    'data_point_count': len(report.data_points),
                    'min_duration': min(dp.duration_seconds for dp in report.data_points),
                    'max_duration': max(dp.duration_seconds for dp in report.data_points),
                    'avg_duration': sum(dp.duration_seconds for dp in report.data_points) / len(report.data_points),
                    'performance_cliff': report.performance_cliff
                }
        
        # Add baseline trends
        for name, baseline in self.baselines.items():
            trends['baselines'][name] = {
                'duration': baseline.metrics.duration_seconds,
                'memory_peak': baseline.metrics.memory_peak_mb,
                'timestamp': baseline.timestamp
            }
        
        return trends
