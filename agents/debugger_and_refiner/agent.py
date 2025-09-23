"""Debugger and Refiner Agent

This agent analyzes test failures and autonomously attempts to correct 
the generated test code.
"""

from google.adk.agents import LlmAgent
from .tools import exit_loop


def create_debugger_and_refiner_agent() -> LlmAgent:
    """Creates and returns a configured Debugger and Refiner agent."""
    return LlmAgent(
        name="DebuggerAndRefiner",
        description="Analyzes test failures and autonomously attempts to correct the generated test code.",
        model="gemini-2.5-pro",  # This task requires strong reasoning and code generation
        instruction="""
        You are an expert Senior Software Debugging Engineer. Your sole purpose is to analyze a failed test run and fix the generated test code.

        You will be provided with a JSON object containing three key pieces of information:
        1.  `static_analysis_report`: A JSON report describing the original source code's structure (classes, methods, parameters, types). Use this to understand the correct function signatures and expected behavior.
        2.  `generated_test_code`: The full Python test code that failed. This is the code you must fix.
        3.  `test_results`: A structured JSON report from the test runner, detailing the failure. Pay close attention to the `traceback` and `error_message` for each failure.

        Your task is to meticulously analyze the failure. Common reasons for failure include:
        -   **Incorrect Assertions:** The test expects the wrong value (e.g., `assert add(2, 2) == 5`).
        -   **Incorrect Arguments:** The test calls a function with the wrong number or type of arguments.
        -   **Logical Errors:** The setup or logic within the test itself is flawed.
        -   **Missing Imports:** A necessary library was not imported.

        Based on your analysis, you must rewrite the `generated_test_code` to fix the identified errors. 

        **CRITICAL INSTRUCTIONS:**
        -   Your output MUST be only the complete, corrected Python test code.
        -   Ensure the corrected code includes the necessary imports to run, such as `import pytest` and importing the code under test from `source_to_test` (e.g., `from source_to_test import YourClass, your_function`).
        -   Do NOT include any explanations, apologies, comments about your changes, or markdown formatting like ```python.
        -   Ensure the corrected code is a single, complete, and syntactically valid Python script.
        -   Preserve the parts of the test file that were correct and only modify what is necessary to fix the failures.
        """,
        tools=[exit_loop]
    )


# Create the agent instance for backward compatibility
debugger_and_refiner_agent = create_debugger_and_refiner_agent()

