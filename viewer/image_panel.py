#author Red
#260620 Red&小宋 RedGarph V0.0.1 — 图片渲染与交互

from PyQt6.QtCore import Qt, QRectF, QRect, QPoint, pyqtSignal
from PyQt6.QtGui import (
    QPixmap, QPainter, QColor, QBrush, QTransform,
    QPen, QFont, QFontMetrics, QAction, QImageReader,
)
from PyQt6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem,
    QLabel, QWidget, QApplication, QHBoxLayout, QPushButton,
)
from collections import OrderedDict
from pathlib import Path

from .constants import ZOOM_FACTOR, ZOOM_MAX, ZOOM_MIN

# 显示用解码长边上限：超过则缩小解码，保存/裁剪时再按全分辨率处理
_DISPLAY_MAX = 3840


class _CropOverlay(QWidget):
    """裁剪选区覆盖层：暗化外部 + 选区边框 + 三分线 + 8 向调整手柄"""

    _HS = 6       # 手柄半宽
    _MIN = 30     # 选区最小尺寸

    _CURSORS = {
        'tl': Qt.CursorShape.SizeFDiagCursor,
        'tr': Qt.CursorShape.SizeBDiagCursor,
        'bl': Qt.CursorShape.SizeBDiagCursor,
        'br': Qt.CursorShape.SizeFDiagCursor,
        't':  Qt.CursorShape.SizeVerCursor,
        'b':  Qt.CursorShape.SizeVerCursor,
        'l':  Qt.CursorShape.SizeHorCursor,
        'r':  Qt.CursorShape.SizeHorCursor,
    }

    def __init__(self, parent):
        super().__init__(parent)
        self._rect = QRect()
        self._state = 'idle'
        self._start = QPoint()
        self._snap = QRect()
        self.setMouseTracking(True)
        self.hide()

    def selection_rect(self) -> QRect:
        return self._rect if self._rect.isValid() else QRect()

    def reset(self):
        self._rect = QRect()
        self._state = 'idle'

    def _handles(self) -> dict[str, QRect]:
        r = self._rect
        if not r.isValid():
            return {}
        hs = self._HS
        cx, cy = r.center().x(), r.center().y()
        return {
            'tl': QRect(r.left() - hs, r.top() - hs, 2 * hs, 2 * hs),
            't':  QRect(cx - hs, r.top() - hs, 2 * hs, 2 * hs),
            'tr': QRect(r.right() - hs, r.top() - hs, 2 * hs, 2 * hs),
            'l':  QRect(r.left() - hs, cy - hs, 2 * hs, 2 * hs),
            'r':  QRect(r.right() - hs, cy - hs, 2 * hs, 2 * hs),
            'bl': QRect(r.left() - hs, r.bottom() - hs, 2 * hs, 2 * hs),
            'b':  QRect(cx - hs, r.bottom() - hs, 2 * hs, 2 * hs),
            'br': QRect(r.right() - hs, r.bottom() - hs, 2 * hs, 2 * hs),
        }

    def _handle_at(self, pos) -> str | None:
        for name, h in self._handles().items():
            if h.contains(pos):
                return name
        return None

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        r = self._rect

        if r.isValid() and r.width() > 2 and r.height() > 2:
            dark = QColor(0, 0, 0, 140)
            p.fillRect(QRect(0, 0, w, r.top()), dark)
            p.fillRect(QRect(0, r.bottom() + 1, w, h - r.bottom() - 1), dark)
            p.fillRect(QRect(0, r.top(), r.left(), r.height()), dark)
            p.fillRect(QRect(r.right() + 1, r.top(), w - r.right() - 1, r.height()), dark)
        else:
            p.fillRect(self.rect(), QColor(0, 0, 0, 80))
            return

        p.setPen(QPen(QColor(255, 255, 255), 1.5))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRect(r)

        grid = QPen(QColor(255, 255, 255, 80), 0.5, Qt.PenStyle.DashLine)
        p.setPen(grid)
        for i in (1, 2):
            x = int(r.left() + r.width() * i / 3)
            y = int(r.top() + r.height() * i / 3)
            p.drawLine(x, r.top(), x, r.bottom())
            p.drawLine(r.left(), y, r.right(), y)

        p.setPen(QPen(QColor(79, 195, 247), 1.5))
        p.setBrush(QBrush(QColor(255, 255, 255)))
        for hr in self._handles().values():
            p.drawRect(hr)

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            super().mousePressEvent(event)
            return
        pos = event.pos()

        handle = self._handle_at(pos)
        if handle:
            self._state = handle
            self._snap = QRect(self._rect)
            return

        if self._rect.contains(pos):
            self._state = 'moving'
            self._snap = QRect(self._rect)
            self._start = pos
            return

        self._state = 'selecting'
        self._start = pos
        self._rect = QRect()

    def mouseMoveEvent(self, event):
        pos = event.pos()

        if self._state == 'selecting':
            self._rect = QRect(self._start, pos).normalized()

        elif self._state == 'moving':
            delta = pos - self._start
            r2 = QRect(self._snap.topLeft() + delta, self._snap.size())
            r2 = r2.intersected(self.rect().adjusted(0, 0, -1, -1))
            if r2.width() >= self._MIN and r2.height() >= self._MIN:
                self._rect = r2

        elif self._state in self._CURSORS:
            self._rect = self._resize_rect(pos)

        else:
            handle = self._handle_at(pos)
            if handle:
                self.setCursor(self._CURSORS[handle])
            elif self._rect.contains(pos):
                self.setCursor(Qt.CursorShape.SizeAllCursor)
            else:
                self.setCursor(Qt.CursorShape.CrossCursor)
            return

        self.update()

    def _resize_rect(self, pos) -> QRect:
        r = QRect(self._snap)
        s = self._state
        if 'l' in s:
            r.setLeft(min(pos.x(), r.right() - self._MIN))
        if 'r' in s:
            r.setRight(max(pos.x(), r.left() + self._MIN))
        if 't' in s:
            r.setTop(min(pos.y(), r.bottom() - self._MIN))
        if 'b' in s:
            r.setBottom(max(pos.y(), r.top() + self._MIN))
        return r.normalized()

    def mouseReleaseEvent(self, event):
        if self._state != 'idle':
            self._state = 'idle'
            event.accept()
            return
        super().mouseReleaseEvent(event)


class ImagePanel(QGraphicsView):
    """图片显示区域：缩放、拖拽、旋转、裁剪、适应窗口"""

    cropConfirmed = pyqtSignal()
    cropCancelled = pyqtSignal()
    toggleCropRequested = pyqtSignal()
    saveRequested = pyqtSignal()
    modifiedChanged = pyqtSignal(bool)

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
        self._full_path: str | None = None  # 磁盘原图路径；裁剪/编辑后置 None
        self._modified = False

        # ── 图片缓存（LRU，避免翻页时重复解码） ──
        self._cache: OrderedDict[str, tuple[tuple[int, int], QPixmap]] = OrderedDict()
        self._cache_max = 20

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

        # ── 底部工具栏（裁剪 / 保存） ──
        self._bottom_toolbar = QWidget(self)
        self._bottom_toolbar.setObjectName("bottomToolbar")
        tb_layout = QHBoxLayout(self._bottom_toolbar)
        tb_layout.setContentsMargins(0, 0, 0, 0)
        tb_layout.setSpacing(6)

        style_btn = (
            "QPushButton { color: #90A4AE; background: rgba(255,255,255,0.06); "
            "border: 1px solid rgba(255,255,255,0.1); border-radius: 4px; "
            "padding: 3px 10px; font: 12px; }"
            "QPushButton:hover { color: #ECEFF1; background: rgba(255,255,255,0.14); }"
        )

        self._btn_toggle_crop = QPushButton("裁剪")
        self._btn_toggle_crop.setObjectName("btnToggleCrop")
        self._btn_toggle_crop.setCheckable(True)
        self._btn_toggle_crop.setCursor(Qt.CursorShape.ArrowCursor)
        self._btn_toggle_crop.setStyleSheet(
            style_btn +
            "QPushButton:checked { color: #4FC3F7; background: rgba(79,195,247,0.15); "
            "border-color: #4FC3F7; }"
        )
        self._btn_toggle_crop.toggled.connect(self._on_toggle_crop)

        self._btn_save = QPushButton("保存")
        self._btn_save.setObjectName("btnSave")
        self._btn_save.setCursor(Qt.CursorShape.ArrowCursor)
        self._btn_save.setStyleSheet(style_btn)
        self._btn_save.clicked.connect(self._emit_save)

        tb_layout.addWidget(self._btn_toggle_crop)
        tb_layout.addWidget(self._btn_save)
        self._bottom_toolbar.adjustSize()
        self._bottom_toolbar.hide()

        # ── 裁剪模式 ──
        self._crop_mode = False
        self._crop_overlay = _CropOverlay(self.viewport())

        # ── 裁剪操作提示 ──
        self._crop_hint = QLabel(self)
        self._crop_hint.setObjectName("cropHint")
        self._crop_hint.setText("拖拽选区 · 调整边缘 · Enter 确认 · Esc 取消")
        self._crop_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._crop_hint.setStyleSheet(
            "QLabel { color: #B0BEC5; font: 13px; "
            "background: rgba(0,0,0,0.55); padding: 6px 18px; "
            "border-radius: 4px; }"
        )
        self._crop_hint.adjustSize()
        self._crop_hint.hide()

        # ── 裁剪操作按钮 ──
        self._crop_btn_bar = QWidget(self)
        self._crop_btn_bar.setObjectName("cropBtnBar")
        self._crop_btn_bar.setStyleSheet(
            "QWidget#cropBtnBar { background: rgba(0,0,0,0.65); "
            "border-radius: 6px; }"
        )
        self._crop_btn_bar.setFixedHeight(44)
        bar_layout = QHBoxLayout(self._crop_btn_bar)
        bar_layout.setContentsMargins(12, 6, 12, 6)
        bar_layout.setSpacing(10)

        self._btn_crop_apply = QPushButton("确认裁剪")
        self._btn_crop_apply.setObjectName("cropApplyBtn")
        self._btn_crop_apply.setCursor(Qt.CursorShape.ArrowCursor)
        self._btn_crop_apply.setStyleSheet(
            "QPushButton { color: #fff; background: #1976D2; "
            "border: none; border-radius: 4px; padding: 4px 16px; "
            "font: 13px; min-width: 80px; }"
            "QPushButton:hover { background: #2196F3; }"
            "QPushButton:pressed { background: #1565C0; }"
        )
        self._btn_crop_apply.clicked.connect(self.apply_crop)

        self._btn_crop_cancel = QPushButton("取消")
        self._btn_crop_cancel.setObjectName("cropCancelBtn")
        self._btn_crop_cancel.setCursor(Qt.CursorShape.ArrowCursor)
        self._btn_crop_cancel.setStyleSheet(
            "QPushButton { color: #ccc; background: rgba(255,255,255,0.08); "
            "border: none; border-radius: 4px; padding: 4px 16px; "
            "font: 13px; min-width: 80px; }"
            "QPushButton:hover { color: #fff; background: rgba(255,255,255,0.15); }"
            "QPushButton:pressed { background: rgba(255,255,255,0.05); }"
        )
        self._btn_crop_cancel.clicked.connect(self.cancel_crop)

        bar_layout.addWidget(self._btn_crop_apply)
        bar_layout.addWidget(self._btn_crop_cancel)
        self._crop_btn_bar.hide()

    # ── 图片加载 ──

    @staticmethod
    def _file_signature(path: str) -> tuple[int, int] | None:
        try:
            stat = Path(path).stat()
        except OSError:
            return None
        return stat.st_mtime_ns, stat.st_size

    def invalidate_cache(self, path: str | Path | None = None):
        """清理指定文件或全部文件的显示缓存。"""
        if path is None:
            self._cache.clear()
        else:
            self._cache.pop(str(path), None)

    def load_image(self, path: str) -> bool:
        """加载图片，适应窗口显示（大图缩小解码，翻页更快）"""
        if self._crop_mode:
            self.exit_crop_mode(apply=False)

        if not path:
            self._source = QPixmap()
            self._rotation = 0
            self._zoom = None
            self._full_path = None
            self._set_modified(False)
            self._item.setPixmap(QPixmap())
            self._scene.setSceneRect(QRectF())
            self._refresh()
            return True

        # 缓存命中：直接使用内存中的 pixmap，跳过磁盘解码
        signature = self._file_signature(path)
        cached = self._cache.get(path)
        if cached is not None and signature is not None and cached[0] == signature:
            self._source = cached[1]
            self._cache.move_to_end(path)
            self._rotation = 0
            self._zoom = None
            self._full_path = path
            self._set_modified(False)
            self._refresh()
            return True

        if cached is not None:
            self._cache.pop(path, None)

        # 缩小解码：长边超过 _DISPLAY_MAX 时按比例缩小，避免全尺寸同步解码卡顿
        reader = QImageReader(path)
        reader.setAutoTransform(True)  # 应用 EXIF 方向
        size = reader.size()
        if size.isValid() and max(size.width(), size.height()) > _DISPLAY_MAX:
            reader.setScaledSize(
                size.scaled(_DISPLAY_MAX, _DISPLAY_MAX, Qt.AspectRatioMode.KeepAspectRatio)
            )
        img = reader.read()
        if img.isNull():
            # 失败时清空旧图，避免调用方看到“新路径 + 旧画面”的不一致状态。
            self.load_image("")
            return False
        pix = QPixmap.fromImage(img)

        # 写入 LRU 缓存
        signature = self._file_signature(path)
        if signature is not None:
            self._cache[path] = (signature, pix)
            if len(self._cache) > self._cache_max:
                self._cache.popitem(last=False)

        self._source = pix
        self._rotation = 0
        self._zoom = None
        self._full_path = path
        self._set_modified(False)
        self._refresh()
        return True

    @property
    def has_image(self) -> bool:
        return not self._source.isNull()

    @property
    def is_modified(self) -> bool:
        return self._modified

    def _set_modified(self, value: bool):
        value = bool(value)
        if value != self._modified:
            self._modified = value
            self.modifiedChanged.emit(value)

    def mark_saved(self):
        """标记当前编辑状态已成功写入磁盘。"""
        self._set_modified(False)

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
        self._set_modified(True)
        self._refresh()

    def rotate_left(self):
        """逆时针旋转 90°"""
        if self._source.isNull():
            return
        self._rotation = (self._rotation - 90) % 360
        self._set_modified(True)
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

    def full_res_pixmap(self) -> QPixmap:
        """全分辨率图片（含旋转）。

        未编辑过时从磁盘全尺寸重解码，保存不丢分辨率；
        已编辑（裁剪）过则直接用内存中的 _source。
        """
        if self._source.isNull():
            return QPixmap()
        if self._full_path is None:
            return self._get_rotated_display()
        reader = QImageReader(self._full_path)
        reader.setAutoTransform(True)
        img = reader.read()
        if img.isNull():
            return self._get_rotated_display()
        pix = QPixmap.fromImage(img)
        if self._rotation:
            t = QTransform().rotate(self._rotation)
            pix = pix.transformed(t, Qt.TransformationMode.SmoothTransformation)
        return pix

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
            self._item.setPixmap(QPixmap())
            self._scene.setSceneRect(QRectF())
            self._zoom_label.setVisible(False)
            self._bottom_toolbar.hide()
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
        self._bottom_toolbar.show()

    def _update_zoom_label(self):
        """更新右下角缩放比例指示器 + 工具栏定位"""
        if self._source.isNull():
            self._zoom_label.setVisible(False)
            self._bottom_toolbar.hide()
            return
        if self._zoom is None:
            text = "适应窗口"
        else:
            pct = int(self._zoom * 100)
            text = f"{pct}%"
        self._zoom_label.setText(text)
        self._zoom_label.setVisible(True)
        self._zoom_label.adjustSize()
        # 定位缩放标签到右下角
        margins = self._zoom_label.contentsMargins()
        lw = self._zoom_label.width() + margins.left() + margins.right() + 10
        lh = self._zoom_label.height() + margins.top() + margins.bottom() + 6
        zx = self.width() - lw - 8
        zy = self.height() - lh - 8
        self._zoom_label.move(zx, zy)
        # 工具栏放在缩放标签左边
        self._bottom_toolbar.adjustSize()
        tw = self._bottom_toolbar.width()
        th = self._bottom_toolbar.height()
        self._bottom_toolbar.move(
            zx - tw - 8,
            zy + (lh - th) // 2,
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
        # 裁剪模式下更新叠加层和提示
        if self._crop_mode:
            self._crop_overlay.setGeometry(self.viewport().rect())
            if self._crop_hint.isVisible():
                cx = (self.width() - self._crop_hint.width()) // 2
                self._crop_hint.move(cx, 20)
            if self._crop_btn_bar.isVisible():
                bx = (self.width() - self._crop_btn_bar.width()) // 2
                self._crop_btn_bar.move(bx, self.height() - self._crop_btn_bar.height() - 20)

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
        self._crop_overlay.reset()
        self._crop_overlay.setGeometry(self.viewport().rect())
        self._crop_overlay.show()
        self._crop_overlay.raise_()
        # 同步工具栏按钮
        self._btn_toggle_crop.blockSignals(True)
        self._btn_toggle_crop.setChecked(True)
        self._btn_toggle_crop.blockSignals(False)
        # 提示居中显示
        self._crop_hint.adjustSize()
        cx = (self.width() - self._crop_hint.width()) // 2
        self._crop_hint.move(cx, 20)
        self._crop_hint.show()
        # 按钮栏居中显示
        self._crop_btn_bar.adjustSize()
        bx = (self.width() - self._crop_btn_bar.width()) // 2
        self._crop_btn_bar.move(bx, self.height() - self._crop_btn_bar.height() - 20)
        self._crop_btn_bar.show()

    def exit_crop_mode(self, apply: bool = False):
        """退出裁剪模式"""
        self._crop_mode = False
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        # 同步工具栏按钮
        self._btn_toggle_crop.blockSignals(True)
        self._btn_toggle_crop.setChecked(False)
        self._btn_toggle_crop.blockSignals(False)
        self._crop_overlay.hide()
        self._crop_hint.hide()
        self._crop_btn_bar.hide()
        if apply and not self._source.isNull():
            rect = self._crop_overlay.selection_rect()
            if rect.width() > 4 and rect.height() > 4:
                self._do_crop(rect)

    def cancel_crop(self):
        """取消裁剪并退出裁剪模式"""
        self.exit_crop_mode(apply=False)
        self.cropCancelled.emit()

    def apply_crop(self):
        """确认裁剪"""
        self.exit_crop_mode(apply=True)
        self.cropConfirmed.emit()

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

        # 未编辑过的图：按显示比例映射到全尺寸图，全分辨率裁剪，保住细节
        if self._full_path is not None:
            reader = QImageReader(self._full_path)
            reader.setAutoTransform(True)
            img = reader.read()
            if not img.isNull():
                full = QPixmap.fromImage(img)
                # 全尺寸图先旋转到与显示一致的方向，再按比例裁剪
                full_display = full
                if self._rotation:
                    t = QTransform().rotate(self._rotation)
                    full_display = full.transformed(
                        t, Qt.TransformationMode.SmoothTransformation
                    )
                sx = full_display.width() / display.width()
                sy = full_display.height() / display.height()
                full_rect = QRect(
                    int(img_rect.x() * sx),
                    int(img_rect.y() * sy),
                    max(1, int(img_rect.width() * sx)),
                    max(1, int(img_rect.height() * sy)),
                ).intersected(full_display.rect())
                if full_rect.width() >= 2 and full_rect.height() >= 2:
                    cropped = full_display.copy(full_rect)
                    # 反向旋转回原始方向，重建 _source
                    if self._rotation:
                        t2 = QTransform().rotate(-self._rotation)
                        cropped = cropped.transformed(
                            t2, Qt.TransformationMode.SmoothTransformation
                        )
                    self._source = cropped
                    self._rotation = 0
                    self._full_path = None
                    self._zoom = None
                    self._set_modified(True)
                    self._refresh()
                    return
            # 全尺寸解码失败：回退到显示图裁剪
            self._full_path = None

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

        self._full_path = None
        self._zoom = None
        self._set_modified(True)
        self._refresh()

    # ── 底部工具栏事件 ──

    def _on_toggle_crop(self, checked):
        self.toggleCropRequested.emit()

    def _emit_save(self):
        self.saveRequested.emit()

    # ── 裁剪模式鼠标事件 ──
    # 由 _CropOverlay 覆盖层全权处理，ImagePanel 不再拦截
