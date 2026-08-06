# render/numeral_bands.py

Builds the two band plates and the eleven crown glyphs — **once at startup
and once per settings change**, never per frame — and holds them in the
process-wide cache THE ONE COPY RULE demands.

## Purpose

Three products, one cache:

| Product | Built by | Rebuilt when |
|---|---|---|
| OUTER band plate — the 24 hour numerals in relief | `outer_band_plate` | its `BandSpec` changes (including `offset_deg`) |
| INNER band plate — the twelve minute numerals + the five tick families, in white glow | `inner_band_plate` | its `BandSpec` changes |
| The ELEVEN crown glyphs — digits 0–9 and the colon, in crown size and relief | `crown_glyph_set` | its `CrownSpec` changes |

A `BandSpec`/`CrownSpec` is a frozen dataclass carrying exactly what can
make two plates differ: the pixel diameter, the face, the size, the band
width, the seating, the relief style, the depth, the light, the darkness,
the contact blur, the border and — for the outer band alone — the
`offset_deg` the Heliocentric rotation will drive. Because the spec IS the
key, a changed rotation re-renders the band without any caller changing
shape, which is exactly what wave 4 needs.

`_PLATES` and `_CROWNS` are module-level dicts: N watches showing the same
settings hold ONE copy of each plate, like `render.assets.shared_cache`
and every other shared book.

## The live crown

`crown_glyph_set` rasterizes the eleven glyphs ONCE. `compose_crown` then
does the per-minute work: it takes a glyph sequence from
`core.numerals.crown_sequence`, looks each glyph up in the finished set,
and returns `(image, angle, rotation)` triples laid out along the crown arc
by `core.numerals.crown_arc_angles`. That is a dictionary lookup and some
arithmetic — no font shaping, no rasterization, no allocation of anything
larger than a tuple, so a MINUTE-cadence layer can afford it every tick.

The `"12h 35min"` format's `h`/`min` run is rendered in the SMALL CUT
(`config.dial.CROWN_SMALL_CUT_FRACTION` of the digit size) — the plate
library has no lowercase, so these come from the same face as the digits,
which is why the crown's default face is chosen for full coverage rather
than inherited from the hour band (see
[Numeral Fonts](numeral_fonts.md)).

## Never on the paint path, never on the disk

Every function here allocates and rasterizes. All of them are called from
`app.controller`'s settings-apply path and from the layers' own lazy
first-build, and the results are cached; `paint()` only ever blits.
Nothing reads or writes a file — the plates are computed, not stored.

## Connections

### Uses
- [Numerals](../../core/__about/numerals.md) — all the math
- [Numeral Relief](numeral_relief.md) — the per-glyph paint
- [Numeral Fonts](numeral_fonts.md) — the proven faces

### Used by
- [Numeral Layers](../layers/__about/numerals.md)
