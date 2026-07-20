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
from datetime import date, timedelta

from PySide6.QtCore import QPointF, QRectF, QSize, Qt, QTimer
from PySide6.QtGui import QColor, QFont, QGuiApplication, QPainter, QPen, QPolygonF
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from app.theme import apply_theme, size_to_screen
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


def _nice_step(span: float, target: int, min_step: float = 0.0) -> float:
    """Fix round G, Task 1 — the classic "nice number" ladder (1-2-5 per
    decade: ...0.1/0.2/0.5/1/2/5/10/20/50/100/200/500/1k/2k/5k...),
    generated arithmetically rather than hardcoded so it covers any
    magnitude (fractional y-spans as readily as the Laskar chart's
    ±200,000-year x-span). Returns the SMALLEST ladder rung that keeps
    the tick count at/under `target`; once even the finest possible
    rung at this magnitude still exceeds it (a span tighter than makes
    sense to subdivide further), that rung is used anyway — more ticks
    than the target, but nothing finer is meaningful for this axis.

    `min_step` (Fix round R1a, Item 5 — a per-chart MIN TICK floor) never
    lets the rung go below it even when the raw span/target math would
    ask for something finer — the day-length chart's "Mon D" labels
    round to a whole calendar day, so a sub-day rung would print the
    SAME label on two adjacent gridlines."""
    if span <= 0 or target <= 0:
        return max(span or 1.0, min_step)
    raw = span / target
    magnitude = 10 ** math.floor(math.log10(raw))
    for factor in (1, 2, 5, 10):
        step = factor * magnitude
        if raw <= step:
            return max(step, min_step)
    return max(10 * magnitude, min_step)  # unreachable — factor=10 always satisfies raw<=step


def _nice_ticks(lo: float, hi: float, target: int, min_step: float = 0.0) -> list[float]:
    span = hi - lo
    if span <= 0:
        return [lo]
    step = _nice_step(span, target, min_step)
    start = math.ceil(lo / step) * step
    ticks: list[float] = []
    value = start
    while value <= hi + step * 1e-6:
        ticks.append(value)
        value += step
    return ticks


def _median_gap(xs: list[float]) -> float | None:
    """The median gap between consecutive values of a SORTED sequence —
    Fix round R1a, Item 5's shared "read the floor off the data" tool:
    robust to a few dense/sparse patches (unlike the raw min gap), so
    ONE real sample stride still governs even when a handful of points
    happen to sit unusually close together."""
    gaps = sorted(b - a for a, b in zip(xs, xs[1:]) if b > a)
    if not gaps:
        return None
    return gaps[len(gaps) // 2]


def _year_label(year: float, zoomed: bool = False) -> str:
    year = int(round(year))
    # Item 6 (owner: "FORMAT brojeva je 000,000") — a thousands
    # separator on every printed year, the multi-millennial charts'
    # whole reason for existing.
    return f"{-year:,} BCE" if year < 0 else f"{year:,}"


def _nearest_index(xs: list[float], value: float) -> int:
    """The index of the sample in the ascending `xs` closest to `value`
    (bisect-based nearest-neighbor) — shared by the crosshair probe and
    the enlarged view's extended-legend "current value" readout
    (Fix round G, Task 3)."""
    index = bisect.bisect_left(xs, value)
    if index >= len(xs):
        return len(xs) - 1
    if index > 0 and abs(xs[index - 1] - value) < abs(xs[index] - value):
        return index - 1
    return index


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
        # Fix round G, Task 1: the y-axis DISPLAY scale (the Days/Hours
        # transform is x24) — nice y-ticks are computed in the SCALED
        # (displayed) space then converted back, so round numbers land
        # in whichever unit is actually shown, not the raw storage unit.
        self._y_scale = 1.0

    def sizeHint(self):  # noqa: N802 — Qt override
        """Fix round R1a, Item 7 — a REAL preferred size, genuinely
        above the `OBSERVATORY_CHART_MIN_HEIGHT_PX` floor. A bare-
        painted QWidget with no layout of its own defaults to an
        INVALID sizeHint(), which collapses every panel's natural
        splitter allocation to exactly its minimum — so the instant the
        dialog is shorter than the splitter's full content (any
        realistic default open, before the owner ever touches a handle)
        every panel is already pinned at its floor and dragging has
        nothing left to redistribute (root cause of "RESIZE ne radi",
        confirmed with a real QTest mouse-press/move/release drive).
        Returning a genuinely larger preferred height gives every panel
        headroom to trade with its neighbor regardless of window size."""
        return QSize(400, defaults.OBSERVATORY_CHART_PREFERRED_HEIGHT_PX)

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

    def _legend_values(self) -> dict[str, str]:
        """Fix round G, Task 3 — per-legend-label CURRENT VALUE strings
        for the enlarged view's extended legend: the crosshair's value
        while hovering, else a sensible per-chart fallback. Empty (no
        value column) by default."""
        return {}

    # adaptive ticks (Fix round G, Task 1) ---------------------------------------
    def _is_zoomed(self) -> bool:
        return (
            self._full_xlo is not None
            and (self._xhi - self._xlo) < (self._full_xhi - self._full_xlo) - 1e-6
        )

    def _x_ticks(self) -> list[float]:
        """The x tick positions for the CURRENT view — adapts to the
        visible span via the generic nice-step ladder. Overridden by
        the day-length chart for calendar-aware month/day positions."""
        return _nice_ticks(self._xlo, self._xhi, defaults.OBSERVATORY_TARGET_X_TICKS)

    def _y_ticks(self) -> list[float]:
        """The y tick positions for the current fitted range, computed
        in the DISPLAY scale (`_y_scale` — the Days/Hours transform) so
        nice numbers land in the shown unit, then converted back to the
        raw axis coordinate."""
        scale = self._y_scale
        lo, hi = self._ylo * scale, self._yhi * scale
        return [
            value / scale
            for value in _nice_ticks(lo, hi, defaults.OBSERVATORY_TARGET_Y_TICKS)
        ]

    # zoom / pan / reset (Fix round D, Task 1) -----------------------------------
    def _reset_view(self) -> None:
        """Restore the full x span (double-click) — the "Reset" affordance."""
        if self._full_xlo is None:
            return
        self._xlo, self._xhi = self._full_xlo, self._full_xhi
        self._fit_y_to_view()
        self.update()

    def _zoom_floor(self, full_span: float) -> float:
        """Fix round R1a, Item 5 — the tightest x-span `_zoom_at` allows
        for THIS chart (its MAX ZOOM). Default: the old span-fraction/
        absolute-floor heuristic — a chart with an honest data
        resolution to derive from (`_LineChart`, `_EclipseChart`)
        overrides this to floor at its OWN sampling, so zoom can never
        outrun what its underlying series can actually resolve (the
        Laskar chart's absurd "1-year view of 1000-year-apart samples",
        owner screenshot ZOOM do 1 GOD.png)."""
        return min(
            full_span * defaults.OBSERVATORY_ZOOM_MIN_FRACTION,
            defaults.OBSERVATORY_ZOOM_MIN_SPAN_FLOOR,
        )

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
        min_span = self._zoom_floor(full_span)
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
        for value in self._y_ticks():
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
        for value in self._x_ticks():
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

    def set_y_scale(self, factor: float) -> None:
        """Fix round G, Task 1: the y-axis DISPLAY scale paired with
        set_y_fmt (e.g. x24 for the Days->Hours switch) — nice y-ticks
        are chosen in this scaled space so round numbers appear in the
        unit actually shown."""
        self._y_scale = factor
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

    def _data_stride(self) -> float | None:
        """Fix round R1a, Item 5 — the median x-gap actually present in
        the first visible series (every series on a given `_LineChart`
        shares the same x grid in this module — season/envelope/Laskar
        all read one bundle's `years`, day-length its own curve) — the
        chart's OWN sampling resolution, read straight off the data
        instead of a hand-picked per-chart constant (so it can never
        drift out of sync with a future bundle stride change)."""
        visible = self._visible()
        if not visible:
            return None
        return _median_gap(visible[0]["xs"])

    def _zoom_floor(self, full_span: float) -> float:
        """Fix round R1a, Item 5 — MAX ZOOM floored at the chart's own
        data resolution: one real sample gap is the tightest span that
        still shows genuine data rather than a straight interpolation
        between two distant points (the Laskar chart's 1000-year stride
        making a 5-year zoom "absurd", owner's own word). Falls back to
        the base heuristic when there are too few points to measure a
        gap from."""
        stride = self._data_stride()
        if stride is None or stride <= 0:
            return super()._zoom_floor(full_span)
        return min(stride, full_span)

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
        return self._x_fmt(value, self._is_zoomed())

    def _fmt_y(self, value: float) -> str:
        return self._y_fmt(value)

    def _legend(self) -> list[tuple[str, str]]:
        # Dedupe by label — the Laskar envelope's +/- band is two series
        # sharing one legend entry (Task 4).
        seen: dict[str, str] = {}
        for entry in self._visible():
            seen.setdefault(entry["label"], entry["color"])
        return list(seen.items())

    def _legend_values(self) -> dict[str, str]:
        """Fix round G, Task 3: per-label CURRENT VALUE for the enlarged
        view's extended legend — the value under the cursor while
        hovering, else the latest sample visible in the current view."""
        visible = self._visible()
        if not visible:
            return {}
        if self._hover is not None:
            rect = _plot_rect(self)
            span = self._xhi - self._xlo or 1.0
            data_x = self._xlo + (self._hover[0] - rect.left()) / rect.width() * span
        else:
            data_x = self._xhi
        values: dict[str, str] = {}
        for entry in visible:
            index = _nearest_index(entry["xs"], data_x)
            values[entry["label"]] = self._y_fmt(entry["ys"][index])
        return values

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
        zoomed_in = self._is_zoomed()
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
            index = _nearest_index(xs, data_x)
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


def _kind_color(family: str, kind: str) -> str:
    """Item 2's per-KIND eclipse color, falling back to the family's
    plain color for any type outside the ground-truthed vocabulary
    (defensive — `kind` is read straight off the Deep Time SQLite
    catalog, external data, Rule #7's documented exception)."""
    return defaults.OBSERVATORY_ECLIPSE_KIND_COLORS[family].get(
        kind, defaults.OBSERVATORY_ECLIPSE_COLORS[family]
    )


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

    def _zoom_floor(self, full_span: float) -> float:
        """Fix round R1a, Item 5 — MAX ZOOM floored at THIS mode's own
        resolution: the median gap between consecutive eclipse YEARS
        (deep mode — solar and lunar interleaved, a genuinely typical
        event-to-event spacing) or the density bucket width (fallback
        mode, `OBSERVATORY_BUNDLE_ECLIPSES`'s own bucket_years)."""
        if self._deep_mode:
            years = sorted(p[0] for p in self._solar + self._lunar)
        elif self._density is not None:
            years = self._density[0]
        else:
            return super()._zoom_floor(full_span)
        stride = _median_gap(years)
        if stride is None or stride <= 0:
            return super()._zoom_floor(full_span)
        return min(stride, full_span)

    def _fmt_x(self, value: float) -> str:
        return _year_label(value)

    def _fmt_y(self, value: float) -> str:
        # Item 6: thousands separator — the density fallback's bucket
        # counts run into the thousands over the multi-millennial span.
        return f"{value:.1f}" if self._deep_mode else f"{int(value):,}"

    def _legend(self) -> list[tuple[str, str]]:
        if not self._deep_mode:
            # The density fallback has no per-kind breakdown to plot —
            # the two family colors are all it can honestly show.
            colors = defaults.OBSERVATORY_ECLIPSE_COLORS
            return [
                (self._tr("Solar"), colors["solar"]),
                (self._tr("Lunar"), colors["lunar"]),
            ]
        # Item 2 (owner: "legenda svaka da bude obojana svojom bojom") —
        # deep mode colors each DOT by its real type, so the legend lists
        # every kind actually present in the fetched window (the full
        # scatter, not the current zoom — a legend should read the same
        # regardless of how far the user has zoomed).
        kind_colors = defaults.OBSERVATORY_ECLIPSE_KIND_COLORS
        entries: list[tuple[str, str]] = []
        for family, series in (("solar", self._solar), ("lunar", self._lunar)):
            present = {kind for _, magnitude, kind in series if magnitude is not None}
            for kind in kind_colors[family]:
                if kind in present:
                    entries.append((
                        f"{self._tr(family.capitalize())} · {self._tr(kind)}",
                        kind_colors[family][kind],
                    ))
        return entries

    def _legend_values(self) -> dict[str, str]:
        """Fix round G, Task 3: "current value" for a scatter/density
        chart reads naturally as a COUNT — events visible in the current
        view (deep mode) or the bucket nearest the view's right edge
        (density fallback)."""
        if self._deep_mode:
            solar_n = sum(
                1 for year, magnitude, _ in self._solar
                if magnitude is not None and self._xlo <= year <= self._xhi
            )
            lunar_n = sum(
                1 for year, magnitude, _ in self._lunar
                if magnitude is not None and self._xlo <= year <= self._xhi
            )
            return {self._tr("Solar"): f"{solar_n:,}", self._tr("Lunar"): f"{lunar_n:,}"}
        if self._density is None:
            return {}
        years, solar, lunar = self._density
        index = _nearest_index(years, self._xhi)
        return {
            self._tr("Solar"): f"{solar[index]:,}", self._tr("Lunar"): f"{lunar[index]:,}",
        }

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
                for year, magnitude, kind in series:
                    if magnitude is None:
                        continue
                    painter.setBrush(QColor(_kind_color(key, kind)))
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
        color = _kind_color(key, kind)
        lines = [
            _year_label(year),
            f"{self._tr(key.capitalize())} · {self._tr(kind)}",
            f"{self._tr('magnitude')}: {magnitude:.2f}",
        ]
        return px, [(px, py, color)], lines


class _DayLengthChart(_LineChart):
    """Chart 4. The x axis is a day-of-year int; Fix round G, Task 1
    (owner: "months -> days when zoomed tight") — the full (un-zoomed)
    year shows the 12 calendar MONTH starts, zoomed in it falls back to
    the generic day-pitch ladder, and labels reconstruct the true
    calendar date (`_ref_year`, leap-year correct) instead of the old
    crude day-of-year // 30 guess."""

    def __init__(self, x_title: str, y_title: str, year: int, y_fmt=None):
        super().__init__(x_title, y_title, y_fmt=y_fmt)
        self._ref_year = year

    def _month_starts(self) -> list[float]:
        return [
            date(self._ref_year, month, 1).timetuple().tm_yday
            for month in range(1, 13)
        ]

    def _x_ticks(self) -> list[float]:
        if self._is_zoomed():
            # Item 5's MIN TICK for this chart: never subdivide below a
            # whole calendar day — `_fmt_x` rounds to the nearest day, so
            # a finer rung would print the same "Mon D" label on two
            # adjacent gridlines (the day-length curve's own atomic unit
            # is one day; there's no such thing as half a day-of-year).
            return _nice_ticks(
                self._xlo, self._xhi, defaults.OBSERVATORY_TARGET_X_TICKS,
                min_step=defaults.OBSERVATORY_DAYLENGTH_MIN_TICK_DAYS,
            )
        return [
            value for value in self._month_starts()
            if self._xlo - 1e-6 <= value <= self._xhi + 1e-6
        ]

    def _fmt_x(self, value: float) -> str:
        day = date(self._ref_year, 1, 1) + timedelta(days=round(value) - 1)
        if self._is_zoomed():
            return f"{_MONTHS[day.month - 1]} {day.day}"
        return _MONTHS[day.month - 1]


# Fix round G, Task 2: the last-used per-chart splitter sizes for THIS
# APP RUN only — a plain module-level cache, cleared on restart, since
# there is no existing settings key for this dialog's own geometry to
# piggyback on (it isn't persisted across opens either).
_last_splitter_sizes: list[int] | None = None


def _build_info_panel(
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
    panel.setStyleSheet(
        f"background: {defaults.THEME_COLORS['surface_1']};"
        f"border-radius: {defaults.THEME_RADIUS_CARD_PX}px;"
    )
    layout = QVBoxLayout(panel)
    layout.setContentsMargins(12, 12, 12, 12)
    layout.setSpacing(defaults.GUIDE_SPACING_PX)
    layout.addWidget(QLabel(f"<b>{tr('About this chart')}</b>"))
    if caption:
        text = QLabel(caption)
        text.setWordWrap(True)
        layout.addWidget(text)
    for label, color, description in info_rows or []:
        row = QHBoxLayout()
        chip = QLabel()
        chip.setFixedSize(12, 12)
        chip.setStyleSheet(f"background: {color}; border-radius: 6px; margin-top: 3px;")
        row.addWidget(chip, alignment=Qt.AlignmentFlag.AlignTop)
        column = QVBoxLayout()
        column.setSpacing(0)
        name = QLabel(f"<b>{label}</b>")
        column.addWidget(name)
        description_label = QLabel(description)
        description_label.setWordWrap(True)
        description_label.setStyleSheet(f"color: {defaults.OBSERVATORY_MUTED_COLOR};")
        column.addWidget(description_label)
        row.addLayout(column, stretch=1)
        layout.addLayout(row)
    layout.addStretch(1)
    return panel


class _EnlargeDialog(QDialog):
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
        self, panel: QWidget, chart: _ChartBase, title: str,
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

        self._info_panel = _build_info_panel(caption, info_rows, tr)
        self._info_panel.setFixedWidth(defaults.OBSERVATORY_INFO_PANEL_WIDTH_PX)
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
            chip.setFixedSize(12, 12)
            chip.setStyleSheet(f"background: {color}; border-radius: 6px;")
            self._legend_row.addWidget(chip)
            value = values.get(label)
            text = QLabel(f"{label}: {value}" if value is not None else label)
            text.setStyleSheet(
                f"color: {defaults.OBSERVATORY_INK_COLOR}; font-weight: 600;"
            )
            self._legend_row.addWidget(text)
            self._legend_row.addSpacing(14)
        self._legend_row.addStretch(1)


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
        # NON-MODAL lifecycle (ITEM 1, R4 owner instruction batch
        # 2026-07-20): the controller `.show()`s this dialog instead of
        # `.exec()`ing it — the dial stays interactive while it is
        # open. The controller keeps the ONE live instance as an
        # attribute and clears it on this dialog's `finished` signal;
        # WA_DeleteOnClose tears the C++ object down the moment the
        # window closes. Unrelated to `_EnlargeDialog`'s own explicit
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

        data = ObservatoryData()
        column = QVBoxLayout(self)

        astro_year = real_year(now.year, cycles)
        anno = astro_year + constants.ANNO_LUCIS_OFFSET
        header = QLabel(
            f"<b>{self._tr('Observatory')}</b> — "
            f"{_year_label(astro_year)} · {self._tr('A.L.')} {anno:,}"
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
        span_label = f"{_year_label(first)}–{_year_label(last)}"
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
        envelope = _LineChart(
            self._tr("year"), self._tr("light − dark (days)"),
            y_fmt=_days_fmt,
        )
        envelope.set_series([{
            "key": "envelope", "label": self._tr("light − dark"),
            "color": defaults.OBSERVATORY_SERIES_COLORS["light"],
            "xs": series["years"], "ys": light_minus_dark,
        }])
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
        day_chart = _DayLengthChart(
            self._tr("day of year"), self._tr("day length"), now.year, y_fmt=_hm,
        )
        day_chart.set_series([{
            "key": "daylength", "label": self._tr("Day length"),
            "color": defaults.OBSERVATORY_DAYLENGTH_COLOR,
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
        laskar_caption = self._tr(
            "Analytic orbital solution (La2004) — amplitude trend only; "
            "exact dates unreliable beyond the measured window. Shown: "
            "{span}."
        ).format(
            span=f"{_year_label(laskar['years'][0])}–{_year_label(laskar['years'][-1])}"
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

    # Fix round G, Task 2 + 3: one panel per chart (title + filter row +
    # chart [+ caption]), added as a QSplitter pane, with a Collapse and
    # an "Enlarge" button appended to the filter row (a bare right-
    # aligned row is created for charts that don't already have one).
    def _add_panel(
        self, title: str, chart: _ChartBase, *,
        filter_row: QHBoxLayout | None = None, caption: str | None = None,
        info_rows: list[tuple[str, str, str]] | None = None,
    ) -> None:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(defaults.GUIDE_SPACING_PX)
        title_label = self._section(title)
        layout.addWidget(title_label)
        # Item 3: the ONE place `_EnlargeDialog` reaches to hide/restore
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
        self, chart: _ChartBase, caption_label: QLabel | None,
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
        self, panel: QWidget, chart: _ChartBase, title: str,
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
        `_EnlargeDialog` already calls `.show()` at the end of its own
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
        dialog = _EnlargeDialog(
            panel, chart, title, caption, self._tr, info_rows, parent=self
        )
        dialog.finished.connect(
            lambda _result: self._close_enlarged(
                dialog, panel, index, sizes, enlarge_button
            )
        )

    def _close_enlarged(
        self, dialog: "_EnlargeDialog", panel: QWidget, index: int,
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
                f"color: {defaults.OBSERVATORY_SERIES_COLORS[key]};"
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
        kind_colors = defaults.OBSERVATORY_ECLIPSE_KIND_COLORS
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


_MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun",
           "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
