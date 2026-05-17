"""
Agent 评估框架。

Evals 是 agent 的回归测试。
评估套件就是一个 Python 文件，运行你的 agent 并断言一切正常没有损坏。

此模块提供：
- 结构化输出验证
- 工具调用准确性测试
- 记忆存储/检索循环测试
- 决策路由验证
"""

from typing import Any, Callable
from dataclasses import dataclass, field


@dataclass
class EvalResult:
    """单个评估案例的结果。"""
    passed: bool
    input: str
    expected: Any = None
    actual: Any = None
    error: str | None = None


@dataclass
class EvalSuiteResult:
    """运行一个评估套件的结果。"""
    name: str
    passed: int = 0
    failed: int = 0
    results: list[EvalResult] = field(default_factory=list)

    @property
    def total(self) -> int:
        return self.passed + self.failed

    @property
    def pass_rate(self) -> float:
        return self.passed / self.total if self.total > 0 else 0.0

    def add_result(self, result: EvalResult):
        """添加一个结果并更新计数。"""
        self.results.append(result)
        if result.passed:
            self.passed += 1
        else:
            self.failed += 1

    def summary(self) -> str:
        """生成一个人类可读的摘要。"""
        status = "✓ 通过" if self.failed == 0 else "✗ 失败"
        return f"{self.name}: {status} ({self.passed}/{self.total})"


class AgentEval:
    """
    Agent 能力的回归测试。

    用法:
        evaluator = AgentEval(agent)
        results = evaluator.test_structured_output(golden_cases)
        print(results.summary())
    """

    def __init__(self, agent):
        """
        使用 agent 实例初始化评估器。

        Args:
            agent: 要测试的 Agent 实例
        """
        self.agent = agent

    def test_structured_output(self, cases: list[dict]) -> EvalSuiteResult:
        """
        测试结构化输出是否解析正确并匹配 schema。

        这是一个硬性断言 —— JSON 必须始终有效。

        Args:
            cases: {"input": str, "schema": str, "must_have_fields": list[str]} 的列表

        Returns:
            包含通过/失败计数和详情的 EvalSuiteResult
        """
        suite = EvalSuiteResult(name="Structured Output")

        for case in cases:
            input_text = case["input"]
            schema = case["schema"]
            required_fields = case.get("must_have_fields", [])

            try:
                result = self.agent.generate_structured(input_text, schema)

                # 检查 1：我们是否获得了有效的 JSON？
                if result is None:
                    suite.add_result(EvalResult(
                        passed=False,
                        input=input_text,
                        expected="Valid JSON",
                        actual=None,
                        error="Failed to parse JSON after retries"
                    ))
                    continue

                # 检查 2：必需的字段是否存在？
                missing_fields = [f for f in required_fields if f not in result]
                if missing_fields:
                    suite.add_result(EvalResult(
                        passed=False,
                        input=input_text,
                        expected=f"Fields: {required_fields}",
                        actual=f"Missing: {missing_fields}",
                        error="Schema contract violated"
                    ))
                    continue

                # 通过所有检查
                suite.add_result(EvalResult(
                    passed=True,
                    input=input_text,
                    actual=result
                ))

            except Exception as e:
                suite.add_result(EvalResult(
                    passed=False,
                    input=input_text,
                    error=str(e)
                ))

        return suite

    def test_tool_calls(self, cases: list[dict]) -> EvalSuiteResult:
        """
        测试工具调用准确性 —— 选择了正确的工具并带有有效参数。

        Args:
            cases: {"input": str, "expected_tool": str, "expected_args": dict (可选)} 的列表

        Returns:
            包含通过/失败计数的 EvalSuiteResult
        """
        suite = EvalSuiteResult(name="Tool Calls")

        for case in cases:
            input_text = case["input"]
            expected_tool = case["expected_tool"]
            expected_args = case.get("expected_args")

            try:
                tool_call = self.agent.request_tool(input_text)

                # 检查 1：我们是否获得了工具调用？
                if tool_call is None:
                    suite.add_result(EvalResult(
                        passed=False,
                        input=input_text,
                        expected=expected_tool,
                        actual=None,
                        error="No tool call generated"
                    ))
                    continue

                # 检查 2：是否是正确的工具？
                actual_tool = tool_call.get("tool")
                if actual_tool != expected_tool:
                    suite.add_result(EvalResult(
                        passed=False,
                        input=input_text,
                        expected=expected_tool,
                        actual=actual_tool,
                        error="Wrong tool selected"
                    ))
                    continue

                # 检查 3：参数是否有效？（如果已指定）
                if expected_args:
                    actual_args = tool_call.get("arguments", {})
                    for key, expected_val in expected_args.items():
                        if actual_args.get(key) != expected_val:
                            suite.add_result(EvalResult(
                                passed=False,
                                input=input_text,
                                expected=expected_args,
                                actual=actual_args,
                                error=f"Wrong argument: {key}"
                            ))
                            continue

                # 通过
                suite.add_result(EvalResult(
                    passed=True,
                    input=input_text,
                    expected=expected_tool,
                    actual=tool_call
                ))

            except Exception as e:
                suite.add_result(EvalResult(
                    passed=False,
                    input=input_text,
                    error=str(e)
                ))

        return suite

    def test_decisions(self, cases: list[dict]) -> EvalSuiteResult:
        """
        测试决策路由 —— agent 从选项中选择正确的动作。

        Args:
            cases: {"input": str, "choices": list[str], "expected": str} 的列表

        Returns:
            包含通过/失败计数的 EvalSuiteResult
        """
        suite = EvalSuiteResult(name="Decisions")

        for case in cases:
            input_text = case["input"]
            choices = case["choices"]
            expected = case["expected"]

            try:
                decision = self.agent.decide(input_text, choices)

                if decision is None:
                    suite.add_result(EvalResult(
                        passed=False,
                        input=input_text,
                        expected=expected,
                        actual=None,
                        error="No decision made"
                    ))
                elif decision != expected:
                    suite.add_result(EvalResult(
                        passed=False,
                        input=input_text,
                        expected=expected,
                        actual=decision,
                        error="Wrong decision"
                    ))
                else:
                    suite.add_result(EvalResult(
                        passed=True,
                        input=input_text,
                        expected=expected,
                        actual=decision
                    ))

            except Exception as e:
                suite.add_result(EvalResult(
                    passed=False,
                    input=input_text,
                    error=str(e)
                ))

        return suite

    def test_memory_cycle(self, cases: list[dict]) -> EvalSuiteResult:
        """
        测试记忆存储 → 检索循环。

        Args:
            cases: {"store_input": str, "query_input": str, "expected_in_response": str} 的列表

        Returns:
            包含通过/失败计数的 EvalSuiteResult
        """
        suite = EvalSuiteResult(name="Memory Cycle")

        for case in cases:
            store_input = case["store_input"]
            query_input = case["query_input"]
            expected_substring = case.get("expected_in_response", "")

            try:
                # 清空记忆以确保干净的测试
                self.agent.memory.clear()

                # 步骤 1：存储
                store_response = self.agent.run_with_memory(store_input)
                if store_response is None:
                    suite.add_result(EvalResult(
                        passed=False,
                        input=store_input,
                        error="Failed to store to memory"
                    ))
                    continue

                # 步骤 2：查询
                query_response = self.agent.run_with_memory(query_input)
                if query_response is None:
                    suite.add_result(EvalResult(
                        passed=False,
                        input=query_input,
                        error="Failed to query memory"
                    ))
                    continue

                # 步骤 3：检查回复中是否包含预期信息
                reply = query_response.get("reply", "")
                if expected_substring.lower() in reply.lower():
                    suite.add_result(EvalResult(
                        passed=True,
                        input=f"{store_input} → {query_input}",
                        expected=expected_substring,
                        actual=reply
                    ))
                else:
                    suite.add_result(EvalResult(
                        passed=False,
                        input=f"{store_input} → {query_input}",
                        expected=expected_substring,
                        actual=reply,
                        error="Expected content not in response"
                    ))

            except Exception as e:
                suite.add_result(EvalResult(
                    passed=False,
                    input=store_input,
                    error=str(e)
                ))

        return suite

    def run_all(self,
                structured_cases: list[dict] = None,
                tool_cases: list[dict] = None,
                decision_cases: list[dict] = None,
                memory_cases: list[dict] = None) -> list[EvalSuiteResult]:
        """
        运行所有评估套件。

        Args:
            structured_cases: 用于结构化输出测试的案例
            tool_cases: 用于工具调用测试的案例
            decision_cases: 用于决策测试的案例
            memory_cases: 用于记忆测试的案例

        Returns:
            所有 EvalSuiteResults 的列表
        """
        results = []

        if structured_cases:
            results.append(self.test_structured_output(structured_cases))

        if tool_cases:
            results.append(self.test_tool_calls(tool_cases))

        if decision_cases:
            results.append(self.test_decisions(decision_cases))

        if memory_cases:
            results.append(self.test_memory_cycle(memory_cases))

        return results


def print_eval_report(results: list[EvalSuiteResult]):
    """
    打印一个格式化的评估报告。

    Args:
        results: 要报告的 EvalSuiteResult 列表
    """
    print("\n" + "="*50)
    print("评估报告")
    print("="*50)

    total_passed = 0
    total_failed = 0

    for suite in results:
        print(f"\n{suite.summary()}")

        # 显示失败项
        for result in suite.results:
            if not result.passed:
                print(f"  ✗ 输入: {result.input[:50]}...")
                if result.expected:
                    print(f"    预期: {result.expected}")
                if result.actual:
                    print(f"    实际: {result.actual}")
                if result.error:
                    print(f"    错误: {result.error}")

        total_passed += suite.passed
        total_failed += suite.failed

    print("\n" + "-"*50)
    overall = "✓ 全部通过" if total_failed == 0 else f"✗ {total_failed} 项失败"
    print(f"总体: {overall} ({total_passed}/{total_passed + total_failed})")
    print("="*50)
