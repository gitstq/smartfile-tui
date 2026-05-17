"""
配置管理模块
"""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from platformdirs import user_config_dir


@dataclass
class Config:
    """应用配置类"""

    # 主题设置
    theme: str = "dark"
    
    # 文件显示设置
    show_hidden: bool = False
    show_preview: bool = True
    preview_max_lines: int = 50
    
    # 搜索设置
    fuzzy_search: bool = True
    case_sensitive: bool = False
    
    # AI设置 (可选)
    ai_enabled: bool = False
    ai_provider: str = "openai"  # openai, anthropic
    ai_api_key: str = ""
    ai_model: str = "gpt-3.5-turbo"
    
    # 快捷键设置
    keybindings: dict[str, str] = field(default_factory=lambda: {
        "quit": "q",
        "up": "up,k",
        "down": "down,j",
        "left": "left,h",
        "right": "right,l,enter",
        "select": "space",
        "search": "/",
        "help": "?",
        "refresh": "r,F5",
        "toggle_hidden": ".",
        "toggle_preview": "p",
        "bookmark": "b",
        "create_dir": "mkdir",
        "create_file": "touch",
        "delete": "delete,d",
        "rename": "rename,R",
        "copy": "copy,c",
        "paste": "paste,v",
        "cut": "cut,x",
    })
    
    # 书签
    bookmarks: dict[str, str] = field(default_factory=dict)
    
    # 最近访问
    recent_paths: list[str] = field(default_factory=list)
    max_recent: int = 20
    
    # 配置文件路径
    config_path: str | None = None

    def __post_init__(self):
        if self.config_path:
            self.load(self.config_path)
        else:
            # 使用默认配置路径
            config_dir = Path(user_config_dir("smartfile", "smartfile"))
            config_dir.mkdir(parents=True, exist_ok=True)
            self.config_path = str(config_dir / "config.json")
            if Path(self.config_path).exists():
                self.load(self.config_path)

    def load(self, path: str) -> None:
        """从文件加载配置"""
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for key, value in data.items():
                if hasattr(self, key):
                    setattr(self, key, value)
        except (json.JSONDecodeError, FileNotFoundError):
            pass  # 使用默认配置

    def save(self) -> None:
        """保存配置到文件"""
        if self.config_path:
            data = {
                "theme": self.theme,
                "show_hidden": self.show_hidden,
                "show_preview": self.show_preview,
                "preview_max_lines": self.preview_max_lines,
                "fuzzy_search": self.fuzzy_search,
                "case_sensitive": self.case_sensitive,
                "ai_enabled": self.ai_enabled,
                "ai_provider": self.ai_provider,
                "ai_model": self.ai_model,
                "keybindings": self.keybindings,
                "bookmarks": self.bookmarks,
                "recent_paths": self.recent_paths,
                "max_recent": self.max_recent,
            }
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

    def add_recent(self, path: str) -> None:
        """添加最近访问路径"""
        if path in self.recent_paths:
            self.recent_paths.remove(path)
        self.recent_paths.insert(0, path)
        self.recent_paths = self.recent_paths[: self.max_recent]
        self.save()

    def add_bookmark(self, name: str, path: str) -> None:
        """添加书签"""
        self.bookmarks[name] = path
        self.save()

    def remove_bookmark(self, name: str) -> None:
        """删除书签"""
        if name in self.bookmarks:
            del self.bookmarks[name]
            self.save()
