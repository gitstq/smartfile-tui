#!/usr/bin/env python3
"""
SmartFile-TUI 主入口模块
"""

import asyncio
import os
import sys
from pathlib import Path

import click
from rich.console import Console

from .app import SmartFileApp
from .config import Config

console = Console()


@click.command()
@click.option(
    "--path",
    "-p",
    default=".",
    help="起始目录路径 (默认: 当前目录)",
)
@click.option(
    "--config",
    "-c",
    type=click.Path(),
    help="配置文件路径",
)
@click.option(
    "--theme",
    "-t",
    default="dark",
    type=click.Choice(["dark", "light", "dracula", "nord", "monokai"]),
    help="UI主题",
)
@click.version_option(version=__import__("smartfile_tui").__version__, prog_name="smartfile")
def main(path: str, config: str | None, theme: str) -> None:
    """
    🚀 SmartFile-TUI - AI驱动的智能终端文件管理器
    
    使用键盘快捷键导航:
    
        ↑/↓ 或 j/k    移动光标
        Enter/l       进入目录/打开文件
        Backspace/h   返回上级目录
        Space         选择/取消选择
        /             搜索
        q             退出
        ?             显示帮助
    """
    try:
        # 验证路径
        start_path = Path(path).resolve()
        if not start_path.exists():
            console.print(f"[red]错误: 路径不存在: {path}[/red]")
            sys.exit(1)
        if not start_path.is_dir():
            console.print(f"[red]错误: 不是目录: {path}[/red]")
            sys.exit(1)

        # 加载配置
        config_obj = Config(config_path=config)
        config_obj.theme = theme

        # 启动应用
        app = SmartFileApp(start_path=str(start_path), config=config_obj)
        app.run()

    except KeyboardInterrupt:
        console.print("\n[yellow]已取消[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]错误: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
