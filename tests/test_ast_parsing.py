#!/usr/bin/env python3
"""
Test AST parsing directly.
"""

import ast
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_ast_parsing():
    """Test AST parsing directly."""
    print("🧪 Testing AST Parsing Directly")
    print("=" * 40)
    
    # Read sample code
    with open("sample_code.py", "r") as f:
        sample_code = f.read()
    
    print(f"📄 Code length: {len(sample_code)} characters")
    
    # Parse AST
    try:
        tree = ast.parse(sample_code)
        print("✅ AST parsing successful")
        
        # Walk the tree manually
        functions = []
        classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)
        
        print(f"📊 Found {len(functions)} functions: {functions}")
        print(f"📊 Found {len(classes)} classes: {classes}")
        
        # Test the CodeVisitor
        print("\n🔍 Testing CodeVisitor...")
        from agents.code_analyzer.tools import CodeVisitor
        
        visitor = CodeVisitor()
        visitor.visit(tree)
        
        print(f"📋 Visitor found {len(visitor.structure)} items:")
        for item in visitor.structure:
            print(f"  - {item['type']}: {item['name']}")
            if item['type'] == 'class' and 'methods' in item:
                for method in item['methods']:
                    print(f"    - method: {method['name']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ast_parsing()
