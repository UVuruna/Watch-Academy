# Observatory

**Script:** [Observatory (script)](observatory.py)

## Purpose
The STATISTICS sibling of the Encyclopedia (owner 2026-07-16: "kao
enciklopedija, samo sa statistikom") — a right-click window (🔭
Observatory…, beside 🏛️ Encyclopedia…) of dark, QPainter-drawn,
interactive charts over the long ephemeris data. Four charts:

1. **Season-duration oscillations** — the four northern astronomical
   seasons' lengths over the millennia, with PER-SERIES CHECKBOXES
   above (the four seasons + the light/dark half-year pair — the
   owner's own Anno Lucis graph, now live in-app).
2. **The light − dark envelope** — the signed light−dark half-year over
   the whole measured span, with the ANNO LUCIS dawn (4079 BCE) and the
   era spans marked (the Age of Light band 4079 BCE → 6423 CE, the Age
   of Darkness beyond, the starry-season transition verticals).
3. **The eclipse timeline** — the nearest past/next solar and lunar
   eclipses from the current (or TRAVELED) moment when the Deep Time
   pack is installed (magnitude scatter, the moment marked); without the
   pack, the bundled density (counts per bucket) + the per-type summary.
4. **The location's day-length curve** — daylight minutes over the year
   at the current (or traveled) observer, computed live via
   `core.sun.day_length_curve`.

## Chart quality rules (the project's dataviz doctrine)
Dark-first on the theme surface; ONE y-axis per chart (never dual);
series colors FIXED per series (the four seasons wear their canonical
cross-wheel element hues, light/dark gold vs slate — never re-colored
when a checkbox hides a series); thin marks, a recessive grid, a legend
always drawn, direct labels on the era marks; a crosshair hover readout
on every chart; the filter row sits ABOVE the charts, not scattered.

## Time Travel interplay
The controller passes the EFFECTIVE `(moment, observer, tz, cycles)` —
the frozen simulation tuple when Time Travel is active, else the live
present. So chart 3's "nearest" is measured from the traveled moment and
chart 4's curve is the traveled observer's year (the proxy Gregorian
year — day length is identical across the 400-year proxy cycle).

## Connections

### Uses
- [Observatory Data](../data/observatory.md) — the committed series
  bundles (always present; never needs deep_time.sqlite)
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

### `_LineChart`
A generic multi-series line chart: fixed per-series colors, toggleable
visibility (identity kept when hidden), optional shaded bands and
labelled vertical marks, an always-drawn legend, and a crosshair readout
(nearest sample by x). Used by charts 1, 2 and 4.

### `_EclipseChart`
Chart 3. With the Deep Time pack: a magnitude scatter of the nearest
`OBSERVATORY_ECLIPSE_WINDOW_N` past/next solar and lunar eclipses around
the moment, the moment drawn as a vertical line, crosshair readout of
the eclipse under the cursor. Without it: the bundled density (solar /
lunar counts per bucket) over the whole span + a "full installation"
note.

### ObservatoryDialog
Normal resizable window; a scroll column of the four titled chart
sections (chart 1 preceded by its checkbox filter row) under a dual-
calendar header line for the moment. Computes the day-length curve once
in `__init__`.

## Design Decisions
QPainter draws every chart — no plotting dependency (the same choice as
the Report). The series bundles are decimated and committed, so the
window opens instantly and works on the partial installation; only
chart 3's EXACT nearest-eclipse mode needs the optional Deep Time pack,
degrading to the bundled density otherwise (the documented split).
