# 第 08 课  -  规划即数据（而非思想）

## 我们要回答什么问题？

**"Agent 如何解决多步骤任务？"**

复杂任务需要多个步骤。规划将目标分解为一系列可以逐步执行的动作。

## 你将构建什么

一个规划系统，具备以下功能：
- 从目标生成逐步计划
- 将规划与执行分离
- 将计划存储为数据结构
- 按顺序执行计划

## 引入的新概念

### 1. 规划 vs 执行

**规划**是生成实现目标所需的步骤。**执行**是实际执行这些步骤。将它们分开后，你可以：
- 在执行前检查计划
- 在需要时修改计划
- 独立调试规划和执行

这种分离非常强大——你可以在 Agent "认为"它应该做的事情实际执行之前看到它。

### 2. 步骤排序

**步骤排序**决定了动作的顺序。步骤之间可能存在依赖关系（步骤 2 需要步骤 1 的输出），也可能是独立的。

目前，我们按顺序执行步骤。后面的课程将更明确地处理依赖关系。

### 3. 验证

**验证**在执行前检查计划。计划是有效的 JSON 吗？它是否具有所需的结构？步骤是否合理？

验证计划能在浪费时间执行之前捕获错误。

## 我们（目前）不做什么

- 没有依赖处理（[第 10 课](10_atom_of_thought.md)）
- 没有原子动作验证（[第 09 课](09_atomic_actions.md)）
- 没有并行执行——步骤按顺序运行

## 代码

查看 `agent/agent.py`，参见 `create_plan()` 和 `execute_plan()` 方法：

```python
def create_plan(self, goal: str) -> dict | None:
    """
    Generate a plan to achieve a goal.
    
    Lesson 08 version.
    
    Args:
        goal: The goal to achieve
        
    Returns:
        Plan with steps
    """
    plan = create_plan(self.llm, goal)
    
    if plan:
        self.state.current_plan = plan
    
    return plan

def execute_plan(self, plan: dict) -> list:
    """
    Execute a plan step by step.
    
    Args:
        plan: Plan dictionary with "steps" list
        
    Returns:
        List of execution results
    """
    if not plan or "steps" not in plan:
        return []
    
    results = []
    
    for step in plan["steps"]:
        # Simple execution - in reality you'd call tools, etc.
        result = {
            "step": step,
            "executed": True
        }
        results.append(result)
        self.state.increment_step()
    
    return results
```

以及 `agent/planner.py` 中的规划器实现：

```python
def create_plan(llm: LocalLLM, goal: str) -> dict | None:
    """
    Generate a plan to achieve a goal.
    
    Used in: Lesson 08
    
    Args:
        llm: The language model to use
        goal: The goal to achieve
        
    Returns:
        Plan as a dictionary with a "steps" list, or None if generation failed
    """
    from shared.utils import extract_json_from_text
    
    prompt = f"""Create a step-by-step plan to achieve the goal. Respond with ONLY valid JSON.

CRITICAL INSTRUCTIONS:
1. Respond with ONLY valid JSON
2. No explanations, no markdown, no other text
3. Start your response with {{ and end with }}

Required JSON format:
{{"steps": ["step1", "step2", "step3"]}}

Goal: {goal}

Response (JSON only):"""
    
    for attempt in range(3):
        response = llm.generate(prompt, temperature=0.0)
        plan = extract_json_from_text(response)
        
        if plan and "steps" in plan and isinstance(plan["steps"], list):
            return plan
    
    return None
```

注意以下几点：
- **结构化输出**——计划是 JSON 数据结构
- **验证**——我们检查计划是否具有预期结构
- **重试逻辑**——多次尝试以获取有效计划
- **简单执行**——步骤按顺序执行（实际的执行逻辑在后面课程中）

## 如何运行

查看 `complete_example.py`，参见 `lesson_08_planning()` 方法：

```python
from agent.agent import Agent

agent = Agent("models/llama-3-8b-instruct.gguf")

plan = agent.create_plan("Write a blog post about AI agents")
print(f"Plan: {plan}")

if plan:
    results = agent.execute_plan(plan)
    print(f"Execution results: {results}")
```

## 与第 07 课对比

**第 07 课（记忆）：**
```
用户: "我叫 Alice" -> 保存到记忆
用户: "我叫什么名字？" -> 从记忆中检索
```
存储和检索事实。

**第 08 课（规划）：**
```
目标: "写文章" -> 计划: ["调研", "大纲", "撰写", "审阅"]
计划 -> 执行每个步骤 -> 结果
```
生成并执行一系列步骤。

![规划流程](diagrams/lesson-08-planning.png)

## 关键洞察

### 计划不是思想

计划不是思想——它们是**数据结构**。这使得它们可检查、可修改且安全。你可以在执行前查看、编辑和验证它们。

### 规划 = 数据生成

规划不是复杂的推理——它是结构化的数据生成。模型生成一个步骤列表，就像生成任何其他结构化输出一样。

### 分离的阶段

将规划与执行分离让你能够：
- 在不执行的情况下调试计划
- 在运行之前修改计划
- 为类似目标重用计划
- 独立测试规划

### 简单执行

目前，执行很简单——只是遍历步骤。后面的课程将添加更复杂的执行，包括依赖关系和验证。

## 常见问题

**"计划太模糊"**
- 使目标更具体
- 在 prompt 中提供良好计划的示例
- 考虑分解过于笼统的目标

**"步骤顺序错误"**
- 模型决定顺序——如有必要请验证
- 考虑添加依赖关系信息
- 如有必要，在执行前检查并重新排序步骤

**"执行没有做任何事情"**
- 本课的执行是一个占位符
- 在实践中，你会调用工具或其他函数
- 模式比实现更重要

## 练习

1. 为不同类型的目标生成计划
2. 在执行前手动修改计划
3. 比较多轮运行中同一目标的计划
4. 尝试验证计划的完整性

## 接下来是什么？

在[第 09 课](09_atomic_actions.md)中，我们将通过将计划步骤转换为带有验证模式的**原子动作**，使执行更加安全。

---

**核心要点：** 规划 = 数据生成，而非推理。计划是可检查的数据结构，能够实现多步骤执行。
