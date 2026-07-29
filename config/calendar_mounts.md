# Calendar Mounts

**Script:** [Calendar Mounts (script)](calendar_mounts.py)

## Purpose

The Calendar's dozen, its mounts, and the thirteenths' own wedge
geometry — one of six modules Session 36 (THE CONFIG SPLIT,
[Work Plan Structure](../WORKPLAN-STRUCTURE.md)) carved out of
`config/defaults.py`.

Layer: config — pure, no Qt, no wall clock.

## What moved here

- **Calendar pointer** — the wedge/arrow geometry (`CALENDAR_WEDGE_
  RADIUS_FRACTION`, `CALENDAR_ARROW_*`).
- **Calendar-pointer 12-sets: the Slavic Months** — `SLAVIC_MONTHS`.
- **THE CALENDAR MOUNT REGISTRY** — `CalendarMount`, `almanac_seat_
  order()`, `EMOTIONS_DOZEN`, `CALENDAR_MOUNTS` (the one registry of
  every roster that may ride the twelve wedges), `CALENDAR_MOUNT_
  MODES` (derived from it), and its radius/mark/alpha geometry
  (`CALENDAR_MOUNT_RADIUS_FRACTION` … `CALENDAR_MOUNT_DIMMED_ALPHA`).

## What did NOT move here

The split map named `THIRTEENTHS` and `CHINESE_MONTH_BRANCH_ANIMALS`
as expected carves from "Weekday body themes" — as of this session
neither name lives in `config/defaults.py` at all: both, along with
`AXLE_ALWAYS_CENTERS`, `OPHIUCHUS_WINDOW`, `SOL_WINDOW` and
`MODRENIK_WINDOW_HALF_DAYS`, already live in `config/constants.py`
(untouched by this session's map). This carve is therefore a no-op
against the file's current state — the map's own preamble warned that
"the waves have moved every line number... headers and NAMES are the
contract", and this is exactly such a case: the named things had
already moved before Session 36 started.

## Connections

### Uses
- [Config (folder)](___config.md) — `constants` (`CalendarMount`
  builds `CALENDAR_MOUNTS["chinese"]` from `constants.CHINESE_MONTH_
  BRANCH_ANIMALS`), `paths`

### Used by
- [Render (folder)](../render/___render.md) — `layers._draw_calendar_
  mount`/`calendar_mount_entries`/`calendar_mount_angle`
- [App (folder)](../app/___app.md) — the Pointer Theme window's
  Calendar mount tab, `settings_store` validation

## Design Decisions

- **The registry stays one dict, `CALENDAR_MOUNTS`**, exactly as
  before — every legal `Settings.calendar_mount` value derives from
  its keys, so adding a roster never needs a second edit.
