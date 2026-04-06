import json
from pathlib import Path

from tests.evals.harness.aggregator import aggregate_eval


def test_e2e_aggregate_contract():
    run_meta = {
        "run_id": "local-run",
        "commit": "local",
        "workflow": "local",
        "suite": "e2e",
        "model": "qwen2.5:3b",
        "shard": 0,
        "repeat": 0,
    }
    case = {
        "case_id": "sample",
        "model": "qwen2.5:3b",
        "suite": "e2e",
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
    env = {
        "runner_type": "local",
        "cpu": "x86_64",
        "memory_mb": 1,
        "ollama_host": "http://localhost:11434",
        "model_digest": None,
    }
    repro = {"runs_compared": 1, "agreement_rate": 1.0}

    payload = aggregate_eval(run_meta, [case], env, repro)
    assert payload["aggregate"]["weighted_score"] > 0
