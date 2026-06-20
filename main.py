#author Red
#260620 Red&小宋 RedGarph V0.0.1 — 图片查看器入口

import sys
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

from viewer.window import MainWindow


def main():
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


if __name__ == "__main__":
    main()
