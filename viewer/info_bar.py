#author Red
#260620 Red&小宋 RedGarph V0.0.1 — 图片信息浮层

import os
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel, QSizePolicy, QVBoxLayout, QWidget


def _format_size(size_bytes: int) -> str:
    """可读文件大小"""
    b = float(size_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if b < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} TB"


class InfoBar(QWidget):
    """底部半透明信息栏 — 文件名、尺寸、大小、页码"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("infoBar")
        self.setVisible(False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        self._label = QLabel()
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._label)

        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Minimum,
        )

    def show_info(self, path: Path | None, pixmap: QPixmap | None = None):
        if not path:
            self._label.setText("")
            return

        name = path.name
        size_str = _format_size(path.stat().st_size)

        if pixmap and not pixmap.isNull():
            dim = f"{pixmap.width()} × {pixmap.height()}"
            self._label.setText(f"{name}  —  {dim}  —  {size_str}")
        else:
            self._label.setText(f"{name}  —  {size_str}")

    def show_page(self, index: int, total: int):
        """追加页码信息（不覆盖已设置的内容）"""
        current = self._label.text()
        if current:
            self._label.setText(f"{current}  —  {index + 1}/{total}")
        else:
            self._label.setText(f"{index + 1}/{total}")

    def toggle(self):
        self.setVisible(not self.isVisible())

    def hide(self):
        self.setVisible(False)

    def show(self):
        self.setVisible(True)
