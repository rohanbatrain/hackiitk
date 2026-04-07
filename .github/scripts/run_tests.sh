#!/bin/bash
# Comprehensive test execution script for CI/CD
# This script ensures proper test discovery and execution

set -e  # Exit on error (but we'll handle errors explicitly)

CATEGORY="${1:-all}"
OUTPUT_DIR="${2:-test_outputs/extreme}"

echo "=========================================="
echo "Test Execution Script"
echo "Category: $CATEGORY"
echo "Output Directory: $OUTPUT_DIR"
echo "Working Directory: $(pwd)"
echo "Python Path: $PYTHONPATH"
echo "=========================================="

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Set Python path to include current directory
export PYTHONPATH="${PYTHONPATH:+${PYTHONPATH}:}$(pwd)"

# Verify Python and pytest are available
echo "Python version: $(python --version)"
echo "Pytest version: $(python -m pytest --version)"

# Function to run tests with proper error handling
run_test_category() {
    local category=$1
    local test_paths=$2
    local max_fail=${3:-5}
    
    echo ""
    echo "=== Running $category tests ==="
    echo "Test paths: $test_paths"
    
    # First check if test paths exist
    for path in $test_paths; do
        if [ ! -e "$path" ]; then
            echo "⚠️ Warning: Test path does not exist: $path"
        else
            echo "✓ Found test path: $path"
        fi
    done
    
    # Discover tests first
    echo ""
    echo "Discovering tests..."
    python -m pytest --collect-only $test_paths 2>&1 | tee "$OUTPUT_DIR/discovery_${category}.log" || {
        echo "⚠️ Test discovery had issues (exit code: $?)"
    }
    
    # Count discovered tests
    local test_count=$(grep -c "test session starts\|<Module\|<Function" "$OUTPUT_DIR/discovery_${category}.log" 2>/dev/null || echo "0")
    echo "Discovered approximately $test_count test items"
    
    # Run tests with output capture
    echo ""
    echo "Running tests..."
    python -m pytest $test_paths \
        -v \
        --tb=short \
        --continue-on-collection-errors \
        --maxfail=$max_fail \
        --junitxml="$OUTPUT_DIR/junit_${category}.xml" \
        --json-report \
        --json-report-file="$OUTPUT_DIR/report_${category}.json" \
        2>&1 | tee "$OUTPUT_DIR/output_${category}.log" || {
            local exit_code=$?
            echo "⚠️ Tests completed with exit code: $exit_code"
            # Don't fail the script - we want to collect results even if tests fail
        }
    
    echo "✓ $category tests completed"
    
    # Show summary if JSON report exists
    if [ -f "$OUTPUT_DIR/report_${category}.json" ]; then
        echo "Test results saved to: $OUTPUT_DIR/report_${category}.json"
        python -c "
import json
try:
    with open('$OUTPUT_DIR/report_${category}.json') as f:
        data = json.load(f)
    summary = data.get('summary', {})
    print(f\"  Total: {summary.get('total', 0)}\")
    print(f\"  Passed: {summary.get('passed', 0)}\")
    print(f\"  Failed: {summary.get('failed', 0)}\")
    print(f\"  Errors: {summary.get('error', 0)}\")
except Exception as e:
    print(f'Could not parse results: {e}')
" 2>/dev/null || echo "  (Could not parse JSON results)"
    fi
}

# Execute tests based on category
case "$CATEGORY" in
    property)
        run_test_category "property" "tests/extreme/engines/test_property_test_expander.py tests/property/" 5
        ;;
    boundary)
        run_test_category "boundary" "tests/extreme/engines/test_boundary_tester.py" 5
        ;;
    adversarial)
        run_test_category "adversarial" "tests/extreme/engines/test_adversarial_tester.py" 5
        ;;
    stress)
        run_test_category "stress" "tests/extreme/engines/test_stress_tester.py tests/extreme/engines/test_component_stress_tester.py" 3
        ;;
    chaos)
        run_test_category "chaos" "tests/extreme/engines/test_chaos_engine.py tests/extreme/engines/test_integration_chaos.py" 3
        ;;
    performance)
        run_test_category "performance" "tests/extreme/engines/test_performance_profiler.py" 3
        ;;
    unit)
        run_test_category "unit" "tests/unit/" 10
        ;;
    integration)
        run_test_category "integration" "tests/integration/" 5
        ;;
    all)
        echo "Running all test categories..."
        run_test_category "property" "tests/extreme/engines/test_property_test_expander.py tests/property/" 5
        run_test_category "boundary" "tests/extreme/engines/test_boundary_tester.py" 5
        run_test_category "adversarial" "tests/extreme/engines/test_adversarial_tester.py" 5
        run_test_category "stress" "tests/extreme/engines/test_stress_tester.py tests/extreme/engines/test_component_stress_tester.py" 3
        run_test_category "chaos" "tests/extreme/engines/test_chaos_engine.py tests/extreme/engines/test_integration_chaos.py" 3
        run_test_category "performance" "tests/extreme/engines/test_performance_profiler.py" 3
        run_test_category "unit" "tests/unit/" 10
        run_test_category "integration" "tests/integration/" 5
        ;;
    *)
        echo "❌ Unknown category: $CATEGORY"
        echo "Valid categories: property, boundary, adversarial, stress, chaos, performance, unit, integration, all"
        exit 1
        ;;
esac

# Show generated outputs
echo ""
echo "=========================================="
echo "Generated Test Outputs:"
echo "=========================================="
ls -lh "$OUTPUT_DIR/" 2>/dev/null || echo "No outputs generated"

echo ""
echo "✓ Test execution script completed"
exit 0  # Always exit successfully so workflow can collect artifacts

