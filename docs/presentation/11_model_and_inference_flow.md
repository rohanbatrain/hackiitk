# 11 – Model and Inference Flow

## Embedding path

- Engine: `retrieval/embedding_engine.py`
- Backend: `SentenceTransformer` loaded from local model path
- Output: normalized 384-d vectors (`all-MiniLM-L6-v2` expectation)

## Retrieval path

- Dense:
  - query embedding -> Chroma similarity search on `catalog` collection
  - distance converted to similarity score
- Sparse:
  - BM25 index over catalog subcategory descriptions
- Fusion:
  - weighted merge and de-dup by subcategory id
- Optional rerank:
  - cross-encoder scoring with `reranker.py`

## LLM path

- Runtime abstraction: `analysis/llm_runtime.py`
- Backends:
  - `ollama` at `http://localhost:11434`
  - `llama-cpp` via local model file
- Structured generation:
  - prompt + schema appended
  - JSON parsing with retries

## Stage A vs Stage B compute split

- Stage A: non-LLM deterministic scoring
- Stage B: LLM reasoning only for unresolved statuses

## Inference constraints

- Low temperature defaults (0.1) for conservative output behavior
- Stage B prompt explicitly asks for JSON-only response
