# 第 04 课 - 使用 LLM 做决策

## 我们在回答什么问题？

**"模型能决定做什么，而不仅仅是回答问题吗？"**

这是**自主性**的第一个时刻。模型不再回复生成的文本，而是从一组有限的选项中做出选择。

## 你将构建什么

一个决策系统，它能够：
- 向模型呈现一组有限的选项
- 强制模型恰好选择一个选项
- 验证决策并在失败时重试
- 使用决策来路由执行

## 引入的新概念

### 1. 决策 Schema

**决策 schema** 是模型必须从中选择的一组有限选项。模型不再生成自由文本，而是从预定义的动作中进行选择，比如"answer_question"、"summarize_text"或"translate"。

这极大地约束了输出空间——与其有无限多种可能的回复，不如只有少数几个有效选项。

### 2. 路由逻辑

一旦做出决策，你的代码可以根据决策来**路由**执行。如果模型选择了"summarize_text"，你就调用摘要函数。如果它选择了"translate"，你就调用翻译函数。

这就是 agent 如何根据它们"决定"要做的事情走不同路径。

### 3. 意图检测

通过将用户输入框定为一个决策问题，你就是在做**意图检测**。模型分析用户想要什么，并将其映射到你可用的动作之一。

这比试图解析自由文本来理解意图要简单得多。

## 我们（暂时）不做什么

- 不使用工具（[第 05 课](05_tools.md)）
- 不使用 agent loop（[第 06 课](06_agent_loop.md)）
- 不使用记忆（[第 07 课](07_memory.md)）
- 不使用规划（[第 08 课](08_planning.md)）

## 代码

查看 `agent/agent.py`，找到 `decide()` 方法：

```python
def decide(self, user_input: str, choices: list[str]) -> str | None:
    """
    Make the model choose from a finite set of options.
    
    Lesson 04 version.
    
    Args:
        user_input: The input to make a decision about
        choices: List of possible actions/decisions
        
    Returns:
        The chosen action or None if decision failed
    """
    options = "\n".join(f"- {choice}" for choice in choices)
    
    prompt = f"""{self.system_prompt}

You must choose ONE of the following options. Respond with ONLY valid JSON.

CRITICAL INSTRUCTIONS:
1. Respond with ONLY valid JSON
2. No explanations, no markdown, no other text
3. Start your response with {{ and end with }}

Available choices:
{options}

Required JSON format:
{{"decision": "one_of_the_choices_above"}}

User request: {user_input}

Response (JSON only):"""
    
    for attempt in range(3):
        response = self.llm.generate(prompt, temperature=0.0)
        parsed = extract_json_from_text(response)
        
        if parsed and "decision" in parsed:
            decision = parsed["decision"]
            if decision in choices:
                return decision
    
    return None
```

注意我们添加了：
- **有限的选项空间** - 模型必须从预定义的列表中选择，不能生成任何东西
- **验证** - 我们检查决策是否确实在选项列表中
- **结构化输出** - 使用与第 03 课相同的 JSON 提取模式
- **重试逻辑** - 最多 3 次尝试以获得有效的决策

## 如何运行

查看 `complete_example.py`，找到 `lesson_04_decisions()` 方法：

```python
from agent.agent import Agent

agent = Agent("models/llama-3-8b-instruct.gguf")

decision = agent.decide(
    "Can you summarize this article for me?",
    choices=["answer_question", "summarize_text", "translate"]
)

print(decision)
# Output: "summarize_text"
```

## 与第 03 课对比

**第 03 课（结构化输出）：**
```
Input: "What is AI?"
Output: {"answer": "AI is...", "confidence": "high"}
```
模型生成的结构化数据中包含它自己创建的值。

**第 04 课（决策制定）：**
```
Input: "Summarize this article"
Choices: ["answer_question", "summarize_text", "translate"]
Output: "summarize_text"
```
模型从预定义的选项中选择——不是生成，只是选择。

## 关键洞见

### 选择 vs 生成

模型不再生成内容——它在**从有限的动作空间中进行选择**。这与自由文本生成有着根本性的不同，并且可预测得多。

### 自主性从这里开始

这是 agent 开始有"agent 的感觉"的地方。它不再只是回复——它在选择做什么。这些选择可能很简单，但这种模式很重要。

### 约束 = 可靠

通过将选项限制在一个小而明确的集合中，你让系统更加可靠。模型无法幻觉出新的动作——它必须从你的列表中选择。

### 验证至关重要

始终验证决策是否确实在你的选项列表中。模型可能返回看起来像决策但不在你允许集合中的内容。

## 常见问题

**"模型返回了不在我列表中的选项"**
- 对照选项列表进行验证（代码已经做了这一点）
- 使你的选项名称清晰且无歧义
- 考虑添加带有更明确指令的重试

**"所有决策看起来都是随机的"**
- 检查你的选项在语义上是否不同
- 确保用户输入确实与选项相关
- 进一步降低 temperature 以获得更确定性的选择

**"模型添加了解释"**
- `extract_json_from_text()` 辅助函数可以处理这个
- 更强的指令有助于处理（代码中已经有了）
- 考虑拒绝带有额外文本的回复

## 练习

1. 创建一个包含 5+ 个选项的决策并测试不同的输入
2. 尝试模糊的输入，看看模型选择哪个选项
3. 添加一个"none_of_the_above"选项，观察它何时被选择
4. 比较 temperature 0.0 与 0.5 时的决策

## 接下来是什么？

在[第 05 课](05_tools.md)中，我们将引入**工具**——agent 可以请求的能力，以超越文本生成的范围。

---

**核心要点：** 决策 = 自主性。agent 做出选择，而不仅仅是回复。约束选项使行为变得可预测。