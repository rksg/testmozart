"""Tools for coverage loop control.

This module contains tools for controlling the coverage optimization loop in Stage 1.
"""

import logging
from typing import Dict, Any
from google.adk.tools import ToolContext
from ..config import COVERAGE_MAX_ITERATIONS, COVERAGE_TARGET, MIN_COVERAGE_THRESHOLD

logger = logging.getLogger("two_stage_system")

def exit_loop(tool_context: ToolContext):
    """
    Exits the coverage optimization loop. Call this tool when coverage target is achieved
    or when the loop should be terminated for any reason.
    """
    # Setting escalate to True signals to a LoopAgent that it should stop iterating.
    tool_context.actions.escalate = True
    logger.info("Coverage loop exit signal sent - escalating to parent agent")
    return "Coverage optimization loop exit signal sent. Stage 1 complete, ready for Stage 2."

def should_continue_coverage_loop(
    coverage_validation: Dict[str, Any],
    iteration_count: int,
    max_iterations: int = COVERAGE_MAX_ITERATIONS
) -> Dict[str, Any]:
    """
    Determine if the coverage optimization loop should continue.
    
    Args:
        coverage_validation: Results from coverage validation
        iteration_count: Current iteration number (0-based)
        max_iterations: Maximum allowed iterations
        
    Returns:
        Dictionary with should_continue (bool) and reason (str)
    """
    logger.info(f"Evaluating coverage loop continuation (iteration {iteration_count}/{max_iterations})")
    
    # Check if coverage_validation is empty or invalid (timing issue)
    if not coverage_validation or not isinstance(coverage_validation, dict):
        logger.warning("Coverage validation data is empty or invalid - possible timing issue")
        reason = f"Coverage validation not yet available. Waiting for validation completion."
        logger.info(f"Deferring coverage loop decision: {reason}")
        return {
            "should_continue": True,
            "reason": reason,
            "current_coverage": 0,
            "gap": 100.0,
            "remaining_iterations": max_iterations - iteration_count,
            "deferred": True
        }
    
    # Extract coverage metrics - handle both formats
    # Format 1: From validate_scenario_coverage
    coverage_summary = coverage_validation.get("coverage_summary", {})
    overall_coverage_1 = coverage_summary.get("overall_coverage", 0)
    
    # Format 2: From calculate_coverage_metrics  
    overall_coverage_2 = coverage_validation.get("coverage_percentage", 0)
    
    # Use whichever is available (prefer the more detailed one)
    overall_coverage = max(overall_coverage_1, overall_coverage_2)
    meets_target = coverage_validation.get("meets_target", False)
    
    # Additional check: if both coverage readings are 0 but we have coverage_summary structure,
    # it might be a data format issue
    if overall_coverage == 0 and coverage_summary and "overall_coverage" in coverage_summary:
        logger.warning("Coverage data format issue detected - attempting alternative extraction")
        # Try direct key access
        overall_coverage = coverage_validation.get("coverage_summary", {}).get("overall_coverage", 0)
    
    logger.debug(f"Current coverage: {overall_coverage}%, Target: {COVERAGE_TARGET}%")
    
    # Check iteration limit first - prevent infinite loops
    if iteration_count >= max_iterations:
        reason = f"Maximum coverage iterations ({max_iterations}) reached"
        logger.info(f"Stopping coverage loop: {reason}")
        return {
            "should_continue": False, 
            "reason": reason,
            "final_coverage": overall_coverage,
            "exit_type": "max_iterations"
        }
    
    # Check if target coverage is achieved
    if meets_target and overall_coverage >= COVERAGE_TARGET:
        reason = f"Target coverage achieved: {overall_coverage}%"
        logger.info(f"Stopping coverage loop: {reason}")
        return {
            "should_continue": False,
            "reason": reason,
            "final_coverage": overall_coverage,
            "exit_type": "target_achieved"
        }
    
    # Check if coverage is good enough to proceed (fallback condition)
    if overall_coverage >= MIN_COVERAGE_THRESHOLD and iteration_count >= 2:
        reason = f"Acceptable coverage reached: {overall_coverage}% (≥{MIN_COVERAGE_THRESHOLD}%) after {iteration_count} iterations"
        logger.info(f"Stopping coverage loop: {reason}")
        return {
            "should_continue": False,
            "reason": reason,
            "final_coverage": overall_coverage,
            "exit_type": "acceptable_threshold"
        }
    
    # Check for no improvement (stagnation detection)
    if iteration_count > 0:
        # This would require tracking previous coverage, for now assume improvement is possible
        pass
    
    # Continue if coverage is insufficient and iterations remain
    remaining_iterations = max_iterations - iteration_count
    gap = COVERAGE_TARGET - overall_coverage
    
    reason = f"Coverage insufficient: {overall_coverage}% (target: {COVERAGE_TARGET}%). Gap: {gap:.1f}%. {remaining_iterations} iterations remaining."
    
    logger.info(f"Continuing coverage loop: {reason}")
    return {
        "should_continue": True,
        "reason": reason,
        "current_coverage": overall_coverage,
        "coverage_gap": gap,
        "remaining_iterations": remaining_iterations
    }


def exit_coverage_loop(
    final_coverage: float,
    exit_reason: str
) -> Dict[str, Any]:
    """
    Tool to exit the coverage optimization loop and prepare for Stage 2.
    
    Args:
        final_coverage: Final coverage percentage achieved
        exit_reason: Reason for exiting the loop
        
    Returns:
        Dictionary with exit confirmation and Stage 2 readiness
    """
    logger.info(f"Exiting coverage loop: {exit_reason}")
    logger.info(f"Final coverage achieved: {final_coverage}%")
    
    # Determine readiness for Stage 2
    ready_for_stage2 = final_coverage >= MIN_COVERAGE_THRESHOLD
    
    if ready_for_stage2:
        stage2_readiness = "READY"
        message = f"Stage 1 completed successfully with {final_coverage}% coverage. Ready to proceed to Stage 2."
    else:
        stage2_readiness = "LIMITED"
        message = f"Stage 1 completed with {final_coverage}% coverage (below optimal threshold). Proceeding to Stage 2 with current scenarios."
    
    result = {
        "should_continue": False,  # Critical: Signal to exit the loop
        "stage1_complete": True,
        "final_coverage_percentage": final_coverage,
        "exit_reason": exit_reason,
        "stage2_readiness": stage2_readiness,
        "ready_for_stage2": ready_for_stage2,
        "completion_message": message,
        "timestamp": "coverage_loop_exit"
    }
    
    logger.info(f"Coverage loop exit complete: {stage2_readiness} for Stage 2")
    return result


def analyze_coverage_improvement(
    previous_coverage: float,
    current_coverage: float,
    iteration_count: int
) -> Dict[str, Any]:
    """
    Analyze coverage improvement between iterations.
    
    Args:
        previous_coverage: Coverage percentage from previous iteration
        current_coverage: Coverage percentage from current iteration
        iteration_count: Current iteration number
        
    Returns:
        Dictionary with improvement analysis
    """
    logger.info(f"Analyzing coverage improvement for iteration {iteration_count}")
    
    improvement = current_coverage - previous_coverage
    improvement_rate = (improvement / previous_coverage * 100) if previous_coverage > 0 else 0
    
    if improvement > 5.0:
        status = "significant_improvement"
        recommendation = "Continue optimization - good progress"
    elif improvement > 1.0:
        status = "moderate_improvement"
        recommendation = "Continue optimization - steady progress"
    elif improvement > 0:
        status = "minor_improvement"
        recommendation = "Consider continuing - slow progress"
    elif improvement == 0:
        status = "no_improvement"
        recommendation = "Consider stopping - no progress detected"
    else:
        status = "regression"
        recommendation = "Investigation needed - coverage decreased"
    
    result = {
        "improvement_absolute": improvement,
        "improvement_percentage": improvement_rate,
        "status": status,
        "recommendation": recommendation,
        "previous_coverage": previous_coverage,
        "current_coverage": current_coverage,
        "iteration": iteration_count
    }
    
    logger.debug(f"Coverage improvement: {improvement:.2f}% absolute, {improvement_rate:.2f}% relative")
    
    return result
