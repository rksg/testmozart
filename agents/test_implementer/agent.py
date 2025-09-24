"""Test Implementer Agent

This agent translates abstract test scenarios into syntactically correct, 
idiomatic unit test code.
"""

from google.adk.agents import LlmAgent
from .tools import write_test_code


def create_test_implementer_agent() -> LlmAgent:
    """Creates and returns a configured Test Implementer agent."""
    return LlmAgent(
        name="TestImplementer",
        description="Translates abstract test scenarios into syntactically correct, idiomatic unit test code.",
        model="gemini-2.5-pro",
        instruction="""
        You are an expert Python developer specializing in writing high-quality, effective unit tests using the pytest framework.
        
        Your task is to convert a list of abstract test scenarios into a complete, runnable Python test file.

        You have ONE tool available: `write_test_code`. Use ONLY this tool.

        Process:
        1. For each test scenario in the input, call `write_test_code(test_scenario, "pytest")` to get a skeleton
        2. Take each skeleton and implement the actual test logic
        3. Combine all implemented test functions into a single Python file

        Your final output must be complete Python code that includes:
        - `import pytest` at the top
        - `from sample_code import *` to import the code under test
        - All test functions with proper assertions

        Do NOT call any function other than `write_test_code`.
        """,
        tools=[write_test_code],
        output_key="test_code"
    )


# Create the agent instance for backward compatibility
test_implementer_agent = create_test_implementer_agent()

