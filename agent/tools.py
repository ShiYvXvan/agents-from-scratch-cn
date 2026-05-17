"""
Agent 的工具定义。

工具是 API，不是能力。
Agent 请求工具；系统执行工具。
"""

from typing import Any


def calculator(a: float, b: float, operation: str = "add") -> float:
    """
    简单的计算器工具。

    Args:
        a: 第一个数字
        b: 第二个数字
        operation: 可选值为 "add"、"subtract"、"multiply"、"divide"

    Returns:
        运算结果
    """
    operations = {
        "add": lambda x, y: x + y,
        "subtract": lambda x, y: x - y,
        "multiply": lambda x, y: x * y,
        "divide": lambda x, y: x / y if y != 0 else float('inf'),
    }

    if operation not in operations:
        raise ValueError(f"Unknown operation: {operation}")

    return operations[operation](a, b)


def get_tool_schema() -> dict:
    """
    获取可用工具的 schema。

    这是 agent 在决定调用哪个工具时看到的内容。

    Returns:
        工具名称到其 schema 的字典映射
    """
    return {
        "calculator": {
            "description": "Perform basic arithmetic operations",
            "parameters": {
                "a": {"type": "number", "description": "First number"},
                "b": {"type": "number", "description": "Second number"},
                "operation": {
                    "type": "string",
                    "enum": ["add", "subtract", "multiply", "divide"],
                    "description": "The operation to perform"
                }
            },
            "required": ["a", "b"]
        }
    }


def execute_tool(tool_name: str, arguments: dict) -> Any:
    """
    按名称使用给定的参数执行一个工具。

    Args:
        tool_name: 要执行的工具名称
        arguments: 工具的参数字典

    Returns:
        工具执行的结果

    Raises:
        ValueError: 如果工具不存在
    """
    tools = {
        "calculator": calculator,
    }

    if tool_name not in tools:
        raise ValueError(f"Unknown tool: {tool_name}")

    return tools[tool_name](**arguments)
