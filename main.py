#author Red
#260622 Red&小宋 RedGarph V0.0.7 — 图片查看器入口

import os
import sys
import traceback
from pathlib import Path
from datetime import datetime

from PyQt6.QtCore import Qt, qInstallMessageHandler
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


def _log(msg: str):
    """写入崩溃日志"""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {msg}\n")


def _qt_handler(msg_type, context, message):
    """捕获 Qt 内部错误/警告"""
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

        win = MainWindow(theme="night")
        win.show()

        # 处理命令行参数
        args = sys.argv[1:]
        if args:
            p = Path(args[0])
            if p.exists():
                win.load_path(p)

        sys.exit(app.exec())
    except Exception:
        _log("Fatal error in main():\n" + traceback.format_exc())
        raise


if __name__ == "__main__":
    main()
