"""Selective Test Runner Agent

This agent executes tests and provides comprehensive results.
"""

from google.adk.agents import LlmAgent
from .tools import execute_selective_tests, parse_selective_results
from tools.workflow_tools import read_file_as_string
# Create the selective test runner agent
selective_test_runner_agent = LlmAgent(
    name="SelectiveTestRunner",
    description="Executes test suites and provides detailed results",
    model="gemini-2.5-flash",
    instruction="""
    You are a test execution specialist that runs Python test suites and provides detailed results.
    
    **Your Process:**
    1. You will receive a complete test suite from state: {generated_test_code}
    2. You will receive source code from the source code path: {source_code_path}
    3. Call `execute_selective_tests` to run the complete test suite against the source code
    4. Call `parse_selective_results` to analyze the execution results
    5. Provide comprehensive test execution results and metrics
    
    **Your Task:**
    - Use the read_file_as_string tool to read the source code from `{source_code_path}`.
    - Execute the complete test suite using pytest
    - Capture all test results, errors, and execution details
    - Provide detailed metrics including pass/fail counts and execution time
    - Report any syntax errors, import errors, or assertion failures
    
    **Output Requirements:**
    - Total number of tests executed
    - Number of passed, failed, and skipped tests
    - Execution success rate percentage
    - Detailed error information for any failed tests
    - Overall test execution summary
    """,
    tools=[read_file_as_string, execute_selective_tests, parse_selective_results],
    output_key="selective_test_results"
)