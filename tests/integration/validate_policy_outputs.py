#!/usr/bin/env python3
"""
Output validation script for policy analysis results.

This script compares generated gap analysis outputs against expected results
to validate detection accuracy for each policy type.

**Validates: Requirement 19.6**

Usage:
    python tests/integration/validate_policy_outputs.py <output_dir>
    python tests/integration/validate_policy_outputs.py outputs/isms_20240328_120000
"""

import sys
import json
from pathlib import Path
from typing import Dict, Set, Tuple


class OutputValidator:
    """Validates policy analysis outputs against expected results."""
    
    def __init__(self, output_dir: str):
        """Initialize validator.
        
        Args:
            output_dir: Path to analysis output directory
        """
        self.output_dir = Path(output_dir)
        self.policy_type = self._detect_policy_type()
        self.expected_gaps = self._load_expected_gaps()
    
    def _detect_policy_type(self) -> str:
        """Detect policy type from output directory or files."""
        # Check directory name
        dir_name = self.output_dir.name.lower()
        if 'isms' in dir_name:
            return 'isms'
        elif 'privacy' in dir_name:
            return 'privacy'
        elif 'patch' in dir_name:
            return 'patch'
        elif 'risk' in dir_name:
            return 'risk'
        
        # Check gap report for clues
        gap_report_path = self.output_dir / 'gap_analysis_report.json'
        if gap_report_path.exists():
            with open(gap_report_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                input_file = data.get('input_file', '').lower()
                if 'isms' in input_file:
                    return 'isms'
                elif 'privacy' in input_file:
                    return 'privacy'
                elif 'patch' in input_file:
                    return 'patch'
                elif 'risk' in input_file:
                    return 'risk'
        
        return 'unknown'
    
    def _load_expected_gaps(self) -> Dict:
        """Load expected gaps for detected policy type."""
        expected_files = {
            'isms': 'tests/fixtures/expected_outputs/expected_isms_gaps.json',
            'privacy': 'tests/fixtures/expected_outputs/expected_privacy_gaps.json',
            'patch': 'tests/fixtures/expected_outputs/expected_patch_gaps.json',
            'risk': 'tests/fixtures/expected_outputs/expected_risk_gaps.json'
        }
        
        if self.policy_type not in expected_files:
            return {}
        
        expected_path = Path(expected_files[self.policy_type])
        if not expected_path.exists():
            return {}
        
        with open(expected_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def validate(self) -> Tuple[bool, Dict]:
        """Validate outputs against expected results.
        
        Returns:
            Tuple of (passed, validation_results)
        """
        results = {
            'policy_type': self.policy_type,
            'output_dir': str(self.output_dir),
            'validations': {}
        }
        
        # Validate gap detection
        gap_validation = self._validate_gap_detection()
        results['validations']['gap_detection'] = gap_validation
        
        # Validate output files
        file_validation = self._validate_output_files()
        results['validations']['output_files'] = file_validation
        
        # Validate revised policy
        policy_validation = self._validate_revised_policy()
        results['validations']['revised_policy'] = policy_validation
        
        # Validate roadmap
        roadmap_validation = self._validate_roadmap()
        results['validations']['roadmap'] = roadmap_validation
        
        # Overall pass/fail
        all_passed = all(
            v.get('passed', False) 
            for v in results['validations'].values()
        )
        
        return all_passed, results
    
    def _validate_gap_detection(self) -> Dict:
        """Validate gap detection accuracy."""
        gap_report_path = self.output_dir / 'gap_analysis_report.json'
        
        if not gap_report_path.exists():
            return {
                'passed': False,
                'error': 'Gap report not found'
            }
        
        if not self.expected_gaps:
            return {
                'passed': True,
                'warning': 'No expected gaps to validate against'
            }
        
        # Load generated gaps
        with open(gap_report_path, 'r', encoding='utf-8') as f:
            gap_data = json.load(f)
        
        identified_gaps = set(gap['subcategory_id'] for gap in gap_data.get('gaps', []))
        expected_gaps = set(gap['subcategory_id'] for gap in self.expected_gaps.get('expected_gaps', []))
        
        # Calculate metrics
        detected = identified_gaps.intersection(expected_gaps)
        missed = expected_gaps - identified_gaps
        false_positives = identified_gaps - expected_gaps
        
        detection_rate = len(detected) / len(expected_gaps) if expected_gaps else 0
        threshold = self.expected_gaps.get('detection_threshold_percentage', 80) / 100
        
        passed = detection_rate >= threshold
        
        return {
            'passed': passed,
            'detection_rate': f"{detection_rate:.1%}",
            'threshold': f"{threshold:.1%}",
            'detected_count': len(detected),
            'expected_count': len(expected_gaps),
            'missed_count': len(missed),
            'false_positive_count': len(false_positives),
            'detected_gaps': sorted(detected),
            'missed_gaps': sorted(missed),
            'false_positives': sorted(false_positives)
        }
    
    def _validate_output_files(self) -> Dict:
        """Validate that all required output files exist."""
        required_files = [
            'gap_analysis_report.md',
            'gap_analysis_report.json',
            'revised_policy.md',
            'implementation_roadmap.md',
            'implementation_roadmap.json'
        ]
        
        missing_files = []
        empty_files = []
        
        for filename in required_files:
            file_path = self.output_dir / filename
            if not file_path.exists():
                missing_files.append(filename)
            elif file_path.stat().st_size == 0:
                empty_files.append(filename)
        
        passed = len(missing_files) == 0 and len(empty_files) == 0
        
        return {
            'passed': passed,
            'required_files': required_files,
            'missing_files': missing_files,
            'empty_files': empty_files
        }
    
    def _validate_revised_policy(self) -> Dict:
        """Validate revised policy content."""
        revised_policy_path = self.output_dir / 'revised_policy.md'
        
        if not revised_policy_path.exists():
            return {
                'passed': False,
                'error': 'Revised policy not found'
            }
        
        with open(revised_policy_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for mandatory warning
        has_warning = any(
            keyword in content
            for keyword in ['IMPORTANT:', 'WARNING:', 'AI system', 'generated', 'review']
        )
        
        # Check for reasonable length
        has_content = len(content) > 1000
        
        passed = has_warning and has_content
        
        return {
            'passed': passed,
            'has_warning': has_warning,
            'has_content': has_content,
            'content_length': len(content)
        }
    
    def _validate_roadmap(self) -> Dict:
        """Validate implementation roadmap."""
        roadmap_path = self.output_dir / 'implementation_roadmap.json'
        
        if not roadmap_path.exists():
            return {
                'passed': False,
                'error': 'Roadmap not found'
            }
        
        with open(roadmap_path, 'r', encoding='utf-8') as f:
            roadmap_data = json.load(f)
        
        # Check for required sections
        has_immediate = 'immediate_actions' in roadmap_data
        has_near_term = 'near_term_actions' in roadmap_data
        has_medium_term = 'medium_term_actions' in roadmap_data
        
        # Check for actions
        total_actions = (
            len(roadmap_data.get('immediate_actions', [])) +
            len(roadmap_data.get('near_term_actions', [])) +
            len(roadmap_data.get('medium_term_actions', []))
        )
        
        has_actions = total_actions > 0
        
        passed = has_immediate and has_near_term and has_medium_term and has_actions
        
        return {
            'passed': passed,
            'has_immediate': has_immediate,
            'has_near_term': has_near_term,
            'has_medium_term': has_medium_term,
            'total_actions': total_actions,
            'immediate_count': len(roadmap_data.get('immediate_actions', [])),
            'near_term_count': len(roadmap_data.get('near_term_actions', [])),
            'medium_term_count': len(roadmap_data.get('medium_term_actions', []))
        }
    
    def print_report(self, results: Dict):
        """Print validation report."""
        print(f"\n{'='*70}")
        print(f"OUTPUT VALIDATION REPORT")
        print(f"{'='*70}")
        print(f"Policy Type: {results['policy_type'].upper()}")
        print(f"Output Directory: {results['output_dir']}")
        
        for validation_name, validation_result in results['validations'].items():
            print(f"\n{validation_name.replace('_', ' ').title()}:")
            
            passed = validation_result.get('passed', False)
            status = '✓ PASSED' if passed else '✗ FAILED'
            print(f"  Status: {status}")
            
            # Print key metrics
            for key, value in validation_result.items():
                if key not in ['passed', 'detected_gaps', 'missed_gaps', 'false_positives']:
                    print(f"  {key.replace('_', ' ').title()}: {value}")
            
            # Print gap details if available
            if 'detected_gaps' in validation_result and validation_result['detected_gaps']:
                print(f"  Detected Gaps: {', '.join(validation_result['detected_gaps'][:5])}")
                if len(validation_result['detected_gaps']) > 5:
                    print(f"    ... and {len(validation_result['detected_gaps']) - 5} more")
            
            if 'missed_gaps' in validation_result and validation_result['missed_gaps']:
                print(f"  Missed Gaps: {', '.join(validation_result['missed_gaps'])}")
        
        print(f"\n{'='*70}\n")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python validate_policy_outputs.py <output_dir>")
        print("\nExample:")
        print("  python validate_policy_outputs.py outputs/isms_20240328_120000")
        sys.exit(1)
    
    output_dir = sys.argv[1]
    
    if not Path(output_dir).exists():
        print(f"Error: Output directory not found: {output_dir}")
        sys.exit(1)
    
    # Create validator
    validator = OutputValidator(output_dir)
    
    # Validate outputs
    print(f"Validating outputs in: {output_dir}")
    passed, results = validator.validate()
    
    # Print report
    validator.print_report(results)
    
    # Exit with appropriate code
    if passed:
        print("✓ All validations passed")
        sys.exit(0)
    else:
        print("✗ Some validations failed")
        sys.exit(1)


if __name__ == '__main__':
    main()
