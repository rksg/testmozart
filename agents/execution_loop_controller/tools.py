"""Tools for execution loop control.

This module contains tools for controlling the execution quality loop in Stage 2.
"""

import logging
from typing import Dict, Any
from google.adk.tools import ToolContext
from ..config import EXECUTION_MAX_ITERATIONS, EXECUTION_SUCCESS_THRESHOLD

logger = logging.getLogger(__name__)

def exit_loop(tool_context: ToolContext):
    """
    Exits the execution quality loop. Call this tool when all tests are passing
    or when the loop should be terminated for any reason.
    """
    # Setting escalate to True signals to a LoopAgent that it should stop iterating.
    tool_context.actions.escalate = True
    logger.info("Execution loop exit signal sent - escalating to parent agent")
    return "Execution quality loop exit signal sent. Stage 2 complete, ready for final reporting."

def should_continue_execution_loop(
    test_status_summary: Dict[str, Any],
    iteration_count: int,
    max_iterations: int = EXECUTION_MAX_ITERATIONS
) -> Dict[str, Any]:
    """
    Determine if the execution quality loop should continue.
    
    Args:
        test_status_summary: Summary from test case status tracker
        iteration_count: Current iteration number (0-based)
        max_iterations: Maximum allowed iterations
        
    Returns:
        Dictionary with should_continue (bool) and reason (str)
    """
    logger.info(f"Evaluating execution loop continuation (iteration {iteration_count}/{max_iterations})")
    
    # Extract key metrics
    all_tests_passing = test_status_summary.get("all_tests_passing", False)
    success_rate = test_status_summary.get("success_rate", 0)
    tests_needing_attention = test_status_summary.get("tests_needing_attention", 0)
    total_tests = test_status_summary.get("total_tests", 0)
    
    logger.debug(f"Current metrics: {success_rate:.1f}% success rate, {tests_needing_attention} tests need attention")
    
    # Check iteration limit first - prevent infinite loops
    if iteration_count >= max_iterations:
        reason = f"Maximum execution iterations ({max_iterations}) reached"
        logger.info(f"Stopping execution loop: {reason}")
        return {
            "should_continue": False,
            "reason": reason,
            "final_success_rate": success_rate,
            "exit_type": "max_iterations",
            "tests_still_failing": tests_needing_attention
        }
    
    # Check if all tests are passing (ideal success)
    if all_tests_passing:
        reason = f"All {total_tests} tests are now passing"
        logger.info(f"Stopping execution loop: {reason}")
        return {
            "should_continue": False,
            "reason": reason,
            "final_success_rate": success_rate,
            "exit_type": "all_passed",
            "tests_still_failing": 0
        }
    
    # Check if success rate meets threshold (acceptable success)
    if success_rate >= EXECUTION_SUCCESS_THRESHOLD and iteration_count >= 2:
        reason = f"Success rate threshold met: {success_rate:.1f}% (≥{EXECUTION_SUCCESS_THRESHOLD}%) after {iteration_count} iterations"
        logger.info(f"Stopping execution loop: {reason}")
        return {
            "should_continue": False,
            "reason": reason,
            "final_success_rate": success_rate,
            "exit_type": "threshold_met",
            "tests_still_failing": tests_needing_attention
        }
    
    # Check for no improvement (stagnation detection)
    if iteration_count > 0 and tests_needing_attention > 0:
        # This would require tracking previous iteration results
        # For now, assume improvement is possible if iterations remain
        pass
    
    # Continue if there are failing tests and iterations remain
    remaining_iterations = max_iterations - iteration_count
    
    reason = f"Tests still failing: {tests_needing_attention}/{total_tests} ({success_rate:.1f}% success rate). {remaining_iterations} iterations remaining."
    
    logger.info(f"Continuing execution loop: {reason}")
    return {
        "should_continue": True,
        "reason": reason,
        "current_success_rate": success_rate,
        "failing_tests": tests_needing_attention,
        "remaining_iterations": remaining_iterations
    }


def exit_execution_loop(
    final_success_rate: float,
    exit_reason: str,
    tests_still_failing: int = 0,
    total_tests: int = 0
) -> Dict[str, Any]:
    """
    Tool to exit the execution quality loop and finalize Stage 2.
    
    Args:
        final_success_rate: Final success rate achieved
        exit_reason: Reason for exiting the loop
        tests_still_failing: Number of tests still failing
        total_tests: Total number of tests
        
    Returns:
        Dictionary with exit confirmation and system readiness
    """
    logger.info(f"Exiting execution loop: {exit_reason}")
    logger.info(f"Final success rate: {final_success_rate:.1f}%")
    
    # Determine system readiness based on final results
    if tests_still_failing == 0:
        system_status = "COMPLETE"
        message = f"Stage 2 completed successfully with 100% test pass rate. All {total_tests} tests are passing."
    elif final_success_rate >= EXECUTION_SUCCESS_THRESHOLD:
        system_status = "ACCEPTABLE"
        message = f"Stage 2 completed with {final_success_rate:.1f}% success rate. {total_tests - tests_still_failing}/{total_tests} tests passing."
    else:
        system_status = "PARTIAL"
        message = f"Stage 2 completed with {final_success_rate:.1f}% success rate. {tests_still_failing} tests still failing."
    
    # Determine what to return to user
    if tests_still_failing == 0:
        return_strategy = "complete_suite"
        return_message = "Returning complete test suite - all tests passing"
    else:
        return_strategy = "passing_tests_only"
        return_message = f"Returning {total_tests - tests_still_failing} passing tests only"
    
    result = {
        "stage2_complete": True,
        "system_complete": True,
        "final_success_rate": final_success_rate,
        "exit_reason": exit_reason,
        "system_status": system_status,
        "completion_message": message,
        "return_strategy": return_strategy,
        "return_message": return_message,
        "tests_summary": {
            "total": total_tests,
            "passing": total_tests - tests_still_failing,
            "failing": tests_still_failing
        },
        "ready_for_reporting": True,
        "timestamp": "execution_loop_exit"
    }
    
    logger.info(f"Execution loop exit complete: {system_status} status")
    return result


def analyze_execution_improvement(
    previous_success_rate: float,
    current_success_rate: float,
    iteration_count: int
) -> Dict[str, Any]:
    """
    Analyze execution quality improvement between iterations.
    
    Args:
        previous_success_rate: Success rate from previous iteration
        current_success_rate: Success rate from current iteration
        iteration_count: Current iteration number
        
    Returns:
        Dictionary with improvement analysis
    """
    logger.info(f"Analyzing execution improvement for iteration {iteration_count}")
    
    improvement = current_success_rate - previous_success_rate
    improvement_rate = (improvement / previous_success_rate * 100) if previous_success_rate > 0 else 0
    
    if improvement > 10.0:
        status = "significant_improvement"
        recommendation = "Continue optimization - excellent progress"
    elif improvement > 5.0:
        status = "good_improvement"
        recommendation = "Continue optimization - good progress"
    elif improvement > 0:
        status = "minor_improvement"
        recommendation = "Continue optimization - slow but steady progress"
    elif improvement == 0:
        status = "no_improvement"
        recommendation = "Consider stopping - no progress detected"
    else:
        status = "regression"
        recommendation = "Investigation needed - success rate decreased"
    
    result = {
        "improvement_absolute": improvement,
        "improvement_percentage": improvement_rate,
        "status": status,
        "recommendation": recommendation,
        "previous_success_rate": previous_success_rate,
        "current_success_rate": current_success_rate,
        "iteration": iteration_count
    }
    
    logger.debug(f"Execution improvement: {improvement:.2f}% absolute, {improvement_rate:.2f}% relative")
    
    return result


def prepare_final_test_suite(
    test_status_summary: Dict[str, Any],
    return_strategy: str = "passing_tests_only"
) -> Dict[str, Any]:
    """
    Prepare the final test suite based on return strategy.
    
    Args:
        test_status_summary: Current test status summary
        return_strategy: Strategy for what to return ("complete_suite" or "passing_tests_only")
        
    Returns:
        Dictionary with final test suite preparation instructions
    """
    logger.info(f"Preparing final test suite with strategy: {return_strategy}")
    
    total_tests = test_status_summary.get("total_tests", 0)
    passing_tests = test_status_summary.get("tests_ready", 0)
    failing_tests = test_status_summary.get("tests_needing_attention", 0)
    
    if return_strategy == "complete_suite":
        # Return all tests, including failing ones (for debugging)
        include_failing = True
        suite_description = f"Complete test suite with {total_tests} tests"
        quality_note = "Includes both passing and failing tests"
    else:
        # Return only passing tests (production ready)
        include_failing = False
        suite_description = f"Production-ready test suite with {passing_tests} passing tests"
        quality_note = f"Excludes {failing_tests} failing tests"
    
    result = {
        "return_strategy": return_strategy,
        "include_failing_tests": include_failing,
        "suite_description": suite_description,
        "quality_note": quality_note,
        "tests_to_include": {
            "passing": passing_tests,
            "failing": failing_tests if include_failing else 0,
            "total": passing_tests + (failing_tests if include_failing else 0)
        },
        "preparation_complete": True
    }
    
    logger.info(f"Final suite prepared: {result['tests_to_include']['total']} tests to include")
    
    return result
