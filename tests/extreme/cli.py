"""
Command-Line Interface for Extreme Testing Framework

This module provides a CLI for running extreme tests with various options.
"""

import argparse
import sys
import logging
from pathlib import Path

from .config import TestConfig
from .runner import MasterTestRunner
from .reporter import ExtremeTestReporter


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Extreme Testing Framework for Offline Policy Gap Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all tests
  python -m tests.extreme.cli
  
  # Run specific categories
  python -m tests.extreme.cli --categories stress chaos
  
  # Run tests for specific requirements
  python -m tests.extreme.cli --requirements 1.1 1.2 2.1
  
  # Run with verbose output
  python -m tests.extreme.cli --verbose
  
  # Run with fail-fast mode
  python -m tests.extreme.cli --fail-fast
        """
    )
    
    parser.add_argument(
        '--categories',
        nargs='+',
        choices=['stress', 'chaos', 'adversarial', 'boundary', 'performance', 'property'],
        help='Test categories to run (default: all)'
    )
    
    parser.add_argument(
        '--requirements',
        nargs='+',
        help='Specific requirement IDs to test (e.g., 1.1 2.3 3.5)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='test_outputs/extreme',
        help='Output directory for test results (default: test_outputs/extreme)'
    )
    
    parser.add_argument(
        '--concurrency',
        type=int,
        default=4,
        help='Number of concurrent test workers (default: 4)'
    )
    
    parser.add_argument(
        '--timeout',
        type=int,
        default=3600,
        help='Timeout for individual tests in seconds (default: 3600)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--fail-fast',
        action='store_true',
        help='Stop execution on first failure'
    )
    
    parser.add_argument(
        '--no-html',
        action='store_true',
        help='Disable HTML report generation'
    )
    
    parser.add_argument(
        '--no-json',
        action='store_true',
        help='Disable JSON report generation'
    )
    
    parser.add_argument(
        '--no-junit',
        action='store_true',
        help='Disable JUnit XML report generation'
    )
    
    return parser.parse_args()


def main():
    """Main entry point for CLI."""
    args = parse_args()
    
    # Create configuration
    config = TestConfig(
        categories=args.categories or ['stress', 'chaos', 'adversarial', 'boundary', 'performance', 'property'],
        requirements=args.requirements or [],
        output_dir=args.output_dir,
        concurrency=args.concurrency,
        timeout_seconds=args.timeout,
        verbose=args.verbose,
        fail_fast=args.fail_fast,
        generate_html_report=not args.no_html,
        generate_json_report=not args.no_json,
        generate_junit_xml=not args.no_junit
    )
    
    # Create runner
    runner = MasterTestRunner(config)
    
    try:
        # Run tests
        report = runner.run_all_tests()
        
        # Generate reports
        if any([config.generate_html_report, config.generate_json_report, config.generate_junit_xml]):
            reporter = ExtremeTestReporter(config.output_dir)
            report_files = reporter.generate_report(report)
            
            print("\n" + "=" * 80)
            print("REPORTS GENERATED")
            print("=" * 80)
            for format_name, file_path in report_files.items():
                print(f"{format_name}: {file_path}")
            print("=" * 80)
        
        # Exit with appropriate code
        if report.failed > 0 or report.errors > 0:
            sys.exit(1)
        else:
            sys.exit(0)
    
    except KeyboardInterrupt:
        print("\n\nTest execution interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\nFatal error during test execution: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
