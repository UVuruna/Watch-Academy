"""The Pointer Theme mini window — R5 MENU REWORK item 3B: replaces the
old 1st Slot > Weekday submenu chain (kinship-grouped, deeply nested)
with an image+name gallery. See pointer_theme.md for the interpretation
note on which setting this window edits versus Slot Theme.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout

from app.theme import apply_theme, size_to_screen
from app.weekday_theme_grid import build_weekday_theme_grid
from config import constants, defaults
from config.ui_text import ui


class PointerThemeDialog(QDialog):
    """Non-modal, LIVE-APPLY (see pointer_theme.md): a tile click calls
    `on_pick(theme)` immediately, exactly like the menu chain it
    replaces — there is nothing to commit, so no OK/Cancel."""

    def __init__(
        self, current_theme: str, on_pick, overlay: dict | None = None,
        stay_on_top: bool = False, parent=None,
    ):
        super().__init__(parent)
        self._tr = lambda text: ui(overlay or {}, text)  # noqa: E731
        self._on_pick = on_pick
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
        self._grid = build_weekday_theme_grid(current_theme, on_pick, self._tr)
        self._layout.addWidget(self._grid)
        apply_theme(self)
        size_to_screen(self, 1, 1, defaults.DIALOG_SQUARE_HEIGHT_FRACTION)

    def refresh(self, current_theme: str) -> None:
        """Rebuild the grid so the newly active tile's border moves —
        called by the controller right after a pick applies, keeping
        the window open (owner spec: this is a live picker, not a
        transactional dialog)."""
        self._layout.removeWidget(self._grid)
        self._grid.deleteLater()
        self._grid = build_weekday_theme_grid(
            current_theme, self._on_pick, self._tr
        )
        self._layout.addWidget(self._grid)

    def set_gate(self, available: bool, reason: str) -> None:
        """Live gray-out while the window is already open and the
        condition changes underneath it (Archetype toggled on, the
        Pointer hidden, the 1st Slot turned off) — the primary gate is
        the top-level menu entry itself; this is the belt to that
        suspender."""
        self._grid.setEnabled(available)
        self._gate_label.setText(reason)
        self._gate_label.setVisible(not available)
