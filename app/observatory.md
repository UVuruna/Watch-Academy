# Observatory

**Script:** [Observatory (script)](observatory.py)

## Purpose
The STATISTICS sibling of the Encyclopedia (owner 2026-07-16: "kao
enciklopedija, samo sa statistikom") — a right-click window (🔭
Observatory…, beside 🏛️ Encyclopedia…) of dark, QPainter-drawn,
interactive charts over the long ephemeris data. FIVE charts:

1. **Season-duration oscillations** — the four northern astronomical
   seasons' lengths over the millennia, with PER-SERIES CHECKBOXES
   above (the four seasons + the light/dark half-year pair — the
   owner's own Anno Lucis graph, now live in-app). Its crosshair also
   reports the light/dark DELTA, in whichever unit the Days/Hours
   switch (below) picks — the series' own axis stays in days.
2. **The light − dark envelope** — the signed light−dark half-year over
   the whole measured span, with the ANNO LUCIS dawn (4079 BCE), the
   Age of Light/Darkness bands, and EVERY measured light/dark peak
   labeled with its year and value (not just the sealed era marks —
   `data.light_dark_extrema()`, Fix round D Task 3). The y-axis/
   crosshair follow the Days/Hours switch (Task 2).
3. **The eclipse timeline** — the nearest past/next solar and lunar
   eclipses from the current (or TRAVELED) moment when the Deep Time
   pack is installed (magnitude scatter, the moment marked); without the
   pack, the bundled density (counts per bucket) + the per-type summary.
4. **The location's day-length curve** — daylight minutes over the year
   at the current (or traveled) observer, computed live via
   `core.sun.day_length_curve`.
5. **The Laskar long envelope** (Fix round D, Task 4 — ROADMAP 15a2
   sealed) — the La2004 amplitude envelope (± days) over the owner's
   ±200,000-year window: the gold amplitude band, the signed oscillation
   inside it, the DE441-measured window (−13k…+17k) shaded, the coming
   eccentricity minimum (~+28,000, ~±1.1 d) labeled. A caption states
   the doctrine: analytic solution, amplitude trend only, dates
   unreliable beyond the measured window. Charts-only — Time Travel
   never leaves the precise −13000…+17000 pack.

## Chart quality rules (the project's dataviz doctrine)
Dark-first on the theme surface; ONE y-axis per chart (never dual);
series colors FIXED per series (the four seasons wear their canonical
cross-wheel element hues, light/dark gold vs slate — never re-colored
when a checkbox hides a series); thin marks, a recessive grid, a legend
always drawn (deduped by label — the Laskar ± band shares one entry),
direct labels on the era/peak marks; a crosshair hover readout on every
chart; the filter row sits ABOVE the charts, not scattered.

### Zoom, pan, units (Fix round D, owner verdicts 2026-07-19)
Every chart (`_ChartBase`) supports mouse-wheel zoom centered on the
cursor's x (`OBSERVATORY_ZOOM_FACTOR` per notch, clamped to
`OBSERVATORY_ZOOM_MIN_FRACTION` of the full span), drag-to-pan with the
left button while zoomed, and a double-click reset to the full span.
Every zoom/pan change re-fits the y axis to whatever x slice is visible
(`_fit_y_to_view`, `OBSERVATORY_Y_FIT_PAD_FRACTION` padding) — a fixed
y range (day-length's 0..24h) applies only at the un-zoomed full view.
A Days/Hours combo in the season filter row (`OBSERVATORY_UNITS_DEFAULT`)
is a pure ×24 DISPLAY transform (`_LineChart.set_y_fmt`/`set_diff_fmt`)
— the underlying series never change.

## Time Travel interplay
The controller passes the EFFECTIVE `(moment, observer, tz, cycles)` —
the frozen simulation tuple when Time Travel is active, else the live
present. So chart 3's "nearest" is measured from the traveled moment and
chart 4's curve is the traveled observer's year (the proxy Gregorian
year — day length is identical across the 400-year proxy cycle).

## Connections

### Uses
- [Observatory Data](../data/observatory.md) — the committed series
  bundles (always present; never needs deep_time.sqlite), including
  `light_dark_extrema()` and the Laskar envelope bundle (Fix round D)
- [Deep Time Repository](../data/deep_time.md) — OPTIONAL: exact nearest
  eclipse instants for chart 3 when the pack is installed
- [Sun](../core/sun.md) — `day_length_curve` for chart 4
- [Deep Time (core)](../core/deep_time.md) — `julian_day_of`,
  `real_year` (the moment → Julian Day / real year)
- [Theme](theme.md) — the dark dialog surface (`apply_theme`)
- [UI Style](ui_style.md) — the vivid Close pill
- [Config (folder)](../config/___config.md) — the `OBSERVATORY_*`
  palette + geometry tokens

### Used by
- [App Controller](controller.md) — opens it from the menu with the
  effective moment/observer and the optional Deep Time pack

## Classes

### `_ChartBase`
The shared canvas: surface fill, axis frame, grid, legend, crosshair —
and, since Fix round D, the zoom/pan/reset machinery every chart
inherits: `wheelEvent` (zoom at cursor), `mousePressEvent`/
`mouseMoveEvent`/`mouseReleaseEvent` (drag-to-pan), `mouseDoubleClickEvent`
(reset), `_zoom_at(x_px, factor)` and `_reset_view()` (the testable
pure-math core), and the `_fit_y_to_view()` hook subclasses override to
auto-fit the y axis to the current x view.

### `_LineChart`
A generic multi-series line chart: fixed per-series colors, toggleable
visibility (identity kept when hidden), optional shaded bands and
labelled vertical marks (sorted by x, thinned at full zoom when they
would collide — `OBSERVATORY_VMARK_MIN_SPACING_PX`), a deduped legend,
and a crosshair readout (nearest sample by x, plus an optional
`diff_pair` delta line). `set_y_fmt`/`set_y_title`/`set_diff_fmt` are
the Days/Hours switch's pure display hooks. Used by charts 1, 2, 4 and 5.

### `_EclipseChart`
Chart 3. With the Deep Time pack: a magnitude scatter of the nearest
`OBSERVATORY_ECLIPSE_WINDOW_N` past/next solar and lunar eclipses around
the moment, the moment drawn as a vertical line, crosshair readout of
the eclipse under the cursor. Without it: the bundled density (solar /
lunar counts per bucket) over the whole span + a "full installation"
note. Its own `_fit_y_to_view()` fits to the scatter/density visible in
the current zoom.

### ObservatoryDialog
Normal resizable window; a scroll column of the five titled chart
sections (chart 1 preceded by its checkbox + Days/Hours filter row)
under a dual-calendar header line for the moment. Computes the
day-length curve once in `__init__`; wires the units combo only after
every chart it touches (`_envelope`, `_season_chart`) exists.

## Design Decisions
QPainter draws every chart — no plotting dependency (the same choice as
the Report). The series bundles are decimated and committed, so the
window opens instantly and works on the partial installation; only
chart 3's EXACT nearest-eclipse mode needs the optional Deep Time pack,
degrading to the bundled density otherwise (the documented split).

The peak finder (`ObservatoryData.light_dark_extrema`) is windowed, not
a bare immediate-neighbor comparison: the bin-mean decimation's own
rounding noise otherwise flags dozens of spurious extrema clustered
around every true peak (measured: 27 "peaks" agreeing to 3 decimals
within a few bins of each other). A candidate must be the most extreme
point within `OBSERVATORY_EXTREMA_WINDOW_YEARS` on each side, with
surviving near-duplicates from a flat plateau merged to the single most
extreme point — over the bundled span this settles to the 3 physically
real turning points (2 dark peaks, 1 light peak).
