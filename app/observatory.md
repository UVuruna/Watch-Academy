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

### R4 (owner instruction batch 2026-07-20)

**ITEM 1 — NON-MODAL.** The controller `.show()`s `ObservatoryDialog`
instead of `.exec()`ing it — the dial stays interactive while it is
open; a second open request raises the ONE live instance instead of
opening a duplicate ([Watch Controller](controller.md)). The dialog
itself gained `WA_DeleteOnClose` (safe here — unlike `_EnlargeDialog`,
this outer dialog never has a REAL child reparented INTO it from
somewhere else; it only ever LENDS a panel out). The Enlarge flow
(`_open_enlarged`) is non-modal too now — see the updated Task 3/Item-1
entries below; `_EnlargeDialog.__init__` already called `.show()` at
its own end, so dropping the caller's `dialog.exec()` and moving its
post-close cleanup into a `finished` signal handler
(`_close_enlarged`) was the whole change, with the Fix round R1a crash
fix's ownership order (`panel` reparents back BEFORE `deleteLater()`)
preserved exactly.

**ITEM 3 — OPENING SIZE.** The old fixed `self.resize(860, 720)`
becomes A4 portrait (210:297) at 80% of the screen's available height
(`app.theme.size_to_screen`, `defaults.DIALOG_A4_*`) — still a normal
resizable/maximizable window past that first paint. Unrelated to (and
untouched by) `_EnlargeDialog`'s own 16:9-at-50%-height sizing below
(Fix round R1a, Item 1) — two different dialogs, two different owner
specs.

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
button opening `_EnlargeDialog`, a NON-MODAL window (R4 ITEM 1, owner
instruction batch 2026-07-20 — was a blocking `.exec()` before; see the
R4 section above) that TEMPORARILY REPARENTS the SAME panel widget
(`panel.setParent(self)`) in on open and back to its original splitter
slot when it closes (`ObservatoryDialog._open_enlarged` builds and
shows it, connecting its `finished` signal to `_close_enlarged`, which
runs the restore — records the splitter index before detaching).
Reparenting the live widgets — instead of building a
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

### Fix round R1a (owner instruction batch 2026-07-20)

**THE CRASH (13 hits in the owner's crash.log, fixed first).**
`_open_enlarged` threw `RuntimeError: Internal C++ object already
deleted` at `self._splitter.insertWidget(index, panel)`, and the chart
never came back to the main window. Root cause: `_EnlargeDialog` set
`WA_DeleteOnClose`, which queues the DIALOG's own C++ destruction via
`deleteLater()`; since `panel` had been reparented onto it
(`panel.setParent(self)`) as a REAL Qt child, that queued deletion
could — and empirically did — destroy `panel` too before
`_open_enlarged` got a chance to reinsert it. The mocked-`exec()`
pattern every PRE-EXISTING enlarge test used (`class _RecordingEnlarge
… def exec(self): … return 0`) never called Qt's real `QDialog.exec()`
loop, so none of them ever exercised the actual `WA_DeleteOnClose`
timing — the bug was invisible to the suite. Fix: `_EnlargeDialog` no
longer sets `WA_DeleteOnClose`; `_open_enlarged` reparents `panel` back
to the splitter FIRST (guaranteed safe — nothing else can delete the
dialog out from under it) and only THEN calls `dialog.deleteLater()`
explicitly. `tests/test_observatory.py::
test_enlarge_close_cycle_survives_a_real_qt_event_loop_twice` drives
the REAL event loop (`_EnlargeDialog.__init__` schedules its own
`accept()` a tick later; `exec()` is left un-mocked) through all 5
charts, twice — the crash log's repeats, and a deleted-object bug bites
hardest on the second round trip.

**Item 1 — Enlarge sizing.** `_EnlargeDialog._size_to_owner_spec`
replaces the old `showMaximized()`: height = 50% of the screen's
`availableGeometry()`, width = that height × 16/9
(`OBSERVATORY_ENLARGE_HEIGHT_FRACTION`/`_ASPECT_W`/`_ASPECT_H`) — on a
16:9 screen this collapses to exactly 25% of the screen's area (the
owner's own arithmetic; see the defaults.py comment). Still a normal
resizable/maximizable window (the hints are unchanged), just not
maximized on open. Qt's own layout system still won't let the dialog
shrink below its genuine content minimum (the fixed-width info panel
included) — on a very small screen the request is clamped UP, never
crushed; any real monitor is comfortably larger than that minimum.

**Item 2 — the INFO layer.** `_build_info_panel` is the Enlarge
dialog's collapsible right-side column (`OBSERVATORY_INFO_PANEL_WIDTH_PX`,
toggled by the "Hide info"/"Show info" button in the button row): the
chart's own caption text (the SAME string a compact-view caption
already shows — one authoritative description, not two competing
ones) plus, for the eclipse chart only, one row per eclipse KIND
actually present (`ObservatoryDialog._eclipse_kind_rows`) — a color
swatch matching the chart's own dots and a one-line meaning
(`OBSERVATORY_ECLIPSE_KIND_INFO`). Every chart now carries an honest,
DATA-DERIVED caption (span read straight off the bundle, minutes/hi-lo
read straight off the computed curve — never a hand-typed number that
could drift): season, envelope, day-length are new; eclipse and Laskar
already had one and keep it (Laskar's now also states its shown
window). The eclipse legend ALSO recolors by real TYPE, not just
solar/lunar: solar walks yellow→orange→red (`partial` mildest to
`total` most complete), lunar walks navy→blue→cyan (`penumbral`
faintest to `total` most complete) — `OBSERVATORY_ECLIPSE_KIND_COLORS`,
`_kind_color()` (falls back to the plain family color for any type
outside the ground-truthed vocabulary — defensive, since `kind` is read
off the external Deep Time SQLite catalog). The density (no-pack)
fallback has no per-instance kind data to plot, so its ON-CHART legend
stays the two family colors; its info-panel rows list the FULL
ground-truthed vocabulary instead (the bundle's own `counts_by_type`
meta already confirms every kind occurs somewhere across the span).

**Item 3 — the title appears once.** The Enlarge dialog's centered
header is now the chart's ONLY in-page title; the panel's own title
label (needed above its filter row when it lives in the main splitter)
is hidden for the duration of the reparent (`panel.title_label`, set in
`_add_panel`) and restored by `_open_enlarged` on the way back out. The
OS window-title-bar text is unaffected (chrome, not "in-page").

**Item 4 — settings beside their chart.** The Days/Hours units combo
used to sit in the SEASON panel's filter row (`_season_filter`) but
visibly redraws the ENVELOPE chart's own y-axis/title/scale — it now
lives in `_envelope_filter`, built and wired exactly where it was
before, just attached to the other panel. It still ALSO reaches the
season chart's own crosshair delta line (`set_diff_fmt`) — a secondary,
already-documented effect of the same switch, unchanged.

**Item 5 — per-chart MIN TICK / MAX ZOOM.** The single global
`OBSERVATORY_ZOOM_MIN_SPAN_FLOOR` clamp (still `_ChartBase._zoom_floor`'s
DEFAULT, used only as a fallback) is now overridden per chart, DERIVED
FROM THE CHART'S OWN DATA — "pick from the data's sampling", per the
owner:
- `_LineChart._zoom_floor` floors at `_data_stride()` — the MEDIAN gap
  between consecutive x samples in the first visible series (every
  series on one `_LineChart` shares an x grid here). Season/envelope
  share the 20-year bin-mean stride (`SEASON_BIN_YEARS`); the Laskar
  chart floors at its bundle's 1000-year stride — you can no longer
  zoom to the owner's "1-year view of 1000-year-apart samples" (ZOOM do
  1 GOD.png), which showed nothing but a straight interpolation.
- `_EclipseChart._zoom_floor` floors at the median gap between eclipse
  YEARS (deep mode, solar+lunar interleaved) or the density bucket
  width (`bucket_years`, fallback mode).
- The day-length curve now samples every REAL day
  (`OBSERVATORY_DAYLENGTH_STEP_DAYS = 1`, was 2) so its own floor —
  and its own MIN TICK — can honestly reach a 1-day pitch: `_nice_step`/
  `_nice_ticks` gained a `min_step` parameter, and `_DayLengthChart.
  _x_ticks()`'s zoomed branch passes `OBSERVATORY_DAYLENGTH_MIN_TICK_DAYS`
  (1.0) so the ladder never subdivides below a whole calendar day (its
  "Mon D" labels round to the nearest day; anything finer would print
  the same label on two adjacent gridlines).

**Item 6 — thousands separator.** `_year_label` and the eclipse
chart's count formatters (`_fmt_y`, `_legend_values`) now print
`000,000`-style — the Laskar chart's 6-digit BCE years were the
motivating case, but every year/count print in the module goes through
one of these two paths.

**Item 7 — the splitter drag and per-chart collapse.**
*Root cause of "RESIZE ne radi":* `_ChartBase` paints its own surface
and has no Qt layout of its own, so its DEFAULT `sizeHint()` is
invalid — every panel's NATURAL splitter allocation collapsed to
exactly its `OBSERVATORY_CHART_MIN_HEIGHT_PX` floor. The instant the
dialog is shorter than the splitter's full natural content height (any
realistic default open — confirmed with a real `QTest` mouse-press/
move/release drive at the dialog's own 860×720 default), the
surrounding `QScrollArea` gives the splitter ONLY that natural size (no
stretch slack), and `setChildrenCollapsible(False)` forbids shrinking
anything further — every panel is already pinned at its neighbor's
floor simultaneously, so a drag has nothing left to redistribute and
silently does nothing. Fix: `_ChartBase.sizeHint()` now returns a real
preferred size (`OBSERVATORY_CHART_PREFERRED_HEIGHT_PX`, genuinely
above the floor), giving every panel headroom to trade with its
neighbor regardless of window size.
*Collapse/Show:* every panel's filter row gains a "Collapse" button
beside "Enlarge" (`ObservatoryDialog._toggle_collapsed`) — hiding the
chart (and its caption) drops them out of the panel's layout sizing
entirely (Qt's default for hidden widgets), so the panel shrinks to
just its title + filter row and hands the freed room to whatever chart
the owner is comparing; the SAME button, now reading "Show", restores
it. State lives on the chart widget itself (`chart._row_collapsed`),
not on Qt's own `isVisible()` (ambiguous before the dialog's first
show, since it also depends on the whole ancestor chain).

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
- [Watch Controller](controller.md) — opens it from the menu with the
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
Task 3 — empty by default). Fix round R1a adds the overridable
`_zoom_floor(full_span)` seam (Item 5 — the base heuristic; `_LineChart`/
`_EclipseChart` override it with a data-derived one) and a real
`sizeHint()` (Item 7 — the splitter-drag root-cause fix).

### `_LineChart`
A generic multi-series line chart: fixed per-series colors, toggleable
visibility (identity kept when hidden), optional shaded bands and
labelled vertical marks (sorted by x, thinned at full zoom when they
would collide — `OBSERVATORY_VMARK_MIN_SPACING_PX`), a deduped legend,
and a crosshair readout (nearest sample by x, plus an optional
`diff_pair` delta line). `set_y_fmt`/`set_y_title`/`set_diff_fmt` are
the Days/Hours switch's pure display hooks. Used by charts 1, 2, 4 and 5.
Fix round R1a adds `_data_stride()` (the median x-gap of the first
visible series — every series on one `_LineChart` shares an x grid
here) and a `_zoom_floor()` override that floors MAX ZOOM at it.

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
a scatter/density series. Fix round R1a: deep-mode dots and the legend
are colored per real eclipse TYPE (`_kind_color`,
`OBSERVATORY_ECLIPSE_KIND_COLORS` — solar yellow→orange→red, lunar
navy→blue→cyan), and `_zoom_floor()` floors MAX ZOOM at the median gap
between eclipse years (deep mode) or the density bucket width
(fallback mode).

### `_DayLengthChart`
Chart 4 (Fix round G, Task 1). A thin `_LineChart` subclass whose x is a
day-of-year int: `_x_ticks()` returns the 12 calendar month starts when
un-zoomed, else defers to the generic ladder (Fix round R1a: with a
`min_step=OBSERVATORY_DAYLENGTH_MIN_TICK_DAYS` floor, since "Mon D"
labels round to the nearest whole day); `_fmt_x()` reconstructs the
true calendar date (leap-year correct, `_ref_year`) for "Mon" / "Mon D"
labels instead of the old `day // 30` approximation. Its data now
samples every real day (`OBSERVATORY_DAYLENGTH_STEP_DAYS = 1`), so its
inherited `_zoom_floor()` (from `_LineChart`) honestly reaches 1.0.

### `_EnlargeDialog`
Fix round G, Task 3 — the "Enlarge" target: see the walkthrough above.
Owns nothing of the chart's OWN state; it only hosts the reparented
panel plus its own extended-legend row, the collapsible info panel
(`_build_info_panel`, Fix round R1a Item 2) and the sizing/ownership
fixes documented in Fix round R1a above (Items 1 and the crash).

### ObservatoryDialog
Normal resizable window; a `QSplitter` column of the five titled chart
panels (chart 1's panel carries its checkbox filter row, chart 2's the
Days/Hours filter row — Fix round R1a Item 4; every panel ends with a
Collapse and an Enlarge button — Fix round G Tasks 2/3, Fix round R1a
Item 7) inside the existing scroll area, under a dual-calendar header
line for the moment. Computes the day-length curve once in `__init__`;
wires the units combo only after every chart it touches (`_envelope`,
`_season_chart`) exists. `_add_panel()` is the one seam that builds a
panel (storing its title label on `panel.title_label` — Item 3) and
registers its Collapse/Enlarge callbacks; `_toggle_collapsed()` is the
Collapse/Show handler (Item 7); `_open_enlarged()` builds and shows the
NON-MODAL `_EnlargeDialog` (R4 ITEM 1) and wires its `finished` signal
to `_close_enlarged()`, which does the reparent-back-then-
`deleteLater()` dance the crash fix established (Fix round R1a);
`_eclipse_kind_rows()` builds the eclipse panel's info-row list
(Item 2).

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
