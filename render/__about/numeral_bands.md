# render/numeral_bands.py

Builds the two band plates and the eleven crown glyphs — **once at startup
and once per settings change**, never per frame — and holds them in the
process-wide cache THE ONE COPY RULE demands.

## Purpose

Three products, one cache:

| Product | Built by | Rebuilt when |
|---|---|---|
| OUTER band plate — the metal AND the hour numerals standing on it | `outer_band_plate` | its `BandSpec` changes (including `offset_deg`) |
| INNER band plate — the minute NUMBERS alone, in white border + glow | `inner_band_plate` | its `BandSpec` changes |
| The ELEVEN crown glyphs — digits 0–9 and the colon, in the crown-text size family | `crown_glyph_set` | its `CrownSpec` changes |
| Each crown glyph's own INK WIDTH, for the advance law | `crown_glyph_ink` | its `CrownSpec` changes |
| A font of a given face fitted to a target INK height | `crown_font_for_ink_height` | never (pure per call) |

A `BandSpec`/`CrownSpec` is a frozen dataclass carrying exactly what can
make two plates differ: the pixel diameter, the face, the size, the band
width, the seating, the relief style, the depth, the light, the darkness,
the contact blur, the border, the ring tint/saturation, the preset's own
LETTER seats or INNER variant, and — for the outer band alone — the
`offset_deg` THE WORLD OFFSET drives
([World](../../core/__about/world.md)). Because the spec IS the key, a
changed rotation re-renders the band without any caller changing shape.
The INNER band always keys on `0.0` — it never rotates in any mode — so
its plate is shared across both phases.

## THE FIDELITY RULING (owner correction 2026-08-06)

The first live-rendered bands reached the owner's screen and diverged from
his art. Three laws followed
([the ledger](../../research/ring_rework.md) §2), and this module is where
they are implemented.

**1 · The band COMPOSES; it never stacks.** The outer plate is drawn
WHOLE — the flat `#656A70` annulus with its black outer rim, then a
numeral at every hour the preset does not seat a LETTER on. The printed
outer PNG is not blitted anywhere any more, because it already carries
printed numerals, and a live numeral over them is the defect the ruling was
issued for (an Ω with a 0 showing beneath it). The INNER band is the same
law read the other way: `RingLayer` blits the variant's NUMBERLESS base
plate (his own art — 360 day hairlines, 60 minute strokes, the quarter/octa
arrows) and this module composes only the NUMBERS into the seats that base
leaves empty. `config.dial.RING_INNER_COMPOSITION` is that map, and it is
his own construction: `seconds.png` IS `simple_point.png` with the numbers
set into it.

**2 · His art is the look.** Every geometry and style constant this module
reads was MEASURED off his plates at their native 3600 px, not chosen:

| Measured on his plates | Constant |
|---|---|
| metal 0.8858 → 0.9998 of the radius, flat `#656A70` (83.7% of band pixels) | `NUMERAL_OUTER_RADIUS_FRACTION`, `NUMERAL_OUTER_BAND_WIDTH_FRACTION` |
| a hard black rim, 0.0035 of the radius, on the OUTER edge alone | `NUMERAL_BAND_RIM_FRACTION`, `palette.NUMERAL_BAND_RIM` |
| digit cap height 0.0436 of the dial diameter | `NUMERAL_OUTER_SIZE_DEFAULT` |
| the odd numerals' white rim, 2.4 px mean-thick at 3600 | `NUMERAL_BORDER_DEFAULT` |
| black reaching 11.1 px outward / 11.3 px inward of a glyph — SYMMETRIC | `NUMERAL_SHADOW_REACH_UNITS` + `NUMERAL_CONTACT_BLUR_DEFAULT` |
| inner elements: a ring-ground body inside a white rim, under a white glow | `palette.MINUTES_INK` / `MINUTES_BORDER` |

Two of those corrected the ledger's own first-pass guesses: size 90 drew a
visibly thinner band than his, and border 0 left an odd numeral with no
white outline at all — the loudest single difference between his art and
wave 3's screen.

**3 · Render time changes WHAT, never HOW it looks.** The user's picks
(font, size, which seats carry jewels, which inner variant) decide the
CONTENT of a seat. The style is fixed by the measured constants above.

### Why the halo is a dilation and not a blur

His black runs SOLID for about 11 px and only then fades over 3. A blurred
silhouette cannot make that plateau — a blur wide enough to reach 11 px is
already smoke at its own edge. So the halo is a DILATION
(`numeral_relief.draw_dilated`: the glyph stroked with a `2 x reach` pen
under the same glyph filled), and the CONTACT BLUR is only its soft edge.
The halo takes NO throw, because his is symmetric to within a fifth of a
pixel; the ledger's directional relief (`draw_relief`, `cast`/`extrude`/
`emboss` at the settled depth) is drawn over it and lies inside it until
the user asks for a deeper one.

`_PLATES` and `_CROWNS` are module-level dicts: N watches showing the same
settings hold ONE copy of each plate, like `render.assets.shared_cache`
and every other shared book. `_PLATES` carries the ONE COPY RULE's own
ceiling (`dial.NUMERAL_PLATE_CACHE_MAX`): in the Heliocentric mode the
band's rotation moves with solar noon — once a day, twice with the night
phase — so without a bound a watch left running for a year would hold a
year of plates. Beyond the ceiling the oldest inserted plate is dropped.

## The live crown

`crown_glyph_set` rasterizes the eleven glyphs ONCE. `compose_crown` then
does the per-minute work: it takes a glyph sequence from
`core.numerals.crown_sequence`, looks each glyph up in the finished set,
and returns `(image, angle, rotation)` triples laid out along the crown
arc by `core.numerals.crown_advance_angles`. That is a dictionary lookup
and some arithmetic — no font shaping, no rasterization, no allocation of
anything larger than a tuple, so a MINUTE-cadence layer can afford it
every tick.

The `"12h 35min"` format's `h`/`min` run is rendered in the SMALL CUT
(`config.dial.CROWN_SMALL_CUT_FRACTION` of the digit size) — the plate
library has no lowercase, so these come from the same face as the digits,
which is why the crown's default face is chosen for full coverage rather
than inherited from the hour band (see
[Numeral Fonts](numeral_fonts.md)).

### THE VISUAL DEFECTS WAVE (owner defects 2026-08-07)

Three of the five rulings land in this module.

**ONE CROWN SIZE LAW.** The owner saw "2 3 : 3 9" in tiny dim glyphs at
the top of the window while NON NOBIS DOMINE stood large and silver
below. Root cause: two size laws on one ring. The static crown arc is
sized `2 * radius * RING_CROWN_TEXT_SIZE * crown_text_scale`
([Ring Layer](../layers/__about/ring.md)); the LIVE crown was sized
`numeral_outer_size * NUMERAL_UNIT_FRACTION * CROWN_NUMERAL_SIZE_FRACTION`
— a law borrowed from the HOUR BAND, landing ~19% smaller. Then a second,
larger shortfall compounded it: that number was handed to
`QFont.setPixelSize`, which sets the EM box, while a jewel plate is
blitted by its IMAGE height, which is its ink plus 0.8% padding. On the
default face a digit therefore drew only 0.717 of the box it was given.

The fix: `CrownSpec.height_px` is the glyph BOX, handed in by
[the crown layer](../layers/__about/numerals.md) from the SAME expression
the static arc uses; the colon is scaled to that box exactly as a letter
plate is; and a digit's font is FITTED by
`crown_font_for_ink_height`, which probes the face's own ink/em ratio at
`CROWN_FIT_PROBE_PX` and scales until the ink fills
`CROWN_PLATE_INK_FRACTION` (0.992 — MEASURED off A/N/O/M/X.png, all 512
px tall with 508 px of ink). Probed, never tabled, so a roster change
cannot leave a stale per-face constant behind.
`CROWN_NUMERAL_SIZE_FRACTION` is retired.

**THE CROWN ADVANCE LAW.** The other half of "scattered": a fixed
angular step gave the colon — 0.22 glyph-heights of ink — exactly the arc
of a 1.45-wide M. `_build_crown` now records each glyph's own INK WIDTH
(the path's, never the tile's, which carries shadow padding on both
sides), `crown_glyph_ink` publishes it, and `compose_crown` advances each
glyph by its ink plus `CROWN_TRACKING_FRACTION` of the box.

**ONE METAL PER CROWN.** The colon rendered GOLD beside gray digits.
Root cause: `jewel_metal_file` honestly falls back to the gold master
until the background recolor drains, and this module BAKES its tiles once
and caches them — so the fallback froze in place for the life of the
process, while the font-drawn digits went straight to the real metal's
body tone through `_crown_metal_body_color`. `CrownSpec.colon_source`
carries the RESOLVED path into the cache key, so the drain's arrival is a
new key and the crown rebuilds in the metal the rest of the ring wears.

### THE TIME CROWN LOOK (owner correction 2026-08-06)

The owner's furious correction: the live crown used to build its glyphs
through the OUTER BAND's own numeral relief/parity machinery
(`draw_relief` + `draw_body` in [Numeral Relief](numeral_relief.md)) — a
white/gray plate-and-frame that is not his jewels' look at all. Every
glyph now goes through THE LETTER pipeline instead:

- **The colon is HIS plate.** `time.png` (`config.dial.RING_JEWEL_ART_DIR`)
  resolves through `render.asset_recolor.jewel_metal_file` — the EXACT
  door every ring jewel resolves its finish through — scaled to the
  crown's own glyph height and stamped with the shadow below. No font
  ever draws it; `assert_covers` no longer asks any face to cover `":"`.
- **The ten digits (and the `"12h 35min"` h/min cut) have no plate**, so
  they wear the crown's own metal BODY COLOR
  (`_crown_metal_body_color`) — the SAME ramp `jewel_metal_file`
  recolors onto, sampled flat at the recipe's own `body_position`
  instead of recolored pixel-by-pixel (there is no baked shading on a
  font glyph to preserve).
- **Both wear THE LETTER SHADOW LAW's stamped halo** —
  `shadow_sample_count`/`normalized_shadow_alpha`/`_stamp_shadow`, the
  SAME construction `render.layers.ring.RingLayer._draw_ring_glyph`
  stamps live for a real jewel (moved here from `render.layers.ring`
  so both callers can import it without a cycle), baked into the tile
  ONCE instead of drawn every repaint.

`CrownSpec` dropped the outer band's `relief_style`/`depth_units`/
`light`/`darkness`/`border_units` fields entirely and gained `metal`
(`RingSpec.crown_text_metal` — the SAME `settings.ring_finish` the ring
jewels wear) and `shade`, so two watches with different active shades
never collide in the shared `_CROWNS` cache. The 2026-08-07 round
replaced `size_units` with `height_px` and added `colon_source` (above).

## Never on the paint path, never on the disk

Every function here allocates and rasterizes. All of them are called from
`app.controller`'s settings-apply path and from the layers' own lazy
first-build, and the results are cached; `paint()` only ever blits.
Nothing reads or writes a file — the plates are computed, not stored.

## Connections

### Uses
- [Numerals](../../core/__about/numerals.md) — all the math
- [Numeral Relief](numeral_relief.md) — the per-glyph paint (the band
  builders only — the live crown's own glyphs no longer use it)
- [Numeral Fonts](numeral_fonts.md) — the proven faces
- [Asset Recolor](asset_recolor.md) — `jewel_metal_file`, the colon's
  own door
- `recolor` package — the metal ramp the crown's flat digit body color
  is sampled from (THE TIME CROWN LOOK)

### Used by
- [Numeral Layers](../layers/__about/numerals.md)
- [Instrument Diagrams](instrument_diagrams.md) — `band_plate` composes
  the `chi` figure's own outer band
