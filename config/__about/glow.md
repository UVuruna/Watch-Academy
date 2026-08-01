# Glow

**Script:** [Glow (script)](../glow.py) · **Flow:** [diagram](../__flow/glow.md)

## Purpose

Event glow windows and the eclipse rendering knobs — one of six
modules Session 36 (THE CONFIG SPLIT, [Work Plan Structure](../../WORKPLAN-STRUCTURE.md))
carved out of `config/defaults.py`.

Layer: config — pure, no Qt, no wall clock.

## Contents

- **Season/moon event glow rendering** — `GLOW_CORE_ALPHA`,
  `GLOW_MID_ALPHA`, `GLOW_MID_STOP`, `GLOW_RADIUS_SCALE`.
  (`GLOW_RING_RADIUS_FRACTION`, the same family, lives in
  [Dial](dial.md) instead — it is a straight alias of a `dial.py` name,
  and one new module may never import another.)
- **The whole `ECLIPSE_*` family**:
  - `ECLIPSE_INVISIBLE_STRENGTH_FACTOR` — the desaturated/half-strength
    glow for an eclipse the observer cannot actually see.
  - Lunar fringe geometry — `ECLIPSE_LUNAR_FRINGE_STOP`/`_HALF_WIDTH`/
    `_ALPHA`.
  - Magnitude → glow-strength linear mapping —
    `ECLIPSE_MAGNITUDE_MIN`/`_MAX`, `ECLIPSE_GLOW_STRENGTH_MIN`/`_MAX`
    (kept alive for exactly ONE state, `solar_partial`).
  - `ECLIPSE_TYPE_STATE` — (kind, catalog type) → fixed render STATE;
    `ECLIPSE_STATE_FALLBACK` for an unrecognised type.
  - `ECLIPSE_STATE_MOON_BRIGHTNESS`, `ECLIPSE_STATE_GLOW_STRENGTH`,
    `ECLIPSE_STATE_FRINGE` — the fixed per-state visual triad (every
    state but `solar_partial`, which keeps the magnitude-linear
    mapping instead).
  - `ECLIPSE_ART_DIR`, `ECLIPSE_TYPE_EMBLEM` — the category emblem per
    (kind, type), used by both the Encyclopedia chapter page and the
    dial's own eclipse-window hover badge.
  - `ECLIPSE_TYPE_ICON_PX` — the small hover-line inline badge size.

## What did NOT move here

Three eclipse-icon names stayed in [Defaults](defaults.md) instead:
`ECLIPSE_SOLAR_ART`, `ECLIPSE_LUNAR_TYPE_ICON` (+ its reader
`eclipse_lunar_type_icon()`) and `ECLIPSE_SOLAR_TYPE_ICON_SOURCE`.
Each needs a name from a DIFFERENT new module —
`ECLIPSE_SOLAR_ART = pantheon.weekday_art(...)`, the two icon tables
key off `ICON_DIR` (the shared UI-icon-chrome root, itself used by
many non-eclipse icon categories) — and the fixed import DAG forbids
one new module importing another. Rather than duplicate `weekday_art`
or `ICON_DIR`, the three names stay in `defaults.py`, which alone may
import both `pantheon.py` and hold `ICON_DIR` itself.

## Connections

### Uses
- [Config (folder)](../___config.md) — `paths`

### Used by
- [Render (folder)](../../render/___render.md) — the event-glow layer,
  the eclipse state machine, `asset_variants.eclipse_solar_type_icon`
- [App (folder)](../../app/___app.md) — the eclipse hover line

## Design Decisions

- **A cross-referencing name follows its dependency, never the other
  way.** Every split-off value that turned out to need another new
  module's data moved to sit beside that data (or, when it needed TWO
  new modules at once, stayed in the remnant `defaults.py`, which
  alone may import every new module downhill).
