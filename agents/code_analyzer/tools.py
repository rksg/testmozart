import ast
from typing import Any, Dict, List, Union

# This class is a visitor that walks the Abstract Syntax Tree (AST) of the Python code.
class CodeVisitor(ast.NodeVisitor):
    """
    Visits nodes in an AST to extract information about classes and functions.
    """
    def __init__(self):
        self.structure: List[Dict[str, Any]] = []
        self._class_stack = []  # Track nested classes

    def visit_ClassDef(self, node: ast.ClassDef):
        """Called when the visitor finds a class definition."""
        class_info = {
            "type": "class",
            "name": node.name,
            "docstring": ast.get_docstring(node),
            "methods": []
        }
        
        # Add to class stack to track we're inside a class
        self._class_stack.append(node.name)
        
        # Iterate through the body of the class to find method definitions
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_info = self._get_function_details(item)
                class_info["methods"].append(method_info)
        
        self.structure.append(class_info)
        
        # Remove from class stack when leaving the class
        self._class_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """
        Called when the visitor finds a function definition.
        Only processes top-level functions (not methods inside classes).
        """
        # Only add functions that are not inside any class
        if not self._class_stack:
            func_info = self._get_function_details(node)
            func_info["type"] = "function"
            self.structure.append(func_info)

    def _get_function_details(self, node: ast.FunctionDef) -> Dict[str, Any]:
        """Helper to extract details from any function or method node."""
        return {
            "name": node.name,
            "docstring": ast.get_docstring(node),
            "parameters": [
                {
                    "name": arg.arg,
                    # ast.unparse is a clean way to get the string representation of a type hint
                    "annotation": ast.unparse(arg.annotation) if arg.annotation else None
                }
                for arg in node.args.args
            ],
            "return_type": ast.unparse(node.returns) if node.returns else None
        }

def analyze_code_structure(source_code: str, language: str) -> Dict[str, Any]:
    """
    Parses source code into a structured JSON representation of its AST.
    
    This tool provides a detailed breakdown of classes, methods, function signatures,
    parameters, type hints, return types, and docstrings.
    
    Args:
        source_code: The source code to be analyzed as a string.
        language: The programming language of the source code (e.g., 'python', 'java').
        
    Returns:
        A JSON-serializable dictionary representing the code structure.
    """
    if language.lower() == 'python':
        try:
            print(f"Analyzing Python code structure...{source_code[:500]}...")  # Print first 30 chars for context
            tree = ast.parse(source_code)
            visitor = CodeVisitor()
            visitor.visit(tree)
            return {"status": "success", "structure": visitor.structure}
        except SyntaxError as e:
            return {"status": "error", "message": f"Python syntax error: {e}"}
    
    elif language.lower() == 'java':
        # Placeholder for Java parsing logic using a library like javalang or py-javaparser
        raise NotImplementedError("Java code analysis is not yet implemented.")
    
    else:
        return {"status": "error", "message": f"Unsupported language: {language}"}

