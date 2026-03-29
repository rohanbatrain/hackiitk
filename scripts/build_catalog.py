#!/usr/bin/env python3
"""
Reference catalog builder script.

This script parses the CIS MS-ISAC NIST CSF 2.0 Policy Template Guide
and builds a structured JSON catalog for offline use.
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def build_catalog(cis_guide_path, output_path):
    """
    Build reference catalog from CIS guide.
    
    Args:
        cis_guide_path: Path to CIS guide PDF
        output_path: Path to save catalog JSON
    
    Returns:
        bool: True if successful, False otherwise
    """
    print(f"Building reference catalog from {cis_guide_path}...")
    
    # Check if CIS guide exists
    if not Path(cis_guide_path).exists():
        print(f"✗ CIS guide not found at {cis_guide_path}")
        print("Please download the CIS MS-ISAC NIST CSF 2.0 Policy Template Guide")
        print("and place it at data/cis_guide.pdf")
        return False
    
    try:
        # Import ReferenceCatalog
        from reference_builder.reference_catalog import ReferenceCatalog
        
        print("Parsing CIS guide...")
        catalog = ReferenceCatalog()
        catalog.build_from_cis_guide(cis_guide_path)
        
        print("Extracting CSF subcategories...")
        all_subs = catalog.get_all_subcategories()
        
        print("Building structured catalog...")
        catalog.persist(output_path)
        
        print(f"✓ Reference catalog saved to {output_path}")
        print(f"Total subcategories: {len(all_subs)}")
        
        # Show distribution by function
        from collections import Counter
        functions = Counter(sub.function for sub in all_subs)
        print("\nSubcategories by function:")
        for function, count in sorted(functions.items()):
            print(f"  {function}: {count}")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to build catalog: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Build reference catalog from CIS guide"
    )
    parser.add_argument(
        "--input",
        type=str,
        default="./data/cis_guide.pdf",
        help="Path to CIS guide PDF (default: ./data/cis_guide.pdf)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="./reference_catalog.json",
        help="Path to save catalog JSON (default: ./reference_catalog.json)"
    )
    
    args = parser.parse_args()
    
    success = build_catalog(args.input, args.output)
    
    if success:
        print("\n✓ Catalog build complete!")
        print("You can now analyze policies against NIST CSF 2.0.")
    else:
        print("\n✗ Catalog build failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
