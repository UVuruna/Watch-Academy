# Motto

**Script:** [Motto (script)](motto.py)

## Purpose
Pure per-glyph angle math for the outer Great Seal MOTTO ARC (TASK 1,
owner "može radi" 2026-07-19, [The DOMY Canon](../CANON.md)'s §The
Banknote): given a motto string and a small set of PINNED
letter→ring-position constraints, `motto_glyph_angles` solves every
character's dial angle — pinned characters land exactly on their seat,
unpinned characters between two consecutive pins are spaced EVENLY
across the angular gap. Zero Qt, zero wall clock (core purity,
[Tests (folder)](../tests/___tests.md)'s `test_purity.py`).

MOTO-FIX round (owner correction 2026-07-19, the dollar's Great Seal
reference image): the two mottos now draw on DISJOINT arcs — ANNUIT
COEPTIS over the TOP, NOVUS ORDO SECLORUM under the BOTTOM, exactly
like the real seal — instead of the first round's mistaken single
top-heavy sweep at two overlapping radii. The new `clockwise` flag
picks the arc's reading direction.

## Connections

### Uses
- [Angles](angles.md) — `ring_position_angle` (the shared hour → dial
  angle formula every ring seat, letter and now motto glyph shares) and
  `readable_rotation_deg` (the per-glyph tangential rotation, unchanged
  by this round — see Design Decisions)

### Used by
- [Ring Presets](../data/rings.md) — `validate_preset` calls this at
  LOAD time so a broken pin config (a typo'd occurrence, an
  out-of-order pin) fails loudly there, never mid-paint
- [Layers](../render/layers.md) — `RingLayer` draws the resolved
  angles (never recomputes them)

## Functions

- `motto_glyph_angles(text, pins, clockwise=True)`: one angle per
  character of `text` (spaces included, so word gaps get their own
  even slot); `pins` is `(letter, occurrence, ring_position)` triples —
  e.g. `("N", 1, 4)` pins the first "N" to the 4h seat. The first pin
  must resolve to index 0 and the last to the final character (every
  glyph belongs to an interior segment). `clockwise=True` (ANNUIT
  COEPTIS's own top arc) unwraps each next pin's angle (+360 as needed)
  to EXCEED the previous one; `clockwise=False` (NOVUS ORDO SECLORUM's
  own bottom arc) unwraps it (-360 as needed) to stay BELOW the
  previous one instead — both read left-to-right to a viewer (see
  Design Decisions for why the direction must flip between the two
  halves).
- `_occurrence_index(text, letter, occurrence)`: the 0-based index of
  the Nth appearance of `letter` — e.g. the 3rd "O" in "NOVUS ORDO
  SECLORUM" is the one ENDING "ORDO", not NOVUS's own O. Raises if
  `text` does not contain that many (Rule #1).

## Design Decisions

**Why the bottom arc reads COUNTERCLOCKWISE (MOTO-FIX round):** dial-x
(`render.layers.dial_point`'s own `distance * sin(theta)`) is monotonic
in OPPOSITE senses across the two halves of the circle — increasing
theta moves screen-x left-to-right over the TOP (theta from -90 to 90,
i.e. 270..360..90) but RIGHT-to-left under the BOTTOM (theta from 90 to
270). So a bottom arc's characters must be placed at DEcreasing theta
to still read left-to-right to a viewer; placing them at increasing
theta (the top arc's own direction) mirrors the text — the first
round's actual bug for the fraction of its arc that did fall under the
bottom. `motto_glyph_angles`'s new `clockwise` flag is exactly this
choice, resolved once per motto entry (`Database/ring_presets.json`'s
own `clockwise` field, `data.rings._validate_motto`).

**Why the per-glyph ROTATION needs no matching flag:**
`core.angles.readable_rotation_deg` already derives "tops outward" vs
"tops inward" from the angle alone (theta in 90..270 flips 180°,
elsewhere it does not) — this was already correct for both halves
before this round (it is the SAME formula the ring's own six letters
use, and Ω at the bottom already stood upright pre-MOTO-FIX). The
MOTO-FIX bug was entirely in the ANGLE math (the bottom motto swept
the wrong way, mostly through the TOP), never in the rotation formula
— feeding `readable_rotation_deg` the corrected (decreasing) bottom-arc
angles makes every glyph upright automatically, no new orientation
parameter required.

**One shared radius, not two (MOTO-FIX round):** the first round gave
each motto its own radius because pinned letters intentionally
OVERLAPPED in angle (both mottos' own O at noon, own S at 16h). The
corrected layout drops that shared-angle design — the two arcs are now
angularly DISJOINT (top 300°-360°-60°, bottom 120°-180°-240°) — so both
draw at the SAME `RING_MOTTO_RADIUS_FRACTION`; `RING_MOTTO_RADIUS_STEP`
is deleted (Rule #6, no leftover unused constant).
