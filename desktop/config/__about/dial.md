# Dial

**Script:** [Dial (script)](../dial.py) · **Flow:** [diagram](../__flow/dial.md)

## Purpose

Dial geometry and window sizing — one of six modules Session 36 (THE
CONFIG SPLIT, [Work Plan Structure](../../../docs/archive/WORKPLAN-STRUCTURE.md))
carved out of `config/defaults.py`, which had grown into a
~3,700-line god-file (root `CLAUDE.md` Rule #20). Everything about how
the drawn DIAL itself is sized and shaped: the window/diameter
presets, the procedural fallback geometry, the ring band (face, tick,
jewels, crown-text arc), hand reach, the subdial/slot seating geometry,
and `OMEGA_HIT_RADIUS_FRACTION` (dial hit-test geometry).

Layer: config — pure, no Qt, no wall clock.

## Contents

- **Window** — `DEFAULT_DIAL_DIAMETER`, `MIN_DIAL_DIAMETER`,
  `MAX_DIAL_DIAMETER`, `SIZE_PRESETS`, the menu size-slider constants,
  the full-text/weekday-name diameter thresholds, `LABEL_OUTLINE_
  WIDTH`, `WATCHDOG_RESHOW_MS`.
- **Procedural FALLBACK geometry** — tick/font sizes, pen widths,
  marker borders (`RING_TICK_WIDTH` … `MARKER_BORDER_WIDTH`); drives
  the painter-drawn ring/labels used whenever a skin ships no ring art
  (user drop-in skins, validate previews) — the bundled DOMY skin uses
  `ring.png` and never touches these.
- **THE SEAT TICK** (owner correction 2026-08-11, slika 1): where a
  minute numeral's own big stroke is masked away, a small tick stands
  in its place — `SEAT_TICK_WIDTH_FRACTION` (hairline-sized, a
  fraction of the interior radius) and `SEAT_TICK_BORDER_RATIO` (the
  white-border stroke's width, as a multiple of the tick width). The
  body colour is `palette.SEAT_TICK_SLATE`; drawn by
  `render.layers.ring.RingLayer._draw_seat_ticks` from the angles
  `render.numeral_bands.inner_number_seat_angles` reports.
- **Moon/Earth rim transit** — `MOON_TRANSIT_OPACITY`, and THE CLEAR
  ORBIT LANE (owner verdict 2026-08-09): `EARTH_MOON_ORBIT_CLEARANCE_
  FRACTION` + `earth_moon_orbit_fraction(ring_size, half_size)`, the
  DRAWN Earth/Moon orbit radius — pulled inside WHICHEVER inner element
  reaches furthest out, `MINUTES_RADIUS_FRACTION` (scaled by
  `interior_scale`) or `POLYGON_FILL_MIN_RADIUS_FRACTION` (below), by
  whichever marker is currently bigger, plus a fixed gap. Read by
  `render.layers.year_marker.YearMarkerLayer` and mirrored by
  `render.compositor.Compositor.element_at`'s hit-test.
- **THE HEXAGRAM/PENTAGON FLOOR** (owner correction round 2026-08-09 —
  a marker was seen sitting across the star/polygon background fill's
  own boundary line): `STAR_RADIUS_FRACTION` (the star/polygon tip,
  moved here from `config.defaults`'s `DEFAULT_SKIN` literal so the
  lane can reason about it) and `POLYGON_FILL_MIN_RADIUS_FRACTION` —
  the smallest apothem (`STAR_RADIUS_FRACTION * cos(half-angle)`)
  across every pointer's own arm half-angle
  (`constants.POINTER_ARM_HALF_ANGLE_DEG`), the deepest the fill's
  outer edge ever dips between two arm tips. THE CLEAR ORBIT LANE
  clears whichever of this floor or the minute band reaches furthest
  out.
- **Ring faces** — `RING_FACE_DIR`, the tint swatch geometry, the ring
  jewel art/shadow/crown-text arc constants (`RING_JEWEL_*`, `RING_CROWN_TEXT_
  *`). **THE PLATE LIBRARY** (owner reorganization 2026-08-07):
  `LETTER_ART_DIR` moved out of `ring/` — the ring, all four crown
  surfaces and (planned) the subdial read the same plates — and
  `LETTER_COMPOSE_INK_GAP_FRACTION`/`LETTER_COMPOSE_VERSION` govern the
  two-digit hour numbers `render.letter_plates` composes from the digit
  masters. **THE LIVE CROWN'S OWN SIZE AND ADVANCE** (owner defects
  2026-08-07): `CROWN_TRACKING_FRACTION` (0.56 of the box) is the extra
  advance each glyph takes beyond its own ink width; with the box itself
  it retires
  `CROWN_NUMERAL_SIZE_FRACTION`, which sized the live crown off the HOUR
  BAND while the static arc beside it used `RING_CROWN_TEXT_SIZE` — two
  size laws on one ring, and the reason the owner's time crown read
  "microscopic". `RING_LIVE_CROWN` gained a `location` key (the
  orientation of a location arc the PRESET owns — The One's ruled bottom
  line) and `RING_LIVE_CROWN_LOCATION_READING` its hover. `RING_JEWEL_SHADOW_MAX_GAP_PX` (THE PIXELATION FIX, 1440p owner
  bug 2026-08-06) is the device-pixel gap `render.layers.ring.
  _shadow_sample_count` keeps between adjacent halo stamps above the
  `RING_JEWEL_SHADOW_SAMPLES` floor.
- **Ring OUTER/INNER composition** (THE COMPOSITIONAL RING MODEL, owner
  decree 2026-08-05) — `RING_OUTER_ART_DIR`/`RING_INNER_ART_DIR`; the
  active outer/inner file names come from `constants.RING_OUTERS`/
  `RING_INNERS` (resolved per-preset by `app.skin_builder._compose_skin`/
  `_resolve_ring_inner`), composed unconditionally by
  `render.layers.ring.RingLayer.paint` — no opt-in, no fallback.
- **Hand sizing** — `HAND_SECOND_REACH_FRACTION`, `HAND_MINUTE_REACH_
  FRACTION` (tip-to-pivot lengths; the hour hand follows each pack's
  own ratio).
- **The subdial/slot cluster** — `SUBDIAL_ROOT_DIR`, `SUBDIAL_SOLO_
  FINISH`, `SLOT_ROUNDEL_*`, `SMALL_SECONDS_TICK_*`, `SMALL_SECONDS_
  HAND_SHADOW_*`, `SUBDIAL_TEXT_SHADOW_OFFSET_FRACTION`, `SLOT_SIZE_
  BY_POINTER` (a per-pointer size dict), `SLOT_SIZE_PINNED`,
  `SLOT_SEAT_OUTWARD`, `WEEKDAY_ROMB_CENTER_OF_TIP`,
  `SUBDIAL_SHADOW_OFFSET_FRACTION`/`SPREAD`.
- **`TIME_TEXT_WIDTH_FRACTION`** and **`UMBRA_CONTRAST_SPANS`** — the
  octa slot text width and the Umbra's own four contrast spans
  (`full`/`half`/`light`/`dark`).
- **`OMEGA_HIT_RADIUS_FRACTION`** — dial HIT geometry, computed from
  `RING_JEWEL_ART_SCALE * 1.5` (the 24h double-click's round hit
  region).
- **`GLOW_RING_RADIUS_FRACTION`** — a straight alias of `RING_JEWEL_
  RADIUS_FRACTION` (the ring band centerline every event glow
  relocates to).

## Connections

### Uses
- [Config (folder)](../___config.md) — `paths`, and `constants.
  POINTER_ARM_HALF_ANGLE_DEG` for THE HEXAGRAM/PENTAGON FLOOR

### Used by
- [Config (folder)](../___config.md) — `defaults.py`'s `DEFAULT_SKIN`
  reads `RING_FACE_DIR` and both `HAND_*_REACH_FRACTION`s from here;
  `defaults.dial_window_margin_fraction` reads the ring/jewel/crown-text
  geometry from here
- [Render (folder)](../../render/___render.md) — every dial-drawing
  layer
- [App (folder)](../../app/___app.md) — Design window, settings dialog

## Design Decisions

- **Not every value under a banner belongs to that banner.** The old
  `defaults.py` had drifted — later, unrelated additions kept landing
  inside an EARLIER section's span because nobody added a fresh
  banner. This module's real boundary is topical (dial geometry),
  never the accident of which comment happened to precede a line.
- **`SETTINGS_NAV_WIDTH_PX`** (the Settings dialog's own nav-column
  width) stayed OUT of this move despite sitting inside the source
  "Ring faces" banner's span — it is Settings-dialog chrome, not ring
  geometry, so it stayed in `defaults.py`.
- **`GLOW_RING_RADIUS_FRACTION` lives here, not in `glow.py`**, because
  its value is a straight alias of a `dial.py` name and the fixed DAG
  forbids one new module importing another — it lives beside what it
  aliases.

## What THE CONSTANTS SPLIT added (2026-08-19)

The **dial identity** block moved in from the deleted
`config/constants.py` and now sits at the TOP of the module, above its
first section: `HOURS_PER_REVOLUTION`, `DIAL_TOP_HOUR`,
`SECONDS_PER_DAY`, `SECONDS_PER_HOUR`, `DIAL_OFFSET_DEG`,
`SOLAR_NOON_SECS`, `SECONDS_PER_DEGREE` and `HAND_HUB_OFFSET_UNITS`.

These numbers ARE the dial convention — 24 hours clockwise, noon at the
top, `DIAL_OFFSET_DEG = 180` ([The Dial](../../../docs/DIAL.md)) — so the
module that owns dial geometry is where a reader looks for them. They
went to the top rather than the bottom because everything below is
measured against them.

They are NOT the sky: the sun depressions, the lunation and the season
anchors went to `config/sky.py` instead.

The whole 38-section map, with the reason for every destination, is
in [Config (folder)](../___config.md#the-constants-split).
