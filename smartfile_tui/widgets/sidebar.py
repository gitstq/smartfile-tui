"""
侧边栏Widget
"""

from textual.containers import Vertical
from textual.widgets import Label, Static, Tree

from ..config import Config


class Sidebar(Vertical):
    """侧边栏组件"""
    
    DEFAULT_CSS = """
    Sidebar {
        width: 100%;
        height: 100%;
        padding: 1;
    }
    
    Sidebar Static {
        width: 100%;
        height: auto;
    }
    
    Sidebar Tree {
        width: 100%;
        height: 1fr;
        border: none;
    }
    
    Sidebar .sidebar-title {
        text-style: bold;
        color: $primary;
        text-align: center;
        padding: 1;
    }
    
    Sidebar .section-title {
        text-style: bold;
        color: $secondary;
        padding-top: 1;
    }
    
    Sidebar .info-item {
        color: $text-muted;
        padding-left: 1;
    }
    """
    
    def __init__(self, config: Config):
        super().__init__()
        self.config = config
    
    def compose(self):
        """构建组件"""
        yield Static("SmartFile", classes="sidebar-title")
        
        # 书签部分
        yield Static("🔖 书签", classes="section-title")
        yield self._create_bookmarks_tree()
        
        # 最近访问
        yield Static("🕐 最近访问", classes="section-title")
        yield self._create_recent_tree()
        
        # 快捷键提示
        yield Static("⌨️ 快捷键", classes="section-title")
        yield Static(
            "↑↓/jk: 导航\n"
            "Enter: 打开\n"
            "Space: 选择\n"
            "/: 搜索\n"
            "?: 帮助\n"
            "q: 退出",
            classes="info-item"
        )
    
    def _create_bookmarks_tree(self) -> Tree:
        """创建书签树"""
        tree = Tree("书签", id="bookmarks-tree")
        
        for name, path in self.config.bookmarks.items():
            tree.add_leaf(f"{name}: {path}")
        
        if not self.config.bookmarks:
            tree.add_leaf("<无书签>")
        
        return tree
    
    def _create_recent_tree(self) -> Tree:
        """创建最近访问树"""
        tree = Tree("最近访问", id="recent-tree")
        
        for path in self.config.recent_paths[:10]:
            display = path
            if len(display) > 25:
                display = "..." + display[-22:]
            tree.add_leaf(display)
        
        if not self.config.recent_paths:
            tree.add_leaf("<无记录>")
        
        return tree
    
    def refresh(self):
        """刷新侧边栏"""
        self.remove_children()
        self.compose()
