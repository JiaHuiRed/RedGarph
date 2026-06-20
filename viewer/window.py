#author Red
#260620 Red&小宋 RedGarph V0.0.1 — 主窗口（左侧缩略图 + 右侧大图）

from pathlib import Path

from PyQt6.QtCore import Qt, QPoint, QRect, pyqtSignal
from PyQt6.QtGui import (
    QAction, QMouseEvent, QDragEnterEvent, QDropEvent, QPainter, QColor,
    QCursor,
)
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QMenu, QApplication,
    QMessageBox, QSplitter,
)

from .constants import (
    APP_NAME, APP_VERSION, WINDOW_WIDTH, WINDOW_HEIGHT, THUMB_PANEL_WIDTH,
)
from .theme import apply_theme, THEMES, THEME_LABELS
from .image_panel import ImagePanel
from .thumb_bar import ThumbBar
from .info_bar import InfoBar
from .file_list import FileList
from .slideshow import Slideshow
from .exif_panel import ExifPanel

RESIZE_MARGIN = 6
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

    def __init__(self, title: str = "RedGarph", parent=None):
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


# ═══════════════════════════════════════════
# ── 主窗口 ──
# ═══════════════════════════════════════════

class MainWindow(QMainWindow):
    """图片查看器：无框窗口 + 左侧缩略图面板 + 右侧大图"""

    def __init__(self, theme: str = "night"):
        super().__init__()

        self._theme = theme
        self._current_path: Path | None = None

        # ── 无框窗口 ──
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setMinimumSize(600, 400)
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setAcceptDrops(True)
        self.setMouseTracking(True)

        # 缩放状态
        self._resizing = False
        self._resize_dir: set[str] = set()
        self._drag_pos: QPoint | None = None
        self._start_geo: QRect | None = None

        apply_theme(self._theme)

        # ── 组件 ──
        self.file_list = FileList(self)
        self.slideshow = Slideshow(self)
        self.image_panel = ImagePanel()
        self.thumb_bar = ThumbBar()
        self.info_bar = InfoBar()
        self.exif_panel = ExifPanel()

        # 缩略图面板默认可见
        self._thumb_visible = True

        self._build_titlebar()
        self._build_ui()
        self._connect_signals()

    # ── 构建 UI ──

    def _build_titlebar(self):
        """构建 macOS 风格标题栏 + 菜单"""
        self.titlebar = TitleBar("RedGarph")
        self.titlebar.close_clicked.connect(self.close)
        self.titlebar.minimize_clicked.connect(self.showMinimized)
        self.titlebar.maximize_clicked.connect(self._toggle_maximize)

        # ── 菜单按钮 ──
        menu_btn = QPushButton("☰")
        menu_btn.setObjectName("MenuButton")
        menu_btn.setFixedSize(28, 22)
        menu_btn.setCursor(Qt.CursorShape.ArrowCursor)
        menu_btn.setFlat(True)

        menu = QMenu(menu_btn)

        # 文件
        act_open = QAction("打开文件夹...", self)
        act_open.setShortcut("Ctrl+O")
        act_open.triggered.connect(self._open_folder)
        menu.addAction(act_open)

        menu.addSeparator()

        # 幻灯片
        self._act_slideshow = QAction("幻灯片播放", self)
        self._act_slideshow.setShortcut("Space")
        self._act_slideshow.setCheckable(True)
        self._act_slideshow.triggered.connect(self._toggle_slideshow)
        menu.addAction(self._act_slideshow)

        menu.addSeparator()

        # 缩略图面板
        self._act_thumb = QAction("缩略图面板", self)
        self._act_thumb.setShortcut("Ctrl+B")
        self._act_thumb.setCheckable(True)
        self._act_thumb.setChecked(True)
        self._act_thumb.triggered.connect(self._toggle_thumb_panel)
        menu.addAction(self._act_thumb)

        # EXIF 信息面板
        self._act_exif = QAction("EXIF 信息", self)
        self._act_exif.setShortcut("Ctrl+E")
        self._act_exif.setCheckable(True)
        self._act_exif.triggered.connect(self._toggle_exif)
        menu.addAction(self._act_exif)

        # 显示信息
        self._act_info = QAction("显示信息", self)
        self._act_info.setShortcut("I")
        self._act_info.setCheckable(True)
        self._act_info.triggered.connect(self._toggle_info)
        menu.addAction(self._act_info)

        menu.addSeparator()

        # 裁剪模式
        self._act_crop = QAction("裁剪模式", self)
        self._act_crop.setShortcut("Ctrl+Shift+C")
        self._act_crop.setCheckable(True)
        self._act_crop.triggered.connect(self._toggle_crop)
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
        act_quit.setShortcut("Ctrl+Q")
        act_quit.triggered.connect(self.close)
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

        # ── 水平分割 ──
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setObjectName("MainSplitter")
        splitter.setHandleWidth(1)
        splitter.setChildrenCollapsible(False)

        # 左：缩略图面板 | 中：图片区域 | 右：EXIF 面板
        image_area = QWidget()
        image_area.setObjectName("ImageArea")
        image_layout = QVBoxLayout(image_area)
        image_layout.setContentsMargins(0, 0, 0, 0)
        image_layout.setSpacing(0)
        image_layout.addWidget(self.image_panel, 1)

        # 信息栏覆盖在图片区域底部
        self.info_bar.setParent(self.image_panel)

        splitter.addWidget(self.thumb_bar)
        splitter.addWidget(image_area)
        splitter.addWidget(self.exif_panel)

        # 设置初始分割比例
        splitter.setSizes([
            THUMB_PANEL_WIDTH,
            WINDOW_WIDTH - THUMB_PANEL_WIDTH - ExifPanel.PANEL_WIDTH,
            ExifPanel.PANEL_WIDTH,
        ])
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)
        splitter.setCollapsible(2, False)

        root.addWidget(splitter, 1)

    def _connect_signals(self):
        """连接组件信号"""
        self.file_list.currentChanged.connect(self._on_index_changed)
        self.file_list.filesChanged.connect(self._on_files_changed)
        self.thumb_bar.thumbnailClicked.connect(self.file_list.go_to)
        self.slideshow.nextRequested.connect(self._slideshow_next)

    # ── 文件操作 ──

    def _open_folder(self):
        """选择文件夹并加载图片"""
        d = QFileDialog.getExistingDirectory(
            self, "选择图片文件夹", "",
            QFileDialog.Option.DontUseNativeDialog,
        )
        if not d:
            return
        if self.file_list.load_directory(d):
            self._update_ui()
        else:
            QMessageBox.information(self, "提示", "文件夹中没有找到图片")

    def load_path(self, path: str | Path):
        """从外部路径加载（拖拽或命令行）"""
        p = Path(path)
        if p.is_dir():
            self.file_list.load_directory(p)
            self._update_ui()
        elif p.is_file() and p.suffix.lower() in {
            ".png", ".jpg", ".jpeg", ".bmp", ".gif",
            ".tif", ".tiff", ".webp", ".ico", ".svg",
        }:
            self.file_list.load_directory(p.parent)
            idx = next(
                (i for i, f in enumerate(self.file_list.files) if f == p),
                -1,
            )
            if idx >= 0:
                self.file_list.go_to(idx)
            self._update_ui()

    # ── UI 更新 ──

    def _update_ui(self):
        """文件列表变化时更新界面"""
        files = self.file_list.files
        idx = self.file_list.index

        if files and idx >= 0:
            self.thumb_bar.set_files(files, idx)
            self.thumb_bar.setVisible(self._thumb_visible)
            self._act_thumb.setChecked(self._thumb_visible)
            self._load_current()
        else:
            self.thumb_bar.clear()
            self.image_panel.load_image("")
            self._current_path = None
            self.titlebar.set_title("RedGarph")

    def _load_current(self):
        """加载当前索引的图片"""
        path = self.file_list.current
        if not path:
            return
        self._current_path = path
        self.image_panel.load_image(str(path))
        self.titlebar.set_title(f"RedGarph — {path.name}")

        # 更新信息栏
        self.info_bar.show_info(path, self.image_panel._source)
        self.info_bar.show_page(self.file_list.index, self.file_list.count)
        self._position_info_bar()

        # 更新 EXIF 面板（如果可见）
        if self.exif_panel.isVisible():
            self.exif_panel.set_image(str(path))

    def _on_index_changed(self, index: int):
        if index >= 0:
            self._load_current()
            self.thumb_bar.set_current(index)

    def _on_files_changed(self):
        self._update_ui()

    # ── 缩略图面板 ──

    def _toggle_thumb_panel(self):
        self._thumb_visible = not self._thumb_visible
        self.thumb_bar.setVisible(self._thumb_visible)
        self._act_thumb.setChecked(self._thumb_visible)

    # ── 幻灯片 ──

    def _toggle_slideshow(self):
        self.slideshow.toggle()
        self._act_slideshow.setChecked(self.slideshow.is_active)

    def _slideshow_next(self):
        if self.file_list.can_next():
            self.file_list.next_image()
        else:
            self.file_list.go_to(0)

    # ── EXIF 面板 ──

    def _toggle_exif(self):
        self.exif_panel.toggle()
        self._act_exif.setChecked(self.exif_panel.isVisible())
        # 切换时刷新当前图片的 EXIF
        if self.exif_panel.isVisible() and self._current_path:
            self.exif_panel.set_image(str(self._current_path))

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
        self._act_info.setChecked(self.info_bar.isVisible())

    def _position_info_bar(self):
        """信息栏在图片区域底部居中"""
        if self.info_bar.isVisible():
            pw = self.image_panel.width()
            ph = self.image_panel.height()
            ih = self.info_bar.sizeHint().height()
            iw = min(pw - 40, 600)
            x = (pw - iw) // 2
            y = ph - ih - 20
            self.info_bar.setGeometry(x if x >= 0 else 0, y if y >= 0 else 0, iw, ih)

    # ── 主题 ──

    def _switch_theme(self, name: str):
        if name == self._theme:
            return
        self._theme = name
        apply_theme(name)
        for n, act in self._theme_actions.items():
            act.setChecked(n == name)

    # ── 关于 ──

    def _show_about(self):
        QMessageBox.about(
            self, "关于 RedGarph",
            f"<b>RedGarph</b> V{APP_VERSION}<br><br>"
            "本地图片查看器<br>"
            "PyQt6 驱动 · macOS 风格界面<br>"
            "左侧缩略图面板 · 缩放/旋转/全屏<br><br>"
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

    # ── 鼠标事件（窗口缩放） ──

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            d = self._get_resize_dir(event.pos())
            if d:
                self._resizing = True
                self._resize_dir = d
                self._drag_pos = event.globalPosition().toPoint()
                self._start_geo = QRect(self.geometry())
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._resizing and self._resize_dir and self._drag_pos and self._start_geo:
            delta = event.globalPosition().toPoint() - self._drag_pos
            geo = QRect(self._start_geo)
            if "left" in self._resize_dir:
                geo.setLeft(geo.left() + delta.x())
            if "right" in self._resize_dir:
                geo.setRight(geo.right() + delta.x())
            if "top" in self._resize_dir:
                geo.setTop(geo.top() + delta.y())
            if "bottom" in self._resize_dir:
                geo.setBottom(geo.bottom() + delta.y())
            if geo.width() >= self.minimumWidth() and geo.height() >= self.minimumHeight():
                self.setGeometry(geo)
            event.accept()
            return
        self._update_cursor(event.pos())
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._resizing:
            self._resizing = False
            self._resize_dir = set()
            self._drag_pos = None
            self._start_geo = None
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def changeEvent(self, event):
        super().changeEvent(event)
        if event and event.type() == event.Type.WindowStateChange:
            m = 0 if self.isMaximized() else 1
            central = self.centralWidget()
            if central:
                central.layout().setContentsMargins(m, 0, m, m)
            self._update_cursor(self.mapFromGlobal(QCursor.pos()))

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

        # Ctrl+O 打开文件夹
        if key == Qt.Key.Key_O and mod == Qt.KeyboardModifier.ControlModifier:
            self._open_folder()
        # Ctrl+Q 退出
        elif key == Qt.Key.Key_Q and mod == Qt.KeyboardModifier.ControlModifier:
            self.close()
        # Ctrl+B 切换缩略图面板
        elif key == Qt.Key.Key_B and mod == Qt.KeyboardModifier.ControlModifier:
            self._toggle_thumb_panel()
        # Space 幻灯播放
        elif key == Qt.Key.Key_Space:
            self._toggle_slideshow()
        # Esc 退出裁剪 / 幻灯片 / 全屏
        elif key == Qt.Key.Key_Escape:
            if self.image_panel.is_crop_mode:
                self.image_panel.cancel_crop()
                self._act_crop.setChecked(False)
            elif self.isFullScreen():
                self.showNormal()
                self.titlebar.setVisible(True)
                self.thumb_bar.setVisible(self._thumb_visible)
            if self.slideshow.is_active:
                self.slideshow.stop()
                self._act_slideshow.setChecked(False)
        # F / F11 全屏
        elif key in (Qt.Key.Key_F, Qt.Key.Key_F11):
            if self.isFullScreen():
                self.showNormal()
                self.titlebar.setVisible(True)
                self.thumb_bar.setVisible(self._thumb_visible)
            else:
                self.showFullScreen()
                self.titlebar.setVisible(False)
                self.thumb_bar.setVisible(False)
        # ← 上一张
        elif key == Qt.Key.Key_Left:
            self._stop_slideshow()
            self.file_list.prev_image()
        # → 下一张
        elif key == Qt.Key.Key_Right:
            self._stop_slideshow()
            self.file_list.next_image()
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
        # I 切换信息栏
        elif key == Qt.Key.Key_I and mod == Qt.KeyboardModifier.NoModifier:
            self._toggle_info()
        # + 放大
        elif key in (Qt.Key.Key_Plus, Qt.Key.Key_Equal):
            self.image_panel.zoom_in()
        # - 缩小
        elif key == Qt.Key.Key_Minus:
            self.image_panel.zoom_out()
        # Ctrl+E EXIF 面板
        elif key == Qt.Key.Key_E and mod == Qt.KeyboardModifier.ControlModifier:
            self._toggle_exif()
        # Ctrl+Shift+C 裁剪模式
        elif key == Qt.Key.Key_C and mod == (
            Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier
        ):
            self._toggle_crop()
        # Enter 确认裁剪
        elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if self.image_panel.is_crop_mode:
                self.image_panel.apply_crop()
                self._act_crop.setChecked(False)
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
