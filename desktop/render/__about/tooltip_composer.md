# Tooltip Composer

**Script:** [Tooltip Composer (script)](../tooltip_composer.py) ·
**Flow:** [diagram](../__flow/tooltip_composer.md)

## Purpose
THE TOOLTIP COMPOSER — **the ONE DOOR** to everything the dial SAYS.

Every hover the dial answers is built behind this class: the arm
legends, the weekday bodies, the tick readout, the ring's jewels and
words, the live crown, the moon, the eclipses, the Earth, the calendar
wedges, the twilight bands, the greetings — and the Encyclopedia TARGET
each of them jumps to when the reader presses SPACE.

**Since 2026-08-19 the bodies live in four family modules beside it**
([Sky](tooltip_sky.md) · [Ring](tooltip_ring.md) ·
[Calendar](tooltip_calendar.md) · [Encyclopedia
Targets](encyclopedia_targets.md)), which this class INHERITS. What is
left here is what belongs to no family:

- **the doors' NAMES** — `tooltip_at`, `encyclopedia_target` and
  `warm_hover_articles`, addressed by [Clock
  Widget](../../app/__about/widget.md) and seventeen test files. Two of
  the three bodies are in this file; `encyclopedia_target`'s body rides
  in [Encyclopedia Targets](encyclopedia_targets.md) and reaches the
  public surface by inheritance, because everything it calls is in that
  family and pulling only the entry point back here would have split one
  chain across two files;
- **the dispatch** — `_tooltip_at`, which names the element under the
  cursor and decides WHICH family answers;
- **the six formatting helpers every family uses** — `_tr` (the active
  language), `_ord` (the ordinal, raised in English only), `_month` /
  `_month_short`, `_year` (the ONE pairing formatter, official year plus
  Anno Lucis plus the optional third calendar) and `_label`;
- **`_skin`**, the property `config.paths.in_display` reads.

278 logic lines, down from 2,239.

It was ~2,400 lines inside [Compositor](compositor.md), a module whose
job is to stack paint layers and answer hit tests. The [OOP
audit](../../../docs/AUDIT-OOP-2026-08-18.md) measured that file method
by method — *"2,126 lines of tooltip / article HTML, 775 of paint and
geometry"* — and graded the cut **high risk**, for a real reason: these
are METHODS over shared state, not free functions like the ones R11
lifted into [Article HTML](article_html.md).

## Connections

### Uses
- [Compositor](compositor.md) — **held, not copied from** (see below)
- [Article HTML](article_html.md) — the whole rich-text vocabulary
- [Config (folder)](../../config/___config.md) · [Core
  (folder)](../../core/___core.md) — the tables and the astronomy the
  texts read
- [Encyclopedia](../../data/__about/encyclopedia.md) ·
  [Symbolism](../../data/__about/symbolism.md) — the two shared books

### Used by
- [Compositor](compositor.md) — builds ONE in `__init__` and keeps
  `tooltip_at`, `encyclopedia_target` and `warm_hover_articles` as
  one-line doors, because that is what [Clock
  Widget](../../app/__about/widget.md) and seventeen test files call

## The interface — what the composer asks the dial for
Two things, and nothing else. Both are PUBLIC on the compositor now,
because a private name reached across an object boundary is the defect
finding L1 recorded elsewhere in the same audit.

- **STATE**, through read-only properties: `skin`, `day`, `tick`,
  `overlay`, `encyclopedia`, `symbolism`, `hidden_unlocked`. Read live on
  every call — which is exactly why the composer holds the DIAL and not
  the values. A re-installed skin or a new day context can never leave a
  stale copy here, and that is the failure mode a "pass the state in"
  design would have introduced.
- **GEOMETRY**, through nine questions: `element_at`, `interior_hit`,
  `world_theta`, `world_offset`, `rotation`, `jewel_offset`,
  `jewel_theta`, `arm_angle_at`, `band_hit`. A tooltip must name the same
  thing the paint drew, so it ASKS the painter rather than re-deriving
  the angles beside it.

## Design Decisions
- **A collaborator, not a module of free functions.** The audit's R11
  lifted the free helpers; what was left genuinely reads `self._skin`,
  `self._day`, `self._last_tick` and the repositories on nearly every
  line. Turning those into arguments would have meant threading four
  values through sixty-seven methods; holding the dial states the
  relationship instead — the dial is the model, the composer speaks for
  it.
- **`_skin` is a PROPERTY here, and named that way on purpose.**
  `config.paths.in_display` — the decorator three entry points wear —
  reads `self._skin.display` off whatever object it decorates. The
  property resolves through the dial, so the decorator works unchanged
  and still cannot see a stale skin.
- **The module tables came along.** `_ENC_*` (the Encyclopedia entry
  orders), `_MONTHS`, `_SOUTH_ANCHOR_FLIP`, `_crown_arc_centre` and
  `_greetings` are read only by the text side. `_ENC_ZODIAC_ORDER` was
  the one shared name, and the method that shared it —
  `_calendar_wedge_target` — is an encyclopedia TARGET, so it came along
  too and the table stopped being shared.
- **MIXINS, not collaborators, for the four families.** This is the
  question the ratchet entry left open — *"the composer HOLDS THE DIAL,
  so three holders is three back-channels"* — and the answer is that the
  families must NOT hold it. The dial is held ONCE, here, and the four
  bases read it through `self._dial`. The call graph makes the case
  concrete: the ring's `_arm_tooltip` calls the sky's `_wet_dry_block`
  and `_span_line`; the calendar's `_tick_tooltip` calls the ring's
  `_live_crown_tooltip`, `_ring_jewel_legend_tooltip`,
  `_ring_word_legend_tooltip` and the sky's `_greetings_tooltip`; the
  targets' `_element_encyclopedia_target` calls the ring's
  `_active_thirteenth`. Collaborators would have needed a hand-built path
  for every crossing; `self` already is one, and no call site changed.
  It is the same rule WA-R14 wrote for `app/controller.py`: **a
  collaborator when the object is HELD, a mixin when the methods share
  `self`.**
- **The module tables went with their family, not with the door.**
  `_ENC_*` to [Encyclopedia Targets](encyclopedia_targets.md),
  `_crown_arc_centre` and `_SOUTH_ANCHOR_FLIP` to [Ring
  Tooltips](tooltip_ring.md), `_greetings` to [Sky
  Tooltips](tooltip_sky.md), `_MONTHS` / `_MONTHS_SHORT` to [Calendar
  Tooltips](tooltip_calendar.md) — the composer imports the last two back
  for `_month()` / `_month_short()`, and the targets module imports
  `_SOUTH_ANCHOR_FLIP` from the ring, because both flip the same arm
  anchors and one table with two readers beats two copies.
- **It LEFT the structure ratchet, and took the ratchet with it.**
  `tests/structure_ratchet.json` is now EMPTY and
  `tests/test_structure_law.py`'s list holds only the five test files a
  test-hygiene round owes. The proof that the cut was a MOVE is
  `tests/test_tooltip_families.py`: 959 hover points over seven dial
  configurations, recorded from the un-split composer at `6aa49db`.
