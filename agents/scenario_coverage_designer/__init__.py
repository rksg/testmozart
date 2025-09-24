"""Scenario Coverage Designer Agent

This module contains the agent responsible for generating test scenarios
that achieve maximum code coverage in Stage 1 of the two-stage architecture.
"""

from .agent import scenario_coverage_designer_agent
from .tools import generate_coverage_focused_scenarios

__all__ = [
    'scenario_coverage_designer_agent',
    'generate_coverage_focused_scenarios'
]
