"""Incremental Test Implementer Agent

This agent implements test code only for failed test cases in Stage 2,
while preserving already passing test implementations.
"""

import logging
from google.adk.agents import LlmAgent
from .tools import implement_failed_tests, merge_test_implementations
from ..test_implementer.tools import write_test_code

logger = logging.getLogger(__name__)

# Create the incremental test implementer agent
incremental_test_implementer_agent = LlmAgent(
    name="IncrementalTestImplementer",
    description="Implements test code only for failed test cases, preserving passing tests",
    model="gemini-2.5-pro",
    instruction="""
    You are an expert Python developer specializing in writing high-quality, effective unit tests using the pytest framework.
    
    Your task is to convert a list of test scenarios, provided in the coverage_focused_scenarios state variable, into a complete, runnable Python test file.

    Follow this exact process for EACH scenario in the scenarios array:
    1. For each scenario, create a test_scenario object with 'description' (from scenario.description) and 'expected_outcome' (infer from target_name and description).
    2. Call the `write_test_code` tool with the test_scenario object and `target_framework='pytest'`. This will give you a function skeleton.
    3. Receive the boilerplate code from the tool.
    4. You MUST then replace the placeholder `# TODO: Implement the test logic and assertion here.` and the `...` with the actual Python code required to execute the test.
    5. This implementation should include:
       - Setting up any necessary input variables based on target_name.
       - Calling the function or method being tested (use target_name field).
       - Writing a clear `assert` statement that verifies the expected outcome.
    
    **Expected Outcome Guidelines:**
    - For Calculator.add: "Should return the sum of two numbers"
    - For greet function: "Should return a greeting message"
    - For class instantiation: "Should create a valid instance"

    After processing all scenarios, combine all the generated test functions into a single Python code block.
    This final block MUST include all necessary imports at the top. This includes `import pytest` and, critically, importing the necessary classes and functions from the code being tested. The code to be tested will be in a file named `sample_code.py`, so your import statement should look like `from sample_code import YourClass, your_function`.
    Your final output should be ONLY the complete Python code as a raw string.
    """,
    tools=[write_test_code],
    output_key="generated_test_code"
)
