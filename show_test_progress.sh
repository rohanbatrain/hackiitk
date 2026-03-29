#!/bin/bash
# Show comprehensive test progress

clear

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  Comprehensive Test Suite - Progress Dashboard              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Find test directory
TEST_DIR=$(ls -td comprehensive_test_* 2>/dev/null | head -1)

if [ -z "$TEST_DIR" ]; then
    echo "❌ No test directory found"
    exit 1
fi

# Count completed tests
COMPLETED=$(find "$TEST_DIR/outputs" -name "gap_analysis_report.json" 2>/dev/null | wc -l | tr -d ' ')
TOTAL=8

# Calculate progress
PERCENT=$((COMPLETED * 100 / TOTAL))

echo "📊 Overall Progress: $COMPLETED / $TOTAL tests ($PERCENT%)"
echo ""

# Progress bar
BAR_LENGTH=50
FILLED=$((COMPLETED * BAR_LENGTH / TOTAL))
EMPTY=$((BAR_LENGTH - FILLED))

printf "["
printf "%${FILLED}s" | tr ' ' '█'
printf "%${EMPTY}s" | tr ' ' '░'
printf "] $PERCENT%%\n"
echo ""

# Show test status
echo "═══ Test Status ═══"
echo ""

# Check each test
declare -a tests=(
    "minimal_isms:Minimal ISMS (200 words)"
    "partial_isms:Partial ISMS (1000 words)"
    "complete_isms:Complete ISMS (5000 words)"
    "risk_management:Risk Management (800 words)"
    "patch_management:Patch Management (600 words)"
    "data_privacy:Data Privacy (1000 words)"
    "empty_policy:Empty Policy (0 words)"
    "minimal_policy:Minimal Policy (50 words)"
)

for test_info in "${tests[@]}"; do
    IFS=':' read -r test_name test_desc <<< "$test_info"
    
    # Check if output exists
    if ls "$TEST_DIR/outputs"/*"$test_name"* 2>/dev/null | grep -q "gap_analysis_report.json"; then
        # Get gap count
        OUTPUT_DIR=$(ls -td "$TEST_DIR/outputs"/*"$test_name"* 2>/dev/null | head -1)
        GAPS=$(grep -o '"subcategory_id"' "$OUTPUT_DIR/gap_analysis_report.json" 2>/dev/null | wc -l | tr -d ' ')
        echo "✅ $test_desc - COMPLETED ($GAPS gaps)"
    else
        # Check if currently running
        if tail -5 comprehensive_test_execution.log 2>/dev/null | grep -q "$test_name"; then
            echo "🔄 $test_desc - RUNNING"
        else
            echo "⏳ $test_desc - PENDING"
        fi
    fi
done

echo ""
echo "═══ Latest Log Output ═══"
echo ""
tail -15 comprehensive_test_execution.log 2>/dev/null

echo ""
echo "═══ Commands ═══"
echo ""
echo "Monitor live: tail -f comprehensive_test_execution.log"
echo "Full progress: ./monitor_tests.sh"
echo "Refresh: ./show_test_progress.sh"
echo ""

# Show estimated time remaining
if [ "$COMPLETED" -gt 0 ]; then
    # Get start time from log
    START_TIME=$(head -5 comprehensive_test_execution.log | grep "Start Time" | cut -d: -f2- | xargs)
    
    # Calculate elapsed time (rough estimate)
    ELAPSED_MINS=$((COMPLETED * 9))  # ~9 min per test
    REMAINING_MINS=$(((TOTAL - COMPLETED) * 9))
    
    echo "⏱️  Estimated time remaining: ~$REMAINING_MINS minutes"
    echo "⏱️  Elapsed time: ~$ELAPSED_MINS minutes"
fi

echo ""
