# Observatory

**Script:** [Observatory (script)](../observatory.py) · **Flow:** [diagram](../__flow/observatory.md)

## Purpose
The statistics sibling of the Encyclopedia — a non-modal right-click
window (🔭 Observatory…) of dark, QPainter-drawn, interactive charts over
the long ephemeris data. FIVE charts, each its own panel in a vertical
`QSplitter`: season-duration oscillations (per-series checkboxes), the
light − dark envelope (the Anno Lucis dawn, the Age of Light/Darkness
bands, every measured peak labeled), the eclipse timeline (exact nearest
past/next eclipses when the Deep Time pack is installed, else the
bundled density), the current location's day-length curve, and the
La2004 Laskar long envelope over ±200,000 years (amplitude trend only —
charts-only, Time Travel itself never leaves the precise pack span).
Series data reads only the committed bundles in `data/observatory.py` —
the window opens instantly and never needs `deep_time.sqlite`.

## THIS FILE IS A DOCUMENTED GOD-FILE (Rule #20 ratchet)
`observatory.py` is 1,646 lines — past the ~1,000-line Violation
threshold — and carries a `tests/test_structure_law.py` ratchet entry.
Two natural seams for a future split: the shared chart-canvas machinery
(`_ChartBase`/`_LineChart`/`_EclipseChart`/`_DayLengthChart` — zoom, pan,
axis ticks, legend, crosshair) versus the dialog shell (`ObservatoryDialog`/
`_EnlargeDialog`/`_build_info_panel` — panels, splitter, filters,
enlarge/collapse). No split has been attempted; document as-is.

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
- [Observatory Data](../../data/__about/observatory.md) — the committed
  series bundles, `light_dark_extrema()`, the Laskar envelope bundle
- [Deep Time Repository](../../data/__about/deep_time.md) — OPTIONAL:
  exact nearest eclipse instants when the pack is installed
- [Sun (core)](../../core/__about/sun.md) — `day_length_curve`
- [Deep Time (core)](../../core/__about/deep_time.md) — `julian_day_of`, `real_year`
- [Theme](theme.md) — the dark dialog surface, `size_to_screen`
- [UI Style](ui_style.md) — the vivid Close pill
- [Config (folder)](../../config/___config.md) — the `OBSERVATORY_*`
  palette and geometry tokens

### Used by
- [Watch Controller](controller.md) — `_open_observatory()` opens (or
  raises the live) instance with the EFFECTIVE `(moment, observer, tz,
  cycles)` — the frozen Time Travel simulation while one is active, else
  the live present — and the optional Deep Time pack

## Classes

### `_ChartBase(QWidget)`
The shared canvas: surface fill, axis frame, grid, legend, crosshair,
plus the zoom/pan/reset machinery every chart inherits (`wheelEvent`,
mouse press/move/release for drag-to-pan, double-click reset,
`_zoom_at`/`_reset_view`). Overridable seams: `_fit_y_to_view()`,
`_x_ticks()`/`_y_ticks()`, `_legend_values()` (the enlarged view's
current-value readout), `_zoom_floor(full_span)`.

### `_LineChart(_ChartBase)`
A generic multi-series line chart — fixed per-series colors, toggleable
visibility, optional shaded bands and labeled vertical marks (thinned at
full zoom to avoid label collisions), a deduped legend, a crosshair
readout with an optional delta line. Used by charts 1, 2, 4 and 5.
`_zoom_floor` derives from `_data_stride()`, the median x-gap of the
first visible series.

### `_EclipseChart(_ChartBase)`
Chart 3. With the Deep Time pack: a magnitude scatter of the nearest
eclipses around the moment, colored per real TYPE (solar
yellow→orange→red by category, lunar navy→blue→cyan). Without it: the
bundled density (counts per bucket) + a per-type summary in the info
panel. `_zoom_floor` derives from the median gap between eclipse years
(or the density bucket width).

### `_DayLengthChart(_LineChart)`
Chart 4. x is day-of-year; `_x_ticks()` shows the 12 calendar month
starts when un-zoomed, else the generic tick ladder; `_fmt_x()`
reconstructs the true leap-year-correct calendar date for its labels.

### `_EnlargeDialog(QDialog)`
The "Enlarge" target for any panel — TEMPORARILY REPARENTS the SAME
panel widget in (`panel.setParent(self)`) and back to its splitter slot
on close, so zoom/pan/checkbox state carries for free in both
directions; adds an extended legend (current-value readout per series,
polled) and a collapsible info panel (`_build_info_panel`). Does NOT set
`WA_DeleteOnClose` (a real fixed crash, see Design Decisions) —
`_close_enlarged` reparents `panel` back FIRST, then calls
`dialog.deleteLater()` explicitly.

### `ObservatoryDialog(QDialog)`
Normal resizable, non-modal window (`WA_DeleteOnClose` — safe here,
since this dialog only ever LENDS a panel out, never has one reparented
INTO it). A `QSplitter` column of the five titled chart panels inside a
`QScrollArea`, under a dual-calendar header. `_add_panel()` builds one
panel (title + filter row + chart [+ caption]) and registers its
Collapse/Enlarge buttons; `_toggle_collapsed()` hides a chart down to
just its title+filter row; `_open_enlarged()`/`_close_enlarged()` drive
the reparent-in/reparent-out dance.

## Design Decisions
- **QPainter draws every chart** — no plotting dependency (same choice
  as [Report](report.md)); the committed, decimated bundles mean the
  window opens instantly and works on a partial installation.
- **The peak finder is WINDOWED, not immediate-neighbor** — the
  bin-mean decimation's own rounding noise otherwise flags dozens of
  spurious extrema clustered around every true peak; a candidate must be
  the most extreme point within a configured year window on each side.
- **A fixed crash, now regression-pinned**: `_EnlargeDialog` used to set
  `WA_DeleteOnClose`, which queued the DIALOG's own C++ destruction via
  `deleteLater()` — since the reparented `panel` was a real Qt child of
  it, that queued deletion could (and did) destroy `panel` before
  `_open_enlarged` reinserted it (`RuntimeError: Internal C++ object
  already deleted`). Fixed by reparenting `panel` back to the splitter
  BEFORE calling `deleteLater()` on the dialog, never after; pinned by a
  real (un-mocked) `QDialog.exec()`-driven test cycling all 5 charts
  twice.
