"""Coverage Analysis Tools

This module provides tools for calculating test coverage metrics.
"""

import ast
import re
import logging
from typing import Dict, List, Set, Any

# Set up logging
logger = logging.getLogger(__name__)

class CoverageAnalyzer:
    """Analyzes code coverage from source code and test scenarios."""
    
    def __init__(self):
        self.functions = set()
        self.classes = set()
        self.methods = {}  # class_name -> [method_names]
        
    def extract_testable_units(self, source_code: str) -> Dict[str, Any]:
        """Extract all testable units from source code."""
        logger.info("Extracting testable units from source code")
        
        try:
            tree = ast.parse(source_code)
            self._visit_node(tree)
            
            result = {
                "functions": list(self.functions),
                "classes": list(self.classes),
                "methods": dict(self.methods),
                "total_units": len(self.functions) + len(self.classes) + sum(len(methods) for methods in self.methods.values())
            }
            
            logger.info(f"Found {result['total_units']} testable units: {len(self.functions)} functions, {len(self.classes)} classes, {sum(len(methods) for methods in self.methods.values())} methods")
            return result
            
        except SyntaxError as e:
            logger.error(f"Syntax error in source code: {e}")
            return {"error": f"Syntax error: {e}"}
    
    def _visit_node(self, node):
        """Visit AST nodes to extract testable units."""
        if isinstance(node, ast.FunctionDef):
            # Top-level function
            if not hasattr(node, '_parent_class'):
                self.functions.add(node.name)
                logger.debug(f"Found function: {node.name}")
        
        elif isinstance(node, ast.ClassDef):
            self.classes.add(node.name)
            self.methods[node.name] = []
            logger.debug(f"Found class: {node.name}")
            
            # Find methods in this class
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    self.methods[node.name].append(item.name)
                    logger.debug(f"Found method: {node.name}.{item.name}")
        
        # Continue visiting child nodes
        for child in ast.iter_child_nodes(node):
            self._visit_node(child)

def calculate_coverage(source_code: str, test_scenarios: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Calculate test coverage based on source code and test scenarios.
    
    Args:
        source_code: The source code to analyze
        test_scenarios: List of test scenarios with description and expected_outcome
        
    Returns:
        Coverage analysis results
    """
    logger.info("Starting coverage calculation")
    
    # Extract testable units
    analyzer = CoverageAnalyzer()
    testable_units = analyzer.extract_testable_units(source_code)
    
    if "error" in testable_units:
        return testable_units
    
    # Analyze test scenario coverage
    covered_functions = set()
    covered_classes = set()
    covered_methods = {}
    
    for scenario in test_scenarios:
        description = scenario.get('description', '').lower()
        
        # Simple pattern matching to identify what's being tested
        # Look for function names
        for func_name in testable_units['functions']:
            if func_name.lower() in description or f"'{func_name}'" in description:
                covered_functions.add(func_name)
                logger.debug(f"Scenario covers function: {func_name}")
        
        # Look for class and method names
        for class_name, methods in testable_units['methods'].items():
            if class_name.lower() in description or f"'{class_name}'" in description:
                covered_classes.add(class_name)
                logger.debug(f"Scenario covers class: {class_name}")
            
            for method_name in methods:
                if method_name.lower() in description or f"'{method_name}'" in description:
                    if class_name not in covered_methods:
                        covered_methods[class_name] = set()
                    covered_methods[class_name].add(method_name)
                    logger.debug(f"Scenario covers method: {class_name}.{method_name}")
    
    # Calculate coverage percentages
    function_coverage = len(covered_functions) / len(testable_units['functions']) if testable_units['functions'] else 1.0
    class_coverage = len(covered_classes) / len(testable_units['classes']) if testable_units['classes'] else 1.0
    
    total_methods = sum(len(methods) for methods in testable_units['methods'].values())
    covered_methods_count = sum(len(methods) for methods in covered_methods.values())
    method_coverage = covered_methods_count / total_methods if total_methods > 0 else 1.0
    
    # Overall coverage (weighted average)
    total_testable = len(testable_units['functions']) + len(testable_units['classes']) + total_methods
    total_covered = len(covered_functions) + len(covered_classes) + covered_methods_count
    overall_coverage = total_covered / total_testable if total_testable > 0 else 1.0
    
    # Identify gaps
    uncovered_functions = set(testable_units['functions']) - covered_functions
    uncovered_classes = set(testable_units['classes']) - covered_classes
    uncovered_methods = {}
    for class_name, methods in testable_units['methods'].items():
        covered_for_class = covered_methods.get(class_name, set())
        uncovered_for_class = set(methods) - covered_for_class
        if uncovered_for_class:
            uncovered_methods[class_name] = list(uncovered_for_class)
    
    result = {
        "coverage_summary": {
            "overall_coverage": round(overall_coverage * 100, 2),
            "function_coverage": round(function_coverage * 100, 2),
            "class_coverage": round(class_coverage * 100, 2),
            "method_coverage": round(method_coverage * 100, 2)
        },
        "covered_units": {
            "functions": list(covered_functions),
            "classes": list(covered_classes),
            "methods": {k: list(v) for k, v in covered_methods.items()}
        },
        "uncovered_units": {
            "functions": list(uncovered_functions),
            "classes": list(uncovered_classes),
            "methods": uncovered_methods
        },
        "testable_units": testable_units,
        "meets_threshold": overall_coverage >= 0.8  # 80% threshold
    }
    
    logger.info(f"Coverage calculation complete. Overall coverage: {result['coverage_summary']['overall_coverage']}%")
    return result
