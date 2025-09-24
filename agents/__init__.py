"""Agents Package

This package contains all the specialized agents for the autonomous test 
suite generation system, organized according to Google ADK best practices.
"""

# Import all agents for backward compatibility
from .code_analyzer import code_analyzer_agent
from .coverage_analyzer import coverage_analyzer_agent
from .test_implementer import test_implementer_agent
from .test_runner import test_runner_agent
from .debugger_and_refiner import debugger_and_refiner_agent
from .report_generator import report_generator_agent
from .result_summarizer import result_summarizer_agent

# Import new two-stage coordinator
from .two_stage_coordinator import two_stage_root_agent as root_agent

__all__ = [
    'code_analyzer_agent',
    'coverage_analyzer_agent',
    'test_implementer_agent',
    'test_runner_agent',
    'debugger_and_refiner_agent',
    'report_generator_agent',
    'result_summarizer_agent',
    'root_agent'
]

