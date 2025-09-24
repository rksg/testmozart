"""Coverage Loop Controller Agent

This module contains the agent responsible for controlling the coverage optimization loop
in Stage 1 of the two-stage architecture.
"""

from .agent import coverage_loop_controller_agent
from .tools import should_continue_coverage_loop, exit_coverage_loop

__all__ = [
    'coverage_loop_controller_agent',
    'should_continue_coverage_loop',
    'exit_coverage_loop'
]
