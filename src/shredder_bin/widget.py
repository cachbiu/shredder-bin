"""Frameless always-on-top recycle widget with shredder GIF."""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QPoint, Qt, QTimer
from PyQt6.QtGui import (
    QAction,
    QColor,
    QDragEnterEvent,
    QDropEvent,
    QMouseEvent,
    QMovie,
    QPainter,
    QPaintEvent,
    QPen,
)
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QMenu,
    QMessageBox,
    QWidget,
)

from shredder_bin.paths import collect_local_paths
from shredder_bin.recycle import open_recycle_bin, send_to_recycle
from shredder_bin.resources import asset_path

WIDGET_WIDTH = 250
WIDGET_HEIGHT = 192
CLICK_SLOP = 6


def _gif_path() -> Path:
    return asset_path("shredder.gif")


class IdleBin(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self._hover = False

    def set_hover(self, hover: bool) -> None:
        if self._hover != hover:
            self._hover = hover
            self.update()

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: ARG002
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        margin = 18
        body = (margin, int(h * 0.32), w - 2 * margin, int(h * 0.52))
        lid = (margin - 6, int(h * 0.22), w - 2 * margin + 12, int(h * 0.12))
        fill = QColor("#3d8bfd") if self._hover else QColor("#5a6570")
        painter.setPen(QPen(QColor("#1e2430"), 3))
        painter.setBrush(fill)
        painter.drawRoundedRect(*lid, 6, 6)
        painter.drawRoundedRect(*body, 10, 10)
        painter.setPen(QPen(QColor("#dce6f0"), 3))
        cx = w // 2
        for dx in (-18, 0, 18):
            painter.drawLine(cx + dx, body[1] + 16, cx + dx, body[1] + body[3] - 16)
        painter.end()


class ShredderWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Shredder Bin")
        self.setFixedSize(WIDGET_WIDTH, WIDGET_HEIGHT)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setAcceptDrops(True)
        self.setStyleSheet("background-color: #1a1d22;")

        self._idle = IdleBin(self)
        self._idle.setGeometry(0, 0, WIDGET_WIDTH, WIDGET_HEIGHT)

        self._gif = QLabel(self)
        self._gif.setGeometry(0, 0, WIDGET_WIDTH, WIDGET_HEIGHT)
        self._gif.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._gif.setScaledContents(True)
        self._gif.hide()

        self._movie: QMovie | None = None
        gif = _gif_path()
        if gif.is_file():
            self._movie = QMovie(str(gif))
            self._gif.setMovie(self._movie)
            self._movie.frameChanged.connect(self._on_gif_frame)
            self._show_idle_frame()

        self._drag_pos: QPoint | None = None
        self._press_global: QPoint | None = None
        self._moved = False
        self._always_on_top = True
        self._busy = False

        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            self.move(geo.right() - WIDGET_WIDTH - 24, geo.bottom() - WIDGET_HEIGHT - 24)

    def _on_gif_frame(self, frame: int) -> None:
        if self._movie is None:
            return
        count = self._movie.frameCount()
        if count > 0 and frame >= count - 1:
            QTimer.singleShot(80, self._stop_gif)

    def _show_idle_frame(self) -> None:
        if self._movie is None:
            self._gif.hide()
            self._idle.show()
            return
        self._idle.hide()
        self._gif.show()
        self._movie.stop()
        self._movie.jumpToFrame(0)

    def _play_gif(self) -> None:
        if self._movie is None:
            return
        self._idle.hide()
        self._gif.show()
        self._movie.stop()
        self._movie.jumpToFrame(0)
        self._movie.start()

    def _stop_gif(self) -> None:
        self._show_idle_frame()
        self._busy = False

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        mime = event.mimeData()
        if mime is not None and mime.hasUrls():
            event.acceptProposedAction()
            self._idle.set_hover(True)
        else:
            event.ignore()

    def dragLeaveEvent(self, event) -> None:  # noqa: ANN001
        self._idle.set_hover(False)
        event.accept()

    def dropEvent(self, event: QDropEvent) -> None:
        self._idle.set_hover(False)
        mime = event.mimeData()
        if mime is None or not mime.hasUrls():
            event.ignore()
            return
        event.acceptProposedAction()
        accepted, rejected = collect_local_paths(list(mime.urls()))
        if rejected and not accepted:
            QMessageBox.warning(
                self,
                "Shredder Bin",
                "Можно удалять только локальные файлы и папки.\n"
                + "\n".join(rejected[:8]),
            )
            return
        if not accepted or self._busy:
            return
        self._busy = True
        failed = send_to_recycle(accepted)
        if failed:
            self._busy = False
            lines = "\n".join(f"{path}: {err}" for path, err in failed[:8])
            QMessageBox.warning(self, "Shredder Bin", f"Не удалось удалить:\n{lines}")
            return
        if self._movie is not None:
            self._play_gif()
        else:
            self._busy = False

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self._press_global = event.globalPosition().toPoint()
            self._moved = False
        elif event.button() == Qt.MouseButton.RightButton:
            self._show_menu(event.globalPosition().toPoint())

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._drag_pos is None or self._press_global is None:
            return
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        current = event.globalPosition().toPoint()
        if (current - self._press_global).manhattanLength() > CLICK_SLOP:
            self._moved = True
            self.move(current - self._drag_pos)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton and not self._moved:
            open_recycle_bin()
        self._drag_pos = None
        self._press_global = None
        self._moved = False

    def _show_menu(self, pos: QPoint) -> None:
        menu = QMenu(self)
        open_act = QAction("Открыть корзину", self)
        open_act.triggered.connect(open_recycle_bin)
        menu.addAction(open_act)

        top_act = QAction("Поверх окон", self)
        top_act.setCheckable(True)
        top_act.setChecked(self._always_on_top)
        top_act.triggered.connect(self._toggle_on_top)
        menu.addAction(top_act)

        menu.addSeparator()
        quit_act = QAction("Выход", self)
        quit_act.triggered.connect(QApplication.quit)
        menu.addAction(quit_act)
        menu.exec(pos)

    def _toggle_on_top(self, checked: bool) -> None:
        self._always_on_top = checked
        flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool
        if checked:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.show()
