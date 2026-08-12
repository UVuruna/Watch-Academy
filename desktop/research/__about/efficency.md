# Efficency (Profiling Helper)

**Script:** [Efficency (script)](../efficency.py)

## Purpose

A small standalone profiling utility, unrelated to the astronomy pipeline —
the `measure` class provides a decorator (`methodEfficency`) that times a
function across FIVE Python clocks at once (`time`, `monotonic`,
`perf_counter`, `thread_time`, `process_time`) and an instance method
(`measuringOverTime`) that loops a callable for N seconds and reports
average/min/max execution time. Its own `__main__` block is a self-test/demo
against a synthetic workload.

## Usage

```bash
python research/efficency.py
```

Runs the built-in demo and prints both the decorator's per-clock timings and
the `measuringOverTime` loop's average/longest/shortest execution time. To
use it elsewhere: `@measure.methodEfficency()` decorates a function, or wrap
a callable with `measure(fn).measuringOverTime(seconds)`.

## Connections

### Uses
- Standard library only (`time`, `functools`)

### Used by
- Nobody else in the project currently — a standalone benchmarking helper,
  not imported by any other script or by the app

## Known issue (flagged, not fixed)

The filename and the class/method names misspell "Efficiency" as
"Efficency" (`efficency.py`, `methodEfficency`) throughout — cosmetic, no
behavior impact; left as-is per this migration's docs-only scope (a rename
would need every caller updated, and today there are none — see
Connections).
