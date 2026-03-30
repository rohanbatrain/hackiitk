"""
Example Usage of Oracle Validator

This script demonstrates how to use the Oracle Validator to validate
gap analysis accuracy against known-good test cases.

**Validates: Requirements 71.1, 71.2, 71.3, 71.4, 71.5**
"""

import logging
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from tests.extreme.support.oracle_validator import OracleValidator
from models.domain import GapAnalysisReport, GapDetail


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def create_mock_gap_analysis_report(oracle_test_case):
    """
    Create a mock gap analysis report for demonstration.
    
    In real usage, this would be replaced with actual gap analysis.
    """
    # For demonstration, create a report that matches the oracle
    gap_details = [
        GapDetail(
            subcategory_id=gap_id,
            subcategory_description=f"Description for {gap_id}",
            status="missing",
            evidence_quote="",
            gap_explanation=f"Gap explanation for {gap_id}",
            severity="High",
            suggested_fix=f"Suggested fix for {gap_id}"
        )
        for gap_id in oracle_test_case.expected_gaps
    ]
    
    return GapAnalysisReport(
        analysis_date=datetime.now(),
        input_file=oracle_test_case.policy_document,
        input_file_hash="mock_hash_123",
        model_name="mock-model",
        model_version="1.0",
        embedding_model="mock-embed",
        gaps=gap_details,
        covered_subcategories=oracle_test_case.expected_covered,
        metadata={}
    )


def example_basic_validation():
    """Example: Basic oracle validation."""
    print("\n" + "="*70)
    print("Example 1: Basic Oracle Validation")
    print("="*70)
    
    # Initialize validator
    oracle_dir = Path(__file__).parent.parent / "oracles"
    validator = OracleValidator(str(oracle_dir))
    
    # Load oracle test cases
    oracles = validator.load_oracles()
    print(f"\n✓ Loaded {len(oracles)} oracle test cases")
    
    # Validate against first oracle
    test_case = oracles[0]
    print(f"\nValidating against oracle: {test_case.test_id}")
    print(f"  Description: {test_case.description}")
    print(f"  Expected gaps: {len(test_case.expected_gaps)}")
    print(f"  Expected covered: {len(test_case.expected_covered)}")
    
    # Create mock result (in real usage, run actual gap analysis)
    result = create_mock_gap_analysis_report(test_case)
    
    # Validate
    validation = validator.validate_against_oracle(test_case, result)
    
    if validation.passed:
        print(f"\n✓ Validation PASSED")
        print(f"  Accuracy: {validation.accuracy:.2%}")
    else:
        print(f"\n✗ Validation FAILED")
        print(f"  Accuracy: {validation.accuracy:.2%}")
        print(f"  False positives: {len(validation.false_positives)}")
        print(f"  False negatives: {len(validation.false_negatives)}")


def example_batch_validation():
    """Example: Batch validation of all oracles."""
    print("\n" + "="*70)
    print("Example 2: Batch Validation")
    print("="*70)
    
    # Initialize validator
    oracle_dir = Path(__file__).parent.parent / "oracles"
    validator = OracleValidator(str(oracle_dir))
    
    # Load oracles
    oracles = validator.load_oracles()
    print(f"\n✓ Loaded {len(oracles)} oracle test cases")
    
    # Validate all oracles
    print("\nValidating all oracles...")
    validations = []
    
    for i, oracle in enumerate(oracles[:5], 1):  # Validate first 5 for demo
        print(f"  [{i}/{5}] {oracle.test_id}...", end=" ")
        
        result = create_mock_gap_analysis_report(oracle)
        validation = validator.validate_against_oracle(oracle, result)
        validations.append(validation)
        
        if validation.passed:
            print("✓ PASS")
        else:
            print("✗ FAIL")
    
    # Measure aggregate accuracy
    metrics = validator.measure_accuracy(validations)
    
    print(f"\n{'='*70}")
    print("Aggregate Accuracy Metrics")
    print(f"{'='*70}")
    print(f"  Total cases:        {metrics.total_cases}")
    print(f"  Passed:             {metrics.passed_cases}")
    print(f"  Failed:             {metrics.failed_cases}")
    print(f"  Overall accuracy:   {metrics.overall_accuracy:.2%}")
    print(f"  Precision:          {metrics.precision:.2%}")
    print(f"  Recall:             {metrics.recall:.2%}")
    print(f"  F1 Score:           {metrics.f1_score:.2%}")
    print(f"  FP Rate:            {metrics.false_positive_rate:.2%}")
    print(f"  FN Rate:            {metrics.false_negative_rate:.2%}")


def example_accuracy_trends():
    """Example: Track accuracy trends over time."""
    print("\n" + "="*70)
    print("Example 3: Accuracy Trend Tracking")
    print("="*70)
    
    # Initialize validator
    oracle_dir = Path(__file__).parent.parent / "oracles"
    validator = OracleValidator(str(oracle_dir))
    
    # Load oracles
    oracles = validator.load_oracles()
    
    # Validate all oracles
    validations = []
    for oracle in oracles[:5]:  # First 5 for demo
        result = create_mock_gap_analysis_report(oracle)
        validation = validator.validate_against_oracle(oracle, result)
        validations.append(validation)
    
    # Measure accuracy
    metrics = validator.measure_accuracy(validations)
    
    # Track trend
    test_run_id = f"demo_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    validator.track_accuracy_trend(metrics, test_run_id)
    
    print(f"\n✓ Tracked accuracy trend for run: {test_run_id}")
    print(f"  Accuracy: {metrics.overall_accuracy:.2%}")
    
    # Get recent trends
    recent_trends = validator.get_accuracy_trends(limit=5)
    
    print(f"\nRecent accuracy trends ({len(recent_trends)} runs):")
    for trend in recent_trends:
        print(f"  {trend.timestamp.strftime('%Y-%m-%d %H:%M:%S')}: "
              f"{trend.metrics.overall_accuracy:.2%} accuracy "
              f"({trend.test_run_id})")


def example_oracle_update():
    """Example: Update oracle test case."""
    print("\n" + "="*70)
    print("Example 4: Oracle Update")
    print("="*70)
    
    # Initialize validator
    oracle_dir = Path(__file__).parent.parent / "oracles"
    validator = OracleValidator(str(oracle_dir))
    
    # Load oracles
    oracles = validator.load_oracles()
    test_case = oracles[0]
    
    print(f"\nOriginal oracle: {test_case.test_id}")
    print(f"  Expected gaps: {len(test_case.expected_gaps)}")
    print(f"  Expected covered: {len(test_case.expected_covered)}")
    
    # Update oracle (for demonstration only - not actually saving)
    new_gaps = ["ID.AM-1", "ID.AM-2"]
    new_covered = ["PR.AC-1", "PR.AC-2", "PR.AC-3"]
    reason = "Demo: Updated reference catalog"
    
    print(f"\nUpdating oracle...")
    print(f"  New gaps: {len(new_gaps)}")
    print(f"  New covered: {len(new_covered)}")
    print(f"  Reason: {reason}")
    
    # Note: Commenting out actual update to preserve demo oracles
    # validator.update_oracle(test_case, new_gaps, new_covered, reason)
    
    print(f"\n✓ Oracle update complete (demo mode - not saved)")


def example_false_positive_detection():
    """Example: Detect false positives."""
    print("\n" + "="*70)
    print("Example 5: False Positive Detection")
    print("="*70)
    
    # Initialize validator
    oracle_dir = Path(__file__).parent.parent / "oracles"
    validator = OracleValidator(str(oracle_dir))
    
    # Load oracles
    oracles = validator.load_oracles()
    test_case = oracles[0]
    
    print(f"\nOracle: {test_case.test_id}")
    print(f"  Expected gaps: {test_case.expected_gaps}")
    
    # Create result with false positives
    extra_gaps = ["PR.DS-1", "PR.DS-2"]  # Not in expected gaps
    
    gap_details = [
        GapDetail(
            subcategory_id=gap_id,
            subcategory_description=f"Description for {gap_id}",
            status="missing",
            evidence_quote="",
            gap_explanation=f"Gap explanation for {gap_id}",
            severity="High",
            suggested_fix=f"Suggested fix for {gap_id}"
        )
        for gap_id in test_case.expected_gaps + extra_gaps
    ]
    
    result = GapAnalysisReport(
        analysis_date=datetime.now(),
        input_file=test_case.policy_document,
        input_file_hash="mock_hash",
        model_name="mock-model",
        model_version="1.0",
        embedding_model="mock-embed",
        gaps=gap_details,
        covered_subcategories=test_case.expected_covered,
        metadata={}
    )
    
    # Validate
    validation = validator.validate_against_oracle(test_case, result)
    
    print(f"\nValidation result:")
    print(f"  Passed: {validation.passed}")
    print(f"  Accuracy: {validation.accuracy:.2%}")
    print(f"  False positives detected: {validation.false_positives}")
    print(f"  False negatives detected: {validation.false_negatives}")


def main():
    """Run all examples."""
    print("\n" + "="*70)
    print("Oracle Validator Usage Examples")
    print("="*70)
    
    try:
        example_basic_validation()
        example_batch_validation()
        example_accuracy_trends()
        example_oracle_update()
        example_false_positive_detection()
        
        print("\n" + "="*70)
        print("All examples completed successfully!")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
