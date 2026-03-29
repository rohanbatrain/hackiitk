#!/usr/bin/env python3
"""
Validation script for test policy gap analysis outputs.

This script compares actual gap analysis outputs against expected outputs
to verify that the Offline Policy Gap Analyzer meets the 80% detection
requirement (Requirement 19.5).

Usage:
    python validate_outputs.py --policy isms --output path/to/gap_analysis_report.json
    python validate_outputs.py --policy privacy --output path/to/gap_analysis_report.json
    python validate_outputs.py --policy patch --output path/to/gap_analysis_report.json
    python validate_outputs.py --policy risk --output path/to/gap_analysis_report.json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple


class GapValidator:
    """Validates gap analysis outputs against expected results."""
    
    def __init__(self, policy_type: str, expected_gaps_path: Path):
        """
        Initialize validator with policy type and expected gaps.
        
        Args:
            policy_type: Type of policy (isms, privacy, patch, risk)
            expected_gaps_path: Path to expected gaps JSON file
        """
        self.policy_type = policy_type
        self.expected_gaps_path = expected_gaps_path
        self.expected_data = self._load_expected_gaps()
        
    def _load_expected_gaps(self) -> Dict:
        """Load expected gaps from JSON file."""
        with open(self.expected_gaps_path, 'r') as f:
            return json.load(f)
    
    def _load_actual_gaps(self, actual_output_path: Path) -> Dict:
        """Load actual gap analysis output from JSON file."""
        with open(actual_output_path, 'r') as f:
            return json.load(f)
    
    def _extract_gap_ids(self, gaps: List[Dict]) -> Set[str]:
        """Extract subcategory IDs from gap list."""
        return {gap['subcategory_id'] for gap in gaps}
    
    def validate(self, actual_output_path: Path) -> Tuple[bool, Dict]:
        """
        Validate actual output against expected gaps.
        
        Args:
            actual_output_path: Path to actual gap analysis report JSON
            
        Returns:
            Tuple of (passed: bool, results: Dict)
        """
        actual_data = self._load_actual_gaps(actual_output_path)
        
        # Extract gap IDs
        expected_gap_ids = self._extract_gap_ids(self.expected_data['expected_gaps'])
        actual_gap_ids = self._extract_gap_ids(actual_data.get('gaps', []))
        
        # Calculate detection metrics
        detected_gaps = expected_gap_ids.intersection(actual_gap_ids)
        missed_gaps = expected_gap_ids - actual_gap_ids
        false_positives = actual_gap_ids - expected_gap_ids
        
        total_expected = len(expected_gap_ids)
        total_detected = len(detected_gaps)
        detection_rate = (total_detected / total_expected * 100) if total_expected > 0 else 0
        
        # Check if detection rate meets threshold
        threshold = self.expected_data['detection_threshold_percentage']
        passed = detection_rate >= threshold
        
        # Build results
        results = {
            'policy_type': self.policy_type,
            'policy_name': self.expected_data['policy_name'],
            'total_expected_gaps': total_expected,
            'total_detected_gaps': total_detected,
            'detection_rate_percentage': round(detection_rate, 2),
            'detection_threshold_percentage': threshold,
            'passed': passed,
            'detected_gaps': sorted(list(detected_gaps)),
            'missed_gaps': sorted(list(missed_gaps)),
            'false_positives': sorted(list(false_positives)),
            'false_positive_count': len(false_positives)
        }
        
        return passed, results
    
    def print_results(self, results: Dict) -> None:
        """Print validation results in human-readable format."""
        print("\n" + "="*80)
        print(f"Gap Detection Validation Results: {results['policy_name']}")
        print("="*80)
        
        print(f"\nPolicy Type: {results['policy_type']}")
        print(f"Total Expected Gaps: {results['total_expected_gaps']}")
        print(f"Total Detected Gaps: {results['total_detected_gaps']}")
        print(f"Detection Rate: {results['detection_rate_percentage']}%")
        print(f"Required Threshold: {results['detection_threshold_percentage']}%")
        
        # Pass/Fail status
        status = "✓ PASSED" if results['passed'] else "✗ FAILED"
        print(f"\nValidation Status: {status}")
        
        # Detected gaps
        if results['detected_gaps']:
            print(f"\n✓ Detected Gaps ({len(results['detected_gaps'])}):")
            for gap_id in results['detected_gaps']:
                print(f"  - {gap_id}")
        
        # Missed gaps
        if results['missed_gaps']:
            print(f"\n✗ Missed Gaps ({len(results['missed_gaps'])}):")
            for gap_id in results['missed_gaps']:
                # Find gap details from expected data
                gap_detail = next(
                    (g for g in self.expected_data['expected_gaps'] 
                     if g['subcategory_id'] == gap_id),
                    None
                )
                if gap_detail:
                    print(f"  - {gap_id}: {gap_detail['description'][:80]}...")
                    print(f"    Severity: {gap_detail['severity']}")
                else:
                    print(f"  - {gap_id}")
        
        # False positives
        if results['false_positives']:
            print(f"\n⚠ False Positives ({len(results['false_positives'])}):")
            print("  (Gaps reported but not intentionally planted)")
            for gap_id in results['false_positives']:
                print(f"  - {gap_id}")
        
        print("\n" + "="*80)
        
        # Additional notes
        if 'notes' in self.expected_data:
            print("\nNotes:")
            for note in self.expected_data['notes']:
                print(f"  • {note}")
            print()


def main():
    """Main entry point for validation script."""
    parser = argparse.ArgumentParser(
        description='Validate gap analysis outputs against expected results'
    )
    parser.add_argument(
        '--policy',
        required=True,
        choices=['isms', 'privacy', 'patch', 'risk'],
        help='Policy type to validate'
    )
    parser.add_argument(
        '--output',
        required=True,
        type=Path,
        help='Path to actual gap analysis report JSON file'
    )
    parser.add_argument(
        '--expected-dir',
        type=Path,
        default=Path(__file__).parent,
        help='Directory containing expected gaps JSON files (default: script directory)'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results in JSON format'
    )
    
    args = parser.parse_args()
    
    # Determine expected gaps file
    expected_gaps_file = args.expected_dir / f"expected_{args.policy}_gaps.json"
    
    if not expected_gaps_file.exists():
        print(f"Error: Expected gaps file not found: {expected_gaps_file}", file=sys.stderr)
        sys.exit(1)
    
    if not args.output.exists():
        print(f"Error: Actual output file not found: {args.output}", file=sys.stderr)
        sys.exit(1)
    
    # Run validation
    validator = GapValidator(args.policy, expected_gaps_file)
    
    try:
        passed, results = validator.validate(args.output)
        
        if args.json:
            # Output JSON results
            print(json.dumps(results, indent=2))
        else:
            # Output human-readable results
            validator.print_results(results)
        
        # Exit with appropriate code
        sys.exit(0 if passed else 1)
        
    except Exception as e:
        print(f"Error during validation: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(2)


if __name__ == '__main__':
    main()
