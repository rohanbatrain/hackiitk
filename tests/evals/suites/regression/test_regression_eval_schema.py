from tests.evals.harness.schema import EVAL_RESULT_SCHEMA


def test_eval_schema_has_required_sections():
    required = set(EVAL_RESULT_SCHEMA["required"])
    assert {"run", "cases", "aggregate", "environment", "reproducibility"}.issubset(required)
