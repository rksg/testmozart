"""Coverage Validator Agent

This agent validates test scenario coverage against code structure in Stage 1.
"""

from google.adk.agents import LlmAgent
from .tools import validate_scenario_coverage
from ..coverage_loop_controller.tools import should_continue_coverage_loop, exit_coverage_loop, exit_loop

# Create the coverage validator agent
coverage_validator_agent = LlmAgent(
    name="CoverageValidator",
    description="Validates test scenario coverage against code structure",
    model="gemini-2.5-flash",
    instruction="""
    You are a specialized coverage validation expert for Stage 1 of the two-stage architecture.
    
    Your SOLE responsibility is to validate whether test scenarios provide adequate coverage
    of the code structure WITHOUT executing any tests.
    
    **Your Process:**
    1. You will receive test scenarios from state: {coverage_focused_scenarios}
    2. You will receive static analysis from state: {static_analysis_report}
    3. You will receive current iteration count from state: {coverage_iteration}
    4. Call `validate_scenario_coverage` to perform static coverage analysis
    5. Call `should_continue_coverage_loop` with the validation results to make loop decision
    6. If loop should exit, call `exit_coverage_loop` and then `exit_loop()`
    7. Provide a clear assessment including the loop decision
    
    **Key Validation Criteria:**
    - All functions are covered by at least one scenario
    - All class methods are covered by at least one scenario  
    - All classes have instantiation scenarios
    - Overall coverage percentage calculation
    
    **You do NOT validate:**
    - Test execution success or failure
    - Test code quality or syntax
    - Performance or runtime metrics
    
    **Output Format:**
    Provide a clear, structured report including:
    - Overall coverage percentage
    - Coverage status (complete/excellent/good/moderate/insufficient)
    - Specific gaps if any (uncovered functions, methods, classes)
    - Recommendation for next steps
    - Whether coverage target is met for Stage 1 completion
    
    **Example Output:**
    "Coverage Validation Results:
    
    Overall Coverage: 95.2%
    Status: Excellent
    
    Coverage Breakdown:
    - Functions: 100% (5/5 covered)
    - Methods: 87.5% (7/8 covered) 
    - Classes: 100% (2/2 covered)
    
    Remaining Gaps:
    - Method 'Calculator.divide' not covered by any scenario
    
    Recommendation: Near-complete coverage achieved. Consider adding one scenario for the uncovered divide method to reach 100% coverage, or proceed to Stage 2 with current excellent coverage."
    
    **Success Criteria for Stage 1:**
    - Target: 100% coverage (ideal)
    - Minimum: 80% coverage (acceptable to proceed)
    """,
    tools=[validate_scenario_coverage, should_continue_coverage_loop, exit_coverage_loop, exit_loop],
    output_key="coverage_validation_result"
)
