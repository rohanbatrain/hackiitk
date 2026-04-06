"""
Unit Tests for TestReporter

Tests report generation with various results, HTML report formatting,
JSON report structure, and JUnit XML generation.

**Validates: Task 32.5**
"""

import pytest
import json
from pathlib import Path
from datetime import datetime
from tests.extreme.reporter import ExtremeTestReporter
from tests.extreme.models import (
    TestReport, CategoryReport, RequirementReport, TestResult,
    BreakingPoint, FailureMode, Metrics, TestStatus, FailureCategory
)


class TestTestReporter:
    """Unit tests for TestReporter component."""
    
    @pytest.fixture
    def output_dir(self, tmp_path):
        """Create temporary output directory."""
        return tmp_path / "test_reports"
    
    @pytest.fixture
    def reporter(self, output_dir):
        """Create ExtremeTestReporter instance."""
        return ExtremeTestReporter(str(output_dir))
    
    @pytest.fixture
    def sample_metrics(self):
        """Create sample metrics."""
        return Metrics(
            duration_seconds=10.5,
            memory_peak_mb=150.0,
            memory_average_mb=120.0,
            cpu_peak_percent=75.0,
            cpu_average_percent=50.0,
            disk_read_mb=25.0,
            disk_write_mb=15.0,
            file_handles_peak=20,
            thread_count_peak=8
        )
    
    @pytest.fixture
    def sample_test_result(self, sample_metrics):
        """Create sample test result."""
        return TestResult(
            test_id="test_001",
            requirement_id="1.1",
            category="stress",
            status=TestStatus.PASS,
            duration_seconds=5.0,
            metrics=sample_metrics
        )
    
    @pytest.fixture
    def sample_report(self, sample_test_result, sample_metrics):
        """Create sample test report."""
        category_report = CategoryReport(
            category="stress",
            total_tests=10,
            passed=8,
            failed=1,
            skipped=1,
            errors=0,
            duration_seconds=50.0,
            test_results=[sample_test_result]
        )
        
        requirement_report = RequirementReport(
            requirement_id="1.1",
            total_tests=5,
            passed=4,
            failed=1,
            test_results=[sample_test_result]
        )
        
        breaking_point = BreakingPoint(
            dimension="document_size",
            maximum_viable_value=100,
            failure_mode=FailureCategory.TIMEOUT,
            error_message="Analysis timed out after 30 minutes",
            metrics_at_failure=sample_metrics
        )
        
        failure_mode = FailureMode(
            failure_id="FM-001",
            category=FailureCategory.CRASH,
            trigger="Document with 10,000+ chunks",
            impact="System crashes with out of memory error",
            mitigation="Implement chunk batching and memory limits",
            discovered_date=datetime.now(),
            test_id="test_001"
        )
        
        return TestReport(
            execution_date=datetime.now(),
            total_tests=10,
            passed=8,
            failed=1,
            skipped=1,
            errors=0,
            duration_seconds=50.0,
            category_results={"stress": category_report},
            requirement_results={"1.1": requirement_report},
            breaking_points=[breaking_point],
            failure_modes=[failure_mode],
            performance_baselines={"baseline_10pages": sample_metrics},
            artifacts_dir="test_outputs/artifacts"
        )
    
    # Test report generation with various results
    
    def test_generate_report_creates_all_formats(self, reporter, sample_report):
        """Test report generation creates all required formats."""
        report_files = reporter.generate_report(sample_report)
        
        assert 'json' in report_files
        assert 'html' in report_files
        assert 'junit_xml' in report_files
        assert 'github_annotations' in report_files
        
        # Verify files exist
        for file_path in report_files.values():
            assert Path(file_path).exists()
    
    def test_generate_report_with_no_failures(self, reporter, sample_metrics):
        """Test report generation with all tests passing."""
        test_result = TestResult(
            test_id="test_pass",
            requirement_id="1.1",
            category="stress",
            status=TestStatus.PASS,
            duration_seconds=5.0,
            metrics=sample_metrics
        )
        
        category_report = CategoryReport(
            category="stress",
            total_tests=5,
            passed=5,
            failed=0,
            skipped=0,
            errors=0,
            duration_seconds=25.0,
            test_results=[test_result]
        )
        
        report = TestReport(
            execution_date=datetime.now(),
            total_tests=5,
            passed=5,
            failed=0,
            skipped=0,
            errors=0,
            duration_seconds=25.0,
            category_results={"stress": category_report},
            requirement_results={},
            breaking_points=[],
            failure_modes=[],
            performance_baselines={},
            artifacts_dir="test_outputs"
        )
        
        report_files = reporter.generate_report(report)
        
        assert Path(report_files['json']).exists()
        assert Path(report_files['html']).exists()
    
    def test_generate_report_with_all_failures(self, reporter, sample_metrics):
        """Test report generation with all tests failing."""
        test_result = TestResult(
            test_id="test_fail",
            requirement_id="1.1",
            category="chaos",
            status=TestStatus.FAIL,
            duration_seconds=5.0,
            error_message="Test failed due to timeout",
            metrics=sample_metrics
        )
        
        category_report = CategoryReport(
            category="chaos",
            total_tests=3,
            passed=0,
            failed=3,
            skipped=0,
            errors=0,
            duration_seconds=15.0,
            test_results=[test_result]
        )
        
        report = TestReport(
            execution_date=datetime.now(),
            total_tests=3,
            passed=0,
            failed=3,
            skipped=0,
            errors=0,
            duration_seconds=15.0,
            category_results={"chaos": category_report},
            requirement_results={},
            breaking_points=[],
            failure_modes=[],
            performance_baselines={},
            artifacts_dir="test_outputs"
        )
        
        report_files = reporter.generate_report(report)
        
        assert Path(report_files['json']).exists()
    
    def test_generate_report_with_mixed_statuses(self, reporter, sample_metrics):
        """Test report generation with mixed test statuses."""
        results = [
            TestResult("test_1", "1.1", "stress", TestStatus.PASS, 5.0, metrics=sample_metrics),
            TestResult("test_2", "1.2", "stress", TestStatus.FAIL, 5.0, error_message="Failed", metrics=sample_metrics),
            TestResult("test_3", "1.3", "stress", TestStatus.SKIP, 0.0, error_message="Skipped"),
            TestResult("test_4", "1.4", "stress", TestStatus.ERROR, 2.0, error_message="Error occurred")
        ]
        
        category_report = CategoryReport(
            category="stress",
            total_tests=4,
            passed=1,
            failed=1,
            skipped=1,
            errors=1,
            duration_seconds=12.0,
            test_results=results
        )
        
        report = TestReport(
            execution_date=datetime.now(),
            total_tests=4,
            passed=1,
            failed=1,
            skipped=1,
            errors=1,
            duration_seconds=12.0,
            category_results={"stress": category_report},
            requirement_results={},
            breaking_points=[],
            failure_modes=[],
            performance_baselines={},
            artifacts_dir="test_outputs"
        )
        
        report_files = reporter.generate_report(report)
        
        assert Path(report_files['json']).exists()
        assert Path(report_files['html']).exists()
    
    # Test HTML report formatting
    
    def test_html_report_contains_executive_summary(self, reporter, sample_report):
        """Test HTML report contains executive summary."""
        report_files = reporter.generate_report(sample_report)
        html_file = Path(report_files['html'])
        
        html_content = html_file.read_text()
        
        assert "Executive Summary" in html_content
        assert "Total Tests" in html_content
        assert "Passed" in html_content
        assert "Failed" in html_content
        assert "Pass Rate" in html_content
    
    def test_html_report_contains_category_results(self, reporter, sample_report):
        """Test HTML report contains category results."""
        report_files = reporter.generate_report(sample_report)
        html_file = Path(report_files['html'])
        
        html_content = html_file.read_text()
        
        assert "Category Results" in html_content
        assert "stress" in html_content
    
    def test_html_report_contains_requirement_coverage(self, reporter, sample_report):
        """Test HTML report contains requirement coverage."""
        report_files = reporter.generate_report(sample_report)
        html_file = Path(report_files['html'])
        
        html_content = html_file.read_text()
        
        assert "Requirement Coverage" in html_content
        assert "1.1" in html_content
    
    def test_html_report_contains_breaking_points(self, reporter, sample_report):
        """Test HTML report contains breaking points."""
        report_files = reporter.generate_report(sample_report)
        html_file = Path(report_files['html'])
        
        html_content = html_file.read_text()
        
        assert "Breaking Points" in html_content
        assert "document_size" in html_content
        assert "100" in html_content
    
    def test_html_report_contains_failure_modes(self, reporter, sample_report):
        """Test HTML report contains failure modes."""
        report_files = reporter.generate_report(sample_report)
        html_file = Path(report_files['html'])
        
        html_content = html_file.read_text()
        
        assert "Failure Modes" in html_content
        assert "FM-001" in html_content
    
    def test_html_report_contains_performance_baselines(self, reporter, sample_report):
        """Test HTML report contains performance baselines."""
        report_files = reporter.generate_report(sample_report)
        html_file = Path(report_files['html'])
        
        html_content = html_file.read_text()
        
        assert "Performance Baselines" in html_content
        assert "baseline_10pages" in html_content
    
    def test_html_report_contains_table_of_contents(self, reporter, sample_report):
        """Test HTML report contains table of contents."""
        report_files = reporter.generate_report(sample_report)
        html_file = Path(report_files['html'])
        
        html_content = html_file.read_text()
        
        assert "Table of Contents" in html_content
        assert "#executive-summary" in html_content
        assert "#category-results" in html_content
        assert "#requirement-coverage" in html_content
    
    def test_html_report_styling(self, reporter, sample_report):
        """Test HTML report includes CSS styling."""
        report_files = reporter.generate_report(sample_report)
        html_file = Path(report_files['html'])
        
        html_content = html_file.read_text()
        
        assert "<style>" in html_content
        assert "font-family" in html_content
        assert ".metric" in html_content
        assert ".status-pass" in html_content
    
    # Test JSON report structure
    
    def test_json_report_structure(self, reporter, sample_report):
        """Test JSON report has correct structure."""
        report_files = reporter.generate_report(sample_report)
        json_file = Path(report_files['json'])
        
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        assert 'execution_date' in data
        assert 'total_tests' in data
        assert 'passed' in data
        assert 'failed' in data
        assert 'skipped' in data
        assert 'errors' in data
        assert 'duration_seconds' in data
        assert 'category_results' in data
        assert 'requirement_results' in data
        assert 'breaking_points' in data
        assert 'failure_modes' in data
        assert 'performance_baselines' in data
    
    def test_json_report_category_results(self, reporter, sample_report):
        """Test JSON report category results structure."""
        report_files = reporter.generate_report(sample_report)
        json_file = Path(report_files['json'])
        
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        assert 'stress' in data['category_results']
        category = data['category_results']['stress']
        assert category['total_tests'] == 10
        assert category['passed'] == 8
        assert category['failed'] == 1
    
    def test_json_report_breaking_points(self, reporter, sample_report):
        """Test JSON report breaking points structure."""
        report_files = reporter.generate_report(sample_report)
        json_file = Path(report_files['json'])
        
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        assert len(data['breaking_points']) == 1
        bp = data['breaking_points'][0]
        assert bp['dimension'] == 'document_size'
        assert bp['maximum_viable_value'] == '100'
        assert bp['failure_mode'] == 'timeout'
    
    def test_json_report_failure_modes(self, reporter, sample_report):
        """Test JSON report failure modes structure."""
        report_files = reporter.generate_report(sample_report)
        json_file = Path(report_files['json'])
        
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        assert len(data['failure_modes']) == 1
        fm = data['failure_modes'][0]
        assert fm['failure_id'] == 'FM-001'
        assert fm['category'] == 'crash'
        assert 'trigger' in fm
        assert 'impact' in fm
        assert 'mitigation' in fm
    
    def test_json_report_performance_baselines(self, reporter, sample_report):
        """Test JSON report performance baselines structure."""
        report_files = reporter.generate_report(sample_report)
        json_file = Path(report_files['json'])
        
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        assert 'baseline_10pages' in data['performance_baselines']
        baseline = data['performance_baselines']['baseline_10pages']
        assert baseline['duration_seconds'] == 10.5
        assert baseline['memory_peak_mb'] == 150.0
    
    # Test JUnit XML generation
    
    def test_junit_xml_structure(self, reporter, sample_report):
        """Test JUnit XML has correct structure."""
        report_files = reporter.generate_report(sample_report)
        xml_file = Path(report_files['junit_xml'])
        
        xml_content = xml_file.read_text()
        
        assert '<?xml version="1.0"' in xml_content
        assert '<testsuites' in xml_content
        assert '<testsuite' in xml_content
        assert '<testcase' in xml_content
        assert '</testsuites>' in xml_content
    
    def test_junit_xml_test_counts(self, reporter, sample_report):
        """Test JUnit XML includes correct test counts."""
        report_files = reporter.generate_report(sample_report)
        xml_file = Path(report_files['junit_xml'])
        
        xml_content = xml_file.read_text()
        
        assert 'tests="10"' in xml_content
        assert 'failures="1"' in xml_content
        assert 'skipped="1"' in xml_content
    
    def test_junit_xml_test_case(self, reporter, sample_report):
        """Test JUnit XML includes test case details."""
        report_files = reporter.generate_report(sample_report)
        xml_file = Path(report_files['junit_xml'])
        
        xml_content = xml_file.read_text()
        
        assert 'name="test_001"' in xml_content
        assert 'classname="stress"' in xml_content
    
    def test_junit_xml_failure_element(self, reporter, sample_metrics):
        """Test JUnit XML includes failure elements."""
        test_result = TestResult(
            test_id="test_fail",
            requirement_id="1.1",
            category="chaos",
            status=TestStatus.FAIL,
            duration_seconds=5.0,
            error_message="Test failed",
            metrics=sample_metrics
        )
        
        category_report = CategoryReport(
            category="chaos",
            total_tests=1,
            passed=0,
            failed=1,
            skipped=0,
            errors=0,
            duration_seconds=5.0,
            test_results=[test_result]
        )
        
        report = TestReport(
            execution_date=datetime.now(),
            total_tests=1,
            passed=0,
            failed=1,
            skipped=0,
            errors=0,
            duration_seconds=5.0,
            category_results={"chaos": category_report},
            requirement_results={},
            breaking_points=[],
            failure_modes=[],
            performance_baselines={},
            artifacts_dir="test_outputs"
        )
        
        report_files = reporter.generate_report(report)
        xml_file = Path(report_files['junit_xml'])
        
        xml_content = xml_file.read_text()
        
        assert '<failure' in xml_content
        assert 'Test failed' in xml_content
    
    def test_junit_xml_error_element(self, reporter, sample_metrics):
        """Test JUnit XML includes error elements."""
        test_result = TestResult(
            test_id="test_error",
            requirement_id="1.1",
            category="stress",
            status=TestStatus.ERROR,
            duration_seconds=2.0,
            error_message="Test error occurred",
            metrics=sample_metrics
        )
        
        category_report = CategoryReport(
            category="stress",
            total_tests=1,
            passed=0,
            failed=0,
            skipped=0,
            errors=1,
            duration_seconds=2.0,
            test_results=[test_result]
        )
        
        report = TestReport(
            execution_date=datetime.now(),
            total_tests=1,
            passed=0,
            failed=0,
            skipped=0,
            errors=1,
            duration_seconds=2.0,
            category_results={"stress": category_report},
            requirement_results={},
            breaking_points=[],
            failure_modes=[],
            performance_baselines={},
            artifacts_dir="test_outputs"
        )
        
        report_files = reporter.generate_report(report)
        xml_file = Path(report_files['junit_xml'])
        
        xml_content = xml_file.read_text()
        
        assert '<error' in xml_content
        assert 'Test error occurred' in xml_content
    
    def test_junit_xml_skipped_element(self, reporter):
        """Test JUnit XML includes skipped elements."""
        test_result = TestResult(
            test_id="test_skip",
            requirement_id="1.1",
            category="boundary",
            status=TestStatus.SKIP,
            duration_seconds=0.0,
            error_message="Test skipped"
        )
        
        category_report = CategoryReport(
            category="boundary",
            total_tests=1,
            passed=0,
            failed=0,
            skipped=1,
            errors=0,
            duration_seconds=0.0,
            test_results=[test_result]
        )
        
        report = TestReport(
            execution_date=datetime.now(),
            total_tests=1,
            passed=0,
            failed=0,
            skipped=1,
            errors=0,
            duration_seconds=0.0,
            category_results={"boundary": category_report},
            requirement_results={},
            breaking_points=[],
            failure_modes=[],
            performance_baselines={},
            artifacts_dir="test_outputs"
        )
        
        report_files = reporter.generate_report(report)
        xml_file = Path(report_files['junit_xml'])
        
        xml_content = xml_file.read_text()
        
        assert '<skipped' in xml_content
    
    # Test failure mode catalog generation
    
    def test_failure_mode_catalog_generation(self, reporter, sample_report):
        """Test failure mode catalog is generated when failures exist."""
        report_files = reporter.generate_report(sample_report)
        
        assert 'failure_catalog' in report_files
        catalog_file = Path(report_files['failure_catalog'])
        assert catalog_file.exists()
        
        catalog_content = catalog_file.read_text()
        assert "# Failure Mode Catalog" in catalog_content
        assert "Breaking Points" in catalog_content
        assert "Failure Modes" in catalog_content
    
    def test_failure_mode_catalog_content(self, reporter, sample_report):
        """Test failure mode catalog contains detailed information."""
        catalog_file = reporter.document_failure_mode(sample_report)
        
        catalog_content = catalog_file.read_text()
        
        # Check breaking points section
        assert "document_size" in catalog_content
        assert "100" in catalog_content
        
        # Check failure modes section
        assert "FM-001" in catalog_content
        assert "Document with 10,000+ chunks" in catalog_content
        assert "Implement chunk batching" in catalog_content
    
    def test_github_annotations_generation(self, reporter, sample_report):
        """Test GitHub annotations file is generated."""
        report_files = reporter.generate_report(sample_report)
        
        assert 'github_annotations' in report_files
        annotations_file = Path(report_files['github_annotations'])
        assert annotations_file.exists()
        
        with open(annotations_file, 'r') as f:
            data = json.load(f)
        
        assert 'annotations' in data
        assert 'summary' in data
        assert data['summary']['total_tests'] == 10
