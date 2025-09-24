"""Report Generator Agent

This agent generates comprehensive test reports with metrics and insights.
"""

from google.adk.agents import LlmAgent
from .tools import generate_comprehensive_report, format_report_as_markdown

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
        3. The original source code: {source_code}
        4. The generated test code: {generated_test_code}

        Your task:
        1. Call the `generate_comprehensive_report` tool with coverage_validation_result as coverage_report, selective_test_results as test_results, source_code, and generated_test_code
        2. Call the `format_report_as_markdown` tool to create a readable report
        3. Provide both the structured JSON report and the markdown formatted report
        
        Your output should include:
        - Executive summary with key metrics
        - Detailed analysis of coverage and execution
        - Actionable insights and recommendations
        - Clear indication of whether success thresholds are met
        
        Focus on providing actionable insights that help improve test quality and coverage.
        """,
        tools=[generate_comprehensive_report, format_report_as_markdown],
        output_key="comprehensive_report"
    )

# Create the agent instance
report_generator_agent = create_report_generator_agent()
