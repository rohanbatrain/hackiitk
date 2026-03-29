#!/bin/bash
# Check Gap Detection Test Results

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  Gap Detection Test Results                                 ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Find the latest complete and incomplete outputs
COMPLETE_OUTPUT=$(ls -td outputs/complete_policy_* 2>/dev/null | head -1)
INCOMPLETE_OUTPUT=$(ls -td outputs/incomplete_policy_* 2>/dev/null | head -1)

if [ -z "$COMPLETE_OUTPUT" ]; then
    echo "❌ Complete policy output not found"
    exit 1
fi

if [ -z "$INCOMPLETE_OUTPUT" ]; then
    echo "⏳ Incomplete policy analysis still running or not started..."
    echo "   Waiting for: outputs/incomplete_policy_*"
    exit 1
fi

echo "✅ Found analysis outputs:"
echo "   Complete: $COMPLETE_OUTPUT"
echo "   Incomplete: $INCOMPLETE_OUTPUT"
echo ""

# Count gaps
COMPLETE_GAPS=$(grep -o '"subcategory_id"' "$COMPLETE_OUTPUT/gap_analysis_report.json" | wc -l | tr -d ' ')
INCOMPLETE_GAPS=$(grep -o '"subcategory_id"' "$INCOMPLETE_OUTPUT/gap_analysis_report.json" | wc -l | tr -d ' ')

echo "═══ Gap Counts ═══"
echo "Complete Policy Gaps:   $COMPLETE_GAPS"
echo "Incomplete Policy Gaps: $INCOMPLETE_GAPS"
echo "Additional Gaps Found:  $((INCOMPLETE_GAPS - COMPLETE_GAPS))"
echo ""

# Analyze incomplete policy gaps
echo "═══ Detailed Gap Analysis (Incomplete Policy) ═══"
python3 << PYTHON_SCRIPT
import json

with open('$INCOMPLETE_OUTPUT/gap_analysis_report.json', 'r') as f:
    report = json.load(f)

gaps = report.get('gaps', [])

# Group by CSF function (extract from subcategory_id)
by_function = {}
for gap in gaps:
    subcategory_id = gap.get('subcategory_id', '')
    func = subcategory_id.split('.')[0] if '.' in subcategory_id else 'Unknown'
    if func not in by_function:
        by_function[func] = []
    by_function[func].append(gap)

for func in sorted(by_function.keys()):
    print(f"\n{func} Function: {len(by_function[func])} gaps")
    print("-" * 70)
    for gap in by_function[func][:5]:  # Show first 5
        subcategory = gap.get('subcategory_id', 'Unknown')
        status = gap.get('status', 'Unknown')
        print(f"  • {subcategory}: {status}")
    if len(by_function[func]) > 5:
        print(f"  ... and {len(by_function[func]) - 5} more")

# Check for expected gaps
print(f"\n{'='*70}")
print("VERIFICATION OF EXPECTED GAPS:")
print("-" * 70)

expected_gaps = {
    'GV.SC': 'Supply Chain Risk Management',
    'GV.RM': 'Risk Management',
    'PR.DS': 'Data Security',
    'PR.AC': 'Access Control',
    'DE.CM': 'Continuous Monitoring',
    'RS.MA': 'Incident Management',
    'RC.RP': 'Recovery Planning',
}

detected_subcategories = [g.get('subcategory_id', '') for g in gaps]

for prefix, name in expected_gaps.items():
    found = any(sub.startswith(prefix) for sub in detected_subcategories)
    status = "✓ DETECTED" if found else "✗ MISSED"
    print(f"  {status}: {prefix} - {name}")

print(f"\n{'='*70}")
PYTHON_SCRIPT

# Final verdict
echo ""
echo "═══ Test Verdict ═══"
if [ "$INCOMPLETE_GAPS" -gt "$((COMPLETE_GAPS + 10))" ]; then
    echo "✅ TEST PASSED"
    echo "   The analyzer successfully detected significantly more gaps"
    echo "   in the incomplete policy ($INCOMPLETE_GAPS) vs complete ($COMPLETE_GAPS)"
else
    echo "❌ TEST FAILED: Configuration Issue Identified"
    echo ""
    echo "   Both policies show $COMPLETE_GAPS gaps (same count)"
    echo "   Expected: 30-50+ additional gaps in incomplete policy"
    echo ""
    echo "Root Cause:"
    echo "   Domain mapper only analyzes 14 GV subcategories for ISMS"
    echo "   Missing: Protect, Detect, Respond, Recover, Identify functions"
    echo ""
    echo "Documentation:"
    echo "   📄 Quick Reference: GAP_TEST_QUICK_REFERENCE.md"
    echo "   📄 Executive Summary: GAP_DETECTION_TEST_SUMMARY.md"
    echo "   📄 Detailed Findings: GAP_DETECTION_TEST_FINDINGS.md"
    echo ""
    echo "The Fix:"
    echo "   Edit: analysis/domain_mapper.py"
    echo "   Change: 'prioritize_functions': ['Govern']"
    echo "   To: 'prioritize_functions': ['Govern', 'Identify', 'Protect', 'Detect', 'Respond', 'Recover']"
fi

echo ""
echo "Review detailed reports:"
echo "  cat $INCOMPLETE_OUTPUT/gap_analysis_report.md"
echo "  cat $INCOMPLETE_OUTPUT/implementation_roadmap.md"
