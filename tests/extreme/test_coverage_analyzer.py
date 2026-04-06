"""
Tests for Coverage Analyzer

This module tests the coverage measurement and analysis functionality.
"""

import json
import pytest
from pathlib import Path
from datetime import datetime

from tests.extreme.coverage_analyzer import (
    CoverageAnalyzer,
    CoverageMetrics,
    CoverageReport
)


class TestCoverageAnalyzer:
    """Test suite for CoverageAnalyzer."""
    
    def test_coverage_analyzer_initialization(self, tmp_path):
        """Test that coverage analyzer initializes correctly."""
        analyzer = CoverageAnalyzer(
            source_dirs=['ingestion', 'retrieval'],
            output_dir=str(tmp_path / "coverage_reports"),
            baseline_dir=str(tmp_path / "baselines")
        )
        
        assert analyzer.source_dirs == ['ingestion', 'retrieval']
        assert analyzer.output_dir.exists()
        assert analyzer.baseline_dir.exists()
    
    def test_coverage_metrics_is_adequate(self):
        """Test coverage metrics adequacy check."""
        # Adequate coverage
        metrics_good = CoverageMetrics(
            module_name="test_module",
            total_statements=100,
            covered_statements=95,
            missing_statements=5,
            coverage_percent=95.0
        )
        assert metrics_good.is_adequate
        
        # Inadequate coverage
        metrics_bad = CoverageMetrics(
            module_name="test_module",
            total_statements=100,
            covered_statements=85,
            missing_statements=15,
            coverage_percent=85.0
        )
        assert not metrics_bad.is_adequate
    
    def test_coverage_report_meets_threshold(self):
        """Test coverage report threshold checking."""
        component_coverage = {
            'module1': CoverageMetrics(
                module_name='module1',
                total_statements=100,
                covered_statements=95,
                missing_statements=5,
                coverage_percent=95.0
            ),
            'module2': CoverageMetrics(
                module_name='module2',
                total_statements=100,
                covered_statements=92,
                missing_statements=8,
                coverage_percent=92.0
            )
        }
        
        report = CoverageReport(
            timestamp=datetime.now(),
            total_coverage_percent=93.5,
            component_coverage=component_coverage,
            untested_paths=[],
            error_paths_covered=True
        )
        
        assert report.meets_threshold(90.0)
        assert not report.meets_threshold(95.0)
    
    def test_coverage_report_low_coverage_components(self):
        """Test identification of low coverage components."""
        component_coverage = {
            'module1': CoverageMetrics(
                module_name='module1',
                total_statements=100,
                covered_statements=95,
                missing_statements=5,
                coverage_percent=95.0
            ),
            'module2': CoverageMetrics(
                module_name='module2',
                total_statements=100,
                covered_statements=85,
                missing_statements=15,
                coverage_percent=85.0
            ),
            'module3': CoverageMetrics(
                module_name='module3',
                total_statements=100,
                covered_statements=88,
                missing_statements=12,
                coverage_percent=88.0
            )
        }
        
        report = CoverageReport(
            timestamp=datetime.now(),
            total_coverage_percent=89.3,
            component_coverage=component_coverage,
            untested_paths=[],
            error_paths_covered=True
        )
        
        low_coverage = report.get_low_coverage_components(90.0)
        assert set(low_coverage) == {'module2', 'module3'}
    
    def test_extract_module_name(self, tmp_path):
        """Test module name extraction from file path."""
        analyzer = CoverageAnalyzer(
            source_dirs=['ingestion'],
            output_dir=str(tmp_path / "coverage_reports")
        )
        
        # Test various path formats
        assert analyzer._extract_module_name('ingestion/document_parser.py') == 'ingestion.document_parser'
        assert analyzer._extract_module_name('retrieval/hybrid_retriever.py') == 'retrieval.hybrid_retriever'
        assert analyzer._extract_module_name('src/utils/config.py') == 'utils.config'
    
    def test_identify_untested_paths(self, tmp_path):
        """Test identification of untested code paths."""
        analyzer = CoverageAnalyzer(
            source_dirs=['ingestion'],
            output_dir=str(tmp_path / "coverage_reports")
        )
        
        component_coverage = {
            'module1': CoverageMetrics(
                module_name='module1',
                total_statements=100,
                covered_statements=95,
                missing_statements=5,
                coverage_percent=95.0,
                missing_lines=[10, 15, 20, 25, 30]
            ),
            'module2': CoverageMetrics(
                module_name='module2',
                total_statements=100,
                covered_statements=100,
                missing_statements=0,
                coverage_percent=100.0,
                missing_lines=[]
            )
        }
        
        untested = analyzer._identify_untested_paths(component_coverage)
        
        assert len(untested) == 5
        assert 'module1:10' in untested
        assert 'module1:15' in untested
        assert 'module1:20' in untested
        assert 'module1:25' in untested
        assert 'module1:30' in untested
    
    def test_verify_coverage_threshold(self, tmp_path):
        """Test coverage threshold verification."""
        analyzer = CoverageAnalyzer(
            source_dirs=['ingestion'],
            output_dir=str(tmp_path / "coverage_reports")
        )
        
        component_coverage = {
            'module1': CoverageMetrics(
                module_name='module1',
                total_statements=100,
                covered_statements=95,
                missing_statements=5,
                coverage_percent=95.0
            ),
            'module2': CoverageMetrics(
                module_name='module2',
                total_statements=100,
                covered_statements=85,
                missing_statements=15,
                coverage_percent=85.0
            )
        }
        
        report = CoverageReport(
            timestamp=datetime.now(),
            total_coverage_percent=90.0,
            component_coverage=component_coverage,
            untested_paths=[],
            error_paths_covered=True
        )
        
        # Test with 90% threshold
        meets_threshold, low_coverage = analyzer.verify_coverage_threshold(report, 90.0)
        assert meets_threshold
        assert 'module2' in low_coverage
        
        # Test with 95% threshold
        meets_threshold, low_coverage = analyzer.verify_coverage_threshold(report, 95.0)
        assert not meets_threshold
        assert 'module2' in low_coverage
        # module1 has exactly 95% so it meets the threshold
    
    def test_coverage_trend_tracking(self, tmp_path):
        """Test coverage trend tracking over time."""
        analyzer = CoverageAnalyzer(
            source_dirs=['ingestion'],
            output_dir=str(tmp_path / "coverage_reports"),
            baseline_dir=str(tmp_path / "baselines")
        )
        
        # Create first report
        report1 = CoverageReport(
            timestamp=datetime.now(),
            total_coverage_percent=85.0,
            component_coverage={},
            untested_paths=[],
            error_paths_covered=True
        )
        
        analyzer._update_coverage_trend(report1)
        
        # Create second report
        report2 = CoverageReport(
            timestamp=datetime.now(),
            total_coverage_percent=90.0,
            component_coverage={},
            untested_paths=[],
            error_paths_covered=True
        )
        
        analyzer._update_coverage_trend(report2)
        
        # Load trend
        trend = analyzer._load_coverage_trend()
        
        assert trend is not None
        assert len(trend) == 2
        assert 85.0 in trend.values()
        assert 90.0 in trend.values()
    
    def test_generate_coverage_summary(self, tmp_path):
        """Test coverage summary generation."""
        analyzer = CoverageAnalyzer(
            source_dirs=['ingestion'],
            output_dir=str(tmp_path / "coverage_reports")
        )
        
        component_coverage = {
            'module1': CoverageMetrics(
                module_name='module1',
                total_statements=100,
                covered_statements=95,
                missing_statements=5,
                coverage_percent=95.0
            ),
            'module2': CoverageMetrics(
                module_name='module2',
                total_statements=100,
                covered_statements=85,
                missing_statements=15,
                coverage_percent=85.0
            )
        }
        
        report = CoverageReport(
            timestamp=datetime.now(),
            total_coverage_percent=90.0,
            component_coverage=component_coverage,
            untested_paths=['module2:10', 'module2:20'],
            error_paths_covered=True,
            html_report_path='/path/to/html',
            json_report_path='/path/to/json'
        )
        
        summary = analyzer.generate_coverage_summary(report)
        
        assert 'COVERAGE ANALYSIS SUMMARY' in summary
        assert '90.00%' in summary
        assert 'module1' in summary
        assert 'module2' in summary
        assert 'Untested Paths' in summary
        assert '/path/to/html' in summary
        assert '/path/to/json' in summary
    
    def test_save_coverage_report(self, tmp_path):
        """Test saving coverage report to file."""
        analyzer = CoverageAnalyzer(
            source_dirs=['ingestion'],
            output_dir=str(tmp_path / "coverage_reports")
        )
        
        report = CoverageReport(
            timestamp=datetime.now(),
            total_coverage_percent=90.0,
            component_coverage={},
            untested_paths=[],
            error_paths_covered=True,
            html_report_path='/path/to/html',
            json_report_path='/path/to/json'
        )
        
        output_path = analyzer.save_coverage_report(report, 'test_summary.txt')
        
        assert Path(output_path).exists()
        
        # Read and verify content
        with open(output_path, 'r') as f:
            content = f.read()
        
        assert 'COVERAGE ANALYSIS SUMMARY' in content
        assert '90.00%' in content


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
