"""Tools for Result Summarization

This module contains tools for the result summarizer agent.
"""

import os
import logging

logger = logging.getLogger(__name__)


def write_test_file_to_project(test_code: str, project_directory: str, test_filename: str = "test_generated.py") -> str:
    """
    Write the generated test file to the project directory.

    Args:
        test_code: The generated test code to write
        project_directory: The project directory path
        test_filename: Name of the test file (default: "test_generated.py")

    Returns:
        Success message with file path
    """
    try:
        test_file_path = os.path.join(project_directory, test_filename)

        # Ensure the directory exists
        os.makedirs(project_directory, exist_ok=True)

        # Write the test file
        with open(test_file_path, 'w') as f:
            f.write(test_code)

        logger.info(f"Test file written to: {test_file_path}")
        lines_written = len(test_code.split('\n'))

        return f"Test file successfully written to {test_file_path} ({lines_written} lines)"

    except Exception as e:
        error_msg = f"Failed to write test file: {str(e)}"
        logger.error(error_msg)
        return error_msg


def push_to_github(pr_url: str) -> str:
    """
    Push the generated test file to the GitHub PR.

    Args:
        pr_url: The GitHub PR URL

    Returns:
        Success message with PR URL
    """
    try:
        from ..utils.github import push_to_github as github_push

        # Push to GitHub
        github_push(pr_url)

        logger.info(f"Successfully pushed changes to PR: {pr_url}")

        return f"Successfully pushed test file to PR: {pr_url}"

    except Exception as e:
        error_msg = f"Failed to push to GitHub: {str(e)}"
        logger.error(error_msg)
        return error_msg
