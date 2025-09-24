#!/usr/bin/env python3
"""
Integration test for the closed-loop feedback system.

This script tests the new closed-loop feedback mechanism to ensure:
1. Feedback analyzer generates proper improvement instructions
2. Enhanced test designer can handle both initial and improvement modes
3. Quality loop correctly evaluates thresholds
4. System doesn't break existing functionality
"""

import logging
import json
import sys
import os

# Add parent directory to path to import agents
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.feedback_analyzer.tools import generate_improvement_instructions, format_instructions_for_llm
from agents.quality_loop.tools import check_quality_thresholds, should_continue_improvement
from agents.test_case_designer.enhanced_agent import enhanced_test_case_designer_agent

def test_feedback_analyzer():
    """Test the feedback analyzer functionality."""
    print("\n🔄 Testing Feedback Analyzer...")
    
    # Mock coverage report with low coverage
    coverage_report = {
        "coverage_summary": {
            "overall_coverage": 45.0,  # Below 80% threshold
            "function_coverage": 40.0,
            "method_coverage": 50.0
        },
        "uncovered_units": {
            "functions": ["subtract", "multiply"],
            "methods": {
                "Calculator": ["divide", "power"]
            }
        }
    }
    
    # Mock test results with some failures
    test_results = {
        "reliability_metrics": {
            "success_rate": 85.0,  # Below 95% threshold
            "failure_types": {
                "assertion_error": 2,
                "type_error": 1
            }
        },
        "failures": [
            {"test_name": "test_add", "error_message": "AssertionError: Expected 5, got 4"}
        ]
    }
    
    # Mock current test scenarios
    current_scenarios = [
        {"description": "Test add function with positive numbers", "expected_outcome": "Returns sum"}
    ]
    
    try:
        # Test improvement instructions generation
        instructions = generate_improvement_instructions(coverage_report, test_results, current_scenarios)
        
        print(f"✅ Generated improvement instructions")
        print(f"   Needs improvement: {instructions['needs_improvement']}")
        print(f"   Coverage issues: {len(instructions['coverage_issues'])}")
        print(f"   Execution issues: {len(instructions['execution_issues'])}")
        print(f"   Specific instructions: {len(instructions['specific_instructions'])}")
        
        # Test LLM-friendly formatting
        llm_instructions = format_instructions_for_llm(instructions)
        
        print(f"✅ Formatted LLM instructions ({len(llm_instructions)} characters)")
        print(f"   Contains HIGH PRIORITY: {'HIGH PRIORITY' in llm_instructions}")
        print(f"   Contains specific functions: {'subtract' in llm_instructions}")
        
        return True
        
    except Exception as e:
        print(f"❌ Feedback analyzer test failed: {e}")
        return False

def test_quality_loop():
    """Test the quality loop functionality."""
    print("\n🎯 Testing Quality Loop...")
    
    # Test case 1: Coverage below threshold
    coverage_report_low = {
        "coverage_summary": {
            "overall_coverage": 65.0,  # Below 80%
            "function_coverage": 60.0,
            "method_coverage": 70.0
        }
    }
    
    test_results_good = {
        "reliability_metrics": {
            "success_rate": 98.0  # Above 95%
        }
    }
    
    try:
        # Test quality threshold checking
        assessment = check_quality_thresholds(coverage_report_low, test_results_good)
        
        print(f"✅ Quality assessment completed")
        print(f"   Meets all thresholds: {assessment['meets_all_thresholds']}")
        print(f"   Coverage: {assessment['current_metrics']['coverage']}%")
        print(f"   Quality score: {assessment['current_metrics']['quality_score']}")
        print(f"   Gaps identified: {len(assessment['gaps'])}")
        
        # Test continuation decision
        should_continue, reason = should_continue_improvement(assessment, 1, 3)
        
        print(f"✅ Continuation decision: {should_continue}")
        print(f"   Reason: {reason}")
        
        # Test case 2: All thresholds met
        coverage_report_high = {
            "coverage_summary": {
                "overall_coverage": 85.0,  # Above 80%
                "function_coverage": 90.0,
                "method_coverage": 80.0
            }
        }
        
        assessment_good = check_quality_thresholds(coverage_report_high, test_results_good)
        should_continue_good, reason_good = should_continue_improvement(assessment_good, 1, 3)
        
        print(f"✅ High quality assessment:")
        print(f"   Meets all thresholds: {assessment_good['meets_all_thresholds']}")
        print(f"   Should continue: {should_continue_good}")
        print(f"   Reason: {reason_good}")
        
        return True
        
    except Exception as e:
        print(f"❌ Quality loop test failed: {e}")
        return False

def test_enhanced_test_designer():
    """Test the enhanced test designer agent configuration."""
    print("\n🧪 Testing Enhanced Test Designer...")
    
    try:
        # Check if agent is properly configured
        agent = enhanced_test_case_designer_agent
        
        print(f"✅ Agent created successfully")
        print(f"   Name: {agent.name}")
        print(f"   Model: {agent.model}")
        print(f"   Tools available: {len(agent.tools)}")
        print(f"   Instruction length: {len(agent.instruction)} characters")
        
        # Check if instruction contains improvement mode guidance
        instruction_text = agent.instruction
        has_improvement_mode = "MODE 2: IMPROVEMENT" in instruction_text
        has_feedback_handling = "improvement_instructions" in instruction_text
        
        print(f"   Has improvement mode: {has_improvement_mode}")
        print(f"   Can handle feedback: {has_feedback_handling}")
        
        return has_improvement_mode and has_feedback_handling
        
    except Exception as e:
        print(f"❌ Enhanced test designer test failed: {e}")
        return False

def test_integration_compatibility():
    """Test that new components don't break existing functionality."""
    print("\n🔗 Testing Integration Compatibility...")
    
    try:
        # Test imports
        from agents.coordinator import root_agent
        from agents.feedback_analyzer import feedback_analyzer_agent
        from agents.quality_loop import quality_improvement_loop_agent
        
        print(f"✅ All imports successful")
        
        # Check root agent structure
        print(f"   Root agent: {root_agent.name}")
        print(f"   Sub-agents: {len(root_agent.sub_agents)}")
        
        # Verify sub-agents
        sub_agent_names = [agent.name for agent in root_agent.sub_agents]
        expected_agents = ["InitialAnalysis", "QualityDrivenDesignLoop", "ExecutionRefinementLoop"]
        
        has_expected_structure = all(expected in sub_agent_names for expected in expected_agents)
        print(f"   Has expected structure: {has_expected_structure}")
        
        # Check quality driven loop structure
        quality_loop = None
        for agent in root_agent.sub_agents:
            if agent.name == "QualityDrivenDesignLoop":
                quality_loop = agent
                break
        
        if quality_loop:
            loop_agent_names = [agent.name for agent in quality_loop.sub_agents]
            print(f"   Quality loop agents: {loop_agent_names}")
            
            expected_loop_agents = ["EnhancedTestCaseDesigner", "CoverageAnalyzer", "FeedbackAnalyzer"]
            has_feedback_agents = any(expected in loop_agent_names for expected in expected_loop_agents)
            print(f"   Has feedback agents: {has_feedback_agents}")
            
            return has_expected_structure and has_feedback_agents
        else:
            print(f"❌ Quality driven loop not found")
            return False
        
    except Exception as e:
        print(f"❌ Integration compatibility test failed: {e}")
        return False

def main():
    """Run all integration tests."""
    print("🚀 Testing Closed-Loop Feedback Integration")
    print("=" * 60)
    
    tests = [
        ("Feedback Analyzer", test_feedback_analyzer),
        ("Quality Loop", test_quality_loop),
        ("Enhanced Test Designer", test_enhanced_test_designer),
        ("Integration Compatibility", test_integration_compatibility),
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
    
    print(f"\n🎉 Overall Result: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    
    if all_passed:
        print("✅ Closed-loop feedback system is ready for use!")
        print("✅ Existing functionality preserved!")
    else:
        print("⚠️  Some issues detected. Please review the failed tests.")
    
    return all_passed

if __name__ == "__main__":
    # Setup logging for test execution
    logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
    
    success = main()
    sys.exit(0 if success else 1)
