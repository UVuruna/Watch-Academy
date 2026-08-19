# Ring Tooltips

**Script:** [Ring Tooltips (script)](../tooltip_ring.py)

## Purpose

Every hover the RING and the ARMS answer. The ring's jewel and word
legends, the live crown, and `_arm_tooltip` — the longest single method
in the whole tooltip bank — with the entire seat vocabulary behind it.

Layer: render.

## Why this file exists

`render/tooltip_composer.py` was 2,239 logic lines and the LAST entry on
the project's structure ratchet. Its entry had been RATIFIED by the owner
on 2026-08-18 with a real argument — there is no second subject hiding in
it, its size is the dial's own vocabulary — and the same entry recorded
the natural next cut: **BY TOOLTIP FAMILY**. On **2026-08-19** the owner
gave the word, and this module is one of the four families.

**Nothing was rewritten.** All 69 methods travelled verbatim, with their
comments and decorators — verified by comparing `ast.dump` of every one
before and after — **with a single named exception**:
`_weekday_tooltip` (in `render/tooltip_calendar.py`) has two occurrences
of `ring.METAL_THEMES` reading `registry.METAL_THEMES` instead, because
the round's last commit deleted that alias. Same object, same behaviour,
and it is the only body that differs.

`tests/test_tooltip_families.py` — recorded from the UN-SPLIT composer at
commit `6aa49db` — proves the dial says byte-for-byte what it said
before: 959 hover points across seven dial configurations, SHA-256 per
point plus 42 representative tooltips kept as full HTML.

## How the dial is held: it is NOT

This module is a **MIXIN** on `TooltipComposer`, not a collaborator.
`self._dial` is the composer's ONE reference, set once in its
`__init__`, and every method here reads the live skin, day and tick
through it.

The collaborator shape was considered and rejected, for the reason the
ratchet entry itself had already written down: *the composer HOLDS THE
DIAL, so three holders is three back-channels*. Four objects each keeping
their own reference to the same dial is four places a stale reference can
hide, and the call graph crosses the families constantly — the ring's
`_arm_tooltip` calls the sky's `_wet_dry_block` and `_span_line`, the
calendar's `_tick_tooltip` calls the ring's `_live_crown_tooltip` and the
sky's `_greetings_tooltip`, the targets' `_element_encyclopedia_target`
calls the ring's `_active_thirteenth`. A collaborator per family would
have needed a hand-built path for every one of those crossings. `self`
already is that path, and it changed not one call site.

This is the same reasoning WA-R14 applied to `app/controller.py`'s five
mixins: **a collaborator when the object is HELD, a mixin when the
methods share `self`.**

## The door is `render/tooltip_composer.py`

Nothing outside the composer imports this module. `tooltip_at`,
`encyclopedia_target` and `warm_hover_articles` are addressed on the
composer by [Clock Widget](../../app/__about/widget.md) and by twenty
test files, and not one of them changed.

## What lives here

- **The ring band** — `_ring_jewel_legend_tooltip`,
  `_ring_word_legend_tooltip`, `_live_crown_tooltip`, and the
  module-level `_crown_arc_centre`.
- **The arm** — `_arm_tooltip`, and `_SOUTH_ANCHOR_FLIP`, the four-entry
  table that maps a southern-hemisphere anchor onto its opposite seat.
- **The archetype arms** — `_archetype_arm_tooltip`,
  `_archetype_three_side`, `_tetramorph_three_side`,
  `_archetype_center_tooltip`, `_archetype_two_rows`.
- **The centre seat** — `_dual_face_columns`, `_center_dual_tooltip`,
  `_center_ninth_alt`, `_dual_seat_taken`.
- **The thirteenth** — `_active_thirteenth`, `_thirteenth_tooltip`.
- **`_combo_key`** — the shared (theme, roster) key three seat readers
  build their lookup from.

## Why `_SOUTH_ANCHOR_FLIP` lives here and not in the composer

Two methods read it: `_arm_tooltip` (this module) and
`_arm_encyclopedia_target` ([Encyclopedia Targets](encyclopedia_targets.md)).
Both are about THE ARM, so the table sits with the arm's own family and
the targets module imports it from here — one table, two readers, no
copy, and no new home invented for a four-entry dict.

## Neighbours

- [Tooltip Composer](tooltip_composer.md) — the door, the dispatch and
  the six shared helpers (`_tr`, `_ord`, `_month`, `_month_short`,
  `_year`, `_label`)
- [Sky Tooltips](tooltip_sky.md) — sun, moon, eclipses, Earth, twilight
- [Ring Tooltips](tooltip_ring.md) — jewels, words, crown, the arms
- [Calendar Tooltips](tooltip_calendar.md) — wedges, mounts, weekdays,
  the tick readout, the sign readings
- [Encyclopedia Targets](encyclopedia_targets.md) — what article an
  element opens

## Connections

### Uses
- [Compositor](compositor.md) — through `self._dial`, held by the
  composer: state (`skin`, `day`, `tick`, `overlay`, `encyclopedia`,
  `symbolism`, `hidden_unlocked`) and geometry (`element_at`,
  `world_theta`, `rotation`, `arm_angle_at`, `band_hit`, …)
- [Article HTML](article_html.md) — the rich-text vocabulary
- [Config (folder)](../../config/___config.md) · [Core
  (folder)](../../core/___core.md) — the tables and the astronomy

### Used by
- [Tooltip Composer](tooltip_composer.md) — as a base class, and by
  nothing else
