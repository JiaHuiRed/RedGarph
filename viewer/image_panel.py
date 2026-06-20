#author Red
#260620 Red&小宋 RedGarph V0.1.0 — 图片渲染与交互

from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import (
    QPixmap, QPainter, QColor, QBrush, QTransform,
)
from PyQt6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem,
)

from .constants import ZOOM_FACTOR, ZOOM_MAX, ZOOM_MIN


class ImagePanel(QGraphicsView):
    """图片显示区域：缩放、拖拽、旋转、适应窗口"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # ── 场景与图元 ──
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self._item = QGraphicsPixmapItem()
        self._scene.addItem(self._item)

        # ── 状态 ──
        self._source = QPixmap()   # 原始未旋转的图片
        self._zoom: float | None = None   # None = 适应窗口模式
        self._rotation = 0          # 0/90/180/270

        # ── 渲染设置 ──
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse
        )
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setViewportUpdateMode(
            QGraphicsView.ViewportUpdateMode.SmartViewportUpdate
        )
        self.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.setBackgroundBrush(QBrush(QColor(30, 30, 30)))

        # 启动鼠标追踪，让拖拽模式正常工作
        self.setMouseTracking(True)

    # ── 图片加载 ──

    def load_image(self, path: str) -> bool:
        """加载图片，适应窗口显示"""
        pix = QPixmap(path)
        if pix.isNull():
            return False
        self._source = pix
        self._rotation = 0
        self._zoom = None
        self._refresh()
        return True

    @property
    def has_image(self) -> bool:
        return not self._source.isNull()

    # ── 缩放 ──

    def fit_to_window(self):
        """适应窗口大小"""
        if self._source.isNull():
            return
        self._zoom = None
        self._refresh()

    def actual_size(self):
        """100% 原始尺寸"""
        if self._source.isNull():
            return
        self._zoom = 1.0
        self._refresh()

    def zoom_in(self):
        """放大"""
        if self._source.isNull():
            return
        if self._zoom is None:
            self._zoom = 1.0
        self._zoom = min(ZOOM_MAX, self._zoom * ZOOM_FACTOR)
        self._refresh()

    def zoom_out(self):
        """缩小"""
        if self._source.isNull():
            return
        if self._zoom is None:
            self._zoom = 1.0
        self._zoom = max(ZOOM_MIN, self._zoom / ZOOM_FACTOR)
        self._refresh()

    # ── 旋转 ──

    def rotate_right(self):
        """顺时针旋转 90°"""
        if self._source.isNull():
            return
        self._rotation = (self._rotation + 90) % 360
        self._refresh()

    def rotate_left(self):
        """逆时针旋转 90°"""
        if self._source.isNull():
            return
        self._rotation = (self._rotation - 90) % 360
        self._refresh()

    # ── 内部刷新 ──

    def _refresh(self):
        """根据 _source / _rotation / _zoom 重建显示"""
        if self._source.isNull():
            return

        # 应用旋转到原始图片
        if self._rotation:
            t = QTransform().rotate(self._rotation)
            display = self._source.transformed(t, Qt.TransformationMode.SmoothTransformation)
        else:
            display = self._source
        self._item.setPixmap(display)

        # 应用缩放
        if self._zoom is None:
            # 适应窗口
            self.resetTransform()
            self.fitInView(self._item, Qt.AspectRatioMode.KeepAspectRatio)
        else:
            self.resetTransform()
            self.scale(self._zoom, self._zoom)

    # ── 鼠标滚轮缩放 ──

    def wheelEvent(self, event):
        if self._source.isNull():
            return

        # 如果当前是适应模式，先从 1.0 开始缩放
        if self._zoom is None:
            self._zoom = 1.0

        factor = ZOOM_FACTOR ** (event.angleDelta().y() / 120)
        new_zoom = self._zoom * factor
        new_zoom = max(ZOOM_MIN, min(ZOOM_MAX, new_zoom))
        self._zoom = new_zoom
        self._refresh()
        event.accept()

    # ── 双击切换 ──

    def mouseDoubleClickEvent(self, event):
        if self._source.isNull():
            return
        if self._zoom is None:
            self.actual_size()
        else:
            self.fit_to_window()
        event.accept()
