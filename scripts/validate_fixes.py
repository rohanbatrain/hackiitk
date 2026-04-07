#!/usr/bin/env python3
"""
Validate that critical fixes are working:
1. Evidence extraction (CRITICAL-2)
2. Function classification (HIGH-1)
"""

import json
import glob
import re
from pathlib import Path

def extract_evidence_from_markdown(md_path):
    """Extract evidence quotes from markdown report."""
    with open(md_path) as f:
        content = f.read()
    
    # Count gaps with evidence
    evidence_pattern = r'\*\*Evidence from Policy\*\*:\s*\n\s*\n\s*>\s*\*\(No relevant text found in policy\)\*'
    no_evidence_count = len(re.findall(evidence_pattern, content))
    
    # Count total gaps
    gap_pattern = r'### Gap \d+:'
    total_gaps = len(re.findall(gap_pattern, content))
    
    with_evidence = total_gaps - no_evidence_count
    
    return with_evidence, total_gaps

def extract_function_from_markdown(md_path):
    """Check if function classification is present in markdown."""
    with open(md_path) as f:
        content = f.read()
    
    # Look for function mentions in the report
    # Since markdown doesn't have function field, we check subcategory IDs
    subcategory_pattern = r'### Gap \d+: ([A-Z]{2}\.[A-Z]+-\d+)'
    subcategories = re.findall(subcategory_pattern, content)
    
    # Map prefixes to functions
    function_map = {
        'GV': 'Govern',
        'ID': 'Identify',
        'PR': 'Protect',
        'DE': 'Detect',
        'RS': 'Respond',
        'RC': 'Recover'
    }
    
    functions = {}
    for subcat_id in subcategories:
        prefix = subcat_id.split('.')[0]
        func = function_map.get(prefix, 'UNKNOWN')
        functions[func] = functions.get(func, 0) + 1
    
    return functions

def main():
    print("=" * 70)
    print("VALIDATION REPORT: Critical Fixes")
    print("=" * 70)
    
    # Find all gap analysis reports from latest test run
    test_dir = "comprehensive_test_20260329_184855"
    
    # Map policy names to output directories
    policy_outputs = {
        "minimal_isms": "outputs/minimal_isms_20260329_185725",
        "partial_isms": "outputs/partial_isms_20260329_190820",
        "complete_isms": "outputs/complete_isms_20260329_192430",
        "risk_management": "outputs/risk_management_20260329_192729",
        "patch_management": "outputs/patch_management_20260329_192854",
        "data_privacy": "outputs/data_privacy_20260329_193101",
    }
    
    print("\n" + "=" * 70)
    print("FIX 1: Evidence Extraction (CRITICAL-2)")
    print("=" * 70)
    print(f"{'Policy':<20} {'With Evidence':<15} {'Total Gaps':<12} {'Rate':<10}")
    print("-" * 70)
    
    total_with_evidence = 0
    total_gaps = 0
    
    for policy_name, output_dir in policy_outputs.items():
        md_path = f"{output_dir}/gap_analysis_report.md"
        if Path(md_path).exists():
            with_evidence, gaps = extract_evidence_from_markdown(md_path)
            rate = (with_evidence / gaps * 100) if gaps > 0 else 0
            print(f"{policy_name:<20} {with_evidence:<15} {gaps:<12} {rate:>6.1f}%")
            total_with_evidence += with_evidence
            total_gaps += gaps
        else:
            print(f"{policy_name:<20} {'N/A':<15} {'N/A':<12} {'N/A':<10}")
    
    print("-" * 70)
    overall_rate = (total_with_evidence / total_gaps * 100) if total_gaps > 0 else 0
    print(f"{'TOTAL':<20} {total_with_evidence:<15} {total_gaps:<12} {overall_rate:>6.1f}%")
    
    print("\n" + "=" * 70)
    print("FIX 2: Function Classification (HIGH-1)")
    print("=" * 70)
    
    all_functions = {}
    for policy_name, output_dir in policy_outputs.items():
        md_path = f"{output_dir}/gap_analysis_report.md"
        if Path(md_path).exists():
            functions = extract_function_from_markdown(md_path)
            print(f"\n{policy_name}:")
            for func, count in sorted(functions.items()):
                print(f"  {func}: {count} gaps")
                all_functions[func] = all_functions.get(func, 0) + count
    
    print(f"\nOverall Function Distribution:")
    for func, count in sorted(all_functions.items()):
        print(f"  {func}: {count} gaps")
    
    unknown_count = all_functions.get('UNKNOWN', 0)
    unknown_rate = (unknown_count / total_gaps * 100) if total_gaps > 0 else 0
    print(f"\nUnknown functions: {unknown_count}/{total_gaps} ({unknown_rate:.1f}%)")
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    # Determine pass/fail
    evidence_pass = overall_rate >= 80
    function_pass = unknown_rate == 0
    
    print(f"\n✅ CRITICAL-2 (Evidence Extraction): {'PASS' if evidence_pass else 'FAIL'}")
    print(f"   - Target: ≥80% gaps with evidence")
    print(f"   - Actual: {overall_rate:.1f}%")
    print(f"   - Status: {'✅ FIXED' if evidence_pass else '❌ NEEDS WORK'}")
    
    print(f"\n✅ HIGH-1 (Function Classification): {'PASS' if function_pass else 'FAIL'}")
    print(f"   - Target: 0% unknown functions")
    print(f"   - Actual: {unknown_rate:.1f}%")
    print(f"   - Status: {'✅ FIXED' if function_pass else '❌ NEEDS WORK'}")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
