"""Deterministic scoring utilities for machine-comparable eval outputs."""

from __future__ import annotations

from typing import Any, Dict, List


def _safe_div(n: float, d: float) -> float:
    return n / d if d else 0.0


def score_case(case_result: Dict[str, Any]) -> float:
    correctness = float(case_result.get("correctness", 0.0))
    schema_valid = 1.0 if case_result.get("schema_valid") else 0.0
    reproducibility = float(case_result.get("reproducibility_score", 0.0))
    crash_penalty = 1.0 if case_result.get("crash") else 0.0

    score = (
        0.50 * correctness +
        0.30 * schema_valid +
        0.20 * reproducibility
    )
    score -= 0.25 * crash_penalty
    return max(0.0, min(1.0, score))


def score_run(case_results: List[Dict[str, Any]]) -> Dict[str, float]:
    total = len(case_results)
    if total == 0:
        return {
            "total_cases": 0,
            "pass_rate": 0.0,
            "weighted_score": 0.0,
            "schema_valid_rate": 0.0,
            "crash_rate": 0.0,
        }

    passed = sum(1 for c in case_results if c.get("status") == "pass")
    schema_valid = sum(1 for c in case_results if c.get("schema_valid"))
    crashes = sum(1 for c in case_results if c.get("crash"))
    weighted = sum(score_case(c) for c in case_results)

    return {
        "total_cases": total,
        "pass_rate": _safe_div(passed, total),
        "weighted_score": _safe_div(weighted, total),
        "schema_valid_rate": _safe_div(schema_valid, total),
        "crash_rate": _safe_div(crashes, total),
    }
