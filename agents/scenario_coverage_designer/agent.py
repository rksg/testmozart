"""Scenario Coverage Designer Agent

This agent is responsible for generating test scenarios that achieve maximum
code coverage in Stage 1 of the two-stage architecture.
"""

from google.adk.agents import LlmAgent
from .tools import generate_coverage_focused_scenarios, prioritize_coverage_gaps

# Create the scenario coverage designer agent
scenario_coverage_designer_agent = LlmAgent(
    name="ScenarioCoverageDesigner",
    description="Generates test scenarios focused on achieving maximum code coverage",
    model="gemini-2.5-flash",
    instruction="""
    You are a test scenario generator. Your job is to create test scenarios for maximum code coverage.

    **CRITICAL: You MUST call the `generate_coverage_focused_scenarios` tool immediately.**

    Input data:
    - Static analysis report: {static_analysis_report}

    Your task:
    1. Call `generate_coverage_focused_scenarios` with the static_analysis_report
    2. Provide a summary of the generated scenarios

    Do NOT write scenarios manually. Use the tool to generate them.
    """,
    tools=[generate_coverage_focused_scenarios, prioritize_coverage_gaps],
    output_key="coverage_focused_scenarios"
)
