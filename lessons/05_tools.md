# 第 05 课 - 引入工具

## 我们在回答什么问题？

**"模型能让我做某件事吗？"**

工具扩展了 agent 的能力，超越了文本生成。agent 不再只能生成文本，而是可以请求执行计算、API 调用或文件操作等动作。

## 你将构建什么

一个工具调用系统，它能够：
- 让 agent 用结构化的参数请求特定工具
- 在执行之前验证工具请求
- 将工具请求与工具执行分离
- 无需重新训练模型即可扩展 agent 的能力

## 引入的新概念

### 1. 工具接口

**工具接口**是 agent 可以请求的已定义的 API。工具有名称和参数，比如 `calculator(a, b, operation)`。agent 请求工具，但由系统来执行它。

这种分离至关重要——agent **描述**它需要什么，但你**控制**实际发生什么。

### 2. 结构化的工具调用

工具调用是函数调用的**结构化 JSON 规范**。模型输出 JSON 如 `{"tool": "calculator", "arguments": {"a": 42, "b": 7, "operation": "multiply"}}`，而你的代码负责验证和执行。

这与第 04 课的决策制定类似，但 agent 不是在选择一个动作，而是在指定一个函数调用。

### 3. 模型选择的动作

agent 决定**使用哪个工具**以及**传递什么参数**。你定义可用的工具，但 agent 选择哪个适合当前情况。

这就是自主性在发挥作用——agent 在选择和配置动作。

## 重要规则

模型**请求**工具。系统**执行**它们。目前还没有自主权。这种分离为你提供了控制权和安全性。

## 我们（暂时）不做什么

- 不使用 agent loop（[第 06 课](06_agent_loop.md)）
- 不使用记忆（[第 07 课](07_memory.md)）
- 不自动执行工具——你仍然手动执行工具调用

## 代码

查看 `agent/agent.py`，找到 `request_tool()` 方法：

```python
def request_tool(self, user_input: str) -> dict | None:
    """
    Have the model request a tool call.
    
    Lesson 05 version.
    
    Args:
        user_input: The user's request
        
    Returns:
        Tool call specification or None if request failed
    """
    prompt = f"""{self.system_prompt}

You are a tool-calling assistant. When asked a math question, you must respond with ONLY valid JSON.

Available tool: calculator
- Parameters: a (number), b (number), operation ("add", "subtract", "multiply", or "divide")

CRITICAL INSTRUCTIONS:
1. Respond with ONLY valid JSON
2. No explanations, no markdown, no other text
3. Start your response with {{ and end with }}

Example format:
{{"tool": "calculator", "arguments": {{"a": 42, "b": 7, "operation": "multiply"}}}}

User request: {user_input}

Response (JSON only):"""
    
    for attempt in range(3):
        response = self.llm.generate(prompt, temperature=0.0)
        parsed = extract_json_from_text(response)
        
        if parsed and "tool" in parsed and "arguments" in parsed:
            return parsed
    
    return None

def execute_tool_call(self, tool_call: dict) -> Any:
    """
    Execute a tool call requested by the model.
    
    Args:
        tool_call: Dictionary with "tool" and "arguments"
        
    Returns:
        Result of the tool execution
    """
    return execute_tool(tool_call["tool"], tool_call["arguments"])
```

注意：
- **结构化输出** - 工具调用是经过验证的 JSON，与第 03 课类似
- **验证** - 我们检查 "tool" 和 "arguments" 是否都存在
- **关注点分离** - 请求和执行是分开的方法
- **可扩展性** - 轻松添加新工具而无需更改模型

## 如何运行

查看 `complete_example.py`，找到 `lesson_05_tools()` 方法：

```python
from agent.agent import Agent

agent = Agent("models/llama-3-8b-instruct.gguf")

tool_call = agent.request_tool("What is 42 * 7?")
print(f"Tool request: {tool_call}")

if tool_call:
    result = agent.execute_tool_call(tool_call)
    print(f"Tool result: {result}")
```

![工具调用流程](diagrams/lesson-05-tool-calling.png)

## 与第 04 课对比

**第 04 课（决策制定）：**
```
Input: "What should I do?"
Choices: ["answer", "calculate", "translate"]
Output: "calculate"
```
agent 从一个动作列表中进行选择。

**第 05 课（工具调用）：**
```
Input: "What is 42 * 7?"
Tool: calculator
Arguments: {"a": 42, "b": 7, "operation": "multiply"}
Result: 294
```
agent 指定带参数的工具调用并获取结果。

## 关键洞见

### 工具是接口，而不是能力

agent 并不拥有这个能力——你才有。agent 通过结构化接口描述它需要什么，而你提供实现。这让你保持控制权。

### 不需要重新训练

要添加新的能力，你只需添加新的工具。模型不需要重新训练——它只需要理解工具接口。这非常强大。

### 通过分离实现安全性

通过将工具请求与执行分离，你可以验证、记录和控制实际发生的事。agent 无法在没有你的代码允许的情况下执行危险操作。

### 结构化 = 可靠

使用与第 03 和 04 课相同的结构化 JSON 模式，使工具调用变得可靠且可解析。模型输出结构化数据，你验证它，然后执行。

## 常见问题

**"模型请求了一个不存在的工具"**
- 对照你可用的工具验证工具名称
- 在 prompt 中提供可用工具的清晰示例
- 优雅地处理无效的工具名称

**"参数类型错误"**
- 在执行之前验证参数类型
- 在工具描述中明确期望的类型
- 考虑对复杂工具使用 schema 验证

**"模型在应该请求工具的时候没有请求"**
- 明确说明何时应该使用工具
- 在 prompt 中提供示例
- 考虑对某些请求类型强制使用工具

## 练习

1. 添加一个新工具（例如"weather"或"search"）并测试它
2. 尝试无效的工具调用，看看验证如何处理它们
3. 修改工具接口，观察模型如何适应
4. 创建具有不同参数类型的工具（字符串、数字、布尔值）

## 接下来是什么？

在[第 06 课](06_agent_loop.md)中，我们将创建 **agent loop**——将决策制定和工具调用组合成一个重复的循环。

---

**核心要点：** 工具调用 = 无需重新训练即可扩展能力。工具是你控制的接口，而不是 agent 拥有的能力。