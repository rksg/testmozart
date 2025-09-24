"""Coordinator Agent

This module orchestrates the autonomous test suite generation system by
coordinating multiple specialized agents in a structured workflow.
"""

import json
import re
import urllib.request
from google.adk.agents import LlmAgent, SequentialAgent, LoopAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.base_tool import BaseTool
from google.genai import types

# Import the individual agent instances from the new structure
from agents.code_analyzer import code_analyzer_agent
from agents.test_case_designer import test_case_designer_agent
from agents.test_implementer import test_implementer_agent
from agents.test_runner import test_runner_agent
from agents.debugger_and_refiner import debugger_and_refiner_agent
from agents.result_summarizer import result_summarizer_agent


def initialize_state(callback_context: CallbackContext):
    """Parses the initial user message and populates the session state."""
    user_content = callback_context.user_content
    if user_content and user_content.parts:
        text = user_content.parts[0].text
        # Check if the input is a URL
        if text and re.match(r'^https?://', text):
            try:
                with urllib.request.urlopen(text) as response:
                    callback_context.state['source_code'] = response.read().decode('utf-8')
                # Assuming python for now, language can be inferred later
                callback_context.state['language'] = 'python'
            except Exception as e:
                print(f"Error fetching URL: {e}")
                # Fallback to treating the text as source code
                callback_context.state['source_code'] = text
                callback_context.state['language'] = 'python'
        else:
            try:
                if text:
                    initial_data = json.loads(text)
                    callback_context.state['source_code'] = initial_data.get('source_code')
                    callback_context.state['language'] = initial_data.get('language')
                else:
                    callback_context.state['source_code'] = ''
                    callback_context.state['language'] = 'python'
            except (json.JSONDecodeError, AttributeError):
                print("Warning: Could not parse initial JSON request. Treating content as raw source code.")
                callback_context.state['source_code'] = text
                callback_context.state['language'] = 'python'

    # Initialize all required state variables to prevent KeyError
    state_initializers = {
        'static_analysis_report': {},
        'test_scenarios': '',
        'generated_test_code': '',
        'test_results': {'status': 'UNKNOWN'},
    }
    for key, default_value in state_initializers.items():
        if callback_context.state.get(key) is None:
            callback_context.state[key] = default_value


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
code_analyzer_agent.instruction += "\n\nYou will receive the source code in the `{source_code}` state variable and the language in the `{language}` state variable."

# 2. TestCaseDesigner: Read from `static_analysis_report`, save to `test_scenarios`.
test_case_designer_agent.instruction += "\n\nYou will receive the static analysis report in the `{static_analysis_report}` state variable."
test_case_designer_agent.output_key = "test_scenarios"

# 3. TestImplementer: Read from `test_scenarios`, save to `generated_test_code`.
test_implementer_agent.instruction += "\n\nYou will receive the test scenarios in the `{test_scenarios}` state variable."
test_implementer_agent.output_key = "generated_test_code"

# 4. TestRunner: Read `source_code` & `generated_test_code`, save to `test_results`.
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

# 5. DebuggerAndRefiner: Read all context, save corrected code back to `generated_test_code`.
# Import the exit_loop tool from the debugger_and_refiner package
from agents.debugger_and_refiner.tools import exit_loop
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

# The first part of the workflow is a deterministic sequence.
generation_pipeline = SequentialAgent(
    name="GenerationPipeline",
    description="Analyzes code and designs test scenarios in a strict sequence.",
    sub_agents=[
        code_analyzer_agent,
        test_case_designer_agent,
        test_implementer_agent,
    ]
)

# The second part is an iterative loop for implementation and refinement.
refinement_loop = LoopAgent(
    name="RefinementLoop",
    description="An iterative workflow that implements, runs, and debugs test code until it passes or max attempts are reached.",
    sub_agents=[
        test_runner_agent,
        debugger_and_refiner_agent
    ],
    max_iterations=3
)

# The root_agent is now a SequentialAgent that controls the deterministic high-level workflow.
root_agent = SequentialAgent(
    name="CoordinatorAgent",
    description="The master orchestrator for the autonomous test suite generation system.",
    sub_agents=[
        generation_pipeline,
        refinement_loop,
        result_summarizer_agent,
    ],
    before_agent_callback=initialize_state
)
