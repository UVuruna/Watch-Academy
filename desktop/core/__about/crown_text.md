# Crown Text

**Script:** [Crown Text (script)](../crown_text.py) · **Flow:** [diagram](../__flow/crown_text.md)

## Purpose
Pure per-glyph angle math for the outer Great Seal CROWN TEXT ARC ([The DOMY
Canon](../../../CANON.md)'s §The Banknote): given a crown text string and a
small set of PINNED letter -> ring-position constraints,
`crown_glyph_angles` solves every character's dial angle — pinned
characters land exactly on their seat, unpinned characters between two
consecutive pins are spaced EVENLY across the angular gap. A second
entry shape, `centered_word_angles`, solves a single station word
centered on one ring seat (the DOMY dark-cross and LOOP light-cross
words). Zero Qt, zero wall clock (core purity,
[Purity Test (script)](../../tests/test_purity.py)).

The two Great Seal crown texts draw on DISJOINT arcs, like the real seal:
ANNUIT COEPTIS over the TOP (8h -> 16h through noon), NOVUS ORDO
SECLORUM under the BOTTOM (4h -> 20h through the bottom/24h) — the
`clockwise` parameter picks which arc a call draws, since dial-x
(`distance * sin(theta)`) is monotonic in OPPOSITE senses across the two
halves of the circle (see Design Decisions).

## Connections

### Uses
- [Angles](angles.md) — `ring_position_angle` (the shared hour -> dial
  angle formula every ring seat, letter and crown-text glyph shares)
- [Config (folder)](../../config/___config.md) — `dial.
  RING_CROWN_TEXT_LETTER_STEP_DEG` (`config/dial.py`, `60.0 / 9` degrees —
  core reaching into config for a numeric constant is the same
  established pattern `core.angles` uses for `constants.DIAL_OFFSET_DEG`;
  purity forbids Qt and the wall clock, not config)

### Used by
- [Ring Presets](../../data/__about/rings.md) — `validate_preset` calls this at
  LOAD time so a broken pin config (a typo'd occurrence, an
  out-of-order pin) fails loudly there, never mid-paint
- [Layers](../../render/layers/___layers.md) — `RingLayer` draws the resolved
  angles, never recomputes them

## Functions

- `centered_word_angles(text, position, clockwise=True)`: one angle per
  character of a single word, the word's midpoint landing exactly on
  `position`'s seat angle, letters at the fixed
  `RING_CROWN_TEXT_LETTER_STEP_DEG` step. Raises if `text` is empty or
  contains a space — one word only.
- `free_arc_angles(text, orientation)` (owner decree 2026-08-05, THE
  COMPOSITIONAL RING MODEL's CROWN TEXT for custom rings): one angle
  per character of an arbitrary text (spaces allowed), centered on the
  dial's own top (`orientation="top"`, clockwise) or bottom
  (`"bottom"`, counter-clockwise) anchor — not tied to any ring seat,
  unlike `centered_word_angles`.
- `crown_glyph_angles(text, pins, clockwise=True)`: one angle per
  character of `text` (spaces included, so word gaps get their own
  slot, un-drawn by the caller). `pins` is `(letter, occurrence,
  ring_position)` triples — e.g. `("N", 1, 4)` pins the first "N" to the
  4h seat. The first pin must resolve to index 0 and the last to the
  final character. With exactly 2 pins, delegates to
  `_tight_two_pin_angles`; with 3+ pins, every character strictly
  between two consecutive pins is the EVEN linear interpolation of that
  segment's own two pinned angles. Raises if fewer than 2 pins, if two
  pins collide on the same index, or if the pins don't cover both text
  ends.
- `_tight_two_pin_angles(text, resolved, clockwise)`: the 2-pin-only
  layout — every letter advances at the fixed `RING_CROWN_TEXT_LETTER_STEP_DEG`
  step from BOTH pins inward; the crown text's own single interior space
  absorbs whatever angular slack remains, centered between its two
  flanking letters. Requires exactly one interior space — raises
  otherwise.
- `_occurrence_index(text, letter, occurrence)`: the 0-based index of
  the Nth appearance of `letter` in `text` — raises if `text` does not
  contain that many.

## Design Decisions

**Why the word gap is centered, not evenly spaced:** the crown text's own
interior space never draws (`RingLayer`'s draw loop skips it), so any
angle assigned to it is inconsequential for rendering — centering it
between its two flanking letters keeps `crown_glyph_angles`'s contract
("one angle per character, spaces included") intact.

**Why the bottom arc reads counterclockwise:** dial-x is monotonic in
OPPOSITE senses across the two halves of the circle — increasing theta
moves screen-x left-to-right over the TOP but right-to-left under the
BOTTOM. A bottom arc's characters must therefore be placed at DEcreasing
theta to still read left-to-right to a viewer; `clockwise=False` is
exactly this choice.

**Why the per-glyph rotation needs no matching flag:**
`core.angles.readable_rotation_deg` already derives "tops outward" vs
"tops inward" from the angle alone (theta in 90..270 flips 180 deg) —
the same formula the ring's own six letters use — so feeding it either
arc's angles draws every glyph upright automatically.

**One shared radius, not two:** the two crown texts' arcs are angularly
DISJOINT (top 300 deg-360 deg-60 deg, bottom 120 deg-180 deg-240 deg),
so both draw at the same `RING_CROWN_TEXT_RADIUS_FRACTION`.

## Known Documentation vs Code Note
The module's own docstrings (`core/crown_text.py`, inherited unchanged
through the TASK 1 module rename) still say
`` `defaults.RING_CROWN_TEXT_LETTER_STEP_DEG` `` in two prose spots — the
constant lives in `config/dial.py` (confirmed:
`RING_CROWN_TEXT_LETTER_STEP_DEG = 60.0 / 9`) and the actual import
(`from config import dial`) and every real reference in the code
(`dial.RING_CROWN_TEXT_LETTER_STEP_DEG`) already use the correct module.
This is a stale in-code comment, not a behavior bug — flagged here per
the Living Docs Rule; not fixed (`.py` files are out of scope for a docs
migration).
