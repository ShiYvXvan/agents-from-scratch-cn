# 第 06 课 - Agent Loop

## 我们在回答什么问题？

**"这如何变成一个 agent，而不仅仅是一个聊天机器人？"**

答案：当它能**观察、决策、行动并重复**时，并且带有状态。聊天机器人回复一次就停止了。agent 则朝着目标执行多个步骤。

## 你将构建什么

一个 agent loop，它能够：
- 按顺序运行多个步骤
- 跨步骤维护状态
- 基于当前状态决定动作
- 在达到目标或超过最大步数时终止

## 引入的新概念

### 1. Agent Loop

**agent loop** 是重复的循环：观察、决策、行动。在每次迭代中，agent 查看当前情况，决定要做什么，执行该动作，并重复直到完成。

这就是 agent 与简单聊天机器人的区别——agent 不会在一条回复后就停止。

### 2. 状态转换

**状态转换**追踪 agent 的状态如何随着每一步而变化。状态可能包括步数计数、完成状态、累积结果或其他追踪信息。

状态让 loop 感知到自己的进度和历史。

### 3. 终止条件

**终止条件**决定 loop 何时停止。常见的条件包括：
- agent 判定自己"完成"了
- 达到最大步数
- 目标已达成
- 发生错误

没有终止条件，loop 会永远运行下去。

## 我们（暂时）不做什么

- 不跨 loop 使用记忆（[第 07 课](07_memory.md)）
- 不使用规划（[第 08 课](08_planning.md)）
- 不使用复杂的推理——只是简单的逐步决策

## 代码

查看 `agent/agent.py`，找到 `agent_step()` 和 `run_loop()` 方法：

```python
def agent_step(self, user_input: str) -> dict | None:
    """
    Execute one step of the agent loop: observe, decide, act.
    
    Lesson 06 version.
    
    Args:
        user_input: User's input or system observation
        
    Returns:
        Action decision or None if step failed
    """
    state_dict = self.state.to_dict()
    
    prompt = f"""{self.system_prompt}

You are an agent. You must decide the next action and respond with ONLY valid JSON.

Current state: steps={state_dict.get('steps', 0)}, done={state_dict.get('done', False)}

Available actions: analyze, research, summarize, answer, done

CRITICAL INSTRUCTIONS:
1. Respond with ONLY valid JSON
2. No explanations, no markdown, no other text
3. Start your response with {{ and end with }}

Required JSON format:
{{"action": "action_name", "reason": "explanation"}}

User input: {user_input}

Response (JSON only):"""
    
    for attempt in range(3):
        response = self.llm.generate(prompt, temperature=0.0)
        parsed = extract_json_from_text(response)
        
        if parsed and "action" in parsed:
            if "reason" not in parsed:
                parsed["reason"] = f"Taking action: {parsed['action']}"
            self.state.increment_step()
            return parsed
    
    return None

def run_loop(self, user_input: str, max_steps: int = 5):
    """
    Run the agent loop for multiple steps.
    
    Args:
        user_input: Initial user input
        max_steps: Maximum number of steps to execute
        
    Returns:
        List of action results
    """
    self.state.reset()
    results = []
    
    while not self.state.done and self.state.steps < max_steps:
        action = self.agent_step(user_input)
        
        if action:
            results.append(action)
            
            # Simple termination condition
            if action.get("action") == "done":
                self.state.mark_done()
        else:
            break
    
    return results
```

注意：
- **状态追踪** - 每一步递增步数计数器并检查完成状态
- **Loop 结构** - `while not done` 持续直到终止
- **动作累积** - 跨步骤收集结果
- **安全限制** - `max_steps` 防止无限 loop

## 如何运行

查看 `complete_example.py`，找到 `lesson_06_agent_loop()` 方法：

```python
from agent.agent import Agent

agent = Agent("models/llama-3-8b-instruct.gguf")

print("\nNote: Repetition in early iterations is expected.")
print("The agent refines its understanding step by step and may repeat analysis")
print("before converging on a clearer explanation.\n")

results = agent.run_loop("Help me understand loops", max_steps=3)

for i, result in enumerate(results, 1):
    print(f"Iteration {i}:")
    action = result.get("action", "unknown")
    reason = result.get("reason", "No reason provided")
    print(f"  Action: {action}")
    print(f"  Reason: {reason}")
    if i < len(results):
        print()
```

输出展示了每次迭代的动作和原因。请注意，早期迭代中的重复是预期行为——agent 会逐步完善自己的理解。

## 与第 05 课对比

**第 05 课（工具调用）：**
```
Request -> Tool call -> Result -> Done
```
单次交互：请求、执行、返回。

**第 06 课（Agent Loop）：**
```
Input -> Step 1 -> Step 2 -> Step 3 -> Done
          |        |        |
        Action   Action   Action
```
多个步骤按顺序执行，每一步决定下一步做什么。

![Agent Loop 流程](diagrams/lesson-06-agent-loop.png)

## 关键洞见

### Agent 不是一个聪明的 Prompt

Agent 不是一个聪明的 prompt。它是一个**带有状态的 loop**。魔法不在 prompt 里——而在于重复的观察、决策和行动循环。

### 状态实现了连续性

没有状态，每一步都是独立的。有了状态，步骤可以相互承接，并追踪朝着目标的进展。

### 终止至关重要

始终要有终止条件。没有它们，loop 可能永远运行或消耗不必要的资源。`max_steps` 是一个简单但必不可少的安全机制。

### 简单更好

这个 loop 刻意保持简单。复杂的推理可以以后再来——首先，建立重复行动的模式。

## 常见问题

**"loop 永远运行"**
- 检查终止条件是否正确设置
- 验证 `max_steps` 是否在生效
- 确保 agent 能够发出"done"的信号

**"每一步看起来都是独立的"**
- 在 prompt 中包含状态信息
- 将累积的结果传递给后续步骤
- 让决策制定过程能够看到状态

**"agent 没有取得进展"**
- 检查动作是否真的改变了什么
- 验证状态是否被正确更新
- 确保 agent 能够看到相关的状态信息

## 练习

1. 修改可用动作，观察 loop 如何适应
2. 更改 `max_steps`，观察它如何影响行为
3. 添加步数计数之外的状态变量
4. 尝试不同的终止条件

## 接下来是什么？

在[第 07 课](07_memory.md)中，我们将添加**记忆**，使 agent 能够在多次交互之间记住信息，而不仅仅是在单个 loop 内。

---

**核心要点：** Agent = loop + 状态。仅此而已。loop 实现了多步行为，状态实现了连续性。