#author Red

#260620 Red&小宋 RedGarph V0.0.1 — 主窗口（图片 + EXIF 信息面板）

import ctypes
import ctypes.wintypes  # 确保 PyInstaller 打包时包含该模块
import os
import subprocess
import tempfile

from pathlib import Path

from PIL import Image as PILImage

from PyQt6.QtCore import Qt, QPoint, QRect, pyqtSignal, QEvent, QTimer

from PyQt6.QtGui import (
    QAction, QMouseEvent, QDragEnterEvent, QDropEvent, QPainter, QColor,
    QCursor, QRegion,
)

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QMenu, QApplication,
    QMessageBox, QSplitter, QInputDialog,
)

from .title_bar import TitleBar, TITLEBAR_HEIGHT
from .constants import (
    APP_NAME, APP_VERSION, WINDOW_WIDTH, WINDOW_HEIGHT, IMAGE_EXTENSIONS,
    SLIDESHOW_INTERVAL,
)
from .theme import apply_theme, THEMES, THEME_LABELS
from .image_panel import ImagePanel
from .info_bar import InfoBar
from .file_list import FileList
from .slideshow import Slideshow
from .exif_panel import ExifPanel

RESIZE_MARGIN = 6

# ═══════════════════════════════════════════
# ── 边缘缩放遮罩 ──
# ═══════════════════════════════════════════
# ── 边缘缩放遮罩 ──
# ═══════════════════════════════════════════
# ═══════════════════════════════════════════

class _EdgeOverlay(QWidget):
    """透明遮罩层：只保留边缘 MARGIN 环响应鼠标，中间区域透传事件"""
    _MARGIN = 8
    _MIN_W  = 600
    _MIN_H  = 400
    _CURSORS = {
        'tl': Qt.CursorShape.SizeFDiagCursor, 'tr': Qt.CursorShape.SizeBDiagCursor,
        'bl': Qt.CursorShape.SizeBDiagCursor, 'br': Qt.CursorShape.SizeFDiagCursor,
        'l':  Qt.CursorShape.SizeHorCursor,   'r':  Qt.CursorShape.SizeHorCursor,
        't':  Qt.CursorShape.SizeVerCursor,   'b':  Qt.CursorShape.SizeVerCursor,
    }

    def __init__(self, parent, window):
        super().__init__(parent)
        self._window    = window
        self._resizing  = False
        self._edge      = None
        self._start_pos = None
        self._start_geo = None
        self.setMouseTracking(True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)

    def _update_mask(self):
        w, h = self.width(), self.height()
        m    = self._MARGIN
        full = QRegion(0, 0, w, h)
        inner = QRegion(m, m, w - 2 * m, h - 2 * m)
        self.setMask(full.subtracted(inner))

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._update_mask()

    def _edge_at(self, pos):
        w, h = self.width(), self.height()
        m = self._MARGIN
        x, y = int(pos.x()), int(pos.y())
        on_l = x <= m; on_r = x >= w - m - 1
        on_t = y <= m; on_b = y >= h - m - 1
        if on_t and on_l: return 'tl'
        if on_t and on_r: return 'tr'
        if on_b and on_l: return 'bl'
        if on_b and on_r: return 'br'
        if on_l: return 'l'
        if on_r: return 'r'
        if on_t: return 't'
        if on_b: return 'b'
        return None

    def mouseMoveEvent(self, e):
        if self._resizing and self._edge:
            dx = e.globalPosition().x() - self._start_pos.x()
            dy = e.globalPosition().y() - self._start_pos.y()
            rx, ry, rw, rh = self._start_geo
            edge = self._edge
            if 'l' in edge: rx += dx; rw -= dx
            if 'r' in edge: rw += dx
            if 't' in edge: ry += dy; rh -= dy
            if 'b' in edge: rh += dy
            if rw < self._MIN_W:
                if 'l' in edge: rx -= (self._MIN_W - rw)
                rw = self._MIN_W
            if rh < self._MIN_H:
                if 't' in edge: ry -= (self._MIN_H - rh)
                rh = self._MIN_H
            self._window.setGeometry(int(rx), int(ry), int(rw), int(rh))
            return
        edge = self._edge_at(e.position())
        self.setCursor(self._CURSORS.get(edge, Qt.CursorShape.ArrowCursor))

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            edge = self._edge_at(e.position())
            if edge:
                self._resizing  = True
                self._edge      = edge
                self._start_pos = e.globalPosition().toPoint()
                self._start_geo = (self._window.x(), self._window.y(),
                                   self._window.width(), self._window.height())
                return
        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        if self._resizing:
            self._resizing  = False
            self._edge      = None
            self._start_pos = None
            self._start_geo = None
            return
        super().mouseReleaseEvent(e)

# ═══════════════════════════════════════════
# ── 主窗口 ──
# ═══════════════════════════════════════════

class MainWindow(QMainWindow):

    """图片查看器：无框窗口 + 图片区域 + EXIF 信息面板"""

    def __init__(self, theme: str = "night"):

        super().__init__()

        self._theme = theme

        self._current_path: Path | None = None
        self._exif_generation = 0
        self._shortcut_actions: list[QAction] = []
        self._pending_folder_dialog: Path | None = None

        # ── 无框窗口 ──

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        self.setMinimumSize(600, 400)

        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)

        self.setAcceptDrops(True)

        self.setMouseTracking(True)

        apply_theme(self._theme)

        # ── 组件 ──

        self.file_list = FileList(self)

        self.slideshow = Slideshow(self)

        self._slideshow_interval = SLIDESHOW_INTERVAL

        self._fullscreen_hover_timer = QTimer(self)

        self._fullscreen_hover_timer.setInterval(100)

        self._fullscreen_hover_timer.timeout.connect(self._check_fullscreen_hover)

        self.image_panel = ImagePanel()

        self.info_bar = InfoBar()

        self.exif_panel = ExifPanel()

        self._build_titlebar()

        self._build_ui()

        self._connect_signals()
        self._install_navigation_shortcuts()

    def _register_shortcut(self, action: QAction, sequence: str):
        """让菜单动作在应用内始终生效，即使焦点位于图片子控件。"""
        action.setShortcut(sequence)
        action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        self.addAction(action)

    def _add_shortcut(self, sequence: str, callback):
        action = QAction(self)
        action.setShortcut(sequence)
        action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        action.triggered.connect(callback)
        self.addAction(action)
        self._shortcut_actions.append(action)

    def _install_navigation_shortcuts(self):
        self._add_shortcut("Left", self._previous_image)
        self._add_shortcut("Right", self._next_image)
        self._add_shortcut("R", self.image_panel.rotate_right)
        self._add_shortcut("Shift+R", self.image_panel.rotate_left)
        self._add_shortcut("F", self._toggle_fullscreen)
        self._add_shortcut("F11", self._toggle_fullscreen)
        self._add_shortcut("Ctrl+0", self.image_panel.fit_to_window)
        self._add_shortcut("Ctrl+1", self.image_panel.actual_size)

    def _previous_image(self):
        self._stop_slideshow()
        self.file_list.prev_image()

    def _next_image(self):
        self._stop_slideshow()
        self.file_list.next_image()

    def _toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
            self.titlebar.setVisible(True)
        else:
            self.showFullScreen()
            self.titlebar.setVisible(False)



    # ── 构建 UI ──

    def _build_titlebar(self):

        """构建 macOS 风格标题栏 + 菜单"""

        self.titlebar = TitleBar("RedGarph", version=APP_VERSION, parent=self)

        self.titlebar.close_clicked.connect(self.close)

        self.titlebar.minimize_clicked.connect(self.showMinimized)

        self.titlebar.maximize_clicked.connect(self._toggle_maximize)

        # ── 菜单按钮 ──

        menu_btn = QPushButton("☰")

        menu_btn.setObjectName("MenuButton")

        menu_btn.setFixedSize(32, 26)

        menu_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        menu_btn.setFlat(True)

        menu = QMenu(menu_btn)

        # 文件

        act_open = QAction("打开文件夹...", self)
        act_open.triggered.connect(self._open_folder)
        self._register_shortcut(act_open, "Ctrl+O")
        menu.addAction(act_open)

        menu.addSeparator()

        # 保存

        act_save = QAction("保存", self)
        act_save.triggered.connect(self._save_image)
        self._register_shortcut(act_save, "Ctrl+S")
        menu.addAction(act_save)

        act_save_as = QAction("另存为...", self)
        act_save_as.triggered.connect(self._save_image_as)
        self._register_shortcut(act_save_as, "Ctrl+Shift+S")
        menu.addAction(act_save_as)

        menu.addSeparator()

        # 复制

        act_copy = QAction("复制图片", self)
        act_copy.triggered.connect(self._copy_to_clipboard)
        self._register_shortcut(act_copy, "Ctrl+C")
        menu.addAction(act_copy)

        menu.addSeparator()

        # 文件操作

        act_show = QAction("在资源管理器中显示", self)
        act_show.triggered.connect(self._show_in_explorer)
        self._register_shortcut(act_show, "Ctrl+Shift+E")
        menu.addAction(act_show)

        act_delete = QAction("删除到回收站", self)
        act_delete.triggered.connect(self._delete_current)
        self._register_shortcut(act_delete, "Delete")
        menu.addAction(act_delete)

        menu.addSeparator()

        # 幻灯片

        self._act_slideshow = QAction("幻灯片播放", self)
        self._act_slideshow.setCheckable(True)
        self._act_slideshow.triggered.connect(self._toggle_slideshow)
        self._register_shortcut(self._act_slideshow, "Space")
        menu.addAction(self._act_slideshow)

        act_slideshow_interval = QAction("间隔调节...", self)
        act_slideshow_interval.triggered.connect(self._adjust_slideshow_interval)
        menu.addAction(act_slideshow_interval)

        menu.addSeparator()

        # EXIF 信息面板

        self._act_exif = QAction("EXIF 信息", self)
        self._act_exif.setCheckable(True)
        self._act_exif.setChecked(True)
        self._act_exif.triggered.connect(self._toggle_exif)
        self._register_shortcut(self._act_exif, "Ctrl+E")
        menu.addAction(self._act_exif)

        # 显示信息

        self._act_info = QAction("显示信息", self)
        self._act_info.setCheckable(True)
        self._act_info.triggered.connect(self._toggle_info)
        self._register_shortcut(self._act_info, "I")
        menu.addAction(self._act_info)

        menu.addSeparator()

        # 裁剪模式

        self._act_crop = QAction("裁剪模式", self)
        self._act_crop.setCheckable(True)
        self._act_crop.triggered.connect(self._toggle_crop)
        self._register_shortcut(self._act_crop, "Ctrl+Shift+C")
        menu.addAction(self._act_crop)

        menu.addSeparator()

        # 主题

        theme_menu = menu.addMenu("主题")

        self._theme_actions: dict[str, QAction] = {}

        for name in THEMES:

            act = QAction(THEME_LABELS[name], self)

            act.setCheckable(True)

            act.setChecked(name == self._theme)

            act.triggered.connect(lambda _, n=name: self._switch_theme(n))

            theme_menu.addAction(act)

            self._theme_actions[name] = act

        menu.addSeparator()

        act_about = QAction("关于 RedGarph", self)

        act_about.triggered.connect(self._show_about)

        menu.addAction(act_about)

        menu.addSeparator()

        act_quit = QAction("退出", self)
        act_quit.triggered.connect(self.close)
        self._register_shortcut(act_quit, "Ctrl+Q")
        menu.addAction(act_quit)

        menu_btn.setMenu(menu)

        menu_btn.clicked.connect(

            lambda: menu.exec(menu_btn.mapToGlobal(

                menu_btn.rect().bottomLeft()

            ))

        )

        self.titlebar.layout().addWidget(menu_btn)

    def _build_ui(self):

        """构建主布局：水平分割 = [缩略图面板 | 图片区域]"""

        central = QWidget()

        self.setCentralWidget(central)

        root = QVBoxLayout(central)

        root.setContentsMargins(1, 0, 1, 1)

        root.setSpacing(0)

        root.addWidget(self.titlebar)

        # ── 水平分割：图片区域 | EXIF 面板 ──

        splitter = QSplitter(Qt.Orientation.Horizontal)

        splitter.setObjectName("MainSplitter")

        splitter.setHandleWidth(1)

        splitter.setChildrenCollapsible(False)

        # 图片区域

        image_area = QWidget()

        image_area.setObjectName("ImageArea")

        image_layout = QVBoxLayout(image_area)

        image_layout.setContentsMargins(0, 0, 0, 0)

        image_layout.setSpacing(0)

        image_layout.addWidget(self.image_panel, 1)

        # 信息栏覆盖在图片区域底部

        self.info_bar.setParent(self.image_panel)

        splitter.addWidget(image_area)

        splitter.addWidget(self.exif_panel)

        splitter.setSizes([

            WINDOW_WIDTH - ExifPanel.PANEL_WIDTH,

            ExifPanel.PANEL_WIDTH,

        ])
        splitter.setCollapsible(0, False)

        splitter.setCollapsible(1, False)

        root.addWidget(splitter, 1)

        # 边缘缩放遮罩（独立悬浮层，不占 layout 空间）

        self._edge_overlay = _EdgeOverlay(self, self)
        self._edge_overlay.setGeometry(self.centralWidget().geometry())
        self._edge_overlay.show()
        self._edge_overlay.raise_()

    def _connect_signals(self):

        """连接组件信号"""

        self.file_list.currentChanged.connect(self._on_index_changed)
        self.file_list.directoryLoadFinished.connect(self._on_directory_load_finished)

        self.slideshow.nextRequested.connect(self._slideshow_next)

        self.slideshow.intervalChanged.connect(self._on_slideshow_interval_changed)

        self.image_panel.cropConfirmed.connect(lambda: self._act_crop.setChecked(False))

        self.image_panel.cropCancelled.connect(lambda: self._act_crop.setChecked(False))

        self.image_panel.toggleCropRequested.connect(self._toggle_crop)

        self.image_panel.saveRequested.connect(self._save_image)
        self.image_panel.imageLoadFinished.connect(self._on_image_load_finished)

    def _on_slideshow_interval_changed(self, sec: int):

        self._slideshow_interval = sec

        self.info_bar.show_info(
            self._current_path, self.image_panel.source, extra=f"幻灯片间隔：{sec}s",
            dimensions=self.image_panel.image_size,
        )

    # ── 文件操作 ──

    def _open_folder(self):

        """选择文件夹并加载图片"""

        d = QFileDialog.getExistingDirectory(
            self, "选择图片文件夹", "",
        )

        if not d:

            return

        self._pending_folder_dialog = Path(d)
        self.file_list.load_directory_async(d)

    def _on_directory_load_finished(self, path: Path, has_images: bool):
        if self._pending_folder_dialog != path:
            return
        self._pending_folder_dialog = None
        if not has_images:
            QMessageBox.information(self, "提示", "文件夹中没有找到图片")

    def load_path(self, path: str | Path):

        """从外部路径加载（拖拽或命令行）"""

        p = Path(path)
        self._pending_folder_dialog = None

        if p.is_dir():

            self.file_list.load_directory_async(p)

        elif p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS:

            self.file_list.load_directory_async(p.parent, selected=p)


    # ── UI 更新 ──

    def _update_ui(self):

        """文件列表变化时更新界面"""

        files = self.file_list.files

        idx = self.file_list.index

        if files and idx >= 0:

            self._load_current()

        else:

            self.image_panel.load_image("")

            self._current_path = None

            self.titlebar.set_title("RedGarph")

            self.info_bar.show_info(None)
            self.exif_panel.clear_exif()
            self._exif_generation += 1

    def _load_current(self):
        """异步加载当前索引的图片"""
        path = self.file_list.current
        if not path:
            return
        self._current_path = path
        self._exif_generation += 1
        self.titlebar.set_title(f"RedGarph — {path.name}")
        self.info_bar.show_info(None, extra="加载中...")
        self.exif_panel.clear_exif()
        self.image_panel.load_image_async(str(path))

    def _on_image_load_finished(self, path_str: str, success: bool):
        path = Path(path_str)
        if self._current_path != path or self.file_list.current != path:
            return
        if not success:
            self.info_bar.show_info(None, extra="无法加载图片")
            self.exif_panel.clear_exif()
            return

        self.titlebar.set_title(f"RedGarph — {path.name}")
        self.info_bar.show_info(
            path,
            self.image_panel.source,
            extra=f"幻灯片间隔：{self._slideshow_interval}s",
            dimensions=self.image_panel.image_size,
        )
        self.info_bar.show_page(self.file_list.index, self.file_list.count)
        self._position_info_bar()
        if not self.exif_panel.isHidden():
            self._queue_exif(path)
    def _queue_exif(self, path: Path):
        """延迟读取 EXIF，并丢弃已经过期的请求。"""
        self._exif_generation += 1
        generation = self._exif_generation
        QTimer.singleShot(
            0,
            lambda p=path, g=generation: self._load_exif_if_current(p, g),
        )

    def _load_exif_if_current(self, path: Path, generation: int):
        if (
            generation != self._exif_generation
            or self.exif_panel.isHidden()
            or self._current_path != path
        ):
            return
        self.exif_panel.set_image_async(str(path))

    def _on_index_changed(self, index: int):
        self._update_ui()

    # ── 幻灯片 ──

    def _toggle_slideshow(self):

        self.slideshow.toggle()

        self._act_slideshow.setChecked(self.slideshow.is_active)

    def _adjust_slideshow_interval(self):

        sec, ok = QInputDialog.getInt(
            self,
            "幻灯片间隔",
            "间隔秒数（1-60）：",
            self._slideshow_interval,
            1,
            60,
        )

        if ok:
            self.slideshow.interval = sec

    def _slideshow_next(self):

        if self.file_list.can_next():

            self.file_list.next_image()

        else:

            self.file_list.go_to(0)

    # ── EXIF 面板 ──

    def _toggle_exif(self):

        self.exif_panel.toggle()

        is_enabled = not self.exif_panel.isHidden()
        self._act_exif.setChecked(is_enabled)

        # 切换时刷新当前图片的 EXIF

        if is_enabled and self._current_path:
            self._queue_exif(self._current_path)
        else:
            self._exif_generation += 1

    # ── 裁剪模式 ──

    def _toggle_crop(self):

        if self.image_panel.is_crop_mode:

            self.image_panel.exit_crop_mode(apply=False)

            self._act_crop.setChecked(False)

        else:

            self.image_panel.enter_crop_mode()

            self._act_crop.setChecked(True)

    # ── 信息栏 ──

    def _toggle_info(self):

        self.info_bar.toggle()

        self._act_info.setChecked(not self.info_bar.isHidden())

    def _position_info_bar(self):

        """信息栏在图片区域底部居中"""

        if self.info_bar.isVisible():

            pw = self.image_panel.width()

            ph = self.image_panel.height()

            ih = self.info_bar.sizeHint().height()

            iw = min(pw - 40, 600)

            x = max(0, (pw - iw) // 2)

            y = max(0, ph - ih - 20)

            self.info_bar.setGeometry(x, y, iw, ih)

    # ── 主题 ──

    def _switch_theme(self, name: str):

        if name == self._theme:

            return

        self._theme = name

        apply_theme(name)

        for n, act in self._theme_actions.items():

            act.setChecked(n == name)

    # ── 保存 / 另存为 ──

    _EXT_FMT = {

        ".jpg": "JPEG", ".jpeg": "JPEG",

        ".png": "PNG", ".bmp": "BMP",

        ".webp": "WEBP", ".tif": "TIFF", ".tiff": "TIFF", ".ico": "ICO",

    }

    @staticmethod
    def _preserve_exif(source: Path, encoded: Path, fmt: str):
        """尽量复制 EXIF；显示图像已应用方向，因此将方向标记归一化。"""
        if fmt not in {"JPEG", "PNG", "TIFF", "WEBP"}:
            return
        try:
            with PILImage.open(source) as source_image:
                exif = source_image.getexif()
                if not exif:
                    return
                source_info = dict(source_image.info)

            exif[274] = 1
            fd, metadata_name = tempfile.mkstemp(
                prefix=f".{encoded.stem}-metadata-",
                suffix=encoded.suffix,
                dir=str(encoded.parent),
            )
            os.close(fd)
            metadata_path = Path(metadata_name)
            try:
                with PILImage.open(encoded) as output_image:
                    save_kwargs = {"exif": exif.tobytes()}
                    for key in ("icc_profile", "dpi"):
                        if key in source_info:
                            save_kwargs[key] = source_info[key]
                    output_image.save(metadata_path, format=fmt, **save_kwargs)
                os.replace(metadata_path, encoded)
            finally:
                metadata_path.unlink(missing_ok=True)
        except Exception:
            # 元数据不支持或源文件不是 Pillow 可读格式时，不影响图像本身保存。
            return

    @classmethod
    def _save_pixmap_atomic(
        cls,
        pix,
        target: Path,
        fmt: str,
        source: Path | None = None,
    ) -> bool:
        """先写同目录临时文件，再替换目标，避免半写文件破坏原图。"""
        try:
            fd, temp_name = tempfile.mkstemp(
                prefix=f".{target.stem}-", suffix=target.suffix, dir=str(target.parent)
            )
            os.close(fd)
            temp_path = Path(temp_name)
            try:
                quality = 95 if fmt == "JPEG" else -1
                if not pix.save(str(temp_path), fmt, quality):
                    return False
                if source is not None and source.exists():
                    cls._preserve_exif(source, temp_path, fmt)
                os.replace(temp_path, target)
                return True
            finally:
                temp_path.unlink(missing_ok=True)
        except (OSError, ValueError):
            return False

    def _save_image(self):

        """Ctrl+S — 覆盖保存（保留当前旋转/裁剪状态）"""

        if not self._current_path:

            return

        if not self.image_panel.is_dirty:
            return

        pix = self.image_panel.full_res_pixmap()

        if pix.isNull():

            return

        fmt = self._EXT_FMT.get(self._current_path.suffix.lower(), "")
        if not fmt:
            QMessageBox.warning(self, "保存失败", "SVG 图片不支持直接覆盖保存，请使用另存为导出")
            return

        if not self._save_pixmap_atomic(
            pix, self._current_path, fmt, source=self._current_path
        ):

            QMessageBox.warning(self, "保存失败", f"无法写入：{self._current_path.name}")
        else:
            self.image_panel.invalidate_cache(str(self._current_path))
            self._load_current()

    def _save_image_as(self):

        """Ctrl+Shift+S — 另存为"""

        if not self._current_path:

            return

        path, _ = QFileDialog.getSaveFileName(
            self, "另存为", str(self._current_path),
            "图片 (*.png *.jpg *.bmp *.webp *.tiff *.ico);;所有文件 (*)",
        )

        if not path:

            return

        fmt = self._EXT_FMT.get(Path(path).suffix.lower(), "")
        if not fmt:
            QMessageBox.warning(self, "保存失败", "仅支持 PNG、JPEG、BMP、WEBP、TIFF 和 ICO 格式")
            return

        pix = self.image_panel.full_res_pixmap()

        if pix.isNull():
            return

        same_path = False
        try:
            same_path = Path(path).resolve() == self._current_path.resolve()
        except OSError:
            pass

        if not self._save_pixmap_atomic(
            pix, Path(path), fmt, source=self._current_path
        ):

            QMessageBox.warning(self, "保存失败", f"无法写入：{Path(path).name}")
        else:
            self.image_panel.invalidate_cache(path)
            if same_path:
                self._load_current()

    # ── 剪贴板 ──

    def _copy_to_clipboard(self):

        """Ctrl+C — 复制当前图片到剪贴板"""

        if not self.image_panel.has_image:

            return

        QApplication.clipboard().setPixmap(self.image_panel.current_pixmap())

    # ── 资源管理器 ──

    def _show_in_explorer(self):

        """Ctrl+Shift+E — 在资源管理器中选中当前文件"""

        if not self._current_path or not self._current_path.exists():

            return

        subprocess.Popen(["explorer", f"/select,{self._current_path}"])

    # ── 删除到回收站 ──

    def _delete_current(self):
        """Del — 将当前文件移至回收站，自动跳到下一张"""
        if not self._current_path or not self._current_path.exists():
            return
        name = self._current_path.name
        reply = QMessageBox.question(
            self, "删除确认", f'将 "{name}" 移至回收站？',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        path = self._current_path
        if not self._recycle_file(path):
            QMessageBox.warning(self, "删除失败", f"无法移至回收站：{name}")
            return

        self.image_panel.invalidate_cache(str(path))
        self.file_list.remove_current()

    @staticmethod

    def _recycle_file(path: Path) -> bool:

        """Windows Shell API — SHFileOperationW 移至回收站"""

        class _Op(ctypes.Structure):

            _fields_ = [

                ("hwnd",    ctypes.c_void_p),

                ("wFunc",   ctypes.c_uint),

                ("pFrom",   ctypes.c_void_p),

                ("pTo",     ctypes.c_void_p),

                ("fFlags",  ctypes.c_ushort),

                ("fAborted",ctypes.wintypes.BOOL),

                ("hMapping",ctypes.c_void_p),

                ("pTitle",  ctypes.c_void_p),

            ]

        # pFrom 需要双 null 结尾的宽字符串

        buf = ctypes.create_unicode_buffer(str(path) + "\0")

        op = _Op(

            wFunc=3,                        # FO_DELETE

            pFrom=ctypes.addressof(buf),

            fFlags=0x50,                    # FOF_ALLOWUNDO | FOF_NOCONFIRMATION

        )

        return ctypes.windll.shell32.SHFileOperationW(ctypes.byref(op)) == 0

    # ── 关于 ──

    def _show_about(self):

        QMessageBox.about(

            self, "关于 RedGarph",

            f"<b>RedGarph</b> V{APP_VERSION}<br><br>"

            "本地图片查看器<br>"

            "PyQt6 驱动 · macOS 风格界面<br>"

            "缩放/旋转/裁剪 · EXIF 信息<br><br>"

            "作者：Red & 小宋",

        )

    # ── 窗口缩放（无框窗口边缘拖拽） ──

    def _get_resize_dir(self, pos: QPoint) -> set[str]:

        if self.isMaximized() or self.isFullScreen():

            return set()

        r: set[str] = set()

        if pos.x() <= RESIZE_MARGIN:

            r.add("left")

        if pos.x() >= self.width() - RESIZE_MARGIN:

            r.add("right")

        if pos.y() <= RESIZE_MARGIN:

            r.add("top")

        if pos.y() >= self.height() - RESIZE_MARGIN:

            r.add("bottom")

        return r

    def _update_cursor(self, pos: QPoint):

        d = self._get_resize_dir(pos)

        if not d:

            self.setCursor(Qt.CursorShape.ArrowCursor)

        elif d in ({"top", "left"}, {"bottom", "right"}):

            self.setCursor(Qt.CursorShape.SizeFDiagCursor)

        elif d in ({"top", "right"}, {"bottom", "left"}):

            self.setCursor(Qt.CursorShape.SizeBDiagCursor)

        elif "top" in d or "bottom" in d:

            self.setCursor(Qt.CursorShape.SizeVerCursor)

        else:

            self.setCursor(Qt.CursorShape.SizeHorCursor)

    def _toggle_maximize(self):

        if self.isMaximized():

            self.showNormal()

        else:

            self.showMaximized()

    def changeEvent(self, event):

        """进入/退出全屏时统一管理标题栏显隐"""

        if event.type() == event.Type.WindowStateChange:

            if self.isFullScreen():

                self.titlebar.setVisible(False)

                self._fullscreen_hover_timer.start()

            else:

                self.titlebar.setVisible(True)

                self._fullscreen_hover_timer.stop()

        super().changeEvent(event)

    def _check_fullscreen_hover(self):

        """全屏时鼠标移到顶部自动显示标题栏"""

        if not self.isFullScreen():

            self._fullscreen_hover_timer.stop()

            self.titlebar.setVisible(True)

            return

        y = QCursor.pos().y()

        top = self.geometry().top()

        if y <= top + TITLEBAR_HEIGHT:

            self.titlebar.setVisible(True)

        else:

            self.titlebar.setVisible(False)

    # ── 拖拽 ──

    def dragEnterEvent(self, event: QDragEnterEvent | None):

        if event and event.mimeData().hasUrls():

            event.acceptProposedAction()

    def dragMoveEvent(self, event):

        if event and event.mimeData().hasUrls():

            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent | None):

        if event is None:

            return

        urls = [

            u.toLocalFile()

            for u in event.mimeData().urls()

            if u.isLocalFile()

        ]

        if urls:

            self.load_path(urls[0])

    # ── 键盘快捷键 ──

    def keyPressEvent(self, event):

        key = event.key()

        mod = event.modifiers()

        # Esc 退出裁剪 / 幻灯片 / 全屏

        if key == Qt.Key.Key_Escape:

            if self.image_panel.is_crop_mode:

                self.image_panel.cancel_crop()

            if self.isFullScreen():

                self.showNormal()

                self.titlebar.setVisible(True)

            if self.slideshow.is_active:

                self.slideshow.stop()

                self._act_slideshow.setChecked(False)

        # F / F11 全屏

        elif key in (Qt.Key.Key_F, Qt.Key.Key_F11):

            if self.isFullScreen():

                self.showNormal()

                self.titlebar.setVisible(True)

            else:

                self.showFullScreen()

                self.titlebar.setVisible(False)

        # ← 上一张

        elif key == Qt.Key.Key_Left:

            self._stop_slideshow()

            self.file_list.prev_image()

        # → 下一张

        elif key == Qt.Key.Key_Right:

            self._stop_slideshow()

            self.file_list.next_image()

        # [ 减少间隔

        if key == Qt.Key.Key_BracketLeft:

            self.slideshow.interval = max(1, self._slideshow_interval - 1)

        # ] 增加间隔

        elif key == Qt.Key.Key_BracketRight:

            self.slideshow.interval = min(60, self._slideshow_interval + 1)

        # R 顺时针旋转

        elif key == Qt.Key.Key_R and mod == Qt.KeyboardModifier.NoModifier:

            self.image_panel.rotate_right()

        # Shift+R 逆时针旋转

        elif key == Qt.Key.Key_R and mod == Qt.KeyboardModifier.ShiftModifier:

            self.image_panel.rotate_left()

        # Ctrl+0 适应窗口

        elif key == Qt.Key.Key_0 and mod == Qt.KeyboardModifier.ControlModifier:

            self.image_panel.fit_to_window()

        # Ctrl+1 原始尺寸

        elif key == Qt.Key.Key_1 and mod == Qt.KeyboardModifier.ControlModifier:

            self.image_panel.actual_size()

        # + 放大

        elif key in (Qt.Key.Key_Plus, Qt.Key.Key_Equal):

            self.image_panel.zoom_in()

        # - 缩小

        elif key == Qt.Key.Key_Minus:

            self.image_panel.zoom_out()

        # Enter 确认裁剪

        elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):

            if self.image_panel.is_crop_mode:

                self.image_panel.apply_crop()

            else:

                super().keyPressEvent(event)

        else:

            super().keyPressEvent(event)

    def _stop_slideshow(self):

        if self.slideshow.is_active:

            self.slideshow.stop()

            self._act_slideshow.setChecked(False)

    # ── 窗口大小变化 ──

    def resizeEvent(self, event):

        super().resizeEvent(event)

        self._position_info_bar()

        # 同步边缘缩放遮罩位置/大小
        geo = self.centralWidget().geometry()
        self._edge_overlay.setGeometry(geo)

