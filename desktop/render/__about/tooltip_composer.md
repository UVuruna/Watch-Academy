# Tooltip Composer

**Script:** [Tooltip Composer (script)](../tooltip_composer.py) ·
**Flow:** [diagram](../__flow/tooltip_composer.md)

## Purpose
THE TOOLTIP COMPOSER — everything the dial SAYS.

Every hover the dial answers is built here: the arm legends, the weekday
bodies, the tick readout, the ring's jewels and words, the live crown,
the moon, the eclipses, the Earth, the calendar wedges, the twilight
bands, the greetings — and the Encyclopedia TARGET each of them jumps to
when the reader presses SPACE.

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
  Widget](../../app/__about/widget.md) and twenty test files call

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
- **It is over the wall, and that is a ratchet entry with a written
  reason** (`tests/structure_ratchet.json`, PENDING OWNER RATIFICATION).
  There is no second subject hiding in 2,238 lines of per-element text;
  its size is the dial's own vocabulary. The audit's third piece —
  `render/encyclopedia_targets.py`, the ~200 lines that answer "what
  article does this open" rather than "what does this say" — would not
  bring the rest under the wall, so it was not done blind.
