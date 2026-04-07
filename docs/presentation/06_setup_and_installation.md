# 06 – Setup and Installation

## Runtime prerequisites

- Python 3.11 or 3.12 recommended by repository docs/workflows
- Local LLM runtime:
  - Ollama service (default runtime path), or
  - llama.cpp-compatible local model file
- Local embedding model files
- ChromaDB-compatible Python environment

## Canonical install paths in repository

### Python dependencies

- `pip install -r requirements.txt`
- Optional pinning guidance in `constraints.txt`

### Package install

- `pip install -e .`
- CLI entrypoint script: `policy-analyzer`

### Model setup scripts

- `python scripts/setup_models.py --all`
- `python scripts/download_models.py --all`

### Catalog setup

- Preferred runtime uses `data/reference_catalog.json` if present
- If absent, pipeline tries to build using `catalog.build_from_cis_guide(...)`

## Practical note on this clone

This clone includes many pre-existing artifacts and may not include runnable local model binaries in Linux sandbox paths; setup should be validated in target environment.
