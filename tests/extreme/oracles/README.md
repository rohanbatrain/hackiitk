# Oracle Test Cases

This directory contains known-good test cases with expected outputs for validating analysis accuracy.

## Purpose

Oracle test cases serve as ground truth for correctness validation. Each oracle contains:
- A policy document
- Expected gaps (CSF subcategories that should be detected as gaps)
- Expected covered subcategories
- Tolerance for acceptable deviation

## Format

Oracle test cases are stored as JSON files with the following structure:

```json
{
  "test_id": "oracle_001",
  "description": "Complete ISMS policy covering all CSF subcategories",
  "policy_document": "path/to/policy.md",
  "expected_gaps": [],
  "expected_covered": [
    "ID.AM-1", "ID.AM-2", "ID.AM-3", ...
  ],
  "expected_gap_count": 0,
  "tolerance": 0.05
}
```

## Creating Oracle Test Cases

1. Create a policy document with known characteristics
2. Manually analyze the policy to determine expected gaps
3. Create a JSON file with the oracle specification
4. Place the JSON file in this directory
5. Run oracle validation tests to verify accuracy

## Validation

Oracle test cases are validated by:
1. Running gap analysis on the policy document
2. Comparing detected gaps with expected gaps
3. Calculating accuracy (percentage of correct classifications)
4. Verifying false positive rate < 5%
5. Verifying false negative rate < 5%

## Maintenance

Oracle test cases should be updated when:
- System behavior intentionally changes
- Reference catalog is updated
- Gap detection logic is modified
- New CSF subcategories are added

## Example Oracle Test Cases

### Oracle 001: Complete Policy
- **Description**: Policy covering all 49 CSF subcategories
- **Expected Gaps**: 0
- **Expected Covered**: All 49 subcategories
- **Purpose**: Validate that complete policies are correctly identified

### Oracle 002: Empty Policy
- **Description**: Minimal policy with no CSF coverage
- **Expected Gaps**: 49
- **Expected Covered**: 0
- **Purpose**: Validate that gaps are correctly identified

### Oracle 003: Partial Policy
- **Description**: Policy covering 25 subcategories
- **Expected Gaps**: 24
- **Expected Covered**: 25 specific subcategories
- **Purpose**: Validate mixed coverage scenarios

### Oracle 004: Boundary Policy
- **Description**: Policy with subcategories at exact threshold scores
- **Expected Gaps**: Varies
- **Expected Covered**: Varies
- **Purpose**: Validate classification at boundaries

## Requirements

Oracle validation addresses:
- Requirement 71.1: Maintain 20+ oracle test cases
- Requirement 71.2: Verify 95% accuracy
- Requirement 71.3: Verify all planted gaps are detected
- Requirement 71.4: Verify false positive rate < 5%
- Requirement 71.5: Update oracles when behavior changes
