#!/usr/bin/env python3
"""
安装验证脚本

安装依赖后运行此脚本以验证你的设置是否正确。
"""

import sys
import os


def check_python_version():
    """检查 Python 版本是否为 3.10 以上"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print("❌ 需要 Python 3.10 以上版本")
        print(f"   当前版本：{version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True


def check_dependencies():
    """检查是否已安装所需的包"""
    try:
        import llama_cpp
        print("✅ llama-cpp-python 已安装")
        return True
    except ImportError:
        print("❌ 未找到 llama-cpp-python")
        print("   安装方式：pip install llama-cpp-python")
        return False


def check_model_directory():
    """检查 models 目录是否存在"""
    if os.path.isdir("models"):
        print("✅ models/ 目录存在")

        # 检查 GGUF 文件
        files = [f for f in os.listdir("models") if f.endswith(".gguf")]
        if files:
            print(f"✅ 找到 {len(files)} 个 GGUF 模型：")
            for f in files:
                size_mb = os.path.getsize(f"models/{f}") / (1024**2)
                print(f"   - {f} ({size_mb:.1f} MB)")
        else:
            print("⚠️  在 models/ 中未找到 GGUF 模型")
            print("   请下载一个模型并将其放入 models/ 中")
        return True
    else:
        print("❌ 未找到 models/ 目录")
        return False


def check_structure():
    """检查仓库结构"""
    required_dirs = ["shared", "agent", "lessons"]
    all_exist = True

    for dir_name in required_dirs:
        if os.path.isdir(dir_name):
            print(f"✅ {dir_name}/ 目录存在")
        else:
            print(f"❌ 未找到 {dir_name}/ 目录")
            all_exist = False

    return all_exist


def main():
    """运行所有检查"""
    print("="*50)
    print("从零开始的 AI Agent——安装验证")
    print("="*50)
    print()

    checks = [
        ("Python 版本", check_python_version),
        ("依赖项", check_dependencies),
        ("Models 目录", check_model_directory),
        ("仓库结构", check_structure),
    ]

    results = []

    for name, check_func in checks:
        print(f"\n{name}：")
        results.append(check_func())

    print("\n" + "="*50)
    if all(results):
        print("✅ 所有检查已通过！你可以开始学习了。")
        print("\n下一步：")
        print("1. 阅读 lessons/01_basic_llm_chat.md")
        print("2. 运行：python complete_example.py")
    else:
        print("⚠️  部分检查未通过。请修复上述问题。")
    print("="*50)


if __name__ == "__main__":
    main()
