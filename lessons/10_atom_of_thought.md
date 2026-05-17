# 第 10 课  -  AoT（思维原子）  -  现在一切都说得通了

## 我们要回答什么问题？

**"如何在不失去控制的情况下扩展规划？"**

复杂任务需要许多具有依赖关系的动作。有些动作可以并行运行，其他动作必须等待。AoT（思维原子）创建依赖图，使复杂工作流能够安全、高效地执行。

## 你将构建什么

一个 AoT 系统，具备以下功能：
- 创建带有节点和依赖关系的依赖图
- 在执行前验证图结构
- 在遵守依赖关系的前提下执行动作
- 支持独立动作的并行执行

## 引入的新概念

### 1. 原子规划

**原子规划**意味着将计划创建为依赖图，其中每个节点都是一个原子动作。节点可以依赖其他节点，从而创建显式的执行顺序。

这是第 08 课的规划和第 09 课的原子动作的自然结合，并增加了依赖跟踪。

### 2. 依赖解析

**依赖解析**确定正确的执行顺序。没有依赖的动作可以立即运行。有依赖的动作等待其依赖完成。

这使得独立动作能够并行执行，同时遵守排序约束。

### 3. 验证执行

**验证执行**意味着在运行之前检查图结构。所有依赖关系都有效吗？是否存在循环依赖？所有必需节点都存在吗？

验证在开始执行前捕获结构错误。

## 代码

查看 `agent/planner.py`，参见 `create_aot_graph()` 函数：

```python
def create_aot_graph(llm: LocalLLM, goal: str) -> dict | None:
    """
    Generate an AoT execution graph.
    
    Used in: Lesson 10
    
    Args:
        llm: The language model to use
        goal: The goal to achieve
        
    Returns:
        AoT graph with nodes and dependencies, or None if generation failed
    """
    from shared.utils import extract_json_from_text
    
    prompt = f"""Create an execution graph to achieve the goal. Respond with ONLY valid JSON.

CRITICAL INSTRUCTIONS:
1. Respond with ONLY valid JSON
2. No explanations, no markdown, no other text
3. Start your response with {{ and end with }}

Required JSON format:
{{
  "nodes": [
    {{"id": "1", "action": "action_name", "depends_on": []}},
    {{"id": "2", "action": "action_name", "depends_on": ["1"]}}
  ]
}}

Each node must have:
- "id": unique identifier (string)
- "action": what to do (string)
- "depends_on": list of node IDs that must complete first (list of strings)

Goal: {goal}

Response (JSON only):"""
    
    for attempt in range(3):
        response = llm.generate(prompt, temperature=0.0)
        graph = extract_json_from_text(response)
        
        if graph and "nodes" in graph and isinstance(graph["nodes"], list):
            # Validate node structure
            node_ids = set()
            for node in graph["nodes"]:
                if "id" not in node or "action" not in node or "depends_on" not in node:
                    break
                node_ids.add(node["id"])
            else:
                # All nodes valid, check dependencies reference valid nodes
                for node in graph["nodes"]:
                    for dep in node.get("depends_on", []):
                        if dep not in node_ids:
                            break
                    else:
                        continue
                    break
                else:
                    return graph
    
    return None
```

以及 `agent/agent.py` 中：

```python
def create_aot_plan(self, goal: str) -> dict | None:
    """
    Generate an AoT execution graph.
    
    Lesson 10 version.
    
    Args:
        goal: The goal to achieve
        
    Returns:
        AoT graph with atomic nodes and dependencies
    """
    return create_aot_graph(self.llm, goal)

def execute_aot_plan(self, graph: dict) -> list:
    """
    Execute an AoT graph respecting dependencies.
    
    Args:
        graph: AoT graph
        
    Returns:
        List of execution results
    """
    def execute_action(action: str):
        # Placeholder for actual action execution
        return f"Executed: {action}"
    
    return execute_graph(graph, execute_action)
```

注意以下几点：
- **图结构**——节点带有 ID、动作和依赖关系
- **验证**——检查所有依赖关系是否引用有效节点
- **依赖解析**——`execute_graph` 函数处理排序
- **可扩展性**——以后很容易添加并行执行

## 如何运行

查看 `complete_example.py`，参见 `lesson_10_aot()` 方法：

```python
from agent.agent import Agent

agent = Agent("models/llama-3-8b-instruct.gguf")

graph = agent.create_aot_plan("Research and write article")
print(f"AoT graph: {graph}")

if graph:
    results = agent.execute_aot_plan(graph)
    print(f"Execution results: {results}")
```

![思维原子图](diagrams/lesson-10-atom-of-thoght.png)

## 与第 09 课对比

**第 09 课（原子动作）：**
```
步骤 -> 原子动作: {"action": "...", "inputs": {...}}
```
单个步骤转换为原子动作。

**第 10 课（AoT）：**
```
目标 -> 图: {
  nodes: [
    {id: "1", action: "...", depends_on: []},
    {id: "2", action: "...", depends_on: ["1"]}
  ]
}
```
多个原子动作带有显式依赖关系。

## 关键洞察

### AoT 是必然的

到此为止，AoT 感觉是**必然的**，而不是高级的。它是规划（第 08 课）、原子动作（第 09 课）和添加依赖关系的自然演化。一旦你理解了各个组成部分，图结构就完全说得通了。

### 这不是高级推理

AoT 不是更聪明的思考——它是**更好的结构**：
- 每个节点都经过验证（来自第 09 课）
- 依赖关系是显式的（本课新增）
- 执行是确定性的（遵守顺序）
- 故障被限制在范围内（到单个节点）

### 结构支撑规模

通过添加依赖关系，你可以处理包含许多动作的复杂工作流。依赖关系可以实现：
- 独立动作的并行执行
- 清晰的执行顺序
- 更容易的调试（知道什么依赖什么）

### 验证是关键

图结构必须在执行前验证。循环依赖、缺失节点或无效引用必须及早捕获。

## 常见问题

**"循环依赖"**
- 验证应该捕获此问题
- 检查依赖关系是否形成有向无环图（DAG）
- 考虑在验证中添加循环检测

**"依赖关系引用了不存在的节点"**
- 验证会检查此问题
- 确保依赖关系中的所有节点 ID 都存在于图中
- 考虑更系统地生成 ID

**"执行顺序看起来有问题"**
- 验证依赖关系是否正确指定
- 检查 `execute_graph` 是否遵守依赖关系
- 考虑添加执行日志以查看顺序

## 练习

1. 创建具有不同依赖结构的图
2. 尝试创建循环依赖，看验证是否能捕获它
3. 比较有无依赖关系的执行顺序
4. 尝试并行执行 vs 顺序执行

## 最终洞察

你现在已经构建了一个具备以下能力的 Agent：
1. 与 LLM 对话（[第 01 课](01_basic_llm_chat.md)）
2. 具有一致的行为（[第 02 课](02_system_prompt.md)）
3. 产生经过验证的输出（[第 03 课](03_structured_output.md)）
4. 做出决策（[第 04 课](04_decision_making.md)）
5. 使用工具（[第 05 课](05_tools.md)）
6. 循环运行（[第 06 课](06_agent_loop.md)）
7. 记住事物（[第 07 课](07_memory.md)）
8. 规划动作（[第 08 课](08_planning.md)）
9. 安全执行（[第 09 课](09_atomic_actions.md)）
10. 通过依赖关系扩展（[第 10 课](10_atom_of_thought.md)）

而且你**完全理解这一切是如何运作的**。没有魔法，没有隐藏的推理——只有结构、验证和显式执行。

---

**核心要点：** AoT 是结构，不是魔法。Agent 是系统，不是心智。依赖图使得复杂工作流成为可能，同时保持控制和可预测性。
