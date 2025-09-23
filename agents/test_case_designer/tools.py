import re
from typing import Any, Dict, List
from pydantic import BaseModel, Field

# Pydantic models define the strict JSON schema for our test scenarios.
# This ensures data consistency between the TestCaseDesigner and TestImplementer agents.

class TestScenario(BaseModel):
    """Represents a single abstract test scenario."""
    description: str = Field(..., description="A clear, concise description of what is being tested.")
    expected_outcome: str = Field(..., description="The expected result or behavior of the code under this test scenario.")

def generate_test_scenarios(natural_language_output: str) -> List[Dict[str, Any]]:
    """
    Takes a natural-language string of test scenarios from an LLM and parses
    it into a structured JSON array of test scenario objects.

    Args:
        natural_language_output: A string containing test scenarios, expected
                                 to be formatted with clear separators.

    Returns:
        A list of dictionaries, where each dictionary conforms to the TestScenario schema.
    """
    scenarios = []
    
    # Split the output into individual scenario blocks based on a separator '---'.
    scenario_blocks = natural_language_output.strip().split('---')

    for block in scenario_blocks:
        if not block.strip():
            continue

        # Use regex to find the content for description and expected outcome.
        # The re.DOTALL flag allows '.' to match newlines.
        desc_match = re.search(r"SCENARIO:\s*(.+?)\s*EXPECTED:", block, re.DOTALL | re.IGNORECASE)
        outcome_match = re.search(r"EXPECTED:\s*(.+)", block, re.DOTALL | re.IGNORECASE)

        if desc_match and outcome_match:
            description = desc_match.group(1).strip()
            expected_outcome = outcome_match.group(1).strip()
            
            try:
                # Validate data against the Pydantic model
                scenario_obj = TestScenario(
                    description=description,
                    expected_outcome=expected_outcome
                )
                # Append the validated data as a dictionary
                scenarios.append(scenario_obj.model_dump())
            except Exception as e:
                # Skip blocks that fail validation
                print(f"Warning: Skipping scenario block due to validation error: {e}\nBlock content:\n{block}")

    if not scenarios:
        raise ValueError("Could not parse any valid scenarios from the provided text.")

    return scenarios

