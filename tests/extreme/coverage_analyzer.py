"""
Coverage Analyzer for Comprehensive Testing Framework

This module provides coverage measurement and analysis capabilities for the
extreme testing framework. It integrates with pytest-cov to track code coverage
across all test categories and generates comprehensive coverage reports.

Requirements: 80.1, 80.2, 80.3, 80.4, 80.5, 80.6
"""

import json
import os
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from tests.extreme.models import TestResult


@dataclass
class CoverageMetrics:
    """Coverage metrics for a component or module."""
    
    module_name: str
    total_statements: int
    covered_statements: int
    missing_statements: int
    coverage_percent: float
    missing_lines: List[int] = field(default_factory=list)
    uncovered_branches: List[Tuple[int, int]] = field(default_factory=list)
    
    @property
    def is_adequate(self) -> bool:
        """Check if coverage meets 90% threshold."""
        return self.coverage_percent >= 90.0


@dataclass
class CoverageReport:
    """Comprehensive coverage report."""
    
    timestamp: datetime
    total_coverage_percent: float
    component_coverage: Dict[str, CoverageMetrics]
    untested_paths: List[str]
    error_paths_covered: bool
    coverage_trend: Optional[Dict[str, float]] = None
    html_report_path: Optional[str] = None
    json_report_path: Optional[str] = None
    
    def meets_threshold(self, threshold: float = 90.0) -> bool:
        """Check if overall coverage meets threshold."""
        return self.total_coverage_percent >= threshold
    
    def get_low_coverage_components(self, threshold: float = 90.0) -> List[str]:
        """Get list of components below coverage threshold."""
        return [
            name for name, metrics in self.component_coverage.items()
            if metrics.coverage_percent < threshold
        ]


class CoverageAnalyzer:
    """
    Analyzes test coverage across all test categories.
    
    This class integrates with pytest-cov to measure code coverage,
    identifies untested code paths, and tracks coverage trends over time.
    
    Requirements: 80.1, 80.2, 80.3, 80.4, 80.5, 80.6
    """
    
    def __init__(
        self,
        source_dirs: List[str],
        output_dir: str = "coverage_reports",
        baseline_dir: str = "coverage_baselines"
    ):
        """
        Initialize coverage analyzer.
        
        Args:
            source_dirs: List of source directories to measure coverage for
            output_dir: Directory for coverage reports
            baseline_dir: Directory for baseline coverage data
        """
        self.source_dirs = source_dirs
        self.output_dir = Path(output_dir)
        self.baseline_dir = Path(baseline_dir)
        
        # Create directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.baseline_dir.mkdir(parents=True, exist_ok=True)
        
        self.coverage_data_file = self.output_dir / ".coverage"
        self.trend_file = self.baseline_dir / "coverage_trends.json"
    
    def run_tests_with_coverage(
        self,
        test_categories: Optional[List[str]] = None,
        pytest_args: Optional[List[str]] = None
    ) -> Tuple[int, str]:
        """
        Run tests with coverage measurement.
        
        Args:
            test_categories: Specific test categories to run (stress, chaos, etc.)
            pytest_args: Additional pytest arguments
        
        Returns:
            Tuple of (exit_code, output)
        
        Requirements: 80.1
        """
        # Build pytest command with coverage
        cmd = [
            "pytest",
            f"--cov={','.join(self.source_dirs)}",
            "--cov-report=html:" + str(self.output_dir / "html"),
            "--cov-report=json:" + str(self.output_dir / "coverage.json"),
            "--cov-report=term-missing",
            f"--cov-config={self._get_coverage_config_path()}",
        ]
        
        # Add test paths
        if test_categories:
            for category in test_categories:
                cmd.append(f"tests/extreme/engines/test_{category}_*.py")
        else:
            cmd.append("tests/")
        
        # Add additional pytest args
        if pytest_args:
            cmd.extend(pytest_args)
        
        # Run tests
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )
        
        return result.returncode, result.stdout + result.stderr
    
    def generate_coverage_report(self) -> CoverageReport:
        """
        Generate comprehensive coverage report from coverage data.
        
        Returns:
            CoverageReport with detailed metrics
        
        Requirements: 80.2, 80.3
        """
        # Load coverage JSON data
        json_path = self.output_dir / "coverage.json"
        if not json_path.exists():
            raise FileNotFoundError(
                f"Coverage data not found at {json_path}. "
                "Run tests with coverage first."
            )
        
        with open(json_path, 'r') as f:
            coverage_data = json.load(f)
        
        # Parse coverage data
        component_coverage = self._parse_coverage_data(coverage_data)
        
        # Calculate total coverage
        total_statements = sum(m.total_statements for m in component_coverage.values())
        covered_statements = sum(m.covered_statements for m in component_coverage.values())
        total_coverage = (covered_statements / total_statements * 100) if total_statements > 0 else 0.0
        
        # Identify untested paths
        untested_paths = self._identify_untested_paths(component_coverage)
        
        # Check error path coverage
        error_paths_covered = self._verify_error_path_coverage(coverage_data)
        
        # Load coverage trend
        coverage_trend = self._load_coverage_trend()
        
        report = CoverageReport(
            timestamp=datetime.now(),
            total_coverage_percent=total_coverage,
            component_coverage=component_coverage,
            untested_paths=untested_paths,
            error_paths_covered=error_paths_covered,
            coverage_trend=coverage_trend,
            html_report_path=str(self.output_dir / "html" / "index.html"),
            json_report_path=str(json_path)
        )
        
        # Update trend
        self._update_coverage_trend(report)
        
        return report
    
    def _parse_coverage_data(self, coverage_data: Dict) -> Dict[str, CoverageMetrics]:
        """Parse coverage JSON data into component metrics."""
        component_coverage = {}
        
        files = coverage_data.get("files", {})
        
        for file_path, file_data in files.items():
            # Extract module name from file path
            module_name = self._extract_module_name(file_path)
            
            summary = file_data.get("summary", {})
            
            total_statements = summary.get("num_statements", 0)
            covered_statements = summary.get("covered_lines", 0)
            missing_statements = summary.get("missing_lines", 0)
            coverage_percent = summary.get("percent_covered", 0.0)
            
            # Get missing line numbers
            missing_lines = file_data.get("missing_lines", [])
            
            # Get uncovered branches
            excluded_lines = file_data.get("excluded_lines", [])
            
            metrics = CoverageMetrics(
                module_name=module_name,
                total_statements=total_statements,
                covered_statements=covered_statements,
                missing_statements=missing_statements,
                coverage_percent=coverage_percent,
                missing_lines=missing_lines
            )
            
            component_coverage[module_name] = metrics
        
        return component_coverage
    
    def _extract_module_name(self, file_path: str) -> str:
        """Extract module name from file path."""
        # Convert file path to module name
        # e.g., "ingestion/document_parser.py" -> "ingestion.document_parser"
        path = Path(file_path)
        parts = path.with_suffix('').parts
        
        # Remove common prefixes
        if parts and parts[0] in ['src', 'lib']:
            parts = parts[1:]
        
        return '.'.join(parts)
    
    def _identify_untested_paths(
        self,
        component_coverage: Dict[str, CoverageMetrics]
    ) -> List[str]:
        """
        Identify code paths not covered by any tests.
        
        Requirements: 80.2
        """
        untested_paths = []
        
        for module_name, metrics in component_coverage.items():
            if metrics.missing_statements > 0:
                for line_num in metrics.missing_lines:
                    untested_paths.append(f"{module_name}:{line_num}")
        
        return untested_paths
    
    def _verify_error_path_coverage(self, coverage_data: Dict) -> bool:
        """
        Verify that error handling paths are covered.
        
        Requirements: 80.5
        """
        # Check if exception handlers and error paths are covered
        # This is a heuristic - we look for common error handling patterns
        
        files = coverage_data.get("files", {})
        
        for file_path, file_data in files.items():
            # Get executed lines
            executed_lines = set(file_data.get("executed_lines", []))
            missing_lines = set(file_data.get("missing_lines", []))
            
            # Read file to check for error handling
            try:
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                
                # Check for uncovered exception handlers
                for i, line in enumerate(lines, start=1):
                    line_stripped = line.strip()
                    
                    # Check for exception handling keywords
                    if any(keyword in line_stripped for keyword in ['except', 'raise', 'finally']):
                        if i in missing_lines:
                            # Found uncovered error handling
                            return False
            
            except (FileNotFoundError, IOError):
                continue
        
        return True
    
    def _load_coverage_trend(self) -> Optional[Dict[str, float]]:
        """Load historical coverage trend data."""
        if not self.trend_file.exists():
            return None
        
        try:
            with open(self.trend_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    
    def _update_coverage_trend(self, report: CoverageReport) -> None:
        """
        Update coverage trend with new data.
        
        Requirements: 80.6
        """
        trend = self._load_coverage_trend() or {}
        
        # Add current coverage
        timestamp_key = report.timestamp.isoformat()
        trend[timestamp_key] = report.total_coverage_percent
        
        # Keep only last 100 entries
        if len(trend) > 100:
            sorted_keys = sorted(trend.keys())
            trend = {k: trend[k] for k in sorted_keys[-100:]}
        
        # Save trend
        with open(self.trend_file, 'w') as f:
            json.dump(trend, f, indent=2)
    
    def _get_coverage_config_path(self) -> str:
        """Get path to coverage configuration file."""
        config_path = Path(".coveragerc")
        
        if not config_path.exists():
            # Create default coverage config
            self._create_default_coverage_config(config_path)
        
        return str(config_path)
    
    def _create_default_coverage_config(self, config_path: Path) -> None:
        """Create default .coveragerc configuration."""
        config_content = """[run]
source = .
omit =
    */tests/*
    */test_*.py
    */__pycache__/*
    */venv/*
    */env/*
    setup.py

[report]
precision = 2
show_missing = True
skip_covered = False

[html]
directory = coverage_reports/html

[json]
output = coverage_reports/coverage.json
"""
        
        with open(config_path, 'w') as f:
            f.write(config_content)
    
    def verify_coverage_threshold(
        self,
        report: CoverageReport,
        threshold: float = 90.0
    ) -> Tuple[bool, List[str]]:
        """
        Verify that coverage meets the specified threshold.
        
        Args:
            report: Coverage report to verify
            threshold: Minimum coverage percentage required
        
        Returns:
            Tuple of (meets_threshold, list of components below threshold)
        
        Requirements: 80.4
        """
        meets_threshold = report.meets_threshold(threshold)
        low_coverage_components = report.get_low_coverage_components(threshold)
        
        return meets_threshold, low_coverage_components
    
    def generate_coverage_summary(self, report: CoverageReport) -> str:
        """Generate human-readable coverage summary."""
        lines = [
            "=" * 80,
            "COVERAGE ANALYSIS SUMMARY",
            "=" * 80,
            f"Timestamp: {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total Coverage: {report.total_coverage_percent:.2f}%",
            f"Threshold Met (≥90%): {'✓ YES' if report.meets_threshold() else '✗ NO'}",
            f"Error Paths Covered: {'✓ YES' if report.error_paths_covered else '✗ NO'}",
            "",
            "Component Coverage:",
            "-" * 80,
        ]
        
        # Sort components by coverage percentage
        sorted_components = sorted(
            report.component_coverage.items(),
            key=lambda x: x[1].coverage_percent
        )
        
        for module_name, metrics in sorted_components:
            status = "✓" if metrics.is_adequate else "✗"
            lines.append(
                f"  {status} {module_name:50s} {metrics.coverage_percent:6.2f}% "
                f"({metrics.covered_statements}/{metrics.total_statements})"
            )
        
        if report.untested_paths:
            lines.extend([
                "",
                f"Untested Paths ({len(report.untested_paths)}):",
                "-" * 80,
            ])
            
            # Show first 20 untested paths
            for path in report.untested_paths[:20]:
                lines.append(f"  - {path}")
            
            if len(report.untested_paths) > 20:
                lines.append(f"  ... and {len(report.untested_paths) - 20} more")
        
        if report.coverage_trend:
            lines.extend([
                "",
                "Coverage Trend (last 10 runs):",
                "-" * 80,
            ])
            
            sorted_trend = sorted(report.coverage_trend.items())[-10:]
            for timestamp, coverage in sorted_trend:
                lines.append(f"  {timestamp}: {coverage:.2f}%")
        
        lines.extend([
            "",
            "Reports:",
            f"  HTML: {report.html_report_path}",
            f"  JSON: {report.json_report_path}",
            "=" * 80,
        ])
        
        return "\n".join(lines)
    
    def save_coverage_report(self, report: CoverageReport, filename: str = "coverage_summary.txt") -> str:
        """Save coverage summary to file."""
        summary = self.generate_coverage_summary(report)
        
        output_path = self.output_dir / filename
        with open(output_path, 'w') as f:
            f.write(summary)
        
        return str(output_path)
