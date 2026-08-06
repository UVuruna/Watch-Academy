# render/numeral_fonts.py

Resolves a ROSTER NAME from [The Dial Numerals](../../research/hour_numerals.md)
§7 to a real `QFont` on this machine, and PROVES that the face can actually
draw the glyphs the dial asks of it.

## Purpose

The two rosters name faces the way a designer does — "Bahnschrift Bold",
"Poppins Black", "Arial Black" — but Qt sees a FAMILY plus a STYLE. This
module owns that one mapping (`config.dial.NUMERAL_OUTER_FACES` /
`NUMERAL_INNER_FACES` carry `(family, style)` pairs) so no caller ever
builds a `QFont` from a roster label itself.

## The coverage proof (why this module exists at all)

`Bernard MT Condensed` and `Eras Bold ITC` were **recovered from
`illustrator/Clock 24h.ai`** and installed by hand. A recovered face can
carry a character in its cmap and still have an EMPTY outline for it —
`QRawFont.supportsCharacter(':')` answers True while the glyph draws
nothing. That is not hypothetical: measured on this machine (2026-08-06),
`Bernard MT Condensed` renders its ten digits perfectly and draws **nothing
at all** for `:` `.` `h` `m` `i` (zero-area `pathForGlyph`, non-zero
advance). Trusting `supportsCharacter` alone would have shipped a live
crown reading `12 35`.

`glyph_coverage()` therefore proves a face by GEOMETRY, not by cmap: it
takes `QRawFont.pathForGlyph` for each glyph and reports the bounding-rect
area, falling back to a render-and-count-non-blank-pixels pass for faces
whose outlines Qt cannot hand back. `assert_covers()` raises — loudly, at
settings-apply time and never mid-paint — when a face the user picked
cannot draw what the band needs.

The consequence is written into `config/dial.py`: the CROWN's own default
face is **not** the outer band's default, because the outer band needs
digits only (which Bernard has) while the crown needs the colon and the
`h`/`min` cut (which Bernard does not). Both defaults are named there with
this reason beside them.

## Connections

### Uses
- `config.dial` — the two rosters and their defaults

### Used by
- [Numeral Relief](numeral_relief.md) — asks for the sized `QFont`
- [Numeral Bands](numeral_bands.md) — proves the picked faces once per
  settings change
