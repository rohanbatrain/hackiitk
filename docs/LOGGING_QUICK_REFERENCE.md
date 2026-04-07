# Logging Quick Reference

## CLI Usage

```bash
# Standard logging
uv run policy-analyzer --policy-path policy.pdf --domain isms

# Verbose logging (detailed debug info)
uv run policy-analyzer --policy-path policy.pdf --domain isms --verbose
```

## Log Levels

| Level    | When to Use                          | Color   |
|----------|--------------------------------------|---------|
| DEBUG    | Detailed debugging (verbose mode)    | Cyan    |
| INFO     | General information                  | Green   |
| WARNING  | Warning messages                     | Yellow  |
| ERROR    | Error conditions                     | Red     |
| CRITICAL | Critical failures                    | Magenta |

## Code Examples

### Basic Logging

```python
from utils.logger import get_logger

logger = get_logger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")
```

### Function Tracing (Verbose Mode)

```python
from utils.logger import log_function_call

@log_function_call('component_name')
def my_function(arg1, arg2):
    return arg1 + arg2
```

### Performance Monitoring

```python
from utils.logger import log_performance

@log_performance('operation_name', 'component_name')
def expensive_operation():
    # ... operation logic
    pass
```

### Memory Tracking (Verbose Mode)

```python
from utils.logger import log_memory_usage

@log_memory_usage('component_name')
def memory_intensive_operation():
    # ... operation logic
    pass
```

### Structured Context

```python
import json

logger.info(
    "Operation complete",
    extra={'context': json.dumps({'count': 100, 'duration': 5.2})}
)
```

## Decorator Combinations

```python
from utils.logger import log_function_call, log_performance, log_memory_usage

# Full instrumentation
@log_performance('analysis', 'analyzer')
@log_memory_usage('analyzer')
@log_function_call('analyzer')
def analyze_data(data):
    return results
```

## Output Files

| File                                    | Content                          |
|-----------------------------------------|----------------------------------|
| `analysis_YYYYMMDD_HHMMSS.log`         | Standard logs (INFO+)            |
| `analysis_YYYYMMDD_HHMMSS_verbose.log` | Verbose logs (DEBUG+, all details) |

## Common Patterns

### Error Handling with Logging

```python
try:
    result = risky_operation()
except Exception as e:
    logger.error(f"Operation failed: {e}", exc_info=True)
    raise
```

### Progress Logging

```python
total = len(items)
for i, item in enumerate(items):
    logger.info(f"Processing {i+1}/{total}: {item.name}")
    process(item)
```

### Conditional Verbose Logging

```python
if logger.isEnabledFor(logging.DEBUG):
    logger.debug(f"Detailed info: {expensive_debug_info()}")
```

## Tips

- Use `--verbose` for debugging and development
- Standard mode for production
- Check verbose log file for complete traces
- Decorators only add overhead in verbose mode
- Colors only appear in terminal output
