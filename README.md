# AI Agents 从零开始

一个温和的、本地优先的 AI Agent 入门教程。

本仓库通过从一个本地 LLM 调用开始，逐步构建**一个 Agent**，来教授 AI Agent 的实际工作原理。

**没有框架。没有云 API。没有隐藏的推理。没有魔法。**

## 相关项目

### [AI Product from Scratch](https://github.com/pguso/ai-product-from-scratch)

[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![React](https://img.shields.io/badge/React-20232A?logo=react&logoColor=61DAFB)](https://reactjs.org/)
[![Node.js](https://img.shields.io/badge/Node.js-339933?logo=node.js&logoColor=white)](https://nodejs.org/)

使用本地 LLM 学习 AI 产品开发基础。涵盖提示工程、结构化输出、多步推理、API 设计和前端集成，包含 10 节综合课程和可视化图表。

### [AI Agents from Scratch (JavaScript 版)](https://github.com/pguso/ai-agents-from-scratch)

![JavaScript](https://img.shields.io/badge/JavaScript-3776AB?logo=javascript&logoColor=yellow)

![Agent 架构](diagrams/agent-architecture.png)

## 哲学理念

Agent 不是人格。它们是循环、状态和约束。

如果某件事让你觉得神奇，打开文件看看——这个仓库里没有隐藏的逻辑。

## 你将学到什么

本仓库通过 12 节课程，构建一个持续演进的 Agent：

| 课程 | 新增能力 | 链接 |
|--------|------------------|------|
| 01 | 文本输入 / 文本输出 | [lessons/01_basic_llm_chat.md](lessons/01_basic_llm_chat.md) |
| 02 | 角色和行为（系统提示词） | [lessons/02_system_prompt.md](lessons/02_system_prompt.md) |
| 03 | 结构化输出（JSON 契约） | [lessons/03_structured_output.md](lessons/03_structured_output.md) |
| 04 | 决策（路由逻辑） | [lessons/04_decision_making.md](lessons/04_decision_making.md) |
| 05 | 工具（外部能力） | [lessons/05_tools.md](lessons/05_tools.md) |
| 06 | Agent 循环（观察 → 决策 → 行动） | [lessons/06_agent_loop.md](lessons/06_agent_loop.md) |
| 07 | 记忆（短期和长期） | [lessons/07_memory.md](lessons/07_memory.md) |
| 08 | 规划（作为数据，而非思想） | [lessons/08_planning.md](lessons/08_planning.md) |
| 09 | 原子动作（安全执行） | [lessons/09_atomic_actions.md](lessons/09_atomic_actions.md) |
| 10 | AoT - 思想原子（依赖图） | [lessons/10_atom_of_thought.md](lessons/10_atom_of_thought.md) |
| 11 | 评估（回归测试） | [lessons/11_evals.md](lessons/11_evals.md) |
| 12 | 遥测（运行时可观测性） | [lessons/12_telemetry.md](lessons/12_telemetry.md) |

## 适合人群

**本仓库适合：**
- 会写代码但对 Agent 感到迷茫的开发者
- 厌倦了"直接用 LangChain"的人
- 想使用本地模型的学习者
- 想要机械式理解的工程师
- 寻找清晰心智模型的教育者

**本仓库不适合：**
- 想要最快演示的人
- 想要 SaaS 启动套件的人
- 相信 Agent 会"思考"的人
- 想要隐藏思维链的人

## 快速开始

**详细安装说明请参阅 [QUICKSTART.md](QUICKSTART.md)**

简而言之：
1. 安装依赖：`pip install -r requirements.txt`
2. 下载 GGUF 模型到 `models/` 文件夹
3. 运行：`python complete_example.py`

**注意：** `complete_example.py` 文件包含展示全部 12 节课程的可执行代码示例。你可以将其作为参考，了解所有概念如何组合在一起。

## 仓库结构

```
ai-agents-from-scratch/
├─ README.md              # 你在这里
├─ philosophy.md          # 这个仓库为什么存在
├─ QUICKSTART.md          # 详细安装指南
├─ complete_example.py    # 全部 12 节课程的演示
├─ requirements.txt       # Python 依赖
│
├─ models/                # 将 GGUF 模型放在这里
├─ shared/                # 可复用工具（LLM、提示词、工具函数）
├─ agent/                 # 逐步演进的 Agent 实现
│  ├─ agent.py             # 主 Agent 类
│  ├─ memory.py            # 记忆系统
│  ├─ planner.py           # 规划和原子动作
│  ├─ state.py             # Agent 状态管理
│  ├─ tools.py             # 工具定义
│  ├─ evals.py             # 评估框架（课程 11）
│  └─ telemetry.py         # 遥测系统（课程 12）
├─ evals/                 # 用于测试的金标准数据集
│  └─ golden_datasets.py   # 已知正确的测试用例
└─ lessons/               # 逐步说明（01-12）
```

### 关键文件说明

**`agent/agent.py`** - 仓库的核心
- 包含跨越全部 12 节课程逐步演进的 `Agent` 类
- 每节课程为同一个类添加新的方法和能力
- 这是你在学习过程中研究和修改的对象

**`complete_example.py`** - 学习参考
- 包含 12 个独立的函数，对应每节课程
- 每个函数独立演示该课程的概念
- 在组合使用之前，先用它了解单节课程的工作原理
- 运行：`python complete_example.py`

**`agent/evals.py`** - 回归测试（课程 11）
- 用已知正确的用例测试你的 Agent
- 在部署之前捕获提示词回归问题

**`agent/telemetry.py`** - 运行时可观测性（课程 12）
- 用于调试的结构化日志
- 追踪延迟、成功率和调用链

**关系说明**：
- `agent/agent.py` = 你正在学习的代码（实现）
- `complete_example.py` = 每节课的独立示例（用于学习和实验）

## 本仓库不是什么

- 这**不是一个框架**
- 这**不是一个聊天机器人演示**
- 这**不声称模型会思考**
- 这**不暴露思维链**
- 这**不需要 OpenAI 或云 API**

## 核心原则

1. **一个 Agent，多个阶段** - 同一个 `agent.py` 文件随课程逐步增长
2. **显式优于隐式** - 没有隐藏逻辑，没有魔法抽象
3. **结构优于提示** - 可靠性来自约束，而非巧妙的措辞
4. **本地优先** - 无需 API 密钥，无速率限制，无云依赖
5. **教学而非生产** - 这里教授基础原理，而非最佳实践

## 学习路径

每节课程都建立在前一节的基础上。**不要跳课。**

课程设计旨在逐步建立理解：
- 课程 1-3：基础（LLM 基础）
- 课程 4-6：行动能力（决策、工具、循环）
- 课程 7-10：智能（记忆、规划、执行）
- 课程 11-12：可观测性（评估、遥测）

## 贡献

这是一个教育性仓库。贡献应：
- 保持温和、渐进的学习风格
- 保持代码可读性优先于巧妙性
- 添加解释，而不仅仅是功能
- 保持"无框架"的哲学理念

## 许可证

MIT 许可证 - 详见 LICENSE 文件

## 致谢

本仓库综合了现代 Agent 开发的最佳实践，同时刻意避免了会模糊理解的复杂性。

---

**如果你觉得这个项目有用，请给仓库加星并分享给其他正在学习 AI Agent 的人。**
