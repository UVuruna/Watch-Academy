# Topic Tree

**Script:** [Topic Tree (script)](tree.py)

## Purpose
Every card the reader can open, in two layers:

1. `_build_topics` — the flat topic table exactly as the browser always
   built it (moved verbatim).
2. **The Session 27 laws** on top — the Cube split, the register merges,
   the god-block labels, and the `variants` seal that gives EVERY topic a
   range tuple.

Plus the pure, widget-free reading helpers the reader and the tests share.

## Connections

### Uses
- [Topic Builders](builders.md), [Static Pages](pages.md)
- [Encyclopedia Tree](../../config/encyclopedia_tree.md) — the merge declarations, the Cube slices and the jump aliases

### Used by
- [Encyclopedia Dialog](dialog.md), [Reader Screen](reader.md), [Encyclopedia Warm](../encyclopedia_warm.md)

## The shape a screen receives

```
{"title", "tile_title"?, "icon", "entries": [...],
 "variants": ((label, start, stop), ...)}
```

`variants` is TOTAL: a single-register theme carries `(("", 0, n),)`, so
no screen needs a special case (Rule #7).

## The offset law

```
ON switch(direction d):
    offset <- page - start of current register
    next   <- (current + d) MOD register count
    page   <- start of next + MIN(offset, length of next - 1)
```

## The jump contract
`resolve_target(topics, key, entry)` answers three kinds of address with
one path: the Cube's old flat index, the weekday dual remap, and a merged
register's own dial name. An unknown key returns None — the caller is the
dial, and a stale target must never raise.

## THE DOUBLE NINTH LAW (owner decree 2026-07-29)
`topics(travel_date=None, overlay=None, is_daylight=True)` — `_build_
topics` threads `is_daylight` into the shared ninths loop
(`builders._live_ninth_face`, per-theme dispatch by `constants.
NINTH_MECHANISMS`) and `travel_date` into `_weekday_topic` (THE WEEKLY
MANDATE, cp_corpo only). `EncyclopediaDialog` supplies `is_daylight`
from the controller's OWN live tick — never a second sunrise/sunset
computation here.
