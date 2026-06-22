#author Red
#260620 Red&小宋 RedGarph V0.0.1 — EXIF 信息面板

"""右侧 EXIF 信息面板 — 读取并展示图片 EXIF 元数据"""

from collections.abc import Callable
from datetime import datetime
from pathlib import Path

from PIL import Image
from PIL.ExifTags import TAGS as EXIF_TAGS

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem,
    QLabel, QHeaderView,
)

from .constants import format_size as _format_size

# ── 枚举映射 ──
_METERING_MODES = {0: "未知", 1: "平均", 2: "中央重点", 3: "点测光", 4: "多点", 5: "矩阵", 6: "局部"}
_LIGHT_SOURCES = {0: "未知", 1: "日光", 2: "荧光灯", 3: "白炽灯", 4: "闪光灯", 9: "晴天", 10: "阴天", 11: "阴影"}
_FLASH_MODES = {0: "无闪光", 1: "闪光", 5: "防红眼", 7: "防红眼+同步", 9: "闪光", 13: "后帘同步"}
_SENSOR_TYPES = {1: "单色", 2: "单芯片", 3: "双芯片", 4: "三芯片", 5: "色彩矩阵"}
_ENUM_VALS = {0: "标准", 1: "低", 2: "高"}


def _format_exposure(v):
    if isinstance(v, tuple | list) and len(v) == 2 and v[1]:
        return f"{v[0]}/{v[1]} s"
    f = float(v)
    if f >= 1:
        return f"{f:.1f} s"
    return f"1/{int(1/f)} s"


def _format_aperture(v):
    return f"F/{float(v):.1f}"


def _format_metering(v):
    return _METERING_MODES.get(int(v), str(v))


def _format_light(v):
    return _LIGHT_SOURCES.get(int(v), str(v))


def _format_flash(v):
    return _FLASH_MODES.get(int(v), str(v))


def _format_sensor(v):
    return _SENSOR_TYPES.get(int(v), str(v))


def _format_enum(v):
    return _ENUM_VALS.get(int(v), str(v))


# ── 需要展示的 EXIF 字段（tag_id → (标签名, 格式化函数)） ──
_EXIF_FIELDS: dict[int, tuple[str, Callable]] = {
    271: ("相机品牌", str),
    272: ("相机型号", str),
    305: ("软件", str),
    306: ("拍摄日期", str),
    36867: ("原始日期", str),
    33434: ("快门速度", _format_exposure),
    33437: ("光圈", _format_aperture),
    34855: ("ISO", str),
    37386: ("焦距", lambda v: f"{v:.1f} mm" if v else str(v)),
    42036: ("数码变焦", lambda v: f"{float(v):.2f}x"),
    37377: ("快门速度值", lambda v: f"{v:.4f} EV"),
    37378: ("光圈值", lambda v: f"{v:.2f} EV"),
    37379: ("亮度值", lambda v: f"{v:.2f} EV"),
    37380: ("曝光补偿", lambda v: f"{v:.2f} EV"),
    37381: ("最大光圈", lambda v: f"{v:.2f}"),
    37383: ("测光模式", _format_metering),
    37384: ("光源", _format_light),
    37385: ("闪光灯", _format_flash),
    37393: ("图像宽度", str),
    37394: ("图像高度", str),
    40961: ("色彩空间", lambda v: "sRGB" if v == 1 else f"未校准({v})"),
    40962: ("像素宽度", str),
    40963: ("像素高度", str),
    41486: ("对焦距离", lambda v: f"{float(v):.2f} m"),
    41495: ("传感类型", _format_sensor),
    41986: ("对比度", _format_enum),
    41987: ("饱和度", _format_enum),
    41988: ("锐度", _format_enum),
}


class ExifPanel(QWidget):
    """右侧 EXIF 信息面板"""

    PANEL_WIDTH = 260

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("exifPanel")
        self.setMinimumWidth(180)
        self.setVisible(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── 标题 ──
        title = QLabel("信息")
        title.setObjectName("exifTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFixedHeight(32)
        layout.addWidget(title)

        # ── 树形列表 ──
        self._tree = QTreeWidget()
        self._tree.setObjectName("exifTree")
        self._tree.setHeaderLabels(["字段", "值"])
        self._tree.setRootIsDecorated(False)
        self._tree.setAlternatingRowColors(True)
        self._tree.setColumnCount(2)
        self._tree.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        hdr = self._tree.header()
        if hdr:
            hdr.setStretchLastSection(False)
            hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self._tree, 1)

    def set_image(self, path: str | Path):
        """加载图片基本信息 + EXIF 附加信息"""
        self._tree.clear()
        fp = Path(path)

        try:
            # ── 基本信息（总是有） ──
            items: list[QTreeWidgetItem] = []
            items.append(QTreeWidgetItem(["文件名", fp.name]))
            items.append(QTreeWidgetItem([
                "大小", _format_size(fp.stat().st_size),
            ]))
            items.append(QTreeWidgetItem([
                "修改时间",
                datetime.fromtimestamp(fp.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
            ]))

            # 尝试获取图片尺寸（不依赖 EXIF）
            raw = None
            try:
                with Image.open(str(fp)) as img:
                    w, h = img.size
                    items.append(QTreeWidgetItem(["尺寸", f"{w} × {h} px"]))
                    try:
                        raw = dict(img.getexif())
                    except Exception:
                        pass
            except Exception:
                items.append(QTreeWidgetItem(["尺寸", "无法读取"]))

            self._tree.addTopLevelItems(items)

            # ── EXIF 附加信息 ──

            if raw:
                exif_items = []
                for tag_id, (label, fmt) in _EXIF_FIELDS.items():
                    raw_val = raw.get(tag_id)
                    if raw_val is None:
                        continue
                    try:
                        val_str = fmt(raw_val)
                    except Exception:
                        val_str = str(raw_val)
                    item = QTreeWidgetItem([label, val_str])
                    item.setToolTip(1, val_str)
                    exif_items.append(item)

                if exif_items:
                    sep = QTreeWidgetItem(["─── EXIF ───", ""])
                    sep.setFlags(
                        sep.flags() & ~Qt.ItemFlag.ItemIsSelectable
                    )
                    self._tree.addTopLevelItem(sep)
                    self._tree.addTopLevelItems(exif_items)

                    # 额外未映射的原始标签
                    mapped_ids = set(_EXIF_FIELDS.keys())
                    extras = []
                    for tag_id, raw_val in raw.items():
                        if tag_id in mapped_ids or tag_id == 0:
                            continue
                        name = EXIF_TAGS.get(tag_id, f"0x{tag_id:04X}")
                        extras.append(QTreeWidgetItem([name, str(raw_val)[:60]]))
                    if extras:
                        self._tree.addTopLevelItems(extras[:20])

        except Exception:
            self._show_empty("无法读取")

    def clear_exif(self):
        self._tree.clear()

    def _show_empty(self, msg: str):
        item = QTreeWidgetItem(["信息", msg])
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
        self._tree.addTopLevelItem(item)

    def toggle(self):
        self.setVisible(not self.isVisible())
