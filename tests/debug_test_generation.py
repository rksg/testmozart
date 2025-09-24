#!/usr/bin/env python3
"""
Debug script to understand current test generation issues.
"""

import logging
import sys
import os

# Add parent directory to path to import agents
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.code_analyzer.tools import analyze_code_structure
from agents.test_case_designer.tools import generate_test_scenarios
from agents.test_implementer.tools import write_test_code

def debug_test_generation():
    """Debug the test generation pipeline step by step."""
    print("🔍 Debugging Test Generation Pipeline")
    print("=" * 50)
    
    # Step 1: Read sample code
    print("\n📄 Step 1: Reading sample code")
    with open("sample_code.py", "r") as f:
        sample_code = f.read()
    
    print(f"✅ Sample code loaded ({len(sample_code)} characters)")
    print("Sample code preview:")
    print(sample_code[:200] + "..." if len(sample_code) > 200 else sample_code)
    
    # Step 2: Analyze code structure
    print("\n🔍 Step 2: Analyzing code structure")
    try:
        analysis_result = analyze_code_structure(sample_code, "python")
        print(f"✅ Code analysis completed")
        
        if analysis_result.get("status") == "success":
            structure = analysis_result.get("structure", [])
            functions = [item for item in structure if item.get("type") == "function"]
            classes = [item for item in structure if item.get("type") == "class"]
            
            print(f"Functions found: {len(functions)}")
            print(f"Classes found: {len(classes)}")
            
            for func in functions:
                print(f"  - Function: {func['name']} (args: {len(func.get('parameters', []))})")
            
            for cls in classes:
                print(f"  - Class: {cls['name']} (methods: {len(cls.get('methods', []))})")
                for method in cls.get('methods', []):
                    print(f"    - Method: {method['name']} (args: {len(method.get('parameters', []))})")
        else:
            print(f"❌ Analysis failed: {analysis_result.get('message', 'Unknown error')}")
            return False
                
    except Exception as e:
        print(f"❌ Code analysis failed: {e}")
        return False
    
    # Step 3: Generate test scenarios (simulate LLM output)
    print("\n🧪 Step 3: Generating test scenarios")
    
    # Create a realistic test scenario string
    test_scenario_text = """
SCENARIO: Test the Calculator 'add' method with two positive integers (5, 3).
EXPECTED: The method should return 8.
---
SCENARIO: Test the Calculator 'subtract' method with positive numbers (10, 4).
EXPECTED: The method should return 6.
---
SCENARIO: Test the 'greet' function with a valid name 'Alice'.
EXPECTED: The function should return 'Hello, Alice!'.
---
SCENARIO: Test the 'factorial' function with input 5.
EXPECTED: The function should return 120.
---
SCENARIO: Test the StringProcessor 'reverse_string' method with 'hello'.
EXPECTED: The method should return 'olleh'.
"""
    
    try:
        test_scenarios = generate_test_scenarios(test_scenario_text)
        print(f"✅ Test scenarios generated: {len(test_scenarios)}")
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"  {i}. {scenario['description'][:50]}...")
            print(f"     Expected: {scenario['expected_outcome'][:50]}...")
            
    except Exception as e:
        print(f"❌ Test scenario generation failed: {e}")
        return False
    
    # Step 4: Generate test code
    print("\n🏗️ Step 4: Generating test code")
    
    try:
        # Test with first scenario
        first_scenario = test_scenarios[0]
        test_code = write_test_code(first_scenario, "pytest")
        
        print(f"✅ Test code generated for first scenario")
        print("Generated test code:")
        print("-" * 40)
        print(test_code)
        print("-" * 40)
        
    except Exception as e:
        print(f"❌ Test code generation failed: {e}")
        return False
    
    print(f"\n🎯 DIAGNOSIS:")
    print(f"✅ Code analysis works correctly")
    print(f"✅ Test scenario parsing works correctly")
    print(f"✅ Individual test code generation works")
    print(f"❓ Issue likely in the main workflow or LLM integration")
    
    return True

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.WARNING)
    
    success = debug_test_generation()
    
    if not success:
        print("\n❌ Debug failed - check the errors above")
        sys.exit(1)
    else:
        print("\n✅ Debug completed successfully")
        sys.exit(0)
