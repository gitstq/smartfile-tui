#!/usr/bin/env python3
"""
构建脚本 - 支持多平台打包
"""

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], cwd: str | None = None) -> bool:
    """运行命令"""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"命令失败: {' '.join(cmd)}")
        print(f"错误: {e.stderr}")
        return False


def clean_build():
    """清理构建目录"""
    dirs_to_remove = ["build", "dist", "*.egg-info", ".pytest_cache", ".mypy_cache"]
    for pattern in dirs_to_remove:
        for path in Path(".").glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
                print(f"已删除: {path}")


def install_dependencies():
    """安装依赖"""
    print("📦 安装依赖...")
    return run_command([sys.executable, "-m", "pip", "install", "-e", "."])


def build_wheel():
    """构建wheel包"""
    print("📦 构建Wheel包...")
    return run_command([sys.executable, "-m", "pip", "install", "build"]) and \
           run_command([sys.executable, "-m", "build", "--wheel"])


def build_executable():
    """使用PyInstaller构建可执行文件"""
    print("🔨 构建可执行文件...")
    
    # 安装PyInstaller
    if not run_command([sys.executable, "-m", "pip", "install", "pyinstaller"]):
        return False
    
    system = platform.system()
    
    # 基础命令
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", "smartfile",
        "--onefile",
        "--clean",
        "--noconfirm",
    ]
    
    # 系统特定选项
    if system == "Windows":
        cmd.extend(["--console", "--icon", "NONE"])
    else:
        cmd.append("--console")
    
    # 隐藏导入
    cmd.extend([
        "--hidden-import", "textual.widgets",
        "--hidden-import", "rich",
    ])
    
    # 入口点
    cmd.append("smartfile_tui/main.py")
    
    return run_command(cmd)


def run_tests():
    """运行测试"""
    print("🧪 运行测试...")
    return run_command([sys.executable, "-m", "pytest", "-v"])


def run_linters():
    """运行代码检查"""
    print("🔍 运行代码检查...")
    
    # Black格式化检查
    black_ok = run_command([sys.executable, "-m", "black", "--check", "smartfile_tui"])
    
    # Ruff检查
    ruff_ok = run_command([sys.executable, "-m", "ruff", "check", "smartfile_tui"])
    
    # MyPy类型检查
    mypy_ok = run_command([sys.executable, "-m", "mypy", "smartfile_tui"])
    
    return black_ok and ruff_ok and mypy_ok


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="SmartFile-TUI 构建脚本")
    parser.add_argument(
        "command",
        choices=["clean", "install", "test", "lint", "wheel", "exe", "all"],
        help="构建命令",
    )
    
    args = parser.parse_args()
    
    success = True
    
    if args.command == "clean":
        clean_build()
    elif args.command == "install":
        success = install_dependencies()
    elif args.command == "test":
        success = run_tests()
    elif args.command == "lint":
        success = run_linters()
    elif args.command == "wheel":
        success = build_wheel()
    elif args.command == "exe":
        success = build_executable()
    elif args.command == "all":
        clean_build()
        success = (
            install_dependencies() and
            run_tests() and
            run_linters() and
            build_wheel() and
            build_executable()
        )
    
    if success:
        print("✅ 构建成功!")
        return 0
    else:
        print("❌ 构建失败!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
