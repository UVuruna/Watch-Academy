# Charts

**Script:** [Charts (script)](../charts.py) · **Flow:**
[diagram](../__flow/charts.md)

## Purpose
THE OBSERVATORY'S CHARTS — the four plots and the graph paper they are
drawn on. `ChartBase` plus three subclasses, and above them the free
functions every plot shares: the plot rectangle, the two axis mappings,
the "nice" 1-2-5 tick ladder, the label formatters.

This is the half of the old `app/observatory.py` that is pure geometry
over data: it opens no window and holds no session state (R12 of the
[OOP audit](../../../../docs/AUDIT-OOP-2026-08-18.md), 2026-08-18).

## Every chart supports (Fix round D)
Mouse-wheel zoom centered on the cursor, drag-to-pan while zoomed, and a
double-click reset — the y axis auto-fits whatever x slice is visible on
every change. A Days/Hours combo is a pure ×24 DISPLAY transform over
the season/envelope charts; the underlying series never change. Axis
tick pitch adapts to the current view (a "nice number" 1-2-5 ladder,
`_nice_step`/`_nice_ticks`), and each chart's own MAX ZOOM floors at
something derived from its own data sampling stride, never a single
global constant.


## Connections

### Uses
- [Observatory Data](../../../data/__about/observatory.md) — the
  committed series bundles
- [Config (folder)](../../../config/___config.md) — the `OBSERVATORY_*`
  palette and geometry tokens

### Used by
- [Panels](panels.md) — `EnlargeDialog` hosts a `ChartBase`
- [Dialog](dialog.md) — builds one instance per panel
- `tests/test_observatory.py` — `ChartBase`, `_nice_step`, `year_label`

### `ChartBase(QWidget)`
The shared canvas: surface fill, axis frame, grid, legend, crosshair,
plus the zoom/pan/reset machinery every chart inherits (`wheelEvent`,
mouse press/move/release for drag-to-pan, double-click reset,
`_zoom_at`/`_reset_view`). Overridable seams: `_fit_y_to_view()`,
`_x_ticks()`/`_y_ticks()`, `_legend_values()` (the enlarged view's
current-value readout), `_zoom_floor(full_span)`.

### `LineChart(ChartBase)`
A generic multi-series line chart — fixed per-series colors, toggleable
visibility, optional shaded bands and labeled vertical marks (thinned at
full zoom to avoid label collisions), a deduped legend, a crosshair
readout with an optional delta line. Used by charts 1, 2, 4 and 5.
`_zoom_floor` derives from `_data_stride()`, the median x-gap of the
first visible series.

### `EclipseChart(ChartBase)`
Chart 3. With the Deep Time pack: a magnitude scatter of the nearest
eclipses around the moment, colored per real TYPE (solar
yellow→orange→red by category, lunar navy→blue→cyan). Without it: the
bundled density (counts per bucket) + a per-type summary in the info
panel. `_zoom_floor` derives from the median gap between eclipse years
(or the density bucket width).

### `DayLengthChart(LineChart)`
Chart 4. x is day-of-year; `_x_ticks()` shows the 12 calendar month
starts when un-zoomed, else the generic tick ladder; `_fmt_x()`
reconstructs the true leap-year-correct calendar date for its labels.

## Design Decisions
- **QPainter draws every chart** — no plotting dependency (same choice
  as [Report](../../__about/report.md)); the committed, decimated
  bundles mean the window opens instantly and works on a partial
  installation.
- **The peak finder is WINDOWED, not immediate-neighbor** — the
  bin-mean decimation's own rounding noise otherwise flags dozens of
  spurious extrema clustered around every true peak; a candidate must be
  the most extreme point within a configured year window on each side.
- **`year_label` is PUBLIC** because the dialog's header reads it too. A
  private name imported across a module boundary is the defect finding
  L1 recorded elsewhere in the same audit.
