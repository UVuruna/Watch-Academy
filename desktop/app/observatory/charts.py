"""THE OBSERVATORY'S CHARTS — the four plots and the graph paper.

One `ChartBase` and three subclasses over it: `LineChart` (the day-length
and eclipse-count curves), `EclipseChart` (one mark per event, coloured
by kind) and `DayLengthChart` (a `LineChart` that knows the months). The
free functions above them are the graph paper every plot draws on — the
plot rectangle, the two axis mappings, the "nice" tick steps, the label
formatters.

Split out of a 1,697-line `app/observatory.py` on 2026-08-18 (R12 of the
OOP audit): charts, panels and the dialog were three responsibilities in
one file, and this is the one that is pure geometry over data — it opens
no window and holds no session state.

Layer: app. Documentation: __about/charts.md.
"""

import bisect
import math
from datetime import date, timedelta

from PySide6.QtCore import QPointF, QRectF, QSize, Qt
from PySide6.QtGui import QColor, QPainter, QPen, QPolygonF
from PySide6.QtWidgets import QWidget
from config import defaults, palette

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


def year_label(year: float, zoomed: bool = False) -> str:
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


class ChartBase(QWidget):
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
        resolution to derive from (`LineChart`, `EclipseChart`)
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
        painter.fillRect(self.rect(), QColor(palette.OBSERVATORY_SURFACE_COLOR))
        font = painter.font()
        font.setPixelSize(11)
        painter.setFont(font)
        if not self._has_data():
            painter.setPen(QColor(palette.OBSERVATORY_MUTED_COLOR))
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
        grid = QColor(palette.OBSERVATORY_GRID_COLOR)
        muted = QColor(palette.OBSERVATORY_MUTED_COLOR)
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
            painter.setPen(QColor(palette.OBSERVATORY_INK_COLOR))
            width = painter.fontMetrics().horizontalAdvance(label)
            painter.drawText(int(x) + 12, int(y), width + 8, 14,
                             Qt.AlignmentFlag.AlignLeft, label)
            x += 12 + width + 20
            if x > rect.right() - 60:
                x = rect.left() + 8
                y += 16

    def _draw_crosshair(self, painter: QPainter, rect: QRectF, probe: tuple) -> None:
        snap_x, marks, lines = probe
        cross = QColor(palette.OBSERVATORY_CROSSHAIR_COLOR)
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
        panel = QColor(palette.OBSERVATORY_SURFACE_COLOR)
        panel.setAlpha(235)
        painter.setBrush(panel)
        painter.setPen(QPen(QColor(palette.OBSERVATORY_GRID_COLOR), 1))
        painter.drawRoundedRect(QRectF(bx, by, box_w, box_h), 6, 6)
        painter.setPen(QColor(palette.OBSERVATORY_INK_COLOR))
        for index, line in enumerate(lines):
            painter.drawText(
                int(bx) + 7, int(by) + 4 + index * 15, box_w - 14, 15,
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, line,
            )


class LineChart(ChartBase):
    """A multi-series line chart with fixed per-series colors, toggleable
    visibility (identity kept), optional shaded era bands + labelled
    verticals, and a crosshair readout (nearest sample by x)."""

    def __init__(self, x_title: str, y_title: str, y_fmt=None, x_fmt=None,
                 diff_pair: tuple[str, str] | None = None):
        super().__init__()
        self._x_title = x_title
        self._y_title = y_title
        self._y_fmt = y_fmt or (lambda v: f"{v:g}")
        self._x_fmt = x_fmt or year_label
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
        the first visible series (every series on a given `LineChart`
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
    return palette.OBSERVATORY_ECLIPSE_KIND_COLORS[family].get(
        kind, palette.OBSERVATORY_ECLIPSE_COLORS[family]
    )


class EclipseChart(ChartBase):
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
        return year_label(value)

    def _fmt_y(self, value: float) -> str:
        # Item 6: thousands separator — the density fallback's bucket
        # counts run into the thousands over the multi-millennial span.
        return f"{value:.1f}" if self._deep_mode else f"{int(value):,}"

    def _legend(self) -> list[tuple[str, str]]:
        if not self._deep_mode:
            # The density fallback has no per-kind breakdown to plot —
            # the two family colors are all it can honestly show.
            colors = palette.OBSERVATORY_ECLIPSE_COLORS
            return [
                (self._tr("Solar"), colors["solar"]),
                (self._tr("Lunar"), colors["lunar"]),
            ]
        # Item 2 (owner: "legenda svaka da bude obojana svojom bojom") —
        # deep mode colors each DOT by its real type, so the legend lists
        # every kind actually present in the fetched window (the full
        # scatter, not the current zoom — a legend should read the same
        # regardless of how far the user has zoomed).
        kind_colors = palette.OBSERVATORY_ECLIPSE_KIND_COLORS
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
        colors = palette.OBSERVATORY_ECLIPSE_COLORS
        if self._now_year is not None and self._xlo <= self._now_year <= self._xhi:
            px = _xmap(rect, self._xlo, self._xhi, self._now_year)
            painter.setPen(QPen(QColor(palette.OBSERVATORY_NOW_MARK_COLOR), 1))
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
            year_label(year),
            f"{self._tr(key.capitalize())} · {self._tr(kind)}",
            f"{self._tr('magnitude')}: {magnitude:.2f}",
        ]
        return px, [(px, py, color)], lines


class DayLengthChart(LineChart):
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


_MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun",
           "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
