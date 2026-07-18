# Deep Time Repository

**Script:** [Deep Time Repository (script)](deep_time.py)

## Purpose
Read-only repository over the OPTIONAL full-span data pack
`Database/deep_time.sqlite` (built by `setup/make_deep_time.py` from the
research events database; gitignored — ships only with the FULL
installation). Exposes the same `YearAnchors` / `MoonWindow` shapes the
bundled repositories expose, so `build_day_context` works unchanged,
plus the eclipse catalog the Quick Jump eclipse navigation reads.

## Detection and chaining (one resolution point)

`DeepTimeRepository.detect()` — the ONE place that decides whether the
pack exists (`config.paths.deep_time_path()`, frozen-safe). The
controller calls it once at startup and injects the instance into
[Seasons](seasons.md) and [Moon Phases](moon_phases.md); each falls
through to it ONLY when the bundled JSON has no entry for the requested
year (bundled-first keeps the 1560–2640 tier minute-exact and
bit-identical to before). Absent pack → the repositories raise their
existing loud ValueError and Time Travel keeps the friendly clamp.

## The proxy frame

Instants of years outside datetime's 1–9999 return shifted by whole
400-year Gregorian cycles into the canonical window (see
[Deep Time](../core/deep_time.md) — the shift is exact for every dial
computation). `year_anchors(astro_year)` / `moon_window(astro_year)`
take the REAL astronomical year and apply
`core.deep_time.proxy_cycles(astro_year)` — the same function the
controller canonicalizes the traveled moment with, so anchors always
bracket the simulated proxy moment.

## Classes

### DeepEclipse
Frozen record of one catalog eclipse: `kind` ("solar"/"lunar"), the
astronomical calendar instant (`year, month, day, second_of_day`, UT),
`type` (total/annular/hybrid/partial/penumbral), `magnitude`,
greatest-eclipse `lat`/`lon` (solar only, None where the finder
reported no surface point) and `jd_ut` (the catalog ordering key).

### DeepTimeRepository
- `detect(path=None)`: classmethod — the pack file exists → repository,
  else None. Never raises on absence (absence is a supported state).
- `coverage()`: inclusive (first, last) astronomical years, read from
  the pack's `meta` table (written by the generator from the actual
  event extents — Rule #4, never hardcoded).
- `year_anchors(astro_year)`: six proxy-shifted anchor instants
  (December solstice of year−1 … spring equinox of year+1) from
  `sun_events`; outside coverage raises ValueError naming the span.
- `moon_window(astro_year)`: the year ± neighbors' principal phases as
  (proxy instant, cycle fraction), fraction = crossing degree / 360.
- `eclipse_after(jd_ut, kind)` / `eclipse_before(jd_ut, kind)`: the
  nearest catalog eclipse strictly after/before a Julian Day — the
  Quick Jump prev/next feed; None at the catalog edge (the jump then
  stays put, the standard clamp).
- `eclipses_near(now, cycles)` (ROADMAP 15h item 11): up to 4
  `core.clock_state.EclipseEvent` — the nearest solar/lunar eclipse
  before AND after `now` (a day-context build instant, possibly
  proxy-shifted), via `eclipse_before`/`eclipse_after` — two INDEXED
  jd_ut lookups per kind, never a table scan, called ONCE per
  day-context rebuild. `cycles` un-shifts `now` to the real
  astronomical Julian Day the catalog orders by
  (`core.deep_time.julian_day_of`) and re-shifts the found instants
  back into `now`'s own proxy frame, so they compare directly against
  every other `DayContext` datetime. The controller feeds the result
  straight into `build_day_context`; `core.clock_state.build_tick_state`
  then only compares already-fetched instants — the display's ONLY
  database read per day.

## Connections

### Uses
- [Config (folder)](../config/___config.md) — `paths.deep_time_path()`,
  the pack filename constant
- [Deep Time](../core/deep_time.md) — proxy cycles
- [Year Wheel](../core/year_wheel.md) / [Moon](../core/moon.md) — the
  `YearAnchors` / `MoonWindow` dataclasses

### Used by
- [Seasons](seasons.md), [Moon Phases](moon_phases.md) — the chain
  target beyond the bundled coverage
- [App Controller](../app/controller.md) — detection at startup, the
  eclipse Quick Jumps, the widened Time Travel coverage
- [Tests (folder)](../tests/___tests.md) — against a small fixture pack
  (`tests/deep_fixture.py`), never the full build

## Design Decisions
- SQLite opened read-only (URI `mode=ro`) — the pack is immutable app
  data; a missing table or meta key raises loudly (Rule #1).
- Calendar fields are stored per event (not ISO strings) because
  `datetime.fromisoformat` cannot parse negative years; eclipses also
  carry `jd_ut` as the one monotonic ordering key across the whole span.
- **The eclipse display's ABSENCE RULE (ROADMAP 15h item 11):** the
  on-dial eclipse display (`render.layers.YearMarkerLayer`) has NO
  bundled fallback — unlike seasons/moon phases, eclipses live ONLY in
  this optional pack. `App Controller` feeds `eclipses_near()` into
  `build_day_context` only when `DeepTimeRepository.detect()` found the
  file; absent, `DayContext.eclipses` stays `()` and
  `TickState.eclipse_event` is always `None` — the render never sees a
  half-populated state, matching the app exactly as it behaved before
  this round.
