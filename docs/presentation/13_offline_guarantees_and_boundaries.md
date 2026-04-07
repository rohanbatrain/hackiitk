# 13 – Offline Guarantees and Boundaries

## What is offline in active design

- Embeddings are generated locally from local model path.
- Vector retrieval runs against local Chroma persistence.
- LLM runtime expects local Ollama endpoint or local llama.cpp model file.
- Reports/roadmaps/audit logs are local file outputs.

## Practical offline boundary definition

“Fully offline” is true **after all required models/dependencies are already installed locally**.

## Hidden/conditional network dependencies

- Initial model downloads (`scripts/setup_models.py`, `scripts/download_models.py`)
- If model path points to unresolved/remote resources, runtime may fail or try dependency-level fetch behavior outside intended path
- Ollama requires local service availability; it is local network (`localhost`) not internet

## Verification strategy

- Restrict network during analysis run
- Confirm no cloud endpoint in config/runtime paths
- Confirm successful output generation from local resources only

## Boundary caveats

- Repository contains docs and scripts with mixed assumptions; offline guarantee should be validated against the exact execution path used in production deployment.
