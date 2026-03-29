#!/bin/bash
# Simple test runner for gap detection validation
# Usage: ./tests/fixtures/run_tests.sh [--analyze]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

echo "=========================================="
echo "Gap Detection Validation Test Suite"
echo "=========================================="
echo ""

# Check if --analyze flag is provided
ANALYZE_FLAG=""
if [ "$1" == "--analyze" ]; then
    ANALYZE_FLAG="--analyze-and-validate"
    echo "Mode: Analyze and Validate"
else
    echo "Mode: Validate Existing Outputs"
    echo "(Use --analyze to run analysis first)"
fi

echo ""
echo "Test Policies:"
echo "  - ISMS Policy (8 planted gaps)"
echo "  - Data Privacy Policy (12 planted gaps)"
echo "  - Patch Management Policy (12 planted gaps)"
echo "  - Risk Management Policy (12 planted gaps)"
echo ""
echo "Required Detection Rate: 80%"
echo ""
echo "=========================================="
echo ""

# Run batch validation
python tests/fixtures/expected_outputs/validate_all.py \
    --output-dir outputs \
    --fixtures-dir tests/fixtures \
    $ANALYZE_FLAG

EXIT_CODE=$?

echo ""
echo "=========================================="
if [ $EXIT_CODE -eq 0 ]; then
    echo "✓ ALL TESTS PASSED"
    echo "The analyzer meets the 80% detection requirement."
else
    echo "✗ TESTS FAILED"
    echo "The analyzer does not meet requirements."
fi
echo "=========================================="

exit $EXIT_CODE
