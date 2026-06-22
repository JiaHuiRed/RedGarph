#author Red
#260620 Red&小宋 RedGarph V0.0.1 — 目录扫描与文件导航

import os
import re
from pathlib import Path

from PyQt6.QtCore import QObject, pyqtSignal

from .constants import IMAGE_EXTENSIONS


def _natural_key(name: str):
    """自然排序 key — 'img2' < 'img10'"""
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r"(\d+)", name)]


class FileList(QObject):
    """扫描目录、管理图片文件列表、导航"""

    currentChanged = pyqtSignal(int)        # 当前索引变化
    filesChanged = pyqtSignal()              # 文件列表变化

    def __init__(self, parent=None):
        super().__init__(parent)
        self._files: list[Path] = []
        self._index = -1
        self._directory: Path | None = None

    # ── 属性 ──

    @property
    def directory(self) -> Path | None:
        return self._directory

    @property
    def files(self) -> list[Path]:
        return self._files

    @property
    def index(self) -> int:
        return self._index

    @property
    def current(self) -> Path | None:
        if 0 <= self._index < len(self._files):
            return self._files[self._index]
        return None

    @property
    def count(self) -> int:
        return len(self._files)

    # ── 操作 ──

    def load_directory(self, path: str | Path):
        """扫描目录，加载所有图片"""
        path = Path(path)
        if not path.is_dir():
            return False

        files = []
        for f in sorted(path.iterdir(), key=lambda p: _natural_key(p.name)):
            if f.suffix.lower() in IMAGE_EXTENSIONS and f.is_file():
                files.append(f)

        self._directory = path
        self._files = files
        self._index = 0 if files else -1
        self.filesChanged.emit()
        self.currentChanged.emit(self._index)
        return True

    def go_to(self, index: int):
        """跳转到指定索引"""
        if not self._files:
            return
        index = max(0, min(index, len(self._files) - 1))
        if index != self._index:
            self._index = index
            self.currentChanged.emit(self._index)

    def next_image(self):
        """下一张"""
        self.go_to(self._index + 1)

    def prev_image(self):
        """上一张"""
        self.go_to(self._index - 1)

    def can_next(self) -> bool:
        return self._index < len(self._files) - 1

    def can_prev(self) -> bool:
        return self._index > 0

    def remove_current(self) -> "Path | None":
        """从列表移除当前文件（不写磁盘），返回被移除的路径"""
        if not self._files or self._index < 0:
            return None
        removed = self._files.pop(self._index)
        if not self._files:
            self._index = -1
        elif self._index >= len(self._files):
            self._index = len(self._files) - 1
        self.filesChanged.emit()
        return removed
