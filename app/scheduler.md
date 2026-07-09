# Minute Scheduler

**Script:** [Minute Scheduler (script)](scheduler.py)

## Purpose
Fires the controller's tick just past every minute boundary. The wall
clock is read fresh on every fire (never accumulated intervals), so a
late fire after sleep/resume self-corrects on the next tick.

## Connections

### Uses
- [Config (folder)](../config/___config.md) — `TICK_EPSILON_MS`,
  `CLOCK_JUMP_THRESHOLD_S`

### Used by
- [App Controller](controller.md)

## Classes

### MinuteScheduler
Self-rescheduling single-shot `QTimer` (PreciseTimer type).

#### Methods
- `start()` / `stop()`
- `set_per_second(per_second)`: cadence change at runtime (the Seconds
  element switch) — re-aims the pending shot immediately so a freshly
  enabled seconds hand never sits frozen for up to a minute
- `_fire()`: compares actual vs expected fire time; a gap beyond the
  threshold is reported as `on_tick(clock_jumped=True)` so the controller
  forces a full day-context refresh (sleep/resume, manual clock change)
