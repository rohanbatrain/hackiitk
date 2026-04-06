"""
Unit tests for GitHub Actions test result aggregation logic.

Tests the aggregation logic that consolidates results from parallel test jobs.
"""

import json
import pytest
from pathlib import Path
from datetime import datetime
import sys
import os

# Add .github/scripts to path to import the aggregation module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '.github', 'scripts'))
from aggregate_results import aggregate_test_results, format_console_output


class TestAggregateTestResults:
    """Test suite for aggregate_test_results function."""
    
    def test_aggregation_with_complete_results_from_all_categories(self, tmp_path):
        """
        Test aggregation with complete results from all 8 categories.
        
        Validates Requirements 5.1-5.5: Result aggregation calculates correct totals,
        pass/fail/error/skip counts, duration, pass rate, and per-category statistics.
        """
        # Create test data for all 8 categories
        categories = ["property", "boundary", "adversarial", "stress", "chaos", "performance", "unit", "integration"]
        
        for i, category in enumerate(categories):
            category_dir = tmp_path / f"test-results-{category}"
            category_dir.mkdir()
            
            # Create result file with varying test counts
            result_data = {
                "total_tests": 10 + i,
                "passed": 9 + i,
                "failed": 1,
                "errors": 0,
                "skipped": 0,
                "duration_seconds": 5.0 + i
            }
            
            result_file = category_dir / f"report_{category}.json"
            with open(result_file, "w") as f:
                json.dump(result_data, f)
        
        # Aggregate results
        results = aggregate_test_results(tmp_path)
        
        # Verify aggregated totals
        assert results["total_tests"] == sum(10 + i for i in range(8))  # 108 total
        assert results["passed"] == sum(9 + i for i in range(8))  # 100 passed
        assert results["failed"] == 8  # 1 per category
        assert results["errors"] == 0
        assert results["skipped"] == 0
        assert results["duration_seconds"] == sum(5.0 + i for i in range(8))  # 68.0 seconds
        
        # Verify pass rate calculation
        expected_pass_rate = (100 / 108) * 100
        assert abs(results["pass_rate"] - expected_pass_rate) < 0.01
        
        # Verify parallel jobs count
        assert results["parallel_jobs"] == 8
        
        # Verify category breakdown
        assert len(results["categories"]) == 8
        for i, category in enumerate(categories):
            assert category in results["categories"]
            assert results["categories"][category]["total"] == 10 + i
            assert results["categories"][category]["passed"] == 9 + i
            assert results["categories"][category]["failed"] == 1
            
            # Verify per-category pass rate
            expected_cat_pass_rate = ((9 + i) / (10 + i)) * 100
            assert abs(results["categories"][category]["pass_rate"] - expected_cat_pass_rate) < 0.01
    
    def test_aggregation_with_missing_categories(self, tmp_path):
        """
        Test aggregation with missing categories.
        
        Validates Requirement 10.4: Aggregator handles missing artifacts gracefully
        and continues processing available categories.
        """
        # Create test data for only 3 categories (5 missing)
        categories = ["property", "unit", "integration"]
        
        for category in categories:
            category_dir = tmp_path / f"test-results-{category}"
            category_dir.mkdir()
            
            result_data = {
                "total_tests": 20,
                "passed": 18,
                "failed": 2,
                "errors": 0,
                "skipped": 0,
                "duration_seconds": 10.0
            }
            
            result_file = category_dir / f"report_{category}.json"
            with open(result_file, "w") as f:
                json.dump(result_data, f)
        
        # Aggregate results
        results = aggregate_test_results(tmp_path)
        
        # Verify only available categories are included
        assert results["parallel_jobs"] == 3
        assert len(results["categories"]) == 3
        assert "property" in results["categories"]
        assert "unit" in results["categories"]
        assert "integration" in results["categories"]
        
        # Verify aggregated totals reflect only available categories
        assert results["total_tests"] == 60  # 20 * 3
        assert results["passed"] == 54  # 18 * 3
        assert results["failed"] == 6  # 2 * 3
        
        # Verify pass rate is calculated correctly
        expected_pass_rate = (54 / 60) * 100
        assert abs(results["pass_rate"] - expected_pass_rate) < 0.01
    
    def test_aggregation_with_malformed_json_files(self, tmp_path, capsys):
        """
        Test aggregation with malformed JSON files.
        
        Validates Requirement 10.4: Aggregator handles malformed JSON gracefully,
        logs errors, and continues processing other files.
        """
        # Create one valid category
        valid_dir = tmp_path / "test-results-property"
        valid_dir.mkdir()
        
        valid_data = {
            "total_tests": 10,
            "passed": 9,
            "failed": 1,
            "errors": 0,
            "skipped": 0,
            "duration_seconds": 5.0
        }
        
        valid_file = valid_dir / "report_property.json"
        with open(valid_file, "w") as f:
            json.dump(valid_data, f)
        
        # Create category with malformed JSON
        malformed_dir = tmp_path / "test-results-boundary"
        malformed_dir.mkdir()
        
        malformed_file = malformed_dir / "report_boundary.json"
        with open(malformed_file, "w") as f:
            f.write("{invalid json content")
        
        # Create category with incomplete JSON (missing required fields)
        incomplete_dir = tmp_path / "test-results-unit"
        incomplete_dir.mkdir()
        
        incomplete_file = incomplete_dir / "report_unit.json"
        with open(incomplete_file, "w") as f:
            json.dump({"some_field": "value"}, f)  # Missing total_tests field
        
        # Aggregate results
        results = aggregate_test_results(tmp_path)
        
        # Verify error was logged for malformed JSON
        captured = capsys.readouterr()
        assert "⚠️ Error parsing JSON file" in captured.out
        
        # Verify only valid data was aggregated
        assert results["total_tests"] == 10
        assert results["passed"] == 9
        assert results["failed"] == 1
        
        # Verify parallel jobs count includes all directories
        assert results["parallel_jobs"] == 3
        
        # Verify all categories appear in breakdown (even if empty due to malformed data)
        # but only valid category has non-zero counts
        assert "property" in results["categories"]
        assert results["categories"]["property"]["total"] == 10
        assert results["categories"]["property"]["passed"] == 9
        
        # Malformed/incomplete categories should have zero counts
        if "boundary" in results["categories"]:
            assert results["categories"]["boundary"]["total"] == 0
        if "unit" in results["categories"]:
            assert results["categories"]["unit"]["total"] == 0
    
    def test_aggregation_with_zero_tests_minimal_dependency_mode(self, tmp_path):
        """
        Test aggregation with zero tests (minimal dependency mode).
        
        Validates Requirement 10.4: Aggregator handles case where no tests execute
        and generates appropriate empty results summary.
        """
        # Create empty results directory (no test artifacts)
        # Don't create any subdirectories
        
        # Aggregate results
        results = aggregate_test_results(tmp_path)
        
        # Verify empty results structure
        assert results["total_tests"] == 0
        assert results["passed"] == 0
        assert results["failed"] == 0
        assert results["errors"] == 0
        assert results["skipped"] == 0
        assert results["duration_seconds"] == 0.0
        assert results["pass_rate"] == 0.0
        assert results["parallel_jobs"] == 0
        assert len(results["categories"]) == 0
    
    def test_aggregation_with_nonexistent_directory(self, tmp_path):
        """
        Test aggregation when results directory doesn't exist.
        
        Validates Requirement 10.4: Aggregator handles missing directory gracefully.
        """
        # Use non-existent directory
        nonexistent_dir = tmp_path / "does-not-exist"
        
        # Aggregate results
        results = aggregate_test_results(nonexistent_dir)
        
        # Verify empty results structure
        assert results["total_tests"] == 0
        assert results["passed"] == 0
        assert results["failed"] == 0
        assert results["errors"] == 0
        assert results["skipped"] == 0
        assert results["pass_rate"] == 0.0
        assert results["parallel_jobs"] == 0
    
    def test_pass_rate_calculation_accuracy(self, tmp_path):
        """
        Test pass rate calculation accuracy with various scenarios.
        
        Validates Requirements 5.4, 5.5: Pass rate and per-category pass rates
        are calculated accurately.
        """
        # Test scenario 1: 100% pass rate
        scenario1_dir = tmp_path / "scenario1"
        scenario1_dir.mkdir()
        
        cat1_dir = scenario1_dir / "test-results-property"
        cat1_dir.mkdir()
        
        with open(cat1_dir / "report.json", "w") as f:
            json.dump({
                "total_tests": 50,
                "passed": 50,
                "failed": 0,
                "errors": 0,
                "skipped": 0,
                "duration_seconds": 10.0
            }, f)
        
        results1 = aggregate_test_results(scenario1_dir)
        assert results1["pass_rate"] == 100.0
        assert results1["categories"]["property"]["pass_rate"] == 100.0
        
        # Test scenario 2: 0% pass rate
        scenario2_dir = tmp_path / "scenario2"
        scenario2_dir.mkdir()
        
        cat2_dir = scenario2_dir / "test-results-boundary"
        cat2_dir.mkdir()
        
        with open(cat2_dir / "report.json", "w") as f:
            json.dump({
                "total_tests": 30,
                "passed": 0,
                "failed": 30,
                "errors": 0,
                "skipped": 0,
                "duration_seconds": 15.0
            }, f)
        
        results2 = aggregate_test_results(scenario2_dir)
        assert results2["pass_rate"] == 0.0
        assert results2["categories"]["boundary"]["pass_rate"] == 0.0
        
        # Test scenario 3: 95% pass rate (success threshold)
        scenario3_dir = tmp_path / "scenario3"
        scenario3_dir.mkdir()
        
        cat3_dir = scenario3_dir / "test-results-unit"
        cat3_dir.mkdir()
        
        with open(cat3_dir / "report.json", "w") as f:
            json.dump({
                "total_tests": 100,
                "passed": 95,
                "failed": 5,
                "errors": 0,
                "skipped": 0,
                "duration_seconds": 20.0
            }, f)
        
        results3 = aggregate_test_results(scenario3_dir)
        assert results3["pass_rate"] == 95.0
        assert results3["categories"]["unit"]["pass_rate"] == 95.0
        
        # Test scenario 4: Mixed results with errors and skipped
        scenario4_dir = tmp_path / "scenario4"
        scenario4_dir.mkdir()
        
        cat4_dir = scenario4_dir / "test-results-integration"
        cat4_dir.mkdir()
        
        with open(cat4_dir / "report.json", "w") as f:
            json.dump({
                "total_tests": 80,
                "passed": 70,
                "failed": 5,
                "errors": 3,
                "skipped": 2,
                "duration_seconds": 25.0
            }, f)
        
        results4 = aggregate_test_results(scenario4_dir)
        expected_pass_rate = (70 / 80) * 100
        assert abs(results4["pass_rate"] - expected_pass_rate) < 0.01
        assert abs(results4["categories"]["integration"]["pass_rate"] - expected_pass_rate) < 0.01
    
    def test_aggregation_with_multiple_json_files_per_category(self, tmp_path):
        """
        Test aggregation when a category has multiple JSON result files.
        
        Validates that aggregator correctly sums results from multiple files
        in the same category.
        """
        # Create category with multiple result files
        category_dir = tmp_path / "test-results-property"
        category_dir.mkdir()
        
        # First result file
        with open(category_dir / "report_part1.json", "w") as f:
            json.dump({
                "total_tests": 20,
                "passed": 18,
                "failed": 2,
                "errors": 0,
                "skipped": 0,
                "duration_seconds": 5.0
            }, f)
        
        # Second result file
        with open(category_dir / "report_part2.json", "w") as f:
            json.dump({
                "total_tests": 15,
                "passed": 14,
                "failed": 1,
                "errors": 0,
                "skipped": 0,
                "duration_seconds": 3.0
            }, f)
        
        # Aggregate results
        results = aggregate_test_results(tmp_path)
        
        # Verify results are summed correctly
        assert results["total_tests"] == 35  # 20 + 15
        assert results["passed"] == 32  # 18 + 14
        assert results["failed"] == 3  # 2 + 1
        assert results["duration_seconds"] == 8.0  # 5.0 + 3.0
        
        # Verify category statistics
        assert results["categories"]["property"]["total"] == 35
        assert results["categories"]["property"]["passed"] == 32
        assert results["categories"]["property"]["failed"] == 3


class TestFormatConsoleOutput:
    """Test suite for format_console_output function."""
    
    def test_format_output_with_successful_results(self):
        """
        Test console output formatting with successful test results (≥95% pass rate).
        
        Validates Requirements 6.1-6.5, 14.1-14.5: Report formatting includes all
        required metrics and proper formatting.
        """
        results = {
            "execution_date": "2024-01-15T10:30:00",
            "total_tests": 100,
            "passed": 96,
            "failed": 3,
            "errors": 1,
            "skipped": 0,
            "duration_seconds": 600.0,
            "pass_rate": 96.0,
            "parallel_jobs": 8,
            "categories": {
                "property": {"total": 20, "passed": 20, "failed": 0, "errors": 0, "pass_rate": 100.0},
                "boundary": {"total": 15, "passed": 14, "failed": 1, "errors": 0, "pass_rate": 93.3},
                "unit": {"total": 30, "passed": 29, "failed": 1, "errors": 0, "pass_rate": 96.7},
                "integration": {"total": 35, "passed": 33, "failed": 1, "errors": 1, "pass_rate": 94.3}
            }
        }
        
        output = format_console_output(results)
        
        # Verify separator lines
        assert "=" * 80 in output
        
        # Verify header
        assert "PARALLEL TEST SUITE RESULTS" in output
        
        # Verify metrics are present
        assert "Parallel Jobs: 8" in output
        assert "Total Tests: 100" in output
        assert "Passed: 96 (96.0%)" in output
        assert "Failed: 3" in output
        assert "Errors: 1" in output
        assert "Skipped: 0" in output
        assert "Duration: 10.0 minutes" in output
        
        # Verify category breakdown
        assert "Category Breakdown:" in output
        assert "property: 20/20 (100.0%)" in output
        assert "boundary: 14/15 (93.3%)" in output
        assert "unit: 29/30 (96.7%)" in output
        assert "integration: 33/35 (94.3%)" in output
        
        # Verify success criteria message
        assert "✅ SUCCESS CRITERIA MET (≥95% pass rate)" in output
    
    def test_format_output_with_failed_criteria(self):
        """
        Test console output formatting when success criteria not met (<95% pass rate).
        
        Validates Requirement 7.3: Report displays failure message when pass rate < 95%.
        """
        results = {
            "execution_date": "2024-01-15T10:30:00",
            "total_tests": 100,
            "passed": 90,
            "failed": 10,
            "errors": 0,
            "skipped": 0,
            "duration_seconds": 600.0,
            "pass_rate": 90.0,
            "parallel_jobs": 8,
            "categories": {
                "property": {"total": 50, "passed": 45, "failed": 5, "errors": 0, "pass_rate": 90.0},
                "unit": {"total": 50, "passed": 45, "failed": 5, "errors": 0, "pass_rate": 90.0}
            }
        }
        
        output = format_console_output(results)
        
        # Verify failure message
        assert "⚠️  SUCCESS CRITERIA NOT MET (90.0% < 95%)" in output
        assert "✅ SUCCESS CRITERIA MET" not in output
    
    def test_format_output_with_zero_tests(self):
        """
        Test console output formatting with zero tests (minimal dependency mode).
        
        Validates Requirement 7.4: Report displays minimal dependency mode message
        when no tests execute.
        """
        results = {
            "execution_date": "2024-01-15T10:30:00",
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "skipped": 0,
            "duration_seconds": 0.0,
            "pass_rate": 0.0,
            "parallel_jobs": 0,
            "categories": {}
        }
        
        output = format_console_output(results)
        
        # Verify minimal dependency mode message
        assert "ℹ️  No tests executed (minimal dependency mode)" in output
        assert "SUCCESS CRITERIA" not in output
    
    def test_format_output_excludes_empty_categories(self):
        """
        Test that console output excludes categories with zero tests.
        
        Validates that category breakdown only shows categories with actual tests.
        """
        results = {
            "execution_date": "2024-01-15T10:30:00",
            "total_tests": 50,
            "passed": 48,
            "failed": 2,
            "errors": 0,
            "skipped": 0,
            "duration_seconds": 300.0,
            "pass_rate": 96.0,
            "parallel_jobs": 3,
            "categories": {
                "property": {"total": 30, "passed": 29, "failed": 1, "errors": 0, "pass_rate": 96.7},
                "unit": {"total": 20, "passed": 19, "failed": 1, "errors": 0, "pass_rate": 95.0},
                "boundary": {"total": 0, "passed": 0, "failed": 0, "errors": 0, "pass_rate": 0.0}
            }
        }
        
        output = format_console_output(results)
        
        # Verify only non-empty categories are shown
        assert "property: 29/30 (96.7%)" in output
        assert "unit: 19/20 (95.0%)" in output
        assert "boundary:" not in output  # Should be excluded
    
    def test_format_output_categories_sorted_alphabetically(self):
        """
        Test that category breakdown is sorted alphabetically.
        
        Validates consistent ordering of categories in output.
        """
        results = {
            "execution_date": "2024-01-15T10:30:00",
            "total_tests": 60,
            "passed": 58,
            "failed": 2,
            "errors": 0,
            "skipped": 0,
            "duration_seconds": 300.0,
            "pass_rate": 96.7,
            "parallel_jobs": 3,
            "categories": {
                "unit": {"total": 20, "passed": 19, "failed": 1, "errors": 0, "pass_rate": 95.0},
                "boundary": {"total": 20, "passed": 20, "failed": 0, "errors": 0, "pass_rate": 100.0},
                "property": {"total": 20, "passed": 19, "failed": 1, "errors": 0, "pass_rate": 95.0}
            }
        }
        
        output = format_console_output(results)
        
        # Extract category lines
        lines = output.split("\n")
        category_lines = [line for line in lines if ":" in line and "/" in line and "(" in line]
        
        # Verify alphabetical order
        assert len(category_lines) == 3
        assert "boundary" in category_lines[0]
        assert "property" in category_lines[1]
        assert "unit" in category_lines[2]
