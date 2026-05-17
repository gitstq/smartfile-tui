"""
Textual TUI 应用主模块
"""

from pathlib import Path
from typing import Optional

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import (
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    Static,
    Tree,
)

from .config import Config
from .file_manager import FileInfo, FileManager
from .widgets.file_list import FileList
from .widgets.preview import PreviewPanel
from .widgets.sidebar import Sidebar


class SmartFileApp(App):
    """SmartFile TUI 应用"""
    
    CSS = """
    Screen {
        layout: grid;
        grid-size: 3 1;
        grid-columns: 25 2fr 1fr;
    }
    
    #sidebar {
        width: 100%;
        height: 100%;
        border-right: solid $primary;
    }
    
    #file-list-container {
        width: 100%;
        height: 100%;
        border-right: solid $primary;
    }
    
    #preview-panel {
        width: 100%;
        height: 100%;
    }
    
    #search-input {
        dock: top;
        height: 3;
        display: none;
    }
    
    #search-input.visible {
        display: block;
    }
    
    .title {
        text-style: bold;
        color: $primary;
    }
    
    .info {
        color: $text-muted;
    }
    
    .error {
        color: $error;
    }
    
    .success {
        color: $success;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "退出"),
        Binding("?", "show_help", "帮助"),
        Binding("/", "toggle_search", "搜索"),
        Binding("r", "refresh", "刷新"),
        Binding(".", "toggle_hidden", "隐藏文件"),
        Binding("p", "toggle_preview", "预览"),
        Binding("b", "show_bookmarks", "书签"),
        Binding("space", "select", "选择"),
        Binding("c", "copy", "复制"),
        Binding("x", "cut", "剪切"),
        Binding("v", "paste", "粘贴"),
        Binding("d", "delete", "删除"),
        Binding("R", "rename", "重命名"),
        Binding("n", "new_file", "新建文件"),
        Binding("N", "new_dir", "新建目录"),
    ]
    
    current_path = reactive(str(Path.home()))
    selected_files = reactive(set)
    show_hidden = reactive(False)
    show_preview_panel = reactive(True)
    search_mode = reactive(False)
    
    def __init__(self, start_path: str, config: Config):
        super().__init__()
        self.current_path = start_path
        self.config = config
        self.file_manager = FileManager()
        self.show_hidden = config.show_hidden
        self.show_preview_panel = config.show_preview
        
        # 添加文件操作回调
        self.file_manager.add_operation_callback(self._on_file_operation)
    
    def compose(self) -> ComposeResult:
        """构建UI"""
        yield Header(show_clock=True)
        
        # 搜索输入框
        yield Input(
            placeholder="输入搜索模式 (支持通配符 *, ?)...",
            id="search-input",
        )
        
        # 侧边栏
        with Vertical(id="sidebar"):
            yield Sidebar(config=self.config)
        
        # 文件列表
        with Vertical(id="file-list-container"):
            yield FileList(
                file_manager=self.file_manager,
                show_hidden=self.show_hidden,
            )
        
        # 预览面板
        with Vertical(id="preview-panel"):
            yield PreviewPanel(file_manager=self.file_manager)
        
        yield Footer()
    
    def on_mount(self) -> None:
        """挂载后初始化"""
        self.title = "SmartFile-TUI"
        self.sub_title = self.current_path
        
        # 加载当前目录
        self._load_directory()
    
    def watch_current_path(self, path: str) -> None:
        """监听路径变化"""
        self.sub_title = path
        self.config.add_recent(path)
        self._load_directory()
    
    def watch_show_hidden(self, show: bool) -> None:
        """监听隐藏文件设置变化"""
        self.config.show_hidden = show
        self.config.save()
        self._load_directory()
    
    def watch_show_preview_panel(self, show: bool) -> None:
        """监听预览面板设置变化"""
        self.config.show_preview = show
        self.config.save()
        preview = self.query_one("#preview-panel", Vertical)
        preview.display = show
    
    def watch_search_mode(self, active: bool) -> None:
        """监听搜索模式变化"""
        search_input = self.query_one("#search-input", Input)
        if active:
            search_input.add_class("visible")
            search_input.focus()
        else:
            search_input.remove_class("visible")
            file_list = self.query_one(FileList)
            file_list.focus()
    
    async def _load_directory(self) -> None:
        """加载目录内容"""
        file_list = self.query_one(FileList)
        await file_list.load_directory(self.current_path)
        
        # 更新预览
        preview = self.query_one(PreviewPanel)
        await preview.update_preview(None)
    
    def _on_file_operation(self, operation: str, paths: list) -> None:
        """文件操作回调"""
        self.notify(f"{operation}: {len(paths)} 项", severity="information")
        self._load_directory()
    
    # ========== 动作处理 ==========
    
    def action_toggle_search(self) -> None:
        """切换搜索模式"""
        self.search_mode = not self.search_mode
    
    def action_refresh(self) -> None:
        """刷新"""
        self._load_directory()
    
    def action_toggle_hidden(self) -> None:
        """切换隐藏文件显示"""
        self.show_hidden = not self.show_hidden
    
    def action_toggle_preview(self) -> None:
        """切换预览面板"""
        self.show_preview_panel = not self.show_preview_panel
    
    def action_show_bookmarks(self) -> None:
        """显示书签"""
        # TODO: 实现书签对话框
        self.notify("书签功能开发中...", severity="warning")
    
    def action_show_help(self) -> None:
        """显示帮助"""
        help_text = """
        # SmartFile-TUI 快捷键
        
        ## 导航
        - ↑/↓ 或 j/k: 上下移动
        - ←/→ 或 h/l: 进入/退出目录
        - Enter: 打开文件/进入目录
        - Backspace: 返回上级
        
        ## 文件操作
        - Space: 选择/取消选择
        - c: 复制到剪贴板
        - x: 剪切到剪贴板
        - v: 粘贴
        - d: 删除
        - R: 重命名
        - n: 新建文件
        - N: 新建目录
        
        ## 视图
        - /: 搜索
        - .: 切换隐藏文件
        - p: 切换预览面板
        - b: 书签
        - r: 刷新
        
        ## 其他
        - q: 退出
        - ?: 显示帮助
        """
        self.notify(help_text, title="帮助", timeout=10)
    
    # ========== 事件处理 ==========
    
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """搜索输入提交"""
        if event.input.id == "search-input":
            pattern = event.value
            if pattern:
                file_list = self.query_one(FileList)
                await file_list.search(self.current_path, pattern)
            self.search_mode = False
    
    async def on_input_changed(self, event: Input.Changed) -> None:
        """搜索输入变化"""
        if event.input.id == "search-input":
            pattern = event.value
            if pattern:
                file_list = self.query_one(FileList)
                await file_list.search(self.current_path, pattern)
    
    async def on_file_list_selection_changed(self, event) -> None:
        """文件选择变化"""
        preview = self.query_one(PreviewPanel)
        await preview.update_preview(event.file_info)
    
    async def on_file_list_path_changed(self, event) -> None:
        """路径变化"""
        self.current_path = event.path
    
    async def on_file_list_file_opened(self, event) -> None:
        """文件被打开"""
        if event.file_info.is_dir:
            self.current_path = event.file_info.path
        else:
            # 使用系统默认程序打开文件
            import subprocess
            import platform
            
            system = platform.system()
            try:
                if system == "Darwin":
                    subprocess.run(["open", event.file_info.path])
                elif system == "Linux":
                    subprocess.run(["xdg-open", event.file_info.path])
                elif system == "Windows":
                    subprocess.run(["start", event.file_info.path], shell=True)
            except Exception as e:
                self.notify(f"无法打开文件: {e}", severity="error")
