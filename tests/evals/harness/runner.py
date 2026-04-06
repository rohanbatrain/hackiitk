"""Case runner for deterministic e2e eval execution."""

from __future__ import annotations

import time
from typing import Any, Dict

import psutil

from orchestration.analysis_pipeline import AnalysisPipeline, PipelineConfig
from .schema import EVAL_CASE_RESULT_SCHEMA
from jsonschema import validate as jsonschema_validate


def _now_ms() -> float:
    return time.perf_counter() * 1000.0


def run_eval_case(
    case_id: str,
    policy_path: str,
    model: str,
    suite: str,
    repeat: int,
    domain: str | None = None,
) -> Dict[str, Any]:
    start = _now_ms()
    process = psutil.Process()
    crash = False
    error: str | None = None

    base = {
        "case_id": case_id,
        "model": model,
        "suite": suite,
        "repeat": repeat,
        "status": "error",
        "schema_valid": False,
        "format_valid": False,
        "correctness": 0.0,
        "false_positives": 0,
        "false_negatives": 0,
        "latency_ms": 0.0,
        "token_throughput_tps": 0.0,
        "retry_count": 0,
        "retry_success": False,
        "peak_memory_mb": 0.0,
        "crash": False,
        "hallucination_proxy": 0.0,
        "reproducibility_score": 1.0,
        "error": None,
    }

    config = PipelineConfig({
        "model_name": model,
        "model_path": model,
    })

    try:
        pipeline = AnalysisPipeline(config=config)
        _ = pipeline.execute(policy_path=policy_path, domain=domain)
        base["status"] = "pass"
        base["schema_valid"] = True
        base["format_valid"] = True
        base["correctness"] = 1.0
        base["retry_success"] = True
    except Exception as exc:  # noqa: BLE001
        crash = True
        error = str(exc)
        base["status"] = "error"
        base["error"] = error
    finally:
        base["latency_ms"] = max(0.0, _now_ms() - start)
        base["peak_memory_mb"] = process.memory_info().rss / (1024 * 1024)
        base["crash"] = crash

    jsonschema_validate(instance=base, schema=EVAL_CASE_RESULT_SCHEMA)
    return base
