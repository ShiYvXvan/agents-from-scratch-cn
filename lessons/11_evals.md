# 第 11 课 - Evals（Agent 的回归测试）

## 我们要回答什么问题？

**"当我做出更改后，如何知道我的 Agent 仍然能正常工作？"**

一旦你有了工具、记忆和结构化输出，更改 prompt 就变得有风险。一个小小的措辞变化就可能破坏 JSON 解析。一个"改进"可能让工具调用变得不那么可靠。没有 evals，质量会悄然下降。

一个 eval 套件只是一个 Python 文件，它运行你的 Agent 并断言一切没有被破坏。

## 你将构建什么

一个评估系统，具备以下功能：
- 测试 prompt 和 JSON 解析的可靠性
- 验证工具调用准确性
- 检查记忆存储和检索循环
- 在部署前捕获回归

## 引入的新概念

### 1. Eval 套件

**Eval 套件**是验证 Agent 行为的测试用例集合。每个用例有一个输入和一个预期结果。你在每次更改 prompt 后运行该套件。

这并不神奇——只是用已知输入运行你的 Agent 并检查输出。

### 2. 黄金数据集

**黄金数据集**是你的事实来源——必须始终通过的已知良好示例。如果黄金用例失败，Agent 就坏了（而不是测试坏了）。

黄金数据集与你的 prompt 一起受版本控制。当你更改 prompt 时，你运行黄金数据集来验证没有东西被破坏。

### 3. 硬断言 vs 软断言

**硬断言**必须始终通过：
- JSON 必须有效
- 必需字段必须存在
- 工具名称必须匹配可用工具

**软断言**通常应该通过：
- 答案在语义上是正确的
- 措辞合适
- 工具参数是最优的

从硬断言开始。软断言以后再说。

## 为什么这在现实世界中会失败

一个改进措辞的 prompt 更改可能：
- 增加冗长程度
- 将 JSON 推出上下文窗口
- 破坏解析
- ……而不改变正确性

这就是 evals 存在的原因。它们能捕获这些静默的失败。

## 我们（目前）不做什么

- 没有运行时监控（[第 12 课](12_telemetry.md)）
- 没有 A/B 测试
- 没有生产可观测性
- 没有 LLM-as-judge evals（目前太复杂）

## 代码

查看 `agent/evals.py`：

```python
from dataclasses import dataclass, field
from typing import Any


@dataclass
class EvalResult:
    """Result of a single eval case."""
    passed: bool
    input: str
    expected: Any = None
    actual: Any = None
    error: str | None = None


@dataclass 
class EvalSuiteResult:
    """Result of running an eval suite."""
    name: str
    passed: int = 0
    failed: int = 0
    results: list[EvalResult] = field(default_factory=list)
    
    @property
    def pass_rate(self) -> float:
        return self.passed / (self.passed + self.failed) if (self.passed + self.failed) > 0 else 0.0
    
    def summary(self) -> str:
        status = "✓ PASSED" if self.failed == 0 else "✗ FAILED"
        return f"{self.name}: {status} ({self.passed}/{self.passed + self.failed})"


class AgentEval:
    """Regression testing for agent capabilities."""
    
    def __init__(self, agent):
        self.agent = agent
    
    def test_structured_output(self, cases: list[dict]) -> EvalSuiteResult:
        """Test that structured output parses correctly and matches schema."""
        suite = EvalSuiteResult(name="Structured Output")
        
        for case in cases:
            result = self.agent.generate_structured(case["input"], case["schema"])
            
            # Check 1: Did we get valid JSON?
            if result is None:
                suite.add_result(EvalResult(
                    passed=False,
                    input=case["input"],
                    error="Failed to parse JSON"
                ))
                continue
            
            # Check 2: Are required fields present?
            missing = [f for f in case.get("must_have_fields", []) if f not in result]
            if missing:
                suite.add_result(EvalResult(
                    passed=False,
                    input=case["input"],
                    error=f"Missing fields: {missing}"
                ))
                continue
            
            suite.add_result(EvalResult(passed=True, input=case["input"], actual=result))
        
        return suite
```

注意以下几点：
- **纯 Python**——不需要测试框架
- **结构化结果**——每个结果捕获输入、预期值、实际值、错误
- **可组合**——运行一个套件或多个套件
- **可操作**——失败告诉你具体出了什么问题

## 黄金数据集

查看 `evals/golden_datasets.py`：

```python
STRUCTURED_OUTPUT_GOLDEN = [
    {
        "input": "Explain quantum computing in one sentence",
        "schema": """{
  "topic": "the topic name as a string",
  "difficulty": "beginner" or "intermediate" or "advanced"
}

Example: {"topic": "machine learning", "difficulty": "intermediate"}""",
        "must_have_fields": ["topic", "difficulty"]
    },
]

TOOL_CALL_GOLDEN = [
    {
        "input": "What is 42 * 7?",
        "expected_tool": "calculator",
        "expected_args": {"operation": "multiply"}
    },
]

MEMORY_GOLDEN = [
    {
        "store_input": "My name is Alice",
        "query_input": "What's my name?",
        "expected_in_response": "Alice"
    },
]
```

注意以下几点：
- **带示例的多行模式**——单行模式经常让模型困惑
- **受版本控制**——这些文件存放在你的仓库中
- **覆盖边缘情况**——特殊字符、数字等
- **具体的断言**——不是"它工作了"，而是"这个字段存在"

## 如何运行

查看 `complete_example.py`，参见 `lesson_11_evals()` 方法：

```python
from agent.agent import Agent
from agent.evals import AgentEval, print_eval_report
from evals.golden_datasets import (
    STRUCTURED_OUTPUT_GOLDEN,
    TOOL_CALL_GOLDEN,
    MEMORY_GOLDEN
)

agent = Agent("models/llama-3-8b-instruct.gguf")
evaluator = AgentEval(agent)

# Run all evals
results = evaluator.run_all(
    structured_cases=STRUCTURED_OUTPUT_GOLDEN,
    tool_cases=TOOL_CALL_GOLDEN,
    memory_cases=MEMORY_GOLDEN
)

# Print report
print_eval_report(results)
```

示例输出：

```
==================================================
EVAL REPORT
==================================================

Structured Output: ✓ PASSED (4/4)
Tool Calls: ✓ PASSED (5/5)
Memory Cycle: ✓ PASSED (3/3)

--------------------------------------------------
Overall: ✓ ALL PASSED (12/12)
==================================================
```

或者当某些测试失败时：

```
==================================================
EVAL REPORT
==================================================

Structured Output: ✗ FAILED (3/4)
  ✗ Input: What does 'hello world' mean in progra...
    Expected: Fields: ['explanation']
    Actual: Missing: ['explanation']
    Error: Schema contract violated

--------------------------------------------------
Overall: ✗ 1 FAILED (11/12)
==================================================
```

## 应该测试什么

| 组件 | 要评估什么 | 示例断言 |
| --------- | ------------ | ----------------- |
| 结构化输出 | JSON 有效性 + 模式契约 | `parse_json(output) is not None and matches schema` |
| 决策 | 正确的路由 | `decision in valid_choices` |
| 工具调用 | 正确的工具 + 参数 | `tool_call["tool"] == "calculator"` |
| 记忆 | 存储/检索循环 | `agent.memory.get_all()` 包含已保存的事实 |

## 与第 03 课对比

**第 03 课（结构化输出）：**
- 生成期间的一次性验证
- JSON 失败时重试
- 没有历史记录

**第 11 课（Evals）：**
- 跨多个用例的系统化测试
- 跟踪随时间变化的成功率
- 在部署前捕获回归

## 关键洞察

### Evals 只是断言

这里没有魔法。你运行 Agent，检查输出，报告通过/失败。其强大之处在于系统化地进行这一过程。

### 黄金数据集是你的契约

当有人问"Agent 工作吗？"时，你指向黄金数据集。100% 通过率 = 它工作了。更低的通过率 = 需要修复的具体故障。

### 每次更改前运行 Evals

工作流程：
1. 做出 prompt 更改
2. 运行 evals
3. 如有失败，修复或回退
4. 提交

这就是防止质量下降的方法。

### 从简单开始

你不需要 1000 个测试用例。从每个功能 5-10 个黄金用例开始。随着在生产中发现边缘情况，再添加更多。

## 常见问题

**"Evals 太慢了"**
- 运行较小的子集进行快速检查
- 在提交前运行完整套件
- 考虑缓存模型加载

**"软断言不稳定的"**
- 只从硬断言开始
- 当有足够数据时再添加软断言
- 在语义匹配之前考虑使用精确匹配

**"我不知道该测试什么"**
- 从正常路径开始
- 添加在生产中出错的用例
- 覆盖边缘情况（空输入、特殊字符等）

## 练习

1. 添加一个当前会失败的新黄金用例，然后修复 prompt
2. 有意破坏一个 prompt，验证 evals 能捕获回归
3. 添加一个边缘情况（空输入、非常长的输入、unicode）
4. 为规划（第 08 课）创建黄金数据集

## 接下来是什么？

在[第 12 课](12_telemetry.md)中，我们将添加 **telemetry**——理解你的 Agent 在运行时正在做什么，而不仅仅是在测试中。

---

**核心要点：** Evals = 系统化测试。黄金数据集 = 你的契约。在每次 prompt 更改前运行它们。
