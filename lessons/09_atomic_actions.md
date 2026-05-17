# 第 09 课  -  原子步骤与安全执行

## 我们要回答什么问题？

**"如何让计划变得既安全又可预测？"**

像"写文章"这样的计划步骤是模糊的，难以验证。原子动作将步骤分解为最小的、定义明确的操作，使其可以被安全地验证和执行。

## 你将构建什么

一个原子动作系统，具备以下功能：
- 将模糊的计划步骤转换为具体的、有类型的动作
- 在执行前验证动作
- 使用模式确保参数正确
- 使执行变得可预测且可调试

## 引入的新概念

### 1. 原子性

**原子性**意味着将动作分解为尽可能小的单元。不是"写文章"，而是得到带有具体参数（如主题和长度）的 `generate_text`。

原子动作是不可分割的——它们要么完全成功，要么完全失败，不存在部分状态。

### 2. 确定性

**确定性**意味着可预测的结果。给定相同的原子动作和相同的输入，你应该得到相似的结果（考虑到 LLM 的随机性）。

原子动作通过消除歧义使执行变得具有确定性。

### 3. 类型化执行

**类型化执行**意味着动作具有经过验证的模式。每个动作指定：
- 动作名称（例如 `generate_text`）
- 所需输入（例如 `{"topic": string, "length": string}`）
- 验证规则

这在执行前捕获错误。

## 我们（目前）不做什么

- 没有动作间的依赖处理（[第 10 课](10_atom_of_thought.md)）
- 没有并行执行
- 没有动作执行实现——只是转换和验证

## 代码

查看 `agent/planner.py`，参见 `create_atomic_action()` 函数：

```python
def create_atomic_action(llm: LocalLLM, step: str) -> dict | None:
    """
    Convert a plan step into an atomic action.
    
    Used in: Lesson 09
    
    Args:
        llm: The language model to use
        step: A step from a plan
        
    Returns:
        Atomic action as a dictionary, or None if generation failed
    """
    from shared.utils import extract_json_from_text
    
    prompt = f"""Convert this step into an atomic action. Respond with ONLY valid JSON.

CRITICAL INSTRUCTIONS:
1. Respond with ONLY valid JSON
2. No explanations, no markdown, no other text
3. Start your response with {{ and end with }}

Required JSON format:
{{
  "action": "action_name",
  "inputs": {{"key": "value"}}
}}

The action should be a simple, atomic operation name.
The inputs should be a dictionary with the parameters needed for this action.

Step to convert:
{step}

Response (JSON only):"""
    
    for attempt in range(3):
        response = llm.generate(prompt, temperature=0.0)
        action = extract_json_from_text(response)
        
        if action and "action" in action:
            return action
    
    return None
```

以及 `agent/agent.py` 中：

```python
def create_atomic_action(self, step: str) -> dict | None:
    """
    Convert a plan step into an atomic action.
    
    Lesson 09 version.
    
    Args:
        step: A step from a plan (e.g., "Write an explanation of AI agents")
        
    Returns:
        Atomic action dictionary with "action" and "inputs", or None if generation failed
    """
    return create_atomic_action(self.llm, step)
```

注意以下几点：
- **步骤转换**——模糊的步骤变成带有参数的具体动作
- **模式验证**——动作必须具有 `action` 和 `inputs` 字段
- **结构化输出**——使用与前几课相同的 JSON 模式
- **重试逻辑**——多次尝试以获取有效的原子动作

## 如何运行

查看 `complete_example.py`，参见 `lesson_09_atomic_actions()` 方法：

```python
from agent.agent import Agent

agent = Agent("models/llama-3-8b-instruct.gguf")

# Convert a plan step into an atomic action
step = "Write an explanation of AI agents"
atomic_action = agent.create_atomic_action(step)
print(f"Step: {step}")
print(f"Atomic action: {atomic_action}")

# Example with a step from a plan
plan = agent.create_plan("Create a tutorial about Python")
if plan and "steps" in plan and plan["steps"]:
    first_step = plan["steps"][0]
    atomic_action_from_plan = agent.create_atomic_action(first_step)
    print(f"\nPlan step: {first_step}")
    print(f"Atomic action from plan step: {atomic_action_from_plan}")
```

## 与第 08 课对比

**第 08 课（规划）：**
```
目标 -> 计划: ["调研主题", "创建大纲", "撰写草稿"]
```
计划是模糊步骤描述的列表。

**第 09 课（原子动作）：**
```
步骤: "撰写草稿" -> 原子: {"action": "generate_text", "inputs": {"topic": "...", "length": "..."}}
```
步骤变成具有已验证参数的具体有类型动作。

## 关键洞察

### 小步骤 = 安全系统

动作越小，系统越安全。原子动作：
- 更容易验证——你可以在执行前检查参数
- 更容易测试——每个动作都可以独立测试
- 更容易调试——故障被隔离到具体动作
- 更难发生灾难性故障——小动作的影响范围有限

### 模糊 vs 具体

"写文章"是模糊的。`generate_text(topic='AI agents', length='1000 words')` 是具体的。具体性使验证和可预测执行成为可能。

### 验证发生在早期

通过在执行前验证动作，你能及早捕获错误。带有无效动作的计划可以在任何工作完成之前被拒绝。

### 构建模块

原子动作是构建模块。复杂的工作流由许多简单的原子动作构建而成，每个都经过验证且安全。

## 常见问题

**"原子动作仍然模糊"**
- 在 prompt 中提供更清晰的指示
- 给出良好原子动作的示例
- 考虑将动作名称限制在预定义的集合中

**"验证失败"**
- 检查动作是否同时具有 `action` 和 `inputs` 字段
- 验证 JSON 结构是否正确
- 考虑为 inputs 添加模式验证

**"转换失败"**
- 某些步骤可能无法清晰地映射到原子动作
- 考虑多次重试（已实现）
- 提供更多关于什么是良好原子动作的上下文

## 练习

1. 将不同类型的计划步骤转换为原子动作
2. 比较相似步骤的原子动作
3. 尝试在执行前验证原子动作
4. 尝试不同的输入参数结构

## 接下来是什么？

在[第 10 课](10_atom_of_thought.md)中，我们将结合规划、原子动作和**依赖关系**，创建能够按正确顺序甚至并行执行动作的执行图。

---

**核心要点：** 小步骤 = 安全系统。原子动作通过将模糊计划分解为具体的、经过验证的操作，使执行变得可预测、可调试且安全。
