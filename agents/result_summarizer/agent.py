"""Result Summarizer Agent

This agent summarizes the final test generation results for the user.
"""

from google.adk.agents import LlmAgent
from .tools import write_test_file_to_project, push_to_github


def create_result_summarizer_agent() -> LlmAgent:
    """Creates and returns a configured Result Summarizer agent."""
    return LlmAgent(
        name="ResultSummarizer",
        description="Summarizes the final test generation results for the user.",
        model="gemini-2.5-pro",
        instruction="""You are the final reporting agent. Your task is to present the results to the user and handle file writing and GitHub operations.

PROCESS:
GITHUB WORKFLOW (when pr_url is available):
4. Use the `write_test_file_to_project` tool to write the modified test code to the project directory:
   - test_code: `{generated_test_code}` state variable
   - project_directory: from `{project_directory}` state variable
   - test_filename: `{test_filename}` state variable
5. Use the `push_to_github` tool to push changes to the PR:
   - pr_url: from `{pr_url}` state variable
6. Return a success message with the PR URL

LOCAL WORKFLOW (when pr_url is NOT available):
4. Inspect the `{selective_test_results}` from the shared state.
- If `selective_test_results.status` is "PASS", your final answer MUST be only the modified Python code, enclosed in a python markdown block.
- If `selective_test_results.status` is anything other than "PASS", respond with a message explaining that the tests could not be automatically fixed. You MUST include both the modified Python code from step 2 (in a python markdown block) and the final `{selective_test_results}` (in a json markdown block) to help the user debug manually.
""",
        tools=[write_test_file_to_project, push_to_github],
        output_key="final_test_suite"
    )


# Create the agent instance for backward compatibility
result_summarizer_agent = create_result_summarizer_agent()

