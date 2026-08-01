# Deep Time Repository

**Script:** [Deep Time Repository (script)](../deep_time.py) ·
**Flow:** [diagram](../__flow/deep_time.md)

## Purpose

Read-only repository over the OPTIONAL full-span data pack
`Database/deep_time.sqlite` (built by `setup/make_deep_time.py`;
gitignored — ships only with the FULL installation). Exposes the same
`YearAnchors` / `MoonWindow` shapes the bundled repositories expose, so
`build_day_context` works unchanged for pack years, plus the eclipse
catalog the Quick Jump navigation reads. Instants of years outside
`datetime`'s 1–9999 range are proxy-shifted by whole 400-year Gregorian
cycles (`core.deep_time.proxy_cycles`) into the canonical window.

## Connections

### Uses
- [Config (folder)](../../config/___config.md) — `paths.deep_time_path()`,
  `constants.GREGORIAN_CYCLE_YEARS`
- [Core (folder)](../../core/___core.md) — `core.deep_time.julian_day_of`
  / `proxy_cycles`, the `YearAnchors` / `MoonWindow` dataclasses,
  `core.clock_state.EclipseEvent`

### Used by
- [Seasons Repository](seasons.md), [Moon Phases Repository]
  (moon_phases.md) — the chain target beyond bundled coverage
- [Watch Controller](../../app/__about/controller.md) — `detect()` at startup,
  the eclipse Quick Jumps, the widened Time Travel coverage
- [Tests (folder)](../../tests/___tests.md) — against a small fixture
  pack, never the full build

## Classes

### DeepEclipse
Frozen record of one catalog eclipse: `kind` ("solar"/"lunar"), the
calendar instant (`year, month, day, second_of_day`, UT), `type`
(total/annular/hybrid/partial/penumbral), `magnitude`, greatest-eclipse
`lat`/`lon` (solar only, `None` where absent), `jd_ut` (the ordering
key).

### DeepTimeRepository
- `detect(path=None)` (classmethod): the pack file exists → repository
  instance; absent → `None` (a supported state, never raised). THE one
  resolution point — called once at startup.
- `coverage()`: the inclusive `(first, last)` astronomical years the
  pack covers, read from its `meta` table.
- `year_anchors(astro_year)`: six proxy-shifted anchor instants
  bracketing `astro_year`, from the `sun_events` table.
- `moon_window(astro_year)`: the year ± neighbors' principal phases as
  `(proxy instant, cycle fraction)`.
- `eclipse_after(jd_ut, kind)` / `eclipse_before(jd_ut, kind)`: the
  nearest catalog eclipse strictly after/before a Julian Day, or `None`
  at the catalog edge.
- `eclipses_near(now, cycles)`: up to 4 `EclipseEvent`s — the nearest
  solar/lunar eclipse before AND after `now`, via two indexed
  `eclipse_before`/`eclipse_after` lookups per kind, never a table
  scan.

## Design Decisions

SQLite is opened read-only (`mode=ro` URI) — the pack is immutable app
data; a missing table or meta key raises loudly. Calendar fields are
stored per-event (not as ISO strings) because `datetime.fromisoformat`
cannot parse negative years; eclipses additionally carry `jd_ut` as the
one monotonic ordering key across the whole span.
