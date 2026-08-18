"""THE OBSERVATORY'S PANELS — what sits BESIDE a chart.

The "About this chart" info box, the `ChartPane` that pairs a plot with
it, and `EnlargeDialog`, the full-screen target a chart is reparented
INTO and back out of.

Split out of a 1,697-line `app/observatory.py` on 2026-08-18 (R12 of the
OOP audit). These are the widgets that frame a chart without being one.

Layer: app. Documentation: __about/panels.md.
"""

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget,
)
from app.observatory.charts import ChartBase
from app.theme import apply_theme
from app.ui_style import style_button
from config import constants, defaults, encyclopedia_ui, palette


def build_info_panel(
    caption: str | None, info_rows: list[tuple[str, str, str]] | None, tr,
) -> QWidget:
    """Item 2 — the Enlarge dialog's collapsible right-side info column:
    this chart's own description (the SAME text a compact-view caption
    already carries, no second competing text to keep honest) plus, for
    the eclipse chart only, one row per eclipse KIND actually present —
    a color swatch matching the chart's own dots and a one-line meaning
    (owner: "sa strane tekst o svakoj ukratko opisano... legenda svaka
    da bude obojana svojom bojom")."""
    panel = QWidget()
    # Scoped to the panel itself — an unscoped rule cascades to every
    # child QLabel (the encyclopedia Card's ALG-6 lesson, same round).
    panel.setObjectName("aboutChartPanel")
    panel.setStyleSheet(
        "QWidget#aboutChartPanel {"
        f"background: {palette.THEME_COLORS['surface_1']};"
        f"border-radius: {encyclopedia_ui.THEME_RADIUS_CARD_PX}px; }}"
    )
    layout = QVBoxLayout(panel)
    layout.setContentsMargins(*[defaults.INFO_PANEL_MARGIN_PX] * 4)
    layout.setSpacing(defaults.GUIDE_SPACING_PX)
    layout.addWidget(QLabel(f"<b>{tr('About this chart')}</b>"))
    if caption:
        text = QLabel(caption)
        text.setWordWrap(True)
        layout.addWidget(text)
    for label, color, description in info_rows or []:
        row = QHBoxLayout()
        chip = QLabel()
        chip.setFixedSize(12, 12)  # layout-law: exempt - decorative 12px legend color chip, carries no text
        chip.setStyleSheet(f"background: {color}; border-radius: 6px; margin-top: 3px;")
        row.addWidget(chip, alignment=Qt.AlignmentFlag.AlignTop)
        column = QVBoxLayout()
        column.setSpacing(0)
        name = QLabel(f"<b>{label}</b>")
        column.addWidget(name)
        description_label = QLabel(description)
        description_label.setWordWrap(True)
        description_label.setStyleSheet(f"color: {palette.OBSERVATORY_MUTED_COLOR};")
        column.addWidget(description_label)
        row.addLayout(column, stretch=1)
        layout.addLayout(row)
    layout.addStretch(1)
    return panel


class EnlargeDialog(QDialog):
    """Fix round G, Task 3 — the "Enlarge" target: hosts the caller's
    chart panel (reparented in on open, back out on close by
    `ObservatoryDialog._open_enlarged`) so zoom/pan/checkbox state
    carries over for free — there is only ever one instance of these
    widgets, so there is nothing to keep in sync. Adds an EXTENDED
    legend (every series, its color chip and its current value,
    refreshed on a light timer as the user hovers/zooms) and, Fix round
    R1a, a collapsible INFO panel (Item 2) beside the chart.

    Ownership (the crash — 13 hits in the owner's crash.log): this
    dialog does NOT set WA_DeleteOnClose. That flag used to queue the
    dialog's own C++ destruction via `deleteLater()`; since `panel` was
    reparented onto it as a REAL Qt child, the queued deletion could
    (and empirically did) destroy `panel` too before
    `ObservatoryDialog._open_enlarged` reinserted it into the splitter —
    "Internal C++ object already deleted", and the chart never came
    back. Ownership is explicit instead: the caller reparents `panel`
    back out FIRST after `exec()` returns, THEN calls `deleteLater()` on
    this dialog itself — deletion can never race the handoff."""

    def __init__(
        self, panel: QWidget, chart: ChartBase, title: str,
        caption: str | None, tr, info_rows: list[tuple[str, str, str]] | None = None,
        parent=None,
    ):
        super().__init__(parent)
        self._chart = chart
        self._tr = tr
        self.setWindowTitle(f"{constants.APP_NAME} — {title}")
        self.setWindowFlag(Qt.WindowType.WindowMaximizeButtonHint, True)
        self.setWindowFlag(Qt.WindowType.WindowMinimizeButtonHint, True)

        outer = QVBoxLayout(self)
        # Item 3 (owner screenshot "Title 2 puta") — this centered
        # heading is now the dialog's ONLY in-page title; the panel's
        # own title label (needed when it lives in the main splitter,
        # left-aligned above its filter row) is hidden for the duration
        # of the reparent and restored by `_open_enlarged` on the way
        # back out.
        header = QLabel(f"<b>{title}</b>")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet(f"font-size: {defaults.GUIDE_SUBTITLE_PX}px;")
        outer.addWidget(header)
        panel.title_label.setVisible(False)

        content = QHBoxLayout()
        outer.addLayout(content, stretch=1)

        chart_column = QVBoxLayout()
        panel.setParent(self)
        chart_column.addWidget(panel, stretch=1)
        self._legend_row = QHBoxLayout()
        chart_column.addLayout(self._legend_row)
        content.addLayout(chart_column, stretch=1)

        self._info_panel = build_info_panel(caption, info_rows, tr)
        self._info_panel.setFixedWidth(defaults.OBSERVATORY_INFO_PANEL_WIDTH_PX)  # layout-law: exempt - fixed info column by design; the audit's elision check verifies its content fits
        content.addWidget(self._info_panel)

        self._refresh_legend()
        # A light poll (not a hot path — a handful of small labels) so
        # the "current value" readout follows hover/zoom/pan without
        # threading the shared chart base with new signal plumbing.
        self._legend_timer = QTimer(self)
        self._legend_timer.timeout.connect(self._refresh_legend)
        self._legend_timer.start(200)
        self.finished.connect(self._legend_timer.stop)

        buttons = QHBoxLayout()
        self._info_toggle = QPushButton(tr("Hide info"))
        style_button(self._info_toggle, "neutral", small=True)
        self._info_toggle.clicked.connect(self._toggle_info)
        buttons.addWidget(self._info_toggle)
        buttons.addStretch(1)
        close = QPushButton(tr("Close"))
        style_button(close, "neutral", small=True)
        close.clicked.connect(self.accept)
        buttons.addWidget(close)
        outer.addLayout(buttons)

        apply_theme(self)
        self._size_to_owner_spec()
        self.show()

    def _size_to_owner_spec(self) -> None:
        """Item 1 (owner: ASPECT 16:9, 50% of screen HEIGHT = 25% of
        screen area) — replaces the old `showMaximized()`. Still a
        normal resizable/maximizable window (the hints above), just not
        maximized on open."""
        screen = self.screen() or QGuiApplication.primaryScreen()
        available = screen.availableGeometry()
        height = int(available.height() * defaults.OBSERVATORY_ENLARGE_HEIGHT_FRACTION)
        width = int(
            height * defaults.OBSERVATORY_ENLARGE_ASPECT_W
            / defaults.OBSERVATORY_ENLARGE_ASPECT_H
        )
        self.resize(width, height)
        self.move(available.center() - self.rect().center())

    def _toggle_info(self) -> None:
        showing = not self._info_panel.isVisible()
        self._info_panel.setVisible(showing)
        self._info_toggle.setText(
            self._tr("Hide info") if showing else self._tr("Show info")
        )

    def _refresh_legend(self) -> None:
        while self._legend_row.count():
            item = self._legend_row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        values = self._chart._legend_values()
        for label, color in self._chart._legend():
            chip = QLabel()
            chip.setFixedSize(12, 12)  # layout-law: exempt - decorative 12px legend color chip, carries no text
            chip.setStyleSheet(f"background: {color}; border-radius: 6px;")
            self._legend_row.addWidget(chip)
            value = values.get(label)
            text = QLabel(f"{label}: {value}" if value is not None else label)
            text.setStyleSheet(
                f"color: {palette.OBSERVATORY_INK_COLOR}; font-weight: 600;"
            )
            self._legend_row.addWidget(text)
            self._legend_row.addSpacing(14)
        self._legend_row.addStretch(1)


class ChartPane(QWidget):
    """A splitter pane whose minimum height follows its own WRAPPED
    caption: QSplitter sizes panes off `minimumSizeHint`, which ignores
    heightForWidth, so a pane with a wrapping caption could be squeezed
    until the chart painted straight over the caption (audit finding
    2026-08-06 — 11px of chart on the caption's pixels)."""

    def minimumSizeHint(self):          # noqa: N802 — Qt override
        hint = super().minimumSizeHint()
        layout = self.layout()
        if layout is not None and layout.hasHeightForWidth():
            width = self.width() or hint.width()
            hint.setHeight(max(hint.height(), layout.heightForWidth(width)))
        return hint
