# Minute Scheduler

**Script:** [Minute Scheduler (script)](../scheduler.py) · **Flow:** [diagram](../__flow/scheduler.md)

## Purpose
Fires the controller's tick just past every minute (or second) boundary.
The wall clock is read FRESH on every fire — never accumulated intervals
— so a late fire after sleep/resume self-corrects on the next
scheduling pass instead of drifting forever.

## Connections

### Uses
- [Config (folder)](../../config/___config.md) — `defaults.TICK_EPSILON_MS`,
  `defaults.CLOCK_JUMP_THRESHOLD_S`

### Used by
- [Watch Controller](controller.md) — one `MinuteScheduler` per watch,
  kept per-watch rather than shared (see [Watch Manager](watch_manager.md)'s
  Design Decisions for why a shared scheduler was declined)

## Classes

### MinuteScheduler(QObject)
Wraps a single-shot, `PreciseTimer`-typed `QTimer` that reschedules
itself after every fire.

#### Methods
- `__init__(on_tick, parent=None, per_second=False)`: `on_tick(clock_jumped: bool)`
  fires just after every minute boundary, or every second boundary when
  `per_second` is True (the seconds hand / a seconds-showing slot)
- `start()` / `stop()`
- `set_per_second(per_second)`: cadence change at runtime — re-aims the
  pending shot immediately instead of waiting up to a minute for a
  freshly enabled seconds hand to un-freeze
- `_schedule()`: computes milliseconds to the next boundary from
  `datetime.now()` and arms the timer; records the expected fire time
- `_fire()`: compares actual vs. expected fire time — a gap beyond
  `CLOCK_JUMP_THRESHOLD_S` calls `on_tick(clock_jumped=True)` so the
  controller forces a full day-context refresh (sleep/resume, a manual
  clock change). Reschedules in a `finally` block: Qt swallows any
  non-`SystemExit` exception raised inside a timer slot, so without the
  `finally` one escaped exception would leave the single-shot timer
  unarmed and freeze the dial forever.
