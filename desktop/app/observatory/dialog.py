"""THE OBSERVATORY WINDOW — the shell the charts live in.

`ObservatoryDialog`: the splitter, the chart roster, the controls, the
Enlarge route, and the session-only splitter memory. Everything that
knows a WINDOW is open.

Split out of a 1,697-line `app/observatory.py` on 2026-08-18 (R12 of the
OOP audit); the plots are in [charts.py](charts.py) and the boxes beside
them in [panels.py](panels.py).

Layer: app. Documentation: __about/dialog.md · __flow/dialog.md.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QFrame, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QSplitter, QStyle, QVBoxLayout, QWidget,
)

from app.dialog_base import AcademyDialog
from app.observatory.charts import (
    ChartBase, DayLengthChart, EclipseChart, LineChart, year_label,
)
from app.observatory.panels import ChartPane, EnlargeDialog
from app.theme import apply_theme, size_to_screen
from app.ui_style import style_button, uniform_width
from config import constants, defaults, encyclopedia_ui, palette
from core.deep_time import julian_day_of, real_year
from core.sun import day_length_curve
from data.observatory import shared_observatory


# Fix round G, Task 2: the last-used per-chart splitter sizes for THIS
# APP RUN only — a plain module-level cache, cleared on restart, since
# there is no existing settings key for this dialog's own geometry to
# piggyback on (it isn't persisted across opens either).
_last_splitter_sizes: list[int] | None = None


class ObservatoryDialog(AcademyDialog):
    def __init__(
        self, now, observer, tz, cycles=0, deep=None, translations=None,
        stay_on_top: bool = False,
    ):
        super().__init__("Observatory", translations, stay_on_top)
        self.setWindowFlag(Qt.WindowType.WindowMaximizeButtonHint, True)
        self.setWindowFlag(Qt.WindowType.WindowMinimizeButtonHint, True)
        # NON-MODAL lifecycle (ITEM 1, R4 owner instruction batch
        # 2026-07-20): the controller `.show()`s this dialog instead of
        # `.exec()`ing it — the dial stays interactive while it is
        # open. The controller keeps the ONE live instance as an
        # attribute and clears it on this dialog's `finished` signal;
        # WA_DeleteOnClose tears the C++ object down the moment the
        # window closes. Unrelated to `EnlargeDialog`'s own explicit
        # ownership (that one still needs it BECAUSE it reparents a
        # REAL child, `panel`, borrowed from THIS dialog's splitter —
        # see its docstring); this outer dialog reparents nothing INTO
        # itself, so the plain Qt idiom is safe here.
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        # OPENING SIZE (owner DESIGN #1): A4 portrait at 80% of the
        # screen's available height.
        size_to_screen(
            self, defaults.DIALOG_A4_ASPECT_W, defaults.DIALOG_A4_ASPECT_H,
            defaults.DIALOG_A4_HEIGHT_FRACTION,
        )

        data = shared_observatory()
        column = QVBoxLayout(self)

        astro_year = real_year(now.year, cycles)
        anno = astro_year + constants.ANNO_LUCIS_OFFSET
        header = QLabel(
            f"<b>{self._tr('Observatory')}</b> — "
            f"{year_label(astro_year)} · {self._tr('A.L.')} {anno:,}"
        )
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        column.addWidget(header)

        # Fix round G, Task 2 (owner: every chart stretches vertically):
        # a QSplitter over the chart column, one panel (title + filter
        # row + chart [+ caption]) per chart — the natural Qt shape for
        # a "drag to resize" affordance, and it plays fine with the
        # surrounding QScrollArea (the splitter's minimumSizeHint is the
        # sum of its panels', so once that exceeds the viewport the
        # scroll area shows its bar exactly as the old plain VBox did;
        # verified with an offscreen render at a small dialog size).
        self._splitter = QSplitter(Qt.Orientation.Vertical)
        self._splitter.setChildrenCollapsible(False)

        # 1 — the season-duration oscillations with the checkbox filter.
        series = data.season_series()
        first, last = data.season_span()
        span_label = f"{year_label(first)}–{year_label(last)}"
        self._season_chart = LineChart(
            self._tr("year"), self._tr("days"), y_fmt=lambda v: f"{v:.1f}",
            # Task 2: the crosshair also reports the light/dark delta,
            # in whichever unit the switch picks — the series' own axis
            # (raw durations) always stays in days.
            diff_pair=("light", "dark"),
        )
        self._season_chart.set_series([
            {"key": key, "label": self._tr(key.capitalize()),
             "color": palette.OBSERVATORY_SERIES_COLORS[key],
             "xs": series["years"], "ys": series[key]}
            for key in ("spring", "summer", "autumn", "winter", "light", "dark")
        ])
        # Start with only the two halves lit (the owner's own graph) so
        # the busy four-season lines do not crowd the first view.
        for key in ("spring", "summer", "autumn", "winter"):
            self._season_chart.set_visible(key, False)
        # Item 2 — an honest, data-derived caption (span read straight
        # off the bundle, never a number that could drift from it).
        season_caption = self._tr(
            "The four northern astronomical seasons' length in days, "
            "{span}. Toggle any line above; Light and Dark are the "
            "derived half-year sums (Spring+Summer, Autumn+Winter)."
        ).format(span=span_label)
        self._add_panel(
            self._tr("Season durations"), self._season_chart,
            filter_row=self._season_filter(), caption=season_caption,
        )

        # 2 — the light − dark envelope with the eras and every peak.
        eras = data.season_eras()
        light_minus_dark = [
            round(light - dark, 4)
            for light, dark in zip(series["light"], series["dark"])
        ]
        envelope = LineChart(
            self._tr("year"), self._tr("light − dark (days)"),
            y_fmt=_days_fmt,
        )
        envelope.set_series([{
            "key": "envelope", "label": self._tr("light − dark"),
            "color": palette.OBSERVATORY_SERIES_COLORS["light"],
            "xs": series["years"], "ys": light_minus_dark,
        }])
        light_from, light_to = eras["age_of_light"]
        envelope.set_bands([
            (first, light_from, palette.OBSERVATORY_ERA_DARK_BAND),
            (light_from, light_to, palette.OBSERVATORY_ERA_LIGHT_BAND),
            (light_to, last, palette.OBSERVATORY_ERA_DARK_BAND),
        ])
        mark = palette.OBSERVATORY_ERA_MARK_COLOR
        # Task 3: EVERY light/dark peak of the measured record, not just
        # the four sealed era marks — a simple neighbor-comparison over
        # the decimated bundle (data.light_dark_extrema()); each one
        # labeled with its year and value, thinned at full zoom.
        vmarks = [
            (eras["anno_lucis_year"], self._tr("Anno Lucis"), mark),
            (light_to, self._tr("Age of Darkness"), mark),
        ]
        for year, value, kind in data.light_dark_extrema():
            peak_label = self._tr("light peak") if kind == "light_peak" else self._tr("dark peak")
            vmarks.append((year, f"{peak_label} {year_label(year)} {value:+.1f}d", mark))
        envelope.set_vmarks(vmarks)
        self._envelope = envelope
        # Item 4 (owner screenshot "Settings na pogresnom mestu") — the
        # Days/Hours units switch now sits BESIDE this panel, the chart
        # it actually redraws, not the season panel above (see
        # `_envelope_filter`).
        envelope_caption = self._tr(
            "The signed light-minus-dark half-year, {span}, shaded by "
            "the Age of Light/Darkness eras with every measured peak "
            "labeled. Units follow the switch beside this chart."
        ).format(span=span_label)
        self._add_panel(
            self._tr("The light − dark envelope"), envelope,
            filter_row=self._envelope_filter(), caption=envelope_caption,
        )

        # 3 — the eclipse timeline.
        self._eclipse_chart = EclipseChart(self._tr)
        density = data.eclipse_density()
        meta = data.eclipse_meta()
        if deep is not None:
            solar, lunar = self._nearest_eclipses(deep, now, cycles)
            self._eclipse_chart.set_scatter(solar, lunar, astro_year)
            note = self._tr(
                "Nearest solar and lunar eclipses around the moment "
                "(exact instants from the full installation)."
            )
            eclipse_info_rows = self._eclipse_kind_rows(solar, lunar)
        else:
            self._eclipse_chart.set_density(density, astro_year)
            note = self._tr(
                "Eclipse density over the span — {solar}/{lunar} per century "
                "(solar/lunar). Install the full pack for exact instants."
            ).format(
                solar=meta["per_century"]["solar"],
                lunar=meta["per_century"]["lunar"],
            )
            eclipse_info_rows = self._eclipse_kind_rows(None, None)
        self._add_panel(
            self._tr("Eclipse timeline"), self._eclipse_chart, caption=note,
            info_rows=eclipse_info_rows,
        )

        # 4 — the location's day-length curve over the year.
        curve = day_length_curve(
            observer, tz, now.year, defaults.OBSERVATORY_DAYLENGTH_STEP_DAYS
        )
        day_chart = DayLengthChart(
            self._tr("day of year"), self._tr("day length"), now.year, y_fmt=_hm,
        )
        day_chart.set_series([{
            "key": "daylength", "label": self._tr("Day length"),
            "color": palette.OBSERVATORY_DAYLENGTH_COLOR,
            "xs": [day.timetuple().tm_yday for day, _ in curve],
            "ys": [minutes for _, minutes in curve],
        }])
        day_chart.set_fixed_y(0.0, 24 * 60)
        self._day_chart = day_chart
        minutes = [value for _, value in curve]
        day_caption = self._tr(
            "Daylight minutes across {year} at the current observer "
            "(day-of-year on the x-axis), ranging {low}–{high}."
        ).format(year=now.year, low=_hm(min(minutes)), high=_hm(max(minutes)))
        self._add_panel(
            self._tr("Day length over the year"), day_chart, caption=day_caption,
        )

        # 5 — the La2004 Laskar long envelope, ±200,000 years, amplitude
        # only (Fix round D, Task 4 — charts-only, ROADMAP 15a2 sealed).
        laskar = data.laskar_envelope()
        laskar_meta = data.laskar_envelope_meta()
        laskar_chart = LineChart(
            self._tr("year"), self._tr("amplitude (± days)"),
            y_fmt=lambda v: f"{v:+.1f}",
        )
        laskar_chart.set_series([
            {"key": "envelope_hi", "label": self._tr("amplitude envelope"),
             "color": palette.OBSERVATORY_LASKAR_ENVELOPE_COLOR,
             "xs": laskar["years"], "ys": laskar["envelope_days"]},
            {"key": "envelope_lo", "label": self._tr("amplitude envelope"),
             "color": palette.OBSERVATORY_LASKAR_ENVELOPE_COLOR,
             "xs": laskar["years"], "ys": [-v for v in laskar["envelope_days"]]},
            {"key": "signed", "label": self._tr("light − dark (signed)"),
             "color": palette.OBSERVATORY_LASKAR_SIGNED_COLOR,
             "xs": laskar["years"], "ys": laskar["signed_days"]},
        ])
        de441_lo, de441_hi = laskar_meta["de441_window_years"]
        laskar_chart.set_bands([
            (de441_lo, de441_hi, palette.OBSERVATORY_LASKAR_DE441_BAND),
        ])
        ecc_min = laskar_meta["extrema"]["coming_ecc_min"]
        laskar_chart.set_vmarks([(
            ecc_min["year"],
            f"{self._tr('eccentricity minimum')} {year_label(ecc_min['year'])} "
            f"(±{ecc_min['envelope_days']:.1f}d)",
            palette.OBSERVATORY_ERA_MARK_COLOR,
        )])
        self._laskar_chart = laskar_chart
        laskar_caption = self._tr(
            "Analytic orbital solution (La2004) — amplitude trend only; "
            "exact dates unreliable beyond the measured window. Shown: "
            "{span}."
        ).format(
            span=f"{year_label(laskar['years'][0])}–{year_label(laskar['years'][-1])}"
        )
        self._add_panel(
            self._tr("The Laskar long envelope (±200,000 years)"), laskar_chart,
            caption=laskar_caption,
        )

        # Task 2: wire the Days/Hours switch now that every chart it
        # touches (envelope + season) exists.
        self._units_combo.currentIndexChanged.connect(self._on_units_changed)
        self._on_units_changed(self._units_combo.currentIndex())

        # Fix round G, Task 2: restore the LAST splitter sizes used this
        # session (module-level cache — no settings key, matching that
        # this dialog's own window geometry isn't persisted either), then
        # keep it updated on every drag.
        global _last_splitter_sizes
        if (_last_splitter_sizes is not None
                and len(_last_splitter_sizes) == self._splitter.count()):
            self._splitter.setSizes(_last_splitter_sizes)
        self._splitter.splitterMoved.connect(self._on_splitter_moved)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(self._splitter)
        column.addWidget(scroll, stretch=1)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        close = QPushButton(self._tr("Close"))
        style_button(close, "neutral", small=True)
        close.clicked.connect(self.accept)
        buttons.addWidget(close)
        column.addLayout(buttons)

        apply_theme(self)
        # THE SPACE & LEGIBILITY LAW: the DECLARED minimum, computed from
        # the content's own hints (post-theme) and capped at the screen
        # floor — past the cap the chart column's scroll area lawfully
        # takes over VERTICALLY (the window is genuinely full there). The
        # WIDTH must cover the widest panel plus the scrollbar beside it:
        # sized off the outer hint alone, the filter row's own Enlarge
        # button was cut at the window's opening minimum (design review
        # 2026-08-06).
        scrollbar = self.style().pixelMetric(
            QStyle.PixelMetric.PM_ScrollBarExtent
        )
        margins = column.contentsMargins()
        width = max(
            self.sizeHint().width(),
            self._splitter.minimumSizeHint().width() + scrollbar
            + margins.left() + margins.right(),
        )
        self.setMinimumSize(min(width, 1280),
                            min(self.sizeHint().height(), 720))

    def _section(self, title: str) -> QLabel:
        label = QLabel(f"<b>{title}</b>")
        label.setStyleSheet(f"font-size: {defaults.GUIDE_SUBTITLE_PX}px;")
        return label

    def _caption(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setWordWrap(True)
        label.setStyleSheet(
            f"color: {palette.OBSERVATORY_MUTED_COLOR};"
            f"font-size: {encyclopedia_ui.UI_BUTTON_SMALL_FONT_PX}px;"
        )
        return label

    # Fix round G, Task 2 + 3: one panel per chart (title + filter row +
    # chart [+ caption]), added as a QSplitter pane, with a Collapse and
    # an "Enlarge" button appended to the filter row (a bare right-
    # aligned row is created for charts that don't already have one).
    def _add_panel(
        self, title: str, chart: ChartBase, *,
        filter_row: QHBoxLayout | None = None, caption: str | None = None,
        info_rows: list[tuple[str, str, str]] | None = None,
    ) -> None:
        panel = ChartPane()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(defaults.GUIDE_SPACING_PX)
        title_label = self._section(title)
        layout.addWidget(title_label)
        # Item 3: the ONE place `EnlargeDialog` reaches to hide/restore
        # this panel's own title while it is hosted there (that dialog
        # carries its own centered title instead).
        panel.title_label = title_label
        if filter_row is None:
            filter_row = QHBoxLayout()
            filter_row.addStretch(1)
        collapse_button = QPushButton(self._tr("Collapse"))
        style_button(collapse_button, "neutral", small=True)
        filter_row.addWidget(collapse_button)
        enlarge_button = QPushButton(self._tr("Enlarge"))
        style_button(enlarge_button, "neutral", small=True)
        filter_row.addWidget(enlarge_button)
        # ALG-5: the pair shares the widest label's size — and "Show",
        # the collapse button's OTHER caption, is measured in too, so
        # toggling never re-shrinks the button.
        collapse_button.setMinimumWidth(max(
            collapse_button.sizeHint().width(),
            collapse_button.fontMetrics().horizontalAdvance(self._tr("Show")) + 28,
        ))
        uniform_width((collapse_button, enlarge_button))
        layout.addLayout(filter_row)
        layout.addWidget(chart, stretch=1)
        caption_label = self._caption(caption) if caption else None
        if caption_label is not None:
            layout.addWidget(caption_label)
        collapse_button.clicked.connect(
            lambda: self._toggle_collapsed(chart, caption_label, collapse_button, enlarge_button)
        )
        enlarge_button.clicked.connect(
            lambda: self._open_enlarged(panel, chart, title, caption, info_rows, enlarge_button)
        )
        self._splitter.addWidget(panel)

    def _on_splitter_moved(self, pos: int, index: int) -> None:
        global _last_splitter_sizes
        _last_splitter_sizes = self._splitter.sizes()

    def _toggle_collapsed(
        self, chart: ChartBase, caption_label: QLabel | None,
        collapse_button: QPushButton, enlarge_button: QPushButton,
    ) -> None:
        """Item 7's second half (owner: add a per-chart COLLAPSE button
        to hide it, and a SHOW somewhere to bring it back — "za slučaj
        da korisnik hoće da upoređuje neke grafikone"). ONE toggling
        button does both: Qt layouts skip HIDDEN widgets entirely when
        sizing their parent, so a collapsed panel shrinks down to just
        its title + filter row, handing the freed room to whatever
        chart the owner is comparing; clicking the SAME button (now
        reading "Show") restores it. State lives on the chart widget
        itself, not on Qt's own isVisible() (which also depends on the
        whole ancestor chain and would misread before the dialog's
        first show)."""
        collapsed = not getattr(chart, "_row_collapsed", False)
        chart._row_collapsed = collapsed
        chart.setVisible(not collapsed)
        if caption_label is not None:
            caption_label.setVisible(not collapsed)
        enlarge_button.setEnabled(not collapsed)
        collapse_button.setText(self._tr("Show") if collapsed else self._tr("Collapse"))

    def _open_enlarged(
        self, panel: QWidget, chart: ChartBase, title: str,
        caption: str | None, info_rows: list[tuple[str, str, str]] | None,
        enlarge_button: QPushButton,
    ) -> None:
        """Task 3: reparent the SAME panel (title + filter + chart) into
        the Enlarge dialog and back — the cleanest way to "share the
        model/state" the current classes allow, since zoom/pan/checkbox
        state all live directly on these widgets; moving them (instead
        of building a parallel copy) carries that state for free and
        needs no synchronization in either direction.

        NON-MODAL now (ITEM 1, R4 owner instruction batch 2026-07-20):
        `EnlargeDialog` already calls `.show()` at the end of its own
        `__init__` — the old `dialog.exec()` right after construction
        was what re-entered it as a BLOCKING application-modal loop
        (`exec()` forces that regardless of the dialog's own
        windowModality), stalling the dial AND the Observatory itself
        for as long as the chart stayed enlarged. Dropping the `exec()`
        call and moving the cleanup that used to run right after it
        into a `finished` signal handler (`_close_enlarged`) keeps
        EXACTLY the same ownership order the Fix round R1a crash fix
        established — `panel` reparents back to the splitter BEFORE the
        dialog is destroyed — just triggered by the signal instead of a
        blocking return."""
        index = self._splitter.indexOf(panel)
        sizes = self._splitter.sizes()
        enlarge_button.setVisible(False)
        dialog = EnlargeDialog(
            panel, chart, title, caption, self._tr, info_rows, parent=self
        )
        dialog.finished.connect(
            lambda _result: self._close_enlarged(
                dialog, panel, index, sizes, enlarge_button
            )
        )

    def _close_enlarged(
        self, dialog: "EnlargeDialog", panel: QWidget, index: int,
        sizes: list[int], enlarge_button: QPushButton,
    ) -> None:
        """The `_open_enlarged` cleanup, now signal-driven — `panel` is
        reparented back to the splitter BEFORE the dialog is destroyed
        (the Fix round R1a crash fix's ownership order, preserved
        exactly), then the enlarged dialog is `deleteLater()`d."""
        self._splitter.insertWidget(index, panel)
        self._splitter.setSizes(sizes)
        panel.title_label.setVisible(True)
        panel.show()
        enlarge_button.setVisible(True)
        dialog.deleteLater()

    def _season_filter(self) -> QHBoxLayout:
        """The per-series checkboxes ABOVE chart 1 (owner: four seasons +
        the light/dark half-year pair) — swatch-colored, identity fixed.
        The Days/Hours units switch USED to sit in this same row (Fix
        round D) but visibly drives the ENVELOPE chart's axis, not this
        one (Item 4, owner screenshot "Settings na pogresnom mestu") —
        it now lives in `_envelope_filter`, beside the chart it actually
        changes."""
        row = QHBoxLayout()
        row.addStretch(1)
        for key in ("spring", "summer", "autumn", "winter", "light", "dark"):
            box = QCheckBox(self._tr(key.capitalize()))
            box.setChecked(key in ("light", "dark"))
            box.setStyleSheet(
                # The series' CANON chart hue, lightened only as far as
                # ALG-2 needs for TEXT on the dark surface — the chart
                # line itself keeps the exact canon color.
                f"color: {palette.readable_on_dark(palette.OBSERVATORY_SERIES_COLORS[key])};"
                "font-weight: bold;"
            )
            box.toggled.connect(
                lambda on, k=key: self._season_chart.set_visible(k, on)
            )
            row.addWidget(box)
        row.addStretch(1)
        return row

    def _envelope_filter(self) -> QHBoxLayout:
        """Item 4: the Days/Hours units switch, now beside the envelope
        panel whose y-axis/title/scale it actually redraws (see
        `_on_units_changed`) — it also still reaches the season chart's
        OWN crosshair delta line, a secondary, already-documented
        effect of the same switch."""
        row = QHBoxLayout()
        row.addStretch(1)
        row.addWidget(QLabel(self._tr("light − dark units:")))
        self._units_combo = QComboBox()
        self._units_combo.addItem(self._tr("Days"), "days")
        self._units_combo.addItem(self._tr("Hours"), "hours")
        self._units_combo.setCurrentIndex(
            1 if defaults.OBSERVATORY_UNITS_DEFAULT == "hours" else 0
        )
        row.addWidget(self._units_combo)
        row.addStretch(1)
        return row

    def _on_units_changed(self, index: int) -> None:
        """Task 2: a pure display transform (×24) — the underlying
        series never change, only the y-axis/crosshair labels. Fix round
        G, Task 1: the envelope's y-tick PITCH also switches to the
        scaled space (`set_y_scale`) so nice numbers land in hours, not
        days-converted-to-odd-hours."""
        hours = self._units_combo.itemData(index) == "hours"
        fmt = _hours_fmt if hours else _days_fmt
        title = self._tr("light − dark (hours)") if hours else self._tr("light − dark (days)")
        self._envelope.set_y_fmt(fmt)
        self._envelope.set_y_title(title)
        self._envelope.set_y_scale(24.0 if hours else 1.0)
        self._season_chart.set_diff_fmt(fmt)

    def _nearest_eclipses(self, deep, now, cycles):
        """The nearest OBSERVATORY_ECLIPSE_WINDOW_N eclipses of each kind
        on each side of the moment — repeated indexed jd lookups, no
        scan (honors Time Travel's frozen moment via `cycles`)."""
        jd = julian_day_of(now, cycles)
        window = defaults.OBSERVATORY_ECLIPSE_WINDOW_N
        result = {"solar": [], "lunar": []}
        for kind in ("solar", "lunar"):
            for finder in (deep.eclipse_after, deep.eclipse_before):
                cursor = jd
                for _ in range(window):
                    eclipse = finder(cursor, kind)
                    if eclipse is None:
                        break
                    year = eclipse.year + _fraction(eclipse)
                    result[kind].append((year, eclipse.magnitude, eclipse.type))
                    cursor = eclipse.jd_ut
        return result["solar"], result["lunar"]

    def _eclipse_kind_rows(self, solar, lunar) -> list[tuple[str, str, str]]:
        """Item 2 — the eclipse panel's info-rows (label, color, one-
        line meaning): deep mode lists every kind actually present in
        the fetched scatter (pass `solar`/`lunar`); the density fallback
        (pass `None, None`) lists the FULL ground-truthed vocabulary —
        its bundle's own `counts_by_type` meta already confirms every
        one of them occurs somewhere across the span, just without a
        per-instance breakdown to plot."""
        kind_colors = palette.OBSERVATORY_ECLIPSE_KIND_COLORS
        kind_info = defaults.OBSERVATORY_ECLIPSE_KIND_INFO
        rows: list[tuple[str, str, str]] = []
        for family, series in (("solar", solar), ("lunar", lunar)):
            if series is not None:
                present = {kind for _, magnitude, kind in series if magnitude is not None}
            else:
                present = set(kind_colors[family])
            for kind in kind_colors[family]:
                if kind in present:
                    rows.append((
                        f"{self._tr(family.capitalize())} · {self._tr(kind)}",
                        kind_colors[family][kind],
                        self._tr(kind_info[(family, kind)]),
                    ))
        return rows


def _fraction(eclipse) -> float:
    return (eclipse.month - 1) / 12.0 + (eclipse.day - 1) / 372.0


def _days_fmt(value: float) -> str:
    return f"{value:+.1f} d"


def _hours_fmt(value: float) -> str:
    return f"{value * 24:+.0f} h"


def _hm(minutes: float) -> str:
    minutes = int(round(minutes))
    return f"{minutes // 60}:{minutes % 60:02d}"
