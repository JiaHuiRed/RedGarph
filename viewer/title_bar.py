#author Red
#260802 Red&小宋 RedGarph V0.1.6 — 标题栏组件

from PyQt6.QtCore import QPoint, Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtWidgets import (
    QPushButton, QWidget, QHBoxLayout, QLabel,
)

# ── 标题栏尺寸 ──

TITLEBAR_HEIGHT = 34

TRAFFIC_SIZE = 12

TRAFFIC_MARGIN = 8

# ── macOS 交通灯颜色 ──

COLOR_CLOSE = "#ff5f56"

COLOR_MINIMIZE = "#ffbd2e"

COLOR_MAXIMIZE = "#27c93f"


# ═══════════════════════════════════════════
# ── 交通灯按钮 ──
# ═══════════════════════════════════════════

class TrafficButton(QPushButton):

    """纯色圆点交通灯按钮"""

    def __init__(self, color: str):

        super().__init__()

        self._color = color

        self.setFixedSize(TRAFFIC_SIZE, TRAFFIC_SIZE)

        self.setCursor(Qt.CursorShape.ArrowCursor)

    def paintEvent(self, event):

        p = QPainter(self)

        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        p.setBrush(QColor(self._color))

        p.setPen(Qt.PenStyle.NoPen)

        p.drawEllipse(self.rect())

        p.end()


# ═══════════════════════════════════════════
# ── macOS 风格标题栏 ──
# ═══════════════════════════════════════════

class TitleBar(QWidget):

    """自定义标题栏：交通灯 + 标题 + 拖拽移动"""

    close_clicked = pyqtSignal()

    minimize_clicked = pyqtSignal()

    maximize_clicked = pyqtSignal()

    def __init__(self, title: str = "RedGarph", version: str = "", parent=None):

        super().__init__(parent)

        self.setObjectName("titleBar")

        self.setFixedHeight(TITLEBAR_HEIGHT)

        self._drag_pos = QPoint()

        self._dragging = False

        layout = QHBoxLayout(self)

        layout.setContentsMargins(TRAFFIC_MARGIN, 0, TRAFFIC_MARGIN, 0)

        layout.setSpacing(TRAFFIC_MARGIN)

        layout.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )

        # ── 交通灯 ──

        self.btn_close = TrafficButton(COLOR_CLOSE)

        self.btn_min = TrafficButton(COLOR_MINIMIZE)

        self.btn_max = TrafficButton(COLOR_MAXIMIZE)

        self.btn_close.clicked.connect(self.close_clicked.emit)

        self.btn_min.clicked.connect(self.minimize_clicked.emit)

        self.btn_max.clicked.connect(self.maximize_clicked.emit)

        layout.addWidget(self.btn_close)

        layout.addWidget(self.btn_min)

        layout.addWidget(self.btn_max)

        # ── 版本号 ──

        if version:

            ver_label = QLabel(f"v{version}")

            ver_label.setObjectName("verLabel")

            layout.addWidget(ver_label)

        # ── 标题 ──

        self.title_label = QLabel(title)

        self.title_label.setObjectName("titleLabel")

        layout.addSpacing(12)

        layout.addWidget(self.title_label, 1, Qt.AlignmentFlag.AlignLeft)

    def set_title(self, text: str):

        self.title_label.setText(text)

    # ── 窗口拖拽 ──

    def mousePressEvent(self, event):

        if event.button() == Qt.MouseButton.LeftButton:

            self._drag_pos = event.globalPosition().toPoint()

            self._dragging = True

            event.accept()

    def mouseMoveEvent(self, event):

        if self._dragging and event.buttons() == Qt.MouseButton.LeftButton:

            win = self.window()

            if win.isMaximized() or win.isFullScreen():

                return

            delta = event.globalPosition().toPoint() - self._drag_pos

            win.move(win.x() + delta.x(), win.y() + delta.y())

            self._drag_pos = event.globalPosition().toPoint()

            event.accept()

    def mouseReleaseEvent(self, event):

        if event.button() == Qt.MouseButton.LeftButton:

            self._dragging = False

            event.accept()

    def mouseDoubleClickEvent(self, event):

        if event.button() == Qt.MouseButton.LeftButton:

            self.maximize_clicked.emit()

            event.accept()
