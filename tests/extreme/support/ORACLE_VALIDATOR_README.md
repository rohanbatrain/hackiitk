# Oracle Validator

The Oracle Validator validates gap analysis accuracy against known-good test cases (oracles). It maintains oracle test cases with expected outputs and calculates accuracy metrics including precision, recall, F1 score, and false positive/negative rates.

## Purpose

Oracle-based testing provides ground truth validation for the gap analysis system. By comparing actual analysis results against manually verified expected outputs, we can:

- Measure analysis accuracy objectively
- Detect false positives (gaps incorrectly identified)
- Detect false negatives (gaps missed)
- Track accuracy trends over time
- Validate system behavior after changes

**Validates: Requirements 71.1, 71.2, 71.3, 71.4, 71.5**

## Features

### Oracle Test Case Management (Requirement 71.1)
- Load 20+ oracle test cases from JSON files
- Each oracle specifies expected gaps and covered subcategories
- Configurable tolerance for acceptable deviation (default 5%)

### Validation Logic (Requirements 71.2, 71.3, 71.4)
- Compare actual gap analysis results against oracle expectations
- Calculate accuracy as percentage of correct classifications
- Detect false positives (gaps detected but not expected)
- Detect false negatives (expected gaps not detected)
- Verify false positive rate < 5%
- Verify all planted gaps are detected

### Accuracy Metrics (Requirement 71.2)
- Overall accuracy across all test cases
- Precision: TP / (TP + FP)
- Recall: TP / (TP + FN)
- F1 Score: Harmonic mean of precision and recall
- False positive rate
- False negative rate

### Oracle Update Mechanism (Requirement 71.5)
- Update oracle expectations when system behavior intentionally changes
- Track update reason for audit trail
- Preserve oracle metadata during updates

### Accuracy Trend Tracking (Requirement 71.5)
- Track accuracy metrics over time
- Store accuracy history to file
- Retrieve recent trends for analysis
- Detect accuracy degradation

## Usage

### Basic Usage

```python
from tests.extreme.support.oracle_validator import OracleValidator

# Initialize validator
validator = OracleValidator("tests/extreme/oracles")

# Load oracle test cases
oracles = validator.load_oracles()
print(f"Loaded {len(oracles)} oracle test cases")

# Validate against an oracle
test_case = oracles[0]
result = run_gap_analysis(test_case.policy_document)  # Your analysis function

validation = validator.validate_against_oracle(test_case, result)

if validation.passed:
    print(f"✓ Validation passed: {validation.accuracy:.2%} accuracy")
else:
    print(f"✗ Validation failed: {validation.accuracy:.2%} accuracy")
    print(f"  False positives: {validation.false_positives}")
    print(f"  False negatives: {validation.false_negatives}")
```

### Batch Validation

```python
# Validate all oracles
validations = []
for oracle in oracles:
    result = run_gap_analysis(oracle.policy_document)
    validation = validator.validate_against_oracle(oracle, result)
    validations.append(validation)

# Measure aggregate accuracy
metrics = validator.measure_accuracy(validations)

print(f"Overall Results:")
print(f"  Total cases: {metrics.total_cases}")
print(f"  Passed: {metrics.passed_cases}")
print(f"  Failed: {metrics.failed_cases}")
print(f"  Accuracy: {metrics.overall_accuracy:.2%}")
print(f"  Precision: {metrics.precision:.2%}")
print(f"  Recall: {metrics.recall:.2%}")
print(f"  F1 Score: {metrics.f1_score:.2%}")
print(f"  FP Rate: {metrics.false_positive_rate:.2%}")
print(f"  FN Rate: {metrics.false_negative_rate:.2%}")
```

### Track Accuracy Trends

```python
# Track accuracy for this test run
validator.track_accuracy_trend(metrics, test_run_id="run_2024_01_15")

# Get recent trends
recent_trends = validator.get_accuracy_trends(limit=10)

for trend in recent_trends:
    print(f"{trend.timestamp}: {trend.metrics.overall_accuracy:.2%} accuracy")
```

### Update Oracle

```python
# Update oracle when system behavior intentionally changes
test_case = oracles[0]

new_gaps = ["ID.AM-1", "ID.AM-2"]
new_covered = ["PR.AC-1", "PR.AC-2", "PR.AC-3"]
reason = "Updated reference catalog to include new subcategories"

validator.update_oracle(
    test_case,
    new_gaps,
    new_covered,
    reason
)
```

## Oracle Test Case Format

Oracle test cases are stored as JSON files in the `tests/extreme/oracles/` directory:

```json
{
  "test_id": "oracle_001",
  "description": "Complete ISMS policy covering all 49 CSF subcategories",
  "policy_document": "tests/fixtures/dummy_policies/complete_policy.md",
  "expected_gaps": [],
  "expected_covered": [
    "ID.AM-1", "ID.AM-2", "ID.AM-3", ...
  ],
  "expected_gap_count": 0,
  "tolerance": 0.05
}
```

### Fields

- **test_id**: Unique identifier for the oracle
- **description**: Human-readable description of the test case
- **policy_document**: Path to the policy document to analyze
- **expected_gaps**: List of CSF subcategory IDs that should be detected as gaps
- **expected_covered**: List of CSF subcategory IDs that should be covered
- **expected_gap_count**: Number of expected gaps (for validation)
- **tolerance**: Acceptable deviation from perfect accuracy (default 0.05 = 5%)

## Creating New Oracle Test Cases

### Manual Creation

1. Create a policy document with known characteristics
2. Manually analyze the policy to determine expected gaps
3. Create a JSON file following the format above
4. Place the file in `tests/extreme/oracles/` with naming pattern `oracle_*.json`

### Using the Generator

The `generate_oracles.py` script can create oracle test cases programmatically:

```python
from tests.extreme.oracles.generate_oracles import generate_oracle, ALL_SUBCATEGORIES

# Generate oracle with specific coverage
oracle = generate_oracle(
    test_id="oracle_025",
    description="Policy covering only Asset Management",
    policy_doc="tests/fixtures/dummy_policies/asset_mgmt.md",
    covered_indices=[0, 1, 2, 3, 4, 5]  # ID.AM-1 through ID.AM-6
)

# Save to file
import json
with open("tests/extreme/oracles/oracle_025.json", "w") as f:
    json.dump(oracle, f, indent=2)
```

## Validation Criteria

### Pass Criteria

An oracle validation passes if:
1. Accuracy ≥ (1.0 - tolerance) (default: ≥ 95%)
2. False positive rate < 5%
3. All planted gaps are detected (no false negatives for intentional gaps)

### Accuracy Calculation

```
Accuracy = (True Positives + True Negatives) / Total Subcategories

Where:
- True Positive (TP): Gap correctly identified
- False Positive (FP): Gap incorrectly identified (not in expected_gaps)
- False Negative (FN): Gap missed (in expected_gaps but not detected)
- True Negative (TN): Covered correctly identified
```

### Precision and Recall

```
Precision = TP / (TP + FP)  # How many detected gaps are correct
Recall = TP / (TP + FN)     # How many actual gaps were detected
F1 Score = 2 * (Precision * Recall) / (Precision + Recall)
```

## Integration with Test Framework

The Oracle Validator integrates with the extreme testing framework:

```python
from tests.extreme.base import BaseTestEngine
from tests.extreme.models import TestResult, TestStatus
from tests.extreme.support.oracle_validator import OracleValidator

class BoundaryTester(BaseTestEngine):
    def __init__(self, config, oracle_validator):
        super().__init__(config)
        self.oracle = oracle_validator
    
    def test_oracle_validation(self):
        """Test gap analysis accuracy against oracles."""
        oracles = self.oracle.load_oracles()
        validations = []
        
        for oracle in oracles:
            result = self.run_analysis(oracle.policy_document)
            validation = self.oracle.validate_against_oracle(oracle, result)
            validations.append(validation)
        
        metrics = self.oracle.measure_accuracy(validations)
        
        # Track trend
        self.oracle.track_accuracy_trend(metrics, self.test_run_id)
        
        # Create test result
        return TestResult(
            test_id="oracle_validation",
            requirement_id="71.1-71.5",
            category="boundary",
            status=TestStatus.PASS if metrics.passed_cases == metrics.total_cases else TestStatus.FAIL,
            duration_seconds=0.0,
            metrics=None
        )
```

## Maintenance

### When to Update Oracles

Update oracle test cases when:
- Reference catalog is updated (new subcategories added)
- Gap detection logic is modified intentionally
- Classification thresholds are changed
- System behavior intentionally changes

### Accuracy History

Accuracy history is stored in `tests/extreme/oracles/accuracy_history.json`:

```json
[
  {
    "timestamp": "2024-01-15T10:30:00",
    "test_run_id": "run_001",
    "metrics": {
      "total_cases": 24,
      "passed_cases": 23,
      "failed_cases": 1,
      "overall_accuracy": 0.96,
      "precision": 0.97,
      "recall": 0.95,
      "f1_score": 0.96,
      "false_positive_rate": 0.02,
      "false_negative_rate": 0.03
    }
  }
]
```

## Example Oracle Test Cases

The framework includes 24 oracle test cases covering various scenarios:

1. **oracle_001**: Complete policy (0 gaps)
2. **oracle_002**: Empty policy (49 gaps)
3. **oracle_003**: Partial policy (24 gaps)
4. **oracle_004**: Boundary coverage (16 gaps)
5. **oracle_005**: Identify function only
6. **oracle_006**: Protect function only
7. **oracle_007**: Asset Management only
8. **oracle_008**: Access Control only
9. **oracle_009**: Data Security only
10. **oracle_010**: Alternating pattern
11. **oracle_011**: First half covered
12. **oracle_012**: Second half covered
13. **oracle_013**: Minimal coverage (5 subcategories)
14. **oracle_014**: Near complete (45 subcategories)
15. **oracle_015**: Risk Assessment focus
16. **oracle_016**: Governance focus
17. **oracle_017**: Training focus
18. **oracle_018**: Supply Chain focus
19. **oracle_019**: Business Environment focus
20. **oracle_020**: Risk Management focus
21. **oracle_021**: Information Protection focus
22. **oracle_022**: Sparse coverage (10 subcategories)
23. **oracle_023**: Dense coverage (40 subcategories)
24. **oracle_024**: Keywords only (no implementation)

## Testing

Run the Oracle Validator tests:

```bash
python -m pytest tests/extreme/support/test_oracle_validator.py -v
```

Test coverage includes:
- Oracle loading from files
- Validation logic (perfect match, false positives, false negatives)
- Accuracy metrics calculation
- Oracle update mechanism
- Accuracy trend tracking
- Integration workflows

## Requirements Validation

- ✓ **Requirement 71.1**: Maintain 20+ oracle test cases (24 oracles included)
- ✓ **Requirement 71.2**: Verify 95% accuracy (accuracy calculation and threshold checking)
- ✓ **Requirement 71.3**: Verify all planted gaps detected (false negative detection)
- ✓ **Requirement 71.4**: Verify false positive rate < 5% (FP rate calculation and threshold)
- ✓ **Requirement 71.5**: Update oracles when behavior changes (update mechanism and trend tracking)
