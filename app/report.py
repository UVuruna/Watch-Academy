"""The hidden efficiency REPORT (owner 2026-07-15).

Unlocked sessions get a 📊 Report entry above Exit: every measured
functionality since the installation — call counts, execution-time
statistics (readable units, the exact numbers in a sortable table),
a top-total bar chart and the selected function's recent-durations
sparkline. QPainter draws both charts; the dialog reads profiling
snapshots once per second.
"""

import csv

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.ui_style import style_button
from config import constants, defaults, profiling
from config.ui_text import ui


def format_ns(ns: int) -> str:
    """Readable duration (owner spec: µs or ms as fits, two decimals
    for small numbers, whole ns need none)."""
    if ns < 1_000:
        return f"{ns} ns"
    if ns < 1_000_000:
        return f"{ns / 1_000:.2f} µs"
    if ns < 1_000_000_000:
        return f"{ns / 1_000_000:.2f} ms"
    return f"{ns / 1_000_000_000:.3f} s"


class _NumericItem(QTableWidgetItem):
    """Sorts by the raw nanosecond value carried in UserRole while
    DISPLAYING the readable unit."""

    def __lt__(self, other) -> bool:
        return (
            self.data(Qt.ItemDataRole.UserRole)
            < other.data(Qt.ItemDataRole.UserRole)
        )


class _BarChart(QWidget):
    """Top functions by TOTAL time — horizontal bars, one quiet gold
    hue (single series: the labels carry identity, the values sit at
    the bar ends; the table below holds the exact numbers)."""

    def __init__(self):
        super().__init__()
        self._rows: list[tuple[str, int]] = []
        self._selected: str | None = None
        self.setMinimumHeight(defaults.REPORT_CHART_HEIGHT_PX)

    def set_data(self, rows: list[tuple[str, int]], selected: str | None):
        self._rows = rows
        self._selected = selected
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802 — Qt override
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(defaults.REPORT_SURFACE_COLOR))
        if not self._rows:
            painter.setPen(QColor(defaults.REPORT_MUTED_COLOR))
            painter.drawText(
                self.rect(), Qt.AlignmentFlag.AlignCenter,
                self._empty_text,
            )
            painter.end()
            return
        top = max(total for _, total in self._rows)
        label_w = 150
        value_w = 78
        gap = 2
        row_h = max(
            12, min(24, (self.height() - 8) // len(self._rows))
        )
        font = painter.font()
        font.setPixelSize(11)
        painter.setFont(font)
        for index, (name, total) in enumerate(self._rows):
            y = 4 + index * row_h
            bar_span = self.width() - label_w - value_w - 16
            width = max(3, round(bar_span * total / top))
            painter.setPen(QColor(defaults.REPORT_INK_COLOR))
            painter.drawText(
                4, y, label_w, row_h - gap,
                Qt.AlignmentFlag.AlignVCenter
                | Qt.AlignmentFlag.AlignRight,
                name,
            )
            color = (
                defaults.REPORT_MARK_COLOR
                if self._selected in (None, name)
                else defaults.REPORT_MARK_DIM_COLOR
            )
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(color))
            painter.drawRoundedRect(
                label_w + 8, y + 1, width, row_h - gap - 2, 2, 2
            )
            painter.setPen(QColor(defaults.REPORT_MUTED_COLOR))
            painter.drawText(
                label_w + 12 + width, y, value_w, row_h - gap,
                Qt.AlignmentFlag.AlignVCenter,
                format_ns(total),
            )
        painter.end()

    _empty_text = ""


class _Sparkline(QWidget):
    """The selected function's recent durations (this session) — a
    2 px line in the same hue, min/max/last read-outs in muted ink."""

    def __init__(self):
        super().__init__()
        self._name: str | None = None
        self._values: list[int] = []
        self.setMinimumHeight(defaults.REPORT_CHART_HEIGHT_PX // 2)

    def set_data(self, name: str | None, values: list[int]):
        self._name = name
        self._values = values
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802 — Qt override
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(defaults.REPORT_SURFACE_COLOR))
        font = painter.font()
        font.setPixelSize(11)
        painter.setFont(font)
        if self._name is None or len(self._values) < 2:
            painter.setPen(QColor(defaults.REPORT_MUTED_COLOR))
            painter.drawText(
                self.rect(), Qt.AlignmentFlag.AlignCenter,
                self._empty_text,
            )
            painter.end()
            return
        painter.setPen(QColor(defaults.REPORT_INK_COLOR))
        painter.drawText(
            8, 4, self.width() - 16, 14,
            Qt.AlignmentFlag.AlignLeft, self._name,
        )
        low, high = min(self._values), max(self._values)
        span = max(1, high - low)
        left, right = 8, self.width() - 8
        top, bottom = 22, self.height() - 18
        step = (right - left) / max(1, len(self._values) - 1)
        pen = QPen(QColor(defaults.REPORT_MARK_COLOR), 2)
        painter.setPen(pen)
        points = [
            (
                left + index * step,
                bottom - (value - low) / span * (bottom - top),
            )
            for index, value in enumerate(self._values)
        ]
        for (x1, y1), (x2, y2) in zip(points, points[1:]):
            painter.drawLine(round(x1), round(y1), round(x2), round(y2))
        painter.setPen(QColor(defaults.REPORT_MUTED_COLOR))
        painter.drawText(
            8, self.height() - 15, self.width() - 16, 14,
            Qt.AlignmentFlag.AlignLeft,
            f"min {format_ns(low)}   max {format_ns(high)}   "
            f"last {format_ns(self._values[-1])}",
        )
        painter.end()

    _empty_text = ""


class ReportDialog(QDialog):
    COLUMNS = ("Function", "Calls", "Average", "Min", "Max", "Total", "Last")

    def __init__(self, overlay: dict | None = None, parent=None):
        super().__init__(parent)
        tr = self._tr = lambda text: ui(overlay or {}, text)
        self.setWindowTitle(f"{constants.APP_NAME} — {tr('Report')}")
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self.resize(760, 620)

        column = QVBoxLayout(self)
        self._chart = _BarChart()
        self._chart._empty_text = tr(
            "No measurements yet — use the clock a little."
        )
        column.addWidget(QLabel(f"<b>{tr('Top functions by total time')}</b>"))
        column.addWidget(self._chart)
        self._spark = _Sparkline()
        self._spark._empty_text = tr(
            "Select a row to watch its recent durations."
        )
        column.addWidget(self._spark)

        self._table = QTableWidget(0, len(self.COLUMNS))
        self._table.setHorizontalHeaderLabels(
            [tr(name) for name in self.COLUMNS]
        )
        self._table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self._table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self._table.setSortingEnabled(True)
        self._table.itemSelectionChanged.connect(self._refresh_charts)
        column.addWidget(self._table, stretch=1)

        row = QHBoxLayout()
        reset = QPushButton(tr("Reset"))
        style_button(reset, "previous", small=True)
        reset.clicked.connect(self._reset)
        download = QPushButton(tr("Download"))
        style_button(download, "download", small=True)
        download.clicked.connect(self._download)
        row.addWidget(reset)
        row.addWidget(download)
        row.addStretch(1)
        close = QPushButton(tr("Close"))
        style_button(close, "neutral", small=True)
        close.clicked.connect(self.accept)
        row.addWidget(close)
        column.addLayout(row)

        self._snapshot: dict[str, dict] = {}
        self._refresh()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh)
        self._timer.start(defaults.REPORT_REFRESH_MS)

    # --- data -----------------------------------------------------------------

    def _selected_name(self) -> str | None:
        items = self._table.selectedItems()
        return items[0].text() if items else None

    def _refresh(self) -> None:
        self._snapshot = profiling.snapshot()
        selected = self._selected_name()
        header = self._table.horizontalHeader()
        sort_column = header.sortIndicatorSection()
        sort_order = header.sortIndicatorOrder()
        self._table.setSortingEnabled(False)
        self._table.setRowCount(len(self._snapshot))
        for row, (name, entry) in enumerate(sorted(self._snapshot.items())):
            first = QTableWidgetItem(name)
            self._table.setItem(row, 0, first)
            calls = _NumericItem(f"{entry['count']:,}")
            calls.setData(Qt.ItemDataRole.UserRole, entry["count"])
            self._table.setItem(row, 1, calls)
            average = entry["total_ns"] // max(1, entry["count"])
            for column, value in (
                (2, average), (3, entry["min_ns"]), (4, entry["max_ns"]),
                (5, entry["total_ns"]), (6, entry["last_ns"]),
            ):
                item = _NumericItem(format_ns(value))
                item.setData(Qt.ItemDataRole.UserRole, value)
                self._table.setItem(row, column, item)
            if name == selected:
                self._table.selectRow(row)
        self._table.setSortingEnabled(True)
        self._table.sortItems(sort_column, sort_order)
        self._refresh_charts()

    def _refresh_charts(self) -> None:
        selected = self._selected_name()
        top = sorted(
            (
                (name, entry["total_ns"])
                for name, entry in self._snapshot.items()
            ),
            key=lambda pair: pair[1],
            reverse=True,
        )[: defaults.REPORT_BAR_TOP_N]
        self._chart.set_data(top, selected)
        if selected in self._snapshot:
            self._spark.set_data(
                selected, self._snapshot[selected]["recent"]
            )
        else:
            self._spark.set_data(None, [])

    # --- actions --------------------------------------------------------------

    def _reset(self) -> None:
        profiling.reset()
        self._refresh()

    def _download(self) -> None:
        target, _ = QFileDialog.getSaveFileName(
            self, self._tr("Download"), "domy_report.csv",
            "CSV (*.csv)",
        )
        if not target:
            return
        with open(target, "w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow([
                "function", "calls", "average_ns", "min_ns",
                "max_ns", "total_ns", "last_ns",
            ])
            for name, entry in sorted(self._snapshot.items()):
                writer.writerow([
                    name, entry["count"],
                    entry["total_ns"] // max(1, entry["count"]),
                    entry["min_ns"], entry["max_ns"],
                    entry["total_ns"], entry["last_ns"],
                ])
