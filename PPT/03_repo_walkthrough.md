# 03 – Repository Walkthrough

## Top-level layout (implementation-relevant)

- `cli/` – user-facing CLI entry and related utilities
- `orchestration/` – end-to-end pipeline wiring
- `ingestion/` – document parsing and chunking
- `reference_builder/` – CSF catalog model and builders/parsers
- `retrieval/` – embeddings, vector store, sparse BM25, rerank, hybrid retrieval
- `analysis/` – Stage A/Stage B gap analysis and LLM runtime
- `revision/` – policy revision generation
- `reporting/` – report/roadmap generation, output handling, audit logging
- `models/` – domain dataclasses and JSON schemas
- `utils/` – config, logging, progress, error handling, performance helpers
- `scripts/` – setup, model download, catalog build, verification scripts
- `tests/` – unit/integration/property/extreme/adversarial/synthetic/performance
- `.github/workflows/` – CI workflows

## Entrypoints and command surfaces

### Primary runtime CLI (current)

- `policy-analyzer` script entrypoint points to `cli.main:main` (`pyproject.toml`, `setup.py`)
- Direct module run via wrapper script `pa` executes `python -m cli.main`

### Additional/legacy command surfaces

- `analysis/cli.py` exists but is placeholder and not the main pipeline CLI path
- `cli/enhanced_commands.py` and `cli/completion.py` provide extra commands/utilities but are not the main argparse path

## Data and artifact directories

- `data/` – includes reference catalog and policy samples
- `audit_logs/` – many timestamped audit JSON files
- Output directories are created at runtime under configured output base (not pre-existing in this clone)

## Documentation drift warning

Multiple markdown docs describe commands/flows that differ from current code. For authoritative behavior, this package follows code paths in `cli/main.py` and `orchestration/analysis_pipeline.py`.
