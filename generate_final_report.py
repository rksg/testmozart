#!/usr/bin/env python3
"""
Generate a final human readable report based on the system's capabilities.
"""

import sys
import os
import json
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.report_generator.tools import generate_comprehensive_report_with_iterations, format_report_as_markdown

def create_sample_final_report():
    """Create a sample final report showing what the system should generate."""
    
    print("📊 生成最终人类可读报告")
    print("=" * 50)
    
    # Sample data that would come from a complete system run
    sample_coverage_report = {
        "coverage_analysis": {
            "summary": {
                "overall_coverage": 95.5,
                "function_coverage": 100.0,
                "method_coverage": 100.0,
                "class_coverage": 85.0
            }
        },
        "covered_units": {
            "functions": ["greet", "factorial", "find_max", "is_palindrome"],
            "classes": ["Calculator", "StringProcessor"],
            "methods": ["Calculator.add", "Calculator.subtract", "Calculator.multiply", 
                       "Calculator.divide", "Calculator.power", "StringProcessor.reverse_string",
                       "StringProcessor.count_words", "StringProcessor.capitalize_words"]
        },
        "uncovered_units": {
            "functions": [],
            "classes": [],
            "methods": {
                "Calculator": ["__init__"]
            }
        },
        "testable_units": {
            "total_functions": 4,
            "total_classes": 2,
            "total_methods": 9
        }
    }
    
    sample_test_results = {
        "status": "PASS",
        "summary": "42 passed in 0.12s",
        "failures": [],
        "execution_metrics": {
            "session_id": "exec_final_demo",
            "start_time": "2025-09-23T18:20:00.000000",
            "end_time": "2025-09-23T18:20:00.120000",
            "execution_time": 0.12,
            "test_counts": {
                "total": 42,
                "passed": 42,
                "failed": 0
            },
            "test_status": "PASS",
            "success": True
        },
        "reliability_metrics": {
            "success_rate": 100.0,
            "total_executions": 3,
            "successful_executions": 3,
            "average_execution_time": 0.11,
            "meets_threshold": True,
            "trend": "stable"
        }
    }
    
    # Sample iteration history showing the closed-loop improvement
    sample_iteration_history = [
        {
            "iteration": 1,
            "test_scenarios_count": 35,
            "coverage": 87.5,
            "success_rate": 95.0,
            "quality_score": 82.0,
            "improvements_made": ["Added edge case tests", "Fixed import issues"],
            "status": "IMPROVED"
        },
        {
            "iteration": 2,
            "test_scenarios_count": 40,
            "coverage": 92.0,
            "success_rate": 100.0,
            "quality_score": 88.5,
            "improvements_made": ["Added class instantiation tests", "Enhanced error handling tests"],
            "status": "IMPROVED"
        },
        {
            "iteration": 3,
            "test_scenarios_count": 42,
            "coverage": 95.5,
            "success_rate": 100.0,
            "quality_score": 94.0,
            "improvements_made": ["Added boundary condition tests"],
            "status": "FINAL"
        }
    ]
    
    # Read the actual source code
    try:
        with open("sample_code.py", "r") as f:
            source_code = f.read()
    except:
        source_code = "# Sample code not available"
    
    # Sample generated test code
    generated_test_code = '''import pytest
from sample_code import Calculator, StringProcessor, greet, factorial, find_max, is_palindrome

# Calculator class tests
def test_calculator_instantiation():
    calc = Calculator()
    assert calc is not None

def test_add_positive_integers():
    calc = Calculator()
    assert calc.add(5, 3) == 8

def test_add_negative_integers():
    calc = Calculator()
    assert calc.add(-5, -3) == -8

# ... 39 more comprehensive test cases ...

def test_is_palindrome_complex():
    assert is_palindrome("A man a plan a canal Panama") is True
'''
    
    print("✅ 生成综合报告...")
    
    # Generate the comprehensive report with iterations
    comprehensive_report = generate_comprehensive_report_with_iterations(
        coverage_report=sample_coverage_report,
        test_results=sample_test_results,
        source_code=source_code,
        generated_test_code=generated_test_code,
        iteration_history=sample_iteration_history
    )
    
    print("✅ 格式化为Markdown...")
    
    # Format as markdown
    markdown_report = format_report_as_markdown(comprehensive_report)
    
    # Save reports
    os.makedirs("output", exist_ok=True)
    
    # Save JSON report
    with open("output/final_comprehensive_report.json", "w") as f:
        json.dump(comprehensive_report, f, indent=2)
    
    # Save Markdown report
    with open("output/final_human_readable_report.md", "w") as f:
        f.write(markdown_report)
    
    print("✅ 报告已生成:")
    print(f"   📄 JSON报告: output/final_comprehensive_report.json")
    print(f"   📄 人类可读报告: output/final_human_readable_report.md")
    
    # Display key parts of the report
    print("\n" + "=" * 60)
    print("📋 最终人类可读报告预览:")
    print("=" * 60)
    print(markdown_report[:1000] + "..." if len(markdown_report) > 1000 else markdown_report)
    
    return "output/final_human_readable_report.md"

if __name__ == "__main__":
    report_path = create_sample_final_report()
    print(f"\n🎉 最终人类可读报告已生成: {report_path}")
