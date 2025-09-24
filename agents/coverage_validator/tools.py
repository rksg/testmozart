"""Tools for coverage validation.

This module contains tools for validating test scenario coverage against code structure.
"""

import logging
from typing import Dict, List, Any, Set

logger = logging.getLogger("two_stage_system")

def validate_scenario_coverage(
    test_scenarios: List[Dict[str, Any]],
    static_analysis: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Validate that test scenarios provide adequate coverage of the code structure.
    
    This is a static analysis that maps scenarios to code units without execution.
    
    Args:
        test_scenarios: List of test scenarios to validate
        static_analysis: Static code analysis results
        
    Returns:
        Dictionary with coverage validation results
    """
    logger.info(f"Validating coverage for {len(test_scenarios)} scenarios")
    
    # Extract all testable units from static analysis
    all_functions = set()
    all_classes = set()
    all_methods = set()
    
    # Handle both old format and new AST-based format
    if 'structure' in static_analysis:
        # New AST-based format from code_analyzer
        structure = static_analysis['structure']
        for item in structure:
            if item.get('type') == 'function':
                all_functions.add(item['name'])
            elif item.get('type') == 'class':
                all_classes.add(item['name'])
                # Process methods within the class
                for method in item.get('methods', []):
                    all_methods.add(f"{item['name']}.{method['name']}")
    else:
        # Legacy format
        # Process functions
        functions = static_analysis.get('functions', [])
        for func in functions:
            func_name = func.get('name')
            if func_name:
                all_functions.add(func_name)
        
        # Process classes
        classes = static_analysis.get('classes', [])
        for cls in classes:
            class_name = cls.get('name')
            if class_name:
                all_classes.add(class_name)
        
        # Process methods
        methods = static_analysis.get('methods', {})
        for class_name, class_methods in methods.items():
            for method in class_methods:
                method_name = method.get('name')
                if method_name:
                    all_methods.add(f"{class_name}.{method_name}")
    
    # Track covered units by analyzing scenario targets
    covered_functions = set()
    covered_classes = set()
    covered_methods = set()
    
    for scenario in test_scenarios:
        target_type = scenario.get('target_type', '')
        target_name = scenario.get('target_name', '')
        coverage_target = scenario.get('coverage_target', '')
        
        # Parse coverage target to determine what's covered
        if target_type == 'function' or coverage_target.startswith('function:'):
            covered_functions.add(target_name)
        elif target_type == 'class' or coverage_target.startswith('class:'):
            covered_classes.add(target_name)
        elif target_type == 'method' or coverage_target.startswith('method:'):
            covered_methods.add(target_name)
    
    # Calculate coverage metrics
    total_units = len(all_functions) + len(all_classes) + len(all_methods)
    covered_units = len(covered_functions) + len(covered_classes) + len(covered_methods)
    
    overall_coverage = (covered_units / total_units * 100) if total_units > 0 else 0
    
    function_coverage = (len(covered_functions) / len(all_functions) * 100) if all_functions else 100
    class_coverage = (len(covered_classes) / len(all_classes) * 100) if all_classes else 100
    method_coverage = (len(covered_methods) / len(all_methods) * 100) if all_methods else 100
    
    # Identify uncovered units
    uncovered_functions = all_functions - covered_functions
    uncovered_classes = all_classes - covered_classes
    uncovered_methods = all_methods - covered_methods
    
    result = {
        "coverage_summary": {
            "overall_coverage": round(overall_coverage, 2),
            "function_coverage": round(function_coverage, 2),
            "class_coverage": round(class_coverage, 2),
            "method_coverage": round(method_coverage, 2)
        },
        "coverage_details": {
            "total_units": total_units,
            "covered_units": covered_units,
            "uncovered_units": total_units - covered_units
        },
        "covered_units": {
            "functions": list(covered_functions),
            "classes": list(covered_classes),
            "methods": list(covered_methods)
        },
        "uncovered_units": {
            "functions": list(uncovered_functions),
            "classes": list(uncovered_classes),
            "methods": list(uncovered_methods)
        },
        "meets_target": overall_coverage >= 100.0,
        "validation_metadata": {
            "total_scenarios": len(test_scenarios),
            "scenarios_analyzed": len(test_scenarios),
            "validation_timestamp": "static_analysis_based"
        }
    }
    
    logger.info(f"Coverage validation complete: {overall_coverage:.2f}% overall coverage")
    logger.info(f"📊 Coverage Breakdown:")
    logger.info(f"   Functions: {function_coverage:.1f}% ({len(covered_functions)}/{len(all_functions)} covered)")
    logger.info(f"   Classes: {class_coverage:.1f}% ({len(covered_classes)}/{len(all_classes)} covered)")
    logger.info(f"   Methods: {method_coverage:.1f}% ({len(covered_methods)}/{len(all_methods)} covered)")
    
    if uncovered_functions or uncovered_classes or uncovered_methods:
        logger.info("⚠️  Uncovered Units:")
        if uncovered_functions:
            logger.info(f"   Functions: {', '.join(uncovered_functions)}")
        if uncovered_classes:
            logger.info(f"   Classes: {', '.join(uncovered_classes)}")
        if uncovered_methods:
            logger.info(f"   Methods: {', '.join(uncovered_methods)}")
    else:
        logger.info("✅ All units covered!")
    
    logger.debug(f"Function coverage: {function_coverage:.2f}%, Class coverage: {class_coverage:.2f}%, Method coverage: {method_coverage:.2f}%")
    
    return result


def calculate_coverage_metrics(
    coverage_validation: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Calculate detailed coverage metrics from validation results.
    
    Args:
        coverage_validation: Results from validate_scenario_coverage
        
    Returns:
        Dictionary with detailed coverage metrics and recommendations
    """
    logger.info("Calculating detailed coverage metrics")
    
    coverage_summary = coverage_validation.get("coverage_summary", {})
    coverage_details = coverage_validation.get("coverage_details", {})
    uncovered_units = coverage_validation.get("uncovered_units", {})
    
    overall_coverage = coverage_summary.get("overall_coverage", 0)
    
    # Determine coverage status
    if overall_coverage >= 100.0:
        status = "complete"
        recommendation = "Coverage target achieved. Ready for Stage 2."
    elif overall_coverage >= 90.0:
        status = "excellent" 
        recommendation = "Near-complete coverage. Consider proceeding to Stage 2."
    elif overall_coverage >= 80.0:
        status = "good"
        recommendation = "Good coverage achieved. Minor gaps remain."
    elif overall_coverage >= 60.0:
        status = "moderate"
        recommendation = "Moderate coverage. Significant gaps need attention."
    else:
        status = "insufficient"
        recommendation = "Insufficient coverage. Major improvements needed."
    
    # Identify priority improvement areas
    improvement_areas = []
    
    uncovered_functions = uncovered_units.get("functions", [])
    if uncovered_functions:
        improvement_areas.append({
            "type": "functions",
            "count": len(uncovered_functions),
            "items": uncovered_functions[:5],  # Show first 5
            "priority": "high"
        })
    
    uncovered_methods = uncovered_units.get("methods", [])
    if uncovered_methods:
        improvement_areas.append({
            "type": "methods",
            "count": len(uncovered_methods),
            "items": uncovered_methods[:5],  # Show first 5
            "priority": "high"
        })
    
    uncovered_classes = uncovered_units.get("classes", [])
    if uncovered_classes:
        improvement_areas.append({
            "type": "classes",
            "count": len(uncovered_classes),
            "items": uncovered_classes[:5],  # Show first 5
            "priority": "medium"
        })
    
    result = {
        "overall_status": status,
        "coverage_percentage": overall_coverage,
        "recommendation": recommendation,
        "meets_target": overall_coverage >= 100.0,
        "improvement_areas": improvement_areas,
        "metrics_breakdown": coverage_summary,
        "gap_analysis": {
            "total_gaps": coverage_details.get("uncovered_units", 0),
            "critical_gaps": len(uncovered_functions) + len(uncovered_methods),
            "minor_gaps": len(uncovered_classes)
        }
    }
    
    logger.info(f"Coverage metrics calculated: {status} status with {overall_coverage:.2f}% coverage")
    
    return result
