"""Code Analyzer Agent

This agent performs deep, accurate static analysis of source code by parsing it
into a structured format using AST analysis.
"""

from google.adk.agents import LlmAgent
from agents.code_analyzer.tools import analyze_code_structure


def create_code_analyzer_agent() -> LlmAgent:
    """Creates and returns a configured Code Analyzer agent."""
    return LlmAgent(
        name="CodeAnalyzer",
        description="Performs deep, accurate static analysis of source code by parsing it into a structured format.",
        model="gemini-2.5-flash",
        instruction="""
        You are a specialized agent for static code analysis. Your sole responsibility is to call the `analyze_code_structure` tool.
        You will receive the source code in the `{source_code}` state variable and the language in the `{language}` state variable.
        You must pass both the language and the source code to the tool.
        Do NOT attempt to analyze, summarize, or explain the code yourself. Only call the tool.
        """,
        tools=[
            analyze_code_structure
        ]
    )


# Create the agent instance for backward compatibility
code_analyzer_agent = create_code_analyzer_agent()

