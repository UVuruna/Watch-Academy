# Topic Tree

**Script:** [Topic Tree (script)](../tree.py) · **Flow:** [diagram](../__flow/tree.md)

## Purpose
Every card the reader can open, built in two layers:

1. `_build_topics` — the flat topic table exactly as the browser always
   built it (moved verbatim from the old `app/encyclopedia.py`): one
   entry per page, article refs resolved lazily so the overlay always
   applies.
2. **The Session 27 laws** on top (owner-sealed 2026-07-28) — the Cube's
   42-page run split into its four cards, the register merges (Bible x3,
   Creeds x2, Eclipses x2) folded into one card each, and every topic
   sealed with a `variants` tuple the reader's switcher walks.

Plus the pure, widget-free reading helpers the reader and the tests share.

## Connections

### Uses
- [Topic Builders](builders.md), [Static Pages](pages.md) — the pieces `_build_topics` assembles
- [Encyclopedia Tree (config)](../../../config/__about/encyclopedia_tree.md) — `CUBE_TOPICS`, `VARIANT_SOURCES`, `GOD_VARIANT_LABELS`, `TOPIC_ALIASES`, `cube_target`, `whole_of` — the merge declarations, the Cube slices and the jump aliases
- [Instrument Diagrams](../../../render/__about/instrument_diagrams.md) — `INSTRUMENT_FIGURES`, which instrument pages draw themselves instead of loading a file
- [Asset Recolor](../../../render/__about/asset_recolor.md), [Asset Variants](../../../render/__about/asset_variants.md) — `metal_variant_path`, `moon_phase_file`

### Used by
- [Encyclopedia Dialog](dialog.md), [Reader Screen](reader.md) — `topics()`, `variant_at`, `switch_variant`, `resolve_target`
- [Encyclopedia Warm](../../__about/encyclopedia_warm.md) — walks `topics()` as its single inventory of derived art to pre-build

## The shape a screen receives

```
{"title", "tile_title"?, "icon", "entries": [...],
 "variants": ((label, start, stop), ...)}
```

`variants` is ALWAYS present — a topic with one variant carries
`(("", 0, len(entries)),)` and its switcher stays hidden, so no screen
needs a special case (Rule #7).

## Functions

- `_build_topics(travel_date=None, is_daylight=True) -> dict`: the flat
  table — every weekday theme, Astrology, Chinese zodiac, The Week, The
  Instrument, Virtues/Sins/Moods, The Nine Intelligences, The Slavic
  Months, the shared Ninths loop, the Pantheon/Wider-Court blocks, The
  Two Triangles, Trinity, Moon, Seasons, Sun, Eras, both Eclipse
  families and the Archetypes hall (Cube/Double Trinity/Crosses/One Soul)
- `topics(travel_date=None, overlay=None, is_daylight=True) -> dict`:
  the public entry point — `_build_topics` plus the Guide topic, then the
  Session 27 laws in order: `_split_cube`, `_merge_variants`,
  `_label_god_variants`, `_drop_look_topics`, `_seal_variants`
- `variant_at(topic, index) -> int`: which variant a page index sits in
- `switch_variant(topic, index, delta) -> int`: THE OFFSET LAW — steps
  to the next/previous register, keeping the reader's position inside
  the block (clamped when the target register is shorter)
- `resolve_target(all_topics, key, entry) -> tuple | None`: `(topic_key,
  index)` for a jump addressed the dial's OLD way — the Cube's flat
  index, the weekday dual remap, or a merged register's alias; `None`
  for an unknown key (the caller is the dial, and a stale target must
  never raise)

## THE DOUBLE NINTH LAW (owner decree 2026-07-29)
`topics()` threads `is_daylight` into the shared ninths loop
(`builders._live_ninth_face`, per-theme dispatch by
`constants.NINTH_MECHANISMS`) and `travel_date` into `_weekday_topic`
(THE WEEKLY MANDATE, cp_corpo only). `EncyclopediaDialog` supplies
`is_daylight` from the controller's OWN live tick — never a second
sunrise/sunset computation here.

## Design Decisions
- **The tree is declared once, in config.** `config/encyclopedia_tree.py`
  is the ONE table of wholes, memberships, variants, aliases and
  accents; this module reads it and never re-declares a whole.
- **A merged register is a contiguous run of pages, never a
  re-ordering.** `_merge_variants` concatenates each source topic's
  entries in declaration order and records the boundaries — nothing
  about an existing page's position changes when it joins a loop.
- **An unknown jump target is silently ignored**, never raised — the
  caller is the dial reading a possibly-stale hover target.
