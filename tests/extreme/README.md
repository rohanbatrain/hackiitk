# Extreme Testing Framework

Comprehensive stress, chaos, adversarial, boundary, and performance testing framework for the Offline Policy Gap Analyzer.

## Overview

This testing framework goes beyond standard unit and integration tests to validate system behavior under extreme conditions, including:

- **Stress Testing**: Maximum load scenarios (100-page documents, 500k words, 10k+ chunks, concurrent operations)
- **Chaos Engineering**: Fault injection (disk failures, memory exhaustion, corruption, process interruptions)
- **Adversarial Testing**: Security boundaries (malicious PDFs, injection attacks, buffer overflows, path traversal)
- **Boundary Testing**: Edge cases (empty documents, extreme structures, encoding attacks, coverage boundaries)
- **Performance Profiling**: Degradation curves, bottleneck identification, baseline establishment
- **Property Testing**: Expanded property-based tests with aggressive strategies

## Directory Structure

```
tests/extreme/
├── __init__.py           # Package initialization
├── config.py             # Test configuration management
├── models.py             # Data models (TestResult, Metrics, Reports)
├── base.py               # Base classes and utilities
├── runner.py             # Master test runner
├── reporter.py           # Test report generation
├── cli.py                # Command-line interface
├── README.md             # This file
├── engines/              # Test execution engines
│   ├── __init__.py
│   ├── stress_tester.py          # (To be implemented)
│   ├── chaos_engine.py           # (To be implemented)
│   ├── adversarial_tester.py     # (To be implemented)
│   ├── boundary_tester.py        # (To be implemented)
│   ├── performance_profiler.py   # (To be implemented)
│   └── property_expander.py      # (To be implemented)
├── support/              # Support components
│   ├── __init__.py
│   ├── fault_injector.py         # (To be implemented)
│   ├── test_data_generator.py    # (To be implemented)
│   ├── metrics_collector.py      # (To be implemented)
│   └── oracle_validator.py       # (To be implemented)
└── oracles/              # Known-good test cases
    └── README.md         # Oracle test case documentation
```

## Installation

The extreme testing framework is part of the main project. Ensure all dependencies are installed:

```bash
pip install -r requirements.txt
```

Additional dependencies for extreme testing:
- `psutil` - Resource monitoring
- `hypothesis` - Property-based testing
- `pytest` - Test execution

## Usage

### Running All Tests

```bash
python -m tests.extreme.cli
```

### Running Specific Categories

```bash
# Run only stress tests
python -m tests.extreme.cli --categories stress

# Run stress and chaos tests
python -m tests.extreme.cli --categories stress chaos
```

### Running Specific Requirements

```bash
# Run tests for specific requirements
python -m tests.extreme.cli --requirements 1.1 1.2 2.1
```

### Options

```bash
# Verbose output
python -m tests.extreme.cli --verbose

# Fail-fast mode (stop on first failure)
python -m tests.extreme.cli --fail-fast

# Custom output directory
python -m tests.extreme.cli --output-dir /path/to/output

# Custom concurrency
python -m tests.extreme.cli --concurrency 8

# Custom timeout (in seconds)
python -m tests.extreme.cli --timeout 7200
```

### Report Generation

By default, the framework generates reports in three formats:
- **HTML**: Human-readable report with visualizations
- **JSON**: Machine-readable report for processing
- **JUnit XML**: CI/CD integration format

Disable specific formats:
```bash
python -m tests.extreme.cli --no-html --no-json --no-junit
```

## Configuration

Test configuration can be customized via the `TestConfig` class in `config.py`:

```python
from tests.extreme.config import TestConfig

config = TestConfig(
    categories=['stress', 'chaos'],
    max_document_pages=200,
    max_concurrent_operations=10,
    verbose=True
)
```

### Key Configuration Parameters

- `categories`: Test categories to run
- `requirements`: Specific requirement IDs to test
- `concurrency`: Number of concurrent test workers
- `timeout_seconds`: Timeout for individual tests
- `max_document_pages`: Maximum document size for stress tests
- `max_concurrent_operations`: Maximum concurrent operations
- `fault_injection_points`: Number of fault injection points
- `property_test_multiplier`: Multiplier for property test cases

## Test Categories

### Stress Testing
Validates system behavior under maximum load:
- 100-page PDF documents
- 500,000-word documents
- 10,000+ chunks after segmentation
- 5+ concurrent analysis operations
- Resource leak detection

### Chaos Engineering
Injects faults to validate error handling:
- Disk full scenarios
- Memory exhaustion
- Model file corruption
- Process interruptions (SIGINT, SIGTERM, SIGKILL)
- File system permission errors
- Configuration chaos

### Adversarial Testing
Tests security boundaries:
- Malicious PDF files (embedded JavaScript, malformed structure)
- Buffer overflow attempts
- Encoding attacks (null bytes, Unicode control characters)
- Path traversal attempts
- Prompt injection attacks

### Boundary Testing
Validates edge cases:
- Empty and whitespace-only documents
- Structural anomalies (no headings, 100+ nesting levels)
- Extreme coverage boundaries (0 gaps, 49 gaps)
- Encoding diversity (Chinese, Arabic, Cyrillic, emoji)
- Similarity score boundaries

### Performance Profiling
Measures performance characteristics:
- Document size scaling (1 to 100 pages)
- Chunk count scaling (10 to 10,000 chunks)
- LLM context scaling (100 to 10,000 tokens)
- Bottleneck identification
- Baseline establishment

### Property Testing
Expanded property-based tests:
- 10x more test cases per property
- Aggressive search strategies
- Invariant testing
- Round-trip properties
- Metamorphic properties

## Reports

### HTML Report
Interactive report with:
- Executive summary
- Pass/fail statistics
- Category results
- Breaking points
- Failure modes
- Performance baselines

### JSON Report
Machine-readable report containing:
- All test results
- Detailed metrics
- Breaking points
- Failure modes
- Artifacts paths

### JUnit XML Report
CI/CD integration format compatible with:
- Jenkins
- GitLab CI
- GitHub Actions
- CircleCI

## Development

### Adding New Tests

1. Create test engine in `engines/` directory
2. Inherit from `BaseTestEngine` in `base.py`
3. Implement `run_tests()` method
4. Register engine in `runner.py`

Example:
```python
from tests.extreme.base import BaseTestEngine
from tests.extreme.models import TestResult, TestStatus

class MyTestEngine(BaseTestEngine):
    def run_tests(self) -> List[TestResult]:
        results = []
        
        with self._test_context("my_test_1") as ctx:
            # Test implementation
            pass
            
        result = self._create_test_result(
            test_id="my_test_1",
            requirement_id="1.1",
            category="my_category",
            status=TestStatus.PASS,
            duration=ctx['duration']
        )
        results.append(result)
        
        return results
```

### Adding Support Components

1. Create component in `support/` directory
2. Implement required interfaces
3. Use in test engines

## Requirements Coverage

This framework validates 80+ requirements from the comprehensive testing specification:
- Requirements 1-71: Functional requirements
- Requirement 72: Test orchestration
- Requirement 73: Failure mode documentation
- Requirements 74-80: Additional validation requirements

## License

Same as parent project.
