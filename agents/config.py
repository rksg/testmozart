"""Configuration parameters for the two-stage architecture."""

# Stage 1: Coverage Optimization Loop Configuration
COVERAGE_MAX_ITERATIONS = 5      # Maximum iterations for coverage optimization
COVERAGE_TARGET = 100            # Target coverage percentage (100% = full coverage)
MIN_COVERAGE_THRESHOLD = 80      # Minimum acceptable coverage to proceed to Stage 2

# Stage 2: Execution Quality Loop Configuration  
EXECUTION_MAX_ITERATIONS = 10    # Maximum iterations for execution quality improvement
EXECUTION_SUCCESS_THRESHOLD = 95 # Target execution success rate percentage

# General Configuration
DEFAULT_TEST_FRAMEWORK = "pytest"
LOG_LEVEL = "INFO"

# Quality Thresholds (kept for compatibility with reporting)
QUALITY_SCORE_THRESHOLD = 90
SUCCESS_RATE_THRESHOLD = 95
