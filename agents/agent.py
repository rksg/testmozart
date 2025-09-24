"""Coordinator Agent

This module orchestrates the autonomous test suite generation system by
coordinating multiple specialized agents in a structured workflow.

Note: This is a legacy coordinator that has been replaced by the two_stage_coordinator.
It is kept for reference but should not be used in the main system.
"""

import json
from google.adk.agents import LlmAgent, SequentialAgent, LoopAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.base_tool import BaseTool
from google.genai import types

# Import the individual agent instances from the current structure
from .code_analyzer import code_analyzer_agent
from .coverage_analyzer import coverage_analyzer_agent
from .test_implementer.agent import create_test_implementer_agent
from .test_runner.agent import create_test_runner_agent
from .debugger_and_refiner import debugger_and_refiner_agent
from .report_generator import report_generator_agent
from .result_summarizer import result_summarizer_agent


def initialize_state(callback_context: CallbackContext):
    """Parses the initial user message and populates the session state."""
    user_content = callback_context.user_content
    if user_content and user_content.parts:
        try:
            initial_data = json.loads(user_content.parts[0].text)
            callback_context.state['source_code'] = initial_data.get('source_code')
            callback_context.state['language'] = initial_data.get('language')
        except (json.JSONDecodeError, AttributeError):
            print("Warning: Could not parse initial JSON request. Treating content as raw source code.")
            callback_context.state['source_code'] = user_content.parts[0].text
            callback_context.state['language'] = 'python'
    
    # Initialize all required state variables to prevent KeyError
    callback_context.state.setdefault('static_analysis_report', {})
    callback_context.state.setdefault('test_scenarios', '')
    callback_context.state.setdefault('coverage_report', {})
    callback_context.state.setdefault('generated_test_code', '')
    callback_context.state.setdefault('test_results', {"status": "UNKNOWN"})
    callback_context.state.setdefault('comprehensive_report', {})


def save_analysis_to_state(tool: BaseTool, args: dict, tool_context: ToolContext, tool_response: dict):
    """
    This callback intercepts the result from the `analyze_code_structure` tool,
    saves it directly to the session state, and ends the agent's turn.
    This is more efficient than waiting for the LLM to summarize the result.
    """
    if tool.name == 'analyze_code_structure':
        # Save the tool's direct output to the state.
        tool_context.state['static_analysis_report'] = tool_response
        # Return a simple content object. This signals to the ADK that the
        # agent's turn is complete, preventing an unnecessary second LLM call.
        return types.Content(parts=[types.Part(text="Static analysis complete.")])


# --- Configure Individual Agents for the Workflow ---

# 1. CodeAnalyzer: Use the callback to save output.
code_analyzer_agent.after_tool_callback = save_analysis_to_state

# 2. CoverageAnalyzer: Read from `source_code` and `test_scenarios`, save to `coverage_report`.
coverage_analyzer_agent.instruction += "\n\nYou will receive the source code in `{source_code}` and test scenarios in `{test_scenarios}` state variables."
coverage_analyzer_agent.output_key = "coverage_report"

# 3. TestImplementer: Read from `test_scenarios`, save to `generated_test_code`.
def create_configured_test_implementer():
    """Creates a properly configured test implementer agent."""
    agent = create_test_implementer_agent()
    agent.instruction += "\n\nYou will receive the test scenarios in the `{test_scenarios}` state variable."
    agent.output_key = "generated_test_code"
    return agent

# Create the main test implementer agent
test_implementer_agent = create_configured_test_implementer()

# 4. TestRunner: Read `source_code` & `generated_test_code`, save to `test_results`.
test_runner_agent = create_test_runner_agent()
async def build_test_runner_instruction(ctx: CallbackContext) -> str:
    """Dynamically creates the prompt for the test runner with code from the state."""
    source_code = ctx.state.get('source_code', '')
    generated_code = ctx.state.get('generated_test_code', '')

    source_code_json_str = json.dumps(source_code)
    generated_code_json_str = json.dumps(generated_code)
    
    return f"""
    You are a highly reliable test execution engine. Your task is to execute a test suite against source code.

    First, call the `execute_tests_sandboxed` tool with the following two arguments:
    - `source_code_under_test`: Set this to the string {source_code_json_str}
    - `generated_test_code`: Set this to the string {generated_code_json_str}

    Second, take the entire, raw JSON output from `execute_tests_sandboxed` and immediately pass it as the `raw_execution_output` argument to the `parse_test_results` tool.
    Your final output must be only the structured JSON object returned by the `parse_test_results` tool. Do not add any commentary or explanation.
    """

test_runner_agent.instruction = build_test_runner_instruction
test_runner_agent.output_key = "test_results"

# 5. ReportGenerator: Read all analysis results, save to `comprehensive_report`.
report_generator_agent.instruction += "\n\nYou will receive coverage_report, test_results, source_code, and generated_test_code from the shared state."
report_generator_agent.output_key = "comprehensive_report"

# 6. DebuggerAndRefiner: Read all context, save corrected code back to `generated_test_code`.
# Import the exit_loop tool from the debugger_and_refiner package
from .debugger_and_refiner.tools import exit_loop
debugger_and_refiner_agent.tools.append(exit_loop)

debugger_and_refiner_agent.instruction = """
You are an expert Senior Software Debugging Engineer. Your sole purpose is to analyze a failed test run and fix the generated test code.

You have access to the following information from the shared state:
- `{static_analysis_report}`: A JSON report describing the original source code's structure.
- `{generated_test_code}`: The full Python test code that failed. This is the code you must fix.
- `{test_results}`: A structured JSON report from the test runner, detailing the failure.

Your task is to meticulously analyze the `test_results`. If the `status` is "PASS", your job is done and you MUST call the `exit_loop` tool immediately.

If the `status` is "FAIL", you must rewrite the `generated_test_code` to fix the errors identified in the `test_results`.

**CRITICAL INSTRUCTIONS:**
- If tests passed, call `exit_loop()`.
- If tests failed, your output MUST be only the complete, corrected Python test code.
- Ensure the corrected code includes the necessary imports to run, such as `import pytest` and importing the code under test from `source_to_test` (e.g., `from source_to_test import YourClass, your_function`).
- Do NOT include any explanations, comments, or markdown formatting like ```python.
"""
debugger_and_refiner_agent.output_key = "generated_test_code"


# --- Assemble Workflow Agents ---

# Initial code analysis - this only runs once
initial_analysis = SequentialAgent(
    name="InitialAnalysis",
    description="Performs initial code analysis to understand the structure.",
    sub_agents=[
        code_analyzer_agent,
    ]
)

# Create a separate test runner instance for the execution refinement loop
execution_test_runner = create_test_runner_agent()
execution_test_runner.name = "ExecutionTestRunner"  # Give it a unique name
execution_test_runner.instruction = build_test_runner_instruction
execution_test_runner.output_key = "test_results"

# Final execution and refinement loop - focuses on fixing syntax/execution errors
execution_refinement_loop = LoopAgent(
    name="ExecutionRefinementLoop",
    description="Fixes execution errors in the final test code until it runs successfully.",
    sub_agents=[
        execution_test_runner,
        debugger_and_refiner_agent
    ],
    max_iterations=3
)

# The legacy_root_agent orchestrates a simplified workflow
# NOTE: This is kept for reference only. Use two_stage_coordinator.root_agent instead.
legacy_root_agent = SequentialAgent(
    name="LegacyCoordinatorAgent",
    description="Legacy coordinator for the autonomous test suite generation system.",
    sub_agents=[
        initial_analysis,
        test_implementer_agent,
        execution_refinement_loop,
        report_generator_agent,
        result_summarizer_agent,
    ],
    before_agent_callback=initialize_state
)