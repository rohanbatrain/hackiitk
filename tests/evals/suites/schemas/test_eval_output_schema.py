from jsonschema import validate

from tests.evals.harness.schema import EVAL_CASE_RESULT_SCHEMA


def test_case_schema_round_trip():
    sample = {
        "case_id": "case",
        "model": "qwen2.5:3b",
        "suite": "schemas",
        "repeat": 0,
        "status": "pass",
        "schema_valid": True,
        "format_valid": True,
        "correctness": 1.0,
        "false_positives": 0,
        "false_negatives": 0,
        "latency_ms": 1.0,
        "token_throughput_tps": 1.0,
        "retry_count": 0,
        "retry_success": True,
        "peak_memory_mb": 1.0,
        "crash": False,
        "hallucination_proxy": 0.0,
        "reproducibility_score": 1.0,
        "error": None,
    }
    validate(instance=sample, schema=EVAL_CASE_RESULT_SCHEMA)
