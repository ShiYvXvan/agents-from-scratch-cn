# 第 01 课 - 与模型对话

## 我们在回答什么问题？

**"我到底该怎么跟一个语言模型对话？"**

这是最基础的一步。在构建 agent 之前，我们需要理解最简单的交互形式：文本输入，文本输出。

## 你将构建什么

一个最简交互，它将：
- 加载一个本地 LLM
- 向它发送文本
- 接收返回的文本

仅此而已。没有魔法。没有框架。只有基础。

## 引入的新概念

### 1. Prompt

**prompt** 就是你发送给模型的文本。它可以是一个问题（比如"什么是 AI agent？"）、一条指令（比如"解释量子计算"）、或者一个请求（比如"写一首关于海洋的诗"）。模型会基于它在训练中学到的模式来补全或回应这段文本。

### 2. Token

模型并不是把文本当作词语来看——它们看到的是 **token**。token 是文本片段（通常是单词或子词）。例如，"Hello world" 可能是 2 个 token，而 "artificial intelligence" 根据模型不同可能是 2 到 4 个 token。

这一点很重要，因为模型有 token 限制（context window），生成速度以每秒 token 数来衡量，更长的 prompt 会消耗更多的 token，留给回复的空间就更少。

### 3. Context

**context** 是模型一次能"看到"的全部内容。它包括你的 prompt、之前的对话以及系统指令。模型有一个 **context window**（例如 2048 个 token）。如果你超过了这个限制，模型就看不到更早的文本了。

## 我们（暂时）不做什么

- 不使用 system prompt（[第 02 课](02_system_prompt.md)）
- 不使用结构化输出（[第 03 课](03_structured_output.md)）
- 不使用工具（[第 05 课](05_tools.md)）
- 不使用 agent（[第 06 课](06_agent_loop.md)）
- 不使用记忆（[第 07 课](07_memory.md)）

本课刻意保持最简。

## 代码

查看 `agent/agent.py`，找到 `simple_generate()` 方法：

```python
def simple_generate(self, user_input: str) -> str:
    """
    Simplest possible interaction - just pass text to the LLM.
    """
    return self.llm.generate(user_input)
```

就是这样。一行代码。没有任何复杂性。

## 如何运行

查看 `complete_example.py`，找到 `lesson_01_basic_chat()` 方法：

```python
from agent.agent import Agent

agent = Agent("models/llama-3-8b-instruct.gguf")

response = agent.simple_generate("What is an AI agent?")
print(response)
```

## 内部发生了什么？

1. 你的文本被转换成 token
2. token 被发送给模型
3. 模型预测下一个 token
4. 重复直到满足停止条件（结束 token、最大长度等）
5. token 被转换回文本
6. 文本返回给你

## 关键洞见

### 并不存在"理解"

模型并不"理解"你的问题。相反，它识别 token 中的模式，预测可能的延续，并生成概率性的文本。这很重要：**模型是模式匹配器，不是思维体。**

### 它是概率性的

对同一个 prompt 运行两次，你可能会得到不同的回复。这是因为模型在生成时使用了随机性（temperature），并且存在多个合理的延续可能。不存在唯一"正确"的答案——只有概率性的输出。

### 文本输入 = 文本输出

仅此而已。我们之后构建的一切（agent、工具、记忆）都是建立在这个简单基础之上的。

## 常见问题

**"回复被截断了"**
- 在 `shared/llm.py` 中增大 `max_tokens`

**"模型在自我重复"**
- 这对补全模型来说是正常现象
- 我们将在[第 02 课](02_system_prompt.md)中通过更好的 prompt 来解决

**"回复与 prompt 不匹配"**
- 有些模型需要特定格式
- 我们将在[第 02 课](02_system_prompt.md)和[第 03 课](03_structured_output.md)中添加结构化

## 练习

1. 尝试不同的 prompt，观察回复的变化
2. 在 `shared/llm.py` 中修改 `temperature`（0.0 = 确定性，1.0 = 创造性）
3. 使用 `max_tokens` 控制回复长度

## 接下来是什么？

在[第 02 课](02_system_prompt.md)中，我们将添加 **system prompt** 来塑造模型的行为。这将把随机的文本补全转变为一致、有用的回复。

---

**核心要点：** LLM 只是一个文本补全引擎。我们构建的一切都是与这个简单机制的结构化交互。
