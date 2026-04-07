# Extreme Testing Framework - Team Handover Guide

**Project**: Offline Policy Gap Analyzer  
**Framework**: Extreme Testing Suite  
**Purpose**: Comprehensive stress, chaos, adversarial, boundary, performance, and property-based testing  
**Last Updated**: April 7, 2026

---

## 🎯 What Is This Tool?

The Extreme Testing Framework validates the Offline Policy Gap Analyzer under extreme conditions that go beyond normal unit/integration tests. It ensures the system remains robust under stress, chaos, adversarial attacks, boundary conditions, and performance degradation.

**Test Categories**:
- **Stress**: 1000+ files, 100MB+ outputs, concurrent operations
- **Chaos**: Random failures, resource exhaustion, timing attacks
- **Adversarial**: Malicious PDFs, injection attacks, fuzzing
- **Boundary**: Edge cases, limits, overflow conditions
- **Performance**: Degradation curves, bottleneck identification
- **Property**: 1000+ examples per property using Hypothesis

---

## 🚀 Quick Start

### Run All Tests
```bash
python -m tests.extreme.cli
```

### Run Specific Categories
```bash
# Stress tests only
python -m tests.extreme.cli --categories stress

# Multiple categories
python -m tests.extreme.cli --categories stress chaos adversarial

# All available: stress, chaos, adversarial, boundary, performance, property
```

### Run Specific Requirements
```bash
# Test specific requirement IDs
python -m tests.extreme.cli --requirements 1.1 1.2 2.1
```

### Common Options
```bash
# Verbose output
python -m tests.extreme.cli --verbose

# Stop on first failure
python -m tests.extreme.cli --fail-fast

# Custom output directory
python -m tests.extreme.cli --output-dir my_results

# Adjust concurrency (default: 4)
python -m tests.extreme.cli --concurrency 8

# Set timeout (default: 3600 seconds)
python -m tests.extreme.cli --timeout 1800
```

---

## 📊 Understanding Test Results

### Output Formats
The framework generates three report formats:

1. **HTML Report** (`test_outputs/extreme/report.html`)
   - Visual dashboard with charts and graphs
   - Detailed test results with stack traces
   - Performance metrics and trends

2. **JSON Report** (`test_outputs/extreme/report.json`)
   - Machine-readable format for CI/CD integration
   - Complete test metadata and results
   - Suitable for automated analysis

3. **JUnit XML** (`test_outputs/extreme/junit.xml`)
   - Standard format for CI/CD systems
   - Compatible with Jenkins, GitLab CI, GitHub Actions
   - Test suite aggregation

### Disable Reports
```bash
# Disable specific report types
python -m tests.extreme.cli --no-html --no-json --no-junit
```

---

## 🔍 Analyzing Test Failures

### Reading Test Output
```
FAILED tests/extreme/stress/test_large_files.py::test_1000_files
  AssertionError: Expected 1000 chunks, got 998
  
  Context:
    - Input: 1000 PDF files (10MB each)
    - Memory usage: 2.3GB peak
    - Duration: 45.2 seconds
    - Error: 2 files failed to parse due to corruption
```

### Key Metrics to Monitor
- **Pass Rate**: Should be > 95% for production readiness
- **Memory Usage**: Watch for memory leaks (increasing over time)
- **Duration**: Identify slow tests (> 60 seconds)
- **Error Patterns**: Recurring errors indicate systemic issues

### Common Failure Patterns

| Pattern | Cause | Solution |
|---------|-------|----------|
| Timeout | Test exceeds time limit | Increase `--timeout` or optimize code |
| Memory Error | Insufficient RAM | Reduce `--concurrency` or add memory |
| Random Failures | Race conditions | Fix concurrency bugs in code |
| Consistent Failures | Real bugs | Fix the underlying issue |

---

## 🏗️ Framework Architecture

### Directory Structure
```
tests/extreme/
├── cli.py              # Command-line interface (THIS FILE)
├── config.py           # Test configuration
├── runner.py           # Master test runner
├── reporter.py         # Report generation
├── oracles/            # Test oracles and accuracy tracking
│   └── accuracy_history.json
├── stress/             # Stress test implementations
├── chaos/              # Chaos engineering tests
├── adversarial/        # Security and attack tests
├── boundary/           # Edge case tests
├── performance/        # Performance profiling tests
└── property/           # Property-based tests (Hypothesis)
```

### Test Configuration
Located in `tests/extreme/config.py`:
- Default categories
- Timeout settings
- Concurrency limits
- Output paths
- Report formats

---

## 🔧 Integration with CI/CD

### GitHub Actions
```yaml
- name: Run Extreme Tests
  run: |
    python -m tests.extreme.cli \
      --categories stress chaos \
      --output-dir ${{ github.workspace }}/test-results \
      --no-html
      
- name: Upload Results
  uses: actions/upload-artifact@v3
  with:
    name: extreme-test-results
    path: test-results/
```

### GitLab CI
```yaml
extreme_tests:
  script:
    - python -m tests.extreme.cli --categories stress chaos
  artifacts:
    reports:
      junit: test_outputs/extreme/junit.xml
    paths:
      - test_outputs/extreme/
```

### Docker
```bash
# Run tests in Docker container
docker run -v $(pwd):/app ghcr.io/your-org/policy-analyzer:latest \
  python -m tests.extreme.cli --categories stress
```

---

## 📈 Performance Benchmarks

### Expected Execution Times
| Category | Tests | Duration | Concurrency |
|----------|-------|----------|-------------|
| Stress | ~50 | 10-15 min | 4 workers |
| Chaos | ~30 | 5-10 min | 4 workers |
| Adversarial | ~40 | 8-12 min | 4 workers |
| Boundary | ~25 | 3-5 min | 4 workers |
| Performance | ~20 | 15-20 min | 1 worker |
| Property | ~35 | 20-30 min | 4 workers |
| **Total** | **~200** | **60-90 min** | **4 workers** |

### Optimization Tips
- Increase `--concurrency` on powerful machines (8-16 cores)
- Use `--categories` to run only needed tests
- Use `--fail-fast` during development to catch issues early
- Run full suite nightly, subset during development

---

## 🐛 Troubleshooting

### Issue: Tests Timeout
```bash
# Increase timeout to 2 hours
python -m tests.extreme.cli --timeout 7200
```

### Issue: Out of Memory
```bash
# Reduce concurrency
python -m tests.extreme.cli --concurrency 2
```

### Issue: Dependency Errors
```bash
# Install all dependencies
pip install -r requirements.txt

# Verify installation
python -c "import hypothesis; print(hypothesis.__version__)"
```

### Issue: No Tests Found
```bash
# Verify you're in project root
pwd  # Should show project root

# Check test discovery
python -m pytest tests/extreme/ --collect-only
```

### Issue: Permission Denied (Output Directory)
```bash
# Use custom output directory
python -m tests.extreme.cli --output-dir ~/test-results
```

---

## 📚 Additional Resources

- **Test Suite Status**: `TEST_SUITE_STATUS.md`
- **Comprehensive Testing Spec**: `.kiro/specs/comprehensive-hardest-testing/`
- **Extreme Testing README**: `tests/extreme/README.md`
- **CLI Guide**: `docs/CLI_GUIDE.md`
- **Constraints**: `constraints.txt` (dependency versions)

---

## 🎓 Best Practices

### For Developers
1. **Run locally before pushing**: `python -m tests.extreme.cli --categories stress --fail-fast`
2. **Fix failures immediately**: Don't let them accumulate
3. **Monitor memory usage**: Use `--verbose` to see resource consumption
4. **Add new tests**: When fixing bugs, add extreme tests to prevent regression

### For CI/CD
1. **Run subset in PR checks**: `--categories stress chaos` (faster feedback)
2. **Run full suite nightly**: All categories for comprehensive coverage
3. **Archive reports**: Keep historical data for trend analysis
4. **Set failure thresholds**: Fail build if pass rate < 95%

### For QA/Testing Teams
1. **Review HTML reports**: Visual dashboard shows trends
2. **Track accuracy history**: `tests/extreme/oracles/accuracy_history.json`
3. **Identify flaky tests**: Tests that fail intermittently
4. **Validate fixes**: Re-run specific categories after bug fixes

---

## 🚨 Critical Notes

- **Do NOT run in production**: These tests are destructive and resource-intensive
- **Requires significant resources**: 8GB+ RAM, 4+ CPU cores recommended
- **May take 60-90 minutes**: Plan accordingly for CI/CD pipelines
- **Some failures are expected**: 97.7% pass rate is production-ready
- **Property tests use randomness**: Results may vary slightly between runs

---

## 📞 Support & Questions

- **Documentation**: Check `tests/extreme/README.md` first
- **Issues**: Review `TODO.md` for known issues
- **CI Status**: Check `.github/workflows/` for pipeline status
- **Dependencies**: See `constraints.txt` for version requirements

---

**Quick Reference Card**:
```bash
# Most common command
python -m tests.extreme.cli --categories stress chaos --verbose

# Development workflow
python -m tests.extreme.cli --categories stress --fail-fast

# CI/CD workflow
python -m tests.extreme.cli --no-html --output-dir ci-results

# Full validation
python -m tests.extreme.cli
```

---

**Status**: Production Ready | **Pass Rate**: 97.7% | **Total Tests**: 702 passing
