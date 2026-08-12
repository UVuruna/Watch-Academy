# Minute Scheduler — Flow

**About:** [description](../__about/scheduler.md)

## Algorithm — self-correcting reschedule

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart TB
    A[start / set_per_second] --> B[_schedule]
    B --> C["now = datetime.now()
    ms = time to next minute/second boundary + TICK_EPSILON_MS
    expected = now + ms"]
    C --> D[arm single-shot QTimer for ms]
    D --> E((timer fires))
    E --> F[_fire]
    F --> G{"abs(now - expected)
    > CLOCK_JUMP_THRESHOLD_S ?"}
    G -- yes --> H["on_tick(clock_jumped=True)"]
    G -- no --> I["on_tick(clock_jumped=False)"]
    H --> B
    I --> B
```

Pseudocode:

    FUNCTION _schedule():
        now <- wall clock, timezone-aware
        ms  <- milliseconds until the next minute (or second) boundary
              + TICK_EPSILON_MS
        expected <- now + ms
        arm single-shot timer for ms

    FUNCTION _fire():
        now <- wall clock
        jumped <- expected is set AND |now - expected| > CLOCK_JUMP_THRESHOLD_S
        TRY:
            on_tick(jumped)
        FINALLY:
            _schedule()   # always reschedule, even if on_tick raised

The interval is never accumulated — every `_schedule()` call reads the
wall clock fresh, so a late fire (machine slept, GUI thread was busy)
self-corrects on its own next pass rather than drifting cumulatively.
