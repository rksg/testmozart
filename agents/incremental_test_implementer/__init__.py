"""Incremental Test Implementer Agent

This module contains the agent responsible for implementing only the test cases
that need attention (failed or new) in Stage 2 of the two-stage architecture.
"""

from .agent import incremental_test_implementer_agent
from .tools import implement_failed_tests, merge_test_implementations

__all__ = [
    'incremental_test_implementer_agent',
    'implement_failed_tests',
    'merge_test_implementations'
]
