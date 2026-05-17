<div align="center">

# 🚀 SmartFile-TUI

**AI驱动的智能终端文件管理器**  
*AI-Powered Intelligent Terminal File Manager*

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey.svg)]()

[English](#english) | [简体中文](#简体中文) | [繁體中文](#繁體中文)

</div>

---

<a name="简体中文"></a>
## 🎉 项目介绍

SmartFile-TUI 是一款**现代化、AI驱动的终端文件管理器**，融合了传统文件管理器的效率与现代AI技术的智能特性。

### 💡 灵感来源

本项目受到以下优秀开源项目的启发：
- **[yazi](https://github.com/sxyazi/yazi)** - 极速异步文件管理器（Rust）
- **[superfile](https://github.com/yorukot/superfile)** - 美观的TUI设计（Go）
- **[veld-fm](https://github.com/BranBushes/veld-fm)** - Python可扩展性

### ✨ 核心差异化亮点

| 特性 | 传统文件管理器 | SmartFile-TUI |
|------|---------------|---------------|
| 文件分类 | 仅按扩展名 | 🤖 **AI智能分类+自动标签** |
| 搜索方式 | 文件名匹配 | 🔍 **语义搜索（理解内容）** |
| 文件操作 | 同步阻塞 | ⚡ **异步非阻塞** |
| 界面风格 | 传统终端 | 🎨 **现代化TUI** |
| 扩展性 | 有限 | 🔌 **插件系统** |

---

## ✨ 核心特性

### 🗂️ 现代化TUI界面
- 基于 **Textual** 框架构建
- 响应式设计，支持窗口大小自适应
- 多主题支持（Dark/Light/Dracula/Nord/Monokai）
- 流畅的键盘导航体验

### 🤖 AI智能功能
- **智能文件分类**：自动识别文件类型并分类
- **自动标签生成**：基于文件名和内容特征
- **语义搜索**：不仅匹配文件名，更理解搜索意图
- **使用频率分析**：智能推荐常用文件

### ⚡ 高性能异步操作
- 基于 **asyncio** 的异步文件操作
- 复制/移动/删除不阻塞界面
- 大文件操作流畅无卡顿

### 🎨 丰富的文件预览
- 文本文件语法高亮
- 目录内容预览
- 图片/媒体文件信息展示
- 可配置预览行数

### 🔧 强大的文件操作
- 多选批量操作
- 剪贴板复制/剪切/粘贴
- 快速创建文件/目录
- 书签与快速跳转
- 最近访问记录

### 🔌 可扩展架构
- 插件系统（开发中）
- 自定义键位绑定
- 主题自定义
- 配置文件支持

---

## 🚀 快速开始

### 环境要求

- **Python** 3.9 或更高版本
- **操作系统**: Linux / macOS / Windows

### 安装方式

#### 方式一：通过 pip 安装（推荐）

```bash
pip install smartfile-tui
```

#### 方式二：从源码安装

```bash
git clone https://github.com/gitstq/smartfile-tui.git
cd smartfile-tui
pip install -e .
```

### 启动命令

```bash
# 基本启动
smartfile

# 或简写
sft

# 指定起始目录
smartfile -p /path/to/directory

# 指定主题
smartfile -t dracula

# 显示帮助
smartfile --help
```

---

## 📖 详细使用指南

### ⌨️ 快捷键一览

#### 导航操作
| 快捷键 | 功能 |
|--------|------|
| `↑` / `↓` 或 `j` / `k` | 上下移动 |
| `←` / `→` 或 `h` / `l` | 返回/进入目录 |
| `Enter` | 打开文件/进入目录 |
| `Backspace` | 返回上级目录 |

#### 文件操作
| 快捷键 | 功能 |
|--------|------|
| `Space` | 选择/取消选择 |
| `c` | 复制到剪贴板 |
| `x` | 剪切到剪贴板 |
| `v` | 粘贴 |
| `d` | 删除 |
| `R` | 重命名 |
| `n` | 新建文件 |
| `N` | 新建目录 |

#### 视图与搜索
| 快捷键 | 功能 |
|--------|------|
| `/` | 搜索文件 |
| `.` | 切换隐藏文件显示 |
| `p` | 切换预览面板 |
| `b` | 书签 |
| `r` | 刷新 |
| `?` | 显示帮助 |
| `q` | 退出 |

### 🔍 搜索功能

SmartFile-TUI 支持强大的文件搜索：

1. **快速搜索**：按 `/` 输入文件名模式
2. **通配符支持**：使用 `*` 和 `?` 进行模式匹配
3. **递归搜索**：自动在所有子目录中搜索
4. **语义搜索**：AI理解搜索意图，不仅匹配文件名

### 🎨 主题切换

```bash
# 使用暗色主题（默认）
smartfile -t dark

# 使用亮色主题
smartfile -t light

# 使用 Dracula 主题
smartfile -t dracula

# 使用 Nord 主题
smartfile -t nord

# 使用 Monokai 主题
smartfile -t monokai
```

### 🔖 书签管理

- 按 `b` 打开书签面板
- 支持快速跳转到常用目录
- 自动保存最近访问记录

---

## 💡 设计思路与迭代规划

### 技术选型原因

| 技术 | 选择原因 |
|------|---------|
| **Python** | 生态丰富，易于扩展，开发效率高 |
| **Textual** | 现代化的Python TUI框架，组件丰富 |
| **asyncio** | 原生异步支持，高性能IO操作 |
| **Rich** | 美观的终端渲染，支持语法高亮 |
| **Pydantic** | 类型安全，配置验证 |

### 后续功能迭代计划

#### v1.1.0（近期）
- [ ] 文件内容全文搜索
- [ ] 压缩文件直接浏览（zip/tar）
- [ ] 更多主题支持
- [ ] 文件对比功能

#### v1.2.0（中期）
- [ ] 插件系统正式发布
- [ ] 远程文件管理（SFTP/FTP）
- [ ] 文件同步功能
- [ ] 批量重命名工具

#### v2.0.0（远期）
- [ ] 完整的AI助手集成
- [ ] 自然语言命令
- [ ] 智能工作流自动化
- [ ] 团队协作功能

### 社区贡献方向

我们欢迎以下方向的贡献：
- 🐛 Bug 修复
- ✨ 新功能开发
- 🌍 多语言翻译
- 🎨 主题设计
- 📚 文档完善
- 🔌 插件开发

---

## 📦 打包与部署指南

### 开发环境搭建

```bash
# 克隆仓库
git clone https://github.com/gitstq/smartfile-tui.git
cd smartfile-tui

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或: venv\Scripts\activate  # Windows

# 安装开发依赖
pip install -e ".[dev]"
```

### 运行测试

```bash
# 运行单元测试
pytest

# 运行代码检查
black --check smartfile_tui
ruff check smartfile_tui
mypy smartfile_tui
```

### 构建可执行文件

```bash
# 使用构建脚本
python build.py all

# 或手动构建
pip install pyinstaller
pyinstaller --onefile --name smartfile smartfile_tui/main.py
```

### 发布到 PyPI

```bash
# 构建包
python -m build

# 上传到 PyPI
python -m twine upload dist/*
```

---

## 🤝 贡献指南

### 提交 Issue

- 使用清晰的标题描述问题
- 提供复现步骤
- 说明环境信息（OS、Python版本）
- 附上错误日志（如有）

### 提交 Pull Request

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### 代码规范

- 遵循 PEP 8 规范
- 使用 Black 格式化代码
- 添加类型注解
- 编写单元测试

---

## 📄 开源协议

本项目采用 [MIT License](LICENSE) 开源协议。

---

<a name="english"></a>
## 🎉 Introduction (English)

SmartFile-TUI is a **modern, AI-powered terminal file manager** that combines the efficiency of traditional file managers with intelligent features of modern AI technology.

### ✨ Key Features

- 🤖 **AI Smart Classification**: Automatic file categorization and tagging
- 🔍 **Semantic Search**: Understands search intent, not just filename matching
- ⚡ **Async Operations**: Non-blocking file copy/move/delete
- 🎨 **Modern TUI**: Built with Textual framework
- 🖼️ **Rich Preview**: Syntax highlighting, directory preview
- 🔌 **Extensible**: Plugin system support

### 🚀 Quick Start

```bash
# Install
pip install smartfile-tui

# Run
smartfile
# or
sft
```

See full documentation above or visit [GitHub Repository](https://github.com/gitstq/smartfile-tui).

---

<a name="繁體中文"></a>
## 🎉 項目介紹 (繁體中文)

SmartFile-TUI 是一款**現代化、AI驅動的終端檔案管理器**，融合了傳統檔案管理器的效率與現代AI技術的智能特性。

### ✨ 核心特性

- 🤖 **AI智能分類**：自動識別檔案類型並分類
- 🔍 **語義搜尋**：不僅匹配檔名，更理解搜尋意圖
- ⚡ **非同步操作**：複製/移動/刪除不阻塞介面
- 🎨 **現代化TUI**：基於 Textual 框架
- 🖼️ **豐富預覽**：語法高亮、目錄預覽
- 🔌 **可擴展**：支援插件系統

### 🚀 快速開始

```bash
# 安裝
pip install smartfile-tui

# 執行
smartfile
# 或
sft
```

完整文件請參考上方的簡體中文版本或訪問 [GitHub 倉庫](https://github.com/gitstq/smartfile-tui)。

---

<div align="center">

**Made with ❤️ by SmartFile Team**

[⭐ Star us on GitHub](https://github.com/gitstq/smartfile-tui) | [🐛 Report Bug](https://github.com/gitstq/smartfile-tui/issues) | [💡 Request Feature](https://github.com/gitstq/smartfile-tui/issues)

</div>
