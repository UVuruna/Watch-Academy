# Topic Tree — Flow

**About:** [description](../__about/tree.md)

## Algorithm — `topics()` build pipeline

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart TB
    A[_build_topics] --> B["+ _guide_topic(overlay)"]
    B --> C[_split_cube<br/>42-page Cube run → 4 cards]
    C --> D[_merge_variants<br/>registers of one subject → one card]
    D --> E[_label_god_variants<br/>Planetary / Pantheon / Wider Court labels]
    E --> F[_drop_look_topics<br/>remove planet_signs ghost card]
    F --> G[_seal_variants<br/>every topic gets a variants tuple]
    G --> H[(topics dict)]
```

Order matters: the Cube split must run before the merges/seal see the
four Cube cards; the seal must run last so every topic — merged or not
— ends up with a `variants` tuple.

## Algorithm — THE OFFSET LAW (`switch_variant`)

    FUNCTION switch_variant(topic, index, delta):
        variants <- topic.variants
        current  <- variant_at(topic, index)          # which register index sits in
        offset   <- index - variants[current].start
        next     <- (current + delta) MOD len(variants)
        RETURN variants[next].start + MIN(offset, variants[next].length - 1)

Monday stays Monday when the register changes; a shorter register (the
Wider Court runs 4 pages against Planetary's 11) clamps to its own last
page instead of overrunning into the next block.

## Algorithm — `resolve_target(topics, key, entry)`

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart TB
    A[key, entry] --> B{key == 'cube'?}
    B -- yes --> C[tree.cube_target entry]
    B -- no --> D{key in restructured topics AND entry == 0?}
    D -- yes --> E[entry <- WEEKDAY_DUAL_PAGE_INDEX]
    D -- no --> F{key in TOPIC_ALIASES?}
    E --> F
    F -- yes --> G["topic_key, variants[alias].start + entry"]
    F -- no --> H{key in all_topics?}
    H -- yes --> I["key, entry"]
    H -- no --> J[None — stale target, caller must not raise]
```
