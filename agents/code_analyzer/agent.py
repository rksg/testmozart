"""Code Analyzer Agent

This agent performs deep, accurate static analysis of source code by parsing it 
into a structured format using AST analysis.
"""

from google.adk.agents import LlmAgent
from .tools import analyze_code_structure
from tools.workflow_tools import read_file_as_string

def create_code_analyzer_agent() -> LlmAgent:
    """Creates and returns a configured Code Analyzer agent."""
    return LlmAgent(
        name="CodeAnalyzer",
        description="Performs deep, accurate static analysis of source code by parsing it into a structured format.",
        model="gemini-2.5-flash",
        instruction="""
        You are a specialized agent for static code analysis. Your sole responsibility is to read_file_as_string on a list of source code file paths in {source_code_path} and call the `analyze_code_structure` tool with the `read_file_as_string` result as source_code and python as the language.
        You must correctly identify the programming language from the user's request or file context and pass both the language and the source code to the tool.
        Do NOT attempt to analyze, summarize, or explain the code yourself. Only call the tool.
        """,
        tools=[
            analyze_code_structure,
            read_file_as_string
        ]
    )


# Create the agent instance for backward compatibility
code_analyzer_agent = create_code_analyzer_agent()

