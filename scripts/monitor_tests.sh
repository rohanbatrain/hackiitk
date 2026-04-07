#!/bin/bash
# Real-time test monitoring script

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  Comprehensive Test Suite - Live Monitor                    ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if tests are running
if ! ps aux | grep -q "[r]un_comprehensive_tests"; then
    echo "❌ Test suite is not running"
    echo ""
    echo "To start tests: ./run_comprehensive_tests.sh"
    exit 1
fi

echo "✅ Test suite is running"
echo ""

# Find test directory
TEST_DIR=$(ls -td comprehensive_test_* 2>/dev/null | head -1)

if [ -z "$TEST_DIR" ]; then
    echo "❌ Test directory not found"
    exit 1
fi

echo "📁 Test Directory: $TEST_DIR"
echo ""

# Function to count completed analyses
count_completed() {
    find "$TEST_DIR/outputs" -name "gap_analysis_report.json" 2>/dev/null | wc -l | tr -d ' '
}

# Function to get current test
get_current_test() {
    tail -5 comprehensive_test_execution.log | grep "Test " | tail -1
}

# Show progress
echo "═══ Test Progress ═══"
echo ""

COMPLETED=$(count_completed)
TOTAL=8

echo "Completed: $COMPLETED / $TOTAL tests"
echo ""

# Show current test
CURRENT=$(get_current_test)
if [ -n "$CURRENT" ]; then
    echo "Current: $CURRENT"
fi

echo ""
echo "═══ Live Log (Ctrl+C to exit) ═══"
echo ""

# Tail the log file
tail -f comprehensive_test_execution.log
