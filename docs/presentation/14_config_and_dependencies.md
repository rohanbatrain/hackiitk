# 14 – Config and Dependencies

## Dependency manifests

- `requirements.txt` (primary)
- `constraints.txt` (pinning constraints)
- `pyproject.toml` project dependencies
- `requirements-frozen.txt`, `requirements-ci.txt` (supporting variants)

## Key runtime dependencies

- Parsing: `PyMuPDF`, `pdfplumber`, `python-docx`, `chardet`
- Embedding/retrieval: `sentence-transformers`, `chromadb`, `rank-bm25`
- LLM orchestration: `langchain`, `langchain-community`, `langchain-ollama`, `llama-cpp-python`
- Validation/utilities: `jsonschema`, `pyyaml`, `psutil`, `click`, `rich`

## Config surfaces (important mismatch)

1. `config.example.yaml` and `utils/config_loader.py` expect mostly flat keys.
2. `config.yaml` in repo is nested by sections (`chunking`, `retrieval`, `llm`, ...).
3. `PipelineConfig` in `orchestration/analysis_pipeline.py` also expects flat keys.

Operational implication: not all config files in repo are directly interchangeable without transformation.

## PipelineConfig defaults (selected)

- chunk_size: 512
- overlap: 50
- top_k: 5
- temperature: 0.1
- max_tokens: 512
- model_path/model_name defaults around qwen2.5 variants
- embedding path default: `models/embeddings/all-MiniLM-L6-v2`
- vector store default: `vector_store/chroma_db`
- catalog default: `data/reference_catalog.json`
