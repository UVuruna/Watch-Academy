# __main__ — CLI Selftest

**Script:** [__main__ (script)](../__main__.py)

## Purpose
Prints the full computed clock state for any city and any moment,
without launching the Qt widget — a fast way to eyeball DST, polar and
solstice states:

```
python -m core --city Belgrade
python -m core --city Tromso --at 2026-01-15T12:00
python -m core --lat 78.2232 --lng 15.6267 --tz Europe/Oslo --at 2026-12-21T12:00
```

Not an algorithm of its own — it validates CLI arguments (city vs.
manual lat/lng/tz, coordinate range checks), resolves a location, then
delegates entirely to [Clock State](clock_state.md)'s
`build_day_context`/`build_tick_state` and formats the result as plain
text. Purity-exempt for the wall clock only (`--at` defaults to
`datetime.now(tz)`), which [Purity Test (script)](../../tests/test_purity.py)
documents as this file's one allowed exception.

## Connections

### Uses
- [Clock State](clock_state.md) — `build_day_context`, `build_tick_state`
- [Config (folder)](../../config/___config.md) — `LATITUDE_RANGE`,
  `LONGITUDE_RANGE`, `WEEKDAY_BODIES`
- [Locations Repository](../../data/__about/locations.md) — `find_city`
- [Moon Phases Repository](../../data/__about/moon_phases.md) — `moon_window`
- [Seasons Repository](../../data/__about/seasons.md) — `year_anchors`

### Used by
- Run directly as `python -m core` — no in-project caller

## Functions
- `main()`: argument parsing (`--city` XOR `--lat`/`--lng`/`--tz`, plus
  optional `--at`), coordinate range validation, then the
  build-and-print flow.
- `_fmt(event)`: `"HH:MM:SS"` or `"—"` for a `None` sun event.
