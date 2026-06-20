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
QMainWindow, QWidget { background-color: #1e1e1e; color: #e0e0e0; }

/* ── 标题栏 ── */
#titleBar { background-color: #2d2d2d; border-bottom: 1px solid #3c3c3c; }
#titleLabel { color: #cccccc; font-size: 13px; }

/* ── 缩略图栏 ── */
#thumbBar { background-color: #252525; border-top: 1px solid #3c3c3c; }
#thumbBar QListWidget {
    background-color: #252525; border: none; outline: none;
}
#thumbBar QListWidget::item {
    background-color: transparent; border: 2px solid transparent; border-radius: 4px;
    margin: 4px 2px; padding: 2px;
}
#thumbBar QListWidget::item:selected {
    border: 2px solid #4a9eff; background-color: rgba(74, 158, 255, 0.1);
}
#thumbBar QListWidget::item:hover {
    border: 2px solid #6a6a6a;
}

/* ── 信息栏 ── */
#infoBar {
    background-color: rgba(30, 30, 30, 180); color: #e0e0e0;
    border-radius: 6px; padding: 6px 12px; font-size: 13px;
}

/* ── 缩放指示器 ── */
#zoomLabel {
    background-color: rgba(45, 45, 45, 180); color: #cccccc;
    border-radius: 6px; font-size: 12px;
}

/* ── EXIF 面板 ── */
#exifPanel { background-color: #252525; border: none; }
#exifTitle { background-color: #2d2d2d; color: #cccccc; font-size: 13px; font-weight: bold; border-bottom: 1px solid #3c3c3c; }
#exifTree { background-color: #252525; color: #e0e0e0; border: none; }
#exifTree::item { padding: 3px 6px; border-bottom: 1px solid #2d2d2d; }
#exifTree::item:selected { background-color: rgba(74, 158, 255, 0.15); color: #4a9eff; }
#exifTree QHeaderView::section { background-color: #2d2d2d; color: #aaaaaa; border-bottom: 1px solid #3c3c3c; padding: 4px 6px; font-size: 12px; }

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

#titleBar { background-color: #e8e8e8; border-bottom: 1px solid #d0d0d0; }
#titleLabel { color: #555; font-size: 13px; }

#thumbBar { background-color: #ececec; border-top: 1px solid #d0d0d0; }
#thumbBar QListWidget {
    background-color: #ececec; border: none; outline: none;
}
#thumbBar QListWidget::item {
    background-color: transparent; border: 2px solid transparent; border-radius: 4px;
    margin: 4px 2px; padding: 2px;
}
#thumbBar QListWidget::item:selected {
    border: 2px solid #0078d4; background-color: rgba(0, 120, 212, 0.08);
}
#thumbBar QListWidget::item:hover {
    border: 2px solid #aaa;
}

#infoBar {
    background-color: rgba(245, 245, 245, 200); color: #333;
    border-radius: 6px; padding: 6px 12px; font-size: 13px;
}

#zoomLabel {
    background-color: rgba(220, 220, 220, 200); color: #555;
    border-radius: 6px; font-size: 12px;
}

#exifPanel { background-color: #ececec; border: none; }
#exifTitle { background-color: #e8e8e8; color: #555; font-size: 13px; font-weight: bold; border-bottom: 1px solid #d0d0d0; }
#exifTree { background-color: #ececec; color: #333; border: none; }
#exifTree::item { padding: 3px 6px; border-bottom: 1px solid #e0e0e0; }
#exifTree::item:selected { background-color: rgba(0, 120, 212, 0.1); color: #0078d4; }
#exifTree QHeaderView::section { background-color: #e8e8e8; color: #777; border-bottom: 1px solid #d0d0d0; padding: 4px 6px; font-size: 12px; }

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

#titleBar { background-color: #112240; border-bottom: 1px solid #1a3a5c; }
#titleLabel { color: #8892b0; font-size: 13px; }

#thumbBar { background-color: #0a1628; border-top: 1px solid #1a3a5c; }
#thumbBar QListWidget {
    background-color: #0a1628; border: none; outline: none;
}
#thumbBar QListWidget::item {
    background-color: transparent; border: 2px solid transparent; border-radius: 4px;
    margin: 4px 2px; padding: 2px;
}
#thumbBar QListWidget::item:selected {
    border: 2px solid #5dade2; background-color: rgba(93, 173, 226, 0.1);
}
#thumbBar QListWidget::item:hover {
    border: 2px solid #2c5282;
}

#infoBar {
    background-color: rgba(13, 27, 42, 200); color: #c8d6e5;
    border-radius: 6px; padding: 6px 12px; font-size: 13px;
}

#zoomLabel {
    background-color: rgba(17, 34, 64, 200); color: #8892b0;
    border-radius: 6px; font-size: 12px;
}

#exifPanel { background-color: #0a1628; border: none; }
#exifTitle { background-color: #112240; color: #8892b0; font-size: 13px; font-weight: bold; border-bottom: 1px solid #1a3a5c; }
#exifTree { background-color: #0a1628; color: #c8d6e5; border: none; }
#exifTree::item { padding: 3px 6px; border-bottom: 1px solid #112240; }
#exifTree::item:selected { background-color: rgba(93, 173, 226, 0.12); color: #5dade2; }
#exifTree QHeaderView::section { background-color: #112240; color: #8892b0; border-bottom: 1px solid #1a3a5c; padding: 4px 6px; font-size: 12px; }

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


def _make_palette(dark: bool, accent=None):
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
