# Sky Tooltips

**Script:** [Sky Tooltips (script)](../tooltip_sky.py)

## Purpose

Every hover the SKY answers. The sun face over the centre seat, the moon
marker with its lunation ordinal, the eclipse text with its visibility
line, type icon and article, the Earth marker with its season row and
wet/dry span, the twilight bands, and the deep-time period window with
its greetings.

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

- **The sun** — `_sun_face_tooltip`.
- **The moon** — `_moon_text`, `_lunation_ordinal`.
- **Eclipses** — `_eclipse_text` with `_eclipse_type_icon_tag`,
  `_eclipse_visibility_text`, `_eclipse_article` and `_eclipse_emblem`.
- **The Earth** — `_earth_text`, `_period_earth_html`, `_season_row`,
  `_wet_dry_span_at`, `_current_season_key`.
- **The seasons' spans** — `_wet_dry_block`, `_span_line`,
  `_season_name_for`, `_anchor_instant`. These four are read by the
  RING family's `_arm_tooltip` as well: a season arm says the same thing
  the Earth marker says, and it says it through these.
- **The bands and the window** — `_twilight_tooltip`, `_period_tooltip`,
  `_period_word`, `_greetings_tooltip`.
- **`_greetings`** — the module-level lazy loader for the Four
  Greetings verses.

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
