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
chart; the filter row sits ABOVE the charts, not scattered, and ends
with an "Enlarge" button (Fix round G, Task 3) on every chart.

### Zoom, pan, units (Fix round D, owner verdicts 2026-07-19)
Every chart (`_ChartBase`) supports mouse-wheel zoom centered on the
cursor's x (`OBSERVATORY_ZOOM_FACTOR` per notch, clamped by
`_min_zoom_span` — see Fix round G below), drag-to-pan with the
left button while zoomed, and a double-click reset to the full span.
Every zoom/pan change re-fits the y axis to whatever x slice is visible
(`_fit_y_to_view`, `OBSERVATORY_Y_FIT_PAD_FRACTION` padding) — a fixed
y range (day-length's 0..24h) applies only at the un-zoomed full view.
A Days/Hours combo in the season filter row (`OBSERVATORY_UNITS_DEFAULT`)
is a pure ×24 DISPLAY transform (`_LineChart.set_y_fmt`/`set_diff_fmt`)
— the underlying series never change.

### Adaptive ticks, adjustable height, enlarge (Fix round G, owner verdicts 2026-07-19)
Three owner asks from the same screenshot batch (slika 8 + addendum):

**Task 1 — adaptive axis ticks.** The x/y tick PITCH now adapts to the
CURRENT view on every chart, via a generic "nice number" ladder
(`_nice_step` — the classic 1-2-5-per-decade progression, generated
arithmetically so it covers any magnitude, not a hardcoded list) picking
the smallest rung that keeps the tick count at/under a config target
(`OBSERVATORY_TARGET_X_TICKS`/`_Y_TICKS`); once even the ladder's finest
rung still exceeds the target (a span tighter than makes sense to
subdivide further), that rung is used anyway. `_ChartBase._x_ticks()`/
`_y_ticks()` replace the old direct `_nice_ticks(...)` calls in
`_draw_axes` and are the overridable seam. The Y path is additionally
SCALE-AWARE (`_y_scale`, paired with the Days/Hours `set_y_fmt` — see
`_LineChart.set_y_scale`): nice numbers are chosen in the DISPLAYED unit
(hours) then converted back to the raw (days) axis coordinate, so a
switch to Hours doesn't leave odd day-fraction ticks. The day-length
chart (`_DayLengthChart`) gets its own x-tick override: the full
un-zoomed year shows the 12 calendar MONTH starts (leap-year correct via
real `date` arithmetic, replacing the old crude `day // 30` guess),
zoomed in tight it falls back to the generic day-pitch ladder with
"Mon D" labels. Reaching a 1-year pitch at all requires zooming past
where the OLD fraction-only clamp (`OBSERVATORY_ZOOM_MIN_FRACTION`,
1% of the full span) would ever go on the multi-millennial charts — 1%
of ~30,000 years is still ~300 years — so `_min_zoom_span` now clamps to
whichever is SMALLER, that fraction OR the new absolute
`OBSERVATORY_ZOOM_MIN_SPAN_FLOOR` (6 units); on the season/envelope/
Laskar/eclipse-density charts the floor wins, letting max zoom reach a
handful of years where the target-8 ladder naturally bottoms out at a
1-year pitch (owner: "na max zumu TICK na 1 GODINU"). NOTE for the
owner: the season/envelope bundle is itself BIN-MEAN DECIMATED at a
20-year stride (`SEASON_BIN_YEARS`, `setup/make_observatory.py`) — a
separate, un-touched concern from the axis-tick pitch fixed here; zoomed
past that stride the plotted LINE still only bends every 20 years even
though the grid itself is now finer.

**Task 2 — adjustable chart height.** The five chart sections now live
in one `QSplitter(Qt.Orientation.Vertical)` (`ObservatoryDialog._add_panel`),
one panel (title + filter row + chart [+ caption]) per pane, dragged via
the handles the shared theme now styles (`app/theme.py`
`QSplitter::handle`). `setChildrenCollapsible(False)` keeps every chart
at/above its `OBSERVATORY_CHART_MIN_HEIGHT_PX` floor. The splitter sits
INSIDE the existing `QScrollArea` unchanged — its `minimumSizeHint` is
the sum of its panels', so once that exceeds the viewport the scroll
area shows its bar exactly as the old plain `QVBoxLayout` did (verified
with an offscreen render at a small dialog size,
`test_dialog_with_splitter_renders_at_a_small_size`). Per-chart heights
persist for the SESSION only — a module-level cache
(`_last_splitter_sizes`, restored via `setSizes()` on the next open,
updated on `splitterMoved`) — no settings key, matching that this
dialog's own window geometry was never persisted across opens either.

**Task 3 — enlarge.** Every panel's filter row ends with an "Enlarge"
button opening `_EnlargeDialog`, a maximized window that TEMPORARILY
REPARENTS the SAME panel widget (`panel.setParent(self)`) in on open and
back to its original splitter slot on close
(`ObservatoryDialog._open_enlarged`, which records the splitter index
before detaching). Reparenting the live widgets — instead of building a
parallel copy fed from a shared model — was the cleanest fit for how
this module is already shaped: zoom (`_xlo`/`_xhi`), pan and every
checkbox's state already live directly ON these Qt widgets, there is no
separate state object to hand to a second view, and Qt widgets are cheap
to reparent at runtime. The result: zoom/pan/checkboxes carry into the
enlarged view and back out for free, with no synchronization code in
either direction, and Task 1's ticks work identically since it is
IDENTICALLY the same `_ChartBase` instance. `_EnlargeDialog` adds an
EXTENDED LEGEND (every series' color chip plus a "current value"
readout — the crosshair's value while hovering, else the sample nearest
the view's right edge; `_ChartBase._legend_values()`, refreshed on a
200ms `QTimer` poll rather than new signal plumbing on the shared chart
base) and an INFO STRIP (the title plus whatever caption string the
panel already carries — the Laskar doctrine line, the eclipse install
note; charts without one just show the title, never an invented one).
`WA_DeleteOnClose` plus stopping the legend timer on `finished` avoid
leaking a background timer per enlarge/close cycle. Esc / the native
close box use `QDialog`'s default reject-on-Escape — unmodified,
matching every other dialog in the app.

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
auto-fit the y axis to the current x view. Fix round G adds
`_is_zoomed()` (shared by the vmark-thinning and the day-length month/
day switch), the overridable `_x_ticks()`/`_y_ticks()` seam (Task 1) and
`_legend_values()` (the enlarged view's per-label current-value readout,
Task 3 — empty by default).

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
the current zoom. `_legend_values()` (Fix round G, Task 3) reports a
COUNT — events visible in view (deep mode) or the bucket nearest the
view's right edge (density fallback) — the natural "current value" for
a scatter/density series.

### `_DayLengthChart`
Chart 4 (Fix round G, Task 1). A thin `_LineChart` subclass whose x is a
day-of-year int: `_x_ticks()` returns the 12 calendar month starts when
un-zoomed, else defers to the generic ladder; `_fmt_x()` reconstructs
the true calendar date (leap-year correct, `_ref_year`) for "Mon" /
"Mon D" labels instead of the old `day // 30` approximation.

### `_EnlargeDialog`
Fix round G, Task 3 — the "Enlarge" target: see the walkthrough above.
Owns nothing of the chart's OWN state; it only hosts the reparented
panel plus its own extended-legend row and info-strip labels.

### ObservatoryDialog
Normal resizable window; a `QSplitter` column of the five titled chart
panels (chart 1's panel carries its checkbox + Days/Hours filter row;
every panel ends with an Enlarge button — Fix round G, Tasks 2/3) inside
the existing scroll area, under a dual-calendar header line for the
moment. Computes the day-length curve once in `__init__`; wires the
units combo only after every chart it touches (`_envelope`,
`_season_chart`) exists. `_add_panel()` is the one seam that builds a
panel and registers its Enlarge callback; `_open_enlarged()` does the
reparent-out/reparent-back dance around `_EnlargeDialog.exec()`.

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
