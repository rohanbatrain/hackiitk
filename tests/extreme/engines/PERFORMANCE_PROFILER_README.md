# Performance Profiler

## Quick Start

The Performance Profiler measures performance degradation curves and identifies bottlenecks in the Offline Policy Gap Analyzer.

### Basic Usage

```python
from tests.extreme.engines.performance_profiler import PerformanceProfiler
from tests.extreme.config import TestConfig
from tests.extreme.support.metrics_collector import MetricsCollector
from tests.extreme.data_generator import TestDataGenerator

# Initialize
config = TestConfig(output_dir="./performance_output")
metrics_collector = MetricsCollector()
test_data_generator = TestDataGenerator()

profiler = PerformanceProfiler(
    config=config,
    metrics_collector=metrics_collector,
    test_data_generator=test_data_generator
)

# Run all profiling tests
results = profiler.run_tests()

# Or run individual tests
result = profiler.profile_document_size_scaling()
result = profiler.identify_bottlenecks()
result = profiler.establish_baselines()
result = profiler.generate_degradation_graphs()
```

### What It Tests

1. **Document Size Scaling** - Performance from 1 to 100 pages
2. **Chunk Count Scaling** - Performance from 10 to 10,000 chunks
3. **LLM Context Scaling** - LLM inference time from 100 to 10,000 tokens
4. **Bottleneck Identification** - Identifies slow pipeline stages
5. **Baseline Establishment** - Creates performance baselines for regression detection
6. **Degradation Graphs** - Generates visualizations and reports

### Output Files

All outputs are saved to `{output_dir}/performance_tests/`:

- `document_size/document_size_scaling_report.json` - Document size scaling data
- `chunk_count/chunk_count_scaling_report.json` - Chunk count scaling data
- `llm_context/llm_context_scaling_report.json` - LLM context scaling data
- `bottlenecks/bottleneck_report.json` - Identified bottlenecks
- `baselines/baselines.json` - Performance baselines
- `graphs/performance_comparison_report.md` - Comprehensive analysis
- `graphs/performance_trends.json` - Machine-readable trends

### Running Tests

```bash
# Run all performance profiler tests
pytest tests/extreme/engines/test_performance_profiler.py -v

# Run only fast unit tests (skip integration)
pytest tests/extreme/engines/test_performance_profiler.py -v -m "not slow"

# Run only integration tests
pytest tests/extreme/engines/test_performance_profiler.py -v -m "slow"
```

### Performance Characteristics

- **Execution Time**: 1-3 hours for complete profiling suite
- **Memory Usage**: 100-2000MB peak (scales with document size)
- **Disk Usage**: ~500MB for test documents and outputs

### Key Features

- **Performance Cliff Detection**: Automatically identifies non-linear degradation
- **Bottleneck Analysis**: Identifies slow pipeline stages
- **Baseline Tracking**: Enables regression detection
- **Multiple Visualizations**: CSV, text charts, markdown reports, JSON trends
- **Hardware Context**: Captures system info for baseline comparison

### Requirements Validated

- 19.1-19.7: Performance profiling and degradation analysis
- 74.1-74.6: Baseline establishment and regression detection

See [PERFORMANCE_PROFILER_SUMMARY.md](PERFORMANCE_PROFILER_SUMMARY.md) for detailed documentation.
