# Warm — Flow

**About:** [description](../__about/warm.md)

## Algorithm — the four ordered phases

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart LR
    P[Every dial's first frame painted] --> A[1. Dial art]
    A --> W[2. Working set]
    W --> E[3. Encyclopedia]
    E --> H[4. Hover articles]
    A -. repaint per recolor .-> P
```

Pseudocode:

    FUNCTION run_warm(hover_sweeps, progress, on_art_ready, should_stop):
        warm_pending_art(progress, on_art_ready, should_stop)      # phase 1
        IF should_stop() -> RETURN
        warm_working_set(progress)                                # phase 2
        IF should_stop() -> RETURN
        warm_encyclopedia(progress, should_stop)                  # phase 3
        FOR EACH sweep IN hover_sweeps:                            # phase 4
            IF should_stop() -> RETURN
            sweep()

1. **Dial art** — the letter recolors the dials are currently standing
   in for with their gold masters; each lands with an immediate repaint
   via `on_art_ready` (a queued Qt signal, since this runs off the GUI
   thread).
2. **Working set** — the downscaled dial copies of oversized sources.
3. **Encyclopedia** — every metal variant and decode-ceiling downscale a
   page can ask for.
4. **Hover articles** — every spoken hover probe, last and only after
   the dials are dressed.

`should_stop` is polled between phases, never mid-phase — a daemon
thread dies with the process regardless, so the check only avoids
leaving a half-written cache file on the way out.
