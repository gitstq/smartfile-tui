"""
文件管理核心模块
"""

import asyncio
import fnmatch
import os
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable, List, Optional

import aiofiles
import aiofiles.os


@dataclass
class FileInfo:
    """文件信息数据类"""
    name: str
    path: str
    is_dir: bool
    size: int = 0
    modified_time: datetime = field(default_factory=datetime.now)
    permissions: str = ""
    is_symlink: bool = False
    symlink_target: Optional[str] = None
    
    @property
    def extension(self) -> str:
        """获取文件扩展名"""
        return Path(self.name).suffix.lower()
    
    @property
    def is_hidden(self) -> bool:
        """检查是否为隐藏文件"""
        return self.name.startswith(".")
    
    @property
    def formatted_size(self) -> str:
        """格式化文件大小"""
        if self.is_dir:
            return "<DIR>"
        size = self.size
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} PB"
    
    @property
    def formatted_time(self) -> str:
        """格式化修改时间"""
        return self.modified_time.strftime("%Y-%m-%d %H:%M")


class FileManager:
    """异步文件管理器"""
    
    def __init__(self):
        self.clipboard: List[str] = []
        self.clipboard_operation: Optional[str] = None  # 'copy' or 'cut'
        self._operation_callbacks: List[Callable] = []
    
    def add_operation_callback(self, callback: Callable) -> None:
        """添加操作回调"""
        self._operation_callbacks.append(callback)
    
    def _notify_callbacks(self, operation: str, paths: List[str]) -> None:
        """通知所有回调"""
        for callback in self._operation_callbacks:
            try:
                callback(operation, paths)
            except Exception:
                pass
    
    async def list_directory(
        self,
        path: str,
        show_hidden: bool = False,
        sort_by: str = "name",
        reverse: bool = False
    ) -> List[FileInfo]:
        """
        异步列出目录内容
        
        Args:
            path: 目录路径
            show_hidden: 是否显示隐藏文件
            sort_by: 排序方式 (name, size, time, type)
            reverse: 是否倒序
        """
        try:
            entries = []
            loop = asyncio.get_event_loop()
            
            # 获取目录内容
            for entry in await loop.run_in_executor(None, lambda: list(os.scandir(path))):
                # 跳过隐藏文件
                if not show_hidden and entry.name.startswith("."):
                    continue
                
                stat = entry.stat(follow_symlinks=False)
                info = FileInfo(
                    name=entry.name,
                    path=entry.path,
                    is_dir=entry.is_dir(follow_symlinks=False),
                    size=stat.st_size,
                    modified_time=datetime.fromtimestamp(stat.st_mtime),
                    permissions=oct(stat.st_mode)[-3:],
                    is_symlink=entry.is_symlink(),
                )
                
                if info.is_symlink:
                    try:
                        info.symlink_target = os.readlink(entry.path)
                    except OSError:
                        pass
                
                entries.append(info)
            
            # 排序
            sort_key = {
                "name": lambda x: x.name.lower(),
                "size": lambda x: (not x.is_dir, x.size),
                "time": lambda x: x.modified_time,
                "type": lambda x: (not x.is_dir, x.extension, x.name.lower()),
            }.get(sort_by, lambda x: x.name.lower())
            
            entries.sort(key=sort_key, reverse=reverse)
            return entries
            
        except PermissionError:
            return []
        except OSError:
            return []
    
    async def search_files(
        self,
        path: str,
        pattern: str,
        recursive: bool = True,
        show_hidden: bool = False
    ) -> List[FileInfo]:
        """
        搜索文件
        
        Args:
            path: 搜索起始路径
            pattern: 搜索模式 (支持通配符)
            recursive: 是否递归搜索
            show_hidden: 是否包含隐藏文件
        """
        results = []
        
        if recursive:
            for root, dirs, files in os.walk(path):
                # 过滤隐藏目录
                if not show_hidden:
                    dirs[:] = [d for d in dirs if not d.startswith(".")]
                
                for name in files + dirs:
                    if not show_hidden and name.startswith("."):
                        continue
                    
                    if fnmatch.fnmatch(name.lower(), pattern.lower()):
                        full_path = os.path.join(root, name)
                        try:
                            stat = os.stat(full_path)
                            results.append(FileInfo(
                                name=name,
                                path=full_path,
                                is_dir=os.path.isdir(full_path),
                                size=stat.st_size,
                                modified_time=datetime.fromtimestamp(stat.st_mtime),
                            ))
                        except OSError:
                            pass
        else:
            entries = await self.list_directory(path, show_hidden=show_hidden)
            for entry in entries:
                if fnmatch.fnmatch(entry.name.lower(), pattern.lower()):
                    results.append(entry)
        
        return results
    
    async def copy_to_clipboard(self, paths: List[str], operation: str = "copy") -> None:
        """
        复制文件到剪贴板
        
        Args:
            paths: 文件路径列表
            operation: 'copy' 或 'cut'
        """
        self.clipboard = paths.copy()
        self.clipboard_operation = operation
    
    async def paste_from_clipboard(self, target_dir: str) -> List[str]:
        """
        从剪贴板粘贴文件
        
        Args:
            target_dir: 目标目录
            
        Returns:
            操作成功的文件列表
        """
        if not self.clipboard or not self.clipboard_operation:
            return []
        
        results = []
        
        for src_path in self.clipboard:
            if not os.path.exists(src_path):
                continue
            
            name = os.path.basename(src_path)
            dst_path = os.path.join(target_dir, name)
            
            try:
                if self.clipboard_operation == "copy":
                    if os.path.isdir(src_path):
                        await asyncio.get_event_loop().run_in_executor(
                            None, lambda: shutil.copytree(src_path, dst_path)
                        )
                    else:
                        await asyncio.get_event_loop().run_in_executor(
                            None, lambda: shutil.copy2(src_path, dst_path)
                        )
                elif self.clipboard_operation == "cut":
                    await asyncio.get_event_loop().run_in_executor(
                        None, lambda: shutil.move(src_path, dst_path)
                    )
                
                results.append(dst_path)
            except (shutil.Error, OSError):
                pass
        
        # 如果是剪切操作，清空剪贴板
        if self.clipboard_operation == "cut":
            self.clipboard = []
            self.clipboard_operation = None
        
        self._notify_callbacks("paste", results)
        return results
    
    async def delete(self, paths: List[str]) -> List[str]:
        """
        删除文件或目录
        
        Args:
            paths: 要删除的路径列表
            
        Returns:
            成功删除的路径列表
        """
        results = []
        
        for path in paths:
            try:
                if os.path.isdir(path):
                    await asyncio.get_event_loop().run_in_executor(
                        None, lambda: shutil.rmtree(path)
                    )
                else:
                    await aiofiles.os.remove(path)
                results.append(path)
            except (OSError, shutil.Error):
                pass
        
        self._notify_callbacks("delete", results)
        return results
    
    async def rename(self, path: str, new_name: str) -> Optional[str]:
        """
        重命名文件或目录
        
        Args:
            path: 原路径
            new_name: 新名称
            
        Returns:
            新路径或None
        """
        try:
            parent = os.path.dirname(path)
            new_path = os.path.join(parent, new_name)
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: os.rename(path, new_path)
            )
            self._notify_callbacks("rename", [new_path])
            return new_path
        except OSError:
            return None
    
    async def create_directory(self, parent: str, name: str) -> Optional[str]:
        """
        创建目录
        
        Args:
            parent: 父目录
            name: 目录名
            
        Returns:
            新目录路径或None
        """
        try:
            path = os.path.join(parent, name)
            await aiofiles.os.makedirs(path, exist_ok=True)
            self._notify_callbacks("mkdir", [path])
            return path
        except OSError:
            return None
    
    async def create_file(self, parent: str, name: str) -> Optional[str]:
        """
        创建空文件
        
        Args:
            parent: 父目录
            name: 文件名
            
        Returns:
            新文件路径或None
        """
        try:
            path = os.path.join(parent, name)
            async with aiofiles.open(path, "w"):
                pass
            self._notify_callbacks("touch", [path])
            return path
        except OSError:
            return None
    
    async def get_preview(self, path: str, max_lines: int = 50) -> str:
        """
        获取文件预览内容
        
        Args:
            path: 文件路径
            max_lines: 最大行数
            
        Returns:
            预览内容
        """
        if os.path.isdir(path):
            try:
                entries = os.listdir(path)[:max_lines]
                return "\n".join(entries) if entries else "<空目录>"
            except PermissionError:
                return "<无权限访问>"
        
        # 尝试读取文本文件
        try:
            async with aiofiles.open(path, "r", encoding="utf-8", errors="ignore") as f:
                lines = []
                for _ in range(max_lines):
                    line = await f.readline()
                    if not line:
                        break
                    lines.append(line.rstrip())
                return "\n".join(lines) if lines else "<空文件>"
        except (UnicodeDecodeError, OSError):
            return "<二进制文件>"
