# Integration Tests

This directory contains integration tests for the Offline Policy Gap Analyzer that validate end-to-end analysis workflows for different policy types.

## Test Files

### Policy-Specific Tests

- **test_isms_policy.py**: Tests ISMS policy analysis with planted gaps in Supply Chain Risk Management and Organizational Context subcategories
- **test_privacy_policy.py**: Tests Data Privacy policy analysis with planted gaps in Identity Management and Data Security subcategories, includes privacy framework limitation warning validation
- **test_patch_policy.py**: Tests Patch Management policy analysis with planted gaps in Risk Assessment and Protective Technology subcategories, validates roadmap prioritization
- **test_risk_policy.py**: Tests Risk Management policy analysis with planted gaps in Risk Management Strategy and Asset Management subcategories, validates revised policy provisions

### Complete Pipeline Test

- **test_complete_pipeline.py**: Tests the complete analysis pipeline with generic policy input, validates all components and outputs

## Test Validation Scripts

### run_all_policy_tests.py

Automated test runner that executes all policy integration tests and generates a comprehensive validation report.

**Usage:**
```bash
# Run all tests with default settings
python tests/integration/run_all_policy_tests.py

# Run with verbose output
python tests/integration/run_all_policy_tests.py --verbose

# Save report to custom location
python tests/integration/run_all_policy_tests.py --output my_report.json
```

**Features:**
- Runs all 4 policy-specific integration tests
- Generates pass/fail report for each policy type
- Saves detailed JSON report with test metrics
- Provides summary statistics

### validate_policy_outputs.py

Output validation script that compares generated analysis outputs against expected results.

**Usage:**
```bash
# Validate outputs from a specific analysis run
python tests/integration/validate_policy_outputs.py outputs/isms_20240328_120000

# The script will auto-detect policy type and compare against expected gaps
```

**Validations:**
- Gap detection accuracy (≥80% threshold)
- Output file completeness
- Revised policy content and warnings
- Implementation roadmap structure

## Running Tests

### Prerequisites

1. Install test dependencies:
```bash
pip install pytest pytest-json-report hypothesis
```

2. Ensure models are downloaded:
```bash
python scripts/setup_models.py
```

3. Build reference catalog:
```bash
python -c "from reference_builder.reference_catalog import ReferenceCatalog; catalog = ReferenceCatalog('data/cis_guide.pdf'); catalog.persist('data/reference_catalog.json')"
```

### Run Individual Test

```bash
# Run ISMS policy test
pytest tests/integration/test_isms_policy.py -v -s

# Run with markers
pytest tests/integration/test_isms_policy.py -v -s -m integration

# Run specific test function
pytest tests/integration/test_isms_policy.py::test_isms_policy_analysis -v -s
```

### Run All Integration Tests

```bash
# Using pytest
pytest tests/integration/ -v -s -m integration

# Using test runner script (recommended)
python tests/integration/run_all_policy_tests.py --verbose
```

## Test Data

Test policies and expected results are located in:
- `tests/fixtures/dummy_policies/`: Dummy policy files with intentional gaps
- `tests/fixtures/expected_outputs/`: Expected gap detection results for validation

See `tests/fixtures/TEST_DATA_SUMMARY.md` for details on planted gaps.

## Success Criteria

Each policy test must meet the following criteria to pass:

1. **Gap Detection**: Detect at least 80% of intentionally planted gaps
2. **Output Files**: Generate all required output files (gap report, revised policy, roadmap)
3. **Revised Policy**: Include mandatory AI-generated content warning
4. **Roadmap**: Prioritize critical/high severity gaps as Immediate actions
5. **Domain Prioritization**: Focus on relevant CSF subcategories for policy type

## Test Markers

- `@pytest.mark.integration`: Integration test (requires full system)
- `@pytest.mark.slow`: Long-running test (may take several minutes)

## Troubleshooting

### Tests Skipped

If tests are skipped, check:
- Model files exist in `models/` directory
- Test policy files exist in `tests/fixtures/dummy_policies/`
- Expected gap files exist in `tests/fixtures/expected_outputs/`

### Low Detection Rate

If gap detection rate is below 80%:
- Check embedding model is loaded correctly
- Verify reference catalog contains all 49 CSF subcategories
- Review Stage A scoring thresholds in configuration
- Check LLM model is generating structured outputs correctly

### Memory Issues

If tests fail with memory errors:
- Use smaller model (Qwen2.5-3B instead of 7B/8B models)
- Reduce chunk_size in configuration
- Reduce top_k retrieval parameter
- Close other applications to free RAM

## Continuous Integration

These tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Integration Tests
  run: |
    python tests/integration/run_all_policy_tests.py --output test_report.json
  timeout-minutes: 30
```

## Requirements Validation

These integration tests validate the following requirements:

- **Requirement 19.1**: ISMS policy analysis with 80% gap detection
- **Requirement 19.2**: Data Privacy policy analysis with framework limitation warning
- **Requirement 19.3**: Patch Management policy analysis with roadmap prioritization
- **Requirement 19.4**: Risk Management policy analysis with revised provisions
- **Requirement 19.5**: 80% detection threshold for all policy types
- **Requirement 19.6**: Automated test validation script

## Contributing

When adding new integration tests:

1. Create test file following naming convention: `test_<policy_type>_policy.py`
2. Add expected gaps JSON to `tests/fixtures/expected_outputs/`
3. Update this README with test description
4. Add test to `run_all_policy_tests.py` test_files list
5. Ensure test includes proper markers and docstrings
