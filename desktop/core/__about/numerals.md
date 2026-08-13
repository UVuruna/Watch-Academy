# core/numerals.py

The pure mathematics of the dial's two NUMERAL BANDS — every angle, every
seat rotation, every light vector and every relief step of
[The Dial Numerals](../../research/hour_numerals.md), with no Qt and no
wall clock anywhere near them.

## Purpose

The outer band carries the hour numerals, the inner band the five-minute
numbers. The outer band is drawn by hand at run time (never shipped as
art) because it ROTATES: in the Heliocentric mode the whole hour band
turns so true solar noon stands at the top, so a numeral's seat belongs to
the ANGLE it lands on, never to the hour it carries. This module answers,
for any moment:

- where each numeral sits (`hour_angle`, `minute_angle`),
- WHICH seats carry a numeral at all (`numeral_hours`,
  `inner_number_seats`, `inner_composition`),
- how far it turns so it still reads (`seat_rotation`) — **THE ONE
  SEATING LAW** for the whole ring since 2026-08-07:
  [Angles](angles.md)' `readable_rotation_deg`, which the JEWELS and the
  crown arcs go through, is now an alias of this function rather than a
  second fork of it (the fork disagreed on the four square angles, and
  that is why The One's 18 and 6 lay sideways),
- which way its relief is thrown (`light_offset`),
- how many copies that relief is (`relief_offsets`),
- which colour role it wears (`parity_role`),
- which glyphs the LIVE CROWN needs and in what order
  (`crown_glyph_alphabet`, `crown_sequence`, `crown_arc_angles`,
  `crown_advance_angles`, `arc_degrees`).

**THE CROWN ADVANCE LAW** (owner defect 2026-08-07): the live crown's
glyphs no longer advance at a fixed angular step. `crown_advance_angles`
takes one ANGULAR WIDTH per glyph — each glyph's own ink width plus the
crown's tracking, turned into degrees by `arc_degrees` — and centres each
glyph in its own slot on the top or bottom anchor. The fixed step gave a
0.22-glyph-height-wide colon exactly the arc of a 1.45-wide M, which is
what the owner saw as "2 3 : 3 9", scattered. `crown_arc_angles` (the
fixed step) stays for the callers that only pin the arc's DIRECTION, and
feeding equal advances to the new law reproduces it exactly.

**THE COMPOSITION LAW** (THE FIDELITY RULING, owner correction
2026-08-06, [the ring ledger](../../research/ring_rework.md) §2): a seat
carries exactly ONE content. `numeral_hours(letter_hours)` returns the
hours of the outer band that carry a NUMERAL — every hour except the ones
the preset seats a LETTER on — and is the one place the ring's own 1..24
counting (midnight = 24) folds into the band's 0..23.
`inner_number_seats(variant)` is the same law on the inner band: each
shipped variant is one of the owner's NUMBERLESS plates plus the
five-minute seats that carry a number, so a seat holding one of his arrows
never also holds a number. An Ω with a 0 under it is the defect both
functions exist to make impossible.

**THE ANGULAR WEDGE** (owner ballot verdict 2026-08-13): the composition
law above answers a STATIC question — which seat belongs to a letter —
and it is the whole answer only while the jewels ride the band. The
`numerals_turn` rotation scope (`config.dial.WORLD_ROTATION_SCOPES`) pins
the jewels and the crown to the SCREEN and lets the numerals travel under
them, so the collision becomes a live one and this module answers it too:

- `jewel_arc_half_deg(ring_size, jewels_scale)` — half the arc one jewel
  occupies, derived from the ring's own seating data (the stamped height
  `RING_JEWEL_ART_SCALE * jewels_scale` on the stamped radius
  `dial.outer_centreline`), never a magic number. Its one honest
  approximation is written into its docstring: the seating data knows a
  plate's HEIGHT, not its per-glyph WIDTH, so the width is taken as equal
  to the height — square masters, and conservative where a glyph is
  narrower, which errs toward hiding rather than clipping.
- `numeral_arc_half_deg()` — half a SEAT PITCH. A numeral owns its seat
  and nothing more. Measuring ink instead would make the rule depend on
  which digits happen to stand there, on the face and on the size slider;
  the owner chose the wedge over a pixel test for exactly that reason.
- `occluded_numeral_hours(jewel_hours, offset_deg, jewel_half_deg)` — the
  hours whose numeral is NOT DRAWN because a fixed jewel's arc meets it.
  Touching arcs do not overlap; anything that does hides the numeral
  whole. The owner's partial-cut rule ("a jewel that clips two adjacent
  numerals suppresses BOTH") needs no branch of its own: a jewel standing
  between two seats simply overlaps both wedges. It can never reach a
  third, because the seats are 15 degrees apart.

The other half of that verdict costs this module nothing: with the jewels
off the seats, `numeral_hours` is handed the OCCLUDED hours instead of the
letter seats, so the labels 6, 12, 18 and 0 — bare on every release before,
because a jewel sat on each — are composed the moment the rotation carries
them clear. Seat 24 is the band's own hour 0 and `hour_labels` already
names it "0", the only non-duplicate name midnight has.

Everything is a plain float, tuple or string. `render/` turns them into
pixels; nothing here knows that pixels exist.

## The laws it implements

**Seating** (ledger §4, amended by the owner 2026-08-11 — THE FLOWING
SIDES) — angles run clockwise from the top, folded into (−180°, 180°].
Only the TOP and BOTTOM seats (0/180) stand upright; the SIDE squares
(±90) no longer stand upright of their own right — they FLOW with the
half they open clockwise: the +90 seat turns with the lower half (the
extra 180° flip), the −90 seat turns with the upper half (no flip). Every
other numeral takes the angle it sits on, and the lower half turns a
further 180° on BOTH signs of the fold so nothing reads upside down.
`upright` seating is `rot = 0` everywhere. The former `flow_squares`
parameter is gone — this is now the only rule.

**Light** (ledger §6) — `radial` puts one lamp at the dial centre, so every
numeral throws its shadow straight outward:
`offset(deg) = depth · (sin deg, cos deg)`, **y positive UP**. The four
square angles therefore land exactly on `(0, +d) · (+d, 0) · (0, −d) ·
(−d, 0)`, which is the table the panel's readout prints and
`tests/test_numerals.py` pins. `fixed` returns the typed X/Y offset
unchanged — what is typed is what lands, and `depth` says nothing.

**Relief** (ledger §5) — `cast` is ONE copy at the full depth (the gap
stays open, the numeral floats); `extrude` is `round(depth)` copies walking
out from the glyph to the full depth (they weld into a side wall); `emboss`
is one dark copy at `+depth` and one lit copy at `−0.6 · depth`. The
offsets returned are PAGE-SPACE — the render side never applies them inside
a numeral's own rotated frame, or the lower half of the ring would throw
its relief the opposite way from the upper half.

**Parity** (ledger §3) — an EVEN numeral is a white plate on the ring, an
ODD one is a cut-out of ring colour. `parity_role` answers `"even"` /
`"odd"` for a label; the hexes live in `config/palette.py`. The BORDER is
what makes rule B visible at all, which is why its default is a measured
number and not zero (see
[Numeral Bands](../../render/__about/numeral_bands.md) → The Fidelity
Ruling).

**The live crown** (ring_rework §3) — exactly ELEVEN glyphs exist (the ten
digits and the colon), so `crown_glyph_alphabet()` is what the renderer
rasterizes once per settings change. `crown_sequence(hour, minute, fmt)`
then names, per minute, which of them to compose: `"hh:mm"` → `1 2 : 3 5`,
`"12h 35min"` → `1 2 h 3 5 m i n` (the h/min run is drawn in the small cut
— see `render/numeral_bands.py`).

## Connections

### Uses
- [Angles](angles.md) — the dial's one clockwise-from-top convention
- `config.dial` — the roster names, ranges and step tables

### Used by
- [Numeral Bands](../../render/__about/numeral_bands.md) — rasterizes them
- [Numeral Relief](../../render/__about/numeral_relief.md) — paints them
- [Numeral Layers](../../render/layers/__about/numerals.md) — seats them
- `tests/test_numerals.py` — the golden tables
