# Encyclopedia Targets

**Script:** [Encyclopedia Targets (script)](../encyclopedia_targets.py)

## Purpose

WHAT ARTICLE an element opens — never what it says.
`encyclopedia_target(x, y, size)` is the Spacebar jump and the LEARN MORE
link in every hover footer: it maps the element under the cursor to a
`(topic, index)` pair in the Encyclopedia's own entry order.

Layer: render.

## Why this file exists

`render/tooltip_composer.py` was 2,239 logic lines and the LAST entry on
the project's structure ratchet. Its entry had been RATIFIED by the owner
on 2026-08-18 with a real argument — there is no second subject hiding in
it, its size is the dial's own vocabulary — and the same entry recorded
the natural next cut: **BY TOOLTIP FAMILY**. On **2026-08-19** the owner
gave the word, and this module is one of the four families.

**Nothing was rewritten.** Every method travelled verbatim, with its
comments and decorators, and `tests/test_tooltip_families.py` — recorded
from the UN-SPLIT composer at commit `6aa49db` — proves the dial says
byte-for-byte what it said before: 959 hover points across seven dial
configurations, SHA-256 per point plus 42 representative tooltips kept as
full HTML.

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

- **The door's body** — `encyclopedia_target`, and the three it
  dispatches to: `_element_encyclopedia_target`,
  `_arm_encyclopedia_target`, `_calendar_wedge_target`.
- **The per-topic resolvers** — `_weekday_encyclopedia_target`,
  `_eclipse_encyclopedia_target`, `_season_topic_index`,
  `_sun_topic_index`.
- **The order tables** — `_ENC_ZODIAC_ORDER`, `_ENC_WEEK_ORDER`,
  `_ENC_SEASON_ORDER`, `_ENC_SUN_ORDER`, `_ENC_TRIO_ORDER`,
  `_ENC_ECLIPSE_SOLAR_ORDER`, `_ENC_ECLIPSE_LUNAR_ORDER`. Each mirrors
  the Encyclopedia's own listing for one topic, because the jump indexes
  into that listing.
- **The thirteenths' places** — `_ENC_OPHIUCHUS_INDEX`,
  `_ENC_CAT_INDEX`, `_ENC_SOL_INDEX`, `_ENC_MODRENIK_INDEX` and the
  `_ENC_THIRTEENTH_TARGET` map they build: Ophiuchus and The Cat close
  their gallery topics, Sol and Modrenik close "months".

## Why this is a family at all

The other three answer "what does this element SAY". This one answers a
different QUESTION about the same elements, and the difference is
visible in behaviour: **it works with the LEGEND OFF.** When the owner
turns hovers off, every tooltip in the other three families goes silent
and the Spacebar jump still opens the right page — because this is
geometry and indexing, never text. That is also why it borrows
`_SOUTH_ANCHOR_FLIP` from [Ring Tooltips](tooltip_ring.md) rather than
owning it: it needs the arm's seat arithmetic, not the arm's words.

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
