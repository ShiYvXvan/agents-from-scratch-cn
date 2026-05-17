"""
LocalLLM - 一个简单的 llama-cpp-python 封装器。

此类提供了一个最小化的接口来与本地语言模型交互。
刻意不包含任何魔法：
- 无重试机制（在第 03 课中添加）
- 无工具调用（在第 05 课中添加）
- 无记忆功能（在第 07 课中添加）

仅文本输入，文本输出。
"""

from shared.llama_logging import disable_llama_logging
from llama_cpp import Llama

disable_llama_logging()

class LocalLLM:
    """
    使用 llama.cpp 进行本地 LLM 推理的最小化封装器。

    此类刻意保持简单，并在各课程中逐步扩展。
    """

    def __init__(
        self,
        model_path: str,
        temperature: float = 0.2,
        max_tokens: int = 512,
        n_ctx: int = 2048
    ):
        """
        初始化本地 LLM。

        参数：
            model_path: GGUF 模型文件路径
            temperature: 采样温度（0.0 = 确定性输出，1.0 = 创造性输出）
            max_tokens: 每次响应生成的最大 token 数
            n_ctx: 上下文窗口大小
        """
        self.llm = Llama(
            model_path=model_path,
            temperature=temperature,
            n_ctx=n_ctx,
            verbose=False,
        )
        self.max_tokens = max_tokens

    def generate(self, prompt: str, temperature: float = None, stop: list[str] = None) -> str:
        """
        根据提示词生成文本。

        参数：
            prompt: 输入文本提示词
            temperature: 可选的温度覆盖值
            stop: 可选的停止序列列表

        返回值：
            生成的文本字符串
        """
        kwargs = {
            "prompt": prompt,
            "max_tokens": self.max_tokens,
            "stop": stop if stop is not None else ["</s>", "\n\n", "User:", "Assistant:"],
        }

        if temperature is not None:
            kwargs["temperature"] = temperature

        response = self.llm(**kwargs)
        return response["choices"][0]["text"].strip()
