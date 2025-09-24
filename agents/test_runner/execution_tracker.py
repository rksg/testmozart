"""Execution Tracking Module

This module tracks test execution metrics and reliability statistics.
"""

import time
import logging
from typing import Dict, Any, List
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)

class ExecutionTracker:
    """Tracks test execution metrics and statistics."""
    
    def __init__(self):
        self.execution_history: List[Dict[str, Any]] = []
        self.current_session = None
        
    def start_execution(self, test_code: str, source_code: str) -> str:
        """Start tracking a test execution session."""
        session_id = f"exec_{int(time.time())}"
        
        self.current_session = {
            "session_id": session_id,
            "start_time": datetime.now().isoformat(),
            "test_code_length": len(test_code),
            "source_code_length": len(source_code),
            "status": "running"
        }
        
        logger.info(f"Started execution tracking for session {session_id}")
        return session_id
    
    def end_execution(self, session_id: str, test_results: Dict[str, Any], raw_output: Dict[str, Any]) -> Dict[str, Any]:
        """End tracking and calculate metrics."""
        if not self.current_session or self.current_session["session_id"] != session_id:
            logger.error(f"No active session found for {session_id}")
            return {"error": "No active session"}
        
        end_time = datetime.now()
        start_time = datetime.fromisoformat(self.current_session["start_time"])
        execution_time = (end_time - start_time).total_seconds()
        
        # Analyze test results
        status = test_results.get("status", "UNKNOWN")
        failures = test_results.get("failures", [])
        summary = test_results.get("summary", "")
        
        # Extract test counts from summary
        test_counts = self._parse_test_summary(summary)
        
        session_result = {
            **self.current_session,
            "end_time": end_time.isoformat(),
            "execution_time": execution_time,
            "status": "completed",
            "test_status": status,
            "test_counts": test_counts,
            "failure_count": len(failures),
            "raw_exit_code": raw_output.get("exit_code", -1),
            "has_stderr": bool(raw_output.get("stderr", "").strip()),
            "success": status == "PASS" and raw_output.get("exit_code", -1) == 0
        }
        
        self.execution_history.append(session_result)
        self.current_session = None
        
        logger.info(f"Completed execution tracking for session {session_id}. Status: {status}, Time: {execution_time:.2f}s")
        return session_result
    
    def _parse_test_summary(self, summary: str) -> Dict[str, int]:
        """Parse test summary to extract test counts."""
        counts = {"passed": 0, "failed": 0, "total": 0}
        
        if not summary:
            return counts
        
        # Look for patterns like "3 failed, 14 passed"
        import re
        
        failed_match = re.search(r'(\d+)\s+failed', summary)
        if failed_match:
            counts["failed"] = int(failed_match.group(1))
        
        passed_match = re.search(r'(\d+)\s+passed', summary)
        if passed_match:
            counts["passed"] = int(passed_match.group(1))
        
        counts["total"] = counts["passed"] + counts["failed"]
        
        logger.debug(f"Parsed test counts: {counts}")
        return counts
    
    def get_reliability_metrics(self) -> Dict[str, Any]:
        """Calculate reliability metrics from execution history."""
        if not self.execution_history:
            return {
                "total_executions": 0,
                "success_rate": 0.0,
                "average_execution_time": 0.0,
                "meets_threshold": False
            }
        
        total_executions = len(self.execution_history)
        successful_executions = sum(1 for exec in self.execution_history if exec.get("success", False))
        
        success_rate = successful_executions / total_executions
        avg_execution_time = sum(exec.get("execution_time", 0) for exec in self.execution_history) / total_executions
        
        # Analyze failure patterns
        failure_types = {}
        for exec in self.execution_history:
            if not exec.get("success", False):
                if exec.get("raw_exit_code") != 0:
                    failure_types["execution_error"] = failure_types.get("execution_error", 0) + 1
                elif exec.get("test_status") == "FAIL":
                    failure_types["test_failure"] = failure_types.get("test_failure", 0) + 1
                else:
                    failure_types["unknown"] = failure_types.get("unknown", 0) + 1
        
        recent_executions = self.execution_history[-10:]  # Last 10 executions
        recent_success_rate = sum(1 for exec in recent_executions if exec.get("success", False)) / len(recent_executions)
        
        metrics = {
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "success_rate": round(success_rate * 100, 2),
            "recent_success_rate": round(recent_success_rate * 100, 2),
            "average_execution_time": round(avg_execution_time, 2),
            "failure_types": failure_types,
            "meets_threshold": success_rate >= 0.95,  # 95% threshold
            "trend": "improving" if recent_success_rate > success_rate else "stable" if recent_success_rate == success_rate else "declining"
        }
        
        logger.info(f"Reliability metrics: {success_rate*100:.1f}% success rate over {total_executions} executions")
        return metrics

# Global tracker instance
execution_tracker = ExecutionTracker()
