"""Tools for scenario coverage design.

This module contains tools for generating test scenarios that maximize code coverage.
"""

import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger("two_stage_system")

def generate_coverage_focused_scenarios(
    static_analysis: Dict[str, Any],
    uncovered_units: Optional[List[Dict[str, Any]]] = None,
    iteration_count: int = 0
) -> Dict[str, Any]:
    """
    Generate test scenarios focused on achieving maximum code coverage.
    
    This tool is specifically designed for Stage 1 of the two-stage architecture.
    It focuses purely on coverage without worrying about test execution.
    
    Args:
        static_analysis: Static code analysis results
        uncovered_units: List of code units that need coverage (optional)
        iteration_count: Current iteration number for context
        
    Returns:
        Dictionary containing generated test scenarios
    """
    logger.info(f"Generating coverage-focused scenarios (iteration {iteration_count})")
    
    # Extract code structure from static analysis
    # Handle both old format and new AST-based format
    if 'structure' in static_analysis:
        # New AST-based format from code_analyzer
        structure = static_analysis['structure']
        classes = [item for item in structure if item.get('type') == 'class']
        functions = [item for item in structure if item.get('type') == 'function']
        methods = {}
        for cls in classes:
            methods[cls['name']] = cls.get('methods', [])
    else:
        # Legacy format
        classes = static_analysis.get('classes', [])
        functions = static_analysis.get('functions', [])
        methods = static_analysis.get('methods', {})
    
    logger.debug(f"Found {len(classes)} classes, {len(functions)} functions")
    
    # Generate scenarios for all code units
    scenarios = []
    scenario_id = 1
    
    # Generate scenarios for standalone functions
    for func in functions:
        func_name = func.get('name', 'unknown')
        func_params = func.get('parameters', [])
        
        # Generate basic functionality scenario
        scenarios.append({
            "id": f"scenario_{scenario_id:03d}",
            "target_type": "function",
            "target_name": func_name,
            "description": f"Test the '{func_name}' function with typical inputs",
            "coverage_target": f"function:{func_name}",
            "priority": "high"
        })
        scenario_id += 1
        
        # Generate edge case scenarios if function has parameters
        if func_params:
            scenarios.append({
                "id": f"scenario_{scenario_id:03d}",
                "target_type": "function", 
                "target_name": func_name,
                "description": f"Test the '{func_name}' function with edge case inputs",
                "coverage_target": f"function:{func_name}",
                "priority": "medium"
            })
            scenario_id += 1
    
    # Generate scenarios for class methods
    for class_name, class_methods in methods.items():
        for method in class_methods:
            method_name = method.get('name', 'unknown')
            
            # Skip magic methods unless specifically needed
            if method_name.startswith('__') and method_name.endswith('__'):
                if method_name not in ['__init__', '__str__', '__repr__']:
                    continue
            
            scenarios.append({
                "id": f"scenario_{scenario_id:03d}",
                "target_type": "method",
                "target_name": f"{class_name}.{method_name}",
                "description": f"Test the '{method_name}' method of '{class_name}' class",
                "coverage_target": f"method:{class_name}.{method_name}",
                "priority": "high"
            })
            scenario_id += 1
    
    # Generate class instantiation scenarios
    for class_info in classes:
        class_name = class_info.get('name', 'unknown')
        scenarios.append({
            "id": f"scenario_{scenario_id:03d}",
            "target_type": "class",
            "target_name": class_name,
            "description": f"Test instantiation and basic usage of '{class_name}' class",
            "coverage_target": f"class:{class_name}",
            "priority": "high"
        })
        scenario_id += 1
    
    # Focus on uncovered units if provided (for iterations > 1)
    if uncovered_units and iteration_count > 0:
        logger.info(f"Focusing on {len(uncovered_units)} uncovered units")
        
        for unit in uncovered_units:
            # Handle both string and dict formats
            if isinstance(unit, str):
                # If unit is a string, try to parse it
                if ':' in unit:
                    unit_type, unit_name = unit.split(':', 1)
                else:
                    unit_type = 'unknown'
                    unit_name = unit
            elif isinstance(unit, dict):
                unit_type = unit.get('type', 'unknown')
                unit_name = unit.get('name', 'unknown')
            else:
                logger.warning(f"Unknown unit format: {unit}")
                continue
            
            scenarios.append({
                "id": f"scenario_{scenario_id:03d}_focus",
                "target_type": unit_type,
                "target_name": unit_name,
                "description": f"Focused coverage test for {unit_type} '{unit_name}' (iteration {iteration_count})",
                "coverage_target": f"{unit_type}:{unit_name}",
                "priority": "critical",
                "iteration_focus": True
            })
            scenario_id += 1
    
    result = {
        "scenarios": scenarios,
        "total_scenarios": len(scenarios),
        "coverage_targets": [s["coverage_target"] for s in scenarios],
        "generation_metadata": {
            "iteration": iteration_count,
            "focused_on_uncovered": bool(uncovered_units),
            "total_functions": len(functions),
            "total_classes": len(classes),
            "total_methods": sum(len(methods) for methods in methods.values())
        }
    }
    
    logger.info(f"Generated {len(scenarios)} scenarios for coverage optimization")
    
    # Log detailed scenario information
    logger.info("📋 Generated Test Scenarios:")
    for i, scenario in enumerate(scenarios, 1):
        logger.info(f"   {i}. [{scenario.get('priority', 'unknown').upper()}] {scenario.get('description', 'No description')}")
        logger.info(f"      Target: {scenario.get('target_type', 'unknown')} -> {scenario.get('target_name', 'unknown')}")
        logger.info(f"      Coverage: {scenario.get('coverage_target', 'unknown')}")
    
    return result


def prioritize_coverage_gaps(
    current_coverage: Dict[str, Any],
    target_coverage: float = 100.0
) -> List[Dict[str, Any]]:
    """
    Prioritize coverage gaps that need to be addressed.
    
    Args:
        current_coverage: Current coverage analysis results
        target_coverage: Target coverage percentage
        
    Returns:
        List of prioritized coverage gaps
    """
    logger.info("Prioritizing coverage gaps")
    
    gaps = []
    
    # Extract uncovered units from coverage report
    uncovered_units = current_coverage.get('uncovered_units', {})
    
    # Prioritize uncovered functions
    uncovered_functions = uncovered_units.get('functions', [])
    for func_name in uncovered_functions:
        gaps.append({
            "type": "function",
            "name": func_name,
            "priority": "high",
            "reason": "Function not covered by any test scenario"
        })
    
    # Prioritize uncovered methods
    uncovered_methods = uncovered_units.get('methods', {})
    for class_name, methods in uncovered_methods.items():
        for method_name in methods:
            gaps.append({
                "type": "method", 
                "name": f"{class_name}.{method_name}",
                "priority": "high",
                "reason": f"Method of class '{class_name}' not covered"
            })
    
    # Prioritize uncovered classes
    uncovered_classes = uncovered_units.get('classes', [])
    for class_name in uncovered_classes:
        gaps.append({
            "type": "class",
            "name": class_name,
            "priority": "medium",
            "reason": "Class not instantiated in any test scenario"
        })
    
    # Sort by priority (critical > high > medium > low)
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    gaps.sort(key=lambda x: priority_order.get(x.get("priority", "low"), 3))
    
    logger.info(f"Identified {len(gaps)} coverage gaps")
    return gaps
