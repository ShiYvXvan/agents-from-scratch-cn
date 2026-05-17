"""
Agent 的提示词模板。

这些函数构建的提示词在各课程中逐步演进：
- 第 01 课：base_prompt（仅文本）
- 第 02 课：system_prompt（添加角色）
- 第 03 课：json_contract（添加结构化）
- 第 04 课及以上：用于决策、工具调用、规划的专用提示词

提示词是 Agent 系统中的一等公民。
"""


def base_prompt(user_input: str) -> str:
    """
    最简单的提示词——仅包含用户文本。

    用于：第 01 课

    参数：
        user_input: 用户的问题或请求

    返回值：
        未经修改的用户输入
    """
    return user_input


def system_prompt(role: str, user_input: str) -> str:
    """
    添加系统角色以塑造行为。

    用于：第 02 课

    参数：
        role: 助手角色和行为的描述
        user_input: 用户的问题或请求

    返回值：
        包含系统和用户部分的格式化提示词
    """
    return f"""<SYSTEM>
{role}
</SYSTEM>

<USER>
{user_input}
</USER>"""


def json_contract(schema: str, content: str) -> str:
    """
    强制结构化 JSON 输出。

    用于：第 03 课

    参数：
        schema: JSON 模式描述
        content: 要处理的内容

    返回值：
        强制 JSON 输出的提示词
    """
    return f"""Return ONLY valid JSON.
No explanations. No markdown. No extra text.

Schema:
{schema}

Content:
{content}"""


def decision_prompt(choices: list[str], user_input: str) -> str:
    """
    使模型从有限的选项集中进行选择。

    用于：第 04 课

    参数：
        choices: 可能的操作/决策列表
        user_input: 需要做出决策的输入

    返回值：
        强制决策的提示词
    """
    options = "\n".join(f"- {choice}" for choice in choices)

    return f"""You must choose ONE of the following options.
Return ONLY valid JSON.

Available choices:
{options}

Schema:
{{ "decision": string }}

Input:
{user_input}"""


def tool_call_prompt(tools: dict, user_input: str) -> str:
    """
    请求模型发起工具调用。

    用于：第 05 课

    参数：
        tools: 可用工具及其模式的字典
        user_input: 用户的请求

    返回值：
        请求工具调用的提示词
    """
    return f"""You may request ONE tool call.

Available tools:
{tools}

Return ONLY valid JSON.

Schema:
{{
  "tool": string,
  "arguments": object
}}

User request:
{user_input}"""


def agent_step_prompt(state: dict, user_input: str) -> str:
    """
    根据当前状态生成下一个 Agent 操作。

    用于：第 06 课

    参数：
        state: 当前 Agent 状态
        user_input: 用户输入或系统观察结果

    返回值：
        用于 Agent 步骤执行的提示词
    """
    return f"""You are an agent.

Current state:
{state}

Decide the next action.

Return ONLY valid JSON.

Schema:
{{
  "action": string,
  "reason": string
}}

User input:
{user_input}"""


def memory_prompt(state: dict, memory: list, user_input: str) -> str:
    """
    带有记忆上下文的 Agent 提示词。

    用于：第 07 课

    参数：
        state: 当前 Agent 状态
        memory: 相关记忆列表
        user_input: 用户输入

    返回值：
        带有记忆上下文的提示词
    """
    return f"""You are an agent with memory.

Current state:
{state}

Relevant memory:
{memory}

Decide what to do next.

Return ONLY valid JSON.

Schema:
{{
  "action": string,
  "save_to_memory": string | null
}}

User input:
{user_input}"""


def planning_prompt(goal: str) -> str:
    """
    生成实现目标的计划。

    用于：第 08 课

    参数：
        goal: 要实现的目标

    返回值：
        用于计划生成的提示词
    """
    return f"""Create a step-by-step plan to achieve the goal.

Return ONLY valid JSON.

Schema:
{{
  "steps": [string]
}}

Goal:
{goal}"""


def atomic_action_prompt(step: str) -> str:
    """
    将计划步骤转换为原子操作。

    用于：第 09 课

    参数：
        step: 计划中的一个步骤

    返回值：
        生成原子操作的提示词
    """
    return f"""Convert this step into an atomic action.

Return ONLY valid JSON.

Schema:
{{
  "action": string,
  "inputs": object
}}

Step:
{step}"""


def aot_prompt(goal: str) -> str:
    """
    生成 Atom of Thought 执行图。

    用于：第 10 课

    参数：
        goal: 要实现的目标

    返回值：
        用于 AoT 图生成的提示词
    """
    return f"""Create an atomic execution graph for the goal.

Return ONLY valid JSON.

Schema:
{{
  "nodes": [
    {{
      "id": string,
      "action": string,
      "depends_on": [string]
    }}
  ]
}}

Goal:
{goal}"""
