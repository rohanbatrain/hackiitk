#!/usr/bin/env python3
"""
Automated test validation script for all policy types.

This script runs all integration tests for ISMS, Data Privacy, Patch Management,
and Risk Management policies, then generates a comprehensive test report with
pass/fail status for each policy type.

**Validates: Requirement 19.6**

Usage:
    python tests/integration/run_all_policy_tests.py
    python tests/integration/run_all_policy_tests.py --verbose
    python tests/integration/run_all_policy_tests.py --output report.json
"""

import sys
import os
import json
import argparse
from pathlib import Path
from datetime import datetime
import subprocess
from typing import Dict, List, Tuple


class PolicyTestRunner:
    """Runs all policy integration tests and generates validation report."""
    
    def __init__(self, verbose: bool = False, output_file: str = None):
        """Initialize test runner.
        
        Args:
            verbose: Enable verbose output
            output_file: Path to save JSON report
        """
        self.verbose = verbose
        self.output_file = output_file
        self.results = {
            'test_date': datetime.now().isoformat(),
            'policy_tests': {},
            'summary': {
                'total_tests': 0,
                'passed': 0,
                'failed': 0,
                'skipped': 0
            }
        }
    
    def run_pytest(self, test_file: str, test_name: str) -> Tuple[bool, str, Dict]:
        """Run pytest for a specific test file.
        
        Args:
            test_file: Path to test file
            test_name: Name of the test for reporting
            
        Returns:
            Tuple of (success, output, details)
        """
        print(f"\n{'='*70}")
        print(f"Running {test_name}...")
        print(f"{'='*70}")
        
        # Build pytest command
        cmd = [
            sys.executable, '-m', 'pytest',
            test_file,
            '-v',
            '--tb=short',
            '--color=yes' if self.verbose else '--color=no',
            '-s' if self.verbose else '',
            '--json-report',
            '--json-report-file=test_report.json'
        ]
        
        # Remove empty strings
        cmd = [c for c in cmd if c]
        
        try:
            # Run pytest
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            success = result.returncode == 0
            output = result.stdout + result.stderr
            
            # Parse output for key metrics
            details = self._parse_pytest_output(output)
            
            if self.verbose:
                print(output)
            
            return success, output, details
            
        except subprocess.TimeoutExpired:
            return False, "Test timed out after 10 minutes", {'error': 'timeout'}
        except Exception as e:
            return False, f"Test execution failed: {str(e)}", {'error': str(e)}
    
    def _parse_pytest_output(self, output: str) -> Dict:
        """Parse pytest output for key metrics.
        
        Args:
            output: Pytest output text
            
        Returns:
            Dictionary with parsed metrics
        """
        details = {
            'tests_run': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'errors': []
        }
        
        # Parse summary line
        for line in output.split('\n'):
            if 'passed' in line.lower() or 'failed' in line.lower():
                # Extract numbers from summary
                if 'passed' in line:
                    try:
                        passed = int(line.split('passed')[0].strip().split()[-1])
                        details['passed'] = passed
                    except:
                        pass
                
                if 'failed' in line:
                    try:
                        failed = int(line.split('failed')[0].strip().split()[-1])
                        details['failed'] = failed
                    except:
                        pass
                
                if 'skipped' in line:
                    try:
                        skipped = int(line.split('skipped')[0].strip().split()[-1])
                        details['skipped'] = skipped
                    except:
                        pass
            
            # Capture error messages
            if 'FAILED' in line or 'ERROR' in line:
                details['errors'].append(line.strip())
        
        details['tests_run'] = details['passed'] + details['failed'] + details['skipped']
        
        return details
    
    def run_all_tests(self) -> bool:
        """Run all policy integration tests.
        
        Returns:
            True if all tests passed, False otherwise
        """
        # Define test files
        test_files = [
            ('tests/integration/test_isms_policy.py', 'ISMS Policy Analysis'),
            ('tests/integration/test_privacy_policy.py', 'Data Privacy Policy Analysis'),
            ('tests/integration/test_patch_policy.py', 'Patch Management Policy Analysis'),
            ('tests/integration/test_risk_policy.py', 'Risk Management Policy Analysis')
        ]
        
        all_passed = True
        
        for test_file, test_name in test_files:
            # Check if test file exists
            if not Path(test_file).exists():
                print(f"\n⚠ Warning: Test file not found: {test_file}")
                self.results['policy_tests'][test_name] = {
                    'status': 'skipped',
                    'reason': 'Test file not found'
                }
                self.results['summary']['skipped'] += 1
                continue
            
            # Run test
            success, output, details = self.run_pytest(test_file, test_name)
            
            # Record results
            self.results['policy_tests'][test_name] = {
                'status': 'passed' if success else 'failed',
                'test_file': test_file,
                'details': details,
                'output_summary': output[-500:] if len(output) > 500 else output
            }
            
            self.results['summary']['total_tests'] += 1
            if success:
                self.results['summary']['passed'] += 1
                print(f"\n✓ {test_name} PASSED")
            else:
                self.results['summary']['failed'] += 1
                all_passed = False
                print(f"\n✗ {test_name} FAILED")
                if details.get('errors'):
                    print("  Errors:")
                    for error in details['errors'][:3]:  # Show first 3 errors
                        print(f"    - {error}")
        
        return all_passed
    
    def generate_report(self):
        """Generate and display test report."""
        print(f"\n{'='*70}")
        print("TEST VALIDATION REPORT")
        print(f"{'='*70}")
        print(f"Test Date: {self.results['test_date']}")
        print(f"\nSummary:")
        print(f"  Total Tests: {self.results['summary']['total_tests']}")
        print(f"  Passed: {self.results['summary']['passed']}")
        print(f"  Failed: {self.results['summary']['failed']}")
        print(f"  Skipped: {self.results['summary']['skipped']}")
        
        print(f"\nPolicy Test Results:")
        for policy_name, result in self.results['policy_tests'].items():
            status_symbol = '✓' if result['status'] == 'passed' else '✗' if result['status'] == 'failed' else '⊘'
            print(f"  {status_symbol} {policy_name}: {result['status'].upper()}")
            
            if 'details' in result:
                details = result['details']
                if details.get('tests_run', 0) > 0:
                    print(f"      Tests run: {details['tests_run']}, "
                          f"Passed: {details['passed']}, "
                          f"Failed: {details['failed']}, "
                          f"Skipped: {details['skipped']}")
        
        # Overall status
        print(f"\n{'='*70}")
        if self.results['summary']['failed'] == 0 and self.results['summary']['passed'] > 0:
            print("✓ ALL TESTS PASSED")
        elif self.results['summary']['failed'] > 0:
            print("✗ SOME TESTS FAILED")
        else:
            print("⚠ NO TESTS RUN")
        print(f"{'='*70}\n")
        
        # Save JSON report if requested
        if self.output_file:
            self._save_json_report()
    
    def _save_json_report(self):
        """Save test results to JSON file."""
        try:
            output_path = Path(self.output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2)
            
            print(f"✓ Test report saved to: {output_path}")
        except Exception as e:
            print(f"✗ Failed to save report: {e}")


def main():
    """Main entry point for test validation script."""
    parser = argparse.ArgumentParser(
        description='Run all policy integration tests and generate validation report'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='test_validation_report.json',
        help='Path to save JSON report (default: test_validation_report.json)'
    )
    
    args = parser.parse_args()
    
    # Create test runner
    runner = PolicyTestRunner(verbose=args.verbose, output_file=args.output)
    
    # Run all tests
    print("Starting automated policy test validation...")
    all_passed = runner.run_all_tests()
    
    # Generate report
    runner.generate_report()
    
    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)


if __name__ == '__main__':
    main()
