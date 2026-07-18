# Report

**Script:** [Report (script)](report.py)

## Purpose
The HIDDEN efficiency report (owner 2026-07-15): once the secret code
unlocks the session, a 📊 Report entry appears above Exit and opens
this dialog — every measured functionality since the installation,
with call counts and execution-time statistics.

## Connections

### Uses
- [Profiling](../config/profiling.md) — `snapshot()` / `reset()`
- [UI Style](ui_style.md) — the vivid button pills
- [Theme](theme.md) — the dark dialog surface + the results table
- [Config (folder)](../config/___config.md) — colors, sizes, ui text

### Used by
- [App Controller](../app/controller.md) — the hidden menu entry

## Classes

### ReportDialog
Stay-on-top dialog, refreshed once per second from
`profiling.snapshot()`:

- **Table** — one row per measured name: Calls, Average, Min, Max,
  Total, Last. Click a header to sort (numeric, via the underlying
  nanosecond values); units pick themselves per value (ns → µs → ms →
  s, two decimals — the owner's spec: readable numbers whatever the
  function's speed).
- **Top bar chart** — total time by function, top 10, one quiet gold
  hue (single series — the row labels carry identity, values labeled
  directly, no legend).
- **Sparkline** — the SELECTED row's recent durations, session-only,
  with min/max/last read-outs; shows drift while the app runs.
- **Buttons** — Reset (clears the lifetime store) and Download (CSV
  of the aggregates) in the shared vivid style.

## Design Decisions
QPainter draws both charts — no plotting dependency for two small
marks. The dialog reads snapshots; it never touches the lock-guarded
store directly. The exact numbers always live in the table, so the
charts stay label-light.
