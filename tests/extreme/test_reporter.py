"""
Unit tests for ExtremeTestReporter

Tests report generation in multiple formats (HTML, JSON, JUnit XML)
and failure mode documentation.
"""

import pytest
from pathlib import Path
from datetime import datetime
import json
import xml.etree.ElementTree as ET

from tests.extreme.reporter import ExtremeTestReporter
from tests.extreme.models import (
    TestReport, CategoryReport, RequirementReport, TestResult,
    BreakingPoint, FailureMode, Metrics, TestStatus, FailureCategory
)


@pytest.fixture
def sample_metrics():
    """Create sample metrics."""
    return Metrics(
        duration_seconds=10.5,
        memory_peak_mb=512.0,
        memory_average_mb=256.0,
        cpu_peak_percent=85.0,
        cpu_average_percent=45.0,
        disk_read_mb=100.0,
        disk_write_mb=50.0,
        file_handles_peak=25,
        thread_count_peak=8
    )


@pytest.fixture
def sample_test_results(sample_metrics):
    """Create sample test results."""
    return [
        TestResult(
            test_id="test_stress_1",
            requirement_id="1.1",
            category="stress",
            status=TestStatus.PASS,
            duration_seconds=5.2,
            metrics=sample_metrics
        ),
        TestResult(
            test_id="test_stress_2",
            requirement_id="1.2",
            category="stress",
            status=TestStatus.FAIL,
            duration_seconds=3.1,
            error_message="Test failed due to timeout"
        ),
        TestResult(
            test_id="test_chaos_1",
            requirement_id="3.1",
            category="chaos",
            status=TestStatus.PASS,
            duration_seconds=7.8
        ),
    ]


@pytest.fixture
def sample_report(sample_test_results, sample_metrics):
    """Create a sample test report."""
    category_report = CategoryReport(
        category="stress",
        total_tests=2,
        passed=1,
        failed=1,
        skipped=0,
        errors=0,
        duration_seconds=8.3,
        test_results=sample_test_results[:2]
    )
    
    chaos_report = CategoryReport(
        category="chaos",
        total_tests=1,
        passed=1,
        failed=0,
        skipped=0,
        errors=0,
        duration_seconds=7.8,
        test_results=[sample_test_results[2]]
    )
    
    req_report = RequirementReport(
        requirement_id="1.1",
        total_tests=1,
        passed=1,
        failed=0,
        test_results=[sample_test_results[0]]
    )
    
    breaking_point = BreakingPoint(
        dimension="document_size",
        maximum_viable_value="100 pages",
        failure_mode=FailureCategory.TIMEOUT,
        error_message="Analysis exceeded 30 minute timeout",
        metrics_at_failure=sample_metrics
    )
    
    failure_mode = FailureMode(
        failure_id="FM001",
        category=FailureCategory.CRASH,
        trigger="Processing document with 10,000+ chunks",
        impact="System crashes with out-of-memory error",
        mitigation="Implement chunk batching and memory limits",
        discovered_date=datetime.now(),
        test_id="test_stress_2"
    )
    
    return TestReport(
        execution_date=datetime.now(),
        total_tests=3,
        passed=2,
        failed=1,
        skipped=0,
        errors=0,
        duration_seconds=16.1,
        category_results={"stress": category_report, "chaos": chaos_report},
        requirement_results={"1.1": req_report},
        breaking_points=[breaking_point],
        failure_modes=[failure_mode],
        performance_baselines={"10_page_baseline": sample_metrics},
        artifacts_dir="test_outputs/extreme/artifacts"
    )


def test_reporter_initialization(tmp_path):
    """Test reporter initialization."""
    reporter = ExtremeTestReporter(output_dir=str(tmp_path))
    assert reporter.output_dir == tmp_path
    assert tmp_path.exists()


def test_generate_json_report(tmp_path, sample_report):
    """Test JSON report generation."""
    reporter = ExtremeTestReporter(output_dir=str(tmp_path))
    report_files = reporter.generate_report(sample_report)
    
    assert 'json' in report_files
    json_file = Path(report_files['json'])
    assert json_file.exists()
    
    # Verify JSON is valid and contains expected data
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    assert data['total_tests'] == 3
    assert data['passed'] == 2
    assert data['failed'] == 1
    assert 'category_results' in data
    assert 'stress' in data['category_results']
    assert 'breaking_points' in data
    assert len(data['breaking_points']) == 1


def test_generate_html_report(tmp_path, sample_report):
    """Test HTML report generation."""
    reporter = ExtremeTestReporter(output_dir=str(tmp_path))
    report_files = reporter.generate_report(sample_report)
    
    assert 'html' in report_files
    html_file = Path(report_files['html'])
    assert html_file.exists()
    
    # Verify HTML contains expected sections
    with open(html_file, 'r') as f:
        content = f.read()
    
    assert 'Executive Summary' in content
    assert 'Category Results' in content
    assert 'Requirement Coverage' in content
    assert 'Breaking Points' in content
    assert 'Failure Modes' in content
    assert 'Performance Baselines' in content
    assert '66.7% Pass Rate' in content  # 2/3 = 66.7%


def test_generate_junit_xml(tmp_path, sample_report):
    """Test JUnit XML report generation."""
    reporter = ExtremeTestReporter(output_dir=str(tmp_path))
    report_files = reporter.generate_report(sample_report)
    
    assert 'junit_xml' in report_files
    xml_file = Path(report_files['junit_xml'])
    assert xml_file.exists()
    
    # Verify XML is valid and contains expected data
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    assert root.tag == 'testsuites'
    assert root.attrib['tests'] == '3'
    assert root.attrib['failures'] == '1'
    
    # Check test suites
    testsuites = root.findall('testsuite')
    assert len(testsuites) == 2  # stress and chaos
    
    # Check test cases
    testcases = root.findall('.//testcase')
    assert len(testcases) == 3


def test_failure_mode_documentation(tmp_path, sample_report):
    """Test failure mode catalog generation."""
    reporter = ExtremeTestReporter(output_dir=str(tmp_path))
    report_files = reporter.generate_report(sample_report)
    
    assert 'failure_catalog' in report_files
    catalog_file = Path(report_files['failure_catalog'])
    assert catalog_file.exists()
    
    # Verify catalog contains expected sections
    with open(catalog_file, 'r') as f:
        content = f.read()
    
    assert '# Failure Mode Catalog' in content
    assert '## Breaking Points' in content
    assert '## Failure Modes' in content
    assert '## Mitigation Strategies' in content
    assert 'document_size' in content
    assert 'FM001' in content


def test_empty_report(tmp_path):
    """Test report generation with no failures or breaking points."""
    empty_report = TestReport(
        execution_date=datetime.now(),
        total_tests=5,
        passed=5,
        failed=0,
        skipped=0,
        errors=0,
        duration_seconds=10.0,
        artifacts_dir="test_outputs/extreme/artifacts"
    )
    
    reporter = ExtremeTestReporter(output_dir=str(tmp_path))
    report_files = reporter.generate_report(empty_report)
    
    # Should not generate failure catalog for empty report
    assert 'failure_catalog' not in report_files
    
    # But should generate other reports
    assert 'json' in report_files
    assert 'html' in report_files
    assert 'junit_xml' in report_files


def test_html_special_characters(tmp_path):
    """Test HTML report handles special characters correctly."""
    test_result = TestResult(
        test_id="test_<script>alert('xss')</script>",
        requirement_id="1.1",
        category="security",
        status=TestStatus.FAIL,
        duration_seconds=1.0,
        error_message="Error with <special> & \"characters\""
    )
    
    report = TestReport(
        execution_date=datetime.now(),
        total_tests=1,
        passed=0,
        failed=1,
        skipped=0,
        errors=0,
        duration_seconds=1.0,
        category_results={
            "security": CategoryReport(
                category="security",
                total_tests=1,
                passed=0,
                failed=1,
                skipped=0,
                errors=0,
                duration_seconds=1.0,
                test_results=[test_result]
            )
        },
        artifacts_dir="test_outputs/extreme/artifacts"
    )
    
    reporter = ExtremeTestReporter(output_dir=str(tmp_path))
    report_files = reporter.generate_report(report)
    
    html_file = Path(report_files['html'])
    with open(html_file, 'r') as f:
        content = f.read()
    
    # Verify special characters are escaped
    assert '<script>' not in content
    assert '&lt;script&gt;' in content or 'alert' not in content


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
