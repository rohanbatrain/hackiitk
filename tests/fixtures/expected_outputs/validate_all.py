#!/usr/bin/env python3
"""
Batch validation script for all test policies.

This script runs gap analysis on all test policies and validates the outputs
against expected results.

Usage:
    python validate_all.py --output-dir path/to/outputs
    python validate_all.py --analyze-and-validate  # Run analysis then validate
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List


class BatchValidator:
    """Batch validator for all test policies."""
    
    POLICIES = ['isms', 'privacy', 'patch', 'risk']
    
    POLICY_FILES = {
        'isms': 'isms_policy.md',
        'privacy': 'privacy_policy.md',
        'patch': 'patch_policy.md',
        'risk': 'risk_policy.md'
    }
    
    def __init__(self, fixtures_dir: Path, output_dir: Path):
        """
        Initialize batch validator.
        
        Args:
            fixtures_dir: Directory containing test fixtures
            output_dir: Directory containing analysis outputs
        """
        self.fixtures_dir = fixtures_dir
        self.output_dir = output_dir
        self.expected_dir = fixtures_dir / 'expected_outputs'
        self.policies_dir = fixtures_dir / 'dummy_policies'
        
    def run_analysis(self, policy_type: str) -> Path:
        """
        Run gap analysis on a test policy.
        
        Args:
            policy_type: Type of policy to analyze
            
        Returns:
            Path to output directory
        """
        policy_file = self.policies_dir / self.POLICY_FILES[policy_type]
        
        if not policy_file.exists():
            raise FileNotFoundError(f"Policy file not found: {policy_file}")
        
        print(f"\n{'='*80}")
        print(f"Running analysis on {policy_type} policy...")
        print(f"{'='*80}")
        
        # Run analysis script
        cmd = [
            sys.executable,
            'examples/run_analysis.py',
            str(policy_file),
            '--output-dir', str(self.output_dir)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Analysis failed for {policy_type}:")
            print(result.stderr)
            raise RuntimeError(f"Analysis failed for {policy_type}")
        
        print(result.stdout)
        
        # Find the output directory (most recent for this policy)
        output_dirs = sorted(
            self.output_dir.glob(f"{policy_type}_policy_*"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        if not output_dirs:
            raise FileNotFoundError(f"No output directory found for {policy_type}")
        
        return output_dirs[0]
    
    def validate_policy(self, policy_type: str, output_path: Path) -> Dict:
        """
        Validate gap analysis output for a policy.
        
        Args:
            policy_type: Type of policy
            output_path: Path to gap analysis report JSON
            
        Returns:
            Validation results dictionary
        """
        print(f"\n{'='*80}")
        print(f"Validating {policy_type} policy output...")
        print(f"{'='*80}")
        
        # Run validation script
        cmd = [
            sys.executable,
            str(self.expected_dir / 'validate_outputs.py'),
            '--policy', policy_type,
            '--output', str(output_path),
            '--json'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 2:
            # Validation script error
            print(f"Validation error for {policy_type}:")
            print(result.stderr)
            raise RuntimeError(f"Validation error for {policy_type}")
        
        # Parse JSON results
        results = json.loads(result.stdout)
        
        # Print summary
        status = "✓ PASSED" if results['passed'] else "✗ FAILED"
        print(f"\n{status}: {results['policy_name']}")
        print(f"Detection Rate: {results['detection_rate_percentage']}% "
              f"(threshold: {results['detection_threshold_percentage']}%)")
        print(f"Detected: {results['total_detected_gaps']}/{results['total_expected_gaps']} gaps")
        
        if results['missed_gaps']:
            print(f"Missed: {', '.join(results['missed_gaps'])}")
        
        if results['false_positives']:
            print(f"False Positives: {len(results['false_positives'])}")
        
        return results
    
    def run_all(self, analyze: bool = False) -> Dict[str, Dict]:
        """
        Run validation on all test policies.
        
        Args:
            analyze: If True, run analysis before validation
            
        Returns:
            Dictionary of validation results by policy type
        """
        all_results = {}
        
        for policy_type in self.POLICIES:
            try:
                if analyze:
                    # Run analysis
                    output_dir = self.run_analysis(policy_type)
                    output_file = output_dir / 'gap_analysis_report.json'
                else:
                    # Find existing output
                    output_dirs = sorted(
                        self.output_dir.glob(f"{policy_type}_policy_*"),
                        key=lambda p: p.stat().st_mtime,
                        reverse=True
                    )
                    
                    if not output_dirs:
                        print(f"Warning: No output found for {policy_type}, skipping...")
                        continue
                    
                    output_file = output_dirs[0] / 'gap_analysis_report.json'
                
                if not output_file.exists():
                    print(f"Warning: Output file not found: {output_file}, skipping...")
                    continue
                
                # Validate
                results = self.validate_policy(policy_type, output_file)
                all_results[policy_type] = results
                
            except Exception as e:
                print(f"Error processing {policy_type}: {e}")
                all_results[policy_type] = {
                    'passed': False,
                    'error': str(e)
                }
        
        return all_results
    
    def print_summary(self, all_results: Dict[str, Dict]) -> None:
        """Print summary of all validation results."""
        print("\n" + "="*80)
        print("VALIDATION SUMMARY")
        print("="*80)
        
        total_policies = len(all_results)
        passed_policies = sum(1 for r in all_results.values() if r.get('passed', False))
        
        print(f"\nTotal Policies Tested: {total_policies}")
        print(f"Passed: {passed_policies}")
        print(f"Failed: {total_policies - passed_policies}")
        
        print("\nDetailed Results:")
        for policy_type, results in all_results.items():
            if 'error' in results:
                print(f"  {policy_type}: ERROR - {results['error']}")
            else:
                status = "✓ PASS" if results['passed'] else "✗ FAIL"
                rate = results.get('detection_rate_percentage', 0)
                print(f"  {policy_type}: {status} ({rate}% detection rate)")
        
        print("\n" + "="*80)
        
        # Overall pass/fail
        if passed_policies == total_policies:
            print("\n✓ ALL TESTS PASSED")
            print("The Offline Policy Gap Analyzer meets the 80% detection requirement.")
        else:
            print("\n✗ SOME TESTS FAILED")
            print("The analyzer does not meet the 80% detection requirement for all policies.")
        
        print()


def main():
    """Main entry point for batch validation."""
    parser = argparse.ArgumentParser(
        description='Batch validation for all test policies'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path('outputs'),
        help='Directory containing analysis outputs (default: outputs/)'
    )
    parser.add_argument(
        '--fixtures-dir',
        type=Path,
        default=Path(__file__).parent.parent,
        help='Directory containing test fixtures (default: tests/fixtures/)'
    )
    parser.add_argument(
        '--analyze-and-validate',
        action='store_true',
        help='Run analysis on test policies before validation'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results in JSON format'
    )
    
    args = parser.parse_args()
    
    # Create validator
    validator = BatchValidator(args.fixtures_dir, args.output_dir)
    
    try:
        # Run validation
        all_results = validator.run_all(analyze=args.analyze_and_validate)
        
        if args.json:
            # Output JSON results
            print(json.dumps(all_results, indent=2))
        else:
            # Print summary
            validator.print_summary(all_results)
        
        # Exit with appropriate code
        all_passed = all(r.get('passed', False) for r in all_results.values())
        sys.exit(0 if all_passed else 1)
        
    except Exception as e:
        print(f"Error during batch validation: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(2)


if __name__ == '__main__':
    main()
