# 第 12 课 - Telemetry（运行时可观测性）

## 我们要回答什么问题？

**"我的 Agent 在运行时到底在做什么？"**

Evals 告诉你 Agent 在部署前是否工作。Telemetry 告诉你在部署期间发生了什么。没有 telemetry，调试就是靠猜。

## 你将构建什么

一个 telemetry 系统，具备以下功能：
- 记录每个 LLM 调用的输入和输出
- 跟踪工具调用的成功/失败率
- 测量延迟和重试次数
- 通过 traces 实现事后调试

## 引入的新概念

### 1. 结构化日志

**结构化日志**意味着 JSON 日志，而不是 print 语句。每个日志条目有统一的模式：时间戳、事件类型、数据、错误。

```json
{"event_type": "llm_call", "timestamp": "2024-01-15T10:30:00", "duration_ms": 1523, "success": true}
```

这是可搜索的、可解析的、机器可读的。

### 2. Span 和 Trace

一个 **span** 是一个操作——一个单独的 LLM 调用、一次工具执行、一次记忆访问。

一个 **trace** 是一次完整的 Agent 交互——由 trace ID 关联的多个 span 链接在一起。

当某件事失败时，你找到那个 trace，逐步看到到底发生了什么。

### 3. 指标

**指标**是聚合的数字：
- `llm_success_rate`——JSON 解析正确的频率是多少？
- `avg_latency_ms`——LLM 调用需要多长时间？
- `tool_failure_rate`——工具调用失败的频率是多少？

指标让你一目了然地了解 Agent 的健康状况。

## 我们（目前）不做什么

- 没有分布式追踪（仅限单机）
- 没有生产仪表盘（基于文件的日志记录）
- 没有告警（手动检查）
- 没有 OpenTelemetry（保持简单）

## 代码

查看 `agent/telemetry.py`：

```python
import json
import time
from datetime import datetime
from uuid import uuid4
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Span:
    """A single operation in a trace."""
    span_id: str
    trace_id: str
    event_type: str
    timestamp: str
    duration_ms: Optional[float] = None
    data: Optional[dict] = None
    error: Optional[str] = None


@dataclass
class Metrics:
    """Aggregated metrics for the agent."""
    llm_calls: int = 0
    llm_failures: int = 0
    llm_retries: int = 0
    tool_calls: int = 0
    tool_failures: int = 0
    total_latency_ms: float = 0.0
    
    @property
    def avg_latency_ms(self) -> float:
        return self.total_latency_ms / self.llm_calls if self.llm_calls > 0 else 0.0
    
    @property
    def llm_success_rate(self) -> float:
        return 1 - (self.llm_failures / self.llm_calls) if self.llm_calls > 0 else 0.0


class Telemetry:
    """Simple telemetry for agent observability."""
    
    def __init__(self, log_file: str = "agent_telemetry.jsonl"):
        self.log_file = log_file
        self.current_trace_id = None
        self.metrics = Metrics()
    
    def start_trace(self) -> str:
        """Start a new trace (one full agent interaction)."""
        self.current_trace_id = str(uuid4())[:8]
        return self.current_trace_id
    
    def log_llm_call(self, prompt_length: int, response_length: int, 
                     duration_ms: float, success: bool = True, error: str = None):
        """Log an LLM call."""
        span = Span(
            span_id=str(uuid4())[:8],
            trace_id=self.current_trace_id or "no-trace",
            event_type="llm_call",
            timestamp=datetime.now().isoformat(),
            duration_ms=round(duration_ms, 2),
            data={"prompt_length": prompt_length, "response_length": response_length},
            error=error
        )
        
        # Write to log file
        with open(self.log_file, "a") as f:
            f.write(json.dumps(asdict(span)) + "\n")
        
        # Update metrics
        self.metrics.llm_calls += 1
        self.metrics.total_latency_ms += duration_ms
        if not success:
            self.metrics.llm_failures += 1
```

注意以下几点：
- **Dataclasses**——清晰、有类型的结构
- **JSONL 格式**——每行一个 JSON 对象，易于解析
- **指标累积**——随进程跟踪聚合数据
- **Trace 链接**——所有 span 共享一个 trace ID

## 如何运行

查看 `complete_example.py`，参见 `lesson_12_telemetry()` 方法：

```python
from agent.agent import Agent
from agent.telemetry import Telemetry

agent = Agent("models/llama-3-8b-instruct.gguf")
telemetry = Telemetry()

# Start a trace
trace_id = telemetry.start_trace()
print(f"Trace ID: {trace_id}")

# Simulate some operations (in real usage, these come from instrumented agent)
import time

start = time.time()
result = agent.generate_structured("What is Python?", '{"answer": string}')
duration = (time.time() - start) * 1000

telemetry.log_llm_call(
    prompt_length=100,
    response_length=len(str(result)),
    duration_ms=duration,
    success=result is not None
)

# Check metrics
telemetry.print_summary()
```

示例输出：

```
========================================
TELEMETRY SUMMARY
========================================
LLM Calls:      3
  Success Rate: 100.00%
  Avg Latency:  1245ms
  Retries:      0
Tool Calls:     2
  Success Rate: 100.00%
Memory Ops:     1
========================================
```

## 查看日志文件

Telemetry 记录到 `agent_telemetry.jsonl`：

```jsonl
{"span_id": "a1b2c3d4", "trace_id": "x9y8z7w6", "event_type": "llm_call", "timestamp": "2024-01-15T10:30:00.123456", "duration_ms": 1523.45, "data": {"prompt_length": 256, "response_length": 89, "success": true}}
{"span_id": "e5f6g7h8", "trace_id": "x9y8z7w6", "event_type": "tool_call", "timestamp": "2024-01-15T10:30:02.456789", "duration_ms": 5.23, "data": {"tool": "calculator", "arguments": {"a": 42, "b": 7, "operation": "multiply"}}}
```

要调试某个特定交互，按 `trace_id` 过滤：
```bash
grep "x9y8z7w6" agent_telemetry.jsonl
```

## 应该记录什么

| 事件 | 要捕获的数据 | 为什么 |
|-------|-----------------|-----|
| LLM 调用 | prompt_length, response_length, duration_ms, success | 跟踪延迟，识别慢/失败的调用 |
| 工具请求 | tool_name, arguments | 调试错误的工具选择 |
| 工具执行 | tool_name, result, error | 调试工具失败 |
| 记忆操作 | operation, data | 跟踪存储/检索的内容 |
| 决策 | choices, selected | 调试路由问题 |

## 与第 11 课对比

**第 11 课（Evals）：**
- 在部署前运行
- 已知输入，预期输出
- 二元通过/失败
- 捕获回归

**第 12 课（Telemetry）：**
- 在部署期间运行
- 未知输入，观测到的输出
- 持续监控
- 使调试成为可能

它们是互补的。Evals 防止有问题的代码被发布。Telemetry 帮助你理解已发布的代码在做什么。

## 关键洞察

### Telemetry 只是结构化日志

没有魔法。你在往文件中写 JSON。其强大之处在于：
- 统一的模式
- Trace ID 关联相关事件
- 聚合的指标

### Trace 是你的调试超能力

当用户报告"Agent 给出了奇怪的答案"时，你：
1. 获取 trace ID
2. 找到该 trace 的所有 span
3. 看到到底发生了什么

没有 traces，你只能靠猜。

### 指标告诉你系统健康状况

扫一眼指标就知道是否有问题：
- 成功率在下降？检查 prompt 问题
- 延迟在增加？检查模型/硬件
- 重试次数在增加？检查 JSON 解析

### 从简单开始，以后再添加

这个实现记录到文件。这对起步来说足够了。以后你可以添加：
- 数据库存储
- 实时仪表盘
- 阈值告警

但从文件开始。

## 常见问题

**"日志文件太大"**
- 轮转日志（按天/小时创建新文件）
- 在生产中只记录失败
- 截断较长的数据字段

**"我找不到我需要的 trace"**
- 在面向用户的错误信息中添加 trace ID
- 在应用日志中记录 trace ID
- 考虑在 traces 中添加用户 ID

**"Telemetry 拖慢了我的 Agent"**
- 异步记录（先缓冲，再写入）
- 减少每个 span 捕获的数据
- 采样而不是记录所有内容

## 练习

1. 将 telemetry 添加到 Agent 循环中，追踪完整的多步骤交互
2. 计算 20 次结构化输出调用中的 JSON 解析成功率
3. 比较不同 prompt 长度之间的延迟
4. 在日志中找到失败的 span 并调试出了什么问题

## 接下来是什么？

恭喜！你已经完成核心课程。

你现在拥有一个具备以下能力的 Agent：
- 结构化输出（第 03 课）
- 决策能力（第 04 课）
- 工具调用（第 05 课）
- Agent 循环（第 06 课）
- 记忆（第 07 课）
- 规划（第 08 课）
- 原子动作（第 09 课）
- 依赖图（第 10 课）
- 回归测试（第 11 课）
- 运行时可观测性（第 12 课）

这是一个从第一性原理构建的完整的、可观测的、可测试的 Agent。

---

**核心要点：** Telemetry = 结构化日志 + traces + 指标。它将"出了点问题"变成"这是到底发生了什么"。
