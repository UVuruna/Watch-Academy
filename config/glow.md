# Glow

**Script:** [Glow (script)](glow.py)

## Purpose

Event glow windows and the eclipse rendering knobs — one of six
modules Session 36 (THE CONFIG SPLIT,
[Work Plan Structure](../WORKPLAN-STRUCTURE.md)) carved out of
`config/defaults.py`.

Layer: config — pure, no Qt, no wall clock.

## What moved here

- **Season/moon event glow rendering** — `GLOW_CORE_ALPHA`, `GLOW_MID_
  ALPHA`, `GLOW_MID_STOP`, `GLOW_RADIUS_SCALE`. (`GLOW_RING_RADIUS_
  FRACTION`, textually the first of this family, moved to `dial.py`
  instead — see that module's Design Decisions.)
- **The whole `ECLIPSE_*` family** — the invisible-strength factor, the
  lunar fringe geometry, the magnitude→glow-strength scale, the type
  state machine (`ECLIPSE_TYPE_STATE`, `ECLIPSE_STATE_*`), the art
  directory and the category emblem table, `ECLIPSE_TYPE_ICON_PX`.

## What did NOT move here

Three eclipse-icon names stayed in `defaults.py` instead:
`ECLIPSE_SOLAR_ART`, `ECLIPSE_LUNAR_TYPE_ICON` (+ its reader
`eclipse_lunar_type_icon()`) and `ECLIPSE_SOLAR_TYPE_ICON_SOURCE`.
Each needs a name from a DIFFERENT new module —
`ECLIPSE_SOLAR_ART = pantheon.weekday_art(...)`, the two icon tables
key off `ICON_DIR` (the shared UI-icon-chrome root, itself used by
many non-eclipse icon categories) — and the fixed import DAG forbids
one new module importing another. Rather than duplicate `weekday_art`
or `ICON_DIR` (Rule #5), the three names stay in the remnant, which
may import both `pantheon.py` and hold `ICON_DIR` itself.

## Connections

### Uses
- [Config (folder)](___config.md) — `paths`

### Used by
- [Render (folder)](../render/___render.md) — the event-glow layer,
  the eclipse state machine, `asset_variants.eclipse_solar_type_icon`
- [App (folder)](../app/___app.md) — the eclipse hover line

## Design Decisions

- **A cross-referencing name follows its dependency, never the other
  way.** Every split-off value that turned out to need another new
  module's data moved to sit beside that data (or, when it needed TWO
  new modules at once, stayed in the remnant, which alone may import
  every new module downhill) — see `config/pantheon.md` and
  `config/___config.md`'s own account of every such move.
