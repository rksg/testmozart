#!/usr/bin/env python3
"""
Test script for enhanced autonomous test suite generation system.

This script tests the new enhancements:
1. Coverage analysis
2. Execution tracking  
3. Report generation
4. Quality assessment
"""

import logging
import json
import sys
import os

# Add parent directory to path to import agents
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.coverage_analyzer.tools import calculate_coverage
from agents.test_runner.execution_tracker import execution_tracker
from agents.report_generator.tools import generate_comprehensive_report, format_report_as_markdown

def test_coverage_analysis():
    """Test coverage analysis functionality."""
    print("\n🧪 Testing Coverage Analysis...")
    
    sample_code = '''
class Calculator:
    """A simple calculator class."""
    
    def add(self, a: int, b: int) -> int:
        """Adds two numbers together."""
        return a + b
    
    def subtract(self, a: int, b: int) -> int:
        """Subtracts b from a."""
        return a - b

def greet(name: str) -> str:
    """Returns a greeting message."""
    return f"Hello, {name}"

def farewell(name: str) -> str:
    """Returns a farewell message."""
    return f"Goodbye, {name}"
'''
    
    # Test scenarios that cover some but not all functions
    test_scenarios = [
        {'description': 'Test the add method with two positive integers', 'expected_outcome': 'Should return correct sum'},
        {'description': 'Test the greet function with a name', 'expected_outcome': 'Should return greeting'},
        {'description': 'Test Calculator class functionality', 'expected_outcome': 'Should work correctly'}
    ]
    
    try:
        result = calculate_coverage(sample_code, test_scenarios)
        
        print(f"✅ Coverage Analysis Results:")
        print(f"   Overall Coverage: {result['coverage_summary']['overall_coverage']}%")
        print(f"   Function Coverage: {result['coverage_summary']['function_coverage']}%")
        print(f"   Method Coverage: {result['coverage_summary']['method_coverage']}%")
        print(f"   Meets 80% Threshold: {'✅ Yes' if result['meets_threshold'] else '❌ No'}")
        print(f"   Covered Functions: {result['covered_units']['functions']}")
        print(f"   Uncovered Functions: {result['uncovered_units']['functions']}")
        
        return result
        
    except Exception as e:
        print(f"❌ Coverage analysis failed: {e}")
        return None

def test_execution_tracking():
    """Test execution tracking functionality."""
    print("\n🔄 Testing Execution Tracking...")
    
    try:
        # Simulate test execution
        session_id = execution_tracker.start_execution("test code", "source code")
        print(f"✅ Started tracking session: {session_id}")
        
        # Simulate test results
        mock_test_results = {
            "status": "PASS",
            "summary": "5 passed in 0.3s",
            "failures": []
        }
        
        mock_raw_output = {
            "exit_code": 0,
            "stdout": "5 passed",
            "stderr": ""
        }
        
        session_result = execution_tracker.end_execution(session_id, mock_test_results, mock_raw_output)
        reliability_metrics = execution_tracker.get_reliability_metrics()
        
        print(f"✅ Execution Tracking Results:")
        print(f"   Execution Time: {session_result['execution_time']:.2f}s")
        print(f"   Success: {'✅ Yes' if session_result['success'] else '❌ No'}")
        print(f"   Success Rate: {reliability_metrics['success_rate']}%")
        print(f"   Total Executions: {reliability_metrics['total_executions']}")
        print(f"   Meets 95% Threshold: {'✅ Yes' if reliability_metrics['meets_threshold'] else '❌ No'}")
        
        return {"session_result": session_result, "reliability_metrics": reliability_metrics}
        
    except Exception as e:
        print(f"❌ Execution tracking failed: {e}")
        return None

def test_report_generation(coverage_result, execution_result):
    """Test comprehensive report generation."""
    print("\n📊 Testing Report Generation...")
    
    if not coverage_result or not execution_result:
        print("❌ Skipping report generation due to missing data")
        return None
    
    try:
        # Mock test results with execution metrics
        test_results = {
            "status": "PASS",
            "summary": "5 passed in 0.3s",
            "failures": [],
            "execution_metrics": execution_result["session_result"],
            "reliability_metrics": execution_result["reliability_metrics"]
        }
        
        # Generate comprehensive report
        report = generate_comprehensive_report(
            coverage_result,
            test_results,
            "sample source code",
            "sample test code"
        )
        
        print(f"✅ Report Generation Results:")
        print(f"   Overall Score: {report['executive_summary']['overall_score']}%")
        print(f"   System Health: {report['executive_summary']['system_health']}")
        print(f"   Coverage Score: {report['executive_summary']['coverage_score']}%")
        print(f"   Execution Success Rate: {report['executive_summary']['execution_success_rate']}%")
        print(f"   Meets Coverage Threshold: {'✅ Yes' if report['executive_summary']['meets_coverage_threshold'] else '❌ No'}")
        print(f"   Meets Execution Threshold: {'✅ Yes' if report['executive_summary']['meets_execution_threshold'] else '❌ No'}")
        print(f"   Number of Insights: {len(report['insights'])}")
        print(f"   Number of Recommendations: {len(report['recommendations'])}")
        
        # Test markdown formatting
        markdown = format_report_as_markdown(report)
        print(f"   Markdown Report Length: {len(markdown)} characters")
        
        # Save report to file
        with open("output/sample_comprehensive_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        with open("output/sample_report.md", "w") as f:
            f.write(markdown)
        
        print(f"   📄 Reports saved: output/sample_comprehensive_report.json, output/sample_report.md")
        
        return report
        
    except Exception as e:
        print(f"❌ Report generation failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Run all enhancement tests."""
    print("🚀 Testing Enhanced Autonomous Test Suite Generation System")
    print("=" * 60)
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Test each enhancement
    coverage_result = test_coverage_analysis()
    execution_result = test_execution_tracking()
    report_result = test_report_generation(coverage_result, execution_result)
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 Test Summary:")
    print(f"   Coverage Analysis: {'✅ PASS' if coverage_result else '❌ FAIL'}")
    print(f"   Execution Tracking: {'✅ PASS' if execution_result else '❌ FAIL'}")
    print(f"   Report Generation: {'✅ PASS' if report_result else '❌ FAIL'}")
    
    if all([coverage_result, execution_result, report_result]):
        print("\n🎉 All enhancements working correctly!")
        print("System is ready for integration testing.")
    else:
        print("\n⚠️ Some enhancements failed. Check logs for details.")
    
    return all([coverage_result, execution_result, report_result])

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
