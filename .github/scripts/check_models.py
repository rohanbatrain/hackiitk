#!/usr/bin/env python3
"""Validate required/optional Ollama model availability."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def main() -> int:
    manifest_path = Path("/home/runner/work/hackiitk/hackiitk/tests/evals/model_manifest.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    try:
        out = subprocess.check_output(["ollama", "list"], text=True)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: cannot list Ollama models: {exc}")
        return 2

    available = set()
    for line in out.splitlines()[1:]:
        if not line.strip():
            continue
        parts = line.split()
        if parts:
            available.add(parts[0])

    missing_required = [m for m in manifest["required_models"] if m not in available]
    missing_optional = [m for m in manifest["optional_models"] if m not in available]

    if missing_optional:
        print("Optional models unavailable:")
        for m in missing_optional:
            print(f"  - {m}")

    if missing_required:
        print("Required models missing:")
        for m in missing_required:
            print(f"  - {m}")
        return 1

    print("All required models available.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
