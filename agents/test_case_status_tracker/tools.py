"""Tools for test case status tracking.

This module provides tools for tracking individual test case status across iterations
in Stage 2 of the two-stage architecture, enabling incremental improvements.
"""

import logging
from typing import Dict, List, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class TestCaseStatus(Enum):
    """Test case execution status."""
    PENDING = "pending"       # Not yet implemented or executed
    PASSED = "passed"         # Successfully executed
    FAILED = "failed"         # Failed execution
    SYNTAX_ERROR = "syntax_error"  # Syntax/import errors
    SKIPPED = "skipped"       # Skipped in current iteration

@dataclass
class TestCaseRecord:
    """Record for tracking individual test case status."""
    id: str
    scenario_description: str
    target_name: str
    status: TestCaseStatus
    last_error: str = ""
    iteration_passed: int = -1
    iteration_failed: int = -1
    test_code: str = ""
    execution_output: str = ""


def initialize_test_status_tracking(
    test_scenarios: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Initialize test case status tracking for Stage 2.
    
    Args:
        test_scenarios: Test scenarios from Stage 1 (coverage-validated)
        
    Returns:
        Dictionary with initialized test case tracking
    """
    logger.info(f"Initializing test case status tracking for {len(test_scenarios)} scenarios")
    
    test_records = {}
    
    for scenario in test_scenarios:
        test_id = scenario.get("id", f"test_{len(test_records) + 1:03d}")
        
        record = TestCaseRecord(
            id=test_id,
            scenario_description=scenario.get("description", ""),
            target_name=scenario.get("target_name", ""),
            status=TestCaseStatus.PENDING
        )
        
        test_records[test_id] = asdict(record)
    
    tracking_data = {
        "test_records": test_records,
        "total_tests": len(test_records),
        "status_summary": {
            "pending": len(test_records),
            "passed": 0,
            "failed": 0,
            "syntax_error": 0,
            "skipped": 0
        },
        "initialization_complete": True,
        "current_iteration": 0
    }
    
    logger.info(f"Test status tracking initialized for {len(test_records)} test cases")
    return tracking_data


def update_test_case_status(
    tracking_data: Dict[str, Any],
    test_results: Dict[str, Any],
    iteration_count: int
) -> Dict[str, Any]:
    """
    Update test case status based on execution results.
    
    Args:
        tracking_data: Current tracking data
        test_results: Results from test execution
        iteration_count: Current iteration number
        
    Returns:
        Updated tracking data
    """
    logger.info(f"Updating test case status for iteration {iteration_count}")
    
    test_records = tracking_data.get("test_records", {})
    
    # Parse test results to update individual test status
    execution_results = test_results.get("test_details", [])
    overall_status = test_results.get("status", "UNKNOWN")
    
    # Reset status summary
    status_summary = {
        "pending": 0,
        "passed": 0,
        "failed": 0,
        "syntax_error": 0,
        "skipped": 0
    }
    
    # Update based on execution results
    if execution_results:
        for result in execution_results:
            test_name = result.get("test_name", "")
            test_status = result.get("status", "UNKNOWN")
            error_message = result.get("error", "")
            
            # Find matching test record by name or description
            matching_record = None
            for test_id, record in test_records.items():
                if (test_name in record["scenario_description"] or 
                    test_name == record["target_name"] or
                    test_id == test_name):
                    matching_record = test_id
                    break
            
            if matching_record:
                record = test_records[matching_record]
                
                if test_status == "PASS":
                    record["status"] = TestCaseStatus.PASSED.value
                    record["iteration_passed"] = iteration_count
                    record["last_error"] = ""
                elif "SyntaxError" in error_message or "ImportError" in error_message:
                    record["status"] = TestCaseStatus.SYNTAX_ERROR.value
                    record["iteration_failed"] = iteration_count
                    record["last_error"] = error_message
                else:
                    record["status"] = TestCaseStatus.FAILED.value
                    record["iteration_failed"] = iteration_count
                    record["last_error"] = error_message
                
                record["execution_output"] = result.get("output", "")
    
    # If no detailed results, update based on overall status
    elif overall_status == "PASS":
        # Mark all as passed if overall success
        for record in test_records.values():
            if record["status"] == TestCaseStatus.PENDING.value:
                record["status"] = TestCaseStatus.PASSED.value
                record["iteration_passed"] = iteration_count
    
    elif overall_status in ["FAIL", "ERROR"]:
        # Mark all as failed if overall failure
        error_message = test_results.get("error_summary", "Execution failed")
        for record in test_records.values():
            if record["status"] == TestCaseStatus.PENDING.value:
                if "SyntaxError" in error_message or "ImportError" in error_message:
                    record["status"] = TestCaseStatus.SYNTAX_ERROR.value
                else:
                    record["status"] = TestCaseStatus.FAILED.value
                record["iteration_failed"] = iteration_count
                record["last_error"] = error_message
    
    # Update status summary
    for record in test_records.values():
        status_key = record["status"]
        if status_key in status_summary:
            status_summary[status_key] += 1
    
    # Update tracking data
    tracking_data["test_records"] = test_records
    tracking_data["status_summary"] = status_summary
    tracking_data["current_iteration"] = iteration_count
    tracking_data["last_update"] = f"iteration_{iteration_count}"
    
    logger.info(f"Status updated: {status_summary['passed']} passed, {status_summary['failed']} failed, {status_summary['syntax_error']} syntax errors")
    
    return tracking_data


def get_failed_test_cases(
    tracking_data: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Get list of test cases that need attention (failed or syntax errors).
    
    Args:
        tracking_data: Current tracking data
        
    Returns:
        List of test cases that need to be fixed
    """
    test_records = tracking_data.get("test_records", {})
    
    failed_tests = []
    for test_id, record in test_records.items():
        status = record["status"]
        if status in [TestCaseStatus.FAILED.value, TestCaseStatus.SYNTAX_ERROR.value]:
            failed_tests.append({
                "test_id": test_id,
                "description": record["scenario_description"],
                "target_name": record["target_name"],
                "status": status,
                "error": record["last_error"],
                "needs_regeneration": True
            })
    
    logger.info(f"Found {len(failed_tests)} test cases that need attention")
    return failed_tests


def get_passed_test_cases(
    tracking_data: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Get list of test cases that are already passing.
    
    Args:
        tracking_data: Current tracking data
        
    Returns:
        List of test cases that are passing and should be preserved
    """
    test_records = tracking_data.get("test_records", {})
    
    passed_tests = []
    for test_id, record in test_records.items():
        if record["status"] == TestCaseStatus.PASSED.value:
            passed_tests.append({
                "test_id": test_id,
                "description": record["scenario_description"],
                "target_name": record["target_name"],
                "test_code": record["test_code"],
                "iteration_passed": record["iteration_passed"],
                "preserve": True
            })
    
    logger.info(f"Found {len(passed_tests)} test cases that are passing")
    return passed_tests


def get_status_summary(
    tracking_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Get comprehensive status summary for decision making.
    
    Args:
        tracking_data: Current tracking data
        
    Returns:
        Dictionary with status summary and metrics
    """
    status_summary = tracking_data.get("status_summary", {})
    total_tests = tracking_data.get("total_tests", 0)
    current_iteration = tracking_data.get("current_iteration", 0)
    
    passed_count = status_summary.get("passed", 0)
    failed_count = status_summary.get("failed", 0)
    syntax_error_count = status_summary.get("syntax_error", 0)
    pending_count = status_summary.get("pending", 0)
    
    # Calculate success rate
    executed_tests = passed_count + failed_count + syntax_error_count
    success_rate = (passed_count / executed_tests * 100) if executed_tests > 0 else 0
    
    # Determine overall status
    if passed_count == total_tests:
        overall_status = "all_passed"
    elif failed_count == 0 and syntax_error_count == 0:
        overall_status = "partial_success"
    elif syntax_error_count > 0:
        overall_status = "syntax_issues"
    else:
        overall_status = "execution_issues"
    
    result = {
        "overall_status": overall_status,
        "success_rate": round(success_rate, 2),
        "total_tests": total_tests,
        "status_breakdown": status_summary,
        "tests_needing_attention": failed_count + syntax_error_count,
        "tests_ready": passed_count,
        "current_iteration": current_iteration,
        "all_tests_passing": passed_count == total_tests,
        "has_failures": (failed_count + syntax_error_count) > 0
    }
    
    logger.info(f"Status summary: {overall_status}, {success_rate:.1f}% success rate")
    
    return result
