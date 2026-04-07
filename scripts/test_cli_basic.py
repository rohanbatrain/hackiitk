#!/usr/bin/env python3
"""
Quick test to verify CLI structure is correct.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    
    try:
        import click
        print("✓ Click imported")
    except ImportError as e:
        print(f"✗ Click import failed: {e}")
        return False
    
    try:
        from rich.console import Console
        print("✓ Rich imported")
    except ImportError as e:
        print(f"✗ Rich import failed: {e}")
        return False
    
    try:
        from cli.main import cli, analyze, list_models, info, init_config
        print("✓ CLI commands imported")
    except ImportError as e:
        print(f"✗ CLI import failed: {e}")
        return False
    
    return True

def test_cli_structure():
    """Test CLI structure."""
    print("\nTesting CLI structure...")
    
    try:
        from cli.main import cli
        
        # Check if cli is a Click group
        if hasattr(cli, 'commands'):
            print(f"✓ CLI is a Click group with {len(cli.commands)} commands")
            for cmd_name in cli.commands:
                print(f"  - {cmd_name}")
        else:
            print("✗ CLI is not a proper Click group")
            return False
        
        return True
    except Exception as e:
        print(f"✗ CLI structure test failed: {e}")
        return False

def test_help():
    """Test help generation."""
    print("\nTesting help generation...")
    
    try:
        from click.testing import CliRunner
        from cli.main import cli
        
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        
        if result.exit_code == 0:
            print("✓ Help command works")
            print("\nHelp output preview:")
            print(result.output[:500])
            return True
        else:
            print(f"✗ Help command failed with exit code {result.exit_code}")
            return False
    except Exception as e:
        print(f"✗ Help test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("CLI Enhancement Verification")
    print("=" * 60)
    print()
    
    tests = [
        ("Imports", test_imports),
        ("CLI Structure", test_cli_structure),
        ("Help Generation", test_help),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name} crashed: {e}")
            results.append((test_name, False))
        print()
    
    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ All tests passed! CLI is ready.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
