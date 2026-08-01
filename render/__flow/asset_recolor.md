# Asset Recolor — Flow

**About:** [description](../__about/asset_recolor.md)

## The lazy two-phase variant

```mermaid
flowchart TB
    A[metal_variant_path source, metal] --> B{metal is a swap target\nAND source exists?}
    B -- no --> C[return source path unchanged]
    B -- yes --> D[compute cache path:\nhash(source)+mtime+metal+shade+version]
    D --> E[record ledger entry:\ncache path -> source, metal]
    E --> F[return cache path\nNO PIXELS BUILT YET]
    F -.first real use.-> G[ensure_variant cache_path]
    G --> H{path in ledger AND\nnot already on disk?}
    H -- no --> I[return path unchanged\nalready built, or nothing recorded]
    H -- yes --> J[LOCK path]
    J --> K[recolor source with the metal kernel]
    K --> L[save to path]
    L --> M[return path\nsource path on a failed write]
```

Pseudocode:

    FUNCTION metal_variant_path(source, metal):
        IF metal not a swap target OR source missing: RETURN source
        cache = raster_cache / hash(source, mtime, metal, shade, VERSION)
        ledger[cache] = (source, metal)        # recipe only, no pixels
        RETURN cache

    FUNCTION ensure_variant(path):
        IF path not in ledger OR path already exists on disk: RETURN path
        WITH per-path lock:
            recolor ledger[path].source with ledger[path].metal -> write to path
        RETURN path                             # source path if the write failed

The eager door, `metal_variant_file`, is just
`ensure_variant(metal_variant_path(path, metal))` — naming and building
in one call, for callers (tooltips) that need a real file NOW.
