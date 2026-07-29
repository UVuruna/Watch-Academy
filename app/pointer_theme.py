"""The Pointer Theme mini window — R5 MENU REWORK item 3B: replaces the
old 1st Slot > Weekday submenu chain (kinship-grouped, deeply nested)
with an image+name gallery. See pointer_theme.md for the interpretation
note on which setting this window edits versus Slot Theme.

POINTERS REWORK phase 2 (owner decree 2026-07-29): on the CALENDAR
pointer this window grows a second tab — the MOUNT, the roster riding
its twelve wedges — moved here out of the Design window's Pointer tab.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QLabel, QTabWidget, QVBoxLayout

from app.theme import apply_theme, size_to_screen
from app.weekday_theme_grid import (
    build_calendar_mount_grid,
    build_weekday_theme_grid,
)
from config import constants, defaults
from config.ui_text import ui


class PointerThemeDialog(QDialog):
    """Non-modal, LIVE-APPLY (see pointer_theme.md): a tile click calls
    `on_pick(theme)` immediately, exactly like the menu chain it
    replaces — there is nothing to commit, so no OK/Cancel.

    `current_mount` is the live mount WHILE the Calendar pointer is
    active (the only pointer with wedges to mount a roster on) and None
    on every other pointer — so the window is two tabs on the Calendar
    and the single gallery it has always been elsewhere. It is read on
    every `refresh()` too, so switching pointers under an open window
    grows or drops the tab live."""

    def __init__(
        self, current_theme: str, on_pick, current_mount: str | None = None,
        on_pick_mount=None, overlay: dict | None = None,
        stay_on_top: bool = False, parent=None,
    ):
        super().__init__(parent)
        self._tr = lambda text: ui(overlay or {}, text)  # noqa: E731
        self._on_pick = on_pick
        self._on_pick_mount = on_pick_mount
        self.setWindowTitle(
            f"{constants.APP_NAME} — {self._tr('Pointer Theme')}"
        )
        if stay_on_top:
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self._layout = QVBoxLayout(self)
        self._gate_label = QLabel()
        self._gate_label.setWordWrap(True)
        self._gate_label.setStyleSheet(
            f"color: {defaults.TIME_TRAVEL_WARNING_COLOR};"
        )
        self._gate_label.hide()
        self._layout.addWidget(self._gate_label)
        self._body = self._build(current_theme, current_mount)
        self._layout.addWidget(self._body)
        apply_theme(self)
        size_to_screen(self, 1, 1, defaults.DIALOG_SQUARE_HEIGHT_FRACTION)

    def _build(self, current_theme: str, current_mount: str | None):
        """The window's content: the weekday gallery alone, or — on the
        Calendar — that gallery and the mount gallery as two tabs."""
        weekday = build_weekday_theme_grid(current_theme, self._on_pick, self._tr)
        if current_mount is None or self._on_pick_mount is None:
            return weekday
        tabs = QTabWidget()
        tabs.addTab(weekday, self._tr("Weekday bodies"))
        tabs.addTab(
            build_calendar_mount_grid(
                current_mount, self._on_pick_mount, self._tr
            ),
            self._tr("Calendar mount"),
        )
        return tabs

    def refresh(self, current_theme: str, current_mount: str | None = None) -> None:
        """Rebuild the content so the newly active tile's border moves —
        called by the controller right after a pick applies, keeping
        the window open (owner spec: this is a live picker, not a
        transactional dialog)."""
        self._layout.removeWidget(self._body)
        # `setParent(None)` BEFORE `deleteLater()`: deletion is deferred
        # to the event loop, so without this the replaced widget stays a
        # live child of the dialog and anything walking the tree still
        # finds the OLD content beside the new.
        self._body.setParent(None)
        self._body.deleteLater()
        self._body = self._build(current_theme, current_mount)
        self._layout.addWidget(self._body)

    def set_gate(self, available: bool, reason: str) -> None:
        """Live gray-out while the window is already open and the
        condition changes underneath it (Archetype toggled on, the
        Pointer hidden, the 1st Slot turned off) — the primary gate is
        the top-level menu entry itself; this is the belt to that
        suspender."""
        self._body.setEnabled(available)
        self._gate_label.setText(reason)
        self._gate_label.setVisible(not available)
