"""
Master Test Runner for Extreme Testing Framework

This module orchestrates execution of all test categories and generates
comprehensive test reports.
"""

import logging
import time
from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime

from .config import TestConfig
from .models import (
    TestResult, TestReport, CategoryReport, RequirementReport,
    TestStatus, BreakingPoint, FailureMode
)


class MasterTestRunner:
    """Orchestrates execution of all test categories."""
    
    def __init__(self, config: TestConfig):
        """
        Initialize master test runner.
        
        Args:
            config: Test configuration
        """
        self.config = config
        self.logger = self._setup_logger()
        self.test_engines: Dict[str, Any] = {}
        self.results: List[TestResult] = []
    
    def _setup_logger(self) -> logging.Logger:
        """Set up logging for test execution."""
        logger = logging.getLogger("MasterTestRunner")
        logger.setLevel(logging.DEBUG if self.config.verbose else logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG if self.config.verbose else logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler
        log_dir = Path(self.config.output_dir) / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    def initialize_engines(self):
        """Initialize all test engines based on configuration."""
        self.logger.info("Initializing test engines...")
        
        # Import test engines dynamically to avoid circular imports
        # Engines will be initialized in subsequent tasks
        
        for category in self.config.categories:
            self.logger.info(f"  - {category} engine (placeholder)")
        
        self.logger.info("Test engines initialized")
    
    def run_all_tests(self) -> TestReport:
        """
        Execute all test categories and return comprehensive report.
        
        Returns:
            TestReport with all results
        """
        self.logger.info("=" * 80)
        self.logger.info("EXTREME TESTING FRAMEWORK - STARTING TEST EXECUTION")
        self.logger.info("=" * 80)
        
        start_time = time.time()
        
        # Initialize engines
        self.initialize_engines()
        
        # Execute tests by category
        category_results = {}
        for category in self.config.categories:
            self.logger.info(f"\n{'=' * 80}")
            self.logger.info(f"EXECUTING {category.upper()} TESTS")
            self.logger.info(f"{'=' * 80}\n")
            
            category_report = self.run_category(category)
            category_results[category] = category_report
            
            # Check fail-fast
            if self.config.fail_fast and category_report.failed > 0:
                self.logger.warning("Fail-fast enabled, stopping execution")
                break
        
        # Aggregate results
        duration = time.time() - start_time
        report = self._generate_report(category_results, duration)
        
        self.logger.info("\n" + "=" * 80)
        self.logger.info("TEST EXECUTION COMPLETE")
        self.logger.info("=" * 80)
        self.logger.info(f"Total tests: {report.total_tests}")
        self.logger.info(f"Passed: {report.passed}")
        self.logger.info(f"Failed: {report.failed}")
        self.logger.info(f"Skipped: {report.skipped}")
        self.logger.info(f"Errors: {report.errors}")
        self.logger.info(f"Duration: {duration:.2f}s")
        self.logger.info("=" * 80)
        
        return report
    
    def run_category(self, category: str) -> CategoryReport:
        """
        Execute specific test category.
        
        Args:
            category: Test category name
            
        Returns:
            CategoryReport with results
        """
        start_time = time.time()
        
        # Placeholder for actual engine execution
        # Engines will be implemented in subsequent tasks
        self.logger.info(f"Running {category} tests (placeholder)")
        
        test_results = []
        
        # Create category report
        duration = time.time() - start_time
        passed = sum(1 for r in test_results if r.status == TestStatus.PASS)
        failed = sum(1 for r in test_results if r.status == TestStatus.FAIL)
        skipped = sum(1 for r in test_results if r.status == TestStatus.SKIP)
        errors = sum(1 for r in test_results if r.status == TestStatus.ERROR)
        
        return CategoryReport(
            category=category,
            total_tests=len(test_results),
            passed=passed,
            failed=failed,
            skipped=skipped,
            errors=errors,
            duration_seconds=duration,
            test_results=test_results
        )
    
    def run_requirement(self, requirement_id: str) -> RequirementReport:
        """
        Execute tests for specific requirement.
        
        Args:
            requirement_id: Requirement identifier
            
        Returns:
            RequirementReport with results
        """
        self.logger.info(f"Running tests for requirement: {requirement_id}")
        
        # Filter results by requirement
        test_results = [r for r in self.results if r.requirement_id == requirement_id]
        
        passed = sum(1 for r in test_results if r.status == TestStatus.PASS)
        failed = sum(1 for r in test_results if r.status == TestStatus.FAIL)
        
        return RequirementReport(
            requirement_id=requirement_id,
            total_tests=len(test_results),
            passed=passed,
            failed=failed,
            test_results=test_results
        )
    
    def _generate_report(
        self,
        category_results: Dict[str, CategoryReport],
        duration: float
    ) -> TestReport:
        """
        Generate comprehensive test report.
        
        Args:
            category_results: Results by category
            duration: Total execution duration
            
        Returns:
            TestReport
        """
        # Aggregate all test results
        all_results = []
        for category_report in category_results.values():
            all_results.extend(category_report.test_results)
        
        # Calculate totals
        total_tests = len(all_results)
        passed = sum(1 for r in all_results if r.status == TestStatus.PASS)
        failed = sum(1 for r in all_results if r.status == TestStatus.FAIL)
        skipped = sum(1 for r in all_results if r.status == TestStatus.SKIP)
        errors = sum(1 for r in all_results if r.status == TestStatus.ERROR)
        
        # Generate requirement reports
        requirement_results = {}
        unique_requirements = set(r.requirement_id for r in all_results)
        for req_id in unique_requirements:
            req_results = [r for r in all_results if r.requirement_id == req_id]
            req_passed = sum(1 for r in req_results if r.status == TestStatus.PASS)
            req_failed = sum(1 for r in req_results if r.status == TestStatus.FAIL)
            
            requirement_results[req_id] = RequirementReport(
                requirement_id=req_id,
                total_tests=len(req_results),
                passed=req_passed,
                failed=req_failed,
                test_results=req_results
            )
        
        return TestReport(
            execution_date=datetime.now(),
            total_tests=total_tests,
            passed=passed,
            failed=failed,
            skipped=skipped,
            errors=errors,
            duration_seconds=duration,
            category_results=category_results,
            requirement_results=requirement_results,
            breaking_points=[],  # Will be populated by test engines
            failure_modes=[],  # Will be populated by test engines
            performance_baselines={},  # Will be populated by performance profiler
            artifacts_dir=self.config.output_dir
        )
