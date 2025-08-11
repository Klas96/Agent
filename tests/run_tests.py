#!/usr/bin/env python3
"""
Test runner for PocketFlow tests.
"""

import subprocess
import sys
from pathlib import Path

def run_test(test_file):
    """Run a single test file."""
    print(f"\n{'='*60}")
    print(f"Running {test_file}...")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=True, text=True, cwd=Path(__file__).parent)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"Error running {test_file}: {e}")
        return False

def main():
    """Run all tests."""
    test_dir = Path(__file__).parent
    
    # List of test files to run
    test_files = [
        "test_postgresql.py",
        "test_migration.py", 
        "test_dashboard.py"
    ]
    
    print("🧪 PocketFlow Test Suite")
    print("=" * 60)
    
    results = {}
    all_passed = True
    
    for test_file in test_files:
        test_path = test_dir / test_file
        if test_path.exists():
            success = run_test(test_file)
            results[test_file] = success
            if not success:
                all_passed = False
        else:
            print(f"⚠️  Test file not found: {test_file}")
            results[test_file] = False
            all_passed = False
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 Test Results Summary")
    print(f"{'='*60}")
    
    for test_file, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_file}: {status}")
    
    print(f"\n{'='*60}")
    if all_passed:
        print("🎉 All tests passed!")
        exit(0)
    else:
        print("❌ Some tests failed!")
        exit(1)

if __name__ == "__main__":
    main() 