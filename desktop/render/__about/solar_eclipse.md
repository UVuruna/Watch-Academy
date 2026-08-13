# Solar Eclipse

**Script:** [Solar Eclipse (script)](../solar_eclipse.py) · **Flow:** [diagram](../__flow/solar_eclipse.md)

## Purpose
Every picture the SUN side of an eclipse can draw — six display styles
over four catalog types — and the geometry all of them share.

It was born out of [Marker Marks](marker_marks.md) on 2026-08-13, when
the owner's three ballot-accepted styles were painted and that module
crossed THE STRUCTURE LAW's 1,000-line threshold. The split is by
RESPONSIBILITY, not by size: `marker_marks` draws what a body wears on
an ORDINARY day — the position pointer and the four life stations, marks
the Earth and the Moon wear all year — while this module draws the
EVENT, the third body that only exists on the day of an eclipse.
`draw_solar_eclipse` and `solar_occulter_geometry` are re-exported from
`marker_marks`, so no call site and no tooth had to move with them.

The lunar half of an eclipse lives in [Moon Face](moon_face.md) and on
the Moon Horizon Band; the halo behind any relocated marker is older
still and lives in [Eclipse Glow](eclipse_glow.md).

## The six styles
| Style | What it draws | How the TYPE is carried |
|-------|---------------|-------------------------|
| `bite` (default) | the owner's two body plates composited — the geometry across the face | the occulter's size and its offset |
| `magnitude_arc` | a ring gauge at 1.18 body radii, body untouched | two lanes for a hybrid, the annular orange |
| `halo` | a soft pearl ring OUTSIDE the body, growing with coverage | a second ring for a hybrid, an orange rim for an annular |
| `totality_path` | a thin arc at 1.30 body radii — its length and brightness say how near the observer stands | the light waiting at the centre line; a split arc for a hybrid |
| `type_emblem` | a badge on the body's lower limb | the badge IS the type |
| `dial_shadow` | light taken away instead of added; **never the default** | an orange rim at the shadow's edge |

## THE TOTALITY PATH — what the data knows, and what it does not
The owner's own brief (2026-08-13): a thin arc beside the body whose
LENGTH and BRIGHTNESS say how near the observer is to the path of
totality — full and bright means standing in the band, short and dim
means it is happening but 3,500 km away.

This is an astronomical instrument, so the honest answer to "what can
this actually measure" is written down rather than assumed:

- **What exists and is real.** `core.clock_state.EclipseEvent.distance_km`
  — the observer's haversine great-circle distance to the catalog's
  GREATEST-ECLIPSE ground point, stamped by `_with_visibility` from the
  Deep Time pack's `solar_eclipses.lat/lon`. The arc is derived from
  exactly this, read off the event and never recomputed, so it can
  never disagree with the hover's own "path {d} km away" reason.
- **What it is NOT.** It is not the distance to the nearest point of the
  central PATH. The catalog stores one point per eclipse, not the track.
  An observer standing squarely ON the path but 2,000 km along it from
  greatest eclipse reads 2,000 km here, so the mark UNDER-reads for
  them — never over-reads, which is the safe direction for an
  instrument.
- **What does not exist anywhere in the program.** A LOCAL magnitude or
  obscuration for this observer. The catalog magnitude is the eclipse's
  greatest magnitude *somewhere on Earth*, so it cannot stand in for a
  local reading. It is used only where there is no ground point at all
  (a catalog row without one; the Encyclopedia plates and the picker
  tiles, which have no observer by construction) — and then **the arc
  is drawn DASHED**, which is the honesty requirement made visible: a
  solid arc is a measured distance, a dashed one is an estimate.

The scale is `constants.ECLIPSE_SOLAR_VISIBILITY_KM` (3,500 km) — the
SAME number the visibility flag and the hover reason already use, so the
owner's own "3,500 km away" IS that constant, the arc empties exactly
where the app already says the eclipse cannot be seen from here, and the
two can never drift apart. `totality_path_reach(covered, distance_km)`
is the one pure function that answers it, module-level so the dial, the
plates and the teeth read the same number.

The TYPE is carried the way every other style here carries it. A
**hybrid** SPLITS its arc — half in the corona's pearl on the outer lane
at the top, half in the ring-of-fire orange on the inner lane at the
bottom — because the eclipse is total along part of its track and
annular along the rest. (A second concentric lane in a different hue was
the first cut and it was not enough: measured 0.098 structure against
`solar_total_totality_path`, well under the 0.20 floor; 0.267 after the
split.) A **partial** wears a thinner arc, because a partial eclipse has
no band of totality anywhere on Earth: there is a nearest point of
greatest eclipse to stand near, but nothing to stand inside, and the
mark must not promise one.

The arc's COLOUR is the light waiting at the centre line — pearl for a
total (the corona is visible only from inside the band), orange for an
annular (the ring of fire), the plain eclipse red for a partial (no
central light to travel toward at all). This is deliberately not
`_state_color`, and the reason is measured: at totality both this arc
and the `magnitude_arc` gauge are a full ring, and at the 64 px
thumbnail the distinctness tooth works at, the 1.18 and 1.30 lanes fall
in the SAME 8×8 block — radius could never separate them (structure
0.194 at width 0.13 and 0.180 at 0.16, both under the floor). Only a
genuine hue change could, and pearl-against-red means something rather
than being a colour picked to pass a test.

## THE TYPE EMBLEM
A badge on the body's lower limb — one ring for annular and two rings
for hybrid, which are the owner's own two. The other two were decided
here, and the grammar is one thing learned once: **how much of the
emblem's centre is open says how much of the Sun survives.**

| Type | Emblem | Why |
|------|--------|-----|
| annular | one ring | the ring of fire, his own word |
| hybrid | two rings | his own word: annular AND total |
| total | a filled disc | the one type where nothing of the Sun is left — the ring's centre closes |
| partial | a bitten disc | never centrally covered, so the emblem is never symmetric — `_bite`'s geometry drawn small |

It is stamped on a night backing disc rather than straight onto the Sun
art, for the same reason the `halo` style's ring is pearl and not red: a
mark that reads against only one background is a mark that silently
disappears on all the others.

The SEAT is measured against the wall. `glow.MARK_REACH_LIMIT` is 1.38
body radii, and the badge must be big enough for the distinctness
tooth's 8×8 block to read it at all — measured at 0.30 body radii the
emblem scored 0.130 structure against `magnitude_arc`, under the 0.20
floor, i.e. the same picture; at 0.45 it clears comfortably. So the seat
is 0.92 and the radius 0.45, which puts the outer edge exactly on the
wall and hangs the badge on the body's limb rather than clear of it. Its
direction is straight down in the mark's own frame — this module's frame
is translated to the body but never rotated, and every other mark in it
is radially symmetric, so no direction was ever claimed.

## THE DIAL SHADOW — and exactly how far it reaches
The one style that takes light away instead of adding it. **Never the
default**, by the owner's explicit order; pinned by
`tests/test_eclipse_style_completion.py::test_dial_shadow_is_never_the_solar_default`.

Its REACH and its DEPTH both rise with the covered fraction (1.05 → 1.36
body radii, alpha 0.25 → 0.80). Both had to move: depth alone is a
global brightness change, and a global brightness change is precisely
what the distinctness tooth is blind to *on purpose* — the owner's own
condemned pair was two pictures that differed by nothing else. An
annular eclipse never goes fully dark, so its ring of fire is written as
a rim at the shadow's own edge, and a hybrid, annular along part of its
track, wears that rim twice.

**What this round could NOT reach, stated plainly.** His brief is "for
the minutes the eclipse lasts, the WHOLE ring loses light". A mark is
painted in the eclipse body's own frame, inside the transparent window
margin the widget reserves, so what ships is the eclipse's darkness
falling on the dial AROUND its body and fading out by the wall. Taking
the light off the ring band, the numerals and the jewels as well needs a
veil composited ABOVE those layers — `render/compositor.py` and
`render/layers/ring.py`, neither of them this round's to touch. A full
version would need: a compositor-level veil that runs after the ring
layers, gated on `ctx.tick.eclipse_body_event` being live AND on the
skin's solar style being `dial_shadow`, using the SAME covered-fraction
depth ramp this mark already computes — which would move into a shared
function here rather than being written a second time, so the body's
shadow and the dial's can never disagree.

## The eclipse "bite", repainted as seen (owner correction 2026-08-11)
A black offset-occulter circle over the already-black eclipse art was
invisible ("ne moze crni isecak na crnoj eklipsi") — the base art
under the bite is now `config.defaults.ECLIPSE_SOLAR_ART`, the owner's
own icon (a black disc in rays), and the bite paints the VISIBLE
remainder BRIGHT rather than painting a dark occulter over dark art.
The old procedural corona-spikes block is gone. (SUPERSEDED the same
week — the bite is now his own two body plates composited, below. The
correction that produced this paragraph still stands and is the reason
the composition draws his own art rather than a procedural silhouette;
only the mechanics changed.)

## THE SIZE RATIO — the occulter is the Sun's own size (owner bug 2026-08-13)
His words, looking at `solar_partial_bite.png`: *"kruznica delimicnog
pomracenja je manja od kruznice sunca"* — and he was right, by a factor
of four.

The 2026-08-11 cut expressed the magnitude as a lunar PHASE and asked
`moon_lit_region` for the matching lit AREA. A phase terminator is a
half-ellipse of semi-axis `r*|cos 2*pi*f|`, so at the catalogue's
typical partial magnitude 0.62 the dark curve was drawn **0.24 r**
wide. Correct area, wrong object: the picture said *a small body
crossed the Sun*, and the bite's curvature was a tight little circle
instead of the Sun's own.

At a solar eclipse the Moon's apparent diameter is within a few percent
of the Sun's — that is the whole reason eclipses look the way they do —
and which side of 1.0 the ratio falls on is what DECIDES the type.
`marker_marks._SOLAR_SIZE_RATIO` states it per state (total 1.05,
hybrid 1.00, annular 0.95, partial 1.00), with the catalogue ranges in
its comment. A partial eclipse is a near-MISS IN ALIGNMENT, not a small
Moon.

So `solar_occulter_geometry(state, radius, covered)` returns the
occulter's radius from that table and its centre DISTANCE from the
magnitude:

```
d = R + r - 2 * R * magnitude
```

— the same formula, and deliberately the same shape, as the lunar
side's `render.moon_face.draw_umbra_sweep`; the `2 *` factor always
multiplies the radius of the body being ECLIPSED (the Moon there, the
Sun here). Magnitude 0 lands exactly on tangency, full coverage on
`d = 0`. The bite then fills the intersection with the silhouette
colour and the remainder bright, both clipped to the Sun's disc, so the
body always reads at its true size. ANNULAR (occulter centred and
genuinely smaller) and TOTAL (corona and silhouette) keep their own
branches untouched. `_ANNULAR_SHRINK` stays a deliberate legibility
exaggeration of the true 0.95 ratio — at a real 0.95 the ring of fire
is two pixels wide on a dial mark.

Tooth: `tests/test_eclipse.py::test_the_partial_occulter_is_the_suns_own_size`,
counter-proved by restoring the phase formula (it reports 0.240).

## THE ECLIPSE REWORK (owner order 2026-08-13)
His words: *"skoro sve slikamo isto ... zato i treba rework"* — and a
full render of the matrix proved him right twice over. Four
combinations rendered ONE byte-identical picture, and a further pair
(`solar_partial_halo` at magnitude 0.62 against `solar_total_halo` at
1.05) was the same picture to the eye while a hash called it different.
Three collapses lived in this module and all three are closed here:

- **`halo` was empty.** The style returned without drawing, so the
  caller's glow was the entire picture and the only thing separating a
  62 % partial from totality was the glow's own alpha. It now draws a
  MAGNITUDE RING outside the body — radius, thickness and alpha all
  rising with the covered fraction — and the body itself is still
  untouched, which is the property the style is chosen for. The ring is
  PEARL, not the type's colour: the first cut drew it in the eclipse
  red, inside a red halo, and it was invisible.
- **`bite` collapsed into `halo` at totality.** It returned early when
  the Sun was fully covered, so the two styles drew the same thing at
  the one moment the style exists for. Totality now paints the CORONA
  and the black silhouette inside it — the only thing a person actually
  sees.
- **`hybrid` was an alias of `total`** (`config.glow.ECLIPSE_TYPE_STATE`),
  which made the two identical in every style at once. A hybrid eclipse
  is total along part of its ground track and annular along the rest,
  so every style here now draws BOTH AT ONCE, one rule learned once:
  the `bite` shows the corona with a ring of fire along half the limb,
  the `magnitude_arc` splits its sweep across two lanes (the annular
  half on an inner ring, the total half on the outer), and the `halo`
  wears two concentric rings instead of one.

## THE BITE IS HIS OWN TWO BODIES (owner art + owner rule, 2026-08-13)
The same evening as the rework, the owner drew two plates —
`shared/assets/instrument/icons/eclipse_body_sun.png` (his rayed yellow
Sun) and `eclipse_body_moon.png` (a black disc with a rim glow) — and
ruled that the `bite` style is nothing but those two composited. He had
named them `eclipse_light`/`eclipse_dark` and renamed them himself,
because colour is the least important thing about them and "dark" reads
as a dark Sun rather than as the Moon.

**ONE composition, all four types.** Draw his Sun, then his Moon over it
at the `occulter_radius` and `centre_distance` `solar_occulter_geometry`
already returns, clipped so the dark disc covers the Sun's YELLOW DISC
and never its rays. In his words: at totality cover the whole disc and
leave only the rays; at every other type the dark disc is smaller or
offset, so part of the yellow disc survives beside the rays. Totality is
simply the case where the composition happens to cover everything —
never a different picture drawn a different way.

The geometry he confirmed, type by type: ANNULAR — the Moon IS centred,
merely too far away to be big enough, so the dark disc shrinks and stays
put. PARTIAL — the Moon does not cross the centre, so a disc of the
Sun's own size is offset and the dark edge is that disc's real circular
arc at its real offset. TOTAL — covered, rays alone. HYBRID — see below.

**Everything is MEASURED off his files, never guessed**
(`marker_marks._SUN_PLATE_*`, `_MOON_PLATE_*`; `tests/test_eclipse_plates.py`
re-measures them and fails if a constant drifts from the art):

| Plate | Measurement | Fraction of half-size |
|-------|-------------|----------------------|
| `eclipse_body_sun.png` (576²) | last fully solid yellow ring — the DISC | 0.623 |
| | outermost ring carrying any ink — the RAY TIPS | 0.889 |
| `eclipse_body_moon.png` (360²) | last ring of pure black — the Moon's limb | 0.925 |
| | rim glow, which runs to the frame edge and is cut there | 1.000 |

Two consequences fall straight out of those numbers. The Sun plate is
scaled so its yellow disc is exactly the body radius, which puts his ray
tips at 0.889/0.623 = **1.427** body radii — past the **1.38** the
transparent window margin reserves (`_MARK_REACH_LIMIT`), so the plate is
CLIPPED at that wall. It costs the outer 3 % of the ray tips on the ~13 %
of the limb still carrying a spoke out there, at under half alpha; no
continuous ink exists to cut, so no hard circular edge can appear.
Shrinking the plate instead would have drawn the Sun 3 % smaller than the
geometry every other mark is built on. And the Moon plate is scaled by its
BLACK BODY, not its frame: the occulter is the solid disc, his rim glow is
extra light beyond it, and the clip to the yellow disc keeps that glow off
the rays.

**The procedural corona is retired.** Totality was shown to the owner with
the argument that his yellow rays are not what a real corona looks like —
pearly white, irregular, long streamers — and he ruled against it: it is
his instrument and this is how it represents an eclipse. `_corona` and
`_ring_of_fire` are both gone; the `bite` style draws no procedural marks
at all any more.

**Only the PNGs are ever read.** The `.svg` twins beside them are dead
twice over: Qt renders SVG Tiny 1.2 and silently drops `mask`, `filter`
and `feColorMatrix`, so his mask-built Moon comes out a flat olive disc —
and by his own account his exporter mangles them anyway, which is why he
redrew both as PNG. Never wire the SVG back in.

## THE GHOST RING — how a hybrid stays its own picture
A hybrid begins annular, turns total across the middle of its path and
ends annular. We draw ONE picture, at greatest eclipse, and at the
epicentre a hybrid IS total — so the honest composition is the total one,
and both would cover the disc completely (ratios 1.00 and 1.05, both
landing on centre distance zero). That is the collapse the rework closed,
about to re-open.

So the hybrid's second half is carried by an added MARK rather than by a
faked geometry: **one thin ring of fire hugging the inside of the dark
limb**, in the annular orange. It says *totality here, the ring of fire
elsewhere along this path* — and it is true, which the half-and-half split
it replaced never was (no eclipse looks like that from anywhere).

Its WIDTH is measured, not chosen: exactly the rim-glow band of his own
Moon plate (1.000 − 0.925), a fifth of the annular ring's own
`1 − _ANNULAR_SHRINK`. Only its strength is a decision, and a narrow one —
the ring is the ONE thing separating hybrid from total, so it has to clear
the distinctness measure's structure floor of 0.20. Measured: **0.171 at
alpha 0.55** (below the floor — the same picture), 0.221 at 0.70,
**0.291 at 0.90**, which is what ships.

The tooth is [`tests/test_eclipse_distinctness.py`](../../tests/___tests.md),
which compares every legal (type, style) pair with a perceptual measure
rather than a hash — deliberately blind to global brightness, because
that blindness is exactly what let the owner's pair pass a hash.

## THE STYLE DOOR (owner ballot 2026-08-13)
`draw_solar_eclipse` no longer trusts `style` directly: it asks
[Eclipse Style Door](eclipse_style.md)'s `resolve_eclipse_style` first,
which answers the SAME shipped style unchanged for `bite`/`magnitude_arc`/
`halo`, or a declared fallback for the ballot's three new solar names
(`totality_path`/`type_emblem`/`dial_shadow`) that have no painter of
their own yet. `_solar_eclipse_body` itself never sees an unpainted
name — it still raises for anything outside its own three, which is
now unreachable except through a bug in the door.

## Connections

### Uses
- [Eclipse Style Door](eclipse_style.md) — `resolve_eclipse_style`,
  asked before `draw_solar_eclipse` dispatches
- [Assets](assets.md) — `shared_cache`, the one process-wide decoded
  image cache the two body plates are rasterized through
- [Config (folder)](../../config/___config.md) — `constants`
  (`ECLIPSE_SOLAR_VISIBILITY_KM`, the style roster), `defaults` (the two
  body plates), `glow` (`MARK_REACH_LIMIT`, the one wall both mark
  modules read), `palette` (the eclipse red, the ring-of-fire orange,
  the corona pearl, the night ground)

### Used by
- [Marker Marks](marker_marks.md) — re-exports `draw_solar_eclipse` and
  `solar_occulter_geometry`, so every existing call site is unchanged
- [Layers (subfolder)](../layers/___layers.md) — `YearMarkerLayer` draws
  the eclipse body's overlay, and is the ONE caller that has an observer
  and therefore passes `distance_km`
- [Eclipse Plates](eclipse_plates.md) — the Encyclopedia's look slider
  renders every (type, style) through the same painter
- [Watch Face (folder)](../../app/___app.md) — `thumbs` builds the
  picker preview from the same function

## Functions
- `draw_solar_eclipse(painter, style, radius, state, magnitude, color, origin=None, distance_km=None)`
  — the one door; asks `resolve_eclipse_style` before it dispatches.
- `totality_path_reach(covered, distance_km) -> (nearness, measured)` —
  pure and module-level, so the dial and the teeth read one number.
- `solar_occulter_geometry(state, radius, covered) -> (occulter radius, centre distance)`
  — the size ratio and the alignment offset, shared by `bite` and by
  `config.defaults`.
