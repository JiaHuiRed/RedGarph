#author Red
#260620 Red&小宋 RedGarph V0.0.1 — 图片渲染与交互

from PyQt6.QtCore import Qt, QRectF, QRect, QPoint, QSize
from PyQt6.QtGui import (
    QPixmap, QPainter, QColor, QBrush, QTransform,
    QPen, QFont, QFontMetrics, QAction,
)
from PyQt6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem,
    QLabel, QRubberBand, QApplication,
)

from .constants import ZOOM_FACTOR, ZOOM_MAX, ZOOM_MIN


class ImagePanel(QGraphicsView):
    """图片显示区域：缩放、拖拽、旋转、裁剪、适应窗口"""

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

        # ── 缩放比例指示器（右下角） ──
        self._zoom_label = QLabel(self)
        self._zoom_label.setObjectName("zoomLabel")
        self._zoom_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom
        )
        self._zoom_label.setContentsMargins(6, 4, 10, 6)
        self._zoom_label.setVisible(False)

        # ── 裁剪模式 ──
        self._crop_mode = False
        self._crop_origin: QPoint | None = None
        self._crop_rubber = QRubberBand(QRubberBand.Shape.Rectangle, self)
        self._crop_rubber.hide()
        self._crop_rubber.setStyleSheet(
            "QRubberBand { border: 2px solid #4FC3F7; "
            "background: rgba(79, 195, 247, 0.08); }"
        )

        # ── 裁剪操作提示 ──
        self._crop_hint = QLabel(self)
        self._crop_hint.setObjectName("cropHint")
        self._crop_hint.setText("点击拖拽选区 · Enter 确认 · Esc 取消")
        self._crop_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._crop_hint.setStyleSheet(
            "QLabel { color: #B0BEC5; font: 13px; "
            "background: rgba(0,0,0,0.55); padding: 6px 18px; "
            "border-radius: 4px; }"
        )
        self._crop_hint.adjustSize()
        self._crop_hint.hide()

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

    @property
    def source(self) -> QPixmap:
        """原始图片（未旋转）"""
        return self._source

    def current_pixmap(self) -> QPixmap:
        """返回当前显示状态的图片（含旋转，用于保存/复制）"""
        if self._source.isNull():
            return QPixmap()
        return self._get_rotated_display()

    # ── 内部刷新 ──

    def _get_rotated_display(self) -> QPixmap:
        """返回旋转后的显示用图片"""
        if self._rotation:
            t = QTransform().rotate(self._rotation)
            return self._source.transformed(t, Qt.TransformationMode.SmoothTransformation)
        return self._source

    def _refresh(self):
        """根据 _source / _rotation / _zoom 重建显示"""
        if self._source.isNull():
            self._zoom_label.setVisible(False)
            return

        display = self._get_rotated_display()
        self._item.setPixmap(display)

        # 临时切到居中锚点，避免 AnchorUnderMouse 导致非滚轮缩放时图片偏移
        old_tx = self.transformationAnchor()
        old_rx = self.resizeAnchor()
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)

        if self._zoom is None:
            self._scene.setSceneRect(self._item.boundingRect())
            self.fitInView(self._item, Qt.AspectRatioMode.KeepAspectRatio)
        else:
            self.resetTransform()
            self.scale(self._zoom, self._zoom)

        self.setTransformationAnchor(old_tx)
        self.setResizeAnchor(old_rx)

        self._update_zoom_label()

    def _update_zoom_label(self):
        """更新右下角缩放比例指示器"""
        if self._source.isNull():
            self._zoom_label.setVisible(False)
            return
        if self._zoom is None:
            text = "适应窗口"
        else:
            pct = int(self._zoom * 100)
            text = f"{pct}%"
        self._zoom_label.setText(text)
        self._zoom_label.setVisible(True)
        self._zoom_label.adjustSize()
        # 定位到右下角
        margins = self._zoom_label.contentsMargins()
        lw = self._zoom_label.width() + margins.left() + margins.right() + 10
        lh = self._zoom_label.height() + margins.top() + margins.bottom() + 6
        self._zoom_label.move(
            self.width() - lw - 8,
            self.height() - lh - 8,
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._zoom is None and not self._source.isNull():
            old_tx = self.transformationAnchor()
            old_rx = self.resizeAnchor()
            self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
            self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
            self._scene.setSceneRect(self._item.boundingRect())
            self.fitInView(self._item, Qt.AspectRatioMode.KeepAspectRatio)
            self.setTransformationAnchor(old_tx)
            self.setResizeAnchor(old_rx)
        self._update_zoom_label()
        # 裁剪模式下重定位提示
        if self._crop_mode and self._crop_hint.isVisible():
            cx = (self.width() - self._crop_hint.width()) // 2
            self._crop_hint.move(cx, 20)

    # ── 鼠标滚轮缩放 ──

    def wheelEvent(self, event):
        if self._source.isNull():
            return

        if self._zoom is None:
            self._zoom = 1.0

        factor = ZOOM_FACTOR ** (event.angleDelta().y() / 120)
        new_zoom = self._zoom * factor
        new_zoom = max(ZOOM_MIN, min(ZOOM_MAX, new_zoom))
        self._zoom = new_zoom

        # 直接缩放，保留 AnchorUnderMouse 以鼠标为中心
        self.resetTransform()
        self.scale(self._zoom, self._zoom)
        self._update_zoom_label()
        event.accept()

    # ── 双击切换 ──

    def mouseDoubleClickEvent(self, event):
        if self._source.isNull():
            return
        if self._crop_mode:
            return  # 裁剪模式下不切换
        if self._zoom is None:
            self.actual_size()
        else:
            self.fit_to_window()
        event.accept()

    # ═══════════════════════════════════════════
    # ── 裁剪模式 ──
    # ═══════════════════════════════════════════

    @property
    def is_crop_mode(self) -> bool:
        return self._crop_mode

    def enter_crop_mode(self):
        """进入裁剪模式"""
        if self._source.isNull():
            return
        self._crop_mode = True
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self._crop_origin = None
        self._crop_rubber.hide()
        # 提示居中显示
        self._crop_hint.adjustSize()
        cx = (self.width() - self._crop_hint.width()) // 2
        self._crop_hint.move(cx, 20)
        self._crop_hint.show()

    def exit_crop_mode(self, apply: bool = False):
        """退出裁剪模式"""
        self._crop_mode = False
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self._crop_rubber.hide()
        self._crop_hint.hide()
        self._crop_origin = None
        if apply and not self._source.isNull():
            rect = self._crop_rubber.geometry()
            if rect.width() > 4 and rect.height() > 4:
                self._do_crop(rect)

    def cancel_crop(self):
        """取消裁剪并退出裁剪模式"""
        self.exit_crop_mode(apply=False)

    def apply_crop(self):
        """确认裁剪"""
        self.exit_crop_mode(apply=True)

    def _do_crop(self, viewport_rect: QRect):
        """执行裁剪"""
        # 视口坐标 → 场景坐标
        scene_rect = self.mapToScene(viewport_rect).boundingRect()
        # 场景坐标 → 图元坐标（减去 item 位置偏移）
        item_pos = self._item.pos()
        img_rect = QRect(
            int(scene_rect.x() - item_pos.x()),
            int(scene_rect.y() - item_pos.y()),
            int(scene_rect.width()),
            int(scene_rect.height()),
        ).normalized()

        # 裁剪当前显示的图片（已旋转）
        display = self._get_rotated_display()

        # 边界保护
        if display.isNull():
            return
        img_rect = img_rect.intersected(display.rect())
        if img_rect.width() < 2 or img_rect.height() < 2:
            return

        cropped = display.copy(img_rect)

        # 如果图片被旋转过，裁剪后反向旋转回原始方向
        if self._rotation:
            t2 = QTransform().rotate(-self._rotation)
            cropped = cropped.transformed(
                t2, Qt.TransformationMode.SmoothTransformation
            )
            # 从裁剪版重建 _source（无旋转）
            self._source = cropped
            self._rotation = 0
        else:
            self._source = cropped

        self._zoom = None
        self._refresh()

    # ── 裁剪模式鼠标事件 ──

    def mousePressEvent(self, event):
        if self._crop_mode and event.button() == Qt.MouseButton.LeftButton:
            self._crop_origin = event.pos()
            self._crop_rubber.setGeometry(QRect(self._crop_origin, QSize()))
            self._crop_rubber.show()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._crop_mode and self._crop_origin is not None:
            rect = QRect(self._crop_origin, event.pos()).normalized()
            self._crop_rubber.setGeometry(rect)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._crop_mode:
            # 裁剪框画完，等待 Enter / Esc
            event.accept()
            return
        super().mouseReleaseEvent(event)
