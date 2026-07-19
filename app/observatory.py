"""The Observatory — the statistics sibling of the Encyclopedia (owner
2026-07-16: "kao enciklopedija, samo sa statistikom").

Dark, QPainter-drawn, interactive charts over the long ephemeris data:
the season-duration oscillations (per-series checkboxes), the light−dark
envelope with the Anno Lucis dawn, every measured light/dark peak and
the era spans, the eclipse timeline (nearest past/next from the
traveled moment when the Deep Time pack is present; the bundled density
otherwise), the current location's day-length curve over the year, and
the La2004 Laskar long envelope over +/-200,000 years (charts-only —
ROADMAP 15a2). Series data reads only the committed bundles
(data/observatory.py) — the charts never require deep_time.sqlite.

Fix round D (owner verdicts 2026-07-19): every chart supports
mouse-wheel zoom centered on the cursor, drag-to-pan while zoomed and a
double-click reset, with the y axis auto-fitting the visible x slice on
every change (_ChartBase); a Days/Hours switch governs every
"light − dark" readout (_LineChart.set_y_fmt/set_diff_fmt).
"""

import bisect
import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QPolygonF
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
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
        # Fix round D, Task 1: the full data extent (reset target) vs the
        # current VIEW (self._xlo/_xhi double as the view — every mapper
        # and probe already reads them, so zoom is "just" narrowing them).
        self._full_xlo: float | None = None
        self._full_xhi: float | None = None
        self._drag_from_px: float | None = None
        self._drag_view: tuple[float, float] | None = None

    # subclasses override -------------------------------------------------------
    def _has_data(self) -> bool:
        return True

    def _fit_y_to_view(self) -> None:
        """Recompute self._ylo/_yhi from the data visible in the current
        x view (self._xlo/_xhi) — called after every zoom/pan/reset so
        the y axis auto-fits (owner Task 1). No-op by default."""
        return

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

    # zoom / pan / reset (Fix round D, Task 1) -----------------------------------
    def _reset_view(self) -> None:
        """Restore the full x span (double-click) — the "Reset" affordance."""
        if self._full_xlo is None:
            return
        self._xlo, self._xhi = self._full_xlo, self._full_xhi
        self._fit_y_to_view()
        self.update()

    def _zoom_at(self, x_px: float, factor: float) -> None:
        """Zoom the x view by `factor` (< 1 = in, > 1 = out), keeping the
        data value under `x_px` fixed, clamped to the full extent, then
        auto-fits the y axis to whatever slice is now visible."""
        if self._full_xlo is None or not self._has_data():
            return
        rect = _plot_rect(self)
        span = self._xhi - self._xlo or 1.0
        data_x = self._xlo + (x_px - rect.left()) / rect.width() * span
        full_span = self._full_xhi - self._full_xlo
        if full_span <= 0:
            return
        min_span = full_span * defaults.OBSERVATORY_ZOOM_MIN_FRACTION
        new_span = max(min_span, min(full_span, span * factor))
        frac = (data_x - self._xlo) / span
        new_lo = data_x - frac * new_span
        new_hi = new_lo + new_span
        if new_lo < self._full_xlo:
            new_lo, new_hi = self._full_xlo, self._full_xlo + new_span
        if new_hi > self._full_xhi:
            new_hi, new_lo = self._full_xhi, self._full_xhi - new_span
        self._xlo, self._xhi = new_lo, new_hi
        self._fit_y_to_view()
        self.update()

    def wheelEvent(self, event) -> None:  # noqa: N802 — Qt override
        delta = event.angleDelta().y()
        if delta == 0 or self._full_xlo is None:
            event.ignore()
            return
        factor = (
            defaults.OBSERVATORY_ZOOM_FACTOR if delta > 0
            else 1.0 / defaults.OBSERVATORY_ZOOM_FACTOR
        )
        self._zoom_at(event.position().x(), factor)
        event.accept()

    def mouseDoubleClickEvent(self, event) -> None:  # noqa: N802 — Qt override
        self._reset_view()

    def mousePressEvent(self, event) -> None:  # noqa: N802 — Qt override
        if event.button() == Qt.MouseButton.LeftButton and self._full_xlo is not None:
            self._drag_from_px = event.position().x()
            self._drag_view = (self._xlo, self._xhi)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802 — Qt override
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_from_px = None
            self._drag_view = None

    # base painting -------------------------------------------------------------
    def mouseMoveEvent(self, event) -> None:  # noqa: N802 — Qt override
        self._hover = (event.position().x(), event.position().y())
        if self._drag_from_px is not None and self._drag_view is not None:
            rect = _plot_rect(self)
            view_lo, view_hi = self._drag_view
            span = view_hi - view_lo
            dx = -(event.position().x() - self._drag_from_px) / rect.width() * span
            new_lo, new_hi = view_lo + dx, view_hi + dx
            if new_lo < self._full_xlo:
                new_hi += self._full_xlo - new_lo
                new_lo = self._full_xlo
            if new_hi > self._full_xhi:
                new_lo -= new_hi - self._full_xhi
                new_hi = self._full_xhi
            self._xlo, self._xhi = new_lo, new_hi
            self._fit_y_to_view()
        self.update()

    def leaveEvent(self, event) -> None:  # noqa: N802 — Qt override
        self._hover = None
        self._drag_from_px = None
        self._drag_view = None
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

    def __init__(self, x_title: str, y_title: str, y_fmt=None, x_fmt=None,
                 diff_pair: tuple[str, str] | None = None):
        super().__init__()
        self._x_title = x_title
        self._y_title = y_title
        self._y_fmt = y_fmt or (lambda v: f"{v:g}")
        self._x_fmt = x_fmt or _year_label
        self._series: list[dict] = []
        self._bands: list[tuple] = []
        self._vmarks: list[tuple] = []
        self._fixed_y: tuple[float, float] | None = None
        # Task 2: an optional (key_a, key_b) pair whose DIFFERENCE the
        # crosshair also reports (e.g. light/dark), in its own unit —
        # decoupled from the main y_fmt so the series' own axis stays in
        # its natural unit (days) even when the delta switches to hours.
        self._diff_pair = diff_pair
        self._diff_fmt = self._y_fmt

    def set_series(self, series: list[dict]) -> None:
        self._series = [dict(entry, visible=True) for entry in series]
        self._reset_view()

    def set_bands(self, bands: list[tuple]) -> None:  # (x0, x1, (hex, alpha))
        self._bands = bands

    def set_vmarks(self, vmarks: list[tuple]) -> None:  # (x, label, color)
        self._vmarks = sorted(vmarks, key=lambda mark: mark[0])

    def set_fixed_y(self, lo: float, hi: float) -> None:
        self._fixed_y = (lo, hi)
        if self._full_xlo is not None:
            self._fit_y_to_view()
            self.update()

    def set_y_fmt(self, fmt) -> None:
        """Task 2: swap the y-axis/series formatter (the units switch) —
        a pure display transform, the underlying series never change."""
        self._y_fmt = fmt
        self.update()

    def set_y_title(self, title: str) -> None:
        self._y_title = title
        self.update()

    def set_diff_fmt(self, fmt) -> None:
        """Task 2: the formatter for the diff_pair crosshair line only."""
        self._diff_fmt = fmt
        self.update()

    def set_visible(self, key: str, on: bool) -> None:
        for entry in self._series:
            if entry["key"] == key:
                entry["visible"] = on
        self._reset_view()
        self.update()

    def _visible(self) -> list[dict]:
        return [entry for entry in self._series if entry["visible"] and entry["xs"]]

    def _has_data(self) -> bool:
        return bool(self._visible())

    def _reset_view(self) -> None:
        visible = self._visible()
        if not visible:
            return
        self._full_xlo = min(entry["xs"][0] for entry in visible)
        self._full_xhi = max(entry["xs"][-1] for entry in visible)
        self._xlo, self._xhi = self._full_xlo, self._full_xhi
        self._fit_y_to_view()

    def _fit_y_to_view(self) -> None:
        """Task 1: the y range for whatever x SLICE is currently visible
        — the full un-zoomed view keeps the fixed range (day-length's
        nice 0..24h axis) if one is set; any zoom auto-fits the slice."""
        visible = self._visible()
        if not visible:
            return
        zoomed = (self._xlo, self._xhi) != (self._full_xlo, self._full_xhi)
        if self._fixed_y is not None and not zoomed:
            self._ylo, self._yhi = self._fixed_y
            return
        ys: list[float] = []
        for entry in visible:
            xs, vals = entry["xs"], entry["ys"]
            i0 = bisect.bisect_left(xs, self._xlo)
            i1 = bisect.bisect_right(xs, self._xhi)
            i0 = max(0, i0 - 1)          # one point of context past each edge
            i1 = min(len(xs), i1 + 1)
            ys.extend(vals[i0:i1])
        if not ys:
            return
        lo, hi = min(ys), max(ys)
        pad = (hi - lo) * defaults.OBSERVATORY_Y_FIT_PAD_FRACTION or 1.0
        self._ylo, self._yhi = lo - pad, hi + pad

    def _fmt_x(self, value: float) -> str:
        return self._x_fmt(value)

    def _fmt_y(self, value: float) -> str:
        return self._y_fmt(value)

    def _legend(self) -> list[tuple[str, str]]:
        # Dedupe by label — the Laskar envelope's +/- band is two series
        # sharing one legend entry (Task 4).
        seen: dict[str, str] = {}
        for entry in self._visible():
            seen.setdefault(entry["label"], entry["color"])
        return list(seen.items())

    def _draw_data(self, painter: QPainter, rect: QRectF) -> None:
        for x0, x1, (hex_color, alpha) in self._bands:
            color = QColor(hex_color)
            color.setAlpha(alpha)
            left = _xmap(rect, self._xlo, self._xhi, max(x0, self._xlo))
            right = _xmap(rect, self._xlo, self._xhi, min(x1, self._xhi))
            painter.fillRect(
                QRectF(left, rect.top(), max(0.0, right - left), rect.height()), color
            )
        # Task 3: thin labels that would collide at the full (un-zoomed)
        # span — zoomed in there is room, so every mark gets its label.
        zoomed_in = (self._full_xlo is not None
                     and (self._xhi - self._xlo) < (self._full_xhi - self._full_xlo) - 1e-6)
        last_label_px: float | None = None
        for x, label, color in self._vmarks:
            if not self._xlo <= x <= self._xhi:
                continue
            px = _xmap(rect, self._xlo, self._xhi, x)
            painter.setPen(QPen(QColor(color), 1, Qt.PenStyle.DashLine))
            painter.drawLine(int(px), int(rect.top()), int(px), int(rect.bottom()))
            if (not zoomed_in and last_label_px is not None
                    and abs(px - last_label_px) < defaults.OBSERVATORY_VMARK_MIN_SPACING_PX):
                continue
            last_label_px = px
            painter.setPen(QColor(color))
            painter.drawText(
                int(px) + 3, int(rect.top()) + 2, 160, 14,
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
        values: dict[str, float] = {}
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
            values[entry["key"]] = y
            if snap_x is None:
                snap_x = px
                header = self._x_fmt(x)
        lines.insert(0, header)
        # Task 2: the light/dark delta line, in the current diff unit.
        if self._diff_pair and all(key in values for key in self._diff_pair):
            key_a, key_b = self._diff_pair
            lines.append(f"Δ: {self._diff_fmt(values[key_a] - values[key_b])}")
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
        self._full_xlo, self._full_xhi = min(years), max(years)
        self._xlo, self._xhi = self._full_xlo, self._full_xhi
        self._fit_y_to_view()

    def set_density(self, density: dict, now_year) -> None:
        self._deep_mode = False
        self._density = (density["years"], density["solar"], density["lunar"])
        self._now_year = now_year
        self._y_title = self._tr("eclipses per bucket")
        years = self._density[0]
        self._full_xlo, self._full_xhi = min(years), max(years)
        self._xlo, self._xhi = self._full_xlo, self._full_xhi
        self._fit_y_to_view()

    def _has_data(self) -> bool:
        return bool(self._solar or self._lunar or self._density)

    def _fit_y_to_view(self) -> None:
        """Task 1: y auto-fits to the eclipses/buckets visible in the
        current x view — magnitude scatter in deep mode, counts in the
        density fallback."""
        if self._deep_mode:
            points = self._solar + self._lunar
            mags = [
                p[1] for p in points
                if p[1] is not None and self._xlo <= p[0] <= self._xhi
            ] or [1.0]
            self._ylo, self._yhi = 0.0, max(mags) * 1.1
            return
        if self._density is None:
            return
        years, solar, lunar = self._density
        counts = [
            value for year, value in zip(years, solar) if self._xlo <= year <= self._xhi
        ] + [
            value for year, value in zip(years, lunar) if self._xlo <= year <= self._xhi
        ]
        self._ylo = 0.0
        self._yhi = (max(counts) if counts else 1.0) * 1.1

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
            self._tr("year"), self._tr("days"), y_fmt=lambda v: f"{v:.1f}",
            # Task 2: the crosshair also reports the light/dark delta,
            # in whichever unit the switch picks — the series' own axis
            # (raw durations) always stays in days.
            diff_pair=("light", "dark"),
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

        # 2 — the light − dark envelope with the eras and every peak.
        eras = data.season_eras()
        light_minus_dark = [
            round(light - dark, 4)
            for light, dark in zip(series["light"], series["dark"])
        ]
        envelope = _LineChart(
            self._tr("year"), self._tr("light − dark (days)"),
            y_fmt=_days_fmt,
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
            vmarks.append((year, f"{peak_label} {_year_label(year)} {value:+.1f}d", mark))
        envelope.set_vmarks(vmarks)
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

        # 5 — the La2004 Laskar long envelope, ±200,000 years, amplitude
        # only (Fix round D, Task 4 — charts-only, ROADMAP 15a2 sealed).
        laskar = data.laskar_envelope()
        laskar_meta = data.laskar_envelope_meta()
        laskar_chart = _LineChart(
            self._tr("year"), self._tr("amplitude (± days)"),
            y_fmt=lambda v: f"{v:+.1f}",
        )
        laskar_chart.set_series([
            {"key": "envelope_hi", "label": self._tr("amplitude envelope"),
             "color": defaults.OBSERVATORY_LASKAR_ENVELOPE_COLOR,
             "xs": laskar["years"], "ys": laskar["envelope_days"]},
            {"key": "envelope_lo", "label": self._tr("amplitude envelope"),
             "color": defaults.OBSERVATORY_LASKAR_ENVELOPE_COLOR,
             "xs": laskar["years"], "ys": [-v for v in laskar["envelope_days"]]},
            {"key": "signed", "label": self._tr("light − dark (signed)"),
             "color": defaults.OBSERVATORY_LASKAR_SIGNED_COLOR,
             "xs": laskar["years"], "ys": laskar["signed_days"]},
        ])
        de441_lo, de441_hi = laskar_meta["de441_window_years"]
        laskar_chart.set_bands([
            (de441_lo, de441_hi, defaults.OBSERVATORY_LASKAR_DE441_BAND),
        ])
        ecc_min = laskar_meta["extrema"]["coming_ecc_min"]
        laskar_chart.set_vmarks([(
            ecc_min["year"],
            f"{self._tr('eccentricity minimum')} {_year_label(ecc_min['year'])} "
            f"(±{ecc_min['envelope_days']:.1f}d)",
            defaults.OBSERVATORY_ERA_MARK_COLOR,
        )])
        self._laskar_chart = laskar_chart
        body.addWidget(self._section(
            self._tr("The Laskar long envelope (±200,000 years)")
        ))
        body.addWidget(laskar_chart)
        body.addWidget(self._caption(self._tr(
            "Analytic orbital solution (La2004) — amplitude trend only; "
            "exact dates unreliable beyond the measured window."
        )))

        # Task 2: wire the Days/Hours switch now that every chart it
        # touches (envelope + season) exists.
        self._units_combo.currentIndexChanged.connect(self._on_units_changed)
        self._on_units_changed(self._units_combo.currentIndex())

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
        the light/dark half-year pair) — swatch-colored, identity fixed
        — plus the Days/Hours switch (Task 2), governing every
        "light − dark" readout on charts 1 and 2. Built here but wired
        (currentIndexChanged connected) once every chart it touches
        exists — see the end of __init__."""
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
        row.addSpacing(16)
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
        series never change, only the y-axis/crosshair labels."""
        hours = self._units_combo.itemData(index) == "hours"
        fmt = _hours_fmt if hours else _days_fmt
        title = self._tr("light − dark (hours)") if hours else self._tr("light − dark (days)")
        self._envelope.set_y_fmt(fmt)
        self._envelope.set_y_title(title)
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


def _fraction(eclipse) -> float:
    return (eclipse.month - 1) / 12.0 + (eclipse.day - 1) / 372.0


def _days_fmt(value: float) -> str:
    return f"{value:+.1f} d"


def _hours_fmt(value: float) -> str:
    return f"{value * 24:+.0f} h"


def _hm(minutes: float) -> str:
    minutes = int(round(minutes))
    return f"{minutes // 60}:{minutes % 60:02d}"


_MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun",
           "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
