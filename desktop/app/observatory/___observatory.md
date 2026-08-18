# app/observatory/

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

Until 2026-08-18 all of that was ONE 1,697-line module. The [OOP
audit](../../../docs/AUDIT-OOP-2026-08-18.md) measured three
responsibilities in it and R12 cut them apart: the plots, the boxes that
sit beside a plot, and the window they live in.

## Files

| File | Tier | One line |
|------|------|----------|
| `charts.py` | Algorithmic | the four plots and the graph paper under them — zoom, pan, ticks, legend, crosshair — [about](__about/charts.md) · [flow](__flow/charts.md) |
| `panels.py` | Standard | what sits BESIDE a chart: the info box, the `ChartPane`, the Enlarge target — [about](__about/panels.md) |
| `dialog.py` | Algorithmic | the window: splitter, chart roster, controls, the Enlarge route — [about](__about/dialog.md) · [flow](__flow/dialog.md) |
| `__init__.py` | Trivial | the package's one public name, `ObservatoryDialog` |

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
- [Theme](../__about/theme.md) — the dark dialog surface, `size_to_screen`
- [UI Style](../__about/ui_style.md) — the vivid Close pill
- [Config (folder)](../../config/___config.md) — the `OBSERVATORY_*`
  palette and geometry tokens


### Used by
- [Watch Controller](../__about/controller.md) — `_open_observatory()` opens (or
  raises the live) instance with the EFFECTIVE `(moment, observer, tz,
  cycles)` — the frozen Time Travel simulation while one is active, else
  the live present — and the optional Deep Time pack


## Design Decisions
- **QPainter draws every chart** — no plotting dependency (same choice
  as [Report](../__about/report.md)); the committed, decimated bundles mean the
  window opens instantly and works on a partial installation.
- **The peak finder is WINDOWED, not immediate-neighbor** — the
  bin-mean decimation's own rounding noise otherwise flags dozens of
  spurious extrema clustered around every true peak; a candidate must be
  the most extreme point within a configured year window on each side.
- **A fixed crash, now regression-pinned**: `EnlargeDialog` used to set
  `WA_DeleteOnClose`, which queued the DIALOG's own C++ destruction via
  `deleteLater()` — since the reparented `panel` was a real Qt child of
  it, that queued deletion could (and did) destroy `panel` before
  `_open_enlarged` reinserted it (`RuntimeError: Internal C++ object
  already deleted`). Fixed by reparenting `panel` back to the splitter
  BEFORE calling `deleteLater()` on the dialog, never after; pinned by a
  real (un-mocked) `QDialog.exec()`-driven test cycling all 5 charts
  twice.
