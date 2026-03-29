# Test Data and Validation Guide

This guide explains how to use the test policies and validation scripts to verify that the Offline Policy Gap Analyzer meets Requirement 19.5: detecting at least 80% of intentionally planted gaps.

## Overview

The test suite includes four dummy policies with intentional gaps:

1. **ISMS Policy** - Missing governance and supply chain risk management
2. **Data Privacy Policy** - Missing identity management and data security controls
3. **Patch Management Policy** - Missing risk assessment and protective technology
4. **Risk Management Policy** - Missing cybersecurity risk strategy and asset management

Each policy has been carefully crafted to include realistic content while intentionally omitting specific NIST CSF 2.0 subcategories that should be detected by the analyzer.

## Test Policy Locations

```
tests/fixtures/dummy_policies/
├── isms_policy.md          # ISMS policy with governance gaps
├── privacy_policy.md       # Privacy policy with access control gaps
├── patch_policy.md         # Patch management with vulnerability gaps
└── risk_policy.md          # Risk management with strategy gaps
```

## Expected Outputs

```
tests/fixtures/expected_outputs/
├── README.md                      # Overview of expected outputs
├── expected_isms_gaps.json        # Expected gaps for ISMS policy
├── expected_privacy_gaps.json     # Expected gaps for privacy policy
├── expected_patch_gaps.json       # Expected gaps for patch policy
├── expected_risk_gaps.json        # Expected gaps for risk policy
├── validate_outputs.py            # Single policy validation script
└── validate_all.py                # Batch validation script
```

## Running Tests

### Option 1: Validate Existing Outputs

If you've already run gap analysis on the test policies:

```bash
# Validate a single policy
python tests/fixtures/expected_outputs/validate_outputs.py \
  --policy isms \
  --output outputs/isms_policy_20240101_120000/gap_analysis_report.json

# Validate all policies
python tests/fixtures/expected_outputs/validate_all.py \
  --output-dir outputs
```

### Option 2: Analyze and Validate

To run analysis and validation in one step:

```bash
# Analyze and validate all test policies
python tests/fixtures/expected_outputs/validate_all.py \
  --analyze-and-validate \
  --output-dir outputs
```

### Option 3: Manual Analysis

Analyze each policy individually:

```bash
# ISMS Policy
python examples/run_analysis.py tests/fixtures/dummy_policies/isms_policy.md

# Privacy Policy
python examples/run_analysis.py tests/fixtures/dummy_policies/privacy_policy.md

# Patch Management Policy
python examples/run_analysis.py tests/fixtures/dummy_policies/patch_policy.md

# Risk Management Policy
python examples/run_analysis.py tests/fixtures/dummy_policies/risk_policy.md
```

Then validate each output:

```bash
python tests/fixtures/expected_outputs/validate_outputs.py \
  --policy isms \
  --output outputs/isms_policy_TIMESTAMP/gap_analysis_report.json
```

## Understanding Validation Results

### Success Criteria

For each policy, the analyzer must detect at least 80% of the intentionally planted gaps:

- **ISMS Policy**: 7 out of 8 gaps (87.5%)
- **Privacy Policy**: 10 out of 12 gaps (83.3%)
- **Patch Management Policy**: 10 out of 12 gaps (83.3%)
- **Risk Management Policy**: 10 out of 12 gaps (83.3%)

### Validation Output

The validation script provides:

1. **Detection Rate**: Percentage of expected gaps that were detected
2. **Detected Gaps**: List of subcategory IDs that were correctly identified
3. **Missed Gaps**: List of subcategory IDs that were not detected
4. **False Positives**: Gaps reported that were not intentionally planted

Example output:

```
================================================================================
Gap Detection Validation Results: ISMS Policy
================================================================================

Policy Type: isms
Total Expected Gaps: 8
Total Detected Gaps: 7
Detection Rate: 87.5%
Required Threshold: 80%

Validation Status: ✓ PASSED

✓ Detected Gaps (7):
  - GV.OV-01
  - GV.OV-02
  - GV.OV-03
  - GV.SC-01
  - GV.SC-02
  - GV.SC-03
  - GV.SC-04

✗ Missed Gaps (1):
  - GV.SC-05: Response and recovery planning and testing are conducted...
    Severity: Medium

⚠ False Positives (2):
  (Gaps reported but not intentionally planted)
  - PR.AA-01
  - PR.DS-01
```

### Interpreting Results

**Passed Validation:**
- Detection rate ≥ 80%
- Analyzer successfully identifies most intentional gaps
- System meets Requirement 19.5

**Failed Validation:**
- Detection rate < 80%
- Too many gaps were missed
- May indicate issues with:
  - Retrieval engine not finding relevant policy sections
  - Stage A scoring thresholds too lenient
  - Stage B LLM prompts not effective
  - Reference catalog missing keywords

**False Positives:**
- Gaps reported that weren't intentionally planted
- Not necessarily a failure - may indicate the analyzer found legitimate gaps
- Should be manually reviewed to determine if they are valid findings

## Troubleshooting Failed Tests

### Low Detection Rate

If detection rate is below 80%:

1. **Check Retrieval Quality**
   - Review retrieval logs to see if relevant policy sections were retrieved
   - Verify hybrid retrieval is combining dense and sparse results
   - Check if reranking is working correctly

2. **Review Stage A Scoring**
   - Examine lexical and semantic scores for missed gaps
   - Check if scoring thresholds are appropriate
   - Verify section heuristics are being applied

3. **Analyze Stage B Reasoning**
   - Review LLM prompts for ambiguous cases
   - Check if LLM is correctly identifying gaps
   - Verify JSON schema validation is working

4. **Validate Reference Catalog**
   - Ensure all 49 CSF subcategories are present
   - Check that keywords are comprehensive
   - Verify domain tags are correct

### High False Positive Rate

If many false positives are reported:

1. **Review False Positives Manually**
   - Some may be legitimate gaps not intentionally planted
   - Determine if they represent real policy weaknesses

2. **Check Stage A Thresholds**
   - Thresholds may be too strict, flagging everything as missing
   - Adjust coverage classification thresholds if needed

3. **Examine LLM Reasoning**
   - LLM may be hallucinating gaps
   - Review Stage B prompts for clarity
   - Consider lowering temperature for more conservative outputs

## Expected Gap Details

### ISMS Policy Gaps

**Missing Subcategories:**
- GV.SC-01 through GV.SC-05 (Supply Chain Risk Management)
- GV.OV-01 through GV.OV-03 (Organizational Context)

**Why These Gaps Exist:**
The ISMS policy covers general information security management but intentionally omits:
- Supply chain and third-party risk management
- Organizational context and mission alignment
- Stakeholder cybersecurity expectations

### Privacy Policy Gaps

**Missing Subcategories:**
- PR.AA-01 through PR.AA-06 (Identity Management and Access Control)
- PR.DS-01, PR.DS-02, PR.DS-05, PR.DS-08, PR.DS-10, PR.DS-11 (Data Security)

**Why These Gaps Exist:**
The privacy policy covers data privacy principles but intentionally omits:
- Technical identity and access control implementation
- Specific data security controls and encryption requirements
- Hardware integrity and data-in-use protection

### Patch Management Policy Gaps

**Missing Subcategories:**
- ID.RA-01 through ID.RA-06 (Risk Assessment)
- PR.PS-01 through PR.PS-06 (Protective Technology)

**Why These Gaps Exist:**
The patch management policy covers patch deployment but intentionally omits:
- Comprehensive vulnerability and risk assessment
- Configuration management and software lifecycle
- Logging and unauthorized software prevention

### Risk Management Policy Gaps

**Missing Subcategories:**
- GV.RM-01 through GV.RM-07 (Risk Management Strategy)
- ID.AM-01 through ID.AM-05 (Asset Management)

**Why These Gaps Exist:**
The risk management policy covers general enterprise risk but intentionally omits:
- Cybersecurity-specific risk management strategy
- Asset inventory and management
- Cybersecurity risk communication channels

## Continuous Integration

To integrate these tests into CI/CD:

```bash
#!/bin/bash
# ci_test_gap_detection.sh

set -e

echo "Running gap detection validation tests..."

# Run batch validation
python tests/fixtures/expected_outputs/validate_all.py \
  --analyze-and-validate \
  --output-dir outputs \
  --json > validation_results.json

# Check exit code
if [ $? -eq 0 ]; then
  echo "✓ All gap detection tests passed"
  exit 0
else
  echo "✗ Gap detection tests failed"
  cat validation_results.json
  exit 1
fi
```

## Manual Review Process

Even when validation passes, manual review is recommended:

1. **Review Detected Gaps**
   - Verify gap explanations are accurate
   - Check that evidence quotes are relevant
   - Confirm severity assignments are appropriate

2. **Review Missed Gaps**
   - Understand why gaps were missed
   - Determine if they are edge cases
   - Consider if detection is critical

3. **Review False Positives**
   - Determine if they are legitimate gaps
   - Update expected outputs if needed
   - Document findings for future reference

## Updating Expected Outputs

If you need to update expected outputs:

1. Edit the appropriate JSON file in `tests/fixtures/expected_outputs/`
2. Update the `expected_gaps` array with new gap definitions
3. Update `total_planted_gaps` and `minimum_required_detection`
4. Add notes explaining the changes
5. Re-run validation to verify

## Summary

The test data and validation scripts provide:

- **Reproducible Testing**: Consistent test policies with known gaps
- **Automated Validation**: Scripts to verify 80% detection requirement
- **Detailed Reporting**: Clear indication of what was detected and missed
- **Troubleshooting Guidance**: Help diagnosing detection issues

Use these tools throughout development to ensure the Offline Policy Gap Analyzer meets its accuracy requirements.
