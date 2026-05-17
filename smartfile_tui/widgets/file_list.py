"""
文件列表Widget
"""

from pathlib import Path
from typing import List, Optional

from rich.text import Text
from textual.containers import Vertical
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import DataTable, Static

from ..file_manager import FileInfo, FileManager


class FileList(Vertical):
    """文件列表组件"""
    
    DEFAULT_CSS = """
    FileList {
        width: 100%;
        height: 100%;
    }
    
    FileList DataTable {
        width: 100%;
        height: 100%;
        border: none;
    }
    
    FileList DataTable > .datatable--cursor {
        background: $primary-darken-2;
    }
    
    FileList DataTable > .datatable--hover {
        background: $primary-darken-1;
    }
    
    FileList .selected {
        background: $success-darken-2;
    }
    
    FileList .directory {
        color: $primary;
        text-style: bold;
    }
    
    FileList .hidden {
        color: $text-muted;
    }
    
    FileList .symlink {
        color: $warning;
    }
    """
    
    files = reactive(list)
    selected_indices = reactive(set)
    cursor_index = reactive(0)
    
    class SelectionChanged(Message):
        """选择变化消息"""
        def __init__(self, file_info: Optional[FileInfo]) -> None:
            self.file_info = file_info
            super().__init__()
    
    class PathChanged(Message):
        """路径变化消息"""
        def __init__(self, path: str) -> None:
            self.path = path
            super().__init__()
    
    class FileOpened(Message):
        """文件打开消息"""
        def __init__(self, file_info: FileInfo) -> None:
            self.file_info = file_info
            super().__init__()
    
    def __init__(self, file_manager: FileManager, show_hidden: bool = False):
        super().__init__()
        self.file_manager = file_manager
        self.show_hidden = show_hidden
        self.current_path = ""
        self._loading = False
    
    def compose(self):
        """构建组件"""
        yield DataTable(
            id="file-table",
            show_cursor=True,
            cursor_type="row",
        )
    
    def on_mount(self):
        """挂载后初始化"""
        table = self.query_one(DataTable)
        table.add_columns(
            "名称",
            "大小",
            "修改时间",
            "权限",
        )
        table.focus()
    
    async def load_directory(self, path: str) -> None:
        """加载目录内容"""
        if self._loading:
            return
        
        self._loading = True
        self.current_path = path
        self.selected_indices = set()
        self.cursor_index = 0
        
        try:
            files = await self.file_manager.list_directory(
                path, 
                show_hidden=self.show_hidden,
                sort_by="type",  # 目录在前
            )
            self.files = files
            self._update_table()
        except Exception:
            pass
        finally:
            self._loading = False
    
    async def search(self, path: str, pattern: str) -> None:
        """搜索文件"""
        if self._loading:
            return
        
        self._loading = True
        self.selected_indices = set()
        
        try:
            files = await self.file_manager.search_files(
                path,
                pattern,
                recursive=True,
                show_hidden=self.show_hidden,
            )
            self.files = files
            self._update_table()
        except Exception:
            pass
        finally:
            self._loading = False
    
    def _update_table(self):
        """更新表格显示"""
        table = self.query_one(DataTable)
        table.clear()
        
        for idx, file_info in enumerate(self.files):
            # 名称列
            name_text = Text(file_info.name)
            if file_info.is_dir:
                name_text.stylize("bold")
                name_text = Text("📁 ") + name_text
            elif file_info.is_symlink:
                name_text = Text("🔗 ") + name_text
            else:
                name_text = Text("📄 ") + name_text
            
            if file_info.is_hidden:
                name_text.stylize("dim")
            
            # 添加行
            table.add_row(
                name_text,
                file_info.formatted_size,
                file_info.formatted_time,
                file_info.permissions,
                key=str(idx),
            )
            
            # 高亮选中项
            if idx in self.selected_indices:
                table.update_cell(str(idx), 0, name_text, style="reverse")
        
        # 恢复光标位置
        if self.files and self.cursor_index < len(self.files):
            table.move_cursor(row=self.cursor_index)
    
    def watch_cursor_index(self, index: int):
        """监听光标变化"""
        if 0 <= index < len(self.files):
            file_info = self.files[index]
            self.post_message(self.SelectionChanged(file_info))
    
    def on_data_table_cursor_moved(self, event):
        """光标移动事件"""
        self.cursor_index = event.cursor_row
    
    def on_data_table_row_selected(self, event):
        """行选中事件"""
        if event.cursor_row is not None:
            self.cursor_index = event.cursor_row
            if 0 <= event.cursor_row < len(self.files):
                file_info = self.files[event.cursor_row]
                self.post_message(self.FileOpened(file_info))
    
    def action_select(self):
        """选择/取消选择当前项"""
        if self.cursor_index < len(self.files):
            if self.cursor_index in self.selected_indices:
                self.selected_indices.remove(self.cursor_index)
            else:
                self.selected_indices.add(self.cursor_index)
            self._update_table()
    
    def action_navigate_up(self):
        """导航到上级目录"""
        parent = Path(self.current_path).parent
        if str(parent) != self.current_path:
            self.post_message(self.PathChanged(str(parent)))
    
    def action_navigate_into(self):
        """进入当前目录"""
        if self.cursor_index < len(self.files):
            file_info = self.files[self.cursor_index]
            if file_info.is_dir:
                self.post_message(self.PathChanged(file_info.path))
    
    def get_selected_files(self) -> List[FileInfo]:
        """获取选中的文件列表"""
        if self.selected_indices:
            return [self.files[i] for i in self.selected_indices if i < len(self.files)]
        elif self.cursor_index < len(self.files):
            return [self.files[self.cursor_index]]
        return []
