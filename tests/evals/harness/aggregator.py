"""Artifact aggregator for shard-level eval outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from jsonschema import validate as jsonschema_validate

from .schema import EVAL_RESULT_SCHEMA, EVAL_CASE_RESULT_SCHEMA
from .scorer import score_run


def load_case_results(path: Path) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    for file in sorted(path.glob("**/*.jsonl")):
        for line in file.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            item = json.loads(line)
            jsonschema_validate(instance=item, schema=EVAL_CASE_RESULT_SCHEMA)
            results.append(item)
    return results


def aggregate_eval(
    run_meta: Dict[str, Any],
    case_results: List[Dict[str, Any]],
    environment: Dict[str, Any],
    reproducibility: Dict[str, Any],
) -> Dict[str, Any]:
    aggregate = score_run(case_results)
    payload = {
        "run": run_meta,
        "cases": case_results,
        "aggregate": aggregate,
        "environment": environment,
        "reproducibility": reproducibility,
    }
    jsonschema_validate(instance=payload, schema=EVAL_RESULT_SCHEMA)
    return payload


def aggregate_from_dir(
    input_dir: str,
    output_file: str,
    run_meta: Dict[str, Any],
    environment: Dict[str, Any],
    reproducibility: Dict[str, Any],
) -> Dict[str, Any]:
    case_results = load_case_results(Path(input_dir))
    payload = aggregate_eval(run_meta, case_results, environment, reproducibility)
    Path(output_file).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload
