# Encyclopedia Warm — Flow

**About:** [description](../__about/encyclopedia_warm.md)

## Algorithm — `warm_encyclopedia`

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart TB
    A[_jobs] --> B["topics = app.encyclopedia.topics()"]
    B --> C["jobs = every topic's card icon
    (gallery-first, deduplicated)"]
    C --> D["+ every entry's look/image paths
    in topic order (deduplicated)"]
    D --> E((jobs list))
    E --> F[FOR EACH job, in order]
    F --> G{should_stop?}
    G -- yes --> H[(return built count)]
    G -- no --> I[resolve path through the art-source fallback]
    I --> J{recorded AND still missing?}
    J -- yes --> K[ensure_variant path — build it now]
    J -- no --> L
    K --> L{file exists AND wider than its decode ceiling?}
    L -- yes --> M[scaled_variant_file path, ceiling]
    L -- no --> N
    M --> N{index % 25 == 0?}
    N -- yes --> O["progress: elapsed, done/total, %, rate"]
    N -- no --> F
    O --> F
```

Pseudocode:

    FUNCTION warm_encyclopedia(progress, should_stop):
        jobs <- _jobs()                       # deduplicated (path, ceiling) pairs
        FOR EACH (raw, ceiling), index IN jobs:
            IF should_stop() -> RETURN built_count
            path <- resolve raw through the art-source fallback
            IF path is a recorded, still-missing metal variant:
                ensure_variant(path); built_count += 1
            IF path exists AND is wider than ceiling:
                scaled_variant_file(path, ceiling)
            EVERY 25 jobs -> progress(elapsed, done/total, %, rate)
        RETURN built_count
