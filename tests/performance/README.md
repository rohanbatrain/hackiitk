# Performance Tests

This directory contains performance tests for the Offline Policy Gap Analyzer. These tests validate that the system meets performance requirements on consumer hardware.

## Test Categories

### 1. Embedding Performance Tests
- **test_embedding_throughput_meets_requirement**: Validates 50+ chunks/min throughput
- **test_embedding_batch_faster_than_sequential**: Verifies batch processing optimization
- **test_embedding_caching_improves_performance**: Tests caching effectiveness

### 2. LLM Performance Tests
- **test_llm_token_generation_speed**: Validates 10+ tokens/sec generation
- **test_llm_memory_usage_3b_model**: Verifies 3B model stays within 8GB

### 3. Pipeline Performance Tests
- **test_20_page_policy_analysis_time**: Validates complete analysis within 10 minutes
- **test_pipeline_memory_stays_within_limits**: Verifies memory constraints
- **test_pipeline_provides_progress_indicators**: Tests progress tracking

### 4. Optimization Tests
- **test_parallel_embedding_when_safe**: Validates parallel processing
- **test_optimal_batch_size_calculation**: Tests batch size optimization

## Running Tests

### Run All Performance Tests
```bash
pytest tests/performance/ -v -s
```

### Run Specific Test Category
```bash
# Embedding tests only
pytest tests/performance/test_performance.py::TestEmbeddingPerformance -v -s

# LLM tests only
pytest tests/performance/test_performance.py::TestLLMPerformance -v -s

# Pipeline tests only
pytest tests/performance/test_performance.py::TestPipelinePerformance -v -s
```

### Run Individual Test
```bash
pytest tests/performance/test_performance.py::TestEmbeddingPerformance::test_embedding_throughput_meets_requirement -v -s
```

## Prerequisites

Performance tests require:

1. **Embedding Model**: `models/embeddings/all-MiniLM-L6-v2`
2. **LLM Model**: Ollama with `qwen2.5:3b` installed
3. **Reference Catalog**: `data/reference_catalog.json`
4. **Sufficient RAM**: 8GB minimum for 3B model tests

### Setup

```bash
# Download models
python scripts/download_models.py

# Install Ollama (if not installed)
# Visit: https://ollama.ai

# Pull LLM model
ollama pull qwen2.5:3b

# Build reference catalog (if needed)
python -c "from reference_builder.reference_catalog import ReferenceCatalog; \
           cat = ReferenceCatalog(); \
           cat.build_from_cis_guide('data/cis_guide.pdf'); \
           cat.persist('data/reference_catalog.json')"
```

## Performance Requirements

Tests validate these requirements:

| Metric | Requirement | Test |
|--------|-------------|------|
| Embedding throughput | ≥50 chunks/min | test_embedding_throughput_meets_requirement |
| LLM generation speed | ≥10 tokens/sec | test_llm_token_generation_speed |
| 3B model memory | ≤8GB | test_llm_memory_usage_3b_model |
| 20-page analysis time | ≤10 minutes | test_20_page_policy_analysis_time |
| Batch speedup | ≥2x | test_embedding_batch_faster_than_sequential |

## Test Output

Performance tests provide detailed output:

```
✓ Embedding throughput: 125.3 chunks/min
✓ Batch processing speedup: 3.2x
✓ Token generation speed: 15.2 tokens/sec
✓ 3B model memory usage: 6.8GB (limit: 8GB)
✓ 20-page policy analysis time: 7.5 minutes
```

## Troubleshooting

### Tests Skipped

If tests are skipped, check:

```bash
# Check embedding model
ls -la models/embeddings/all-MiniLM-L6-v2/

# Check Ollama
ollama list

# Check reference catalog
ls -la data/reference_catalog.json
```

### Performance Below Requirements

If tests fail due to performance:

1. **Check CPU usage**: Should be near 100% during tests
2. **Close other applications**: Free up CPU and RAM
3. **Verify model quantization**: GGUF format for LLM
4. **Check disk I/O**: SSD recommended for vector store
5. **Review configuration**: See `docs/PERFORMANCE.md`

### Memory Issues

If tests fail with OOM errors:

1. **Use smaller model**: Switch to 3B instead of 7B
2. **Reduce batch size**: Lower from 64 to 32
3. **Clear cache**: `engine.clear_cache()`
4. **Close applications**: Free up RAM
5. **Check swap**: Ensure swap is enabled

## Benchmarking

For detailed benchmarking:

```bash
# Run with timing
pytest tests/performance/ -v -s --durations=10

# Generate JSON report
pytest tests/performance/ --json-report --json-report-file=performance.json

# Profile with cProfile
python -m cProfile -o performance.prof -m pytest tests/performance/
```

## Continuous Integration

Performance tests can be run in CI/CD:

```yaml
# .github/workflows/performance.yml
- name: Run performance tests
  run: |
    pytest tests/performance/ -v --tb=short
  timeout-minutes: 30
```

## See Also

- [Performance Optimization Guide](../../docs/PERFORMANCE.md)
- [Architecture Documentation](../../docs/ARCHITECTURE.md)
- [Troubleshooting Guide](../../docs/TROUBLESHOOTING.md)
