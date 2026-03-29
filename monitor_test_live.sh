#!/bin/bash
# Real-Time Test Progress Monitor
# Shows live progress of comprehensive test suite execution

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Find the most recent test directory
TEST_DIR=$(find . -maxdepth 1 -name "comprehensive_test_*" -type d | sort -r | head -1)

if [ -z "$TEST_DIR" ]; then
    echo -e "${RED}No test directory found!${NC}"
    echo "Run ./run_comprehensive_tests.sh first"
    exit 1
fi

echo -e "${BOLD}${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${CYAN}║     Policy Analyzer - Live Test Progress Monitor            ║${NC}"
echo -e "${BOLD}${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Test Directory:${NC} $TEST_DIR"
echo -e "${BLUE}Monitor Started:${NC} $(date)"
echo ""

# Function to get test status
get_test_status() {
    local test_name="$1"
    local log_file="$TEST_DIR/logs/${test_name}_analysis.log"
    local time_file="$TEST_DIR/metrics/${test_name}_time.txt"
    
    if [ -f "$time_file" ]; then
        local duration=$(cat "$time_file")
        echo -e "${GREEN}✅ COMPLETE${NC} (${duration}s)"
    elif [ -f "$log_file" ]; then
        # Check if analysis is running
        local last_line=$(tail -1 "$log_file" 2>/dev/null)
        if echo "$last_line" | grep -q "Analysis pipeline complete"; then
            echo -e "${GREEN}✅ COMPLETE${NC}"
        elif echo "$last_line" | grep -q "ERROR"; then
            echo -e "${RED}❌ FAILED${NC}"
        else
            # Get progress percentage
            local progress=$(grep -o '\[.*%\]' "$log_file" 2>/dev/null | tail -1 | tr -d '[]%' || echo "0")
            if [ -n "$progress" ] && [ "$progress" != "0" ]; then
                echo -e "${YELLOW}🔄 RUNNING${NC} (${progress}%)"
            else
                echo -e "${YELLOW}🔄 STARTING${NC}"
            fi
        fi
    else
        echo -e "${CYAN}⏳ PENDING${NC}"
    fi
}

# Function to get gap count
get_gap_count() {
    local test_name="$1"
    local output_dir=$(find outputs -name "${test_name}_*" -type d 2>/dev/null | head -1)
    
    if [ -n "$output_dir" ] && [ -f "$output_dir/gap_analysis_report.json" ]; then
        local gaps=$(grep -o '"subcategory_id"' "$output_dir/gap_analysis_report.json" | wc -l | tr -d ' ')
        echo "$gaps"
    else
        echo "-"
    fi
}

# Function to get current step
get_current_step() {
    local test_name="$1"
    local log_file="$TEST_DIR/logs/${test_name}_analysis.log"
    
    if [ -f "$log_file" ]; then
        local step=$(grep "Step [0-9]/[0-9]" "$log_file" 2>/dev/null | tail -1 | sed 's/.*Step \([0-9]\/[0-9]\).*/\1/')
        if [ -n "$step" ]; then
            echo "$step"
        else
            echo "-"
        fi
    else
        echo "-"
    fi
}

# Function to get elapsed time
get_elapsed_time() {
    local test_name="$1"
    local log_file="$TEST_DIR/logs/${test_name}_analysis.log"
    
    if [ -f "$log_file" ]; then
        local start_time=$(head -1 "$log_file" | grep -o '\[.*\]' | head -1 | tr -d '[]')
        local end_time=$(tail -1 "$log_file" | grep -o '\[.*\]' | head -1 | tr -d '[]')
        
        if [ -n "$start_time" ]; then
            local start_epoch=$(date -j -f "%Y-%m-%d %H:%M:%S" "$start_time" "+%s" 2>/dev/null || echo "0")
            local current_epoch=$(date "+%s")
            local elapsed=$((current_epoch - start_epoch))
            
            if [ $elapsed -gt 0 ]; then
                local minutes=$((elapsed / 60))
                local seconds=$((elapsed % 60))
                echo "${minutes}m ${seconds}s"
            else
                echo "-"
            fi
        else
            echo "-"
        fi
    else
        echo "-"
    fi
}

# Main monitoring loop
while true; do
    clear
    
    echo -e "${BOLD}${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BOLD}${CYAN}║     Policy Analyzer - Live Test Progress Monitor            ║${NC}"
    echo -e "${BOLD}${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}Test Directory:${NC} $TEST_DIR"
    echo -e "${BLUE}Current Time:${NC} $(date '+%H:%M:%S')"
    echo ""
    
    echo -e "${BOLD}${MAGENTA}═══ Test Progress ═══${NC}"
    echo ""
    
    # Test 1: Minimal ISMS
    echo -e "${BOLD}Test 1.1: Minimal ISMS${NC}"
    echo -e "  Status: $(get_test_status 'minimal_isms')"
    echo -e "  Step: $(get_current_step 'minimal_isms')"
    echo -e "  Elapsed: $(get_elapsed_time 'minimal_isms')"
    echo -e "  Gaps: $(get_gap_count 'minimal_isms')"
    echo ""
    
    # Test 2: Partial ISMS
    echo -e "${BOLD}Test 1.2: Partial ISMS${NC}"
    echo -e "  Status: $(get_test_status 'partial_isms')"
    echo -e "  Step: $(get_current_step 'partial_isms')"
    echo -e "  Elapsed: $(get_elapsed_time 'partial_isms')"
    echo -e "  Gaps: $(get_gap_count 'partial_isms')"
    echo ""
    
    # Test 3: Complete ISMS
    echo -e "${BOLD}Test 1.3: Complete ISMS${NC}"
    echo -e "  Status: $(get_test_status 'complete_isms')"
    echo -e "  Step: $(get_current_step 'complete_isms')"
    echo -e "  Elapsed: $(get_elapsed_time 'complete_isms')"
    echo -e "  Gaps: $(get_gap_count 'complete_isms')"
    echo ""
    
    # Test 4: Risk Management
    echo -e "${BOLD}Test 1.4: Risk Management${NC}"
    echo -e "  Status: $(get_test_status 'risk_management')"
    echo -e "  Step: $(get_current_step 'risk_management')"
    echo -e "  Elapsed: $(get_elapsed_time 'risk_management')"
    echo -e "  Gaps: $(get_gap_count 'risk_management')"
    echo ""
    
    # Test 5: Patch Management
    echo -e "${BOLD}Test 1.5: Patch Management${NC}"
    echo -e "  Status: $(get_test_status 'patch_management')"
    echo -e "  Step: $(get_current_step 'patch_management')"
    echo -e "  Elapsed: $(get_elapsed_time 'patch_management')"
    echo -e "  Gaps: $(get_gap_count 'patch_management')"
    echo ""
    
    # Test 6: Data Privacy
    echo -e "${BOLD}Test 1.6: Data Privacy${NC}"
    echo -e "  Status: $(get_test_status 'data_privacy')"
    echo -e "  Step: $(get_current_step 'data_privacy')"
    echo -e "  Elapsed: $(get_elapsed_time 'data_privacy')"
    echo -e "  Gaps: $(get_gap_count 'data_privacy')"
    echo ""
    
    # Test 7: Empty Policy
    echo -e "${BOLD}Test 4.1: Empty Policy${NC}"
    echo -e "  Status: $(get_test_status 'empty_policy')"
    echo -e "  Step: $(get_current_step 'empty_policy')"
    echo -e "  Elapsed: $(get_elapsed_time 'empty_policy')"
    echo ""
    
    # Test 8: Minimal Policy
    echo -e "${BOLD}Test 4.2: Minimal Policy${NC}"
    echo -e "  Status: $(get_test_status 'minimal_policy')"
    echo -e "  Step: $(get_current_step 'minimal_policy')"
    echo -e "  Elapsed: $(get_elapsed_time 'minimal_policy')"
    echo ""
    
    echo -e "${BOLD}${MAGENTA}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${CYAN}Press Ctrl+C to exit${NC}"
    echo ""
    
    # Check if all tests are complete
    if [ -f "$TEST_DIR/reports/TEST_EXECUTION_LOG.md" ]; then
        if grep -q "Test Suite Complete" "$TEST_DIR/reports/TEST_EXECUTION_LOG.md" 2>/dev/null; then
            echo -e "${GREEN}${BOLD}✅ ALL TESTS COMPLETE!${NC}"
            echo ""
            break
        fi
    fi
    
    sleep 3
done
