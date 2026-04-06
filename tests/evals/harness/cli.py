"""CLI for deterministic eval shard execution and aggregation."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from .runner import run_eval_case
from .aggregator import aggregate_from_dir


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Deterministic eval harness CLI")
    parser.add_argument("--suite", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--shard", type=int, required=True)
    parser.add_argument("--repeat", type=int, default=0)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--commit", default=os.getenv("GITHUB_SHA", "local"))
    parser.add_argument("--workflow", default=os.getenv("GITHUB_WORKFLOW", "local"))
    parser.add_argument("--input-manifest", required=True)
    parser.add_argument("--output-dir", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(args.input_manifest, encoding="utf-8") as f:
        manifest = json.load(f)

    cases = manifest.get("cases", [])
    jsonl_path = output_dir / "case_results.jsonl"

    with open(jsonl_path, "w", encoding="utf-8") as out:
        for case in cases:
            result = run_eval_case(
                case_id=case["case_id"],
                policy_path=case["policy_path"],
                model=args.model,
                suite=args.suite,
                repeat=args.repeat,
                domain=case.get("domain"),
            )
            out.write(json.dumps(result) + "\n")

    run_meta = {
        "run_id": args.run_id,
        "commit": args.commit,
        "workflow": args.workflow,
        "suite": args.suite,
        "model": args.model,
        "shard": args.shard,
        "repeat": args.repeat,
    }
    environment = {
        "runner_type": os.getenv("RUNNER_NAME", "local"),
        "cpu": os.getenv("RUNNER_ARCH", "unknown"),
        "memory_mb": 0,
        "ollama_host": os.getenv("OLLAMA_HOST", "http://localhost:11434"),
        "model_digest": None,
    }
    reproducibility = {
        "runs_compared": 1,
        "agreement_rate": 1.0,
    }

    aggregate_from_dir(
        input_dir=str(output_dir),
        output_file=str(output_dir / "eval_summary.json"),
        run_meta=run_meta,
        environment=environment,
        reproducibility=reproducibility,
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
