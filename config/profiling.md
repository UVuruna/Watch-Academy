# Profiling

**Script:** [Profiling (script)](profiling.py)

## Purpose
Execution-time statistics for the KEY functionalities (owner
2026-07-15): a `@timed("name")` decorator and a `measure("name")`
context manager record wall durations (`perf_counter_ns`) into a
cumulative, install-lifetime store — count, total, min, max and last
per name, plus a session-only deque of recent durations for the
Report's sparkline. Thread-safe (one lock), lazy-loaded, and batched:
recording only marks the store dirty; the controller flushes once per
minute and at quit, so measuring never costs an I/O.

Lives in `config/` — the bottom layer — so every layer above (data,
render, app) can instrument itself without bending the one-way flow;
`core` stays pure and is never decorated (its callers are measured
instead).

## Connections

### Uses
- [Config (folder)](___config.md) — the store path beside settings.json

### Used by
- [App Controller](../app/controller.md) — tick/skin instrumentation,
  the minute flush, quit flush
- [Compositor](../render/compositor.md) — paint, composite rebuild,
  hit test and hover instrumentation
- [Assets](../render/assets.md) — subdial recolor, working-set warmup
- [Report](../app/report.md) — `snapshot()`, `reset()`

## Functions

- `timed(name)`: decorator — measures every call of the wrapped
  function under `name`
- `measure(name)`: context manager — measures an inline block (used
  where a decorator cannot sit, e.g. the day-context rebuild branch)
- `snapshot()`: `{name: {count, total_ns, min_ns, max_ns, last_ns,
  recent}}` copy for display
- `flush()`: atomic save when dirty (tmp + `os.replace`)
- `reset()`: clear everything and persist the empty store

## Design Decisions
Persistence is one JSON file beside settings
(`%APPDATA%/DOMY Watch/profiling.json`) holding only the aggregates —
the recent-durations deques are session memory, so the file stays tiny
no matter how long the app lives. Times are stored in integer
nanoseconds; the Report picks readable units at display time.
