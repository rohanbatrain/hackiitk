# Retrieval Components

This directory contains components for hybrid retrieval combining semantic and keyword search.

## Components

### VectorStore (`vector_store.py`)

Local vector storage using ChromaDB for embedding persistence and similarity search.

**Features:**
- Persistent storage to disk for offline operation
- Multiple collection support (reference catalog, policy embeddings)
- Cosine similarity search
- Metadata preservation

**Python Version Compatibility:**

⚠️ **Important**: ChromaDB currently requires Python < 3.14 due to Pydantic v1 compatibility issues.

- **Recommended**: Python 3.11 or 3.12
- **Not supported**: Python 3.14+

If you're using Python 3.14+, you'll see this error:
```
RuntimeError: ChromaDB is not available: unable to infer type for attribute "chroma_server_nofile"
```

**Workaround for Testing:**
A mock implementation is provided in `tests/mocks/mock_vector_store.py` for basic testing on Python 3.14+.

**Usage:**

```python
from retrieval.vector_store import VectorStore
import numpy as np

# Initialize
store = VectorStore(persist_directory="./vector_store")

# Add embeddings
embeddings = np.random.rand(10, 384).astype(np.float32)
metadata = [
    {
        "chunk_id": f"chunk_{i}",
        "source_text": f"Text {i}",
        "CSF_Subcategory": "GV.RM-01"
    }
    for i in range(10)
]

store.add_embeddings(
    embeddings=embeddings,
    metadata=metadata,
    collection_name="policy_embeddings"
)

# Search
query = np.random.rand(384).astype(np.float32)
results = store.similarity_search(
    query_embedding=query,
    collection_name="policy_embeddings",
    top_k=5
)

# Results contain: id, distance, metadata, document
for result in results:
    print(f"ID: {result['id']}, Distance: {result['distance']}")
```

### EmbeddingEngine (`embedding_engine.py`)

Local sentence transformer for generating embeddings offline.

**Model**: all-MiniLM-L6-v2 (384 dimensions)

## Testing

Unit tests: `tests/unit/test_vector_store.py`
Property tests: `tests/property/test_vector_store.py`

**Note**: Tests will be skipped on Python 3.14+ with a warning. Use Python 3.11 or 3.12 for full test coverage.

## Requirements

See `requirements.txt` for dependencies:
- chromadb>=0.5.0
- sentence-transformers>=2.2.0
- numpy>=1.24.0
