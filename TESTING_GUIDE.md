# Testing Guide - Offline Policy Gap Analyzer

Quick reference for running tests locally and in CI/CD.

---

## Local Testing

### Prerequisites
```bash
# Install dependencies
pip install -r requirements.txt

# Or use UV (faster)
uv pip install -r requirements.txt
```

### Run Tests by Category

```bash
# Using the test script (recommended)
.github/scripts/run_tests.sh unit
.github/scripts/run_tests.sh integration
.github/scripts/run_tests.sh property
.github/scripts/run_tests.sh all

# Using pytest directly
python -m pytest tests/unit/ -v
python -m pytest tests/integration/ -v
python -m pytest tests/extreme/engines/ -v
```

### Test Discovery
```bash
# See what tests will run
python -m pytest --collect-only tests/unit/
python -m pytest --collect-only tests/

# Count tests
python -m pytest --collect-only tests/ -q | wc -l
```

### Run Specific Tests
```bash
# Single file
python -m pytest tests/unit/test_test_data_generator.py -v

# Single test function
python -m pytest tests/unit/test_test_data_generator.py::test_function_name -v

# With pattern matching
python -m pytest tests/ -k "test_embedding" -v
```

### Generate Reports
```bash
# JUnit XML (for CI/CD)
python -m pytest tests/unit/ --junitxml=test_results.xml

# JSON report
python -m pytest tests/unit/ --json-report --json-report-file=report.json

# HTML coverage
python -m pytest tests/unit/ --cov=. --cov-report=html
```

### Parallel Execution
```bash
# Run tests in parallel (requires pytest-xdist)
python -m pytest tests/unit/ -n auto

# Specify number of workers
python -m pytest tests/unit/ -n 4
```

---

## Docker Testing

### Build Image
```bash
# Build locally
docker build -t hackiitk:local .

# Build specific stage
docker build --target ci -t hackiitk:ci .
```

### Run Tests in Container
```bash
# Run default tests
docker run --rm hackiitk:local

# Run specific category
docker run --rm hackiitk:local python -m pytest tests/unit/ -v

# Interactive shell
docker run --rm -it hackiitk:local bash
```

### With Ollama
```bash
# Start Ollama separately
docker run -d --name ollama -p 11434:11434 ollama/ollama
docker exec ollama ollama pull qwen2.5:3b

# Run tests with Ollama
docker run --rm --network host \
  -e OLLAMA_HOST=http://localhost:11434 \
  hackiitk:local python -m pytest tests/ -v
```

---

## CI/CD Workflows

### Trigger Workflows

#### Smoke Tests (Fast)
```bash
# Automatic on push/PR
git push origin main

# Manual trigger
# Go to: Actions → Smoke Tests → Run workflow
```

#### Extreme Tests (Parallel)
```bash
# Automatic on push/PR
git push origin main

# Manual with specific category
# Go to: Actions → Extreme Testing Suite → Run workflow
# Select category: unit, integration, property, etc.
```

#### Full Test Suite (Long)
```bash
# Manual only (8 hours)
# Go to: Actions → Full Test Suite → Run workflow
# Specify models: qwen2.5:3b,phi3.5:3.8b
```

#### Diagnostics (Debug)
```bash
# Manual only
# Go to: Actions → Test Diagnostics → Run workflow
```

### View Results
```bash
# GitHub Actions page
https://github.com/rohanbatrain/hackiitk/actions

# Download artifacts
# Click on workflow run → Artifacts section
# Download: test-results-*, aggregated-test-results
```

---

## Test Categories

### Unit Tests (`tests/unit/`)
- Component-level tests
- Fast execution (<1 minute)
- No external dependencies
- **Files**: 20+ test modules

### Integration Tests (`tests/integration/`)
- System integration tests
- Moderate execution time
- May require external services
- **Files**: Multiple test modules

### Property Tests (`tests/property/`)
- Property-based testing with Hypothesis
- Generates random test cases
- Finds edge cases automatically
- **Files**: Property test modules

### Extreme Tests (`tests/extreme/engines/`)
- Stress testing
- Chaos engineering
- Adversarial testing
- Boundary testing
- Performance profiling
- **Files**: 30+ test modules

---

## Test Output Formats

### JUnit XML
```xml
<!-- test_results.xml -->
<testsuite name="pytest" tests="10" failures="0" errors="0">
  <testcase classname="tests.unit.test_example" name="test_function" time="0.001"/>
</testsuite>
```

### JSON Report
```json
{
  "total_tests": 10,
  "passed": 10,
  "failed": 0,
  "errors": 0,
  "duration_seconds": 5.2
}
```

### Console Output
```
tests/unit/test_example.py::test_function PASSED [10%]
tests/unit/test_example.py::test_another PASSED [20%]
...
========== 10 passed in 5.2s ==========
```

---

## Debugging Failed Tests

### Get Detailed Output
```bash
# Verbose mode
python -m pytest tests/unit/test_example.py -v

# Show print statements
python -m pytest tests/unit/test_example.py -s

# Full traceback
python -m pytest tests/unit/test_example.py --tb=long

# Stop on first failure
python -m pytest tests/unit/ -x
```

### Debug Specific Test
```bash
# Run with debugger
python -m pytest tests/unit/test_example.py --pdb

# Show local variables on failure
python -m pytest tests/unit/test_example.py -l

# Show captured output
python -m pytest tests/unit/test_example.py --capture=no
```

### Check Test Discovery Issues
```bash
# Verify pytest can find tests
python -m pytest --collect-only tests/

# Check for import errors
python -c "import tests.unit.test_example"

# Verify PYTHONPATH
python -c "import sys; print(sys.path)"
```

---

## Performance Tips

### Speed Up Tests
```bash
# Run in parallel
python -m pytest tests/ -n auto

# Run only failed tests from last run
python -m pytest --lf

# Run failed tests first, then others
python -m pytest --ff

# Skip slow tests
python -m pytest tests/ -m "not slow"
```

### Reduce Output
```bash
# Quiet mode
python -m pytest tests/ -q

# Only show failures
python -m pytest tests/ --tb=short

# No capture (faster but messy)
python -m pytest tests/ --capture=no
```

---

## Common Issues

### Issue: Tests Not Found
```bash
# Check naming convention
# Files must be: test_*.py or *_test.py
# Functions must be: test_*

# Verify directory structure
ls -la tests/unit/

# Check __init__.py files exist
find tests/ -name "__init__.py"
```

### Issue: Import Errors
```bash
# Set PYTHONPATH
export PYTHONPATH=$(pwd):$PYTHONPATH

# Or use pytest with path
python -m pytest tests/

# Check imports
python -c "import tests.unit.test_example"
```

### Issue: Dependency Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check installed packages
pip list | grep pytest

# Verify versions
python -c "import pytest; print(pytest.__version__)"
```

---

## Test Markers

### Mark Tests
```python
import pytest

@pytest.mark.slow
def test_slow_operation():
    pass

@pytest.mark.integration
def test_integration():
    pass
```

### Run by Marker
```bash
# Run only slow tests
python -m pytest -m slow

# Skip slow tests
python -m pytest -m "not slow"

# Multiple markers
python -m pytest -m "integration and not slow"
```

---

## Coverage Reports

### Generate Coverage
```bash
# Run with coverage
python -m pytest tests/ --cov=.

# HTML report
python -m pytest tests/ --cov=. --cov-report=html

# XML report (for CI/CD)
python -m pytest tests/ --cov=. --cov-report=xml

# Terminal report with missing lines
python -m pytest tests/ --cov=. --cov-report=term-missing
```

### View Coverage
```bash
# Open HTML report
open htmlcov/index.html

# Check coverage percentage
coverage report
```

---

## Quick Commands

```bash
# Run all tests
python -m pytest tests/ -v

# Run fast tests only
.github/scripts/run_tests.sh unit

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html

# Debug single test
python -m pytest tests/unit/test_example.py::test_function -v -s

# Parallel execution
python -m pytest tests/ -n auto

# Generate all reports
python -m pytest tests/ -v \
  --junitxml=junit.xml \
  --json-report --json-report-file=report.json \
  --cov=. --cov-report=html
```

---

## Resources

- **Pytest Documentation**: https://docs.pytest.org/
- **Hypothesis Documentation**: https://hypothesis.readthedocs.io/
- **GitHub Actions**: https://github.com/rohanbatrain/hackiitk/actions
- **Docker Hub**: https://hub.docker.com/

---

**Last Updated**: April 6, 2026
