"""Logging Configuration

This module sets up comprehensive logging for the enhanced test suite generation system.
"""

import logging
import sys
from datetime import datetime

def setup_logging(level=logging.INFO):
    """
    Set up logging configuration for the entire system.
    
    Args:
        level: Logging level (default: INFO)
    """
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler - detailed logs
    log_filename = f"logs/test_generation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Console handler - minimal key information only
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING)  # Only warnings and errors by default
    console_formatter = logging.Formatter('[%(name)s]: %(message)s')
    console_handler.setFormatter(console_formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)  # File gets everything
    
    # Suppress noisy loggers completely from console
    noisy_loggers = [
        'httpx', 'httpcore', 'urllib3', 'google_adk', 'google_genai'
    ]
    for logger_name in noisy_loggers:
        logger = logging.getLogger(logger_name)
        logger.addHandler(file_handler)
        logger.propagate = False
    
    # Configure specific loggers for our modules - file only
    file_only_loggers = [
        'agents.coverage_analyzer',
        'agents.test_runner.execution_tracker',
        'agents.report_generator'
    ]
    
    for logger_name in file_only_loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
    
    # Configure key agent loggers to show in console
    key_agent_loggers = [
        'agents.coordinator',
        'agents.code_analyzer.agent',
        'agents.test_case_designer.enhanced_agent', 
        'agents.coverage_analyzer.agent',
        'agents.test_implementer.agent',
        'agents.test_runner.agent',
        'agents.debugger_and_refiner.agent',
        'agents.feedback_analyzer.agent',
        'agents.quality_loop.agent',
        'agents.report_generator.agent',
        'agents.result_summarizer.agent'
    ]
    
    for logger_name in key_agent_loggers:
        logger = logging.getLogger(logger_name)
        logger.addHandler(console_handler)
        logger.propagate = False
    
    print(f"Logging configured. Log file: {log_filename}")
    return log_filename
