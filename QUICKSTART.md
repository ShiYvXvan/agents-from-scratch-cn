# 快速入门指南

在 10 分钟内上手并运行 AI Agents from Scratch。

## 前置条件

- Python 3.10 或更高版本
- 8GB+ RAM（用于运行本地模型）
- 约 5-10GB 可用磁盘空间（用于存放模型文件）

## 步骤 1：安装依赖

```bash
pip install llama-cpp-python
```

**可选但推荐：**
```bash
# 首先创建一个虚拟环境
python -m venv venv
source venv/bin/activate  # Windows 上使用: venv\Scripts\activate
pip install llama-cpp-python
```

## 步骤 2：下载模型

你需要一个 GGUF 模型文件。以下是最简单的方法：

1. 前往 https://huggingface.co/bartowski/Meta-Llama-3-8B-Instruct-GGUF
2. 下载 `Meta-Llama-3-8B-Instruct-Q4_K_M.gguf`（约 5GB）
3. 将其放入 `models/` 目录
4. 重命名为 `llama-3-8b-instruct.gguf`（可选，为了简化）

**备选模型：**
- Mistral 7B: https://huggingface.co/bartowski/Mistral-7B-Instruct-v0.2-GGUF
- Gemma 7B: https://huggingface.co/bartowski/gemma-7b-it-GGUF

## 步骤 3：验证环境

```bash
python setup_check.py
```

这将检查：
- Python 版本
- 依赖项
- models 目录
- 仓库结构

## 步骤 4：运行示例

```bash
python complete_example.py
```

这将运行全部 10 课的所有示例。你也可以打开 `complete_example.py` 并修改模型路径，或注释掉你想跳过的课程。

## 步骤 6：开始学习

现在按顺序阅读课程：

1. `lessons/01_basic_llm_chat.md` - 理解基础知识
2. `lessons/02_system_prompt.md` - 添加行为设定
3. `lessons/03_structured_output.md` - 使其可靠
4. ……依此类推，直到第 10 课

每一课都建立在前一课的基础之上。

## 故障排查

### "Module 'llama_cpp' not found"

```bash
pip install llama-cpp-python
```

### "Model file not found"

请检查：
1. 模型文件是否在 `models/` 目录中
2. `complete_example.py` 中的路径是否与实际文件名匹配
3. 文件是否有 `.gguf` 扩展名

### "Out of memory" 错误

尝试更小的模型或更小的量化：
- Q4_K_M: 约 5GB RAM
- Q5_K_M: 约 6GB RAM
- Q8_0: 约 8GB RAM

### 响应缓慢

这在 CPU 推理中是正常的。每次响应需要 10-30 秒，具体取决于：
- 你的 CPU 速度
- 模型大小
- 响应长度

## 下一步

- **阅读 philosophy.md** 以理解本项目的思路
- **逐课学习**课程内容
- **修改 agent** 来进行实验
- **查看 examples/** 获取完整的代码示例

## 获取帮助

- 查看已有的 [GitHub Issues](https://github.com/your-repo/issues)
- 仔细阅读课程的 markdown 文件
- 在 [GitHub Discussions](https://github.com/your-repo/discussions) 中提问

## 成功秘诀

1. **不要跳过课程** —— 它们相互依存
2. **动手运行代码** —— 光读是不够的
3. **实验** —— 修改示例，看看会发生什么
4. **保持耐心** —— 本地推理虽然慢，但值得
5. **阅读注释** —— 代码中解释了「为什么」

祝你学习愉快！🚀
