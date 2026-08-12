# Glyph Shadow

**Script:** [Glyph Shadow (script)](../glyph_shadow.py) · **Flow:** [diagram](../__flow/glyph_shadow.md)

## Purpose

**THE LETTER SHADOW LAW's own home** — the soft stamped halo every RING
glyph wears, and the hard two-colour BORDER the dial's own labels wear.

Two things live here, and they arrived from opposite directions.

### 1. The shadow stamp, extracted

The stamp math (`shadow_sample_count`, `normalized_shadow_alpha`,
`stamp_shadow`, `image_silhouette`) has moved once before: out of
`render.layers.ring` into `render.numeral_bands` (owner correction
2026-08-06) when the live crown's tiles had to wear the same halo the
ring's jewels wore. It moves again now, for the same reason and a third
caller: the on-dial NAME LABELS need it, and they are drawn by
`render.painting`, which `numeral_bands` already imports — so
`numeral_bands` could never be their shared home without a cycle. This
module is low enough for all three. `numeral_bands` re-exports the names
so `render.layers.ring` keeps importing them from where it always did.

### 2. The labels stop being a font — and get a BORDER, not a halo

Owner order 2026-08-12: the weekday names and the Earth's date label
must come from the plate library like everything else, and they must
carry their own edge treatment, for the case he named —

<!-- lang-ok: the owner's own instruction, quoted so the requirement cannot be re-derived wrongly -->
> *"za situacije gde je boja pozadine kao boja slova npr LOOP tematika
> plava na plavom EARTH koji prikazuje datum"*

That is a real failure, not a preference. A label drawn as
white-with-a-black-outline is legible only while the art underneath is
neither white nor black, and LOOP's thematic shade is `cross_blue` — a
dark blue that lands on a blue Earth.

**The first cut was wrong, and his correction IS the design.** It reused
the ring's soft halo, widened to be "dense", and that failed exactly
where it mattered: `SATURDAY`, `TUESDAY`, `MONDAY` and `WEDNESDAY` over
the dim bodies, where a dark cushion around dark ink on a dark ground
separates nothing — while the widened radius began to swallow the
roundel it sat on. His words:

<!-- lang-ok: the owner's own correction, quoted -->
> *"necu veliki halo koji prekriva ceo ROUNDEL ili bilo sta oko cega
> pise NEGO VISE KAO BORDER kretak radijus par px i intenzitet 100%"* —
> and, from the same message, *"shadow beli i crni i radice svuda"*.

So a label wears **two solid contours at full opacity**, each a couple
of DEVICE pixels wide: a dark keyline hugging the ink, a light one
immediately outside it.

| | why |
|---|---|
| **two colours** | ground-independence WITHOUT knowing the ground: on a pale body the dark line reads, on a near-black one the light line does, on a mid tone both do. One colour cannot — that is precisely how the first cut vanished on the dim bodies. |
| **full opacity** | a border, not a glow. `stamp_shadow` renormalizes its per-stamp alpha so N copies read as a soft cushion; `solid_contour` draws every copy at alpha 1.0, so the union is a hard, even outline. |
| **device pixels** | a border is a border at every dial size. A fraction of the letter height is exactly how the first cut grew into something that covered the roundel. Scaled by `dpr` only, so it is the same apparent thickness on a 4K panel as on 1080p. |

Verified over the five worst grounds — near-black, dark blue, dark
green, mid orange and near-white
(`.claude/shots/startup-perf/border_check.png`): the label reads on all
five, including the two where a single-colour edge cannot.

This is also the third arrival of the 2026-08-11 correction — *"tekst
koristi isti kao jewels i crown text a ne ovaj beli FONT"* — after the
crown (0.14.927) and the Fast Travel flash (0.14.927/928). The dial's
own labels were the last white font on the instrument.

## The fallback, and why it is not a law violation

THE ONE PLATE LAW says a glyph with no plate RAISES rather than falling
back, because that fallback is how a whole missing digit alphabet once
shipped as a font-drawn crown with every test green. That rule governs
the LIBRARY DOOR, and `letter_plates.plate_text_pixmap` still obeys it
exactly.

A PAINT LAYER may not die. An exception escaping `paintEvent` with a
`QPainter` still active is the 2026-07-31 crash class — a cascade of
`QBackingStore::endPaint` errors and a permanently broken window. So
`draw_name_label` catches `MissingPlate`, draws that one label with the
old font, and **prints the offending glyph once per process**. Rule #1's
degraded-and-visible, not a silent fallback.

**Measured coverage:** every one of the **881** figure display stems on
disk composes from plates, and so does every weekday label, short and
full. Exactly **one** string in the whole program cannot — the archetype
centre **"The Lord's Day"**, which needs an apostrophe the library does
not have (`assets/instrument/letters/symbols/` holds `@`, `&`, `:`, `$`,
`!`, `?` and the templar cross). That one label draws with the font and
says so on stderr. Whether an apostrophe plate gets drawn is the owner's
call — his art, his decision.

## Connections

### Uses
- [Letter Plates](letter_plates.md) — `plate_text_pixmap`, THE ONE DOOR
  to the plate library (imported lazily inside the function: this module
  sits below `render.painting`, and the plate door reaches
  `render.asset_recolor` -> `render.assets`)
- [Numeral Relief](numeral_relief.md) — `blank_plate`, `plate_painter`,
  `stamp_dpr`, the plate-canvas primitives
- [Config (folder)](../../config/___config.md) — `dial`
  (`RING_JEWEL_SHADOW_*` for the ring's halo, `LABEL_BORDER_DARK_PX` /
  `LABEL_BORDER_LIGHT_PX` for the labels), `palette`
  (`SHADOW_STAMP_TINT`, `SHADOW_STAMP_TINT_LIGHT`)

### Used by
- [Painting](painting.md) — `draw_name_label`, the ONE on-dial label
  draw shared by the weekday bodies, the archetype figures, the calendar
  mount and the centre pass
- [Layers (subfolder)](../layers/___layers.md) —
  `year_marker.YearMarkerLayer._draw_earth_label` (the Earth's date,
  the owner's own blue-on-blue case)
- [Numeral Bands](numeral_bands.md) — re-exports the stamp functions and
  uses them for the baked crown tiles
- [Layers (subfolder)](../layers/___layers.md) — `ring.RingLayer`'s live
  jewel stamp, through `numeral_bands`' re-export

## Functions

### `shadow_sample_count(pixel_radius)` / `normalized_shadow_alpha(samples)`
Unchanged from `numeral_bands`. How many silhouette copies an edge needs
at this device-pixel radius (grown so adjacent stamps stay under
`RING_JEWEL_SHADOW_MAX_GAP_PX` apart — THE PIXELATION FIX, the 1440p
owner bug of 2026-08-06; a scalloped border is worse than no border), and
the per-stamp opacity that keeps a SOFT halo's composited darkness
constant however many copies that turns out to be.

### `stamp_shadow(painter, radius_px, draw_copy)`
The SOFT loop — the ring's and the crown's halo. Renormalized alpha.

### `solid_contour(glyphs, radius_px, color)`
The HARD one — the labels' border. Every copy at full opacity, so the
union is an even outline of exactly `radius_px`. The difference between
this and `stamp_shadow` is the whole of the owner's correction.

### `image_silhouette(image, color)`
An image's own alpha filled flat with `color`.

### `bordered_plate_text(text, height_px, metal, dpr)` / `draw_bordered_plate_text(...)`
Plate-composed text wearing both contours, as a `QPixmap` whose INK
height is `height_px`, and the centred draw of it. Padded by the border
width, so a caller centring the pixmap centres the GLYPHS. Raises
`MissingPlate` straight through — the decision to fall back belongs to
the paint layer.

### `clear_cache()`
Drops the composed labels — a metal/shade switch, an art wave, a test.

## Design Decisions

- **Ink height, not box height.** The old font path sized labels by
  `QFont.setPixelSize`, which is an em box with ascender and descender
  slack; a plate is its glyph with no slack, so the same number would
  have drawn a visibly LARGER label. `PLATE_INK_HEIGHT_FRACTION` maps
  the caller's font-shaped number onto the plate's ink so the
  SET-UNIFORM sizing law (owner verdict 2026-07-18) keeps meaning what
  it meant.
- **The label's metal is the CROWN's metal.** `painting.label_finish`
  reads `letter_plates.crown_finish(skin).metal` — there is exactly one
  answer to "which metal does a plate glyph wear on this dial" (Rule
  #5). On LOOP that really does make the date blue, which is why the
  owner asked for the border rather than for a different colour: the
  border is the fix, the colour stays the instrument's.
- **Cached per (text, ink height, metal, dpr).** These labels repaint
  with the dial and composing one walks a plate per character through
  `jewel_metal_file`.
- **The old black outline is gone, not kept underneath.** An outline
  plus a border is two edges reading as a smudge at small sizes. The
  border replaces it and does its job on more grounds than it did.
