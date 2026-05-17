#!/usr/bin/env python3
"""
完整的 Agent 示例

此脚本演示了使用全部 12 课中功能的 Agent。
旨在作为各部分如何组合在一起的参考。
"""

import time
from agent.agent import Agent


def lesson_01_basic_chat():
    """第 01 课：基本的 LLM 交互"""
    print("\n" + "="*50)
    print("第 01 课：基本的 LLM 对话")
    print("="*50)

    agent = Agent("models/llama-3-8b-instruct.gguf")
    response = agent.simple_generate("Explain what an AI agent is?")
    print(f"响应：{response}")


def lesson_02_with_role():
    """第 02 课：系统提示词"""
    print("\n" + "="*50)
    print("第 02 课：使用系统提示词")
    print("="*50)

    agent = Agent("models/llama-3-8b-instruct.gguf")
    response = agent.generate_with_role("Explain what an AI agent is?")
    print(f"响应：{response}")


def lesson_03_structured():
    """第 03 课：结构化输出"""
    print("\n" + "="*50)
    print("第 03 课：结构化输出")
    print("="*50)

    agent = Agent("models/llama-3-8b-instruct.gguf")

    schema = """{
  "topic": string,
  "difficulty": "beginner" | "intermediate" | "advanced"
}"""

    result = agent.generate_structured(
        "Explain quantum computing",
        schema
    )
    print(f"结构化结果：{result}")


def lesson_04_decisions():
    """第 04 课：决策"""
    print("\n" + "="*50)
    print("第 04 课：决策")
    print("="*50)

    agent = Agent("models/llama-3-8b-instruct.gguf")

    decision = agent.decide(
        "Can you summarize this article for me?",
        choices=["answer_question", "summarize_text", "translate"]
    )
    print(f"决策：{decision}")


def lesson_05_tools():
    """第 05 课：工具调用"""
    print("\n" + "="*50)
    print("第 05 课：工具调用")
    print("="*50)

    agent = Agent("models/llama-3-8b-instruct.gguf")

    tool_call = agent.request_tool("What is 42 * 7?")
    print(f"工具请求：{tool_call}")

    if tool_call:
        result = agent.execute_tool_call(tool_call)
        print(f"工具结果：{result}")


def lesson_06_agent_loop():
    """第 06 课：Agent 循环"""
    print("\n" + "="*50)
    print("第 06 课：Agent 循环")
    print("="*50)

    agent = Agent("models/llama-3-8b-instruct.gguf")

    print("\n注意：早期迭代中的重复是预期行为。")
    print("Agent 会逐步完善其理解，在收敛到更清晰的解释之前")
    print("可能会重复分析。\n")

    results = agent.run_loop("Help me understand loops", max_steps=3)

    for i, result in enumerate(results, 1):
        print(f"迭代 {i}：")
        action = result.get("action", "unknown")
        reason = result.get("reason", "No reason provided")
        print(f"  操作：{action}")
        print(f"  原因：{reason}")
        if i < len(results):
            print()


def lesson_07_memory():
    """第 07 课：记忆"""
    print("\n" + "="*50)
    print("第 07 课：记忆")
    print("="*50)

    agent = Agent("models/llama-3-8b-instruct.gguf")

    # 第一次交互——存储名字
    response1 = agent.run_with_memory("My name is Alice")
    if response1 and "reply" in response1:
        print(f"响应 1：{response1['reply']}")
        if response1.get("save_to_memory"):
            print(f"  → 已保存到记忆：{response1['save_to_memory']}")
    else:
        print(f"响应 1：{response1}")

    # 第二次交互——回忆名字
    response2 = agent.run_with_memory("What's my name?")
    if response2 and "reply" in response2:
        print(f"响应 2：{response2['reply']}")
        if response2.get("save_to_memory"):
            print(f"  → 已保存到记忆：{response2['save_to_memory']}")
    else:
        print(f"响应 2：{response2}")

    print(f"\n记忆内容：{agent.memory.get_all()}")


def lesson_08_planning():
    """第 08 课：规划"""
    print("\n" + "="*50)
    print("第 08 课：规划")
    print("="*50)

    agent = Agent("models/llama-3-8b-instruct.gguf")

    plan = agent.create_plan("Write a blog post about AI agents")
    print(f"计划：{plan}")

    if plan:
        results = agent.execute_plan(plan)
        print(f"执行结果：{results}")


def lesson_09_atomic_actions():
    """第 09 课：原子操作"""
    print("\n" + "="*50)
    print("第 09 课：原子操作")
    print("="*50)

    agent = Agent("models/llama-3-8b-instruct.gguf")

    # 将计划步骤转换为原子操作
    step = "Write an explanation of AI agents"
    atomic_action = agent.create_atomic_action(step)
    print(f"步骤：{step}")
    print(f"原子操作：{atomic_action}")

    # 使用计划中的步骤示例
    plan = agent.create_plan("Create a tutorial about Python")
    if plan and "steps" in plan and plan["steps"]:
        first_step = plan["steps"][0]
        atomic_action_from_plan = agent.create_atomic_action(first_step)
        print(f"\n计划步骤：{first_step}")
        print(f"来自计划步骤的原子操作：{atomic_action_from_plan}")


def lesson_10_aot():
    """第 10 课：Atom of Thought"""
    print("\n" + "="*50)
    print("第 10 课：Atom of Thought")
    print("="*50)

    agent = Agent("models/llama-3-8b-instruct.gguf")

    graph = agent.create_aot_plan("Research and write article")
    print(f"AoT 图：{graph}")

    if graph:
        results = agent.execute_aot_plan(graph)
        print(f"执行结果：{results}")


def lesson_11_evals():
    """第 11 课：评估（回归测试）"""
    print("\n" + "="*50)
    print("第 11 课：评估")
    print("="*50)

    from agent.evals import AgentEval, print_eval_report
    from evals.golden_datasets import (
        STRUCTURED_OUTPUT_GOLDEN,
        TOOL_CALL_GOLDEN,
        DECISION_GOLDEN,
        MEMORY_GOLDEN
    )

    agent = Agent("models/llama-3-8b-instruct.gguf")
    evaluator = AgentEval(agent)

    print("\n正在运行评估套件...")
    print("（这可能需要一分钟，因为它会运行多个 Agent 调用）\n")

    # 为演示运行一个子集（完整套件可能会很慢）
    # 使用每个套件中的前 2 个用例进行快速演示
    results = evaluator.run_all(
        structured_cases=STRUCTURED_OUTPUT_GOLDEN[:2],
        tool_cases=TOOL_CALL_GOLDEN[:2],
        decision_cases=DECISION_GOLDEN[:2],
        memory_cases=MEMORY_GOLDEN[:1]
    )

    # 打印报告
    print_eval_report(results)

    # 展示如何访问单个结果
    print("\n访问单个套件结果：")
    for suite in results:
        print(f"  {suite.name}: {suite.pass_rate:.0%} 通过率")


def lesson_12_telemetry():
    """第 12 课：遥测（运行时可观测性）"""
    print("\n" + "="*50)
    print("第 12 课：遥测")
    print("="*50)

    from agent.telemetry import Telemetry

    agent = Agent("models/llama-3-8b-instruct.gguf")
    telemetry = Telemetry(log_file="agent_telemetry.jsonl")

    # 清除之前的遥测数据以进行干净的演示
    telemetry.clear()

    print("\n正在运行带有遥测的 Agent 操作...")

    # 为此次交互启动一个追踪
    trace_id = telemetry.start_trace()
    print(f"追踪 ID：{trace_id}")

    # 操作 1：结构化输出
    print("\n1. 结构化输出调用...")
    start = time.time()
    result1 = agent.generate_structured(
        "What is Python?",
        '{"answer": string, "difficulty": "beginner" | "intermediate" | "advanced"}'
    )
    duration1 = (time.time() - start) * 1000

    telemetry.log_llm_call(
        prompt_length=150,
        response_length=len(str(result1)) if result1 else 0,
        duration_ms=duration1,
        success=result1 is not None,
        error=None if result1 else "Failed to parse JSON"
    )
    print(f"   结果：{result1}")
    print(f"   耗时：{duration1:.0f}ms")

    # 操作 2：工具调用
    print("\n2. 工具调用...")
    start = time.time()
    tool_call = agent.request_tool("What is 15 * 8?")
    duration2 = (time.time() - start) * 1000

    telemetry.log_llm_call(
        prompt_length=200,
        response_length=len(str(tool_call)) if tool_call else 0,
        duration_ms=duration2,
        success=tool_call is not None
    )

    if tool_call:
        telemetry.log_tool_call(
            tool_name=tool_call.get("tool", "unknown"),
            arguments=tool_call.get("arguments", {}),
            result=agent.execute_tool_call(tool_call) if tool_call else None,
            duration_ms=1.0  # 工具执行很快
        )
        print(f"   工具：{tool_call}")

    # 操作 3：记忆
    print("\n3. 记忆操作...")
    start = time.time()
    result3 = agent.run_with_memory("My favorite color is blue")
    duration3 = (time.time() - start) * 1000

    telemetry.log_llm_call(
        prompt_length=300,
        response_length=len(str(result3)) if result3 else 0,
        duration_ms=duration3,
        success=result3 is not None
    )
    telemetry.log_memory_operation("add", "favorite color is blue")
    print(f"   结果：{result3}")

    # 打印遥测摘要
    telemetry.print_summary()

    # 显示最近的 span
    print("\n最近的 span：")
    for span in telemetry.get_recent_spans(5):
        event = span.get("event_type", "unknown")
        duration = span.get("duration_ms", "N/A")
        print(f"  [{event}] 耗时={duration}ms")

    print(f"\n遥测已记录到：agent_telemetry.jsonl")
    print("查看方式：cat agent_telemetry.jsonl | head -5")


def main():
    """运行所有课程示例"""
    print("\n" + "#"*50)
    print("# AI Agent 示例——全部课程")
    print("#"*50)

    try:
        # 注释掉你想跳过的课程
        lesson_01_basic_chat()
        lesson_02_with_role()
        lesson_03_structured()
        lesson_04_decisions()
        lesson_05_tools()
        lesson_06_agent_loop()
        lesson_07_memory()
        lesson_08_planning()
        lesson_09_atomic_actions()
        lesson_10_aot()
        lesson_11_evals()
        lesson_12_telemetry()

        print("\n" + "="*50)
        print("所有示例已完成！")
        print("="*50)

    except FileNotFoundError as e:
        print(f"\n❌ 错误：{e}")
        print("\n请确保你已完成以下操作：")
        print("1. 下载了 GGUF 模型")
        print("2. 将其放置在 models/ 目录中")
        print("3. 更新了此脚本中的模型路径")
    except Exception as e:
        print(f"\n❌ 意外错误：{e}")


if __name__ == "__main__":
    main()
