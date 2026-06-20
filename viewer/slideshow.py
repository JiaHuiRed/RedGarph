#author Red
#260620 Red&小宋 RedGarph V0.1.0 — 幻灯片播放

from PyQt6.QtCore import QObject, QTimer, pyqtSignal

from .constants import SLIDESHOW_INTERVAL


class Slideshow(QObject):
    """定时自动翻页"""

    nextRequested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_tick)
        self._interval = SLIDESHOW_INTERVAL

    @property
    def is_active(self) -> bool:
        return self._timer.isActive()

    @property
    def interval(self) -> int:
        return self._interval

    @interval.setter
    def interval(self, sec: int):
        self._interval = max(1, sec)
        if self._timer.isActive():
            self._timer.start(self._interval * 1000)

    def start(self, interval: int | None = None):
        if interval is not None:
            self._interval = max(1, interval)
        self._timer.start(self._interval * 1000)

    def stop(self):
        self._timer.stop()

    def toggle(self):
        if self._timer.isActive():
            self.stop()
        else:
            self.start()

    def _on_tick(self):
        self.nextRequested.emit()
