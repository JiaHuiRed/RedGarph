# RedGarph 更新日志

## 0.1.8（2026-09-04）

#### 视觉
- **品牌图标** — 使用抽象 RG 负形与裁剪框设计替换旧头像图标，生成透明背景、多尺寸应用图标。

#### 修复
- **构建依赖预检** — 构建前检查并安装 PyQt6/Pillow，避免构建成功但 exe 启动时报缺少 PyQt6。

---

## 0.1.7（2026-09-04）

#### 优化
- **后台目录扫描** — 大目录扫描与自然排序移出界面线程，切换目录时保持界面响应。
- **后台 EXIF 读取** — 图片元数据在工作线程读取，避免 EXIF 较多或文件较大时阻塞界面。
- **后台图片解码** — 首次打开和翻页解码移出界面线程，快速切换时只应用最后一次请求。
- **缓存与状态管理** — 图片缓存按文件签名和内存上限管理，保存、删除和外部修改后不会复用旧图。
- **界面层级** — 统一三套主题的图片区域、标题栏、浮动工具条和 EXIF 信息卡的间距、圆角及交互态。

#### 修复
- **编辑后刷新** — 旋转、裁剪并保存后重新载入最新内容，实际尺寸和信息栏显示原图尺寸。
- **导航安全** — 切换图片、目录或关闭窗口前保护未保存的旋转/裁剪修改，取消切换时恢复原索引。
- **安全保存** — 先写同目录临时文件再原子替换，常见格式尽量保留 EXIF 并归一化方向信息。
- **加载失败清理** — 无效图片、空目录和清空列表时同步清理旧图、工具栏和元数据。
- **快捷键与依赖** — 补齐 README 中声明的快捷键，启动脚本统一按 requirements.txt 检查依赖。

---

## 0.1.6（2026-08-02）

> 启动性能优化：onedir 打包 + 大图缩小解码 + 窗口置前激活

#### 优化
- **打包方式 onefile → onedir** — 消除每次启动解压 54.9MB 到临时目录的开销，启动到窗口出现从 20s+ 降至约 0.5s（`build_common.bat`）
- **大图缩小解码** — `QImageReader` 长边超过 3840 时缩小解码，大图秒开；保存/另存为/裁剪时全尺寸重解码，不丢分辨率（`viewer/image_panel.py`、`viewer/window.py`）
- **EXIF 延迟读取** — EXIF 面板读取延迟到事件循环空闲，不再阻塞首屏（`viewer/window.py`）

#### 修复
- **静默显示** — 无框窗口启动后主动 `raise_()` + `activateWindow()` + 100ms 延时补激活，窗口直接置前弹出（`main.py`）

---

## 0.1.5（2026-07-29）

> 修复启动崩溃 + 构建脚本统一 + 版本检查

#### 修复
- **启动崩溃** — `main.py` 修复 icon path `TypeError`：`_resource_path("resources" / "icon.ico")` 改为 `_resource_path(Path("resources") / "icon.ico")`（`main.py`）
- **导入缺失** — `viewer/window.py` 补充 `SLIDESHOW_INTERVAL` import，修复打开图片时 `NameError`（`viewer/window.py`）

#### 重构
- **构建脚本统一** — 抽取 `build_common.bat`，`build.bat` / `build_debug.bat` 改为 thin wrapper，避免双份维护（`build.bat`、`build_debug.bat`、`build_common.bat`）
- **原生文件对话框** — 移除 `QFileDialog.Option.DontUseNativeDialog`，恢复 Windows 原生打开/保存对话框（`viewer/window.py`）

#### 构建
- **版本一致性检查** — 构建前自动校验 `viewer/constants.py`、`CHANGELOG.md`、`README.md` 版本是否一致，不一致则中止（`scripts/check_version.py`、`build_common.bat`）
- **产物清理** — 无论构建成功失败，均清理 `build/` 和 `.spec` 文件，避免残留干扰下次构建（`build_common.bat`）

---

## 0.1.4（2026-07-29）

> 全屏顶部悬停标题栏 + 幻灯片间隔调节 UI

#### 新增

- **全屏顶部悬停标题栏** — 全屏模式下鼠标移到窗口顶部自动显示自定义标题栏，移开自动隐藏；`changeEvent` 统一管理进入/退出全屏时的标题栏状态，`_check_fullscreen_hover` 定时检测鼠标位置（`viewer/window.py`）
- **幻灯片间隔调节 UI** — 菜单新增“间隔调节...”动作，通过 `QInputDialog` 输入 1-60 秒；状态栏常驻显示当前幻灯片间隔，间隔变更时实时刷新（`viewer/window.py`）

#### 重构

- **规范空行密度** — 清理 `viewer/window.py` 中过度插入的重复空行，统一为单段间距，提升可读性（`viewer/window.py`）

---

## 0.1.3（2026-07-29）

> 全屏标题栏自动显隐 + 幻灯片间隔快捷键

#### 修复

- **全屏标题栏自动显隐** — 新增 `changeEvent` 统一管理，进入/退出全屏时自动显示/隐藏自定义标题栏；修正 Esc 键独立执行，避免 `elif` 导致幻灯片不停止（`viewer/window.py`）

#### 新增

- **幻灯片间隔快捷键** — `[` 减少 1 秒、`]` 增加 1 秒（范围 1-60 秒），`Slideshow` 新增 `intervalChanged` 信号，`InfoBar` 显示当前间隔（`viewer/slideshow.py`、`viewer/window.py`、`viewer/info_bar.py`）

---

## 0.1.2（2026-07-28）

### 🐛 修复

- **窗口无图标** — `main.py` 增加 `_resource_path()` 兼容源码/PyInstaller 资源路径，`QApplication.setWindowIcon()` 设置标题栏与任务栏图标（`main.py`）
- **`_edge_overlay` 重复创建** — `_build_ui` 移除第一次无用的 `_EdgeOverlay(central, self)` 实例，只保留悬浮层实例（`viewer/window.py`）

### ⚡ 优化

- **启动速度** — 移除 `_build_ui` 中 8 条带 `flush=True` 的 debug print，减少 Windows 控制台 I/O 阻塞（`viewer/window.py`）
- **图片翻页卡顿** — `ImagePanel` 增加 LRU pixmap 缓存（容量 20），翻页时命中缓存直接显示，跳过磁盘解码（`viewer/image_panel.py`）
- **首屏响应** — 命令行参数加载改用 `QTimer.singleShot(0)` 延迟，`_load_current` 增加 `processEvents()`，确保窗口先 paint 再解码大图（`main.py`、`viewer/window.py`）

### ✨ 新功能

- **全屏标题栏自动显隐** — 新增 `changeEvent` 统一管理，进入/退出全屏时自动显示/隐藏自定义标题栏；修正 Esc 键独立执行，避免 `elif` 导致幻灯片不停止（`viewer/window.py`）
- **幻灯片间隔快捷键** — `[` 减少 1 秒、`]` 增加 1 秒（范围 1-60 秒），`Slideshow` 新增 `intervalChanged` 信号，`InfoBar` 显示当前间隔（`viewer/slideshow.py`、`viewer/window.py`、`viewer/info_bar.py`）

### 🛠 构建

- **PyInstaller 资源打包** — `build.bat` / `build_debug.bat` 增加 `--add-data "resources\icon.ico;resources"`，frozen 模式下运行时能正确读取资源文件

---

## 0.1.1（2026-07-05）

### ✨ 新功能

- **裁剪模式重构** — 替换 `QRubberBand` 为自定义 `_CropOverlay`：暗化选区外部、三分线参考线、8 向拖拽手柄、选区移动；光标随位置变化（`image_panel.py`）
- **底部裁剪工具栏** — 右下角新增 `[裁剪]` 和 `[保存]` 按钮，裁剪模式一键启停，裁完直接保存，无需进菜单操作（`image_panel.py`、`window.py`）

### 💎 代码质量

- **移除 `QRubberBand` 依赖** — 裁剪模式完全由 `_CropOverlay（QWidget）` 接管，删除原裁剪鼠标事件分支（`image_panel.py`）
- **信号接口** — `toggleCropRequested` / `saveRequested` 信号连接 window 裁剪/保存流程（`image_panel.py`、`window.py`）

---

## 0.1.0（2026-06-25）

### ✨ 新功能

- **无框 macOS 风格窗口** — `FramelessWindowHint` + 自定义交通灯标题栏（关闭/最小化/全屏），三主题均适配（`window.py`）
- **边缘拖拽缩放** — `_EdgeOverlay` 遮罩层实现四边/顶点拖拽调整窗口大小，替代原生 `nativeEvent` 方案（`window.py`）

### 🐛 Bug 修复

- **PyInstaller windowed 模式闪退** — `nativeEvent` override + `FramelessWindowHint` 在 `--windowed` 下死锁，删除该方法；同时设置 `QT_QPA_PLATFORM_PLUGIN_PATH` 修复 Qt 插件路径、显式 `import ctypes.wintypes` 避免漏打包（`window.py`、`main.py`）

### 💎 代码质量

- **快捷键统一入口** — `_build_titlebar` 移除 11 处 `QAction.setShortcut`，所有快捷键统一由 `keyPressEvent` 处理
- **EXIF 单次读取** — `exif_panel.py` `set_image` 避免重复 `Image.open`

---

## 0.0.9（2026-06-25）

### 🐛 Bug 修复

- **无框窗口边缘缩放失效** — 删除 `nativeEvent`（PyInstaller `--windowed` 下与 `FramelessWindowHint` 死锁），改用 `_EdgeOverlay` 遮罩层实现四边/顶点缩放：透明 widget + `QRegion` 挖空中间区域，只保留边缘 8px 环响应鼠标拖拽，完全不碰原生事件循环（`window.py`）

---

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
