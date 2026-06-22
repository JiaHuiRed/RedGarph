# RedGarph 更新日志

## 0.0.8（2026-06-25）

### 💎 代码质量

- **快捷键统一入口** — `_build_titlebar` 移除 11 处 `QAction.setShortcut`，所有快捷键统一由 `keyPressEvent` 处理，消除菜单与键盘事件重复注册
- **EXIF 单次读取** — `exif_panel.py` `set_image` 中 `Image.open` 获取尺寸后直接读取 `getexif()`，避免重复打开文件

---

## 0.0.7（2026-06-25）

### 🐛 Bug 修复

- **删除功能语法错误** — `window.py` 确认对话框 f-string 内嵌引号未转义，导致模块无法导入（`f'将 "{name}" 移至回收站？'`）
- **删除逻辑回滚风险** — `_delete_current` 先调用 `remove_current()` 再从列表移除，修复为「回收站成功后再移除列表项」，避免文件仍在磁盘但列表已消失
- **PyInstaller windowed exe 启动闪退** — `nativeEvent` override + `FramelessWindowHint` 在 `--windowed` 模式下导致 `win.show()` 死锁，删除 `nativeEvent` 方法（边缘缩放回退到 mouseEvent 方案）；同时设置 `QT_QPA_PLATFORM_PLUGIN_PATH` 修复 Qt 平台插件路径检测、显式 `import ctypes.wintypes` 避免 PyInstaller 漏打包（`window.py`、`main.py`）

### 💎 代码质量

- **清理主题死样式** — `theme.py` 移除三套主题中 `thumbBar` 相关 QSS（缩略图面板 0.0.4 已删除，样式残留）
- **`.gitignore` 补充** — 显式忽略 `crash.log`，避免崩溃日志被 git 跟踪
- **快捷键统一入口** — `_build_titlebar` 移除 11 处 `setShortcut`，所有快捷键统一由 `keyPressEvent` 处理，消除菜单与键盘事件重复注册
- **EXIF 单次读取** — `exif_panel.py` `set_image` 中 `Image.open` 获取尺寸后直接读取 `getexif()`，避免重复打开文件
- **提前创建 native window** — `__init__` 末尾调用 `self.winId()` 让 `FramelessWindowHint` 在 `show()` 前生效，消除初始窗口框闪烁（`window.py`）

---

## 0.0.6（2026-06-22）

### ✨ 新功能

- **保存（Ctrl+S）** — 覆盖保存当前图片（含旋转/裁剪状态），支持 JPEG / PNG / BMP / WebP / TIFF
- **另存为（Ctrl+Shift+S）** — 文件对话框选择新路径保存
- **复制到剪贴板（Ctrl+C）** — 复制当前图片（含旋转状态）到系统剪贴板
- **删除到回收站（Del）** — 确认后将文件移至 Windows 回收站，自动跳到下一张
- **在资源管理器中显示（Ctrl+Shift+E）** — 调用 `explorer /select` 在资源管理器中选中当前文件

### 💎 代码质量

- **移除孤立常量** — 删除 `THUMB_PANEL_WIDTH` / `THUMB_SIZE` / `THUMB_LIST_SIZE`（缩略图面板 0.0.4 已移除的遗留垃圾）
- **`file_list.py` 新增 `remove_current()`** — 从文件列表移除当前项并自动调整索引，复用于删除流程

---

## 0.0.5（2026-06-22）

### ✨ 新功能

- **标题栏版本号** — 交通灯按钮旁显示小版本标签（`v0.0.5`），三主题均适配

### 🐛 Bug 修复

- **多显示器负坐标** — `nativeEvent` LPARAM 坐标改用有符号 `ctypes.c_short` 解析，修复多屏幕左侧/上侧窗口边缘缩放失效问题（`window.py`）

### 💎 代码质量

- **PIL Image 文件句柄泄漏** — `exif_panel.py` 改用 `with Image.open(...)` 保证每次关闭；同时从私有 API `_getexif()` 迁移到公开 API `getexif()`
- **消除 `_format_size` 重复定义** — 提取到 `constants.py`，`info_bar.py` / `exif_panel.py` 统一引用
- **消除硬编码扩展名** — `load_path` 中内联的扩展名集合改用 `IMAGE_EXTENSIONS` 常量（`window.py`）
- **修正导入位置** — `from collections.abc import Callable` 移至 `exif_panel.py` 文件顶部
- **移除冗余中间方法** — `_on_files_changed` 单行转发改为信号直连 `_update_ui`（`window.py`）
- **坐标计算简化** — `_position_info_bar` 中 `x if x >= 0 else 0` 改为 `max(0, x)`
- **版本号统一** — `constants.py` `APP_VERSION` 与实际发布版本保持一致

---

## 0.0.4（2026-06-20）

### ✨ 新功能

- **信息面板升级** — 默认显示文件名/大小/修改时间/图片尺寸（所有图片都有），EXIF 相机数据折叠到"─── EXIF ───"段作为附加信息（`exif_panel.py`）
- **裁剪模式提示** — 进入裁剪模式后顶部显示「点击拖拽选区 · Enter 确认 · Esc 取消」操作提示，蓝色醒目选框（`image_panel.py`）

### 🐛 Bug 修复

- **无框窗口无法拖拽缩放** — 改用 `nativeEvent` + `WM_NCHITTEST` 处理边缘缩放，替代失效的 `mousePressEvent` 方案（`window.py`）
- **缩减的缩略图面板** — 整体移除侧边栏缩略图功能（`thumb_bar.py` 删除，所有引用清理）

### ⚡ 优化

- **构建脚本** — `build.bat` 成功路径末尾加 `pause`，避免编译完成窗口闪退

### 💎 代码质量

- 旋转逻辑提取 `_get_rotated_display()` 消除 `_do_crop` 中的重复
- `_source` 添加 `source` property，外部不再直接访问私有属性
- 移除 `zoomChanged` 死变量、`_make_palette` 未用参数、`setSpacing` 重复调用

---

## 0.0.3（2026-06-20）

### 🐛 Bug 修复

- `QRubberBand.Shape.Rectangle` — 修复 PyQt6 枚举命名空间兼容性（裁剪模式初始化崩溃）
- `contentsMargins()` — 修复 `QLabel` 无 `getContentsMargins` 方法（缩放指示器崩溃）

### 技术细节

- `main.py` 增加崩溃日志（`crash.log`）+ Qt 消息处理器
- 新增 `build_debug.bat`（带控制台的调试版 exe）

## 0.0.2（2026-06-20）

### ✨ 新功能

- **缩放比例指示器** — 右下角实时显示缩放百分比（适应窗口/150%/…）
- **EXIF 信息面板** — 右侧面板（Ctrl+E），显示相机型号、光圈、快门、ISO、焦距等元数据
- **图片裁剪** — Ctrl+Shift+C 进入裁剪模式，拖动选择区域，Enter 确认，Esc 取消

### 🐛 Bug 修复

- `run.bat` 启动脚本优化 — 优先运行编译版 exe，不存在则走源码

### 技术细节

- 新增 `viewer/exif_panel.py`，基于 Pillow 读取 EXIF
- `ImagePanel` 增加缩放指示器 QLabel 叠加层 + 裁剪模式（QRubberBand）
- `build.bat` 一键打包脚本，`--icon resources\icon.ico`
- macOS Big Sur 风格应用图标（暖红橙渐变 + 山景剪影）

## 0.0.1（2026-06-20）

### ✨ 新功能

- **左侧缩略图面板** — 竖向缩略图列表，支持展开/收起（Ctrl+B）
- **图片浏览** — 支持 PNG/JPG/WebP/BMP/GIF/TIFF/SVG/ICO 格式，←→ 切换
- **缩放与拖拽** — 滚轮缩放（以鼠标为中心）、拖拽平移、双击切换适应/原尺寸
- **旋转** — R 顺时针、Shift+R 逆时针 90° 旋转
- **全屏模式** — F/F11 全屏查看，Esc 退出
- **幻灯片播放** — Space 启动/停止，自动切换
- **信息浮层** — I 键切换，显示文件名、分辨率、文件大小、页码
- **三主题** — 夜间/日间/深蓝，菜单一键切换
- **macOS 风格** — 无框窗口 + 交通灯标题栏 + 边缘拖拽缩放
- **拖拽打开** — 拖拽图片/文件夹到窗口打开
- **命令行支持** — `python main.py path\to\image.jpg`

### 技术细节

- PyQt6 + QGraphicsView 架构
- FramelessWindowHint + 自定义标题栏
- 四方向边缘拖拽缩放
- QSplitter 水平分割布局
