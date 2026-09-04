#author Red
#260620 Red&小宋 RedGarph V0.0.1 — 目录扫描与文件导航

import os
import re
from pathlib import Path

from PyQt6.QtCore import QObject, QRunnable, QThreadPool, pyqtSignal

from .constants import IMAGE_EXTENSIONS


def _natural_key(name: str):
    """自然排序 key — 'img2' < 'img10'"""
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r"(\d+)", name)]


def _scan_directory(path: Path, selected: str | Path | None = None):
    """使用 scandir 扫描目录；该函数不接触 Qt，可安全运行在工作线程。"""
    try:
        if not path.is_dir():
            return path, [], -1, False
        files = []
        with os.scandir(path) as entries:
            for entry in entries:
                try:
                    if (
                        Path(entry.name).suffix.lower() in IMAGE_EXTENSIONS
                        and entry.is_file()
                    ):
                        files.append(Path(entry.path))
                except OSError:
                    continue
        files.sort(key=lambda p: _natural_key(p.name))
    except OSError:
        return path, [], -1, True

    index = 0 if files else -1
    if selected is not None and files:
        selected_key = os.path.normcase(os.path.abspath(os.fspath(selected)))
        for i, file_path in enumerate(files):
            if os.path.normcase(os.path.abspath(os.fspath(file_path))) == selected_key:
                index = i
                break
    return path, files, index, True


class _DirectorySignals(QObject):
    finished = pyqtSignal(int, object, object, int, bool)


class _DirectoryTask(QRunnable):
    def __init__(self, request_id: int, path: Path, selected: str | Path | None):
        super().__init__()
        self.request_id = request_id
        self.path = path
        self.selected = selected
        self.signals = _DirectorySignals()

    def run(self):
        path, files, index, is_directory = _scan_directory(self.path, self.selected)
        self.signals.finished.emit(
            self.request_id, path, files, index, is_directory
        )


class FileList(QObject):
    """扫描目录、管理图片文件列表、导航"""

    currentChanged = pyqtSignal(int)        # 当前索引变化
    filesChanged = pyqtSignal()              # 文件列表变化
    directoryLoadFinished = pyqtSignal(object, bool)  # (目录, 是否有图片)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._files: list[Path] = []
        self._index = -1
        self._directory: Path | None = None
        self._load_generation = 0
        self._directory_tasks: dict[int, _DirectoryTask] = {}

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

    def _commit_directory(self, path: Path, files: list[Path], index: int):
        self._directory = path
        self._files = files
        self._index = index
        self.filesChanged.emit()
        self.currentChanged.emit(self._index)

    def load_directory(self, path: str | Path, selected: str | Path | None = None):
        """扫描目录，加载所有图片"""
        path = Path(path)
        if not path.is_dir():
            return False
        self._load_generation += 1
        _, files, index, _ = _scan_directory(path, selected)
        self._commit_directory(path, files, index)
        return bool(files)

    def load_directory_async(
        self, path: str | Path, selected: str | Path | None = None
    ):
        """异步扫描目录；新请求会使尚未完成的旧请求失效。"""
        self._load_generation += 1
        request_id = self._load_generation
        task = _DirectoryTask(request_id, Path(path), selected)
        self._directory_tasks[request_id] = task
        task.signals.finished.connect(self._on_directory_loaded)
        QThreadPool.globalInstance().start(task)

    def _on_directory_loaded(
        self,
        request_id: int,
        path: Path,
        files: list[Path],
        index: int,
        is_directory: bool,
    ):
        self._directory_tasks.pop(request_id, None)
        if request_id != self._load_generation:
            return
        if not is_directory:
            self.directoryLoadFinished.emit(path, False)
            return
        self._commit_directory(path, files, index)
        self.directoryLoadFinished.emit(path, bool(files))

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
        self.currentChanged.emit(self._index)
        return removed
