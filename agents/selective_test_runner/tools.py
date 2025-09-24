"""Tools for selective test execution.

This module contains tools for executing only the tests that need validation,
while trusting already passing test results.
"""

import logging
import os
import tempfile
import subprocess
import json
import re
from typing import Dict, List, Any, Optional
import sys 
logger = logging.getLogger("two_stage_system")

def execute_selective_tests(
    complete_test_suite: str,
    source_code: str,
    tests_to_execute: Optional[List[str]] = None,
    skip_passed_tests: bool = True
) -> Dict[str, Any]:
    """
    Execute only the tests that need validation.
    
    Args:
        complete_test_suite: Complete test code including all tests
        source_code: Source code being tested
        tests_to_execute: Specific test names to execute (None = execute all new/failed)
        skip_passed_tests: Whether to skip tests that already passed
        
    Returns:
        Dictionary with selective execution results
    """
    logger.info("Starting selective test execution")
    
    # Create temporary directory for test execution
    with tempfile.TemporaryDirectory() as temp_dir:
        logger.debug(f"Using temporary directory: {temp_dir}")
        
        # Write source code to file
        source_file = os.path.join(temp_dir, "sample_code.py")
        with open(source_file, "w") as f:
            f.write(source_code)

        req_file = os.path.join(temp_dir, "requirements.txt")

        with open(req_file, "w") as f:
            f.write("pytest\n")
            f.write("sqlglot\n")
            f.write("langgraph\n")
            f.write("pydantic\n")
            f.write("langchain\n")
        # --- 2. Create a virtual environment ---
        print("Creating virtual environment...", 2, 5)
        venv_path = os.path.join(temp_dir, "venv")
        try:
            # Use the currently running Python executable to create the venv
            subprocess.run(
                [sys.executable, "-m", "venv", venv_path], 
                check=True, 
                capture_output=True,
                text=True
            )
        except subprocess.CalledProcessError as e:
            return {
                "exit_code": e.returncode,
                "stdout": e.stdout,
                "stderr": f"Failed to create virtual environment:\n{e.stderr}"
            }            
        # --- 3. Determine platform-specific executable paths ---
        if os.name == 'nt':  # Windows
            bin_dir = "Scripts"
        else:  # macOS, Linux, etc.
            bin_dir = "bin"
            
        pip_exe = os.path.join(venv_path, bin_dir, "pip")
        pytest_exe = os.path.join(venv_path, bin_dir, "pytest")
        
        # --- 2. Create a virtual environment ---
        print("Creating virtual environment...", 2, 5)
        venv_path = os.path.join(temp_dir, "venv")
        try:
            # Use the currently running Python executable to create the venv
            subprocess.run(
                [sys.executable, "-m", "venv", venv_path], 
                check=True, 
                capture_output=True,
                text=True
            )
            
        except subprocess.CalledProcessError as e:
            return {
                "exit_code": e.returncode,
                "stdout": e.stdout,
                "stderr": f"Failed to create virtual environment:\n{e.stderr}"
            }
        # --- 4. Install requirements into the venv ---
        print("Installing test dependencies (pytest)...", 3, 5)
        try:
            subprocess.run(
                [pip_exe, "install", "-r", req_file],
                check=True,
                capture_output=True,
                text=True,
                cwd=temp_dir
            )
        except subprocess.CalledProcessError as e:
            return {
                "exit_code": e.returncode,
                "stdout": e.stdout,
                "stderr": f"Failed to install pytest:\n{e.stderr}"
            }   
        # Install required packages
        # Write test code to file
        test_file = os.path.join(temp_dir, "test_selective.py")
        with open(test_file, "w") as f:
            f.write(complete_test_suite)
        
        # Prepare pytest command
        pytest_cmd = [
            "python", "-m", "pytest", 
            test_file,
            "-v",
            "--tb=short"
        ]
        
        # Add specific test selection if provided
        if tests_to_execute:
            # Convert test names to pytest selection format
            test_selections = []
            for test_name in tests_to_execute:
                test_selections.append(f"{test_file}::{test_name}")
            pytest_cmd.extend(["-k", " or ".join(tests_to_execute)])
        
        logger.info(f"🔧 Preparing to execute selective tests...")
        
        # Execute tests
        try:
            # Show progress
            test_count = len(tests_to_execute) if tests_to_execute else _count_test_functions(complete_test_suite)
            logger.info(f"[1/3] Executing {test_count} test cases...")
            
            result = subprocess.run(
                pytest_cmd,
                cwd=temp_dir,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            logger.info("[2/3] Test execution completed, parsing results...")
            
            # Parse results from pytest stdout
            json_results = _parse_pytest_output(result.stdout, result.returncode)
            
            logger.info("[3/3] ✅ Selective test execution completed")
            
            return {
                "execution_successful": True,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "json_results": json_results,
                "tests_executed": test_count,
                "selective_execution": True,
                "execution_type": "selective"
            }
            
        except subprocess.TimeoutExpired:
            logger.error("Test execution timed out")
            return {
                "execution_successful": False,
                "error": "Test execution timed out after 300 seconds",
                "return_code": -1,
                "execution_type": "selective"
            }
        except Exception as e:
            logger.error(f"Test execution failed: {e}")
            return {
                "execution_successful": False,
                "error": str(e),
                "return_code": -1,
                "execution_type": "selective"
            }


def parse_selective_results(
    execution_results: Dict[str, Any],
    preserved_test_results: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Parse selective test execution results and combine with preserved results.
    
    Args:
        execution_results: Results from execute_selective_tests
        preserved_test_results: Results from tests that were skipped (already passing)
        
    Returns:
        Dictionary with comprehensive test results
    """
    logger.info("Parsing selective test execution results")
    
    if not execution_results.get("execution_successful", False):
        return {
            "status": "ERROR",
            "error_summary": execution_results.get("error", "Execution failed"),
            "test_details": [],
            "execution_type": "selective"
        }
    
    # Parse JSON results if available
    json_results = execution_results.get("json_results")
    test_details = []
    
    if json_results:
        # Parse pytest JSON report
        tests = json_results.get("tests", [])
        
        for test in tests:
            test_name = test.get("nodeid", "").split("::")[-1]
            outcome = test.get("outcome", "unknown")
            
            test_detail = {
                "test_name": test_name,
                "status": "PASS" if outcome == "passed" else "FAIL",
                "outcome": outcome,
                "duration": test.get("duration", 0)
            }
            
            # Add error information if test failed
            if outcome != "passed":
                call_info = test.get("call", {})
                test_detail["error"] = call_info.get("longrepr", "Unknown error")
                test_detail["error_type"] = "execution_failure"
            
            test_details.append(test_detail)
    
    else:
        # Parse stdout/stderr if JSON not available
        stdout = execution_results.get("stdout", "")
        stderr = execution_results.get("stderr", "")
        
        # Simple parsing of pytest output
        if "PASSED" in stdout or "FAILED" in stdout:
            test_details = _parse_pytest_stdout(stdout)
        else:
            # Fallback for execution errors
            test_details = [{
                "test_name": "execution_error",
                "status": "FAIL",
                "error": stderr or "Unknown execution error",
                "error_type": "execution_failure"
            }]
    
    # Add preserved test results (tests that were skipped because they already passed)
    if preserved_test_results:
        for preserved in preserved_test_results:
            test_details.append({
                "test_name": preserved.get("test_id", "unknown"),
                "status": "PASS",
                "outcome": "preserved",
                "duration": 0,
                "preserved": True,
                "note": "Skipped - already passing from previous iteration"
            })
    
    # Calculate overall status
    total_tests = len(test_details)
    passed_tests = sum(1 for t in test_details if t["status"] == "PASS")
    failed_tests = total_tests - passed_tests
    
    if failed_tests == 0:
        status = "PASS"
        error_summary = None
    else:
        status = "FAIL"
        error_summary = f"{failed_tests} out of {total_tests} tests failed"
    
    result = {
        "status": status,
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": failed_tests,
        "test_details": test_details,
        "error_summary": error_summary,
        "execution_type": "selective",
        "reliability_metrics": {
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "total_executed": len([t for t in test_details if not t.get("preserved", False)]),
            "preserved_count": len([t for t in test_details if t.get("preserved", False)])
        }
    }
    
    logger.info(f"Selective execution results: {passed_tests}/{total_tests} tests passed")
    
    # Log detailed test execution results
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    logger.info("🧪 Test Execution Details:")
    logger.info(f"   Total Tests: {total_tests}")
    logger.info(f"   ✅ Passed: {passed_tests}")
    logger.info(f"   ❌ Failed: {failed_tests}")
    logger.info(f"   📊 Success Rate: {success_rate:.1f}%")
    
    if test_details:
        logger.info("📋 Individual Test Results:")
        for test in test_details:
            status_icon = "✅" if test.get("status") == "PASS" else "❌"
            test_name = test.get("test_name", "unknown")
            duration = test.get("duration", 0)
            logger.info(f"   {status_icon} {test_name} ({duration:.3f}s)")
            if test.get("status") != "PASS" and test.get("error"):
                logger.info(f"      Error: {test.get('error', 'Unknown error')[:100]}...")
    
    return result


def _parse_pytest_output(stdout: str, return_code: int) -> Dict[str, Any]:
    """Parse pytest output to extract test results."""
    results = {
        "summary": {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "error": 0
        },
        "tests": [],
        "duration": 0.0
    }
    
    if not stdout:
        return results
    
    lines = stdout.split('\n')
    
    # Parse test results from output
    import re
    for line in lines:
        # Look for test results like "test_file.py::test_name PASSED [33%]"
        # Use regex to properly extract test name and status
        test_match = re.match(r'^(.+?::(.+?))\s+(PASSED|FAILED|SKIPPED|ERROR)', line)
        if test_match:
            full_test_path = test_match.group(1)
            test_name = test_match.group(2)
            status = test_match.group(3).lower()
            
            results["tests"].append({
                "name": test_name,
                "outcome": status,
                "duration": 0.0
            })
            
            if status == "passed":
                results["summary"]["passed"] += 1
            elif status == "failed":
                results["summary"]["failed"] += 1
            elif status == "skipped":
                results["summary"]["skipped"] += 1
            elif status == "error":
                results["summary"]["error"] += 1
            
            results["summary"]["total"] += 1
        
        # Look for duration info
        if "seconds" in line and ("passed" in line or "failed" in line):
            # Try to extract duration from summary line
            import re
            duration_match = re.search(r'(\d+\.?\d*)\s*seconds?', line)
            if duration_match:
                results["duration"] = float(duration_match.group(1))
    
    return results


def _count_test_functions(test_code: str) -> int:
    """Count the number of test functions in test code."""
    pattern = r'def\s+(test_\w+)'
    matches = re.findall(pattern, test_code)
    return len(matches)


def _parse_pytest_stdout(stdout: str) -> List[Dict[str, Any]]:
    """Parse pytest stdout output to extract test results."""
    test_details = []
    
    # Look for test result lines
    lines = stdout.split('\n')
    for line in lines:
        if '::test_' in line and ('PASSED' in line or 'FAILED' in line):
            parts = line.split()
            if len(parts) >= 2:
                test_name = parts[0].split('::')[-1]
                status = "PASS" if "PASSED" in line else "FAIL"
                
                test_detail = {
                    "test_name": test_name,
                    "status": status,
                    "outcome": status.lower() + "ed"
                }
                
                if status == "FAIL":
                    test_detail["error"] = "Test failed - see pytest output for details"
                    test_detail["error_type"] = "assertion_error"
                
                test_details.append(test_detail)
    
    return test_details
