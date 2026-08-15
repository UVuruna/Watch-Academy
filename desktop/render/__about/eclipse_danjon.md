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

## The gauge sits on the RIM, on the side facing the dial's centre

(Owner order 2026-08-15.) Two pieces, two rules:

1. **The label (`L3`) sits dead centre of the disc**, always upright.
   It is text, and text never rotates with the dial — the pre-existing
   southern-hemisphere "turn the gauge back upright"
   `painter.rotate(180.0)` in `render/layers/year_marker.py` still
   applies to it exactly as before; only the LADDER below gets a
   *second*, angle-derived rotation on top of that.
2. **The ladder (plus, for partial/penumbral, the magnitude bar or the
   strike-through riding the same block) sits close to the rim, on the
   inward side, its long axis parallel to the rim's own tangent there.**
   His own words, kept verbatim: *"standardno racuna se ugao na
   kruznici i tako se pozicionira taj pravougaonik da bude paralelan sa
   tangentom na kruznici"* — the angle on the circle is computed as
   usual, and the rectangle is positioned parallel to the circle's own
   tangent there. lang-ok: the owner's own ballot sentence, quoted so
   the requirement cannot be re-derived wrongly.

### One rotation, not four cases

`_gauge_placement(radius, dial_angle_deg)` is a PURE function — no
QPainter, no Qt painting at all — that returns `(dx, dy, rotation_deg)`:
the ladder block's own centre, offset from the Moon's centre, and the
angle the whole block (ladder, marker, bar/strike) is rotated by. Both
numbers come from ONE input, `dial_angle_deg`, the Moon's own dial angle
in `render.painting.dial_point`'s convention (clockwise from top):

```
theta = radians(dial_angle_deg)
dx = -distance * sin(theta)
dy =  distance * cos(theta)
rotation_deg = dial_angle_deg
```

Why this single rotation is correct at every angle, not only the four
the owner named as consequences:

* At `dial_angle_deg == 0` (Moon at the dial's top) "straight down" IS
  "toward the dial's centre" — `dial_point`'s own origin sits below a
  body drawn at the top. So the un-rotated placement (the style's
  original, untouched picture) already satisfies "inward" for angle 0.
* `dial_point` places bodies clockwise from top, and `QPainter.rotate`
  turns the coordinate system clockwise in the same y-down frame — the
  SAME convention on both sides — so carrying that "faces down at angle
  0" construction through `painter.rotate(dial_angle_deg)` keeps it
  facing inward, and keeps the ladder's own width axis perpendicular to
  the radius (parallel to the tangent), at every angle in between, not
  only the four cardinals.

Four hard-coded cardinal cases would look right at 0/90/180/270 and
wrong everywhere else — the tooth,
`tests/test_eclipse_danjon_placement.py`, pins the cardinals AND two
off-cardinal angles (45 deg, 200 deg) specifically to catch that defect,
plus a counter-proof that dropping the rotation (keeping only the
translation) makes the very same assertion fail.

Draw-side, `draw_danjon_scale` calls `_gauge_placement` once, translates
and rotates the painter by its result, then draws the ladder/bar/strike
group in that LOCAL frame exactly as before (only the constants moved
closer to the rim, since the label no longer needs a gap between the
body and the ladder) — the label is drawn separately, before that
transform, so it never inherits the ladder's rotation.

`dial_angle_deg` defaults to `0.0` — "Moon at the top", the style's
original picture — so the Encyclopedia plate (`eclipse_plates.py`) and
the picker tile (`app/watch_face/thumbs.py`) call `draw_danjon_scale`
unchanged and keep their fixed composition. Only the live dial
(`render/layers/year_marker.py`) passes a real angle: the eclipse
body's own `eclipse_body_angle(ctx, event)`, the same one its own `pos`
is placed at.

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
- `draw_danjon_scale(painter, radius, state, magnitude, dial_angle_deg=0.0)`
  — the whole style: the disc multiply at the indicated step (or the
  plain state brightness where no L exists), the `L` label centred in
  the disc (upright), and the ladder/bar/strike group rotated onto the
  rim's tangent at `dial_angle_deg`.
- `_gauge_placement(radius, dial_angle_deg)` — PURE; the ladder block's
  translation and rotation, see above. Tooth:
  `tests/test_eclipse_danjon_placement.py`.
