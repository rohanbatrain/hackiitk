# Expected Test Outputs

This directory contains the expected gap analysis outputs for the dummy test policies. These outputs define the minimum gaps that should be identified by the Offline Policy Gap Analyzer to meet the 80% detection requirement (Requirement 19.5).

## Test Policies Overview

### 1. ISMS Policy (`isms_policy.md`)
**Intentional Gaps:**
- Missing GV.SC (Supply Chain Risk Management) subcategories
- Missing GV.OV (Organizational Context) subcategories

**Expected Detection Rate:** At least 80% of planted gaps

### 2. Data Privacy Policy (`privacy_policy.md`)
**Intentional Gaps:**
- Missing PR.AA (Identity Management and Access Control) subcategories
- Missing PR.DS (Data Security) subcategories

**Expected Detection Rate:** At least 80% of planted gaps

### 3. Patch Management Policy (`patch_policy.md`)
**Intentional Gaps:**
- Missing ID.RA (Risk Assessment) subcategories
- Missing PR.PS (Protective Technology) subcategories

**Expected Detection Rate:** At least 80% of planted gaps

### 4. Risk Management Policy (`risk_policy.md`)
**Intentional Gaps:**
- Missing GV.RM (Risk Management Strategy) subcategories
- Missing ID.RA (Risk Assessment) subcategories

**Expected Detection Rate:** At least 80% of planted gaps

## Validation Process

The validation scripts in this directory compare actual analyzer outputs against expected outputs to verify:

1. **Gap Detection Accuracy:** At least 80% of intentionally planted gaps are identified
2. **False Positive Rate:** Minimal false positives (gaps reported that don't exist)
3. **Severity Assignment:** Appropriate severity levels assigned to identified gaps
4. **Output Format:** Correct JSON and Markdown output formats

## Usage

Run validation scripts after analyzing test policies:

```bash
# Analyze a test policy
python examples/run_analysis.py tests/fixtures/dummy_policies/isms_policy.md

# Validate the output
python tests/fixtures/expected_outputs/validate_outputs.py \
  --policy isms \
  --output outputs/isms_policy_TIMESTAMP/gap_analysis_report.json
```

## Expected Gaps by Policy

See individual files for detailed expected gaps:
- `expected_isms_gaps.json` - ISMS policy expected gaps
- `expected_privacy_gaps.json` - Privacy policy expected gaps
- `expected_patch_gaps.json` - Patch management policy expected gaps
- `expected_risk_gaps.json` - Risk management policy expected gaps
