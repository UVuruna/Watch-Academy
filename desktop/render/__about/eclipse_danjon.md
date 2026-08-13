# Eclipse Danjon

**Script:** [Eclipse Danjon (script)](../eclipse_danjon.py)

## Purpose

THE DANJON SCALE as a display style (owner ballot 2026-08-13,
"danjon_scale" — his note beside it: *this one wants a table and text
with it*). L=0..L=4 is the eyeball brightness/colour scale an observer
estimates for a totally eclipsed Moon at mid-totality:

| L | What the observer sees |
|---|------------------------|
| 0 | Very dark eclipse; the Moon almost invisible, especially mid-totality |
| 1 | Dark, grey or brownish; detail distinguishable only with difficulty |
| 2 | Deep red or rust-coloured, with a very dark central shadow and a relatively bright outer umbral edge |
| 3 | Brick-red, usually with a bright or yellow rim to the shadow |
| 4 | Very bright copper-red or orange, with a bluish, very bright umbral rim |

The five colours of `palette.ECLIPSE_DANJON_COLORS` are read straight
off those descriptions, and they are used TWICE — as the gauge's five
legend cells and as the multiply the Moon's own disc wears at the
indicated step — so the ladder and the Moon can never disagree about
what an L means.

## What this style honestly CANNOT know

**The catalog carries no Danjon value, and none can be computed.** The
Deep Time pack's `lunar_eclipses` table (`data.deep_time.DeepEclipse`)
holds `jd_ut`, the calendar instant, the `type`, and `magnitude` — and
on lunar rows nothing else; `lat`/`lon` are solar-only. L is not a
predictable quantity at all: it is an EYEBALL ESTIMATE made during the
event, and what it lands on depends on the state of Earth's
stratosphere on the night — volcanic aerosol famously drove the
December 1992 eclipse (after Pinatubo) down to L=0 while a clean
atmosphere gives L=3–4 for a comparable geometry.

So this module does not invent an observation. It derives an
**INDICATIVE** L from the one real datum, by the accepted proxy: DEPTH
IN THE UMBRA, i.e. the umbral magnitude. Totality begins at magnitude
1.0 (grazing — the Moon skims the umbra's bright outer edge, the
brightest case, L=4) and the deepest possible central eclipse reaches
magnitude ≈ 1.83 (the darkest case, L=0). That ceiling is measured, not
guessed: Earth's umbra at the Moon's distance is ~2.65 lunar radii, and
the magnitude at concentric immersion is `(R + r) / 2r =
(2.65 + 1) / 2 = 1.825`. The ramp between the two is linear.

The estimate is marked as an estimate in three places, deliberately:

1. **In the mark** — the gauge's cell marker is a DASHED outline, never
   a solid one, and dashed is this program's way of saying "indicative"
   (the same choice the band's penumbral segment already makes).
2. **In the code** — `indicative_danjon`'s name and docstring.
3. **In the docs** — here, and in the Encyclopedia text that explains
   the style.

`indicative_danjon` returns `None` for anything but a TOTAL eclipse,
because the scale is only defined for totality. That is not a gap to be
papered over — it is the third of this style's three pictures:

- **total** → the five cells filled with their own colours, a dashed
  marker under the indicative step, and the step's value spelled out
  beside the ladder in LETTER PLATES (`L3`).
- **partial** → the ladder drawn as empty outlines (no reading exists),
  with a filled bar beneath whose length is the umbral magnitude — the
  real datum a partial eclipse does carry.
- **penumbral** → the Moon never enters the umbra, so there is not even
  an umbral phase to rate: faint empty outlines struck through with one
  diagonal.

## The text is PLATES, never a font

`L3` is composed through
[Letter Plates](letter_plates.md)'s `plate_text_pixmap` — THE ONE PLATE
LAW. A glyph with no plate raises rather than falling back to a font,
and every glyph this module needs (`L`, `0`–`4`) has one.

## Connections

### Uses
- [Letter Plates](letter_plates.md) — `plate_text_pixmap`, the only door
  to drawn text
- [Painting](painting.md) — `tinted_gray`, the disc multiply for the
  states with no L
- [Config (folder)](../../config/___config.md) —
  `palette.ECLIPSE_DANJON_COLORS`/`ECLIPSE_DANJON_FRAME_COLOR`/
  `ECLIPSE_DANJON_MARKER_COLOR`, `glow.ECLIPSE_STATE_MOON_BRIGHTNESS`

### Used by
- [Layers (subfolder)](../layers/___layers.md) — `YearMarkerLayer` draws
  the Moon marker's eclipse this way when `eclipse_lunar_style ==
  "danjon_scale"`
- [Eclipse Plates](eclipse_plates.md) — the Encyclopedia's own plate for
  the style
- [Watch Face (folder)](../../app/___app.md) — `thumbs` builds the
  picker tile with the same call

## Functions
- `indicative_danjon(state, magnitude)` — the INDICATIVE L (0–4) for a
  total eclipse, `None` for every other state. Never an observation.
- `draw_danjon_scale(painter, radius, state, magnitude)` — the whole
  style: the disc multiply at the indicated step (or the plain state
  brightness where no L exists) plus the gauge beneath the body.
