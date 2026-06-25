#author Red
#260620 Red&小宋 RedGarph V0.0.1 — 配置常量

# ── 支持图片格式 ──
IMAGE_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".bmp", ".gif",
    ".tif", ".tiff", ".webp", ".ico", ".svg",
}

# ── 幻灯片默认间隔（秒） ──
SLIDESHOW_INTERVAL = 3

# ── 缩放参数 ──
ZOOM_FACTOR = 1.15
ZOOM_MAX = 32.0
ZOOM_MIN = 0.05

# ── 窗口默认尺寸 ──
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800

# ── 应用信息 ──
APP_NAME = "RedGarph"
APP_VERSION = "0.0.9"
ORG_NAME = "RedStudio"


def format_size(n: int) -> str:
    """人性化文件大小"""
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {unit}" if unit != "B" else f"{n} B"
        n /= 1024
    return f"{n:.1f} TB"
