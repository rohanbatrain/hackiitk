#!/usr/bin/env python3
"""
Verify project setup is complete.
"""

import sys
from pathlib import Path


def verify_directories():
    """Verify all required directories exist."""
    required_dirs = [
        "ingestion",
        "reference_builder",
        "retrieval",
        "analysis",
        "revision",
        "reporting",
        "models",
        "tests",
        "docs",
        "data",
        "scripts",
        "outputs",
        "vector_store"
    ]
    
    print("Checking directories...")
    all_exist = True
    for dir_name in required_dirs:
        path = Path(dir_name)
        if path.exists() and path.is_dir():
            print(f"  ✓ {dir_name}/")
        else:
            print(f"  ✗ {dir_name}/ - MISSING")
            all_exist = False
    
    return all_exist


def verify_files():
    """Verify all required files exist."""
    required_files = [
        "config.yaml",
        "requirements.txt",
        "pyproject.toml",
        ".gitignore",
        "README.md",
        "docs/README.md"
    ]
    
    print("\nChecking configuration files...")
    all_exist = True
    for file_name in required_files:
        path = Path(file_name)
        if path.exists() and path.is_file():
            print(f"  ✓ {file_name}")
        else:
            print(f"  ✗ {file_name} - MISSING")
            all_exist = False
    
    return all_exist


def verify_module_structure():
    """Verify module __init__.py files exist."""
    modules = [
        "ingestion",
        "reference_builder",
        "retrieval",
        "analysis",
        "revision",
        "reporting",
        "models"
    ]
    
    print("\nChecking module structure...")
    all_exist = True
    for module_name in modules:
        init_file = Path(module_name) / "__init__.py"
        if init_file.exists():
            print(f"  ✓ {module_name}/__init__.py")
        else:
            print(f"  ✗ {module_name}/__init__.py - MISSING")
            all_exist = False
    
    return all_exist


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("Offline Policy Gap Analyzer - Setup Verification")
    print("=" * 60)
    
    dirs_ok = verify_directories()
    files_ok = verify_files()
    modules_ok = verify_module_structure()
    
    print("\n" + "=" * 60)
    if dirs_ok and files_ok and modules_ok:
        print("✓ Setup verification PASSED")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Install dependencies: pip install -e .")
        print("2. Download models: python scripts/download_models.py --all")
        print("3. Build catalog: python scripts/build_catalog.py")
        return 0
    else:
        print("✗ Setup verification FAILED")
        print("=" * 60)
        print("\nPlease fix the missing items above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
