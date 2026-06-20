#author Red
#260620 Red&小宋 RedGarph V0.0.1 — 左侧缩略图面板

from pathlib import Path

from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QPixmap, QIcon, QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QListWidgetItem,
    QAbstractItemView,
)

from .constants import THUMB_PANEL_WIDTH, THUMB_SIZE, THUMB_LIST_SIZE


class ThumbBar(QWidget):
    """左侧缩略图面板：竖向列表 + 文件名"""

    thumbnailClicked = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("thumbBar")
        self.setFixedWidth(THUMB_PANEL_WIDTH)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._list = QListWidget()
        self._list.setObjectName("thumbList")
        self._list.setFlow(QListWidget.Flow.TopToBottom)
        self._list.setWrapping(False)
        self._list.setMovement(QListWidget.Movement.Static)
        self._list.setSpacing(1)
        self._list.setIconSize(QSize(THUMB_SIZE, THUMB_SIZE))
        self._list.setGridSize(QSize(THUMB_PANEL_WIDTH, THUMB_LIST_SIZE))
        self._list.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self._list.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self._list.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self._list.setWordWrap(True)
        self._list.setSpacing(2)
        self._list.itemClicked.connect(self._on_clicked)
        layout.addWidget(self._list)

    # ── 加载缩略图 ──

    def set_files(self, files: list[Path], current_index: int):
        """填充缩略图列表"""
        self._list.clear()
        for f in files:
            item = QListWidgetItem()
            px = QPixmap(str(f))
            if not px.isNull():
                thumb = px.scaled(
                    THUMB_SIZE, THUMB_SIZE,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                item.setIcon(QIcon(thumb))
            else:
                # 无法加载的图片用占位图标
                pass

            # 显示文件名（取主名，太长就截断）
            name = f.stem
            if len(name) > 16:
                name = name[:14] + "…"
            item.setText(name)
            item.setToolTip(f.name)
            item.setSizeHint(QSize(THUMB_PANEL_WIDTH - 10, THUMB_LIST_SIZE - 4))
            self._list.addItem(item)

        if 0 <= current_index < len(files):
            self._list.setCurrentRow(current_index)
            self._list.scrollToItem(
                self._list.item(current_index),
                QAbstractItemView.ScrollHint.EnsureVisible,
            )

    def set_current(self, index: int):
        """高亮指定项"""
        if 0 <= index < self._list.count():
            self._list.setCurrentRow(index)
            self._list.scrollToItem(
                self._list.item(index),
                QAbstractItemView.ScrollHint.EnsureVisible,
            )

    def clear(self):
        self._list.clear()

    # ── 信号转发 ──

    def _on_clicked(self, item):
        idx = self._list.row(item)
        self.thumbnailClicked.emit(idx)
