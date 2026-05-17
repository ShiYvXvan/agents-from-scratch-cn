# 第 02 课 - 为模型赋予角色

## 我们在回答什么问题？

**"为什么同一个模型会有不同的行为？"**

你可能已经注意到，LLM 可以扮演不同的角色——技术专家、创意作家、乐于助人的助手。这是如何做到的？

## 你将构建什么

一个使用 **system prompt** 的脚本，用于：
- 为模型分配一个特定角色
- 稳定模型的行为
- 控制语气和格式

## 引入的新概念

### 1. System Prompt

**system prompt** 是一条塑造模型回复方式的指令。就像在对话之前给某人分配角色一样。

示例 system prompt：
```
"You are a calm, precise teacher who explains concepts simply."
```

```
"You are a creative writer who uses vivid imagery."
```

```
"You are a code reviewer who finds bugs and suggests improvements."
```

### 2. 指令层级

大多数模型理解以下层级关系：
1. **System prompt** - 整体行为和角色
2. **User prompt** - 实际的问题或请求

system prompt 具有更高的"优先级"——它引导模型如何解释 user prompt。

### 3. 行为塑造

行为 != 智能。行为 = 指令。

同一个模型可以：
- 技术化或随意化（语气）
- 冗长或简洁（长度）
- 创造性或事实性（风格）

这一切都取决于 system prompt。

## 我们（暂时）不做什么

- 不使用结构化输出（[第 03 课](03_structured_output.md)）
- 不使用决策（[第 04 课](04_decision_making.md)）
- 不使用工具（[第 05 课](05_tools.md)）
- 不使用记忆（[第 07 课](07_memory.md)）

## 代码

查看 `agent/agent.py`，找到 `generate_with_role()` 方法：

```python
def generate_with_role(self, user_input: str) -> str:
    """
    Generate with a system prompt to shape behavior.
    """
    # Use a format that doesn't confuse the model
    prompt = f"""{self.system_prompt}

User: {user_input}
Assistant:"""
    
    response = self.llm.generate(prompt)
    # Clean up any potential tag artifacts
    response = response.replace('<SYSTEM>', '').replace('</SYSTEM>', '')
    response = response.replace('<USER>', '').replace('</USER>', '')
    return response.strip()
```

注意我们添加了：
- 在开头加入 system prompt
- 对话使用简单的 "User:" / "Assistant:" 格式
- 清理代码，移除可能出现的标签残留

## 如何运行

查看 `complete_example.py`，找到 `lesson_02_with_role()` 方法：

```python
from agent.agent import Agent

agent = Agent("models/llama-3-8b-instruct.gguf")

# The agent has a default system prompt:
# "You are a calm, precise, and helpful AI assistant..."

response = agent.generate_with_role("What is an AI agent?")
print(response)
```

## 与第 01 课对比

**不使用 system prompt（[第 01 课](01_basic_llm_chat.md)）：**
```
Input: "What is an AI agent?"
Output: "An AI agent is a system that perceives its environment and acts autonomously to achieve specified goals. It processes information, makes decisions, and can adapt to changing conditions using machine learning algorithms..."
```

**使用 system prompt：**
```
Input: "What is an AI agent?"
Output: "Think of an AI agent as a helpful assistant that can observe what's happening around it and take actions to help you accomplish tasks. Like how a thermostat watches the temperature and adjusts heating automatically - but much more sophisticated."
```

相同的问题。相同的模型。不同的行为。

## System Prompt 的力量

### 示例 1：技术专家
```python
agent.system_prompt = "You are a senior software engineer who explains concepts with code examples."
```

### 示例 2：ELI5（像我 5 岁一样解释）
```python
agent.system_prompt = "You explain complex topics using simple words and everyday analogies."
```

### 示例 3：简洁回复者
```python
agent.system_prompt = "You give accurate answers in 1-2 sentences maximum. No elaboration unless asked."
```

## 关键洞见

### 行为是可配置的

你并没有改变模型——你改变的是对其输出的**约束**。模型仍然在预测 token；system prompt 只是改变了概率分布。

### 一致性得到提升

没有 system prompt 时，模型可能会：
- 这一次很正式，下一次很随意
- 有时冗长，有时简略
- 语气不一致

system prompt 创造了**行为的一致性**。

### 仍然是概率性的

即使有了 system prompt，回复仍然会有所不同。但它们是在你设定的**约束范围内**变化的。

## 常见的 System Prompt 模式

### 1. 角色定义
```
You are a [role] who [behavior].
```

### 2. 约束设置
```
You must [requirement]. You never [prohibition].
```

### 3. 输出格式
```
Always respond with [format]. Use [style].
```

### 4. 组合使用
```
You are a helpful assistant. 
You explain concepts clearly using examples.
You keep responses under 100 words unless asked to elaborate.
```

## 常见问题

**"模型忽略了我的 system prompt"**
- 有些模型比其他模型更好地遵循 system prompt
- 尝试更明确和具体
- 使用更强烈的措辞（"You MUST..."而不是"Try to..."）

**"回复仍然不一致"**
- 这是正常的——LLM 是概率性的
- 降低 `temperature` 以获得更多一致性
- 我们将在[第 03 课](03_structured_output.md)中添加验证

**"system prompt 太长了"**
- 保持在 100-200 词以内
- 更多 token = 留给用户输入和回复的空间更少

## 练习

1. 尝试不同的 system prompt，观察行为变化
2. 创建一个让回复极其简洁的 system prompt
3. 创建一个让回复非常详细的 system prompt
4. 尝试冲突的指令（哪个会胜出？）

## 接下来是什么？

在[第 03 课](03_structured_output.md)中，我们将添加**结构化输出**，让回复变得可靠且可解析。我们将获得经过验证的 JSON，而不是自由文本。

---

**核心要点：** 行为不是智能，而是约束。system prompt 将一个通用模型转变为一个特定助手。