# RedGarph 更新日志

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
