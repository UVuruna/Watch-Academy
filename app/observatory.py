"""The Observatory — the statistics sibling of the Encyclopedia (owner
2026-07-16: "kao enciklopedija, samo sa statistikom").

Dark, QPainter-drawn, interactive charts over the long ephemeris data:
the season-duration oscillations (per-series checkboxes), the light−dark
envelope with the Anno Lucis dawn and the era spans, the eclipse
timeline (nearest past/next from the traveled moment when the Deep Time
pack is present; the bundled density otherwise) and the current
location's day-length curve over the year. Series data reads only the
committed bundles (data/observatory.py) — the charts never require
deep_time.sqlite.
"""

import bisect
import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QPolygonF
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.theme import apply_theme
from app.ui_style import style_button
from config import constants, defaults
from config.ui_text import ui
from core.deep_time import julian_day_of, real_year
from core.sun import day_length_curve
from data.observatory import ObservatoryData

# Plot margins: left (y labels), top, right, bottom (x labels).
_MARGIN = (58, 26, 18, 32)


def _plot_rect(widget: QWidget) -> QRectF:
    left, top, right, bottom = _MARGIN
    return QRectF(
        left, top,
        max(1.0, widget.width() - left - right),
        max(1.0, widget.height() - top - bottom),
    )


def _xmap(rect: QRectF, lo: float, hi: float, value: float) -> float:
    span = hi - lo or 1.0
    return rect.left() + (value - lo) / span * rect.width()


def _ymap(rect: QRectF, lo: float, hi: float, value: float) -> float:
    span = hi - lo or 1.0
    return rect.bottom() - (value - lo) / span * rect.height()


def _nice_ticks(lo: float, hi: float, target: int = 6) -> list[float]:
    span = hi - lo
    if span <= 0:
        return [lo]
    raw = span / target
    magnitude = 10 ** math.floor(math.log10(raw))
    step = magnitude
    for factor in (1, 2, 2.5, 5, 10):
        step = factor * magnitude
        if raw <= step:
            break
    start = math.ceil(lo / step) * step
    ticks: list[float] = []
    value = start
    while value <= hi + step * 1e-6:
        ticks.append(value)
        value += step
    return ticks


def _year_label(year: float) -> str:
    year = int(round(year))
    return f"{-year} BCE" if year < 0 else str(year)


class _ChartBase(QWidget):
    """Shared dark chart canvas: surface fill, axis frame, recessive
    grid, an always-drawn legend and a crosshair readout. Subclasses set
    the ranges/formatters and draw the data."""

    def __init__(self):
        super().__init__()
        self.setMinimumHeight(defaults.OBSERVATORY_CHART_MIN_HEIGHT_PX)
        self.setMouseTracking(True)
        self._hover: tuple[float, float] | None = None
        self._empty_text = ""
        self._x_title = ""
        self._y_title = ""
        self._xlo = self._xhi = self._ylo = self._yhi = 0.0

    # subclasses override -------------------------------------------------------
    def _has_data(self) -> bool:
        return True

    def _fmt_x(self, value: float) -> str:
        return f"{value:g}"

    def _fmt_y(self, value: float) -> str:
        return f"{value:g}"

    def _draw_data(self, painter: QPainter, rect: QRectF) -> None:
        ...

    def _legend(self) -> list[tuple[str, str]]:  # (label, color)
        return []

    def _probe(self, rect: QRectF, x_px: float) -> tuple | None:
        """(snap_x_px, [(x_px, y_px, color)], [readout lines]) or None."""
        return None

    # base painting -------------------------------------------------------------
    def mouseMoveEvent(self, event) -> None:  # noqa: N802 — Qt override
        self._hover = (event.position().x(), event.position().y())
        self.update()

    def leaveEvent(self, event) -> None:  # noqa: N802 — Qt override
        self._hover = None
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802 — Qt override
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(defaults.OBSERVATORY_SURFACE_COLOR))
        font = painter.font()
        font.setPixelSize(11)
        painter.setFont(font)
        if not self._has_data():
            painter.setPen(QColor(defaults.OBSERVATORY_MUTED_COLOR))
            painter.drawText(
                self.rect(), Qt.AlignmentFlag.AlignCenter, self._empty_text
            )
            painter.end()
            return
        rect = _plot_rect(self)
        self._draw_axes(painter, rect)
        self._draw_data(painter, rect)
        self._draw_legend(painter, rect)
        if self._hover is not None:
            probe = self._probe(rect, self._hover[0])
            if probe is not None:
                self._draw_crosshair(painter, rect, probe)
        painter.end()

    def _draw_axes(self, painter: QPainter, rect: QRectF) -> None:
        grid = QColor(defaults.OBSERVATORY_GRID_COLOR)
        muted = QColor(defaults.OBSERVATORY_MUTED_COLOR)
        painter.setPen(QPen(grid, defaults.OBSERVATORY_GRID_WIDTH_PX))
        painter.drawRect(rect)
        for value in _nice_ticks(self._ylo, self._yhi):
            y = _ymap(rect, self._ylo, self._yhi, value)
            if rect.top() - 1 <= y <= rect.bottom() + 1:
                painter.setPen(QPen(grid, defaults.OBSERVATORY_GRID_WIDTH_PX))
                painter.drawLine(int(rect.left()), int(y), int(rect.right()), int(y))
                painter.setPen(muted)
                painter.drawText(
                    0, int(y) - 7, int(rect.left()) - 4, 14,
                    Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                    self._fmt_y(value),
                )
        for value in _nice_ticks(self._xlo, self._xhi):
            x = _xmap(rect, self._xlo, self._xhi, value)
            if rect.left() - 1 <= x <= rect.right() + 1:
                painter.setPen(QPen(grid, defaults.OBSERVATORY_GRID_WIDTH_PX))
                painter.drawLine(int(x), int(rect.top()), int(x), int(rect.bottom()))
                painter.setPen(muted)
                painter.drawText(
                    int(x) - 40, int(rect.bottom()) + 3, 80, 16,
                    Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
                    self._fmt_x(value),
                )
        painter.setPen(muted)
        if self._y_title:
            painter.drawText(
                2, 4, int(rect.left()) + 40, 16,
                Qt.AlignmentFlag.AlignLeft, self._y_title,
            )
        if self._x_title:
            painter.drawText(
                int(rect.right()) - 160, int(rect.bottom()) + 15, 158, 16,
                Qt.AlignmentFlag.AlignRight, self._x_title,
            )

    def _draw_legend(self, painter: QPainter, rect: QRectF) -> None:
        entries = self._legend()
        if not entries:
            return
        x = rect.left() + 8
        y = rect.top() + 6
        for label, color in entries:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(color))
            painter.drawEllipse(int(x), int(y) + 3, 8, 8)
            painter.setPen(QColor(defaults.OBSERVATORY_INK_COLOR))
            width = painter.fontMetrics().horizontalAdvance(label)
            painter.drawText(int(x) + 12, int(y), width + 8, 14,
                             Qt.AlignmentFlag.AlignLeft, label)
            x += 12 + width + 20
            if x > rect.right() - 60:
                x = rect.left() + 8
                y += 16

    def _draw_crosshair(self, painter: QPainter, rect: QRectF, probe: tuple) -> None:
        snap_x, marks, lines = probe
        cross = QColor(defaults.OBSERVATORY_CROSSHAIR_COLOR)
        cross.setAlpha(150)
        painter.setPen(QPen(cross, 1, Qt.PenStyle.DashLine))
        painter.drawLine(int(snap_x), int(rect.top()), int(snap_x), int(rect.bottom()))
        painter.setPen(Qt.PenStyle.NoPen)
        for mx, my, color in marks:
            painter.setBrush(QColor(color))
            painter.drawEllipse(int(mx) - 3, int(my) - 3, 6, 6)
        if not lines:
            return
        metrics = painter.fontMetrics()
        box_w = max(metrics.horizontalAdvance(line) for line in lines) + 14
        box_h = len(lines) * 15 + 8
        bx = min(snap_x + 12, rect.right() - box_w)
        by = max(rect.top() + 4, min(self._hover[1] - box_h - 6, rect.bottom() - box_h))
        panel = QColor(defaults.OBSERVATORY_SURFACE_COLOR)
        panel.setAlpha(235)
        painter.setBrush(panel)
        painter.setPen(QPen(QColor(defaults.OBSERVATORY_GRID_COLOR), 1))
        painter.drawRoundedRect(QRectF(bx, by, box_w, box_h), 6, 6)
        painter.setPen(QColor(defaults.OBSERVATORY_INK_COLOR))
        for index, line in enumerate(lines):
            painter.drawText(
                int(bx) + 7, int(by) + 4 + index * 15, box_w - 14, 15,
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, line,
            )


class _LineChart(_ChartBase):
    """A multi-series line chart with fixed per-series colors, toggleable
    visibility (identity kept), optional shaded era bands + labelled
    verticals, and a crosshair readout (nearest sample by x)."""

    def __init__(self, x_title: str, y_title: str, y_fmt=None, x_fmt=None):
        super().__init__()
        self._x_title = x_title
        self._y_title = y_title
        self._y_fmt = y_fmt or (lambda v: f"{v:g}")
        self._x_fmt = x_fmt or _year_label
        self._series: list[dict] = []
        self._bands: list[tuple] = []
        self._vmarks: list[tuple] = []
        self._fixed_y: tuple[float, float] | None = None

    def set_series(self, series: list[dict]) -> None:
        self._series = [dict(entry, visible=True) for entry in series]
        self._recompute()

    def set_bands(self, bands: list[tuple]) -> None:  # (x0, x1, (hex, alpha))
        self._bands = bands

    def set_vmarks(self, vmarks: list[tuple]) -> None:  # (x, label, color)
        self._vmarks = vmarks

    def set_fixed_y(self, lo: float, hi: float) -> None:
        self._fixed_y = (lo, hi)

    def set_visible(self, key: str, on: bool) -> None:
        for entry in self._series:
            if entry["key"] == key:
                entry["visible"] = on
        self._recompute()
        self.update()

    def _visible(self) -> list[dict]:
        return [entry for entry in self._series if entry["visible"] and entry["xs"]]

    def _has_data(self) -> bool:
        return bool(self._visible())

    def _recompute(self) -> None:
        visible = self._visible()
        if not visible:
            return
        self._xlo = min(entry["xs"][0] for entry in visible)
        self._xhi = max(entry["xs"][-1] for entry in visible)
        if self._fixed_y is not None:
            self._ylo, self._yhi = self._fixed_y
            return
        lo = min(min(entry["ys"]) for entry in visible)
        hi = max(max(entry["ys"]) for entry in visible)
        pad = (hi - lo) * 0.08 or 1.0
        self._ylo, self._yhi = lo - pad, hi + pad

    def _fmt_x(self, value: float) -> str:
        return self._x_fmt(value)

    def _fmt_y(self, value: float) -> str:
        return self._y_fmt(value)

    def _legend(self) -> list[tuple[str, str]]:
        return [(entry["label"], entry["color"]) for entry in self._visible()]

    def _draw_data(self, painter: QPainter, rect: QRectF) -> None:
        for x0, x1, (hex_color, alpha) in self._bands:
            color = QColor(hex_color)
            color.setAlpha(alpha)
            left = _xmap(rect, self._xlo, self._xhi, max(x0, self._xlo))
            right = _xmap(rect, self._xlo, self._xhi, min(x1, self._xhi))
            painter.fillRect(
                QRectF(left, rect.top(), max(0.0, right - left), rect.height()), color
            )
        for x, label, color in self._vmarks:
            if not self._xlo <= x <= self._xhi:
                continue
            px = _xmap(rect, self._xlo, self._xhi, x)
            painter.setPen(QPen(QColor(color), 1, Qt.PenStyle.DashLine))
            painter.drawLine(int(px), int(rect.top()), int(px), int(rect.bottom()))
            painter.setPen(QColor(color))
            painter.drawText(
                int(px) + 3, int(rect.top()) + 2, 120, 14,
                Qt.AlignmentFlag.AlignLeft, label,
            )
        for entry in self._visible():
            painter.setPen(QPen(QColor(entry["color"]), defaults.OBSERVATORY_LINE_WIDTH_PX))
            polygon = QPolygonF([
                self._point(rect, x, y) for x, y in zip(entry["xs"], entry["ys"])
            ])
            painter.drawPolyline(polygon)

    def _point(self, rect: QRectF, x: float, y: float):
        return QPointF(
            _xmap(rect, self._xlo, self._xhi, x),
            _ymap(rect, self._ylo, self._yhi, y),
        )

    def _probe(self, rect: QRectF, x_px: float) -> tuple | None:
        visible = self._visible()
        if not visible:
            return None
        span = self._xhi - self._xlo or 1.0
        data_x = self._xlo + (x_px - rect.left()) / rect.width() * span
        marks = []
        lines = []
        snap_x = None
        for entry in visible:
            xs = entry["xs"]
            index = bisect.bisect_left(xs, data_x)
            if index >= len(xs):
                index = len(xs) - 1
            elif index > 0 and abs(xs[index - 1] - data_x) < abs(xs[index] - data_x):
                index -= 1
            x, y = xs[index], entry["ys"][index]
            px = _xmap(rect, self._xlo, self._xhi, x)
            py = _ymap(rect, self._ylo, self._yhi, y)
            marks.append((px, py, entry["color"]))
            lines.append(f"{entry['label']}: {self._y_fmt(y)}")
            if snap_x is None:
                snap_x = px
                header = self._x_fmt(x)
        lines.insert(0, header)
        return snap_x, marks, lines


class _EclipseChart(_ChartBase):
    """Chart 3. Deep Time present: a magnitude scatter of the nearest
    solar/lunar eclipses around the moment, the moment marked. Absent:
    the bundled density (counts per bucket) over the whole span."""

    def __init__(self, tr):
        super().__init__()
        self._tr = tr
        self._x_title = tr("year")
        self._solar: list[tuple] = []      # (year_float, magnitude, type)
        self._lunar: list[tuple] = []
        self._now_year: float | None = None
        self._density = None               # (years, solar, lunar) fallback
        self._deep_mode = False

    def set_scatter(self, solar, lunar, now_year) -> None:
        self._deep_mode = True
        self._solar, self._lunar = solar, lunar
        self._now_year = now_year
        self._y_title = self._tr("magnitude")
        points = solar + lunar
        years = [p[0] for p in points] + [now_year]
        self._xlo, self._xhi = min(years), max(years)
        mags = [p[1] for p in points if p[1] is not None] or [1.0]
        self._ylo, self._yhi = 0.0, max(mags) * 1.1

    def set_density(self, density: dict, now_year) -> None:
        self._deep_mode = False
        self._density = (density["years"], density["solar"], density["lunar"])
        self._now_year = now_year
        self._y_title = self._tr("eclipses per bucket")
        years = self._density[0]
        self._xlo, self._xhi = min(years), max(years)
        self._ylo = 0.0
        self._yhi = max(max(self._density[1]), max(self._density[2])) * 1.1

    def _has_data(self) -> bool:
        return bool(self._solar or self._lunar or self._density)

    def _fmt_x(self, value: float) -> str:
        return _year_label(value)

    def _fmt_y(self, value: float) -> str:
        return f"{value:.1f}" if self._deep_mode else f"{int(value)}"

    def _legend(self) -> list[tuple[str, str]]:
        colors = defaults.OBSERVATORY_ECLIPSE_COLORS
        return [
            (self._tr("Solar"), colors["solar"]),
            (self._tr("Lunar"), colors["lunar"]),
        ]

    def _draw_data(self, painter: QPainter, rect: QRectF) -> None:
        colors = defaults.OBSERVATORY_ECLIPSE_COLORS
        if self._now_year is not None and self._xlo <= self._now_year <= self._xhi:
            px = _xmap(rect, self._xlo, self._xhi, self._now_year)
            painter.setPen(QPen(QColor(defaults.OBSERVATORY_NOW_MARK_COLOR), 1))
            painter.drawLine(int(px), int(rect.top()), int(px), int(rect.bottom()))
            painter.drawText(
                int(px) + 3, int(rect.top()) + 2, 90, 14,
                Qt.AlignmentFlag.AlignLeft, self._tr("now"),
            )
        if self._deep_mode:
            painter.setPen(Qt.PenStyle.NoPen)
            radius = defaults.OBSERVATORY_MARK_RADIUS_PX
            for series, key in ((self._solar, "solar"), (self._lunar, "lunar")):
                painter.setBrush(QColor(colors[key]))
                for year, magnitude, _ in series:
                    if magnitude is None:
                        continue
                    px = _xmap(rect, self._xlo, self._xhi, year)
                    py = _ymap(rect, self._ylo, self._yhi, magnitude)
                    painter.drawEllipse(int(px) - radius, int(py) - radius,
                                        radius * 2, radius * 2)
            return
        years, solar, lunar = self._density
        for counts, key in ((solar, "solar"), (lunar, "lunar")):
            painter.setPen(QPen(QColor(colors[key]), defaults.OBSERVATORY_LINE_WIDTH_PX))
            polygon = QPolygonF([
                self._point(rect, x, y) for x, y in zip(years, counts)
            ])
            painter.drawPolyline(polygon)

    def _point(self, rect: QRectF, x: float, y: float):
        return QPointF(
            _xmap(rect, self._xlo, self._xhi, x),
            _ymap(rect, self._ylo, self._yhi, y),
        )

    def _probe(self, rect: QRectF, x_px: float) -> tuple | None:
        if not self._deep_mode:
            return None
        span = self._xhi - self._xlo or 1.0
        data_x = self._xlo + (x_px - rect.left()) / rect.width() * span
        best = None
        for series, key in ((self._solar, "solar"), (self._lunar, "lunar")):
            for year, magnitude, kind in series:
                if magnitude is None:
                    continue
                distance = abs(year - data_x)
                if best is None or distance < best[0]:
                    best = (distance, year, magnitude, kind, key)
        if best is None:
            return None
        _, year, magnitude, kind, key = best
        px = _xmap(rect, self._xlo, self._xhi, year)
        py = _ymap(rect, self._ylo, self._yhi, magnitude)
        color = defaults.OBSERVATORY_ECLIPSE_COLORS[key]
        lines = [
            _year_label(year),
            f"{self._tr(key.capitalize())} · {self._tr(kind)}",
            f"{self._tr('magnitude')}: {magnitude:.2f}",
        ]
        return px, [(px, py, color)], lines


class ObservatoryDialog(QDialog):
    def __init__(
        self, now, observer, tz, cycles=0, deep=None, translations=None,
        stay_on_top: bool = False,
    ):
        super().__init__()
        self._overlay = translations or {}
        self._tr = lambda text: ui(self._overlay, text)
        self.setWindowTitle(f"{constants.APP_NAME} — {self._tr('Observatory')}")
        # FIX ROUND A (owner verdict 2026-07-19, screenshots): a NORMAL
        # window by default, like the Encyclopedia — but in "top" z-mode
        # the dial forces itself to the TRUE top of the Z-order
        # (`native.assert_topmost`, HWND_TOPMOST), so an ordinary window
        # opens UNDER it. `stay_on_top` is the controller's
        # `z_mode == "top"` reading; every other z-mode is unchanged.
        if stay_on_top:
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self.setWindowFlag(Qt.WindowType.WindowMaximizeButtonHint, True)
        self.setWindowFlag(Qt.WindowType.WindowMinimizeButtonHint, True)
        self.resize(860, 720)

        data = ObservatoryData()
        column = QVBoxLayout(self)

        astro_year = real_year(now.year, cycles)
        anno = astro_year + constants.ANNO_LUCIS_OFFSET
        header = QLabel(
            f"<b>{self._tr('Observatory')}</b> — "
            f"{_year_label(astro_year)} · {self._tr('A.L.')} {anno}"
        )
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        column.addWidget(header)

        content = QWidget()
        body = QVBoxLayout(content)
        body.setSpacing(defaults.GUIDE_SPACING_PX * 2)

        # 1 — the season-duration oscillations with the checkbox filter.
        series = data.season_series()
        self._season_chart = _LineChart(
            self._tr("year"), self._tr("days"), y_fmt=lambda v: f"{v:.1f}"
        )
        self._season_chart.set_series([
            {"key": key, "label": self._tr(key.capitalize()),
             "color": defaults.OBSERVATORY_SERIES_COLORS[key],
             "xs": series["years"], "ys": series[key]}
            for key in ("spring", "summer", "autumn", "winter", "light", "dark")
        ])
        # Start with only the two halves lit (the owner's own graph) so
        # the busy four-season lines do not crowd the first view.
        for key in ("spring", "summer", "autumn", "winter"):
            self._season_chart.set_visible(key, False)
        body.addWidget(self._section(self._tr("Season durations")))
        body.addLayout(self._season_filter())
        body.addWidget(self._season_chart)

        # 2 — the light − dark envelope with the eras.
        eras = data.season_eras()
        light_minus_dark = [
            round(light - dark, 4)
            for light, dark in zip(series["light"], series["dark"])
        ]
        envelope = _LineChart(
            self._tr("year"), self._tr("light − dark (days)"),
            y_fmt=lambda v: f"{v:+.0f}",
        )
        envelope.set_series([{
            "key": "envelope", "label": self._tr("light − dark"),
            "color": defaults.OBSERVATORY_SERIES_COLORS["light"],
            "xs": series["years"], "ys": light_minus_dark,
        }])
        first, last = data.season_span()
        light_from, light_to = eras["age_of_light"]
        envelope.set_bands([
            (first, light_from, defaults.OBSERVATORY_ERA_DARK_BAND),
            (light_from, light_to, defaults.OBSERVATORY_ERA_LIGHT_BAND),
            (light_to, last, defaults.OBSERVATORY_ERA_DARK_BAND),
        ])
        mark = defaults.OBSERVATORY_ERA_MARK_COLOR
        transitions = eras["starry_transitions"]
        envelope.set_vmarks([
            (eras["anno_lucis_year"], self._tr("Anno Lucis"), mark),
            (transitions["spring_peak"], self._tr("light peak"), mark),
            (light_to, self._tr("Age of Darkness"), mark),
            (transitions["autumn_peak"], self._tr("dark peak"), mark),
        ])
        self._envelope = envelope
        body.addWidget(self._section(self._tr("The light − dark envelope")))
        body.addWidget(envelope)

        # 3 — the eclipse timeline.
        self._eclipse_chart = _EclipseChart(self._tr)
        density = data.eclipse_density()
        meta = data.eclipse_meta()
        if deep is not None:
            solar, lunar = self._nearest_eclipses(deep, now, cycles)
            self._eclipse_chart.set_scatter(solar, lunar, astro_year)
            note = self._tr(
                "Nearest solar and lunar eclipses around the moment "
                "(exact instants from the full installation)."
            )
        else:
            self._eclipse_chart.set_density(density, astro_year)
            note = self._tr(
                "Eclipse density over the span — {solar}/{lunar} per century "
                "(solar/lunar). Install the full pack for exact instants."
            ).format(
                solar=meta["per_century"]["solar"],
                lunar=meta["per_century"]["lunar"],
            )
        body.addWidget(self._section(self._tr("Eclipse timeline")))
        body.addWidget(self._eclipse_chart)
        body.addWidget(self._caption(note))

        # 4 — the location's day-length curve over the year.
        curve = day_length_curve(
            observer, tz, now.year, defaults.OBSERVATORY_DAYLENGTH_STEP_DAYS
        )
        day_chart = _LineChart(
            self._tr("day of year"), self._tr("day length"),
            y_fmt=_hm, x_fmt=lambda v: _MONTHS[max(0, min(11, int(v // 30)))],
        )
        day_chart.set_series([{
            "key": "daylength", "label": self._tr("Day length"),
            "color": defaults.OBSERVATORY_DAYLENGTH_COLOR,
            "xs": [day.timetuple().tm_yday for day, _ in curve],
            "ys": [minutes for _, minutes in curve],
        }])
        day_chart.set_fixed_y(0.0, 24 * 60)
        self._day_chart = day_chart
        body.addWidget(self._section(self._tr("Day length over the year")))
        body.addWidget(day_chart)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(content)
        column.addWidget(scroll, stretch=1)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        close = QPushButton(self._tr("Close"))
        style_button(close, "neutral", small=True)
        close.clicked.connect(self.accept)
        buttons.addWidget(close)
        column.addLayout(buttons)

        apply_theme(self)

    def _section(self, title: str) -> QLabel:
        label = QLabel(f"<b>{title}</b>")
        label.setStyleSheet(f"font-size: {defaults.GUIDE_SUBTITLE_PX}px;")
        return label

    def _caption(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setWordWrap(True)
        label.setStyleSheet(
            f"color: {defaults.OBSERVATORY_MUTED_COLOR};"
            f"font-size: {defaults.UI_BUTTON_SMALL_FONT_PX}px;"
        )
        return label

    def _season_filter(self) -> QHBoxLayout:
        """The per-series checkboxes ABOVE chart 1 (owner: four seasons +
        the light/dark half-year pair) — swatch-colored, identity fixed."""
        row = QHBoxLayout()
        row.addStretch(1)
        for key in ("spring", "summer", "autumn", "winter", "light", "dark"):
            box = QCheckBox(self._tr(key.capitalize()))
            box.setChecked(key in ("light", "dark"))
            box.setStyleSheet(
                f"color: {defaults.OBSERVATORY_SERIES_COLORS[key]};"
                "font-weight: bold;"
            )
            box.toggled.connect(
                lambda on, k=key: self._season_chart.set_visible(k, on)
            )
            row.addWidget(box)
        row.addStretch(1)
        return row

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


def _fraction(eclipse) -> float:
    return (eclipse.month - 1) / 12.0 + (eclipse.day - 1) / 372.0


def _hm(minutes: float) -> str:
    minutes = int(round(minutes))
    return f"{minutes // 60}:{minutes % 60:02d}"


_MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun",
           "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
