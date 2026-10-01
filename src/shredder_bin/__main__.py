"""python -m shredder_bin"""

from __future__ import annotations

import sys

from PyQt6.QtWidgets import QApplication

from shredder_bin.shortcut import ensure_desktop_shortcut
from shredder_bin.widget import ShredderWidget


def main() -> int:
    ensure_desktop_shortcut()
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    widget = ShredderWidget()
    widget.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
