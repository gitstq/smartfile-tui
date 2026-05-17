"""
文件预览Widget
"""

from pathlib import Path
from typing import Optional

from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text
from textual.containers import Vertical
from textual.reactive import reactive
from textual.widgets import Label, Static

from ..file_manager import FileInfo, FileManager


class PreviewPanel(Vertical):
    """文件预览面板"""
    
    DEFAULT_CSS = """
    PreviewPanel {
        width: 100%;
        height: 100%;
        padding: 1;
    }
    
    PreviewPanel Static {
        width: 100%;
        height: 100%;
    }
    
    PreviewPanel .preview-title {
        text-style: bold;
        color: $primary;
        text-align: center;
    }
    
    PreviewPanel .preview-content {
        color: $text;
    }
    
    PreviewPanel .preview-info {
        color: $text-muted;
        text-align: center;
    }
    """
    
    current_file = reactive(None)
    preview_content = reactive("")
    
    def __init__(self, file_manager: FileManager):
        super().__init__()
        self.file_manager = file_manager
        self.max_lines = 50
    
    def compose(self):
        """构建组件"""
        yield Static(id="preview-content")
    
    async def update_preview(self, file_info: Optional[FileInfo]):
        """更新预览内容"""
        self.current_file = file_info
        
        if file_info is None:
            self.preview_content = self._render_empty()
        else:
            content = await self._render_preview(file_info)
            self.preview_content = content
        
        self._update_display()
    
    def _render_empty(self) -> str:
        """渲染空状态"""
        return """
        [center]
        [bold primary]SmartFile-TUI[/bold primary]
        
        AI驱动的智能终端文件管理器
        
        使用 ↑↓ 或 j/k 导航
        按 Enter 打开文件
        按 ? 查看帮助
        [/center]
        """
    
    async def _render_preview(self, file_info: FileInfo) -> str:
        """渲染文件预览"""
        lines = []
        
        # 标题
        icon = "📁" if file_info.is_dir else "📄"
        lines.append(f"[bold primary]{icon} {file_info.name}[/bold primary]")
        lines.append("")
        
        # 基本信息
        lines.append(f"[dim]路径:[/dim] {file_info.path}")
        lines.append(f"[dim]类型:[/dim] {'目录' if file_info.is_dir else '文件'}")
        lines.append(f"[dim]大小:[/dim] {file_info.formatted_size}")
        lines.append(f"[dim]修改时间:[/dim] {file_info.formatted_time}")
        lines.append(f"[dim]权限:[/dim] {file_info.permissions}")
        
        if file_info.is_symlink and file_info.symlink_target:
            lines.append(f"[dim]链接目标:[/dim] {file_info.symlink_target}")
        
        lines.append("")
        lines.append("─" * 40)
        lines.append("")
        
        # 内容预览
        if file_info.is_dir:
            # 目录内容预览
            try:
                preview = await self.file_manager.get_preview(
                    file_info.path, 
                    max_lines=self.max_lines
                )
                lines.append("[bold]目录内容:[/bold]")
                lines.append(preview)
            except Exception as e:
                lines.append(f"[error]无法读取目录: {e}[/error]")
        else:
            # 文件内容预览
            try:
                preview = await self.file_manager.get_preview(
                    file_info.path,
                    max_lines=self.max_lines
                )
                
                # 尝试语法高亮
                ext = Path(file_info.name).suffix.lower()
                if ext in self._get_syntax_extensions():
                    lines.append(f"[bold]文件预览 ({ext}):[/bold]")
                    lines.append("")
                    lines.append(preview)
                else:
                    lines.append("[bold]文件预览:[/bold]")
                    lines.append("")
                    lines.append(preview)
                    
            except Exception as e:
                lines.append(f"[error]无法读取文件: {e}[/error]")
        
        return "\n".join(lines)
    
    def _get_syntax_extensions(self) -> set:
        """获取支持语法高亮的扩展名"""
        return {
            '.py', '.js', '.ts', '.jsx', '.tsx',
            '.java', '.c', '.cpp', '.h', '.hpp',
            '.go', '.rs', '.rb', '.php',
            '.html', '.htm', '.xml', '.css', '.scss', '.sass',
            '.json', '.yaml', '.yml', '.toml', '.ini',
            '.md', '.rst', '.txt',
            '.sh', '.bash', '.zsh', '.fish',
            '.sql', '.vim', '.lua',
        }
    
    def _update_display(self):
        """更新显示"""
        static = self.query_one("#preview-content", Static)
        static.update(self.preview_content)
    
    def watch_preview_content(self, content: str):
        """监听内容变化"""
        self._update_display()
