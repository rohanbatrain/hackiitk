# Offline Policy Gap Analyzer – Understanding Package

This `PPT/` package is a reverse-engineered, implementation-grounded documentation set for the repository at:

- `/home/runner/work/hackiitk/hackiitk`

## What this package contains

- Product and technical understanding from actual code and configs
- Architecture, module, data-flow, and runtime behavior documentation
- Setup/run/use guides aligned to current repository reality
- Diagram source files in Mermaid under `PPT/diagrams/source/`
- Risk, limitations, troubleshooting, and demo prep material

## Scope and methodology

This package was built by inspecting:

- Runtime code: `cli/`, `orchestration/`, `ingestion/`, `retrieval/`, `analysis/`, `revision/`, `reporting/`, `models/`, `utils/`
- Packaging/config: `pyproject.toml`, `setup.py`, `requirements*.txt`, `constraints.txt`, `config*.yaml`
- Scripts: `scripts/`, `setup.sh`, `pa`
- Test and CI artifacts: `tests/`, `.github/workflows/`
- Existing docs for cross-checking implementation drift

## Important truthfulness note

This repository includes **multiple overlapping and partially inconsistent surfaces** (e.g., different CLI styles and stale docs). This package prioritizes:

1. Actual executable implementation in `cli/main.py` + `orchestration/analysis_pipeline.py`
2. Then secondary scripts/tools and tests
3. Then markdown docs (which are sometimes stale)

When behavior is inferred rather than explicit, it is marked as **Inferred from code structure**.
