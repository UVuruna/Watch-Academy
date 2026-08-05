"""The SHORTCUTS window (R-37): a read-only reference dialog listing
EVERY keyboard shortcut the dial answers to — enumerated straight off
`config.shortcuts.SHORTCUTS`, the one table every real key dispatch
(`app.widget.ClockWidget.keyPressEvent`) also reads (Rule #19: never a
hand-written copy that can drift from what actually fires).
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from app.theme import apply_theme
from app.ui_style import style_button
from config import constants, defaults, shortcuts
from config.ui_text import ui


class ShortcutsDialog(QDialog):
    """A quiet, modal table: Shortcut / Action — one row per
    `shortcuts.SHORTCUTS` entry, in the table's own curated order (the
    config module's comments already group them Ring/Slots/Fast Travel/
    Locations; re-sorting alphabetically would scatter that story)."""

    COLUMNS = ("Shortcut", "Action")

    def __init__(self, overlay: dict | None = None, parent=None):
        super().__init__(parent)
        tr = self._tr = lambda text: ui(overlay or {}, text)
        self.setWindowTitle(f"{constants.APP_NAME} — {tr('Shortcuts')}")
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self.resize(
            defaults.SHORTCUTS_WINDOW_WIDTH_PX, defaults.SHORTCUTS_WINDOW_HEIGHT_PX
        )

        column = QVBoxLayout(self)
        self._table = QTableWidget(len(shortcuts.SHORTCUTS), len(self.COLUMNS))
        self._table.setHorizontalHeaderLabels([tr(name) for name in self.COLUMNS])
        self._table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        for row, (action_id, _key, _modifiers, description) in enumerate(
            shortcuts.SHORTCUTS
        ):
            combo = QTableWidgetItem(shortcuts.shortcut_display(action_id))
            combo.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 0, combo)
            self._table.setItem(row, 1, QTableWidgetItem(tr(description)))
        self._table.resizeColumnToContents(0)
        column.addWidget(self._table, stretch=1)

        row = QHBoxLayout()
        row.addStretch(1)
        close = QPushButton(tr("Close"))
        style_button(close, "neutral", small=True)
        close.clicked.connect(self.accept)
        row.addWidget(close)
        column.addLayout(row)

        apply_theme(self)
