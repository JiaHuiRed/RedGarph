#author Red
#260904 Red&小宋 RedGarph V0.1.8 — 图片查看器入口

import os
import sys
import traceback
from pathlib import Path
from datetime import datetime

from PyQt6.QtCore import Qt, qInstallMessageHandler, QTimer, QtMsgType
from PyQt6.QtWidgets import QApplication

from viewer.window import MainWindow

# PyInstaller onefile 模式：sys.executable 是临时目录，日志存不走
# → 改用 exe 所在目录（sys.argv[0] 始终是原始 exe 路径）
if getattr(sys, "frozen", False):
    LOG_DIR = Path(sys.argv[0]).resolve().parent
else:
    LOG_DIR = Path(__file__).resolve().parent
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "crash.log"

# 日志大小上限：超过后轮转为 crash.log.1，避免无限增长
_LOG_MAX_BYTES = 1 * 1024 * 1024


def _resource_path(relative: str) -> Path:
    """兼容源码运行和 PyInstaller onefile 的资源路径"""
    if getattr(sys, "frozen", False):
        base = Path(getattr(sys, "_MEIPASS", "") or Path(sys.argv[0]).resolve().parent)
    else:
        base = Path(__file__).resolve().parent
    return base / relative


def _log(msg: str):
    """写入崩溃日志；超过上限时轮转保留一份旧日志"""
    try:
        if LOG_FILE.exists() and LOG_FILE.stat().st_size > _LOG_MAX_BYTES:
            rotated = LOG_FILE.with_name(LOG_FILE.name + ".1")
            rotated.unlink(missing_ok=True)
            LOG_FILE.replace(rotated)
    except OSError:
        pass
    try:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{ts}] {msg}\n")
    except OSError:
        # 磁盘不可写时静默放弃，不能让日志拖垮应用
        pass


def _qt_handler(msg_type, context, message):
    """捕获 Qt 内部错误/警告；debug 级噪音不落盘"""
    if msg_type == QtMsgType.QtDebugMsg:
        return
    _log(f"Qt: {message}")


def _excepthook(typ, val, tb):
    """捕获未处理异常"""
    _log("Unhandled exception:\n" + "".join(traceback.format_exception(typ, val, tb)))


def main():
    sys.excepthook = _excepthook
    qInstallMessageHandler(_qt_handler)

    # ── PyInstaller frozen: 确保 Qt 能找到平台插件 ──
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None) or Path(sys.argv[0]).resolve().parent
        plugin_path = os.path.join(meipass, "PyQt6", "Qt6", "plugins", "platforms")
        if os.path.isdir(plugin_path):
            os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = plugin_path
            _log(f"QT_QPA_PLATFORM_PLUGIN_PATH={plugin_path}")

    try:
        app = QApplication(sys.argv)
        app.setApplicationName("RedGarph")
        app.setOrganizationName("RedStudio")

        # 设置窗口图标（标题栏 + 任务栏）
        icon_path = _resource_path(Path("resources") / "icon.ico")
        if icon_path.exists():
            from PyQt6.QtGui import QIcon
            app.setWindowIcon(QIcon(str(icon_path)))

        win = MainWindow(theme="night")

        # Qt 6.11 frameless 窗口首次 show 会用默认尺寸建窗再重建（闪烁）。
        # 绕法：先 show 触发重建（隐藏态），稳定后再真正显示
        win.show()
        win.hide()
        QTimer.singleShot(50, win.show)

        # 无框窗口默认不抢前台：延时激活（立即激活在窗口未显示时无效，且可能触发 native 重建闪烁）
        QTimer.singleShot(100, win.raise_)
        QTimer.singleShot(100, win.activateWindow)

        # 处理命令行参数（延迟到事件循环首轮，确保窗口先 show 出来）
        args = sys.argv[1:]
        if args:
            p = Path(args[0])
            if p.exists():
                QTimer.singleShot(0, lambda: win.load_path(p))

        sys.exit(app.exec())
    except Exception:
        _log("Fatal error in main():\n" + traceback.format_exc())
        raise


if __name__ == "__main__":
    main()
