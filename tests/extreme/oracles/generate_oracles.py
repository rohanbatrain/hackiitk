"""
Generate Oracle Test Cases

This script generates 20+ oracle test cases with various coverage patterns.
"""

import json
from pathlib import Path

# All 49 CSF subcategories
ALL_SUBCATEGORIES = [
    "ID.AM-1", "ID.AM-2", "ID.AM-3", "ID.AM-4", "ID.AM-5", "ID.AM-6",
    "ID.BE-1", "ID.BE-2", "ID.BE-3", "ID.BE-4", "ID.BE-5",
    "ID.GV-1", "ID.GV-2", "ID.GV-3", "ID.GV-4",
    "ID.RA-1", "ID.RA-2", "ID.RA-3", "ID.RA-4", "ID.RA-5", "ID.RA-6",
    "ID.RM-1", "ID.RM-2", "ID.RM-3",
    "ID.SC-1", "ID.SC-2", "ID.SC-3", "ID.SC-4", "ID.SC-5",
    "PR.AC-1", "PR.AC-2", "PR.AC-3", "PR.AC-4", "PR.AC-5", "PR.AC-6", "PR.AC-7",
    "PR.AT-1", "PR.AT-2", "PR.AT-3", "PR.AT-4", "PR.AT-5",
    "PR.DS-1", "PR.DS-2", "PR.DS-3", "PR.DS-4", "PR.DS-5", "PR.DS-6", "PR.DS-7", "PR.DS-8",
    "PR.IP-1", "PR.IP-2", "PR.IP-3"
]


def generate_oracle(test_id, description, policy_doc, covered_indices):
    """Generate an oracle test case."""
    covered = [ALL_SUBCATEGORIES[i] for i in covered_indices]
    gaps = [s for s in ALL_SUBCATEGORIES if s not in covered]
    
    return {
        "test_id": test_id,
        "description": description,
        "policy_document": policy_doc,
        "expected_gaps": gaps,
        "expected_covered": covered,
        "expected_gap_count": len(gaps),
        "tolerance": 0.05
    }


def main():
    """Generate oracle test cases."""
    oracles_dir = Path(__file__).parent
    
    # Oracle 005: Only Identify function covered
    oracle_005 = generate_oracle(
        "oracle_005",
        "Policy covering only Identify function (29 subcategories)",
        "tests/fixtures/dummy_policies/identify_only.md",
        list(range(0, 29))  # First 29 are ID.*
    )
    
    # Oracle 006: Only Protect function covered
    oracle_006 = generate_oracle(
        "oracle_006",
        "Policy covering only Protect function (20 subcategories)",
        "tests/fixtures/dummy_policies/protect_only.md",
        list(range(29, 49))  # Last 20 are PR.*
    )
    
    # Oracle 007: Asset Management only
    oracle_007 = generate_oracle(
        "oracle_007",
        "Policy covering only Asset Management (ID.AM)",
        "tests/fixtures/dummy_policies/asset_mgmt_only.md",
        list(range(0, 6))  # ID.AM-1 through ID.AM-6
    )
    
    # Oracle 008: Access Control only
    oracle_008 = generate_oracle(
        "oracle_008",
        "Policy covering only Access Control (PR.AC)",
        "tests/fixtures/dummy_policies/access_control_only.md",
        list(range(29, 36))  # PR.AC-1 through PR.AC-7
    )
    
    # Oracle 009: Data Security only
    oracle_009 = generate_oracle(
        "oracle_009",
        "Policy covering only Data Security (PR.DS)",
        "tests/fixtures/dummy_policies/data_security_only.md",
        list(range(41, 49))  # PR.DS-1 through PR.DS-8
    )
    
    # Oracle 010: Every other subcategory
    oracle_010 = generate_oracle(
        "oracle_010",
        "Policy covering every other subcategory (alternating pattern)",
        "tests/fixtures/dummy_policies/alternating.md",
        list(range(0, 49, 2))  # 0, 2, 4, 6, ...
    )
    
    # Oracle 011: First half covered
    oracle_011 = generate_oracle(
        "oracle_011",
        "Policy covering first 24 subcategories",
        "tests/fixtures/dummy_policies/first_half.md",
        list(range(0, 24))
    )
    
    # Oracle 012: Second half covered
    oracle_012 = generate_oracle(
        "oracle_012",
        "Policy covering last 25 subcategories",
        "tests/fixtures/dummy_policies/second_half.md",
        list(range(24, 49))
    )
    
    # Oracle 013: Minimal coverage (5 subcategories)
    oracle_013 = generate_oracle(
        "oracle_013",
        "Policy with minimal coverage (5 subcategories)",
        "tests/fixtures/dummy_policies/minimal.md",
        [0, 10, 20, 30, 40]
    )
    
    # Oracle 014: Near complete (45 subcategories)
    oracle_014 = generate_oracle(
        "oracle_014",
        "Policy with near complete coverage (45 subcategories)",
        "tests/fixtures/dummy_policies/near_complete.md",
        list(range(0, 45))
    )
    
    # Oracle 015: Risk Assessment focus
    oracle_015 = generate_oracle(
        "oracle_015",
        "Policy focused on Risk Assessment (ID.RA)",
        "tests/fixtures/dummy_policies/risk_assessment.md",
        list(range(14, 20))  # ID.RA-1 through ID.RA-6
    )
    
    # Oracle 016: Governance focus
    oracle_016 = generate_oracle(
        "oracle_016",
        "Policy focused on Governance (ID.GV)",
        "tests/fixtures/dummy_policies/governance.md",
        list(range(11, 15))  # ID.GV-1 through ID.GV-4
    )
    
    # Oracle 017: Training focus
    oracle_017 = generate_oracle(
        "oracle_017",
        "Policy focused on Awareness and Training (PR.AT)",
        "tests/fixtures/dummy_policies/training.md",
        list(range(36, 41))  # PR.AT-1 through PR.AT-5
    )
    
    # Oracle 018: Supply Chain focus
    oracle_018 = generate_oracle(
        "oracle_018",
        "Policy focused on Supply Chain (ID.SC)",
        "tests/fixtures/dummy_policies/supply_chain.md",
        list(range(23, 28))  # ID.SC-1 through ID.SC-5
    )
    
    # Oracle 019: Business Environment focus
    oracle_019 = generate_oracle(
        "oracle_019",
        "Policy focused on Business Environment (ID.BE)",
        "tests/fixtures/dummy_policies/business_env.md",
        list(range(6, 11))  # ID.BE-1 through ID.BE-5
    )
    
    # Oracle 020: Risk Management focus
    oracle_020 = generate_oracle(
        "oracle_020",
        "Policy focused on Risk Management (ID.RM)",
        "tests/fixtures/dummy_policies/risk_mgmt.md",
        list(range(20, 23))  # ID.RM-1 through ID.RM-3
    )
    
    # Oracle 021: Information Protection focus
    oracle_021 = generate_oracle(
        "oracle_021",
        "Policy focused on Information Protection (PR.IP)",
        "tests/fixtures/dummy_policies/info_protection.md",
        list(range(46, 49))  # PR.IP-1 through PR.IP-3
    )
    
    # Oracle 022: Sparse coverage (10 random subcategories)
    oracle_022 = generate_oracle(
        "oracle_022",
        "Policy with sparse coverage (10 subcategories)",
        "tests/fixtures/dummy_policies/sparse.md",
        [0, 5, 10, 15, 20, 25, 30, 35, 40, 45]
    )
    
    # Oracle 023: Dense coverage (40 subcategories)
    oracle_023 = generate_oracle(
        "oracle_023",
        "Policy with dense coverage (40 subcategories)",
        "tests/fixtures/dummy_policies/dense.md",
        list(range(0, 40))
    )
    
    # Oracle 024: Keywords only (no implementation)
    oracle_024 = generate_oracle(
        "oracle_024",
        "Policy with CSF keywords but no actual implementation",
        "tests/fixtures/dummy_policies/keywords_only.md",
        []  # Should detect as gaps despite keywords
    )
    
    # Save all oracles
    oracles = [
        oracle_005, oracle_006, oracle_007, oracle_008, oracle_009,
        oracle_010, oracle_011, oracle_012, oracle_013, oracle_014,
        oracle_015, oracle_016, oracle_017, oracle_018, oracle_019,
        oracle_020, oracle_021, oracle_022, oracle_023, oracle_024
    ]
    
    for oracle in oracles:
        filename = f"{oracle['test_id']}.json"
        filepath = oracles_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(oracle, f, indent=2)
        
        print(f"Generated {filename}")
    
    print(f"\nTotal oracles generated: {len(oracles)}")
    print(f"Total oracles (including existing): {len(oracles) + 4}")


if __name__ == "__main__":
    main()
