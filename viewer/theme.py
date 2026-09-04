#author Red
#260620 Red&小宋 RedGarph V0.0.1 — 三主题系统

from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import QApplication

# ── 主题名称与索引 ──
THEMES = ["night", "day", "deepblue"]
THEME_LABELS = {"night": "夜间", "day": "日间", "deepblue": "深蓝"}


def apply_theme(name: str):
    """切换主题"""
    app = QApplication.instance()
    if not app or not isinstance(app, QApplication):
        return
    qss = _QSS_TABLE.get(name)
    if qss:
        app.setStyleSheet(qss)

    palette = _PALETTE_TABLE.get(name)
    if palette:
        app.setPalette(palette)
    else:
        style = app.style()
        if style:
            app.setPalette(style.standardPalette())


# ── QSS 样式表 ──

_NIGHT_QSS = """
QMainWindow, QWidget { background-color: #181a1d; color: #e6eaf0; }
#ImageArea, #imagePanel { background-color: #111316; }
#imageViewport { background-color: #111316; }

/* ── 标题栏 ── */
#titleBar { background-color: #202226; border-bottom: 1px solid #353940; }
#titleLabel { color: #eef2f7; font-size: 13px; font-weight: 500; }
#verLabel { color: #8d96a3; font-size: 11px; }
#MenuButton {
    color: #b9c1cc; background: transparent; border: 1px solid transparent;
    border-radius: 7px; font-size: 17px; padding: 0;
}
#MenuButton:hover { color: #ffffff; background: rgba(255,255,255,0.10); border-color: rgba(255,255,255,0.12); }
#MenuButton:pressed { background: rgba(255,255,255,0.16); }

/* ── 信息栏 ── */
#infoBar {
    background-color: rgba(30, 33, 38, 228); color: #e8edf4;
    border: 1px solid rgba(255,255,255,0.12); border-radius: 9px;
    padding: 7px 14px; font-size: 13px;
}
#infoBar QLabel { color: #e8edf4; }

/* ── 缩放指示器 ── */
#zoomLabel {
    background-color: rgba(30, 33, 38, 235); color: #e8edf4;
    border: 1px solid rgba(255,255,255,0.12); border-radius: 8px;
    font-size: 12px; font-weight: 500;
}
#bottomToolbar {
    background-color: rgba(30, 33, 38, 235);
    border: 1px solid rgba(255,255,255,0.12); border-radius: 10px;
}

/* ── EXIF 面板 ── */
#exifPanel { background-color: #1c1f23; border-left: 1px solid #363a42; }
#exifTitle { background-color: transparent; color: #f0f3f7; font-size: 14px; font-weight: 600; }
#exifTree {
    background-color: #24272c; alternate-background-color: #2b2e34;
    color: #e8edf4; border: 1px solid #383d46; border-radius: 9px;
}
#exifTree::item { background-color: #24272c; color: #e8edf4; padding: 6px 8px; border: none; }
#exifTree::item:alternate { background-color: #2b2e34; color: #e8edf4; }
#exifTree::item:hover { background-color: #323740; }
#exifTree::item:selected { background-color: rgba(74, 158, 255, 0.22); color: #ffffff; }
#exifTree QHeaderView::section { background-color: #2b2e34; color: #aeb7c4; border: none; border-bottom: 1px solid #3b4049; padding: 7px 8px; font-size: 12px; font-weight: 600; }

#MainSplitter::handle { background-color: #363a42; }

/* ── 滚动条 ── */
QScrollBar:horizontal { background: #2d2d2d; height: 8px; border: none; }
QScrollBar::handle:horizontal { background: #555; border-radius: 4px; min-width: 30px; }
QScrollBar::handle:horizontal:hover { background: #777; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
QScrollBar:vertical { background: #2d2d2d; width: 8px; border: none; }
QScrollBar::handle:vertical { background: #555; border-radius: 4px; min-height: 30px; }
QScrollBar::handle:vertical:hover { background: #777; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

/* ── 菜单 ── */
QMenuBar { background-color: #2d2d2d; color: #ccc; border-bottom: 1px solid #3c3c3c; }
QMenuBar::item:selected { background-color: #3d3d3d; }
QMenu { background-color: #2d2d2d; color: #ccc; border: 1px solid #3c3c3c; }
QMenu::item:selected { background-color: #094771; }

/* ── 对话框 ── */
QMessageBox { background-color: #1e1e1e; color: #e0e0e0; }
QMessageBox QPushButton {
    background-color: #3c3c3c; color: #e0e0e0; border: 1px solid #555;
    border-radius: 4px; padding: 6px 20px; min-width: 60px;
}
QMessageBox QPushButton:hover { background-color: #4a9eff; border-color: #4a9eff; }
"""

_DAY_QSS = """
QMainWindow, QWidget { background-color: #f5f5f5; color: #333; }
#ImageArea, #imagePanel { background-color: #edf0f4; }
#imageViewport { background-color: #edf0f4; }

#titleBar { background-color: #e8e8e8; border-bottom: 1px solid #d0d0d0; }
#titleLabel { color: #555; font-size: 13px; }
#verLabel { color: #aaaaaa; font-size: 11px; }
#MenuButton { color: #6d737b; background: transparent; border: 1px solid transparent; border-radius: 7px; font-size: 17px; padding: 0; }
#MenuButton:hover { color: #333; background: rgba(0,0,0,0.07); border-color: rgba(0,0,0,0.10); }
#MenuButton:pressed { background: rgba(0,0,0,0.12); }

#infoBar {
    background-color: rgba(245, 245, 245, 200); color: #333;
    border: 1px solid rgba(0,0,0,0.12); border-radius: 9px; padding: 7px 14px; font-size: 13px;
}
#infoBar QLabel { color: #333; }

#zoomLabel {
    background-color: rgba(220, 220, 220, 200); color: #555;
    border: 1px solid rgba(0,0,0,0.12); border-radius: 8px; font-size: 12px;
}

#exifPanel { background-color: #f0f1f3; border-left: 1px solid #d2d5da; }
#exifTitle { background-color: #e8e8e8; color: #555; font-size: 13px; font-weight: bold; border-bottom: 1px solid #d0d0d0; }
#exifTree { background-color: #ffffff; alternate-background-color: #f4f5f7; color: #333; border: 1px solid #d5d8dd; border-radius: 9px; }
#exifTree::item { background-color: #ffffff; color: #333; padding: 6px 8px; border: none; }
#exifTree::item:alternate { background-color: #f4f5f7; color: #333; }
#exifTree::item:hover { background-color: #e9f2ff; }
#exifTree::item:selected { background-color: rgba(0, 120, 212, 0.1); color: #0078d4; }
#exifTree QHeaderView::section { background-color: #e8e8e8; color: #777; border-bottom: 1px solid #d0d0d0; padding: 4px 6px; font-size: 12px; }
#MainSplitter::handle { background-color: #d2d5da; }

QScrollBar:horizontal { background: #e0e0e0; height: 8px; border: none; }
QScrollBar::handle:horizontal { background: #aaa; border-radius: 4px; min-width: 30px; }
QScrollBar::handle:horizontal:hover { background: #888; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
QScrollBar:vertical { background: #e0e0e0; width: 8px; border: none; }
QScrollBar::handle:vertical { background: #aaa; border-radius: 4px; min-height: 30px; }
QScrollBar::handle:vertical:hover { background: #888; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

QMenuBar { background-color: #e8e8e8; color: #555; border-bottom: 1px solid #d0d0d0; }
QMenuBar::item:selected { background-color: #d0d0d0; }
QMenu { background-color: #f0f0f0; color: #333; border: 1px solid #d0d0d0; }
QMenu::item:selected { background-color: #0078d4; color: #fff; }

QMessageBox { background-color: #f5f5f5; color: #333; }
QMessageBox QPushButton {
    background-color: #e0e0e0; color: #333; border: 1px solid #ccc;
    border-radius: 4px; padding: 6px 20px; min-width: 60px;
}
QMessageBox QPushButton:hover { background-color: #0078d4; color: #fff; border-color: #0078d4; }
"""

_DEEPBLUE_QSS = """
QMainWindow, QWidget { background-color: #0d1b2a; color: #c8d6e5; }
#ImageArea, #imagePanel { background-color: #091521; }
#imageViewport { background-color: #091521; }

#titleBar { background-color: #112240; border-bottom: 1px solid #1a3a5c; }
#titleLabel { color: #8892b0; font-size: 13px; }
#verLabel { color: #3a5078; font-size: 11px; }
#MenuButton { color: #a8b7cf; background: transparent; border: 1px solid transparent; border-radius: 7px; font-size: 17px; padding: 0; }
#MenuButton:hover { color: #e6f1ff; background: rgba(93,173,226,0.12); border-color: rgba(93,173,226,0.24); }
#MenuButton:pressed { background: rgba(93,173,226,0.18); }

#infoBar {
    background-color: rgba(13, 27, 42, 200); color: #c8d6e5;
    border: 1px solid rgba(93,173,226,0.22); border-radius: 9px; padding: 7px 14px; font-size: 13px;
}
#infoBar QLabel { color: #c8d6e5; }

#zoomLabel {
    background-color: rgba(17, 34, 64, 200); color: #8892b0;
    border: 1px solid rgba(93,173,226,0.22); border-radius: 8px; font-size: 12px;
}

#exifPanel { background-color: #0a1628; border-left: 1px solid #1a3a5c; }
#exifTitle { background-color: #112240; color: #8892b0; font-size: 13px; font-weight: bold; border-bottom: 1px solid #1a3a5c; }
#exifTree { background-color: #0e1e33; alternate-background-color: #112743; color: #c8d6e5; border: 1px solid #1a3a5c; border-radius: 9px; }
#exifTree::item { background-color: #0e1e33; color: #c8d6e5; padding: 6px 8px; border: none; }
#exifTree::item:alternate { background-color: #112743; color: #c8d6e5; }
#exifTree::item:hover { background-color: #173657; }
#exifTree::item:selected { background-color: rgba(93, 173, 226, 0.12); color: #5dade2; }
#exifTree QHeaderView::section { background-color: #112240; color: #8892b0; border-bottom: 1px solid #1a3a5c; padding: 4px 6px; font-size: 12px; }
#MainSplitter::handle { background-color: #1a3a5c; }

QScrollBar:horizontal { background: #112240; height: 8px; border: none; }
QScrollBar::handle:horizontal { background: #2c5282; border-radius: 4px; min-width: 30px; }
QScrollBar::handle:horizontal:hover { background: #3a7bd5; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
QScrollBar:vertical { background: #112240; width: 8px; border: none; }
QScrollBar::handle:vertical { background: #2c5282; border-radius: 4px; min-height: 30px; }
QScrollBar::handle:vertical:hover { background: #3a7bd5; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

QMenuBar { background-color: #112240; color: #8892b0; border-bottom: 1px solid #1a3a5c; }
QMenuBar::item:selected { background-color: #1a3a5c; }
QMenu { background-color: #112240; color: #c8d6e5; border: 1px solid #1a3a5c; }
QMenu::item:selected { background-color: #1a5276; }

QMessageBox { background-color: #0d1b2a; color: #c8d6e5; }
QMessageBox QPushButton {
    background-color: #1a3a5c; color: #c8d6e5; border: 1px solid #2c5282;
    border-radius: 4px; padding: 6px 20px; min-width: 60px;
}
QMessageBox QPushButton:hover { background-color: #5dade2; border-color: #5dade2; color: #0d1b2a; }
"""


def _make_palette(dark: bool):
    """创建 QPalette 辅助"""
    p = QPalette()
    if dark:
        p.setColor(QPalette.ColorRole.Window, QColor("#1e1e1e"))
        p.setColor(QPalette.ColorRole.WindowText, QColor("#e0e0e0"))
        p.setColor(QPalette.ColorRole.Base, QColor("#2d2d2d"))
        p.setColor(QPalette.ColorRole.Text, QColor("#e0e0e0"))
        p.setColor(QPalette.ColorRole.Button, QColor("#3c3c3c"))
        p.setColor(QPalette.ColorRole.ButtonText, QColor("#e0e0e0"))
        p.setColor(QPalette.ColorRole.Highlight, QColor("#4a9eff"))
        p.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    else:
        p.setColor(QPalette.ColorRole.Window, QColor("#f5f5f5"))
        p.setColor(QPalette.ColorRole.WindowText, QColor("#333333"))
        p.setColor(QPalette.ColorRole.Base, QColor("#ffffff"))
        p.setColor(QPalette.ColorRole.Text, QColor("#333333"))
        p.setColor(QPalette.ColorRole.Button, QColor("#e0e0e0"))
        p.setColor(QPalette.ColorRole.ButtonText, QColor("#333333"))
        p.setColor(QPalette.ColorRole.Highlight, QColor("#0078d4"))
        p.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    return p


_QSS_TABLE = {
    "night": _NIGHT_QSS,
    "day": _DAY_QSS,
    "deepblue": _DEEPBLUE_QSS,
}

_PALETTE_TABLE = {
    "night": _make_palette(dark=True),
    "day": _make_palette(dark=False),
    "deepblue": _make_palette(dark=True),
}
