# LLM Model Stress Tester - Integration TODO

## Status

The LLM Model Stress Tester structure is complete, but requires integration work to connect with the actual AnalysisPipeline.

## Current State

- ✅ Test structure and methods defined
- ✅ All test categories implemented (Req 31, 52, 56, 28, 53, 65)
- ✅ Helper methods for policy generation
- ✅ Schema validation logic
- ✅ Metrics collection integration
- ⚠️  Analysis pipeline integration uses stubs

## Integration Work Needed

### 1. Replace Stub Implementation

The current implementation uses `_run_analysis_stub()` which returns mock results. This needs to be replaced with actual AnalysisPipeline calls.

**Current (Stub)**:
```python
result = self._run_analysis_stub(policy_path, output_dir)
```

**Target (Production)**:
```python
config = PipelineConfig(config_dict)
pipeline = AnalysisPipeline(config)
result = pipeline.execute(
    policy_path=str(policy_path),
    output_dir=str(output_dir)
)
```

### 2. Files to Update

All test methods in `llm_model_stress_tester.py` that call `run_analysis()` need to be updated:

- `test_llm_maximum_context_length()`
- `test_llm_conflicting_instructions()`
- `test_llm_output_exceeding_max_tokens()`
- `test_llm_extreme_prompt_scenarios()`
- `test_context_window_exact_maximum()`
- `test_context_window_exceeding()`
- `test_context_window_10x_maximum()`
- `test_temperature_zero_determinism()`
- `test_temperature_high_schema_compliance()`
- `test_temperature_negative_rejection()`
- `test_temperature_range_sweep()`
- `test_all_supported_models()`
- `test_model_consistency()`
- `test_quantization_levels()`
- `test_backend_switching()`

### 3. Configuration Handling

Each test needs proper configuration setup:

```python
# Example for temperature test
config_dict = {
    'llm': {
        'temperature': 0.0,
        'model_name': 'Qwen/Qwen2.5-3B-Instruct',
        'max_tokens': 2048
    }
}
config = PipelineConfig(config_dict)
```

### 4. Output Validation

Tests need to read actual output files and validate them:

```python
output_file = output_dir / "gap_analysis_report.json"
if output_file.exists():
    with open(output_file) as f:
        output_data = json.load(f)
    # Validate schema, check gaps, etc.
```

### 5. Error Handling

Proper error handling for:
- Missing models
- Unavailable backends
- Configuration errors
- Pipeline failures

### 6. Test Data

Some tests may need actual test policy files:
- Create test policies in `tests/fixtures/llm_stress/`
- Reference them in test configuration

## Integration Steps

1. **Phase 1**: Update `_run_analysis_stub()` to use real AnalysisPipeline
2. **Phase 2**: Test with one simple test method (e.g., `test_llm_maximum_context_length`)
3. **Phase 3**: Update all test methods to use real pipeline
4. **Phase 4**: Add proper output validation
5. **Phase 5**: Run full test suite and fix any issues
6. **Phase 6**: Document any discovered limitations or requirements

## Testing the Integration

```bash
# Test individual method
pytest tests/extreme/engines/test_llm_model_stress_tester.py::test_llm_tester_initialization -v

# Test full suite
pytest tests/extreme/engines/test_llm_model_stress_tester.py -v

# Run actual LLM stress tests (requires models)
python -m tests.extreme.cli --category llm_stress
```

## Notes

- The stub implementation allows the test framework structure to be validated without requiring actual LLM models
- Integration should be done incrementally, testing each method as it's updated
- Some tests may need to be marked as `@pytest.mark.slow` or `@pytest.mark.requires_models`
- Consider adding `@pytest.mark.skipif` for tests that require specific models or backends

## Dependencies

- AnalysisPipeline must be fully functional
- LLM models must be available (or tests should gracefully skip)
- Sufficient disk space for test outputs
- Sufficient memory for LLM inference

## Timeline Estimate

- Phase 1-2: 2-4 hours
- Phase 3-4: 4-6 hours
- Phase 5-6: 2-4 hours
- Total: 8-14 hours

## Priority

**Medium-High** - The test structure is complete and can be integrated when LLM testing is prioritized.
