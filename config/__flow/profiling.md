# Profiling — Flow

**About:** [description](../__about/profiling.md)

## Algorithm

```mermaid
flowchart TB
    A["@timed(name) call\nOR measure(name) block"] --> B[start = perf_counter_ns]
    B --> C[run wrapped code]
    C --> D[elapsed = perf_counter_ns - start]
    D --> E["_record(name, elapsed) — under _lock"]
    E --> F{first call for name?}
    F -- yes --> G[_ensure_loaded — lazy read profiling.json once]
    F -- no --> H[entry already in _stats]
    G --> I[create entry: count/total/min/max/last = elapsed]
    H --> J[count+=1, total+=elapsed, min/max updated, last=elapsed]
    I --> K[append to _recent deque, maxlen=RECENT_KEEP]
    J --> K
    K --> L[_dirty = True]

    M[controller: once per minute, and at quit] --> N["flush()"]
    N --> O{_dirty?}
    O -- no --> P[no-op]
    O -- yes --> Q[serialize _stats to JSON]
    Q --> R[write .tmp, os.replace onto profiling.json]
```

Pseudocode:

    record(name, elapsed_ns):
        WITH lock:
            ensure_loaded()   # lazy first read of profiling.json
            entry <- stats.get(name) OR fresh {count:0, total:0, min:elapsed, max:elapsed}
            entry.count += 1; entry.total += elapsed_ns
            entry.min = MIN(entry.min, elapsed_ns); entry.max = MAX(entry.max, elapsed_ns)
            entry.last = elapsed_ns
            recent[name].append(elapsed_ns)   # session-only, capped deque
            dirty <- True

    flush():                          # called by the controller, never by record()
        WITH lock:
            IF NOT dirty: RETURN
            payload <- serialize(stats)
            dirty <- False
        atomically write payload to profiling.json (tmp + os.replace)

Recording never touches disk — it only sets `_dirty`. The controller
is the sole caller of `flush()`, so measuring a hot render path never
risks a stall from file I/O on that path itself.
