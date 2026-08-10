"""The Watch Face window (R-01, see window.md) — the owner-approved
Watch Face & Settings UI rework: a left `QListWidget` sidebar beside a
right `QStackedWidget` page per section (the same list+stack shape
`app.settings_dialog.dialog.SettingsDialog` already uses), replacing —
over several phases — Design/Pointer Theme/Slot Theme and the Settings
dialog's own Display/Colors/Themes groups. Phase ①+② wired five
sections; Phase ③ (see themes.md) replaced the Themes & Slots
placeholder with the real section; Phase ④ (see colors.md/opacity.md)
replaced the last two placeholders — every section was real by then,
and the sidebar has carried its final shape since Phase ①. Phase 6
FINAL cleanup then DELETED the old windows/dialog groups outright —
this window is now the ONLY place any of that content lives.
"""

from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtWidgets import (
    QDialog, QFrame, QHBoxLayout, QLabel, QListWidget, QScrollArea,
    QStackedWidget, QStyle, QVBoxLayout, QWidget,
)

from app.theme import apply_theme, size_to_screen
from app.watch_face import (
    bodies, colors, numerals, opacity, pointer, ring, size, themes, umbra_aura,
)
from config import constants, defaults
from config.ui_text import ui

# THE SPACE & LEGIBILITY LAW's screen floor (rules/GUI.md): the computed
# window minimum below may never demand a screen the user does not have.
# Content past the floor scrolls instead (ladder step 4 — at the floor
# the window is genuinely full).
_SCREEN_FLOOR = (1280, 720)

# Section registry: (title, builder). `builder(settings, setters, tr) ->
# QWidget`, or `None` for a not-yet-built placeholder page — a later
# phase replaces a `None` entry with a real module of the same shape.
_SECTIONS = (
    ("Pointer", pointer.build),
    ("Ring", ring.build),
    ("Numerals", numerals.build),
    ("Hands & Bodies", bodies.build),
    ("Umbra & Aura", umbra_aura.build),
    ("Opacity", opacity.build),
    ("Themes & Slots", themes.build),
    ("Colors", colors.build),
    ("Size", size.build),
)


def _placeholder_page(tr) -> QWidget:
    layout = QVBoxLayout()
    layout.addWidget(QLabel(tr("Arrives in a later phase")))
    layout.addStretch(1)
    widget = QWidget()
    widget.setLayout(layout)
    return widget


class WatchFaceDialog(QDialog):
    """Non-modal, LIVE-APPLY (see window.md): every section's pick calls
    its setter immediately — there is nothing to commit, so no
    OK/Cancel."""

    def __init__(
        self, settings, setters: dict, overlay: dict | None = None,
        stay_on_top: bool = False, parent=None,
    ):
        super().__init__(parent)
        self._tr = lambda text: ui(overlay or {}, text)  # noqa: E731
        self.setWindowTitle(f"{constants.APP_NAME} — {self._tr('Watch Face')}")
        if stay_on_top:
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self._settings = settings
        self._setters = setters
        self._nav_list: QListWidget | None = None
        self._stack: QStackedWidget | None = None
        self._layout = QVBoxLayout(self)
        self._body = QHBoxLayout()
        self._layout.addLayout(self._body, stretch=1)
        # Theme BEFORE build: `_build` computes the content column and the
        # window minimum from the pages' size hints, and the QSS paddings
        # are part of the real size (measured 20px on the Colors groups) —
        # hints taken un-themed under-measure exactly that much.
        apply_theme(self)
        self._build()
        size_to_screen(self, 1, 1, defaults.DIALOG_SQUARE_HEIGHT_FRACTION)

    def refresh(self, settings, setters: dict) -> None:
        """Re-supplies the live settings after a pick applies (owner
        spec: a live picker, not a transactional dialog) — called by
        the controller."""
        self._settings = settings
        self._setters = setters
        self._build()

    def _capture_scrolls(self) -> list[tuple[int, int]]:
        """The scroll offset of every page, so a live-pick rebuild can put
        each one back exactly where it stood (owner decree 2026-08-10: a
        pick may change the WATCH and nothing else — never the section,
        never the scroll, never the focused side of the window)."""
        if self._stack is None:
            return []
        offsets: list[tuple[int, int]] = []
        for index in range(self._stack.count()):
            page_scroll = self._stack.widget(index)
            if isinstance(page_scroll, QScrollArea):
                offsets.append((page_scroll.horizontalScrollBar().value(),
                                page_scroll.verticalScrollBar().value()))
            else:
                offsets.append((0, 0))
        return offsets

    def _restore_scrolls(self, offsets: list[tuple[int, int]]) -> None:
        if self._stack is None:
            return
        for index, (horizontal, vertical) in enumerate(offsets):
            if index >= self._stack.count():
                break
            page_scroll = self._stack.widget(index)
            if isinstance(page_scroll, QScrollArea):
                page_scroll.horizontalScrollBar().setValue(horizontal)
                page_scroll.verticalScrollBar().setValue(vertical)

    def _build(self) -> None:
        # KEEP THE SELECTED ROW across live-pick rebuilds — the SAME fix
        # `design_window.DesignDialog._build` carries for its
        # `QTabWidget`: every pick routes through the controller's
        # `refresh()`, which rebuilds this sidebar+stack pair from
        # scratch, and a fresh `QListWidget` always opens at row 0.
        previous = self._nav_list.currentRow() if self._nav_list is not None else 0
        scrolls = self._capture_scrolls()
        while self._body.count():
            item = self._body.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
        nav_list = QListWidget()
        # MEASURED width, never a guessed constant (ITEM CUT, Zubi fix
        # round 2026-08-09: "Themes & Slots" needed 198px while the old
        # fixed 170 offered 156): the longest section title in the
        # CURRENT font, plus the item/list chrome the theme QSS adds
        # (12px item padding + 6px list padding per side, borders).
        metrics = nav_list.fontMetrics()
        longest = max(
            metrics.horizontalAdvance(self._tr(title))
            for title, _builder in _SECTIONS
        )
        nav_width = max(defaults.SETTINGS_NAV_WIDTH_PX, longest + 48)
        nav_list.setFixedWidth(nav_width)  # layout-law: exempt - measured from the longest title just above
        self._nav_width = nav_width
        stack = QStackedWidget()
        pages: list[QWidget] = []
        for title, builder in _SECTIONS:
            nav_list.addItem(self._tr(title))
            if builder is None:
                page = _placeholder_page(self._tr)
            else:
                page = builder(self._settings, self._setters, self._tr)
            pages.append(page)
        for page in pages:
            holder = QWidget()
            holder_layout = QVBoxLayout(holder)
            holder_layout.setContentsMargins(0, 0, 0, 0)
            holder_layout.addWidget(page)
            # Content packs to the top; leftover height stays EMPTY below
            # instead of being wedged between the rows.
            holder_layout.addStretch(1)
            page_scroll = QScrollArea()
            page_scroll.setWidgetResizable(True)
            page_scroll.setFrameShape(QFrame.Shape.NoFrame)
            page_scroll.setWidget(holder)
            stack.addWidget(page_scroll)
        nav_list.currentRowChanged.connect(stack.setCurrentIndex)
        row = max(0, min(previous, nav_list.count() - 1))
        nav_list.setCurrentRow(row)
        stack.setCurrentIndex(row)
        # The sidebar must NEVER steal the caret from the pick the user
        # just made (owner decree 2026-08-10 — "odvede me na levu
        # stranu"): the list is reachable by mouse and by Tab, but a
        # rebuilt list never grabs focus on its own.
        nav_list.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self._body.addWidget(nav_list)
        self._body.addWidget(stack, stretch=1)
        self._nav_list = nav_list
        self._stack = stack
        # ONE readable content column for every section (the fix for the
        # owner's 2026-08-06 screenshots: bare pages in the stack made the
        # window's minimum the TALLEST section — 2090px — while maximized
        # the rows stretched across the whole 4K screen). The column width
        # is COMPUTED from the widest section's own hint — polished FIRST,
        # because the theme's paddings are part of the real size (hints
        # taken un-polished measured 20px short on the Colors groups) —
        # so no section is starved and none inflated past what any need.
        for page in pages:
            page.ensurePolished()
            for child in page.findChildren(QWidget):
                child.ensurePolished()
        column_width = max(page.minimumSizeHint().width() for page in pages)
        for page in pages:
            page.setMaximumWidth(column_width)
        self._declare_minimum(pages, column_width)
        # TWICE, and that is not belt-and-braces: a scrollbar's range is
        # still 0 until the layout has run, so the immediate call clamps
        # to the top on a page whose geometry is not settled yet. The
        # queued call lands after that layout pass, with the real range.
        self._restore_scrolls(scrolls)
        QTimer.singleShot(0, lambda: self._restore_scrolls(scrolls))

    def _declare_minimum(self, pages: list[QWidget], column_width: int) -> None:
        """The DECLARED minimum, computed from measured content (THE
        SPACE & LEGIBILITY LAW): wide enough for the sidebar plus the
        widest section column plus the scrollbar — no section ever needs
        a horizontal scrollbar — and tall enough for the tallest section
        up to the screen floor, where the vertical scrollbar lawfully
        takes over (the window is genuinely full there)."""
        scrollbar = self.style().pixelMetric(
            QStyle.PixelMetric.PM_ScrollBarExtent
        )
        margins = self._layout.contentsMargins()
        chrome_w = margins.left() + margins.right() + self._body.spacing()
        chrome_h = margins.top() + margins.bottom()
        width = (self._nav_width + column_width
                 + scrollbar + chrome_w)
        tallest = max(page.minimumSizeHint().height() for page in pages)
        floor_w, floor_h = _SCREEN_FLOOR
        self.setMinimumSize(QSize(min(width, floor_w),
                                  min(tallest + chrome_h, floor_h)))
