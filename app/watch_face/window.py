"""The Watch Face window (R-01, see window.md) — the owner-approved
Watch Face & Settings UI rework: a left `QListWidget` sidebar beside a
right `QStackedWidget` page per section (the same list+stack shape
`app.settings_dialog.dialog.SettingsDialog` already uses), replacing —
over several phases — Design/Pointer Theme/Slot Theme and the Settings
dialog's own Display/Colors groups. Phase ①+② wired five sections;
Phase ③ (see themes.md) replaced the Themes & Slots placeholder with
the real section; Phase ④ (see colors.md/opacity.md) replaces the last
two placeholders — every section is now real, and the sidebar has
carried its final shape since Phase ①. The OLD windows/dialog groups
are untouched until Phase 6 retires them.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QHBoxLayout, QLabel, QListWidget, QStackedWidget, QVBoxLayout,
    QWidget,
)

from app.theme import apply_theme, size_to_screen
from app.watch_face import colors, hands, opacity, pointer, ring, size, themes, umbra_aura
from config import constants, defaults
from config.ui_text import ui

# Section registry: (title, builder). `builder(settings, setters, tr) ->
# QWidget`, or `None` for a not-yet-built placeholder page — a later
# phase replaces a `None` entry with a real module of the same shape.
_SECTIONS = (
    ("Pointer", pointer.build),
    ("Ring", ring.build),
    ("Hands", hands.build),
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
        self._build()
        apply_theme(self)
        size_to_screen(self, 1, 1, defaults.DIALOG_SQUARE_HEIGHT_FRACTION)

    def refresh(self, settings, setters: dict) -> None:
        """Re-supplies the live settings after a pick applies (owner
        spec: a live picker, not a transactional dialog) — called by
        the controller."""
        self._settings = settings
        self._setters = setters
        self._build()

    def _build(self) -> None:
        # KEEP THE SELECTED ROW across live-pick rebuilds — the SAME fix
        # `design_window.DesignDialog._build` carries for its
        # `QTabWidget`: every pick routes through the controller's
        # `refresh()`, which rebuilds this sidebar+stack pair from
        # scratch, and a fresh `QListWidget` always opens at row 0.
        previous = self._nav_list.currentRow() if self._nav_list is not None else 0
        while self._body.count():
            item = self._body.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
        nav_list = QListWidget()
        nav_list.setFixedWidth(defaults.SETTINGS_NAV_WIDTH_PX)
        stack = QStackedWidget()
        for title, builder in _SECTIONS:
            nav_list.addItem(self._tr(title))
            if builder is None:
                page = _placeholder_page(self._tr)
            else:
                page = builder(self._settings, self._setters, self._tr)
            stack.addWidget(page)
        nav_list.currentRowChanged.connect(stack.setCurrentIndex)
        nav_list.setCurrentRow(max(0, min(previous, nav_list.count() - 1)))
        self._body.addWidget(nav_list)
        self._body.addWidget(stack, stretch=1)
        self._nav_list = nav_list
        self._stack = stack
