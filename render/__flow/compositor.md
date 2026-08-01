# Compositor — Flow

**About:** [description](../__about/compositor.md)

## The paint-step partition (`_plan_steps`, built once at construction)

```mermaid
flowchart TB
    A["FOR EACH layer IN skin.z_order (built stack)"] --> B{cadence != MINUTE\nAND NOT hover_variable?}
    B -- yes --> C{previous layer\nalso cacheable?}
    C -- yes --> D[append to the SAME cache group]
    C -- no --> E[start a NEW cache group]
    B -- no --> F["LIVE step (paint every frame)"]
    D --> G[next layer]
    E --> G
    F --> G
```

Because the default `z_order` seats the weekday set BELOW the ring (a
STATIC layer), pulling the hover-variable weekday layer out SPLITS the
cache into two segments — background/star below, ring above — while
the drawn Z-order stays pixel-identical.

## The per-frame paint (`paint`)

    FUNCTION paint(painter, size, dpr, tick):
        key = (round(size*dpr), day.cache_key)     # NOT hover, NOT reveal
        IF key changed: drop all composites
        ctx = RenderContext(..., hovered=self._hovered, reveal_active=...)
        FOR EACH step IN self._steps:
            IF step is ("cache", group_index):
                IF composites[group_index] is None:
                    composites[group_index] = _render_group(cached_groups[group_index])
                blit composites[group_index] at (-overhang, -overhang)
            ELSE ("live", layer):
                IF reveal_active AND layer is a HandLayer: skip (hands hide)
                painter.save(); translate to center; layer.paint(painter, ctx); painter.restore()

## The tooltip dispatch (`tooltip_at` -> `_tooltip_at`)

```mermaid
flowchart TB
    A[tooltip_at x, y, size] --> B[_element_at: the SAME hit-test\nset_hover uses]
    B --> C{element found?}
    C -- yes --> D["route to its own _*_tooltip\n(body, slot, archetype, thirteenth, sun_servant)"]
    C -- no --> E{point falls on a ring/calendar/\ntwilight/tick zone?}
    E -- yes --> F["route to that zone's _*_tooltip\n(_tick_tooltip, _calendar_tooltip,\n_twilight_tooltip, _ring_letter_legend_tooltip, ...)"]
    E -- no --> G[None]
    D --> H["_centered / _highlight_terms\nwrap the article text into HTML"]
    F --> H
```

Every `_*_tooltip` method reads the SAME skin-geometry/slot-layout/
ninths functions the paint pass uses (never a parallel hand-measured
geometry), then formats article prose from `SymbolismRepository`/
`EncyclopediaRepository` through the shared `_centered`/
`_highlight_terms` HTML helpers — the "term bank" that gives this file
its third responsibility.
