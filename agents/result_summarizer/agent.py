"""Result Summarizer Agent

This agent summarizes the final test generation results for the user.
"""

from google.adk.agents import LlmAgent


def create_result_summarizer_agent() -> LlmAgent:
    """Creates and returns a configured Result Summarizer agent."""
    return LlmAgent(
        name="ResultSummarizer",
        description="Summarizes the final test generation results for the user.",
        model="gemini-2.5-pro",
        instruction="""You are the final reporting agent. Your task is to present the results to the user based on the final shared state.
1. Retrieve the final test code from the `{generated_test_code}` state variable.
2. **CRITICAL:** In the retrieved code, find the line `from source_to_test import ...` and change it to `from sample_code import ...`. This is because the final test suite will be run against `sample_code.py`.
3. Inspect the `{selective_test_results}` from the shared state.
- If `selective_test_results.status` is "PASS", your final answer MUST be only the modified Python code, enclosed in a python markdown block.
- If `selective_test_results.status` is anything other than "PASS", respond with a message explaining that the tests could not be automatically fixed. You MUST include both the modified Python code from step 2 (in a python markdown block) and the final `{selective_test_results}` (in a json markdown block) to help the user debug manually.
""",
        output_key="final_test_suite"
    )


# Create the agent instance for backward compatibility
result_summarizer_agent = create_result_summarizer_agent()

