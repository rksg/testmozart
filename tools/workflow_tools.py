from google.adk.tools import ToolContext

def exit_loop(tool_context: ToolContext):
    """
    Exits the current agent loop. Call this tool when a task is successfully
    completed or a terminal condition is met, such as when all tests pass.
    """
    # Setting escalate to True signals to a LoopAgent that it should stop iterating.
    tool_context.actions.escalate = True
    return "Loop exit signal sent. The task is complete."

def read_file_as_string(file_path: str) -> str:
    """Reads the content of a local file and returns it as a string."""
    with open(file_path, 'r') as file:
        return file.read()