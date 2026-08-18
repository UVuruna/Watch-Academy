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

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from app import rebuild
from app.dialog_base import AcademyDialog
from app.section_host import SectionHost, stretched_holder
from app.theme import apply_theme, size_to_screen
from app.watch_face import (
    bodies, colors, numerals, opacity, pointer, ring, size, themes,
)
from app.watch_face import section_reset
from app.watch_face.widgets import FlowContent
from config import defaults, encyclopedia_ui

# Section registry: (title, builder). `builder(settings, setters, tr) ->
# QWidget`, or `None` for a not-yet-built placeholder page — a later
# phase replaces a `None` entry with a real module of the same shape.
# THE 2026-08-14 REORGANIZATION (owner ballot verdicts 5A/5B/5D):
# Umbra & Aura dissolved into Colors (5A — its form/contrast galleries
# sit beside Umbra coloring), the pointer hue chips moved from Colors
# to Pointer (5B), and the over-long Hands & Bodies split its Eclipses
# + Stations half into its own page (5D). Nine entries stay nine.
_SECTIONS = (
    ("Pointer", pointer.build),
    ("Ring", ring.build),
    ("Numerals", numerals.build),
    ("Hands & Bodies", bodies.build),
    ("Eclipses & Stations", bodies.build_eclipses),
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


class WatchFaceDialog(AcademyDialog):
    """Non-modal, LIVE-APPLY (see window.md): every section's pick calls
    its setter immediately — there is nothing to commit, so no
    OK/Cancel."""

    def __init__(
        self, settings, setters: dict, overlay: dict | None = None,
        stay_on_top: bool = False, parent=None,
    ):
        super().__init__("Watch Face", overlay, stay_on_top, parent)
        self._settings = settings
        self._setters = setters
        self._host: SectionHost | None = None
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

    # THE WINDOW'S OWN PARTS. The sidebar and the stack are what this
    # window's tests and the runtime layout audit have always asked it
    # for; `SectionHost` holds them now, so these two read through. They
    # are accessors, not a compatibility wrapper: the audit walks a
    # WINDOW's sections, and it should not have to know which widget
    # class the window built them with.
    @property
    def _nav_list(self):
        return None if self._host is None else self._host.nav_list

    @property
    def _stack(self):
        return None if self._host is None else self._host.stack

    def refresh(self, settings, setters: dict) -> None:
        """Re-supplies the live settings after a pick applies (owner
        spec: a live picker, not a transactional dialog) — called by
        the controller."""
        self._settings = settings
        self._setters = setters
        self._build()

    def _build(self) -> None:
        # KEEP THE SELECTED ROW and every page's scroll across live-pick
        # rebuilds (owner decree 2026-08-10: a pick may change the WATCH
        # and nothing else): every pick routes through the controller's
        # `refresh()`, which rebuilds this host from scratch, and a fresh
        # `QListWidget` always opens at row 0.
        previous = self._host.current_row() if self._host is not None else 0
        scrolls = self._host.capture_scrolls() if self._host is not None else []
        # THE OLD HOST IS VISIBLE when this reaches it, and a visible
        # child handed `setParent(None)` stops being a child and becomes
        # a real top-level window at the default screen-centre spot —
        # with its full old contents — until `deleteLater` is reached a
        # repaint later (owner bug 2026-08-15, reported AGAIN 2026-08-16;
        # measured with a global Show/PlatformSurface spy, silent once
        # `rebuild.discard` hides first).
        rebuild.clear_layout(self._body)
        sections: list[tuple[str, QWidget]] = []
        for title, builder in _SECTIONS:
            text = self._tr(title)
            if builder is None:
                page = _placeholder_page(self._tr)
            else:
                # THE PER-SECTION RESET (owner order 2026-08-15) is wired
                # HERE, once, for all nine pages — no section module
                # declares anything. The recording wrapper notes which
                # setters the builder asked for while it built, and that
                # IS the page's own list of settings; see
                # section_reset.py for why a declared list was refused.
                recording = section_reset.RecordingSetters(self._setters)
                page = builder(self._settings, recording, self._tr)
                reset = section_reset.reset_row(
                    recording.asked, self._settings, self._setters, self._tr,
                )
                if reset is not None:
                    page_layout = page.layout()
                    if page_layout is not None:
                        page_layout.addWidget(reset)
            sections.append((text, page))
        # NAV PILL ROW HEIGHT (2026-08-13): QListWidget's own row-layout
        # pass does not always match the delegate's styled sizeHint once
        # QSS padding/margin is involved — left to itself the view spaced
        # rows narrower than the pill it painted, so the SELECTED item's
        # pill overlapped the row above and below (owner-reported text
        # clipping on "Ring" / "Hands & Bodies" around a selected
        # "Numerals"). The reserved row and the painted pill must be one
        # number, computed from the same constants the QSS pill uses.
        metrics = self.fontMetrics()
        row_height = (
            metrics.height()
            + 2 * encyclopedia_ui.THEME_NAV_ITEM_PADDING_V_PX
            + 2 * encyclopedia_ui.THEME_NAV_ITEM_MARGIN_V_PX
        )
        host = SectionHost(
            sections,
            parent=self,
            measure_minimum=True,
            row_height=row_height,
            # A plain holder under `widgetResizable` sizes the page from
            # the width-independent minimum hint, which drops the height
            # a flow gallery only knows once it has a width — the Ring
            # page's "Inner (minute track)" group was handed 375px
            # against its own 388px minimum and lost its bottom margin
            # (measured 2026-08-13 on the owner's live profile).
            # `FlowContent` is exactly the widget that answers this.
            page_holder=stretched_holder(FlowContent),
            horizontal_scroll=False,
        )
        # The sidebar must NEVER steal the caret from the pick the user
        # just made (owner decree 2026-08-10 — "odvede me na levu
        # stranu"): the list is reachable by mouse and by Tab, but a
        # rebuilt list never grabs focus on its own.
        host.nav_list.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        host.set_current_row(previous)
        self._body.addWidget(host, stretch=1)
        self._host = host
        # NO PINNED WIDTH (owner decree 2026-08-14, superseding the fixed
        # column of 2026-08-06): the pages used to be capped with
        # setMaximumWidth() to the widest section's MINIMUM hint, so even
        # an ultra-wide window rendered every gallery in the same narrow
        # column — the eclipse gallery wrapped into two rows while half
        # the window stood empty. The owner's ruling: minimums that keep
        # text legible are lawful, a hard-coded width never is. Content
        # now follows the real viewport width; the flow galleries absorb
        # it by refilling their rows. The measured column survives only
        # as the MINIMUM the window must offer (no horizontal scrollbar
        # by construction), taken from POLISHED hints.
        host.polish_pages()
        self._declare_minimum(host)
        # TWICE, and that is not belt-and-braces: a scrollbar's range is
        # still 0 until the layout has run, so the immediate call clamps
        # to the top on a page whose geometry is not settled yet. The
        # queued call lands after that layout pass, with the real range.
        host.restore_scrolls(scrolls)
        QTimer.singleShot(0, lambda: host.restore_scrolls(scrolls))

    def _declare_minimum(self, host: SectionHost) -> None:
        """The window's own chrome around the host's measured content —
        the sidebar/column/scrollbar arithmetic and the screen floor live
        in [Section Host](../__about/section_host.md)."""
        margins = self._layout.contentsMargins()
        self.setMinimumSize(host.measured_minimum(
            margins.left() + margins.right() + host.spacing,
            margins.top() + margins.bottom(),
        ))
