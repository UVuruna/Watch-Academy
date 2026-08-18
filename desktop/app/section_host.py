"""ONE nav-list-beside-a-page-stack, for every window built that way.

A left `QListWidget` of section titles, a right `QStackedWidget` holding
one `QScrollArea` per section, the sidebar's width MEASURED from the
longest title, and the window minimum computed from the pages' own
hints. The Watch Face window and the Settings dialog had written that
out twice — the same measured-width formula, the same per-page scroll
area, the same "nav + widest page + scrollbar" minimum — and the OOP
audit of 2026-08-18 named it (R16, section 1 COPY).

**The host takes BUILT PAGES, never builders.** That is the seam that
removes the duplication without moving anyone's `self`: both windows
build their pages the way they already did — the Settings dialog's three
section mixins keep every widget handle on the dialog, because
`result_settings()` reads them back on OK — and hand the finished
widgets here. A host that built pages would have to be handed the
dialog's state and hand its widgets back, which is the back-channel a
mixin exists to avoid.

**Nothing here is a policy.** Every difference between the two windows
that reached this file is a NAMED argument with the reason written
beside it, so a third window that wants a section list gets one line
instead of a third copy.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QListWidget, QScrollArea, QStackedWidget, QStyle,
    QVBoxLayout, QWidget,
)

from config import defaults

# THE SPACE & LEGIBILITY LAW's screen floor (rules/GUI.md): a computed
# window minimum may never demand a screen the user does not have.
# Content past the floor scrolls instead — ladder step 4, at which point
# the window is genuinely full. Both windows quoted these two numbers
# separately before this module existed.
SCREEN_FLOOR = (1280, 720)


class SectionHost(QWidget):
    """The nav list and the page stack, as one widget.

    `sections` is a sequence of `(label, page)` — the label exactly as
    it should read in the sidebar (already translated, already carrying
    whatever arrow the window uses) and the page widget, already built.
    """

    def __init__(
        self,
        sections: Sequence[tuple[str, QWidget]],
        *,
        parent: QWidget | None = None,
        measure_minimum: bool = True,
        row_height: int | None = None,
        page_holder: Callable[[QWidget], QWidget] | None = None,
        horizontal_scroll: bool = True,
    ) -> None:
        """
        `measure_minimum` — measure the pages by `minimumSizeHint()`
        (the Watch Face window: its flow galleries reflow, so the
        minimum is the honest number) or by `sizeHint()` (the Settings
        dialog: its panels do not reflow, and the preferred size is what
        keeps a combo row unclipped).

        `row_height` — when given, every nav item's size hint is stamped
        with it. QListWidget's own row-layout pass does not always match
        the delegate's styled hint once QSS padding is involved, and the
        selected item's pill then overlaps its neighbours (owner-reported
        text clipping, 2026-08-13). Only the window that measured that
        row height passes it; a window that never saw the overlap keeps
        Qt's own spacing rather than inheriting a fix for a bug it does
        not have.

        `page_holder` — wraps each page before it enters its scroll
        area. The Watch Face window needs one, because a plain holder
        under `widgetResizable` sizes a page from its width-independent
        minimum and a flow gallery only knows its height once it has a
        width.

        `horizontal_scroll` — False pins the horizontal bar off. A
        `QScrollArea` rebuilt inside an ALREADY VISIBLE window shows an
        empty bar (range 0, nothing to scroll), which is exactly the bar
        the layout law forbids; the window that rebuilds live turns it
        off, the one built once does not need to.
        """
        super().__init__(parent)
        self._measure_minimum = measure_minimum
        self._pages: list[QWidget] = []

        # PARENTED AT CONSTRUCTION, never adopted later (owner bug
        # 2026-08-15, "FLASH sa otvaranjem nekog prozora u sredini"): a
        # parentless QWidget IS a top-level window, and
        # `setCurrentRow`/`setCurrentIndex` on one makes it VISIBLE —
        # Windows hands it a real native window at the screen-centre
        # spot until the reparent hides it a repaint later.
        self._nav_list = QListWidget(self)
        self._stack = QStackedWidget(self)

        metrics = self._nav_list.fontMetrics()
        # MEASURED width, never a guessed constant (ITEM CUT, Zubi fix
        # round 2026-08-09: "Themes & Slots" needed 198px while the old
        # fixed 170 offered 156) — the longest section title in the
        # CURRENT font, plus the item/list chrome the theme QSS adds.
        longest = max(
            (metrics.horizontalAdvance(label) for label, _page in sections),
            default=0,
        )
        self._nav_width = max(
            defaults.SETTINGS_NAV_WIDTH_PX,
            longest + defaults.SETTINGS_NAV_CHROME_PX,
        )
        self._nav_list.setFixedWidth(self._nav_width)  # layout-law: exempt - measured from the longest title just above

        for label, page in sections:
            self._nav_list.addItem(label)
            if row_height is not None:
                item = self._nav_list.item(self._nav_list.count() - 1)
                # `QListWidgetItem.sizeHint()` is `QSize(-1, -1)` until
                # something is stamped on it, and an invalid WIDTH makes
                # Qt discard the whole override, height included. So the
                # width half is computed the way the item's own QSS
                # padding does — text width plus the item's horizontal
                # padding — which is always narrower than `nav_width`
                # (the fixed list width ALREADY reserves the list's own
                # border+padding inset on top of that). Handing the full
                # `nav_width` there overran the viewport and cut the
                # sidebar itself (ALG-8, "needs 170px, list offers 156").
                item_width = (metrics.horizontalAdvance(label)
                              + defaults.SETTINGS_NAV_ITEM_CHROME_PX)
                item.setSizeHint(QSize(item_width, row_height))
            self._pages.append(page)
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QFrame.Shape.NoFrame)
            scroll.setWidget(page if page_holder is None else page_holder(page))
            if not horizontal_scroll:
                scroll.setHorizontalScrollBarPolicy(
                    Qt.ScrollBarPolicy.ScrollBarAlwaysOff
                )
            self._stack.addWidget(scroll)

        self._nav_list.currentRowChanged.connect(self._stack.setCurrentIndex)
        self._nav_list.setCurrentRow(0)
        self._stack.setCurrentIndex(0)

        self._body = QHBoxLayout(self)
        self._body.setContentsMargins(0, 0, 0, 0)
        self._body.addWidget(self._nav_list)
        self._body.addWidget(self._stack, stretch=1)

    # ---------------------------------------------------------------- parts

    @property
    def nav_list(self) -> QListWidget:
        """The sidebar itself — a window that wants its own focus policy
        or selection behaviour reaches it here rather than through an
        option nobody else would use."""
        return self._nav_list

    @property
    def stack(self) -> QStackedWidget:
        """The page stack — a window's own audit reads the current page
        through it, exactly as it did before this widget existed."""
        return self._stack

    @property
    def pages(self) -> list[QWidget]:
        return list(self._pages)

    @property
    def nav_width(self) -> int:
        return self._nav_width

    @property
    def spacing(self) -> int:
        """The gap between sidebar and stack — part of the window's own
        width arithmetic, so it is readable from outside."""
        return self._body.spacing()

    def current_row(self) -> int:
        return self._nav_list.currentRow()

    def set_current_row(self, row: int) -> None:
        row = max(0, min(row, self._nav_list.count() - 1))
        self._nav_list.setCurrentRow(row)
        self._stack.setCurrentIndex(row)

    # ------------------------------------------------------------ measuring

    def _hint(self, page: QWidget) -> QSize:
        return (page.minimumSizeHint() if self._measure_minimum
                else page.sizeHint())

    def polish_pages(self) -> None:
        """Let every page and child resolve its QSS before it is
        measured — the theme's paddings are part of the real size
        (measured 20px on the Colors groups), and hints taken
        un-polished under-measure by exactly that much."""
        for page in self._pages:
            page.ensurePolished()
            for child in page.findChildren(QWidget):
                child.ensurePolished()

    def content_width(self) -> int:
        """The widest section's own width — the column the window must
        offer so no section ever needs a horizontal scrollbar."""
        return max((self._hint(page).width() for page in self._pages),
                   default=0)

    def tallest(self) -> int:
        return max((self._hint(page).height() for page in self._pages),
                   default=0)

    def measured_minimum(
        self, extra_width: int, extra_height: int,
        floor: tuple[int, int] = SCREEN_FLOOR,
    ) -> QSize:
        """THE DECLARED MINIMUM, computed from measured content (THE
        SPACE & LEGIBILITY LAW): wide enough for the sidebar plus the
        widest section plus the scrollbar plus the window's own chrome,
        and tall enough for the tallest section — each capped at the
        screen floor, past which the pages scroll lawfully because the
        window is genuinely full."""
        scrollbar = self.style().pixelMetric(
            QStyle.PixelMetric.PM_ScrollBarExtent
        )
        width = self._nav_width + self.content_width() + scrollbar + extra_width
        height = self.tallest() + extra_height
        return QSize(min(width, floor[0]), min(height, floor[1]))

    # --------------------------------------------------------------- scrolls

    def capture_scrolls(self) -> list[tuple[int, int]]:
        """The scroll offset of every page, so a live-pick rebuild can
        put each one back exactly where it stood (owner decree
        2026-08-10: a pick may change the WATCH and nothing else — never
        the section, never the scroll, never the focused side)."""
        offsets: list[tuple[int, int]] = []
        for index in range(self._stack.count()):
            page_scroll = self._stack.widget(index)
            if isinstance(page_scroll, QScrollArea):
                offsets.append((page_scroll.horizontalScrollBar().value(),
                                page_scroll.verticalScrollBar().value()))
            else:
                offsets.append((0, 0))
        return offsets

    def restore_scrolls(self, offsets: list[tuple[int, int]]) -> None:
        for index, (horizontal, vertical) in enumerate(offsets):
            if index >= self._stack.count():
                break
            page_scroll = self._stack.widget(index)
            if not isinstance(page_scroll, QScrollArea):
                continue
            # ONLY a bar that has somewhere to go (proof shot
            # 2026-08-10): writing a value into an empty scrollbar MAKES
            # IT APPEAR — the rebuild grew a horizontal bar with range 0
            # under the page, which is precisely the "a scrollbar while
            # the window still holds unused space" the layout law
            # forbids.
            for bar, value in ((page_scroll.horizontalScrollBar(), horizontal),
                               (page_scroll.verticalScrollBar(), vertical)):
                if bar.maximum() > 0:
                    bar.setValue(value)


def stretched_holder(holder_factory: Callable[[], QWidget]):
    """A `page_holder` that packs the page to the TOP of `holder_factory`'s
    widget and leaves the rest of the height empty below, instead of
    letting the leftover space be wedged between the page's own rows."""
    def hold(page: QWidget) -> QWidget:
        holder = holder_factory()
        layout = QVBoxLayout(holder)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(page)
        layout.addStretch(1)
        return holder
    return hold
