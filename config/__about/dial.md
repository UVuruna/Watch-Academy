# Dial

**Script:** [Dial (script)](../dial.py) · **Flow:** [diagram](../__flow/dial.md)

## Purpose

Dial geometry and window sizing — one of six modules Session 36 (THE
CONFIG SPLIT, [Work Plan Structure](../../WORKPLAN-STRUCTURE.md))
carved out of `config/defaults.py`, which had grown into a
~3,700-line god-file (root `CLAUDE.md` Rule #20). Everything about how
the drawn DIAL itself is sized and shaped: the window/diameter
presets, the procedural fallback geometry, the ring band (face, tick,
letters, motto arc), hand reach, the subdial/slot seating geometry,
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
- **Moon/Earth rim transit** — `MOON_TRANSIT_OPACITY`.
- **Ring faces** — `RING_FACE_DIR`, the tint swatch geometry, the ring
  letter art/shadow/motto arc constants (`RING_LETTER_*`, `RING_MOTTO_
  *`).
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
  `RING_LETTER_ART_SCALE * 1.5` (the 24h double-click's round hit
  region).
- **`GLOW_RING_RADIUS_FRACTION`** — a straight alias of `RING_LETTER_
  RADIUS_FRACTION` (the ring band centerline every event glow
  relocates to).

## Connections

### Uses
- [Config (folder)](../___config.md) — `paths` only

### Used by
- [Config (folder)](../___config.md) — `defaults.py`'s `DEFAULT_SKIN`
  reads `RING_FACE_DIR` and both `HAND_*_REACH_FRACTION`s from here;
  `defaults.dial_window_margin_fraction` reads the ring/letter/motto
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
