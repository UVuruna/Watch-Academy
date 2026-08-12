# Report

**Script:** [Report (script)](../report.py) · **Flow:** [diagram](../__flow/report.md)

## Purpose
The hidden efficiency report: once the secret code unlocks the session,
a Report entry appears above Exit and opens this dialog -- every
measured functionality since the installation, with call counts,
execution-time statistics, a top-total bar chart and the selected
function's recent-durations sparkline. QPainter draws both charts; the
dialog reads a profiling snapshot once per second.

## Connections

### Uses
- [Profiling (config)](../../config/__about/profiling.md) -- `snapshot()` / `reset()`
- [UI Style](ui_style.md) -- the vivid button pills
- [Theme](theme.md) -- the dark dialog surface + the results table

### Used by
- [Watch Controller](controller.md) -- the hidden `_open_report()` menu entry

## Classes

### `_NumericItem(QTableWidgetItem)`
Sorts by the raw nanosecond value carried in `Qt.ItemDataRole.UserRole`
while DISPLAYING the readable unit (`__lt__` compares the stored role
value, not the text).

### `_BarChart(QWidget)`
Top functions by TOTAL time -- horizontal bars, one quiet gold hue (a
single series: the row labels carry identity, the table holds the exact
numbers). `set_data(rows, selected)` supplies `[(name, total_ns), ...]`;
the selected row's bar stays full-color while the rest dim.

### `_Sparkline(QWidget)`
The selected function's recent durations this session -- a 2px line,
min/max/last read-outs in muted ink. `set_data(name, values)`.

### `ReportDialog(QDialog)`
Stay-on-top, refreshed once per second from `profiling.snapshot()`.

#### Methods
- `_refresh()`: rebuilds the table (sort state preserved), keeps the
  previously selected row selected by name (not by row index, which
  shifts as entries come and go)
- `_refresh_charts()`: feeds the bar chart the top
  `defaults.REPORT_BAR_TOP_N` functions by total time, and the
  sparkline the selected function's `recent` durations
- `_reset()`: `profiling.reset()` then refresh
- `_download()`: writes every measured function's aggregates to a
  user-picked CSV

## Functions
### `format_ns(ns) -> str`
Readable duration: ns as-is, else microseconds/ms/s with two decimals --
the unit picks itself per value so a function's speed is always
readable at a glance.

## Design Decisions
QPainter draws both charts -- no plotting dependency for two small marks.
The dialog reads snapshots only; it never touches the lock-guarded
profiling store directly. Exact numbers always live in the table, so the
charts stay label-light.
