# Design Window — Flow

**About:** [description](../__about/design_window.md)

## Layout

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart TB
    subgraph WIN["DesignDialog — square, 50% of screen height"]
        subgraph TABS["QTabWidget — open tab index preserved across rebuilds"]
            direction LR
            P["Pointer
            variant pills, wheel-pair pills,
            Shape/Curvature/Edge, Hide night borders"]
            R["Ring
            preset tiles, finish pills,
            Two metals?, Shine?"]
            U["Umbra
            form pills, contrast pills"]
            C["Complications
            plate-style pills"]
            H["Hands
            pack tiles (real preview art)"]
            E["Earth
            style tiles (real preview art),
            label-mode pills"]
            S["Size
            preset pills + live diameter slider"]
        end
    end
```

## Algorithm — Pointer tab row gating

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart TB
    A[_pointer_tab] --> B[variant pills + wheel-pair pills — always]
    B --> C{pointer == 'aurora'?}
    C -- yes --> Z[stop — no Shape/Curvature/Edge/Night-border rows]
    C -- no --> D[Shape row: Star / Polygon pills]
    D --> E{"pointer in POLYGON_POINTERS
    AND pointer_shape == 'polygon'?"}
    E -- yes --> F[Curvature slider + Edge pills]
    E -- no --> G[skip]
    F --> H["Hide night borders checkbox
    enabled = daylight_active(settings)"]
    G --> H
```

Every row reads the CURRENT `settings.pointer`/`pointer_shape` fresh on
each build, so a pointer switch alone re-gates the whole tab on the next
live-apply rebuild — no extra wiring needed.
