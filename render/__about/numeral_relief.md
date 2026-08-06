# render/numeral_relief.py

Paints ONE numeral — body, border and relief — into a band plate, in
**page space**, at device resolution.

## Purpose

`core/numerals.py` decides where a glyph sits, how far it turns and which
way its relief is thrown. This module is the only place that turns those
numbers into paint. It owns three things:

1. **The glyph path in page space.** A numeral's outline is built once with
   `QPainterPath.addText`, centred on its own tight bounding box, then
   transformed by `translate(seat) · rotate(rot)`. The relief copies are
   translated by the light vector AFTER that transform — never before.
   That is the ledger's own rule (§5): the relief is real geometry, so a
   tilted seat must not bend its own shadow, and the lower half of the ring
   (which carries the extra 180°) must not throw its relief the opposite
   way from the upper half.
2. **The parity colours** (ledger §3) — even numerals are a white body with
   a ring-colour border, odd numerals a ring-colour body with a white
   border. At border 0 an odd numeral is ring on ring and exists ONLY
   through its relief; that is deliberate, not a bug.
3. **The two soft passes** — the outer band's optional CONTACT BLUR (a
   small, intense black blur with no offset that seats a numeral against
   the metal) and the inner band's WHITE GLOW (small radius, strong
   intensity, a border-and-glow rather than a diffuse halo). Both are drawn
   as a whole-band silhouette layer, blurred ONCE and composited under the
   crisp pass — never per glyph, and never as N stamped copies around a
   circle (the defect that scalloped the letter shadow at 1440p).

## DPR and the pixelation lesson

Every length that reaches a pen or a blur is a DEVICE-pixel length derived
from the plate's own pixel size — no fixed sample counts, no logical-pixel
constants. `box_blur_alpha` runs three box passes (a good gaussian
approximation) with a radius in device pixels, so a 1440p plate gets a
1440p-wide blur and a 360 px plate gets a 360 px one. That is the S1 shadow
fix applied at the source instead of patched afterwards.

## Off the paint path

Nothing here is ever called from `paint()`. The band builder
([Numeral Bands](numeral_bands.md)) calls it while a settings change is
being applied, writes the result into a cached `QImage`, and the layers
blit that image. No disk is touched at any point.

## Connections

### Uses
- [Numerals](../../core/__about/numerals.md) — the seats, rotations and
  relief offsets
- [Numeral Fonts](numeral_fonts.md) — the proven `QFont`
- `config.palette` — every hex

### Used by
- [Numeral Bands](numeral_bands.md)
