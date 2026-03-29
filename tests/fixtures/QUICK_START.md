# Quick Start: Testing Gap Detection

## TL;DR

Run all validation tests:

```bash
# Validate existing outputs
./tests/fixtures/run_tests.sh

# Or analyze and validate
./tests/fixtures/run_tests.sh --analyze
```

## What Gets Tested

Four dummy policies with intentional gaps:

| Policy | Planted Gaps | Must Detect | Focus Area |
|--------|--------------|-------------|------------|
| ISMS | 8 | 7 (87.5%) | Governance, Supply Chain |
| Privacy | 12 | 10 (83.3%) | Access Control, Data Security |
| Patch Mgmt | 12 | 10 (83.3%) | Risk Assessment, Protective Tech |
| Risk Mgmt | 12 | 10 (83.3%) | Risk Strategy, Asset Management |

## Individual Policy Testing

```bash
# Analyze a single policy
python examples/run_analysis.py tests/fixtures/dummy_policies/isms_policy.md

# Validate the output
python tests/fixtures/expected_outputs/validate_outputs.py \
  --policy isms \
  --output outputs/isms_policy_*/gap_analysis_report.json
```

## Understanding Results

**✓ PASSED** = Detection rate ≥ 80%
- Analyzer correctly identifies most intentional gaps
- Meets Requirement 19.5

**✗ FAILED** = Detection rate < 80%
- Too many gaps were missed
- Check retrieval, scoring, or LLM reasoning

**False Positives** = Gaps reported but not planted
- May be legitimate gaps (not necessarily bad)
- Review manually to determine validity

## Common Issues

### "No output directory found"
Run analysis first:
```bash
python examples/run_analysis.py tests/fixtures/dummy_policies/isms_policy.md
```

### "Expected gaps file not found"
Make sure you're in the project root directory.

### Low detection rate
1. Check if models are loaded correctly
2. Verify reference catalog has all 49 subcategories
3. Review retrieval logs for relevant sections
4. Check Stage A scoring thresholds

## Files

```
tests/fixtures/
├── dummy_policies/           # Test policies with planted gaps
│   ├── isms_policy.md
│   ├── privacy_policy.md
│   ├── patch_policy.md
│   └── risk_policy.md
├── expected_outputs/         # Expected gap definitions
│   ├── expected_isms_gaps.json
│   ├── expected_privacy_gaps.json
│   ├── expected_patch_gaps.json
│   ├── expected_risk_gaps.json
│   ├── validate_outputs.py   # Single policy validator
│   └── validate_all.py       # Batch validator
├── run_tests.sh             # Simple test runner
├── QUICK_START.md           # This file
└── TESTING_GUIDE.md         # Detailed guide
```

## Next Steps

1. Run the tests: `./tests/fixtures/run_tests.sh --analyze`
2. Review results in terminal output
3. If tests fail, see TESTING_GUIDE.md for troubleshooting
4. Manually review detected gaps for quality

## Requirements Met

This test suite validates:
- **Requirement 19.1**: ISMS policy with governance gaps
- **Requirement 19.2**: Privacy policy with access control gaps
- **Requirement 19.3**: Patch policy with vulnerability gaps
- **Requirement 19.4**: Risk policy with risk assessment gaps
- **Requirement 19.5**: 80% detection rate for all policies
