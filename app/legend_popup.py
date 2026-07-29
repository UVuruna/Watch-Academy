"""Scrollable legend popup — the hover window replacing QToolTip.

QToolTip neither scrolls nor shrinks: content taller than the screen
gets clipped at its edge (owner report — article hovers on a 1080p
screen). This window caps itself to screen fractions, shows a scrollbar
when the content is taller, and stays open while the cursor is over it
so the wheel can scroll the article.
"""

import math

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QCursor, QGuiApplication, QTextDocument
from PySide6.QtWidgets import QFrame, QLabel, QScrollArea, QVBoxLayout, QWidget

from app import native
from config import encyclopedia_ui, palette


class LegendPopup(QWidget):
    def __init__(self):
        super().__init__(
            None,
            # WindowStaysOnTopHint puts the popup in the TOPMOST band so it
            # can ride above the dial in its "top" z-mode (owner 15h item
            # 3A: the legend was appearing BEHIND the topmost, focused
            # dial — invisible). WA_ShowWithoutActivating keeps it from
            # ever stealing focus.
            Qt.WindowType.ToolTip
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self._label = QLabel()
        self._label.setTextFormat(Qt.TextFormat.RichText)
        # THE HOVER TEASER LAW's clickable footer (owner 2026-07-26):
        # the LEARN MORE anchor must be mouse-reachable — links only,
        # no text selection — and its click is routed to whatever the
        # owner of the popup installs on `on_link` (the widget wires
        # the same Encyclopedia jump SPACE makes).
        self._label.setTextInteractionFlags(
            Qt.TextInteractionFlag.LinksAccessibleByMouse
        )
        self._label.linkActivated.connect(self._link_activated)
        self.on_link = None
        # Justified prose must WRAP inside its declared column (owner
        # regression 2026-07-13: without word wrap the label sized to
        # the unwrapped document — kilometer-wide paragraphs). The
        # label NEVER sizes itself: show_html measures the content and
        # fixes the width, because QLabel's own wordWrap heuristic
        # squeezes declared table columns (measured: two 420px columns
        # collapse to 533px total).
        self._label.setWordWrap(True)
        self._label.setStyleSheet(
            f"color: {palette.LEGEND_TEXT}; "
            f"padding: {encyclopedia_ui.LEGEND_PADDING_PX}px;"
        )
        self._measure = QTextDocument()
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
            f"LegendPopup {{ background: {palette.LEGEND_BORDER}; }}"
            f"QScrollArea, QLabel {{ background: {palette.LEGEND_BG}; }}"
        )
        self._html: str | None = None

    def show_html(self, content: str, anchor: QPoint) -> None:
        """Show `content` beside `anchor` (a global cursor position),
        sized to it but capped to the screen fractions — a taller
        article scrolls instead of clipping."""
        if content != self._html:
            self._html = content
            screen = (
                QGuiApplication.screenAt(anchor)
                or QGuiApplication.primaryScreen()
            ).availableGeometry()
            cap = round(screen.width() * encyclopedia_ui.LEGEND_MAX_WIDTH_FRACTION)
            # Measure the content laid out at the cap: declared table
            # columns hold their width, nowrap lines keep their natural
            # one — idealWidth is the width the content actually asks
            # for (QLabel's own wordWrap sizing would squeeze it).
            self._measure.setDefaultFont(self._label.font())
            self._measure.setHtml(content)
            self._measure.setTextWidth(cap)
            pad = 2 * encyclopedia_ui.LEGEND_PADDING_PX
            wanted = math.ceil(self._measure.idealWidth()) + pad
            self._label.setFixedWidth(max(wanted, 1))
            # Fixed-width table columns do NOT squeeze below their
            # declared widths — content wider than the cap (e.g. the
            # hexa two-column legend on a scaled-down laptop) scrolls
            # sideways instead of clipping.
            self._scroll.setHorizontalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAsNeeded
                if wanted > cap
                else Qt.ScrollBarPolicy.ScrollBarAlwaysOff
            )
            self._label.setText(content)
            self._label.adjustSize()
            frame = 2 + self._scroll.verticalScrollBar().sizeHint().width()
            width = min(self._label.width() + frame, cap)
            height = min(
                self._label.height() + 2,
                round(screen.height() * encyclopedia_ui.LEGEND_MAX_HEIGHT_FRACTION),
            )
            self.resize(width, height)
        screen = (
            QGuiApplication.screenAt(anchor) or QGuiApplication.primaryScreen()
        ).availableGeometry()
        offset = encyclopedia_ui.LEGEND_CURSOR_OFFSET_PX
        x = min(anchor.x() + offset, screen.right() - self.width())
        y = min(anchor.y() + offset, screen.bottom() - self.height())
        self.move(max(screen.left(), x), max(screen.top(), y))
        if not self.isVisible():
            self.show()
        # The WindowStaysOnTopHint flag lands the popup in the topmost
        # band, but the dial's "top" z-mode asserts native HWND_TOPMOST
        # AND is the focused window, which would otherwise sit at the top
        # of that band. Mirror the dial's own trick (SWP_NOACTIVATE, no
        # focus theft) to place the freshly shown popup ABOVE it (owner
        # 15h item 3A). Harmless in the other z-modes.
        native.assert_topmost(int(self.winId()))

    def _link_activated(self, _href: str) -> None:
        """A footer anchor was clicked — hand it to the installed
        handler (the widget's Encyclopedia jump); no handler, no-op."""
        if self.on_link is not None:
            self.on_link()

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
