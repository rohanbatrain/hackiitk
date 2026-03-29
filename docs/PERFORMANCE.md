# Performance Optimization Guide

This document provides guidance on optimizing the performance of the Offline Policy Gap Analyzer for different hardware configurations and use cases.

## Performance Requirements

The system is designed to meet the following performance targets on consumer hardware:

- **20-page policy analysis**: Complete within 10 minutes
- **Embedding throughput**: Process 50+ chunks per minute
- **LLM generation speed**: Generate 10+ tokens per second
- **Memory usage**: 
  - 3B models: Stay within 8GB RAM
  - 7B models: Stay within 16GB RAM

## Hardware Recommendations

### Minimum Configuration
- **CPU**: 4 cores, 2.0 GHz
- **RAM**: 8GB
- **Storage**: 10GB free space
- **Model**: Qwen2.5-3B-Instruct (quantized)

### Recommended Configuration
- **CPU**: 8 cores, 3.0 GHz
- **RAM**: 16GB
- **Storage**: 20GB free space
- **Model**: Qwen3-8B-Instruct (quantized)

### Optimal Configuration
- **CPU**: 16+ cores, 3.5+ GHz
- **RAM**: 32GB
- **Storage**: 50GB free space
- **Model**: Mistral-7B or larger (quantized)

## Optimization Strategies

### 1. Batch Size Tuning

The embedding engine uses configurable batch sizes for optimal throughput:

```python
from retrieval.embedding_engine import EmbeddingEngine

# Default batch size (64) - good for most systems
engine = EmbeddingEngine(model_path="models/embeddings/all-MiniLM-L6-v2")

# Larger batch size for systems with more RAM
embeddings = engine.embed_batch(texts, batch_size=128)

# Smaller batch size for memory-constrained systems
embeddings = engine.embed_batch(texts, batch_size=32)
```

**Tuning Guidelines:**
- 8GB RAM: batch_size=32-64
- 16GB RAM: batch_size=64-128
- 32GB+ RAM: batch_size=128-256

### 2. Embedding Caching

The embedding engine includes built-in caching for repeated operations:

```python
# Enable caching (default)
engine = EmbeddingEngine(
    model_path="models/embeddings/all-MiniLM-L6-v2",
    enable_cache=True,
    cache_size=1000
)

# Check cache statistics
stats = engine.get_cache_stats()
print(f"Cache: {stats['size']}/{stats['capacity']}")

# Clear cache if needed
engine.clear_cache()
```

**Benefits:**
- Repeated embeddings are instant (no recomputation)
- Useful when analyzing multiple similar policies
- Reduces CPU usage for common text patterns

### 3. Model Selection

Choose the appropriate model based on your hardware and accuracy requirements:

| Model | Size | RAM | Speed | Accuracy |
|-------|------|-----|-------|----------|
| Qwen2.5-3B | 2.0GB | 8GB | Fast | Good |
| Phi-3.5-mini | 2.5GB | 8GB | Fast | Good |
| Mistral-7B | 4.5GB | 16GB | Medium | Excellent |
| Qwen3-8B | 5.0GB | 16GB | Medium | Excellent |

**Configuration:**

```yaml
# config.yaml
model_name: "qwen2.5:3b"  # Fast, low memory
# model_name: "mistral:7b"  # Better accuracy, more memory
```

### 4. Parallel Processing

The system automatically uses parallel processing where safe:

```python
from utils.performance import BatchProcessor

# Process items in optimized batches
processor = BatchProcessor()
results = processor.process_in_batches(
    items=chunks,
    process_func=embed_function,
    batch_size=64,
    show_progress=True
)
```

**Parallelization Points:**
- Embedding generation (batch processing)
- Document parsing (multi-page PDFs)
- Vector similarity search

### 5. Memory Management

Monitor and optimize memory usage:

```python
from utils.performance import MemoryMonitor

monitor = MemoryMonitor(threshold=0.9)

# Check memory before operations
if monitor.is_memory_critical():
    print("Warning: Memory usage high")
    monitor.log_memory_status()

# Get available memory
available_mb = monitor.get_available_memory_mb()
print(f"Available: {available_mb:.0f}MB")
```

**Memory Optimization Tips:**
- Use smaller batch sizes if memory is constrained
- Clear embedding cache periodically
- Process large policies in chunks
- Use 3B models instead of 7B models

### 6. Progress Tracking

Enable progress indicators for long-running operations:

```python
from utils.progress import ProgressIndicator, StepProgress

# For batch operations
progress = ProgressIndicator(total=100, operation_name="Processing")
for i in range(100):
    # Do work
    progress.update()
progress.finish()

# For multi-step workflows
steps = StepProgress(total_steps=5, operation_name="Analysis")
steps.start_step("Parsing document")
# ... do work ...
steps.start_step("Embedding chunks")
# ... do work ...
steps.finish()
```

## Performance Profiling

### Running Performance Tests

```bash
# Run all performance tests
pytest tests/performance/test_performance.py -v -s

# Run specific test
pytest tests/performance/test_performance.py::TestEmbeddingPerformance::test_embedding_throughput_meets_requirement -v -s

# Run with detailed output
pytest tests/performance/test_performance.py -v -s --log-cli-level=INFO
```

### Profiling Individual Components

```python
from utils.performance import profile_operation, PerformanceMonitor

# Profile a single operation
with profile_operation("embedding", monitor=None) as metadata:
    embeddings = engine.embed_batch(texts)
    metadata['items_processed'] = len(texts)

# Monitor entire pipeline
monitor = PerformanceMonitor()
monitor.start()

# ... run analysis ...

summary = monitor.get_summary()
monitor.log_summary()
```

### Interpreting Results

Performance test output includes:

```
✓ Embedding throughput: 125.3 chunks/min
✓ Token generation speed: 15.2 tokens/sec
✓ 3B model memory usage: 6.8GB (limit: 8GB)
✓ 20-page policy analysis time: 7.5 minutes
```

**What to look for:**
- Embedding throughput should be >50 chunks/min
- Token generation should be >10 tokens/sec
- Memory usage should stay within limits
- Total analysis time should be <10 minutes

## Troubleshooting Performance Issues

### Slow Embedding Generation

**Symptoms:** Embedding takes >2 minutes per 100 chunks

**Solutions:**
1. Increase batch size: `embed_batch(texts, batch_size=128)`
2. Enable caching: `EmbeddingEngine(enable_cache=True)`
3. Check CPU usage (should be near 100% during embedding)
4. Verify model is loaded from local disk (not network)

### Slow LLM Generation

**Symptoms:** LLM generates <5 tokens/sec

**Solutions:**
1. Use smaller model (3B instead of 7B)
2. Reduce max_tokens: `generate(max_tokens=256)`
3. Check Ollama is running: `ollama list`
4. Verify model is quantized (GGUF format)
5. Close other applications to free CPU

### High Memory Usage

**Symptoms:** System runs out of memory or swaps heavily

**Solutions:**
1. Use smaller model (3B instead of 7B)
2. Reduce batch size: `embed_batch(texts, batch_size=32)`
3. Clear embedding cache: `engine.clear_cache()`
4. Process policy in smaller sections
5. Close other applications

### Long Analysis Time

**Symptoms:** 20-page policy takes >10 minutes

**Solutions:**
1. Profile to identify bottleneck: `PerformanceMonitor`
2. Optimize batch sizes for your hardware
3. Enable caching for repeated operations
4. Use faster model (Qwen2.5-3B)
5. Reduce top_k retrieval: `top_k=3`

## Configuration Examples

### Fast Analysis (Minimum Accuracy)

```yaml
# config.yaml
chunk_size: 256  # Smaller chunks
overlap: 25
top_k: 3  # Fewer retrieval results
temperature: 0.1
max_tokens: 256  # Shorter generations
model_name: "qwen2.5:3b"
```

### Balanced (Recommended)

```yaml
# config.yaml
chunk_size: 512
overlap: 50
top_k: 5
temperature: 0.1
max_tokens: 512
model_name: "qwen2.5:3b"
```

### High Accuracy (Slower)

```yaml
# config.yaml
chunk_size: 768  # Larger chunks
overlap: 100
top_k: 10  # More retrieval results
temperature: 0.1
max_tokens: 1024  # Longer generations
model_name: "mistral:7b"
```

## Benchmarking

### System Benchmarks

Run benchmarks to establish baseline performance:

```bash
# Benchmark embedding engine
python -m tests.performance.benchmark_embedding

# Benchmark LLM runtime
python -m tests.performance.benchmark_llm

# Benchmark complete pipeline
python -m tests.performance.benchmark_pipeline
```

### Expected Performance by Hardware

| Hardware | Embedding | LLM Speed | 20-page Analysis |
|----------|-----------|-----------|------------------|
| 4-core, 8GB | 60 chunks/min | 12 tok/sec | 9 minutes |
| 8-core, 16GB | 120 chunks/min | 18 tok/sec | 6 minutes |
| 16-core, 32GB | 200 chunks/min | 25 tok/sec | 4 minutes |

## Advanced Optimization

### Custom Batch Processing

```python
from utils.performance import BatchProcessor

# Calculate optimal batch size
processor = BatchProcessor()
optimal_size = processor.optimal_batch_size(
    item_size_bytes=2048,  # Estimated chunk size
    available_memory_mb=4000,  # Available RAM
    safety_factor=0.5  # Use 50% of available
)

print(f"Optimal batch size: {optimal_size}")
```

### Memory-Aware Processing

```python
from utils.performance import MemoryMonitor

monitor = MemoryMonitor(threshold=0.85)

# Adjust batch size based on memory
if monitor.check_memory() > 0.7:
    batch_size = 32  # Reduce batch size
else:
    batch_size = 128  # Use larger batches
```

### Profiling with Context Manager

```python
from utils.performance import profile_operation, PerformanceMonitor

monitor = PerformanceMonitor()
monitor.start()

with profile_operation("parse_document", monitor) as meta:
    parsed = parser.parse(policy_path)
    meta['items_processed'] = parsed.page_count

with profile_operation("embed_chunks", monitor) as meta:
    embeddings = engine.embed_batch(chunks)
    meta['items_processed'] = len(chunks)

# Get detailed summary
summary = monitor.get_summary()
for op, metrics in summary['operations'].items():
    print(f"{op}: {metrics['throughput_per_sec']:.1f} items/sec")
```

## Performance Monitoring in Production

### Logging Performance Metrics

```python
import logging
from utils.performance import PerformanceMonitor

logger = logging.getLogger(__name__)
monitor = PerformanceMonitor()

# Run analysis with monitoring
monitor.start()
result = pipeline.execute(policy_path)

# Log summary
monitor.log_summary()

# Save metrics to file
summary = monitor.get_summary()
with open('performance_metrics.json', 'w') as f:
    json.dump(summary, f, indent=2)
```

### Continuous Performance Testing

```bash
# Run performance tests in CI/CD
pytest tests/performance/ --benchmark-only

# Generate performance report
pytest tests/performance/ --benchmark-json=benchmark.json
```

## See Also

- [Architecture Documentation](ARCHITECTURE.md) - System design and components
- [Troubleshooting Guide](TROUBLESHOOTING.md) - Common issues and solutions
- [Dependencies](DEPENDENCIES.md) - Required packages and versions
