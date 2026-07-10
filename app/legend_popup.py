"""Scrollable legend popup — the hover window replacing QToolTip.

QToolTip neither scrolls nor shrinks: content taller than the screen
gets clipped at its edge (owner report — article hovers on a 1080p
screen). This window caps itself to screen fractions, shows a scrollbar
when the content is taller, and stays open while the cursor is over it
so the wheel can scroll the article.
"""

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QCursor, QGuiApplication
from PySide6.QtWidgets import QFrame, QLabel, QScrollArea, QVBoxLayout, QWidget

from config import defaults


class LegendPopup(QWidget):
    def __init__(self):
        super().__init__(
            None,
            Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self._label = QLabel()
        self._label.setTextFormat(Qt.TextFormat.RichText)
        self._label.setStyleSheet(
            f"color: {defaults.LEGEND_TEXT}; "
            f"padding: {defaults.LEGEND_PADDING_PX}px;"
        )
        self._scroll = QScrollArea()
        self._scroll.setWidget(self._label)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(1, 1, 1, 1)   # the border
        layout.addWidget(self._scroll)
        self.setStyleSheet(
            f"LegendPopup {{ background: {defaults.LEGEND_BORDER}; }}"
            f"QScrollArea, QLabel {{ background: {defaults.LEGEND_BG}; }}"
        )
        self._html: str | None = None

    def show_html(self, content: str, anchor: QPoint) -> None:
        """Show `content` beside `anchor` (a global cursor position),
        sized to it but capped to the screen fractions — a taller
        article scrolls instead of clipping."""
        if content != self._html:
            self._html = content
            self._label.setText(content)
            self._label.adjustSize()
            screen = (
                QGuiApplication.screenAt(anchor)
                or QGuiApplication.primaryScreen()
            ).availableGeometry()
            frame = 2 + self._scroll.verticalScrollBar().sizeHint().width()
            width = min(
                self._label.width() + frame,
                round(screen.width() * defaults.LEGEND_MAX_WIDTH_FRACTION),
            )
            height = min(
                self._label.height() + 2,
                round(screen.height() * defaults.LEGEND_MAX_HEIGHT_FRACTION),
            )
            self.resize(width, height)
        screen = (
            QGuiApplication.screenAt(anchor) or QGuiApplication.primaryScreen()
        ).availableGeometry()
        offset = defaults.LEGEND_CURSOR_OFFSET_PX
        x = min(anchor.x() + offset, screen.right() - self.width())
        y = min(anchor.y() + offset, screen.bottom() - self.height())
        self.move(max(screen.left(), x), max(screen.top(), y))
        if not self.isVisible():
            self.show()

    def hide_unless_hovered(self) -> None:
        """Hide — unless the cursor sits INSIDE the popup (crossing from
        the dial into the popup to scroll must not close it)."""
        if not self.geometry().contains(QCursor.pos()):
            self.dismiss()

    def dismiss(self) -> None:
        self._html = None
        self.hide()

    def leaveEvent(self, event) -> None:
        self.dismiss()
        super().leaveEvent(event)
