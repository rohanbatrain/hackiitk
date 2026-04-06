"""Schemas for eval artifacts and model comparison outputs."""

EVAL_CASE_RESULT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "case_id": {"type": "string"},
        "model": {"type": "string"},
        "suite": {"type": "string"},
        "repeat": {"type": "integer", "minimum": 0},
        "status": {"type": "string", "enum": ["pass", "fail", "error", "skip"]},
        "schema_valid": {"type": "boolean"},
        "format_valid": {"type": "boolean"},
        "correctness": {"type": "number", "minimum": 0, "maximum": 1},
        "false_positives": {"type": "integer", "minimum": 0},
        "false_negatives": {"type": "integer", "minimum": 0},
        "latency_ms": {"type": "number", "minimum": 0},
        "token_throughput_tps": {"type": "number", "minimum": 0},
        "retry_count": {"type": "integer", "minimum": 0},
        "retry_success": {"type": "boolean"},
        "peak_memory_mb": {"type": "number", "minimum": 0},
        "crash": {"type": "boolean"},
        "hallucination_proxy": {"type": "number", "minimum": 0},
        "reproducibility_score": {"type": "number", "minimum": 0, "maximum": 1},
        "error": {"type": ["string", "null"]}
    },
    "required": [
        "case_id", "model", "suite", "repeat", "status", "schema_valid", "format_valid",
        "correctness", "false_positives", "false_negatives", "latency_ms", "token_throughput_tps",
        "retry_count", "retry_success", "peak_memory_mb", "crash", "hallucination_proxy",
        "reproducibility_score", "error"
    ],
    "additionalProperties": False,
}

EVAL_RESULT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "run": {
            "type": "object",
            "properties": {
                "run_id": {"type": "string"},
                "commit": {"type": "string"},
                "workflow": {"type": "string"},
                "suite": {"type": "string"},
                "model": {"type": "string"},
                "shard": {"type": "integer", "minimum": 0},
                "repeat": {"type": "integer", "minimum": 0},
            },
            "required": ["run_id", "commit", "workflow", "suite", "model", "shard", "repeat"],
            "additionalProperties": False,
        },
        "cases": {
            "type": "array",
            "items": EVAL_CASE_RESULT_SCHEMA,
        },
        "aggregate": {
            "type": "object",
            "properties": {
                "total_cases": {"type": "integer", "minimum": 0},
                "pass_rate": {"type": "number", "minimum": 0, "maximum": 1},
                "weighted_score": {"type": "number", "minimum": 0, "maximum": 1},
                "schema_valid_rate": {"type": "number", "minimum": 0, "maximum": 1},
                "crash_rate": {"type": "number", "minimum": 0, "maximum": 1},
            },
            "required": ["total_cases", "pass_rate", "weighted_score", "schema_valid_rate", "crash_rate"],
            "additionalProperties": False,
        },
        "environment": {
            "type": "object",
            "properties": {
                "runner_type": {"type": "string"},
                "cpu": {"type": "string"},
                "memory_mb": {"type": "number", "minimum": 0},
                "ollama_host": {"type": "string"},
                "model_digest": {"type": ["string", "null"]},
            },
            "required": ["runner_type", "cpu", "memory_mb", "ollama_host", "model_digest"],
            "additionalProperties": False,
        },
        "reproducibility": {
            "type": "object",
            "properties": {
                "runs_compared": {"type": "integer", "minimum": 1},
                "agreement_rate": {"type": "number", "minimum": 0, "maximum": 1},
            },
            "required": ["runs_compared", "agreement_rate"],
            "additionalProperties": False,
        },
    },
    "required": ["run", "cases", "aggregate", "environment", "reproducibility"],
    "additionalProperties": False,
}
