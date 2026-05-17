# 第 07 课  -  记忆（短期与长期）

## 我们要回答什么问题？

**"Agent 如何记住事物？"**

Agent 需要在多次交互中记住信息。没有记忆，每次对话都从零开始。记忆让 Agent 能够基于之前的对话继续构建，并保持上下文。

## 你将构建什么

一个记忆系统，具备以下功能：
- 跨交互存储事实
- 在需要时检索相关记忆
- 将记忆集成到 Agent 的上下文中
- 允许显式管理记忆

## 引入的新概念

### 1. 上下文 vs 记忆

**上下文**是当前 prompt 中的内容——模型此刻能看到的一切。**记忆**是持久化存储，能够在多次交互之间保留。

上下文是临时的。记忆是持久的。记忆在需要时被加载到上下文中。

### 2. 持久化

**持久化**意味着跨轮次保存事实。当用户说"我叫 Alice"时，这个事实应该被存储起来，并在未来的交互中可用。

没有持久化，Agent 在每次交互后就会忘记一切。

### 3. 检索

**检索**是在需要时获取相关记忆。当用户问"我叫什么名字？"时，Agent 从记忆中检索到"用户的名字是 Alice"，并用它来回答。

简单的检索可能意味着"获取所有记忆"。更复杂的检索会根据当前查询找到相关记忆。

## 我们（目前）不做什么

- 没有规划（[第 08 课](08_planning.md)）
- 没有复杂的记忆检索——只是简单的"获取全部"检索
- 没有记忆衰减或优先级排序

## 代码

查看 `agent/agent.py`，参见 `run_with_memory()` 方法：

```python
def run_with_memory(self, user_input: str) -> dict | None:
    """
    Run agent with memory context.
    
    Lesson 07 version.
    
    Args:
        user_input: User's input
        
    Returns:
        Response with potential memory update
    """
    memory_context = self.memory.get_all()
    
    # Build memory context string
    if memory_context:
        memory_str = "You remember the following:\n" + "\n".join(f"- {item}" for item in memory_context)
    else:
        memory_str = "You have no memories yet."
    
    prompt = f"""{self.system_prompt}

You are an agent with memory. You must respond with ONLY valid JSON.

{memory_str}

CRITICAL INSTRUCTIONS:
1. Respond with ONLY valid JSON
2. No explanations, no markdown, no other text
3. Start your response with {{ and end with }}
4. If the user tells you information (like their name), save it to memory
5. If the user asks about something you remember, USE YOUR MEMORY to answer

Required JSON format:
{{"reply": "your response text", "save_to_memory": "fact to remember" or null}}

Examples:
- User says "My name is Alice" -> {{"reply": "Nice to meet you, Alice!", "save_to_memory": "User's name is Alice"}}
- User asks "What's my name?" and you remember "User's name is Alice" -> {{"reply": "Your name is Alice", "save_to_memory": null}}

User input: {user_input}

Response (JSON only):"""
    
    for attempt in range(3):
        response = self.llm.generate(prompt, temperature=0.0)
        parsed = extract_json_from_text(response)
        
        if parsed and "reply" in parsed:
            # Save to memory if requested
            if parsed.get("save_to_memory"):
                self.memory.add(parsed["save_to_memory"])
            
            self.state.increment_step()
            return parsed
    
    return None
```

注意以下几点：
- **记忆检索**——`memory.get_all()` 加载所有已存储的记忆
- **上下文集成**——记忆被包含在 prompt 中
- **显式存储**——Agent 通过 JSON 明确说明要保存什么
- **自动持久化**——当提供 `save_to_memory` 时，它会自动被存储

## 如何运行

查看 `complete_example.py`，参见 `lesson_07_memory()` 方法：

```python
from agent.agent import Agent

agent = Agent("models/llama-3-8b-instruct.gguf")

# First interaction - store name
response1 = agent.run_with_memory("My name is Alice")
if response1 and "reply" in response1:
    print(f"Response 1: {response1['reply']}")

# Second interaction - recall name
response2 = agent.run_with_memory("What's my name?")
if response2 and "reply" in response2:
    print(f"Response 2: {response2['reply']}")

print(f"Memory contents: {agent.memory.get_all()}")
```

![记忆系统](diagrams/lesson-07-memory.png)

## 与第 06 课对比

**第 06 课（Agent 循环）：**
```
循环 -> 步骤 1 -> 步骤 2 -> 步骤 3 -> 完成
         |         |        |
       动作      动作     动作
```
状态在循环内持久存在，但循环结束后重置。

**第 07 课（记忆）：**
```
交互 1 -> 保存 "名字是 Alice" -> 记忆存储它
交互 2 -> 加载记忆 -> "你的名字是 Alice"
```
记忆在完全独立的交互之间持久存在。

## 关键洞察

### 记忆是显式存储

记忆是**显式存储**，而不是意识。它是你可以检查、修改和删除的数据。没有隐藏的推理——只有已存储的事实。

### 简单即强大

这个记忆系统很简单：存储字符串，检索全部。然而它非常有用。更复杂的检索可以以后再做，但这个基础已经可以工作了。

### Agent 控制存储

Agent 通过 `save_to_memory` 字段决定保存什么。你可以自动化这个过程，但显式控制能保持事物的可预测性。

### 上下文加载

记忆被加载到 prompt 上下文中。模型不能直接访问记忆——它只能看到你在 prompt 中包含的内容。

## 常见问题

**"Agent 不保存信息"**
- 检查响应中是否包含 `save_to_memory`
- 验证 `memory.add()` 是否被调用
- 确保 prompt 清楚地说明了何时保存

**"Agent 忘记了事情"**
- 验证记忆是否被加载到了 prompt 中
- 检查记忆在调用之间是否持久存在
- 确保记忆上下文字符串被包含在内

**"记忆变得太大"**
- 这个简单系统会永远存储所有记忆
- 考虑添加记忆限制或删除功能
- 更复杂的系统可以优先排序或总结记忆

## 练习

1. 保存多个事实，观察它们如何累积
2. 尝试询问记忆中不存在的内容
3. 手动检查 `agent.memory.get_all()` 以查看存储的数据
4. 修改记忆格式，观察它如何影响行为

## 接下来是什么？

在[第 08 课](08_planning.md)中，我们将添加**规划**——将复杂目标分解为一系列步骤的能力。

---

**核心要点：** 记忆 = 数据存储，而非思想。它是显式的、可检查的，并为 Agent 提供了跨交互的连续性。
