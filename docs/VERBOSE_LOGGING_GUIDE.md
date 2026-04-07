# Verbose Logging Guide

## Overview

The Offline Policy Gap Analyzer includes a comprehensive logging system with verbose mode support for in-depth debugging and performance analysis.

## Features

### Standard Logging
- Timestamped log entries
- Component-based organization
- Multiple severity levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Color-coded console output
- File-based persistence

### Verbose Mode
When enabled with `--verbose`, the system provides:
- **Function tracing**: Entry/exit logging with arguments and return values
- **Performance metrics**: Execution time for all operations
- **Memory tracking**: Memory usage before/after operations
- **Detailed stack traces**: Full exception information
- **Component-level debugging**: Fine-grained operation details
- **Separate verbose log file**: Complete debugging information saved separately

## Usage

### Enable Verbose Mode

```bash
# Basic usage with verbose logging
uv run policy-analyzer --policy-path policy.pdf --domain isms --verbose

# With custom output directory
uv run policy-analyzer --policy-path policy.pdf --output-dir ./results --verbose

# With custom configuration
uv run policy-analyzer --policy-path policy.pdf --config config.yaml --verbose
```

### Log Files

When verbose mode is enabled, two log files are created:

1. **Standard log**: `analysis_YYYYMMDD_HHMMSS.log`
   - Contains INFO level and above
   - Clean, production-ready format
   - Suitable for monitoring

2. **Verbose log**: `analysis_YYYYMMDD_HHMMSS_verbose.log`
   - Contains ALL debug information
   - Function traces with file/line numbers
   - Performance metrics
   - Memory usage data
   - Complete stack traces

## Log Format

### Standard Format
```
[2026-04-08 00:55:22.527] INFO     [component_name      ] Message text
```

### Verbose Format
```
[2026-04-08 00:55:22.527] DEBUG    [component_name      ] Message text (filename.py:123 in function_name)
```

### Color Coding (Console)
- **DEBUG**: Cyan
- **INFO**: Green
- **WARNING**: Yellow
- **ERROR**: Red
- **CRITICAL**: Magenta

## Using Verbose Logging in Code

### Function Call Tracing

```python
from utils.logger import log_function_call, get_logger

logger = get_logger(__name__)

@log_function_call('document_parser')
def parse_document(file_path: str, options: dict):
    """Parse a document with automatic entry/exit logging."""
    logger.debug(f"Processing file: {file_path}")
    # ... parsing logic
    return parsed_doc
```

Output in verbose mode:
```
→ Entering parse_document('policy.pdf', {'extract_images': False})
  Processing file: policy.pdf
← Exiting parse_document -> ParsedDocument(...) [1234.56ms]
```

### Performance Monitoring

```python
from utils.logger import log_performance

@log_performance('embedding_generation', 'embedding_engine')
def generate_embeddings(chunks: list):
    """Generate embeddings with automatic timing."""
    # ... embedding logic
    return embeddings
```

Output:
```
Starting embedding_generation...
Completed embedding_generation in 5.23s
```

### Memory Usage Tracking

```python
from utils.logger import log_memory_usage

@log_memory_usage('vector_store')
def load_large_dataset(path: str):
    """Load dataset with memory tracking."""
    # ... loading logic
    return data
```

Output in verbose mode:
```
Memory before load_large_dataset: 245.32 MB
Memory after load_large_dataset: 1024.67 MB (Δ +779.35 MB)
```

### Combining Decorators

```python
@log_performance('document_analysis', 'analyzer')
@log_memory_usage('analyzer')
@log_function_call('analyzer')
def analyze_document(doc: ParsedDocument):
    """Fully instrumented function."""
    # ... analysis logic
    return results
```

## Component Loggers

Each component has its own logger for organized output:

```python
from utils.logger import get_logger

logger = get_logger('my_component')

logger.debug("Detailed debugging information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred")
logger.critical("Critical failure")
```

## Structured Context

Add structured context to log messages:

```python
logger.info(
    "Processing complete",
    extra={
        'context': json.dumps({
            'chunks_processed': 150,
            'duration_seconds': 12.5,
            'success_rate': 0.98
        })
    }
)
```

Output:
```
[2026-04-08 00:55:22.527] INFO [component] Processing complete | {"chunks_processed": 150, "duration_seconds": 12.5, "success_rate": 0.98}
```

## Best Practices

### When to Use Verbose Mode

✅ **Use verbose mode for:**
- Debugging complex issues
- Performance profiling
- Understanding system behavior
- Development and testing
- Troubleshooting production issues

❌ **Avoid verbose mode for:**
- Production deployments (unless debugging)
- Performance-critical operations
- Automated batch processing
- CI/CD pipelines (unless investigating failures)

### Performance Impact

Verbose logging has minimal overhead:
- Function tracing: ~0.1-0.5ms per call
- Memory tracking: ~1-2ms per measurement
- File I/O: Asynchronous, non-blocking

### Log File Management

Verbose logs can grow large. Recommendations:
- Archive logs after analysis
- Use log rotation for long-running processes
- Clean up old logs periodically
- Compress archived logs

```bash
# Clean up old logs (keep last 7 days)
find outputs/ -name "*.log" -mtime +7 -delete

# Compress old logs
find outputs/ -name "*.log" -mtime +1 -exec gzip {} \;
```

## Troubleshooting

### No Verbose Output

If `--verbose` doesn't produce detailed logs:

1. Check that the flag is being passed correctly
2. Verify log level is set to DEBUG
3. Ensure decorators are applied to functions
4. Check that psutil is installed for memory tracking

### Log Files Not Created

If log files aren't being created:

1. Check output directory permissions
2. Verify `--output-dir` is specified or default exists
3. Check disk space availability
4. Review file system errors in console

### Performance Issues

If verbose logging causes slowdowns:

1. Disable memory tracking (most expensive)
2. Reduce function tracing scope
3. Use standard logging instead
4. Profile specific components only

## Examples

### Example 1: Debug Document Parsing

```bash
uv run policy-analyzer \
  --policy-path problematic_policy.pdf \
  --domain isms \
  --verbose \
  --output-dir ./debug_output
```

Check `debug_output/analysis_*_verbose.log` for:
- PDF parsing details
- Text extraction issues
- Character encoding problems
- Page-by-page processing

### Example 2: Profile Performance

```bash
uv run policy-analyzer \
  --policy-path large_policy.pdf \
  --domain isms \
  --verbose \
  --output-dir ./performance_test
```

Analyze verbose log for:
- Slowest operations
- Memory bottlenecks
- I/O wait times
- LLM inference duration

### Example 3: Trace Retrieval Issues

```bash
uv run policy-analyzer \
  --policy-path policy.pdf \
  --domain isms \
  --verbose \
  --output-dir ./retrieval_debug
```

Review verbose log for:
- Embedding generation
- Vector store operations
- Similarity search results
- Reranking decisions

## Advanced Configuration

### Programmatic Setup

```python
from pathlib import Path
from utils.logger import setup_logging, get_logger

# Setup with verbose mode
setup_logging(
    output_dir=Path('./logs'),
    log_level='DEBUG',
    console_output=True,
    verbose=True
)

logger = get_logger('my_component')
logger.debug("Verbose logging is active")
```

### Custom Formatters

```python
from utils.logger import ComponentFormatter
import logging

# Create custom formatter
formatter = ComponentFormatter(
    include_component=True,
    use_colors=True,
    verbose=True
)

# Apply to handler
handler = logging.StreamHandler()
handler.setFormatter(formatter)
```

## Summary

The verbose logging system provides comprehensive debugging capabilities:

- **Easy activation**: Single `--verbose` flag
- **Minimal overhead**: Optimized for production use
- **Rich information**: Function traces, timing, memory
- **Organized output**: Component-based, color-coded
- **Flexible**: Decorators for selective instrumentation

Use verbose mode to gain deep insights into system behavior and quickly diagnose issues.
