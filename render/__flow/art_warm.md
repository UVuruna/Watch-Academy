# Art Warm — Flow

**About:** [description](../__about/art_warm.md)

## The drain loop

```mermaid
flowchart TB
    A[warm_pending_art] --> B[jobs = pending_art minus attempted]
    B --> C{any jobs?}
    C -- no --> D[DONE — return count built]
    C -- yes --> E[FOR EACH job]
    E --> F{caller says stop?}
    F -- yes --> G[return what was built so far]
    F -- no --> H[mark attempted]
    H --> I[ensure_variant: build pixels, write to raster cache]
    I --> J[on_ready callback — dial can repaint now]
    J --> E
    E -- loop exhausted --> B
```

Pseudocode:

    FUNCTION warm_pending_art(progress, on_ready, should_stop):
        attempted = {}
        built = 0
        REPEAT:
            jobs = [p FOR p IN pending_art() IF p NOT IN attempted]
            IF jobs is empty: BREAK
            FOR EACH path IN jobs:
                IF should_stop(): RETURN built
                attempted.add(path)
                ensure_variant(path)          # recolor + disk-cache write
                built += 1
                on_ready()                    # this thread; Qt marshals to GUI
        RETURN built

The REPEAT (not a single FOR) is load-bearing: the GUI thread keeps
recording new recipes while this drains, so a single pass would miss
art discovered mid-run. The `attempted` set is what turns "keep
draining until the ledger is quiet" into a loop that provably
terminates even when a write keeps failing.
