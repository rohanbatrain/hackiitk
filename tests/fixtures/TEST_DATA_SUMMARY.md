# Test Data Summary

## Overview

This directory contains comprehensive test data for validating the Offline Policy Gap Analyzer's ability to detect policy gaps against NIST CSF 2.0 standards. The test suite meets Requirement 19 by providing four dummy policies with intentional gaps and automated validation scripts.

## Test Policies Created

### 1. ISMS Policy (`dummy_policies/isms_policy.md`)
**Purpose**: Test governance and supply chain risk management gap detection

**Content Included**:
- Purpose and scope
- Roles and responsibilities
- Risk management (general)
- Incident response
- Access control
- Information classification
- Security awareness and training
- Compliance and audit

**Intentional Gaps** (8 total):
- **GV.SC-01 to GV.SC-05**: Supply chain risk management program, supplier assessment, contractual requirements, ongoing monitoring, and response planning
- **GV.OV-01 to GV.OV-03**: Organizational context, stakeholder expectations, and legal/regulatory requirement management

**Detection Target**: 7 out of 8 gaps (87.5%)

**Requirement**: 19.1

---

### 2. Data Privacy Policy (`dummy_policies/privacy_policy.md`)
**Purpose**: Test identity management and data security gap detection

**Content Included**:
- Purpose and scope
- Data collection principles
- Data usage and sharing
- Data retention and disposal
- Data subject rights
- International data transfers
- Privacy governance
- Compliance

**Intentional Gaps** (12 total):
- **PR.AA-01 to PR.AA-06**: Identity lifecycle management, credential management, authentication, identity assertions, access permissions, and physical access
- **PR.DS-01, PR.DS-02, PR.DS-05, PR.DS-08, PR.DS-10, PR.DS-11**: Data-at-rest protection, data-in-transit protection, data leak prevention, hardware integrity, data-in-use protection, and backups

**Detection Target**: 10 out of 12 gaps (83.3%)

**Requirement**: 19.2

---

### 3. Patch Management Policy (`dummy_policies/patch_policy.md`)
**Purpose**: Test vulnerability management and protective technology gap detection

**Content Included**:
- Purpose and scope
- Roles and responsibilities
- Patch management process
- Patch testing procedures
- Patch deployment schedules
- Rollback procedures
- Emergency patching
- Reporting and metrics

**Intentional Gaps** (12 total):
- **ID.RA-01 to ID.RA-06**: Vulnerability identification, threat intelligence, threat documentation, business impact assessment, risk assessment methodology, and risk response management
- **PR.PS-01 to PR.PS-06**: Configuration management, software lifecycle, hardware lifecycle, logging, unauthorized software prevention, and secure development

**Detection Target**: 10 out of 12 gaps (83.3%)

**Requirement**: 19.3

---

### 4. Risk Management Policy (`dummy_policies/risk_policy.md`)
**Purpose**: Test cybersecurity risk strategy and asset management gap detection

**Content Included**:
- Purpose and scope
- Risk management principles
- Roles and responsibilities
- Risk identification and assessment
- Risk treatment and monitoring
- Risk communication
- Third-party risk management
- Training and awareness

**Intentional Gaps** (12 total):
- **GV.RM-01 to GV.RM-07**: Risk management objectives, risk appetite statements, cybersecurity integration, strategic direction, communication channels, standardized methodology, and positive risks
- **ID.AM-01 to ID.AM-05**: Hardware inventory, software inventory, network documentation, supplier service inventory, and asset prioritization

**Detection Target**: 10 out of 12 gaps (83.3%)

**Requirement**: 19.4

---

## Expected Outputs

### Gap Definition Files

Each policy has a corresponding JSON file defining expected gaps:

- `expected_outputs/expected_isms_gaps.json`
- `expected_outputs/expected_privacy_gaps.json`
- `expected_outputs/expected_patch_gaps.json`
- `expected_outputs/expected_risk_gaps.json`

**Structure**:
```json
{
  "policy_name": "Policy Name",
  "policy_file": "policy_file.md",
  "expected_gaps": [
    {
      "subcategory_id": "GV.SC-01",
      "function": "Govern",
      "category": "Supply Chain Risk Management",
      "description": "Full NIST description",
      "severity": "High",
      "reason": "Why this gap exists",
      "evidence": "What's missing from the policy"
    }
  ],
  "total_planted_gaps": 8,
  "minimum_required_detection": 7,
  "detection_threshold_percentage": 80,
  "notes": ["Additional context"]
}
```

---

## Validation Scripts

### Single Policy Validation (`validate_outputs.py`)

Validates gap analysis output for a single policy:

```bash
python tests/fixtures/expected_outputs/validate_outputs.py \
  --policy isms \
  --output outputs/isms_policy_*/gap_analysis_report.json
```

**Features**:
- Compares actual vs expected gap IDs
- Calculates detection rate
- Identifies missed gaps and false positives
- Provides detailed human-readable output
- Supports JSON output for automation

### Batch Validation (`validate_all.py`)

Validates all test policies at once:

```bash
python tests/fixtures/expected_outputs/validate_all.py \
  --analyze-and-validate \
  --output-dir outputs
```

**Features**:
- Optionally runs analysis before validation
- Validates all four policies
- Provides summary statistics
- Returns exit code 0 if all pass, 1 if any fail

### Test Runner (`run_tests.sh`)

Simple shell script for running all tests:

```bash
./tests/fixtures/run_tests.sh --analyze
```

---

## Validation Metrics

### Detection Rate Calculation

```
Detection Rate = (Detected Gaps / Total Expected Gaps) × 100%
```

**Pass Criteria**: Detection Rate ≥ 80%

### Metrics Reported

1. **Total Expected Gaps**: Number of intentionally planted gaps
2. **Total Detected Gaps**: Number of expected gaps found by analyzer
3. **Detection Rate**: Percentage of expected gaps detected
4. **Detected Gaps**: List of subcategory IDs correctly identified
5. **Missed Gaps**: List of subcategory IDs not detected
6. **False Positives**: Gaps reported but not intentionally planted

---

## Gap Design Rationale

### Why These Specific Gaps?

1. **Realistic Omissions**: Each gap represents a common real-world policy weakness
2. **Diverse Coverage**: Gaps span all NIST CSF functions (Govern, Identify, Protect)
3. **Varying Severity**: Mix of Critical, High, Medium, and Low severity gaps
4. **Detectable**: Gaps should be detectable through hybrid retrieval and two-stage analysis
5. **Domain-Specific**: Gaps align with policy domain (ISMS, Privacy, Patch, Risk)

### Gap Selection Criteria

**Included Gaps**:
- Clearly missing from policy text
- Relevant to policy domain
- Detectable through keyword and semantic matching
- Represent significant security weaknesses

**Excluded Gaps**:
- Subcategories outside policy scope
- Gaps that would be false positives
- Subcategories that are implicitly covered

---

## Usage Scenarios

### Scenario 1: Development Testing

During development, run tests frequently to verify detection accuracy:

```bash
# Quick validation of existing outputs
./tests/fixtures/run_tests.sh

# Full analysis and validation
./tests/fixtures/run_tests.sh --analyze
```

### Scenario 2: Regression Testing

After making changes to retrieval, scoring, or LLM prompts:

```bash
# Re-analyze all policies
for policy in isms privacy patch risk; do
  python examples/run_analysis.py tests/fixtures/dummy_policies/${policy}_policy.md
done

# Validate all outputs
python tests/fixtures/expected_outputs/validate_all.py --output-dir outputs
```

### Scenario 3: CI/CD Integration

Add to continuous integration pipeline:

```yaml
# .github/workflows/test.yml
- name: Run Gap Detection Tests
  run: |
    ./tests/fixtures/run_tests.sh --analyze
```

### Scenario 4: Manual Quality Review

Review specific policy outputs:

```bash
# Analyze single policy
python examples/run_analysis.py tests/fixtures/dummy_policies/isms_policy.md

# Review output files
cat outputs/isms_policy_*/gap_analysis_report.md

# Validate against expected
python tests/fixtures/expected_outputs/validate_outputs.py \
  --policy isms \
  --output outputs/isms_policy_*/gap_analysis_report.json
```

---

## Interpreting Results

### Successful Validation

```
✓ PASSED: ISMS Policy
Detection Rate: 87.5% (threshold: 80%)
Detected: 7/8 gaps
```

**Interpretation**: Analyzer successfully meets requirements for this policy.

### Failed Validation

```
✗ FAILED: Privacy Policy
Detection Rate: 75.0% (threshold: 80%)
Detected: 9/12 gaps
Missed: PR.AA-03, PR.DS-01, PR.DS-11
```

**Interpretation**: Analyzer missed too many gaps. Investigate:
1. Were relevant policy sections retrieved?
2. Did Stage A scoring classify correctly?
3. Did Stage B LLM identify the gaps?

### False Positives

```
⚠ False Positives (3):
  - PR.AT-01
  - DE.CM-01
  - RS.CO-01
```

**Interpretation**: Analyzer reported gaps not intentionally planted. This may indicate:
1. Legitimate gaps the policy actually has (good finding!)
2. Over-sensitive detection (needs tuning)
3. Hallucination by LLM (needs prompt improvement)

---

## Maintenance

### Updating Test Policies

If policies need updates:

1. Edit markdown files in `dummy_policies/`
2. Ensure intentional gaps remain
3. Re-run validation to verify gaps still detectable

### Updating Expected Outputs

If expected gaps change:

1. Edit JSON files in `expected_outputs/`
2. Update `expected_gaps` array
3. Update `total_planted_gaps` and `minimum_required_detection`
4. Add notes explaining changes
5. Re-run validation

### Adding New Test Policies

To add a new test policy:

1. Create policy markdown in `dummy_policies/`
2. Create expected gaps JSON in `expected_outputs/`
3. Add policy to `POLICIES` list in `validate_all.py`
4. Update documentation

---

## Requirements Traceability

| Requirement | Test Policy | Validation Script | Status |
|-------------|-------------|-------------------|--------|
| 19.1 | isms_policy.md | validate_outputs.py | ✓ Complete |
| 19.2 | privacy_policy.md | validate_outputs.py | ✓ Complete |
| 19.3 | patch_policy.md | validate_outputs.py | ✓ Complete |
| 19.4 | risk_policy.md | validate_outputs.py | ✓ Complete |
| 19.5 | All policies | validate_all.py | ✓ Complete |

---

## Files Created

```
tests/fixtures/
├── dummy_policies/
│   ├── isms_policy.md              # 8 planted gaps (governance, supply chain)
│   ├── privacy_policy.md           # 12 planted gaps (access control, data security)
│   ├── patch_policy.md             # 12 planted gaps (risk assessment, protective tech)
│   └── risk_policy.md              # 12 planted gaps (risk strategy, asset mgmt)
├── expected_outputs/
│   ├── README.md                   # Overview of expected outputs
│   ├── expected_isms_gaps.json     # 8 expected gaps with details
│   ├── expected_privacy_gaps.json  # 12 expected gaps with details
│   ├── expected_patch_gaps.json    # 12 expected gaps with details
│   ├── expected_risk_gaps.json     # 12 expected gaps with details
│   ├── validate_outputs.py         # Single policy validator (executable)
│   └── validate_all.py             # Batch validator (executable)
├── run_tests.sh                    # Simple test runner (executable)
├── QUICK_START.md                  # Quick reference guide
├── TESTING_GUIDE.md                # Comprehensive testing guide
└── TEST_DATA_SUMMARY.md            # This file
```

---

## Summary

The test data suite provides:

✓ **Four realistic test policies** with intentional gaps  
✓ **44 total planted gaps** across all policies  
✓ **Detailed expected output definitions** for validation  
✓ **Automated validation scripts** for pass/fail determination  
✓ **Comprehensive documentation** for usage and troubleshooting  
✓ **80% detection threshold** aligned with Requirement 19.5  
✓ **CI/CD integration support** for continuous testing  

This test suite enables systematic validation that the Offline Policy Gap Analyzer meets its accuracy requirements throughout development and deployment.
