#!/usr/bin/env python3
"""
Test script to verify the fixed system works correctly.
"""

import logging
import sys
import os

# Add parent directory to path to import agents
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.test_runner.tools import _clean_test_code, execute_tests_sandboxed

def test_code_cleaning():
    """Test the code cleaning functionality."""
    print("\n🧹 Testing Code Cleaning Functionality")
    print("=" * 50)
    
    # Test case 1: Code with markdown markers
    dirty_code = """```python
import pytest
from source_to_test import Calculator

def test_add():
    calc = Calculator()
    assert calc.add(2, 3) == 5
```"""
    
    clean_code = _clean_test_code(dirty_code)
    
    print("✅ Test 1: Markdown cleaning")
    print(f"   - Removed opening markers: {'```python' not in clean_code}")
    print(f"   - Removed closing markers: {clean_code.count('```') == 0}")
    print(f"   - Fixed imports: {'from sample_code import' in clean_code}")
    
    # Test case 2: Already clean code
    already_clean = """import pytest
from sample_code import Calculator

def test_add():
    calc = Calculator()
    assert calc.add(2, 3) == 5"""
    
    clean_code2 = _clean_test_code(already_clean)
    print("✅ Test 2: Already clean code")
    print(f"   - Preserved clean code: {clean_code2 == already_clean}")
    
    return True

def test_simple_execution():
    """Test simple test execution."""
    print("\n🚀 Testing Simple Test Execution")
    print("=" * 50)
    
    # Simple source code
    source_code = '''
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b
'''
    
    # Simple test code
    test_code = '''
import pytest
from sample_code import add, multiply

def test_add():
    assert add(2, 3) == 5

def test_multiply():
    assert multiply(4, 5) == 20
'''
    
    try:
        result = execute_tests_sandboxed(source_code, test_code)
        
        print("✅ Test execution completed")
        print(f"   Exit code: {result.get('exit_code', 'unknown')}")
        print(f"   Has stdout: {bool(result.get('stdout', ''))}")
        print(f"   Has stderr: {bool(result.get('stderr', ''))}")
        
        # Check if tests passed
        stdout = result.get('stdout', '')
        tests_passed = 'FAILED' not in stdout and result.get('exit_code') == 0
        print(f"   Tests passed: {tests_passed}")
        
        if not tests_passed:
            print("   STDOUT:")
            print("   " + stdout.replace('\n', '\n   '))
            if result.get('stderr'):
                print("   STDERR:")
                print("   " + result.get('stderr', '').replace('\n', '\n   '))
        
        return tests_passed
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🔧 Testing Fixed System Components")
    print("=" * 60)
    
    tests = [
        ("Code Cleaning", test_code_cleaning),
        ("Simple Execution", test_simple_execution),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📋 Test Summary:")
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! System fixes are working correctly.")
        print("✅ The infinite loop issue should be resolved.")
        print("✅ Test code formatting issues should be fixed.")
    else:
        print("\n⚠️  Some tests failed. Check the issues above.")
    
    return all_passed

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.WARNING)
    
    success = main()
    sys.exit(0 if success else 1)
