# 第 03 课 - 让输出变得可靠

## 我们在回答什么问题？

**"我该如何停止解析自由文本？"**

自由文本的回复是不可预测的。有时模型会添加解释，有时使用不同的格式，有时会产生幻觉。我们需要**结构化**。

## 你将构建什么

一个系统，它能够：
- 强制 JSON 输出
- 验证回复
- 失败时重试

## 引入的新概念

### 1. 输出契约

**输出契约**是对模型必须返回内容的规范。我们不再说"回答问题"，而是说"返回与此 schema 匹配的 JSON"。

```json
{
  "answer": string,
  "confidence": "high" | "medium" | "low"
}
```

### 2. 信任边界

永远不要直接信任 LLM 的输出。始终要：
1. 解析它
2. 验证它
3. 处理失败情况

这是第一个"工程化"时刻——将 LLM 视为一个可能出错的组件来对待。

### 3. 验证

验证确保输出符合你的契约：
- 它是有效的 JSON 吗？
- 它包含必需的字段吗？
- 值的类型是否正确？

## 代码

查看 `agent/agent.py`，找到 `generate_structured()` 方法：

```python
def generate_structured(self, user_input: str, schema: str) -> dict | None:
    """
    Generate structured JSON output with validation and retries.
    
    Lesson 03 version.
    
    Args:
        user_input: The user's question or request
        schema: JSON schema description
        
    Returns:
        Parsed JSON dictionary or None if all retries failed
    """
    prompt = f"""{self.system_prompt}

CRITICAL INSTRUCTIONS:
1. Respond with ONLY valid JSON
2. No explanations, no markdown, no extra text before or after the JSON
3. Start your response with {{ and end with }}

Schema you must follow:
{schema}

User request: {user_input}

Response (JSON only):"""
    
    # Try up to 3 times
    for attempt in range(3):
        response = self.llm.generate(prompt, temperature=0.0)
        parsed = extract_json_from_text(response)
        
        if parsed is not None:
            return parsed
    
    return None
```

注意我们添加了：
- **强指令** - "CRITICAL INSTRUCTIONS"加上明确的 JSON-only 要求
- **Temperature 控制** - `temperature=0.0` 以获得更确定性、更一致的输出
- **JSON 提取** - `extract_json_from_text()` 处理模型添加额外文本的情况
- **重试逻辑** - 最多 3 次尝试以获得有效的 JSON，将概率性行为转变为可靠的结果

## 如何运行

查看 `complete_example.py`，找到 `lesson_03_structured()` 方法：

```python
from agent.agent import Agent

agent = Agent("models/llama-3-8b-instruct.gguf")

schema = '''
{
  "topic": string,
  "difficulty": "beginner" | "intermediate" | "advanced"
}
'''

result = agent.generate_structured(
    "Explain quantum computing",
    schema
)

print(result)
# {"topic": "'quantum computing", "difficulty": "advanced"}
```

## 为什么这很重要

### 之前（自由文本）
```
Output: "Okay! This task is medium difficulty. I'd suggest building..."
```
- 无法解析
- 不一致
- 不可靠

### 之后（结构化）
```
Output: {'topic': 'quantum computing', 'difficulty': 'advanced'}
```
- 可解析
- 可预测
- 已验证

## 关键洞见

### LLM 是概率性的

它们并不总是在第一次尝试时就输出有效的 JSON。重试将概率性行为转变为可靠行为。

### 结构胜过聪明

一个带有验证的简单 prompt 胜过没有验证的聪明 prompt。

### 这是工程化

你将 LLM 视为系统中的一个组件：
- 输入：prompt + schema
- 输出：经过验证的数据或错误
- 重试：如果验证失败则重试

## 常见问题

**"模型在 JSON 之前添加了解释"**
- 使用 `extract_json_from_text()` 辅助函数（在文本中查找 JSON）
- 在 prompt 中强调"ONLY valid JSON"

**"仍然收到无效的回复"**
- 降低 temperature 以获得更确定性的输出
- 对 schema 进行更具体的说明
- 使用经过结构化输出训练的模型

**"重试消耗了太多 token"**
- 3 次重试通常足够了
- 跟踪重试次数以监控模型质量

## 接下来是什么？

在[第 04 课](04_decision_making.md)中，我们添加**决策制定**——模型选择行动，而不仅仅是回答问题。

---

**核心要点：** 结构化输出 + 验证 = 可靠的 agent。