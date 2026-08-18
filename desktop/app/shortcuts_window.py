"""The SHORTCUTS window (R-37): a read-only reference dialog listing
EVERY keyboard shortcut the dial answers to — enumerated straight off
`config.shortcuts.SHORTCUTS`, the one table every real key dispatch
(`app.widget.ClockWidget.keyPressEvent`) also reads (Rule #19: never a
hand-written copy that can drift from what actually fires).
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QHeaderView, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout

from app.dialog_base import AcademyDialog
from app.theme import apply_theme
from app.ui_style import style_button
from config import defaults, shortcuts


class ShortcutsDialog(AcademyDialog):
    """A quiet, modal table: Shortcut / Action — one row per
    `shortcuts.SHORTCUTS` entry, in the table's own curated order (the
    config module's comments already group them Ring/Slots/Fast Travel/
    Locations; re-sorting alphabetically would scatter that story)."""

    COLUMNS = ("Shortcut", "Action")

    def __init__(self, overlay: dict | None = None, parent=None):
        super().__init__("Shortcuts", overlay, stay_on_top=True,
                         parent=parent)
        tr = self._tr
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
        # THE SPACE & LEGIBILITY LAW: minimums COMPUTED from the table's
        # own content (after the theme, whose paddings are part of the
        # real size) — wide enough that the stretched Action column never
        # squeezes below its longest row, tall enough for the whole list
        # up to the screen floor minus this dialog's own chrome, where
        # scrolling lawfully takes over (the window is genuinely full).
        header = self._table.horizontalHeader()
        needed = sum(
            max(self._table.sizeHintForColumn(index),
                header.sectionSizeHint(index))
            for index in range(self._table.columnCount())
        )
        table_chrome = (2 * self._table.frameWidth()
                        + self._table.verticalScrollBar().sizeHint().width())
        self._table.setMinimumWidth(needed + table_chrome)
        rows_height = sum(self._table.sizeHintForRow(index)
                          for index in range(self._table.rowCount()))
        full_height = (header.sizeHint().height() + rows_height
                       + 2 * self._table.frameWidth())
        margins = column.contentsMargins()
        dialog_chrome = (margins.top() + margins.bottom() + column.spacing()
                         + close.sizeHint().height())
        self._table.setMinimumHeight(min(full_height, 720 - dialog_chrome))
