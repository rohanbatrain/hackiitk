# Embedding and Vector Store Stress Tester

## Overview

The Embedding and Vector Store Stress Tester is a comprehensive testing engine that validates embedding generation and vector store operations under extreme conditions, edge cases, and corruption scenarios.

## Features

### Embedding Quality Validation (Task 17.1)
- Tests embedding generation for 10,000+ chunks
- Validates handling of empty strings
- Tests extremely long text (10,000 words)
- Verifies constant dimensionality (384 dimensions)
- Validates similarity score ranges

### Embedding Corruption Testing (Task 17.2)
- Tests embeddings with NaN values
- Tests embeddings with infinite values
- Tests incorrect dimensionality
- Tests all-zero embeddings

### Vector Store Query Stress Testing (Task 17.3)
- 10,000 sequential similarity searches
- 100 concurrent similarity searches
- Large top_k values (10,000)
- Query latency scaling (100 to 100,000 embeddings)
- Search accuracy validation

## Requirements Coverage

| Requirement | Description | Tests |
|-------------|-------------|-------|
| 27.1 | Embeddings for 10,000+ chunks | test_embedding_quality_large_batch |
| 27.2 | Empty string handling | test_embedding_empty_strings |
| 27.3 | Extremely long text | test_embedding_extremely_long_text |
| 27.4 | Constant dimensionality | test_embedding_dimensionality_consistency |
| 27.5 | Similarity score range | test_embedding_similarity_score_range |
| 51.1 | NaN value detection | test_embedding_nan_values |
| 51.2 | Infinite value detection | test_embedding_infinite_values |
| 51.3 | Incorrect dimensionality | test_embedding_incorrect_dimensionality |
| 51.4 | All-zero embeddings | test_embedding_all_zeros |
| 44.1 | Sequential searches | test_sequential_similarity_searches |
| 44.2 | Concurrent searches | test_concurrent_similarity_searches |
| 44.3 | Large top_k | test_large_top_k |
| 44.4 | Query latency scaling | test_query_latency_scaling |
| 44.5 | Search accuracy | test_search_accuracy_with_size |

## Installation

No additional installation required. The tester uses existing project dependencies:
- `sentence-transformers` for embedding generation
- `chromadb` for vector store operations
- `numpy` for numerical operations

## Usage

### Basic Usage

```python
from tests.extreme.engines.embedding_vector_store_stress_tester import (
    EmbeddingVectorStoreStressTester,
    EmbeddingVectorStoreConfig
)
from tests.extreme.support.metrics_collector import MetricsCollector
from tests.extreme.data_generator import TestDataGenerator

# Configure tester
config = EmbeddingVectorStoreConfig(
    sequential_searches=10000,
    concurrent_searches=100,
    max_top_k=10000,
    embedding_test_sizes=[100, 1000, 10000, 100000],
    large_chunk_count=10000
)

# Initialize components
metrics = MetricsCollector()
data_gen = TestDataGenerator()

# Create tester
tester = EmbeddingVectorStoreStressTester(
    config=config,
    metrics_collector=metrics,
    data_generator=data_gen,
    output_dir="test_outputs/embedding_vector_store"
)

# Run all tests
results = tester.run_tests()

# Analyze results
for result in results:
    print(f"{result.test_id}: {result.status.value}")
```

### Running Specific Tests

```python
# Run only embedding quality tests
result = tester.test_embedding_quality_large_batch()
result = tester.test_embedding_empty_strings()
result = tester.test_embedding_extremely_long_text()

# Run only corruption tests
result = tester.test_embedding_nan_values()
result = tester.test_embedding_infinite_values()

# Run only vector store stress tests
result = tester.test_sequential_similarity_searches()
result = tester.test_concurrent_similarity_searches()
```

### Configuration Options

```python
@dataclass
class EmbeddingVectorStoreConfig:
    # Number of sequential searches to perform
    sequential_searches: int = 10000
    
    # Number of concurrent searches to perform
    concurrent_searches: int = 100
    
    # Maximum top_k value to test
    max_top_k: int = 10000
    
    # Collection sizes to test for latency scaling
    embedding_test_sizes: List[int] = [100, 1000, 10000, 100000]
    
    # Number of chunks for large batch testing
    large_chunk_count: int = 10000
```

## Running Tests

### Unit Tests

```bash
# Run all unit tests
pytest tests/extreme/engines/test_embedding_vector_store_stress_tester.py -v

# Run specific test
pytest tests/extreme/engines/test_embedding_vector_store_stress_tester.py::TestEmbeddingVectorStoreStressTester::test_embedding_quality_large_batch -v
```

### Example Script

```bash
# Run example usage script
python tests/extreme/engines/example_embedding_vector_store_usage.py
```

## Test Output

Each test returns a `TestResult` object with:
- `test_id`: Unique test identifier
- `requirement_id`: Comma-separated requirement IDs
- `category`: Test category (stress, boundary, chaos)
- `status`: Test status (PASS, FAIL, SKIP, ERROR)
- `duration_seconds`: Test execution time
- `error_message`: Error details (if failed)
- `metrics`: Performance metrics (memory, CPU, disk I/O)
- `artifacts`: List of generated files

### Example Output

```
✓ embedding_quality_large_batch
  Requirement: 27.1
  Duration: 45.23s
  Memory Peak: 2048.50 MB
  CPU Peak: 85.3%

✓ vector_store_sequential_searches
  Requirement: 44.1
  Duration: 120.45s
  Memory Peak: 512.30 MB
  CPU Peak: 45.2%
```

## Performance Considerations

### Large-Scale Tests
- `test_embedding_quality_large_batch`: ~30-60 seconds (10,000 embeddings)
- `test_sequential_similarity_searches`: ~2-5 minutes (10,000 searches)
- `test_large_top_k`: ~1-2 minutes (15,000 embeddings)
- `test_query_latency_scaling`: ~5-10 minutes (multiple collection sizes)

### Memory Usage
- Embedding generation: ~2-4 GB for 10,000 chunks
- Vector store operations: ~500 MB - 2 GB depending on collection size
- Concurrent operations: Additional overhead for thread management

### Optimization Tips
1. Reduce `sequential_searches` for faster testing (e.g., 1000 instead of 10,000)
2. Reduce `embedding_test_sizes` to skip large collections
3. Use smaller `large_chunk_count` for quicker validation
4. Run tests in parallel when possible

## Troubleshooting

### Model Not Found
```
Error: Model not found at models/all-MiniLM-L6-v2
```
**Solution**: Download the embedding model:
```bash
python scripts/download_models.py
```

### Memory Issues
```
Error: MemoryError during embedding generation
```
**Solution**: Reduce batch sizes or test with smaller collections:
```python
config = EmbeddingVectorStoreConfig(
    large_chunk_count=1000,  # Reduced from 10000
    embedding_test_sizes=[100, 1000]  # Skip large sizes
)
```

### ChromaDB Issues
```
Error: ChromaDB is not available
```
**Solution**: Ensure ChromaDB is installed and Python version is compatible:
```bash
pip install chromadb
# ChromaDB requires Python < 3.14
```

## Integration with Test Framework

The tester integrates with the broader extreme testing framework:

```python
from tests.extreme.runner import TestRunner
from tests.extreme.config import TestConfig

# Create test configuration
config = TestConfig(
    output_dir="test_outputs",
    enable_stress_tests=True
)

# Initialize runner
runner = TestRunner(config)

# Register embedding/vector store tester
runner.register_engine(tester)

# Run all tests
runner.run_all_tests()
```

## Contributing

When adding new tests:
1. Follow the existing naming convention: `test_<category>_<description>`
2. Add requirement ID in docstring: `**Validates: Requirements X.Y**`
3. Use `create_test_result()` helper for consistent result format
4. Add corresponding unit test in `test_embedding_vector_store_stress_tester.py`
5. Update this README with new test information

## References

- [Requirements Document](.kiro/specs/comprehensive-hardest-testing/requirements.md)
- [Design Document](.kiro/specs/comprehensive-hardest-testing/design.md)
- [Tasks Document](.kiro/specs/comprehensive-hardest-testing/tasks.md)
- [Embedding Engine](retrieval/embedding_engine.py)
- [Vector Store](retrieval/vector_store.py)
