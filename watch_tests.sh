#!/bin/bash
# Continuous test monitoring with auto-refresh

while true; do
    clear
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║  Comprehensive Test Suite - Live Monitor                    ║"
    echo "║  Press Ctrl+C to exit                                       ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    echo "🕐 $(date '+%H:%M:%S')"
    echo ""
    
    # Check if test is running
    if ps aux | grep -q "[r]un_comprehensive_tests"; then
        echo "✅ Test suite: RUNNING"
    else
        echo "⏹️  Test suite: STOPPED"
    fi
    echo ""
    
    # Count outputs from today
    TODAY=$(date +%Y%m%d)
    COMPLETED=$(ls outputs/*_${TODAY}_* 2>/dev/null | grep -c "minimal_isms\|partial_isms\|complete_isms\|risk_management\|patch_management\|data_privacy\|empty_policy\|minimal_policy" || echo "0")
    TOTAL=8
    PERCENT=$((COMPLETED * 100 / TOTAL))
    
    echo "📊 Progress: $COMPLETED / $TOTAL tests ($PERCENT%)"
    
    # Progress bar
    BAR_LENGTH=50
    FILLED=$((COMPLETED * BAR_LENGTH / TOTAL))
    EMPTY=$((BAR_LENGTH - FILLED))
    printf "["
    printf "%${FILLED}s" | tr ' ' '█'
    printf "%${EMPTY}s" | tr ' ' '░'
    printf "] $PERCENT%%\n"
    echo ""
    
    # Show completed tests
    echo "═══ Completed Tests ═══"
    ls -t outputs/*_${TODAY}_* 2>/dev/null | head -8 | while read dir; do
        if [ -f "$dir/gap_analysis_report.json" ]; then
            NAME=$(basename "$dir" | cut -d_ -f1-2)
            GAPS=$(grep -o '"subcategory_id"' "$dir/gap_analysis_report.json" 2>/dev/null | wc -l | tr -d ' ')
            TIME=$(stat -f "%Sm" -t "%H:%M" "$dir/gap_analysis_report.json" 2>/dev/null || echo "??:??")
            echo "✅ $NAME - $GAPS gaps ($TIME)"
        fi
    done
    echo ""
    
    # Show latest log
    echo "═══ Latest Activity ═══"
    tail -10 comprehensive_test_execution.log 2>/dev/null | sed 's/^/  /'
    echo ""
    
    echo "Refreshing in 5 seconds..."
    sleep 5
done
