#author Red
#260620 Red&小宋 RedGarph V0.0.3 — 图片查看器入口

import sys
import traceback
from pathlib import Path
from datetime import datetime

from PyQt6.QtCore import Qt, qInstallMessageHandler
from PyQt6.QtWidgets import QApplication

from viewer.window import MainWindow

if getattr(sys, "frozen", False):
    LOG_DIR = Path(sys.executable).parent          # exe 所在目录
else:
    LOG_DIR = Path(__file__).resolve().parent      # 源码目录
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
