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

## Connections

### Uses
- [Angles](angles.md) — `ring_position_angle` (the shared hour → dial
  angle formula every ring seat, letter and now motto glyph shares)

### Used by
- [Ring Presets](../data/rings.md) — `validate_preset` calls this at
  LOAD time so a broken pin config (a typo'd occurrence, an
  out-of-order pin) fails loudly there, never mid-paint
- [Layers](../render/layers.md) — `RingLayer` draws the resolved
  angles (never recomputes them)

## Functions

- `motto_glyph_angles(text, pins)`: one angle per character of `text`
  (spaces included, so word gaps get their own even slot); `pins` is
  `(letter, occurrence, ring_position)` triples — e.g. `("N", 1, 4)`
  pins the first "N" to the 4h seat. The first pin must resolve to
  index 0 and the last to the final character (every glyph belongs to
  an interior segment); consecutive pins must read CLOCKWISE (angles
  are unwrapped, +360 as needed, to keep increasing) — the owner's
  "both mottos read continuously clockwise, evenly spaced between
  pins" spec, solved once and reused verbatim by the renderer.
- `_occurrence_index(text, letter, occurrence)`: the 0-based index of
  the Nth appearance of `letter` — e.g. the 3rd "O" in "NOVUS ORDO
  SECLORUM" is the one ENDING "ORDO", not NOVUS's own O. Raises if
  `text` does not contain that many (Rule #1).

## Design Decisions
Two mottos, drawn at two different radii (`render.layers.RingLayer`,
[Layers](../render/layers.md)) — NOT because this module cares about
radius (it only ever returns angles), but because the two mottos'
pinned letters intentionally OVERLAP in angle (both motto's own O
lands at noon, both texts' own S at 16h — the owner's design: MASON
outside doubles the reading). Two glyphs at the identical angle can
only coexist at two different radii, which is why `RingSpec.motto`
carries two independent entries rather than one merged ring of text.
