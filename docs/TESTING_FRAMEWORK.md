# Testing Framework Documentation

## Overview

The Offline Policy Gap Analyzer includes a comprehensive testing framework that validates system behavior under extreme conditions. This framework goes beyond standard unit and integration tests to include stress testing, chaos engineering, adversarial testing, boundary testing, and performance profiling.

## Architecture

### High-Level Components

```
tests/
├── unit/              # Unit tests for individual components
├── integration/       # End-to-end integration tests
├── property/          # Property-based tests (Hypothesis)
├── performance/       # Performance benchmarks
├── extreme/           # Extreme testing framework
│   ├── engines/       # Test execution engines
│   ├── support/       # Support components
│   ├── oracles/       # Known-good test cases
│   ├── runner.py      # Master test orchestrator
│   ├── reporter.py    # Report generation
│   └── cli.py         # Command-line interface
├── synthetic/         # Generated test documents
├── adversarial/       # Malicious test samples
└── fixtures/          # Test fixtures and data
```

### Test Execution Engines

#### 1. Stress Tester
Tests system behavior under maximum load:
- **100-page documents** with 500k+ words
- **10,000+ chunks** after segmentation
- **Concurrent operations** (5+ simultaneous analyses)
- **Resource leak detection** over 100+ sequential runs
- **Breaking point identification** for various dimensions

**Location**: `tests/extreme/engines/stress_tester.py`

#### 2. Chaos Engine
Injects faults to validate error handling:
- **Disk failures** during output generation, audit logging, vector store persistence
- **Memory exhaustion** during LLM inference, embedding generation
- **Model corruption** (corrupted files, missing models, partial downloads)
- **Process interruptions** (SIGINT, SIGTERM, SIGKILL at 10+ pipeline stages)
- **Permission errors** for all file system operations
- **Configuration chaos** with 50+ invalid configurations

**Location**: `tests/extreme/engines/chaos_engine.py`

#### 3. Adversarial Tester
Tests security boundaries with malicious inputs:
- **Malicious PDFs** (20+ samples: embedded JavaScript, malformed structure, recursive references)
- **Buffer overflow** attempts with extremely long inputs
- **Encoding attacks** (null bytes, Unicode control characters, mixed encodings)
- **Path traversal** attempts (10+ attack patterns)
- **Prompt injection** attacks (15+ patterns for Stage B reasoning)
- **Chunking boundary attacks** (CSF references split across chunks)

**Location**: `tests/extreme/engines/adversarial_tester.py`

#### 4. Boundary Tester
Validates edge cases and extreme conditions:
- **Empty documents** (whitespace-only, special characters only)
- **Structural anomalies** (no headings, 100+ nesting levels, inconsistent hierarchy)
- **Coverage boundaries** (0 gaps, 49 gaps, exact threshold scores)
- **Encoding diversity** (10+ languages: Chinese, Arabic, Cyrillic, emoji)
- **Similarity score boundaries** (0.0, 0.3, 0.5, 0.8, 1.0)
- **Extreme parameters** (chunk overlap 0-512, top_k 1-10,000)

**Location**: `tests/extreme/engines/boundary_tester.py`

#### 5. Performance Profiler
Measures performance characteristics:
- **Document size scaling** (1 to 100 pages)
- **Chunk count scaling** (10 to 10,000 chunks)
- **LLM context scaling** (100 to 10,000 tokens)
- **Bottleneck identification** in analysis pipeline
- **Baseline establishment** on consumer hardware
- **Degradation curve generation**

**Location**: `tests/extreme/engines/performance_profiler.py`

#### 6. Property Test Expander
Expands property-based tests with aggressive strategies:
- **10x more test cases** per property (1000+ examples)
- **Hypothesis aggressive search** strategies
- **Invariant testing** (chunk preservation, gap completeness)
- **Round-trip properties** (parse → serialize → parse)
- **Metamorphic properties** (document extension/reduction)

**Location**: `tests/extreme/engines/property_expander.py`

### Support Components

#### Fault Injector
Provides mechanisms for simulating system failures:
- `inject_disk_full()` - Simulate disk full at specified path
- `inject_memory_limit()` - Simulate memory limit
- `inject_corruption()` - Corrupt specified file
- `inject_signal()` - Send signal to process after delay
- `inject_permission_error()` - Simulate permission error
- `inject_delay()` - Inject delay for operation

**Location**: `tests/extreme/support/fault_injector.py`

#### Test Data Generator
Generates diverse test data:
- **Synthetic policy documents** with configurable size, structure, coverage
- **Malicious PDFs** for security testing
- **Gap policies** with intentional gaps at specific subcategories
- **Extreme structures** (no headings, deep nesting, many sections)
- **Multilingual documents** (10+ languages and character sets)

**Location**: `tests/extreme/support/test_data_generator.py`

#### Metrics Collector
Collects and stores performance metrics:
- **Resource monitoring** (memory, CPU, disk I/O)
- **Resource leak detection** (memory, file handles, threads)
- **Baseline storage** for regression detection
- **Performance comparison** (alert on >20% degradation)

**Location**: `tests/extreme/support/metrics_collector.py`

#### Oracle Validator
Validates analysis accuracy:
- **20+ oracle test cases** with known-correct results
- **Accuracy measurement** (precision, recall, F1)
- **False positive/negative detection**
- **Oracle update mechanism** for intentional behavior changes

**Location**: `tests/extreme/support/oracle_validator.py`

### Master Test Runner

Orchestrates execution of all test categories:
- **Selective execution** by category or requirement
- **Parallel execution** with configurable concurrency
- **Progress indicators** during execution
- **Result aggregation** from all engines
- **Comprehensive reporting** (HTML, JSON, JUnit XML)

**Location**: `tests/extreme/runner.py`

### Test Reporter

Generates comprehensive test reports:
- **HTML reports** with executive summary, visualizations
- **JSON reports** for machine processing
- **JUnit XML** for CI/CD integration
- **Breaking points catalog** with thresholds
- **Failure modes documentation** with mitigations

**Location**: `tests/extreme/reporter.py`

## Test Data Management

### Oracle Test Cases

Location: `tests/extreme/oracles/`

Oracle test cases are known-good test cases with expected outputs. Each oracle includes:
- Policy document (markdown or PDF)
- Expected gaps (CSF subcategory IDs)
- Expected covered subcategories
- Expected gap count
- Tolerance (acceptable deviation)

**Format**:
```json
{
  "test_id": "oracle_001",
  "policy_document": "path/to/policy.md",
  "expected_gaps": ["ID.AM-1", "ID.AM-2", "PR.AC-1"],
  "expected_covered": ["ID.AM-3", "ID.AM-4", ...],
  "expected_gap_count": 3,
  "tolerance": 0.05,
  "description": "Minimal ISMS policy with identity management gaps"
}
```

### Malicious Samples

Location: `tests/adversarial/`

Malicious PDF samples for security testing:
- `malicious_001-005_javascript.pdf` - Embedded JavaScript
- `malicious_006-010_malformed.pdf` - Malformed structure
- `malicious_011-015_recursive.pdf` - Recursive references
- `malicious_016-020_large_object.pdf` - Large embedded objects
- `malicious_021-024_mixed.pdf` - Mixed attack vectors

Metadata: `tests/adversarial/samples_metadata.json`

### Synthetic Documents

Location: `tests/synthetic/`

Generated test documents:
- **Stress tests**: `stress_001_1pages.md` to `stress_100_100pages.md`
- **Gap patterns**: `gap_000_gaps.md` to `gap_049_gaps.md`
- **Multilingual**: `multilingual_001_chinese.md` to `multilingual_015_chinese_arabic.md`
- **Structures**: `structure_001_no_headings.md` to `structure_006_many_sections.md`
- **Boundaries**: `boundary_001_minimum_viable_1page.md` to `boundary_005_few_sections_50pages.md`
- **Performance**: `perf_001_baseline_10pages_50pct.md` to `perf_010_medium_20pages_50pct.md`

## CI/CD Integration

### GitHub Actions

Configuration: `.github/workflows/extreme-tests.yml`

**Workflows**:
- **Fast tests** (every push/PR): property, boundary, adversarial - 30 min
- **Stress tests** (schedule/manual): stress category - 2 hours
- **Chaos tests** (schedule/manual): chaos category - 2 hours
- **Performance tests** (schedule/manual): performance category - 2 hours
- **Full suite** (weekly): all categories with coverage - 4 hours

**Artifacts**:
- HTML reports
- JSON reports
- JUnit XML
- Coverage reports
- Performance baselines

### GitLab CI

Configuration: `.gitlab-ci-extreme.yml`

**Stages**:
1. `fast-tests` - Quick validation (every push/MR)
2. `stress-tests` - Maximum load tests (schedule/manual)
3. `chaos-tests` - Fault injection (schedule/manual)
4. `performance-tests` - Performance profiling (schedule/manual)
5. `full-suite` - Complete suite with coverage (schedule/manual)

**Pipeline Variables**:
- `TEST_CATEGORY` - Specify category (fast, stress, chaos, all)
- `PYTHON_VERSION` - Python version (default: 3.11)

## Coverage Measurement

### Code Coverage

Tool: `pytest-cov`

**Run coverage**:
```bash
python -m tests.extreme.run_coverage
```

**Targets**:
- ≥90% code coverage across all components
- 100% coverage of error handling paths
- All critical paths tested

**Reports**:
- HTML: `coverage_reports_demo/index.html`
- JSON: `coverage_reports_demo/coverage.json`
- Terminal: Summary with missing lines

### Requirement Coverage

**Validation**:
- 100% of 80 requirements covered by tests
- Each requirement mapped to specific tests
- Traceability from requirements → tests → results

**Report**: Generated in test report under "Requirement Coverage" section

## Performance Baselines

Location: `coverage_baselines/`

**Baseline Metrics**:
- 10-page document: ~2 minutes, ~500MB memory
- 50-page document: ~10 minutes, ~2GB memory
- 100-page document: ~30 minutes, ~4GB memory

**Regression Detection**:
- Alert when performance degrades >20% from baseline
- Track performance trends over time
- Identify performance cliffs (non-linear degradation)

## Breaking Points Catalog

Location: `tests/extreme/BREAKING_POINTS.md`

**Documented Breaking Points**:
- Maximum document size: 100 pages
- Maximum chunk count: 10,000 chunks
- Maximum concurrent operations: 5 analyses
- Maximum reference catalog: 1,000 subcategories
- Maximum word count: 500,000 words
- Maximum retrieval top-k: 10,000 results
- Maximum nesting depth: 100 levels
- Maximum section count: 10,000 sections

Each breaking point includes:
- Maximum viable value
- Failure mode
- Error message
- Metrics at failure
- Hardware requirements
- Mitigation strategies

## Failure Modes Catalog

Location: `tests/extreme/FAILURE_MODES.md`

**Documented Failure Modes**:
- FM-001: Memory exhaustion during large document processing
- FM-002: Disk full during output generation
- FM-003: Malicious PDF parsing crash
- FM-004: Concurrent vector store corruption
- FM-005: Prompt injection in Stage B reasoning
- FM-006: Empty document processing
- FM-007: Encoding corruption with non-ASCII text
- FM-008: Resource leak in long-running operations
- FM-009: Configuration validation bypass
- FM-010: LLM context window overflow

Each failure mode includes:
- Category (crash, data_corruption, incorrect_output, performance_degradation)
- Trigger conditions
- Impact on system
- Mitigation strategies
- Discovery date and test

## Requirements Validation

The testing framework validates **80 requirements** from the comprehensive testing specification:

- **Requirements 1-33**: Core testing scenarios (stress, chaos, adversarial, boundary)
- **Requirements 34-71**: Component-specific testing (retrieval, LLM, embedding, output)
- **Requirement 72**: Test orchestration and reporting
- **Requirement 73**: Failure mode documentation
- **Requirements 74-80**: Additional validation (baselines, coverage, CI/CD)

**Traceability**: Each test is tagged with requirement IDs for full traceability.

## Best Practices

### For Developers

1. **Run fast tests before commit**:
   ```bash
   python -m tests.extreme.cli test --fast --fail-fast
   ```

2. **Test specific changes**:
   ```bash
   python -m tests.extreme.cli test --category boundary --requirement 15.1
   ```

3. **Generate test data for manual testing**:
   ```bash
   python -m tests.extreme.cli generate-data --type policy --count 5
   ```

### For CI/CD

1. **Fast tests on every PR** (30 min)
2. **Full suite weekly** (4 hours)
3. **Manual triggers for specific categories**
4. **Artifact retention** for debugging

### For Performance Testing

1. **Establish baselines** on target hardware
2. **Compare against baselines** regularly
3. **Alert on >20% degradation**
4. **Track trends over time**

### For Security Testing

1. **Generate malicious test data**
2. **Run adversarial tests** regularly
3. **Update attack patterns** as new threats emerge
4. **Validate input sanitization**

## Troubleshooting

### Tests Timeout

**Solution**:
```bash
# Increase timeout
python -m tests.extreme.cli test --timeout 7200

# Or run specific categories
python -m tests.extreme.cli test --category property --category boundary
```

### Out of Memory

**Solution**:
```bash
# Reduce concurrency
python -m tests.extreme.cli test --concurrency 2

# Or run fast tests only
python -m tests.extreme.cli test --fast
```

### CI Pipeline Failures

**GitHub Actions**:
- Check workflow logs in Actions tab
- Download artifacts for detailed reports
- Review JUnit XML for specific failures

**GitLab CI**:
- Check pipeline logs in CI/CD → Pipelines
- Download artifacts from job page
- Review JUnit reports in Tests tab

## References

- [Extreme Testing README](../tests/extreme/README.md)
- [CLI and CI Integration Guide](../tests/extreme/CLI_AND_CI_INTEGRATION_GUIDE.md)
- [Data Generator README](../tests/extreme/DATA_GENERATOR_README.md)
- [Breaking Points Catalog](../tests/extreme/BREAKING_POINTS.md)
- [Failure Modes Catalog](../tests/extreme/FAILURE_MODES.md)
- [Requirements Document](../.kiro/specs/comprehensive-hardest-testing/requirements.md)
- [Design Document](../.kiro/specs/comprehensive-hardest-testing/design.md)

