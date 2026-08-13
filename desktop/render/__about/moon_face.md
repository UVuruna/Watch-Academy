# Moon Face

**Script:** [Moon Face (script)](../moon_face.py) · **Flow:** [diagram](../__flow/moon_face.md)

## Purpose
How the Moon's OWN DISC is painted — the three owner-approved
treatments of the unlit half, and the lunar eclipse's umbra sweep
across the face.

Born from the owner's 2026-08-10 verdict on the rendering-proposals
page. Until then the unlit region was over-PAINTED with a translucent
shadow (`moon_shadow_alpha = 0.82`), so at a thin crescent the maria
still showed through and the marker stayed a full round disc with a
bright edge — his complaint that a 5 %-lit Moon "does not look like it
is on the horizon". That treatment is RETIRED, not kept as a menu
entry: it was the defect the round was opened to fix.

THE BLACK DISC (owner correction 2026-08-10, the screenshot round the
day after): the first cut of "opaque" painted the face and then washed
the dark region with `dark_color` at 0.97 alpha — on the dial's
coloured wedges that read as exactly the translucent gray he had
already rejected. "Opaque" now lays a fully opaque BLACK disc
(`palette.MOON_SHADOW_BLACK`) under the whole body first and paints
the lit region over it, so nothing bleeds through the shadow and the
body's true size always reads.

The terminator GEOMETRY is not re-derived here. It comes from
[`asset_variants.moon_lit_region`](asset_variants.md) exactly as
before — the half-disc on the lit side combined with the terminator
half-ellipse (semi-axis `a = R·|cos 2πf|`), united when gibbous,
subtracted when crescent. Only the treatment of what falls OUTSIDE it
changed.

## The face is supplied, never resolved here
`draw_moon_disc` takes a `paint_face` callable rather than an asset
path or a `RenderContext`. Two of the three styles must CLIP before the
face is drawn (they cut the disc rather than cover it), so the module
has to own the ordering — but resolving a pixmap is the dial's job, not
this module's. The dial passes a lambda that draws the moon plate; the
Watch Face picker's preview passes a lambda that draws a plain silver
disc; a test passes a lambda that fills a flat colour. One code path
serves all three, and the same call also replaced the old two-branch
asset/procedural split.

## Connections

### Uses
- [Asset Variants](asset_variants.md) — `moon_lit_region`, the one
  terminator construction
- [Config (folder)](../../config/___config.md) — `constants`
  (`MOON_DARK_STYLES`), `glow` (the eclipse state brightness table),
  `palette` (`MOON_SILVER`, the eclipse tints)

### Used by
- [Layers (subfolder)](../layers/___layers.md) — `YearMarkerLayer`
  draws every Moon marker through `draw_moon_disc`
- [Watch Face (folder)](../../app/___app.md) — `thumbs` builds the
  picker previews by calling the same function at thumbnail scale, so
  a tile can never show art the dial does not draw

## Functions
- `draw_moon_disc(painter, fraction, radius, style, paint_face, dark_color, shadow_alpha)`
  — the whole disc in the chosen style, centred on the painter's
  current origin.
- `draw_umbra_sweep(painter, radius, state, magnitude)` — Earth's
  shadow as a real curved edge crossing the face, deepening to copper
  behind it, with the turquoise ozone rim where the state carries one.

## The sweep after the eclipse rework (owner order 2026-08-13)
Two things changed, and both were accuracy problems as much as display
ones:

1. **The shadow's offset is now the real geometry.** Lunar magnitude is
   the fraction of the Moon's DIAMETER inside the shadow, so the centre
   distance is `d = R + r − 2·r·magnitude`, clamped at zero. The old
   linear "travel" fudge pushed the shadow out by 2.10 r at magnitude 0
   and pulled it to concentric at magnitude 1 — close, but not the
   thing itself, and it clamped the magnitude at 1.0 so every totality
   looked identical. A PENUMBRAL eclipse is measured against the far
   wider penumbra, so it uses its own radius rather than claiming an
   umbral bite it never has.
2. **The shadow is graded, not flat.** At totality the Moon is entirely
   inside the umbra, so a flat copper circle left the "sweep" style
   with no edge anywhere — the one type it was made for showed a
   featureless disc. The umbra is now painted from a near-black core
   (`palette.ECLIPSE_UMBRA_CORE_COLOR`) out to the blood copper at its
   rim, which is what a totally eclipsed Moon really looks like: it is
   lit only by the light bent through every sunrise and sunset on Earth
   at once, and it is brightest toward the limb nearest the umbra's
   edge. The penumbral wash is graded the same way and for the same
   physical reason — without it, "umbra_sweep" and "halo" drew the same
   uniformly dimmed disc for a penumbral eclipse.
- `dark_region(fraction, radius)` — the disc MINUS the lit region, the
  shared path both the opaque fill and the inner glow clip to.
