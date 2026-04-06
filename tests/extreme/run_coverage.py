#!/usr/bin/env python3
"""
Standalone script for running coverage analysis on the test suite.

This script runs all tests with coverage measurement and generates
comprehensive coverage reports.

Requirements: 80.1, 80.2, 80.3, 80.4, 80.5, 80.6

Usage:
    python tests/extreme/run_coverage.py
    python tests/extreme/run_coverage.py --categories stress chaos
    python tests/extreme/run_coverage.py --threshold 95
"""

import argparse
import sys
from pathlib import Path

from tests.extreme.coverage_analyzer import CoverageAnalyzer


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Run tests with coverage measurement",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--categories',
        nargs='+',
        choices=['stress', 'chaos', 'adversarial', 'boundary', 'performance', 'property', 'unit', 'integration'],
        help='Test categories to measure coverage for (default: all)'
    )
    
    parser.add_argument(
        '--threshold',
        type=float,
        default=90.0,
        help='Minimum coverage threshold percentage (default: 90.0)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='coverage_reports',
        help='Output directory for coverage reports (default: coverage_reports)'
    )
    
    parser.add_argument(
        '--baseline-dir',
        type=str,
        default='coverage_baselines',
        help='Directory for baseline coverage data (default: coverage_baselines)'
    )
    
    parser.add_argument(
        '--pytest-args',
        nargs='+',
        help='Additional pytest arguments'
    )
    
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()
    
    print("=" * 80)
    print("COVERAGE ANALYSIS")
    print("=" * 80)
    print(f"Threshold: {args.threshold}%")
    print(f"Output directory: {args.output_dir}")
    if args.categories:
        print(f"Categories: {', '.join(args.categories)}")
    print("=" * 80)
    print()
    
    # Create coverage analyzer
    analyzer = CoverageAnalyzer(
        source_dirs=[
            'ingestion', 'reference_builder', 'retrieval',
            'analysis', 'revision', 'reporting', 'models',
            'cli', 'utils', 'orchestration'
        ],
        output_dir=args.output_dir,
        baseline_dir=args.baseline_dir
    )
    
    # Run tests with coverage
    print("Running tests with coverage measurement...")
    print("-" * 80)
    exit_code, output = analyzer.run_tests_with_coverage(
        test_categories=args.categories,
        pytest_args=args.pytest_args
    )
    
    print(output)
    print("-" * 80)
    print(f"Tests completed with exit code: {exit_code}")
    print()
    
    # Generate coverage report
    print("Generating coverage report...")
    try:
        coverage_report = analyzer.generate_coverage_report()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    # Print summary
    summary = analyzer.generate_coverage_summary(coverage_report)
    print(summary)
    
    # Save summary to file
    summary_path = analyzer.save_coverage_report(coverage_report)
    print(f"\nCoverage summary saved to: {summary_path}")
    
    # Verify threshold
    meets_threshold, low_coverage = analyzer.verify_coverage_threshold(
        coverage_report,
        threshold=args.threshold
    )
    
    if not meets_threshold:
        print(f"\n⚠ WARNING: Coverage threshold not met ({args.threshold}% required)")
        print(f"Components below threshold:")
        for component in low_coverage:
            metrics = coverage_report.component_coverage[component]
            print(f"  - {component}: {metrics.coverage_percent:.2f}%")
        sys.exit(1)
    else:
        print(f"\n✓ Coverage threshold met (≥{args.threshold}%)")
        sys.exit(0)


if __name__ == '__main__':
    main()
