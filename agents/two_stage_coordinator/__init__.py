"""Two-Stage Coordinator

This module contains the new main coordinator that orchestrates the two-stage
architecture for autonomous test suite generation.
"""

from .coordinator import two_stage_root_agent, initialize_two_stage_state

__all__ = [
    'two_stage_root_agent',
    'initialize_two_stage_state'
]
