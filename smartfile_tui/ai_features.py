"""
AI功能模块（可选）

提供AI驱动的文件智能分类、语义搜索等功能
"""

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class FileClassification:
    """文件分类结果"""
    category: str
    tags: List[str]
    confidence: float


class AIFileClassifier:
    """AI文件分类器"""
    
    # 本地规则分类（无需API）
    CATEGORY_RULES = {
        "代码": [".py", ".js", ".ts", ".java", ".cpp", ".c", ".go", ".rs", ".rb", ".php"],
        "Web": [".html", ".htm", ".css", ".scss", ".sass", ".less"],
        "数据": [".json", ".xml", ".yaml", ".yml", ".csv", ".sql"],
        "文档": [".md", ".txt", ".rst", ".doc", ".docx", ".pdf"],
        "配置": [".conf", ".config", ".ini", ".env", ".toml"],
        "媒体": [".jpg", ".jpeg", ".png", ".gif", ".mp4", ".mp3", ".wav"],
        "压缩": [".zip", ".tar", ".gz", ".bz2", ".7z", ".rar"],
        "可执行": [".exe", ".sh", ".bat", ".bin"],
    }
    
    TAG_PATTERNS = {
        "Python": [".py", ".pyw", ".pyi"],
        "JavaScript": [".js", ".mjs", ".cjs"],
        "TypeScript": [".ts", ".tsx"],
        "React": [".jsx", ".tsx"],
        "Java": [".java", ".jar", ".class"],
        "C/C++": [".c", ".cpp", ".h", ".hpp"],
        "Go": [".go"],
        "Rust": [".rs"],
        "Ruby": [".rb"],
        "PHP": [".php"],
        "文档": [".md", ".txt", ".rst"],
        "图片": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"],
        "视频": [".mp4", ".avi", ".mkv", ".mov", ".wmv"],
        "音频": [".mp3", ".wav", ".flac", ".aac", ".ogg"],
        "压缩": [".zip", ".tar", ".gz", ".bz2", ".7z", ".rar"],
    }
    
    def classify(self, filename: str) -> FileClassification:
        """
        根据文件名和扩展名分类文件
        
        Args:
            filename: 文件名
            
        Returns:
            分类结果
        """
        ext = Path(filename).suffix.lower()
        
        # 确定类别
        category = "其他"
        for cat, extensions in self.CATEGORY_RULES.items():
            if ext in extensions:
                category = cat
                break
        
        # 确定标签
        tags = []
        for tag, extensions in self.TAG_PATTERNS.items():
            if ext in extensions:
                tags.append(tag)
        
        # 根据文件名添加额外标签
        name_lower = filename.lower()
        if "test" in name_lower or "spec" in name_lower:
            tags.append("测试")
        if "config" in name_lower or "setting" in name_lower:
            tags.append("配置")
        if "readme" in name_lower:
            tags.append("文档")
        if "docker" in name_lower:
            tags.append("Docker")
        if "makefile" in name_lower or ".mk" in name_lower:
            tags.append("构建")
        
        # 计算置信度
        confidence = 0.8 if tags else 0.5
        
        return FileClassification(
            category=category,
            tags=tags,
            confidence=confidence,
        )
    
    def batch_classify(self, filenames: List[str]) -> Dict[str, FileClassification]:
        """
        批量分类文件
        
        Args:
            filenames: 文件名列表
            
        Returns:
            分类结果字典
        """
        return {name: self.classify(name) for name in filenames}


class SemanticSearch:
    """语义搜索（基于简单关键词匹配）"""
    
    # 同义词映射
    SYNONYMS = {
        "代码": ["code", "program", "script", "source"],
        "文档": ["doc", "document", "readme", "guide", "manual"],
        "配置": ["config", "configuration", "setting", "preference"],
        "图片": ["image", "photo", "picture", "graphic"],
        "视频": ["video", "movie", "film"],
        "音频": ["audio", "music", "sound"],
        "压缩": ["archive", "zip", "compressed"],
    }
    
    def search(self, query: str, filenames: List[str]) -> List[tuple]:
        """
        语义搜索文件
        
        Args:
            query: 搜索查询
            filenames: 文件名列表
            
        Returns:
            匹配的文件和分数列表
        """
        query_lower = query.lower()
        results = []
        
        # 扩展查询词
        expanded_terms = [query_lower]
        for key, synonyms in self.SYNONYMS.items():
            if query_lower in synonyms or query_lower == key:
                expanded_terms.extend(synonyms)
                expanded_terms.append(key)
        
        for filename in filenames:
            score = 0
            name_lower = filename.lower()
            
            # 精确匹配
            if query_lower in name_lower:
                score += 10
            
            # 扩展词匹配
            for term in expanded_terms:
                if term in name_lower:
                    score += 5
            
            # 分类匹配
            classifier = AIFileClassifier()
            classification = classifier.classify(filename)
            
            if query_lower in classification.category.lower():
                score += 8
            
            for tag in classification.tags:
                if query_lower in tag.lower():
                    score += 3
            
            if score > 0:
                results.append((filename, score))
        
        # 按分数排序
        results.sort(key=lambda x: x[1], reverse=True)
        return results


class FileUsageAnalyzer:
    """文件使用分析器"""
    
    def __init__(self, cache_dir: Optional[str] = None):
        self.cache_dir = cache_dir or os.path.expanduser("~/.smartfile/cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        self.usage_file = os.path.join(self.cache_dir, "usage_stats.json")
        self.usage_stats = self._load_stats()
    
    def _load_stats(self) -> Dict:
        """加载使用统计"""
        if os.path.exists(self.usage_file):
            try:
                with open(self.usage_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {}
    
    def _save_stats(self):
        """保存使用统计"""
        try:
            with open(self.usage_file, "w", encoding="utf-8") as f:
                json.dump(self.usage_stats, f, indent=2)
        except IOError:
            pass
    
    def record_access(self, filepath: str):
        """记录文件访问"""
        import time
        
        if filepath not in self.usage_stats:
            self.usage_stats[filepath] = {
                "access_count": 0,
                "first_access": time.time(),
                "last_access": 0,
            }
        
        self.usage_stats[filepath]["access_count"] += 1
        self.usage_stats[filepath]["last_access"] = time.time()
        self._save_stats()
    
    def get_frequent_files(self, limit: int = 10) -> List[tuple]:
        """获取最常访问的文件"""
        sorted_files = sorted(
            self.usage_stats.items(),
            key=lambda x: x[1].get("access_count", 0),
            reverse=True,
        )
        return sorted_files[:limit]
    
    def get_recent_files(self, limit: int = 10) -> List[tuple]:
        """获取最近访问的文件"""
        sorted_files = sorted(
            self.usage_stats.items(),
            key=lambda x: x[1].get("last_access", 0),
            reverse=True,
        )
        return sorted_files[:limit]
    
    def get_recommendations(self, current_dir: str, limit: int = 5) -> List[str]:
        """获取文件推荐"""
        # 基于访问频率和当前目录推荐
        frequent = self.get_frequent_files(20)
        
        recommendations = []
        for filepath, stats in frequent:
            if filepath.startswith(current_dir) and os.path.exists(filepath):
                recommendations.append(filepath)
                if len(recommendations) >= limit:
                    break
        
        return recommendations
