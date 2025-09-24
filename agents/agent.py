"""Two-Stage Coordinator

This module orchestrates the new two-stage autonomous test suite generation system.
"""

import json
import re
import logging
from google.adk.agents import LlmAgent, SequentialAgent, LoopAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.base_tool import BaseTool
from google.genai import types

# Import agent creation functions to avoid sharing agent instances
from .code_analyzer.agent import create_code_analyzer_agent
from .report_generator.agent import create_report_generator_agent
from .result_summarizer.agent import create_result_summarizer_agent

# Import new Stage 1 agent creation functions
from .scenario_coverage_designer.agent import scenario_coverage_designer_agent as create_scenario_coverage_designer
from .coverage_validator.agent import coverage_validator_agent as create_coverage_validator
# Import new Stage 2 agents and tools
from .incremental_test_implementer.agent import incremental_test_implementer_agent as create_incremental_test_implementer
from .selective_test_runner.agent import selective_test_runner_agent as create_selective_test_runner

# Import exit_loop tool
from .coverage_loop_controller.tools import exit_loop

# Import configuration
from .config import COVERAGE_MAX_ITERATIONS, EXECUTION_MAX_ITERATIONS

logger = logging.getLogger("two_stage_system")

def save_source_load_to_local(callback_context: CallbackContext):
    from .utils.gcs_bucket import get_file_from_gcs
    from .utils.github import get_changed_file_from_pr
    """Saves the source code from GCS or GitHub to local state and filesystem."""
    user_content = callback_context.user_content
    if user_content and user_content.parts:
        try:
            text = user_content.parts[0].text
            if re.match(r'^gs://', text):
                gcs_url = user_content.parts[0].text.strip()
                source_code = get_file_from_gcs(gcs_url)
                callback_context.state['source_code_path'] = source_code
                callback_context.state['language'] = 'python'
                logger.info(f"Loaded source code from GCS URL: {gcs_url}")
            elif re.match(r'^https://github\.com/[^/]+/[^/]+/pull/\d+$', text):
                pr_url = user_content.parts[0].text.strip()
                source_code = get_changed_file_from_pr(pr_url)
                callback_context.state['source_code_path'] = source_code
                callback_context.state['language'] = 'python'
                logger.info(f"Downloaded source code from GitHub PR: {pr_url}")
            else:
                initial_data = json.loads(user_content.parts[0].text)
                callback_context.state['language'] = initial_data.get('language')
        except (json.JSONDecodeError, AttributeError):
            logger.warning("Could not parse initial JSON request. Treating content as raw source code.")
            callback_context.state['language'] = 'python'

def initialize_two_stage_state(callback_context: CallbackContext):
    """Initialize state for the two-stage architecture."""
    # Initialize state variables for two-stage architecture
    state_initializers = {
        'static_analysis_report': {},

        # Stage 1 state variables
        'coverage_focused_scenarios': [],
        'coverage_validation_result': {},
        'coverage_loop_decision': {},
        'stage1_complete': False,

        # Stage 2 state variables
        'test_status_tracking': {},
        'incremental_test_implementation': {},
        'selective_test_results': {},
        'execution_loop_decision': {},
        'stage2_complete': False,

        # Final artifacts
        'comprehensive_report': {},
        'generated_test_code': '',

        # Iteration counters
        'coverage_iteration': 0,
        'execution_iteration': 0,
    }
    for key, default_value in state_initializers.items():
        if callback_context.state.get(key) is None:
            callback_context.state[key] = default_value

    logger.info("Two-stage architecture state initialized")


def save_analysis_to_state(tool: BaseTool, args: dict, tool_context: ToolContext, tool_response: dict):
    """Save code analysis results directly to state."""
    if tool.name == 'analyze_code_structure':
        tool_context.state['static_analysis_report'] = tool_response
        print(f"Saved analysis result to state: {tool_response}")
        return tool_response


# Create fresh agent instances for the two-stage system
code_analyzer_agent = create_code_analyzer_agent()
report_generator_agent = create_report_generator_agent()
result_summarizer_agent = create_result_summarizer_agent()

# Create Stage 1 agent instances (imported as aliases)
scenario_coverage_designer_agent = create_scenario_coverage_designer
coverage_validator_agent = create_coverage_validator

# Create Stage 2 agent instances (imported as aliases)
incremental_test_implementer_agent = create_incremental_test_implementer
selective_test_runner_agent = create_selective_test_runner

# Configure the code analyzer
code_analyzer_agent.after_tool_callback = save_analysis_to_state

# Configure Stage 1 agents
scenario_coverage_designer_agent.instruction += "\n\nYou will receive the static analysis report in the `{static_analysis_report}` state variable."

coverage_validator_agent.instruction += "\n\nYou will receive the coverage scenarios in the `{coverage_focused_scenarios}` state variable, static analysis in the `{static_analysis_report}` state variable, and current iteration count in the `{coverage_iteration}` state variable."

# Configure Stage 2 agents
incremental_test_implementer_agent.instruction += "\n\nYou will receive the test scenarios in the `{coverage_focused_scenarios}` state variable."

selective_test_runner_agent.instruction += "\n\nYou will receive the test suite in the `{generated_test_code}` state variable and source code in the path `{source_code_path}`, use read_file_as_string tool to get the source code."

# Configure final reporting agents (reused from existing system)
report_generator_agent.instruction += "\n\nYou will receive coverage report in `{coverage_validation_result}`, test results in `{selective_test_results}`, source code in `{source_code}`, and generated test code in `{generated_test_code}`."

result_summarizer_agent.instruction += "\n\nYou will receive the comprehensive report in `{comprehensive_report}` and final test suite in `{generated_test_code}`."

# --- Stage 1: Coverage Optimization Loop ---

# Create the coverage optimization loop with integrated validation and control
coverage_optimization_loop = LoopAgent(
    name="CoverageOptimizationLoop",
    description="Stage 1: Optimizes test scenarios to achieve maximum code coverage",
    sub_agents=[
        scenario_coverage_designer_agent,
        coverage_validator_agent  # Now includes loop control logic
    ],
    max_iterations=COVERAGE_MAX_ITERATIONS
)

# --- Stage 2: Execution Quality Loop ---

# Simplified Stage 2: Direct test implementation and execution
stage2_test_implementation = SequentialAgent(
    name="Stage2TestImplementation",
    description="Stage 2: Convert scenarios to executable tests and run them",
    sub_agents=[
        incremental_test_implementer_agent,
        selective_test_runner_agent
    ]
)

# --- Complete Two-Stage System ---

two_stage_system = SequentialAgent(
    name="TwoStageTestGeneration",
    description="Complete two-stage test generation system with coverage optimization and test implementation",
    sub_agents=[
        code_analyzer_agent,              # Initial code analysis
        coverage_optimization_loop,       # Stage 1: Coverage optimization
        stage2_test_implementation,       # Stage 2: Test implementation and execution
        report_generator_agent,          # Final reporting
        result_summarizer_agent          # Final output formatting
    ]
)

# The root agent for the two-stage architecture
root_agent = SequentialAgent(
    name="TwoStageCoordinator",
    description="The master coordinator for the two-stage autonomous test suite generation system",
    sub_agents=[two_stage_system],
    before_agent_callback=[save_source_load_to_local, initialize_two_stage_state]
)
