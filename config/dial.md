# Dial

**Script:** [Dial (script)](dial.py)

## Purpose

Dial geometry and window sizing — one of six modules Session 36 (THE
CONFIG SPLIT, [Work Plan Structure](../WORKPLAN-STRUCTURE.md)) carved
out of `config/defaults.py`, which had grown into a ~3,700-line
god-file (root `CLAUDE.md` Rule #20). Everything about how the drawn
DIAL itself is sized and shaped: the window/diameter presets, the
procedural fallback geometry, the ring band (face, tick, letters,
motto arc), hand reach, the subdial/slot seating geometry, and
`OMEGA_HIT_RADIUS_FRACTION` (dial HIT geometry, carved out of the old
"Session 27" section per the split map's named exception).

Layer: config — pure, no Qt, no wall clock.

## What moved here

- **Window** — `DEFAULT_DIAL_DIAMETER`, `MIN_DIAL_DIAMETER`,
  `MAX_DIAL_DIAMETER`, `SIZE_PRESETS`, the menu size-slider constants,
  the full-text/weekday-name diameter thresholds, `LABEL_OUTLINE_
  WIDTH`, `WATCHDOG_RESHOW_MS`.
- **Procedural FALLBACK geometry** — tick/font sizes, pen widths,
  marker borders (`RING_TICK_WIDTH` … `MARKER_BORDER_WIDTH`).
- **Moon/Earth rim transit** — `MOON_TRANSIT_OPACITY`.
- **Ring faces** — `RING_FACE_DIR`, the tint swatch geometry, the ring
  letter art/shadow/motto arc constants (`RING_LETTER_*`, `RING_MOTTO_
  *`). `SETTINGS_NAV_WIDTH_PX` (the Settings dialog's own nav-column
  width) stayed OUT of this move — it sat physically inside the "Ring
  faces" banner's span but is Settings-dialog chrome, not ring
  geometry, so it stayed in `defaults.py`.
- **Hand sizing** — `HAND_SECOND_REACH_FRACTION`, `HAND_MINUTE_REACH_
  FRACTION`.
- **The subdial/slot cluster** — `SUBDIAL_ROOT_DIR`, `SUBDIAL_SOLO_
  FINISH`, `SLOT_ROUNDEL_*`, `SMALL_SECONDS_TICK_*`, `SMALL_SECONDS_
  HAND_SHADOW_*`, `SUBDIAL_TEXT_SHADOW_OFFSET_FRACTION`, `SLOT_SIZE_
  BY_POINTER`, `SLOT_SIZE_PINNED`, `SLOT_SEAT_OUTWARD`, `WEEKDAY_ROMB_
  CENTER_OF_TIP`, `SUBDIAL_SHADOW_OFFSET_FRACTION`/`SPREAD` — these
  physically sat inside the old "Session 27" banner (an unrelated
  later addition drifted into that section's span) but are dial
  rendering geometry, this module's own charter, so they moved here
  rather than following that banner's other content to
  `encyclopedia_ui.py`.
- **`TIME_TEXT_WIDTH_FRACTION`** and **`UMBRA_CONTRAST_SPANS`** — both
  drifted into unrelated banner spans ("THE CALENDAR MOUNT REGISTRY"
  and the Session-27 tail respectively) but are dial-rendering values
  (octa slot text width, the Umbra's own contrast spans).
- **`OMEGA_HIT_RADIUS_FRACTION`** — the split map's one named
  exception: dial HIT geometry computed from `RING_LETTER_ART_SCALE`,
  carved out of the old "Session 27 REWORK" section.
- **`GLOW_RING_RADIUS_FRACTION`** — DAG-forced: its value is
  `= RING_LETTER_RADIUS_FRACTION`, a straight alias of a `dial.py`
  name. `glow.py` cannot define an alias of a name it cannot import
  (the fixed DAG forbids one new module importing another), so the
  spec's own resolution rule ("move the referenced value into the
  same module") applies — it lives beside what it aliases.

## Connections

### Uses
- [Config (folder)](___config.md) — `paths` only

### Used by
- [Config (folder)](___config.md) — `defaults.py`'s `DEFAULT_SKIN`
  reads `RING_FACE_DIR` and both `HAND_*_REACH_FRACTION`s from here;
  `defaults.dial_window_margin_fraction` (a remnant coordinator, see
  its own docstring) reads the ring/letter/motto geometry from here
- [Render (folder)](../render/___render.md) — every dial-drawing layer
- [App (folder)](../app/___app.md) — Design window, settings dialog

## Design Decisions

- **Not every value under a banner belongs to that banner.** The old
  `defaults.py` had drifted — later, unrelated additions kept landing
  inside an EARLIER section's span because nobody added a fresh
  banner. This module's real boundary is topical (dial geometry),
  never the accident of which comment happened to precede a line.
