# 🖼 RedGarph

> **macOS 风格本地图片查看器。** 缩放/旋转/裁剪/EXIF 信息面板。
> _A macOS-style local image viewer with zoom, rotate, crop, and EXIF info panel._

[![版本](https://badgen.net/badge/版本/0.1.0/blue)](CHANGELOG.md)
[![平台](https://badgen.net/badge/平台/Windows/lightgrey)]()
[![Tech](https://badgen.net/badge/Tech/PyQt6/orange)]()

---

## ✨ 功能

- **缩放拖拽** — 滚轮缩放（以鼠标为中心）、拖拽平移、双击切换适应/原尺寸
- **旋转** — R 顺时针、Shift+R 逆时针，每次 90°
- **裁剪** — Ctrl+Shift+C 进入裁剪模式，拖拽选区，Enter 确认，Esc 取消
- **保存** — Ctrl+S 覆盖保存（含旋转/裁剪）；Ctrl+Shift+S 另存为
- **复制** — Ctrl+C 复制当前图片到剪贴板
- **删除** — Del 将当前图片移至回收站，自动跳到下一张
- **EXIF 信息面板** — Ctrl+E 切换右侧面板，显示文件信息与相机元数据
- **全屏** — F/F11 全屏查看
- **幻灯片** — 空格键自动播放
- **信息浮层** — I 键显示/隐藏图片信息（文件名、分辨率、大小、页码）
- **三主题** — 夜间/日间/深蓝，菜单切换
- **拖拽打开** — 拖拽图片或文件夹到窗口
- **macOS 风格** — 无框窗口 + 交通灯标题栏（含版本号）+ 边缘拖拽缩放

---

## 🚀 快速开始

```bash
cd RedGarph
pip install PyQt6
python main.py
# 或
python main.py "C:\图片\photo.jpg"
```

---

## ⌨️ 快捷键

| 按键 | 功能 |
|------|------|
| `←` / `→` | 上一张 / 下一张 |
| `R` / `Shift+R` | 顺时针 / 逆时针旋转 |
| `Ctrl+0` | 适应窗口 |
| `Ctrl+1` | 原始尺寸 |
| `+` / `-` | 放大 / 缩小 |
| `F` / `F11` | 切换全屏 |
| `Space` | 幻灯片播放 / 暂停 |
| `Esc` | 退出全屏 / 停止幻灯片 / 取消裁剪 |
| `I` | 切换信息栏 |
| `Ctrl+E` | 切换 EXIF 信息面板 |
| `Ctrl+Shift+C` | 进入裁剪模式 |
| `Enter` | 确认裁剪 |
| `Ctrl+S` | 保存（覆盖） |
| `Ctrl+Shift+S` | 另存为 |
| `Ctrl+C` | 复制图片到剪贴板 |
| `Del` | 删除到回收站 |
| `Ctrl+Shift+E` | 在资源管理器中显示 |
| `Ctrl+O` | 打开文件夹 |
| `Ctrl+Q` | 退出 |

---

## 📋 更新日志

见 [CHANGELOG.md](CHANGELOG.md)。

---

## 💙 致谢

- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) — Qt6 Python 绑定
