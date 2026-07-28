# 项目记忆

## 当前进度
- 最后工作日期：260728
- 上次做到：V0.1.2 — 启动性能优化 + 窗口图标修复 + 图片缓存
- 待办：1. 锁定 requirements.txt 版本（PyQt6/Pillow）2. 核心逻辑集成测试

## 架构决策
- 快捷键统一由 `keyPressEvent` 处理，`QAction.setShortcut` 全部移除，避免重复注册
- 删除逻辑：先 `_recycle_file()` 成功后再 `remove_current()`，保证数据一致性
- EXIF 读取：单次 `Image.open` 同时获取尺寸和 EXIF，不重复打开
- 图片加载：`ImagePanel.load_image()` 内置 LRU 缓存（20 条），翻页命中缓存跳过磁盘解码
- 首屏加载：命令行参数和文件夹打开均延迟到 `show()` 之后，避免阻塞窗口 paint

## 踩坑记录
- **PowerShell 编码问题**：`git push` 的 verbose 输出在 PowerShell 下会显示 `NativeCommandError`，实际 push 可能已成功，需用 `git status` 确认
- **git proxy 配置**：`git -c http.proxy=... push` 语法正确，PowerShell 会把 stderr 输出误报为错误
- **edit 工具 hash 机制**：文件被多次修改后 hash 会变化，需 re-read 重新获取 hash；大段 Python 代码建议用 `python -c "..."` 脚本直接读写
- **CRLF 换行污染**：Windows 上 `core.autocrlf=true` 会把全仓文件转成 CRLF，导致所有文件显示为 modified；解决：设 `core.autocrlf=false`，Python 源文件统一 LF，`.bat` 文件单独转回 CRLF

## 关键路径
- 主窗口：`viewer/window.py`
- 图片渲染：`viewer/image_panel.py`
- 文件列表：`viewer/file_list.py`
- EXIF 面板：`viewer/exif_panel.py`
- 主题系统：`viewer/theme.py`
- 版本号：`viewer/constants.py:APP_VERSION`（唯一真实来源）；升版时必须同步检查 `build.bat`、`build_debug.bat`、`main.py` 注释里的硬编码版本字符串
