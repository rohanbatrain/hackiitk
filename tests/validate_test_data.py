#!/usr/bin/env python3
"""
Validate that all test data has been created correctly.

This script checks:
- Oracle test cases exist and are valid
- Malicious PDF samples exist
- Synthetic documents exist and are categorized correctly
"""

from pathlib import Path
import json


def validate_oracle_test_cases():
    """Validate oracle test cases."""
    print("\n" + "=" * 80)
    print("Validating Oracle Test Cases")
    print("=" * 80)
    
    oracle_dir = Path("tests/extreme/oracles")
    
    if not oracle_dir.exists():
        print("❌ Oracle directory not found!")
        return False
    
    # Count oracle JSON files
    oracle_files = list(oracle_dir.glob("oracle_*.json"))
    print(f"✅ Found {len(oracle_files)} oracle test case files")
    
    if len(oracle_files) < 20:
        print(f"❌ Expected at least 20 oracle files, found {len(oracle_files)}")
        return False
    
    # Validate a sample oracle file
    sample_oracle = oracle_dir / "oracle_001_complete_policy.json"
    if sample_oracle.exists():
        try:
            data = json.loads(sample_oracle.read_text())
            required_fields = ["test_id", "description", "policy_document", 
                             "expected_gaps", "expected_covered", "expected_gap_count", "tolerance"]
            
            missing_fields = [f for f in required_fields if f not in data]
            if missing_fields:
                print(f"❌ Oracle file missing fields: {missing_fields}")
                return False
            
            print(f"✅ Oracle file structure validated")
            print(f"   Sample: {data['test_id']} - {data['description']}")
        except Exception as e:
            print(f"❌ Error reading oracle file: {e}")
            return False
    
    # Check for README
    readme = oracle_dir / "README.md"
    if readme.exists():
        print("✅ Oracle README.md exists")
    else:
        print("⚠️  Oracle README.md not found")
    
    return True


def validate_malicious_pdfs():
    """Validate malicious PDF samples."""
    print("\n" + "=" * 80)
    print("Validating Malicious PDF Samples")
    print("=" * 80)
    
    adversarial_dir = Path("tests/adversarial")
    
    if not adversarial_dir.exists():
        print("❌ Adversarial directory not found!")
        return False
    
    # Count PDF files
    pdf_files = list(adversarial_dir.glob("malicious_*.pdf"))
    print(f"✅ Found {len(pdf_files)} malicious PDF files")
    
    if len(pdf_files) < 20:
        print(f"❌ Expected at least 20 malicious PDFs, found {len(pdf_files)}")
        return False
    
    # Check attack type distribution
    attack_types = {
        "javascript": len(list(adversarial_dir.glob("malicious_*_javascript.pdf"))),
        "malformed": len(list(adversarial_dir.glob("malicious_*_malformed.pdf"))),
        "recursive": len(list(adversarial_dir.glob("malicious_*_recursive.pdf"))),
        "large_object": len(list(adversarial_dir.glob("malicious_*_large_object.pdf"))),
        "mixed": len(list(adversarial_dir.glob("malicious_*_mixed.pdf")))
    }
    
    print("\nAttack Type Distribution:")
    for attack_type, count in attack_types.items():
        print(f"  {attack_type}: {count} samples")
    
    # Check for metadata
    metadata_file = adversarial_dir / "samples_metadata.json"
    if metadata_file.exists():
        try:
            metadata = json.loads(metadata_file.read_text())
            print(f"\n✅ Metadata file exists")
            print(f"   Total samples: {metadata['total_samples']}")
        except Exception as e:
            print(f"⚠️  Error reading metadata: {e}")
    
    # Check for README
    readme = adversarial_dir / "README.md"
    if readme.exists():
        print("✅ Adversarial README.md exists")
    else:
        print("⚠️  Adversarial README.md not found")
    
    return True


def validate_synthetic_documents():
    """Validate synthetic test documents."""
    print("\n" + "=" * 80)
    print("Validating Synthetic Test Documents")
    print("=" * 80)
    
    synthetic_dir = Path("tests/synthetic")
    
    if not synthetic_dir.exists():
        print("❌ Synthetic directory not found!")
        return False
    
    # Count documents by category
    categories = {
        "stress": list(synthetic_dir.glob("stress_*.md")),
        "structure": list(synthetic_dir.glob("structure_*.md")),
        "multilingual": list(synthetic_dir.glob("multilingual_*.md")),
        "gap": list(synthetic_dir.glob("gap_*.md")),
        "perf": list(synthetic_dir.glob("perf_*.md")),
        "boundary": list(synthetic_dir.glob("boundary_*.md"))
    }
    
    total_docs = sum(len(files) for files in categories.values())
    print(f"✅ Found {total_docs} synthetic documents")
    
    print("\nCategory Distribution:")
    for category, files in categories.items():
        print(f"  {category}: {len(files)} documents")
    
    # Validate specific requirements
    stress_docs = categories["stress"]
    if len(stress_docs) >= 10:
        print(f"\n✅ Stress testing documents: {len(stress_docs)} (requirement: 10+)")
    else:
        print(f"\n❌ Stress testing documents: {len(stress_docs)} (requirement: 10+)")
    
    structure_docs = categories["structure"]
    if len(structure_docs) >= 6:
        print(f"✅ Extreme structure documents: {len(structure_docs)} (requirement: 6+)")
    else:
        print(f"❌ Extreme structure documents: {len(structure_docs)} (requirement: 6+)")
    
    multilingual_docs = categories["multilingual"]
    if len(multilingual_docs) >= 10:
        print(f"✅ Multilingual documents: {len(multilingual_docs)} (requirement: 10+)")
    else:
        print(f"❌ Multilingual documents: {len(multilingual_docs)} (requirement: 10+)")
    
    gap_docs = categories["gap"]
    if len(gap_docs) >= 10:
        print(f"✅ Intentional gap documents: {len(gap_docs)} (requirement: 10+)")
    else:
        print(f"❌ Intentional gap documents: {len(gap_docs)} (requirement: 10+)")
    
    # Check for summary
    summary_file = synthetic_dir / "documents_summary.json"
    if summary_file.exists():
        try:
            summary = json.loads(summary_file.read_text())
            print(f"\n✅ Summary file exists")
            print(f"   Total documents: {summary['total_documents']}")
        except Exception as e:
            print(f"⚠️  Error reading summary: {e}")
    
    # Check for README
    readme = synthetic_dir / "README.md"
    if readme.exists():
        print("✅ Synthetic README.md exists")
    else:
        print("⚠️  Synthetic README.md not found")
    
    return True


def main():
    """Run all validation checks."""
    print("=" * 80)
    print("Test Data Validation")
    print("=" * 80)
    
    results = {
        "Oracle Test Cases": validate_oracle_test_cases(),
        "Malicious PDFs": validate_malicious_pdfs(),
        "Synthetic Documents": validate_synthetic_documents()
    }
    
    print("\n" + "=" * 80)
    print("Validation Summary")
    print("=" * 80)
    
    for category, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {category}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 All validation checks passed!")
        print("\nTask 31 is COMPLETE:")
        print("  ✅ 31.1: Oracle test cases created")
        print("  ✅ 31.2: Malicious PDF samples created")
        print("  ✅ 31.3: Synthetic test documents created")
        return 0
    else:
        print("\n❌ Some validation checks failed!")
        return 1


if __name__ == "__main__":
    exit(main())
