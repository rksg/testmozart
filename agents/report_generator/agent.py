"""Report Generator Agent

This agent generates comprehensive test reports with metrics and insights.
"""

from google.adk.agents import LlmAgent
from .tools import generate_comprehensive_report, format_report_as_markdown
from tools.workflow_tools import read_file_as_string
def create_report_generator_agent() -> LlmAgent:
    """Creates and returns a configured Report Generator agent."""
    return LlmAgent(
        name="ReportGenerator",
        description="Generates comprehensive test reports with coverage metrics, execution statistics, and actionable insights.",
        model="gemini-2.5-pro",
        instruction="""
        You are a test analysis and reporting expert. Your task is to generate a comprehensive test report.

        You will receive from the shared state:
        1. Coverage analysis results: {coverage_validation_result}
        2. Test execution results with metrics: {selective_test_results}
        3. The path of the original source code: {source_code_path}
        4. The generated test code: {generated_test_code}

        Your task:
        1. Call the read_file_as_string tool to read the source code from `{source_code_path}`.
        2. Call the `generate_comprehensive_report` tool with coverage_validation_result as coverage_report, selective_test_results as test_results, source_code, and generated_test_code
        3. Call the `format_report_as_markdown` tool to create a readable report
        4. Provide both the structured JSON report and the markdown formatted report

        Your output should include:
        - Executive summary with key metrics
        - Detailed analysis of coverage and execution
        - Actionable insights and recommendations
        - Clear indication of whether success thresholds are met
        
        Focus on providing actionable insights that help improve test quality and coverage.
        """,
        tools=[read_file_as_string, generate_comprehensive_report, format_report_as_markdown],
        output_key="comprehensive_report"
    )

# Create the agent instance
report_generator_agent = create_report_generator_agent()
