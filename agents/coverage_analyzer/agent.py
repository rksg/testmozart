"""Coverage Analyzer Agent

This agent analyzes test coverage and provides coverage metrics.
"""

import logging
from google.adk.agents import LlmAgent
from .tools import calculate_coverage
from tools.workflow_tools import read_file_as_string

# Set up logging
logger = logging.getLogger(__name__)

def create_coverage_analyzer_agent() -> LlmAgent:
    """Creates and returns a configured Coverage Analyzer agent."""
    logger.info("Creating Coverage Analyzer agent")
    
    return LlmAgent(
        name="CoverageAnalyzer",
        description="Analyzes test coverage and provides detailed coverage metrics.",
        model="gemini-2.5-pro",
        instruction="""
        You are a test coverage analysis expert. Your task is to analyze the coverage of generated test scenarios.

        You will receive:
        1. `{source_code_path}`: The path of the source code file to be analyzed
        2. `{test_scenarios}`: The generated test scenarios in JSON format
        
        Your task:
        1. Call the read_file_as_string tool to read the source code from `{source_code_path}`.
        1. Call the `calculate_coverage` tool with the source code and test scenarios
        2. Analyze the coverage results and provide insights
        3. Identify any coverage gaps and suggest additional test scenarios if needed
        
        Your output should be a JSON object containing the coverage analysis results.
        Focus on providing actionable insights about coverage gaps and suggestions for improvement.
        """,
        tools=[read_file_as_string, calculate_coverage]
    )

# Create the agent instance
coverage_analyzer_agent = create_coverage_analyzer_agent()
