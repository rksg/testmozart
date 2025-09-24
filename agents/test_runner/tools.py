import json
import shutil
import tempfile
import os
import sys
import subprocess
import re  # Added missing import for the parser function
import logging
from typing import Any, Dict, List, Optional
# import docker # No longer needed
from pydantic import BaseModel, Field
from .execution_tracker import execution_tracker

# Set up logging
logger = logging.getLogger(__name__)

def _clean_test_code(test_code: str) -> str:
    """
    Clean test code to remove markdown formatting and other artifacts.
    
    Args:
        test_code: Raw test code that may contain markdown formatting
        
    Returns:
        Clean Python code ready for execution
    """
    # Remove markdown code block markers
    clean_code = test_code.strip()
    
    # Remove opening ```python or ``` markers
    if clean_code.startswith('```python'):
        clean_code = clean_code[9:].strip()
    elif clean_code.startswith('```'):
        clean_code = clean_code[3:].strip()
    
    # Remove closing ``` markers
    if clean_code.endswith('```'):
        clean_code = clean_code[:-3].strip()
    
    # Fix import statements - change source_to_test to sample_code
    clean_code = clean_code.replace('from source_to_test import', 'from sample_code import')
    clean_code = clean_code.replace('import source_to_test', 'import sample_code')
    
    return clean_code

# --- Pydantic Models for Structured Output ---

class TestFailureDetail(BaseModel):
    """Details of a single test failure."""
    test_name: str
    error_message: str
    traceback: str


class TestResult(BaseModel):
    """A structured representation of the test execution results."""
    status: str = Field(..., description="Overall status: 'PASS' or 'FAIL'.")
    summary: str = Field(..., description="The summary line from the test runner (e.g., '1 failed, 1 passed').")
    failures: List[TestFailureDetail] = Field(default_factory=list, description="A list of detailed failure information.")

# --- Helper Functions ---

def _count_test_functions(test_code: str) -> int:
    """Count the number of test functions in the test code."""
    import re
    test_functions = re.findall(r'def (test_\w+)', test_code)
    return len(test_functions)

def _print_progress(message: str, step: int = None, total: int = None):
    """Print progress message to console with optional step counter."""
    if step is not None and total is not None:
        print(f"[{step}/{total}] {message}")
    else:
        print(f"🔧 {message}")

# --- Tool Implementations ---

def execute_tests_sandboxed(source_code_under_test: str, generated_test_code: str) -> Dict[str, Any]:
    """
    Executes generated tests against source code locally in a temporary virtual environment.
    
    Args:
        source_code_under_test: The original source code as a string.
        generated_test_code: The generated pytest test code as a string.

    Returns:
        A dictionary containing the raw stdout, stderr, and exit code from the execution.
    """
    logger.info("Starting sandboxed test execution")
    
    # Count test functions for progress tracking
    test_count = _count_test_functions(generated_test_code)
    _print_progress(f"Preparing to execute {test_count} test cases...")
    
    # Start execution tracking
    session_id = execution_tracker.start_execution(generated_test_code, source_code_under_test)
    
    # Create a temporary directory to work in
    with tempfile.TemporaryDirectory() as temp_dir:
        
        # --- 1. Create files ---
        _print_progress("Creating test environment files...", 1, 5)
        source_path = os.path.join(temp_dir, "sample_code.py")
        test_path = os.path.join(temp_dir, "test_generated.py")
        req_path = os.path.join(temp_dir, "requirements.txt")

        with open(source_path, "w") as f:
            f.write(source_code_under_test)
            
        # Clean the test code to remove any markdown formatting
        clean_test_code = _clean_test_code(generated_test_code)
        
        with open(test_path, "w") as f:
            f.write(clean_test_code)

        with open(req_path, "w") as f:
            f.write("pytest\n")
            f.write("sqlglot\n")

        # --- 2. Create a virtual environment ---
        _print_progress("Creating virtual environment...", 2, 5)
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

        # --- 4. Install requirements into the venv ---
        _print_progress("Installing test dependencies (pytest)...", 3, 5)
        try:
            subprocess.run(
                [pip_exe, "install", "-r", req_path],
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

        # --- 5. Run tests using the venv's pytest ---
        _print_progress(f"Executing {test_count} test cases...", 4, 5)
        # We run from temp_dir so pytest can find 'source_to_test.py'
        # We do NOT use check=True here, as a non-zero exit code is
        # the expected result for failing tests.
        result = subprocess.run(
            [pytest_exe, test_path, "-v"],  # Added -v for verbose output
            capture_output=True,
            text=True,
            cwd=temp_dir
        )

        raw_output = {
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
        
        # Print completion status with results
        if result.returncode == 0:
            _print_progress(f"✅ All {test_count} test cases executed - all passed!", 5, 5)
        else:
            _print_progress(f"⚠️ {test_count} test cases executed - some failures", 5, 5)
        
        logger.info(f"Test execution completed with exit code: {result.returncode}")
        return raw_output
    # temp_dir and its contents (venv, files) are automatically deleted here


def parse_test_results(raw_execution_output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parses the raw output from the sandboxed execution into a structured JSON object.

    Args:
        raw_execution_output: The dictionary returned by execute_tests_sandboxed.

    Returns:
        A dictionary conforming to the TestResult schema.
    """
    _print_progress("Analyzing test results...")
    logger.info("Parsing test execution results")
    
    exit_code = raw_execution_output.get('exit_code', -1)
    stdout = raw_execution_output.get('stdout', '')
    
    # pytest exit code 0 means all tests passed
    # pytest exit code 1 means tests were collected and run, but some failed
    # Other codes (2-5) indicate other errors (interruption, internal error, etc.)
    status = "PASS" if exit_code == 0 else "FAIL"
    
    # If no tests were run (e.g., syntax error in test file), exit_code might be > 1
    # but the parser might not find failure blocks.
    if exit_code != 0 and exit_code != 1:
        summary = "Test execution error (non-zero exit code)."
        # Put stderr in the summary if stdout is empty
        if not stdout.strip() and raw_execution_output.get('stderr'):
             summary = f"Test execution error:\n{raw_execution_output.get('stderr')}"
        
        return TestResult(
            status="FAIL",
            summary=summary,
            failures=[]
        ).model_dump()

    summary = "No summary found."
    
    # Find the pytest summary line
    # This regex looks for the "short test summary info" block
    summary_match = re.search(r"={10,}\s(short test summary info)\s={10,}([\s\S]*)", stdout)
    
    if summary_match:
        # If the summary block exists, grab the content after it
        summary_content = summary_match.group(2).strip()
        # The actual summary is usually the last line(s) of the output
        final_summary_line = stdout.strip().splitlines()[-1]
        if "failed" in final_summary_line or "passed" in final_summary_line:
             summary = final_summary_line.strip('= ')
        else:
             # Fallback if the last line isn't the summary
             summary = summary_content.splitlines()[0] if summary_content else "Test run complete."
    else:
        # Fallback for simpler output
        final_line = stdout.strip().splitlines()[-1]
        if "failed" in final_line or "passed" in final_line or "no tests ran" in final_line:
            summary = final_line.strip('= ')

    
    # In case of failure, parse the details
    failures = []
    if status == "FAIL":
        # Pytest failure sections are typically marked by '___' underlines
        failure_blocks = re.findall(r"_{5,}\s(.+?)\s_{5,}([\s\S]+?)(?=(_{5,}\s.+?\s_{5,}|={10,}\s(short test summary info)\s={10,}))", stdout)
        
        for block in failure_blocks:
            test_name_full = block[0].strip()
            # Extract just the function name
            test_name = test_name_full.split("::")[-1] if "::" in test_name_full else test_name_full
            
            traceback_content = block[1].strip()
            # The error message is typically the last line before the traceback details or a line starting with 'E '
            error_message = "No specific error message found."
            error_lines = [line for line in traceback_content.splitlines() if line.strip().startswith('E ')]
            
            if error_lines:
                error_message = error_lines[-1].strip()[2:] # Get text after 'E '
            elif traceback_content.splitlines():
                error_message = traceback_content.splitlines()[-1].strip()

            failures.append(TestFailureDetail(
                test_name=test_name,
                error_message=error_message,
                traceback=traceback_content
            ))

    result = TestResult(status=status, summary=summary, failures=failures)
    parsed_results = result.model_dump()
    
    # Update execution tracking with results
    # Note: We need to get the session_id from the current session
    if execution_tracker.current_session:
        session_id = execution_tracker.current_session["session_id"]
        execution_metrics = execution_tracker.end_execution(session_id, parsed_results, raw_execution_output)
        
        # Add execution metrics to the results
        parsed_results["execution_metrics"] = execution_metrics
        parsed_results["reliability_metrics"] = execution_tracker.get_reliability_metrics()
        
        logger.info(f"Added execution tracking data to results")
    
    return parsed_results

