"""Test the smart improvement coordinator logic."""

import sys
import os

# Add the project root to the sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.smart_improvement_coordinator.tools import analyze_improvement_needs

print("🧪 测试智能改进协调器")
print("=" * 50)

# Test case 1: Syntax error scenario
print("\n测试1: 语法错误场景")
syntax_error_instructions = {
    "needs_improvement": True,
    "execution_issues": [
        {
            "issue": "critical_execution_failure",
            "severity": "critical",
            "description": "Test code has syntax errors"
        }
    ],
    "coverage_gaps": [],
    "quality_issues": []
}

result1 = analyze_improvement_needs(syntax_error_instructions, 1)
print(f"✅ 动作类型: {result1['action_type']}")
print(f"✅ 跳过场景生成: {result1['skip_scenario_generation']}")
print(f"✅ 跳过测试实现: {result1['skip_implementation']}")
print(f"✅ 原因: {result1['reason']}")

assert result1['action_type'] == 'fix_execution'
assert result1['skip_scenario_generation'] is True
assert result1['skip_implementation'] is False
print("✅ 语法错误测试通过！")

# Test case 2: Coverage gap scenario
print("\n测试2: 覆盖率缺口场景")
coverage_gap_instructions = {
    "needs_improvement": True,
    "execution_issues": [],
    "coverage_gaps": [
        {
            "unit": "some_function",
            "type": "Function",
            "gap": "Not covered by tests"
        }
    ],
    "quality_issues": []
}

result2 = analyze_improvement_needs(coverage_gap_instructions, 1)
print(f"✅ 动作类型: {result2['action_type']}")
print(f"✅ 跳过场景生成: {result2['skip_scenario_generation']}")
print(f"✅ 跳过测试实现: {result2['skip_implementation']}")
print(f"✅ 原因: {result2['reason']}")

assert result2['action_type'] == 'improve_coverage'
assert result2['skip_scenario_generation'] is False
assert result2['skip_implementation'] is False
print("✅ 覆盖率缺口测试通过！")

# Test case 3: No improvement needed
print("\n测试3: 无需改进场景")
no_improvement_instructions = {
    "needs_improvement": False,
    "execution_issues": [],
    "coverage_gaps": [],
    "quality_issues": []
}

result3 = analyze_improvement_needs(no_improvement_instructions, 1)
print(f"✅ 动作类型: {result3['action_type']}")
print(f"✅ 跳过场景生成: {result3['skip_scenario_generation']}")
print(f"✅ 跳过测试实现: {result3['skip_implementation']}")
print(f"✅ 原因: {result3['reason']}")

assert result3['action_type'] == 'none'
assert result3['skip_scenario_generation'] is True
assert result3['skip_implementation'] is True
print("✅ 无需改进测试通过！")

print("\n" + "=" * 50)
print("🎉 所有测试通过！智能协调器逻辑正确。")
print("✅ 语法错误时将跳过场景重新生成")
print("✅ 覆盖率问题时将重新生成场景")
print("✅ 无问题时将跳过所有改进步骤")
