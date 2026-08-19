# Calendar Mounts

**Script:** [Calendar Mounts (script)](../calendar_mounts.py) · **Flow:** [diagram](../__flow/calendar_mounts.md)

## Purpose

The Calendar's dozen, its mounts, and the thirteenths' own wedge
geometry — one of six modules Session 36 (THE CONFIG SPLIT,
[Work Plan Structure](../../../docs/archive/WORKPLAN-STRUCTURE.md)) carved out of
`config/defaults.py`.

Layer: config — pure, no Qt, no wall clock.

## Contents

- **Calendar pointer geometry** — `CALENDAR_WEDGE_RADIUS_FRACTION`, the
  day-arrow triangle constants (`CALENDAR_ARROW_TIP_FRACTION`/`_LENGTH_
  FRACTION`/`_HALF_DEG`). The Calendar's own lit-wedge opacity died
  with the feature (owner decree 2026-07-29) — it now rides the
  standard Aura day/twilight opacities like every other pointer.
- **The Slavic Months 12-set** — `SLAVIC_MONTHS` (Croatian proper noun,
  English gloss, ASCII plate stem, Gregorian month), one of several
  registered 12-sets.
- **THE CALENDAR MOUNT REGISTRY** — `CalendarMount` (a `NamedTuple`:
  `title`, `system` "A"/"B", `members`, `art_dir`, `centre`, optional
  `art_stems`, optional `follows`, optional `paint` — the roster's DARK DEPICTION, a whole mount of its own on the same twelve seats), `almanac_seat_order(by_month)` (the
  June-first rotation every month-keyed mount shares), `EMOTIONS_
  DOZEN`, and `CALENDAR_MOUNTS` — the ONE dict of every roster that may
  ride the twelve wedges: `zodiac`, `almanac`, `months` (Slavic),
  `chinese`, `emotions`, `olympians`, `apostles`, `virtues` (whose `paint` face is the Vices — one theme in two depictions, owner ruling 2026-08-05),
  `sins`. `CALENDAR_MOUNT_MODES` derives the legal `Settings.
  calendar_mount` values from it.
- **Mount rendering geometry** — `CALENDAR_MOUNT_RADIUS_FRACTION`
  (0.65, the DESIGN ZODIAC law's 60–70% band), `CALENDAR_MOUNT_MARK_
  SCALE`, `CALENDAR_MOUNT_ALPHA`/`_LIT_DELTA` (the current member's
  emphasis), `CALENDAR_MOUNT_DIMMED_ALPHA` (THE CAT'S DIMMING LAW).
- `CALENDAR_MOUNT_SEATS_PER_WEDGE` — `{12: 1, 24: 2}`, how many members
  a wedge seats depending on the roster's own size.

## Connections

### Uses
- [Config (folder)](../___config.md) — `zodiac` and `pointer_geometry` (`CalendarMount`
  builds `CALENDAR_MOUNTS["chinese"]` from `zodiac.CHINESE_MONTH_
  BRANCH_ANIMALS`, `CALENDAR_MOUNTS["zodiac"]` from `zodiac.
  ZODIAC_SIGNS`, `["almanac"]` from `pointer_geometry.GREGORIAN_MONTH_NAMES`),
  `paths`

### Used by
- [Render (folder)](../../render/___render.md) — `layers._draw_
  calendar_mount`/`calendar_mount_entries`/`calendar_mount_angle`
- [App (folder)](../../app/___app.md) — the Pointer Theme window's
  Calendar mount tab, `settings_store` validation

## The two dozen systems

A mount's `system` decides its GEOMETRY (`CANON.md` §The Two Dozen
Systems and the Four Dozens):

- **System "A"** — the ZODIAC-aligned wheel: wedge BOUNDARIES sit ON
  the cardinals, so the twelve fall into six PAIRS. Carries dozens that
  come in pairs (`zodiac`, `olympians`, `apostles`).
- **System "B"** — the MONTH-aligned wheel: the same twelve watches
  shifted 15° so their CENTERS sit on the cardinals — one CROWN (12h),
  one ROOT (24h), six opposition axes. Carries dozens defined by
  OPPOSITES (`almanac`, `months`, `chinese`, `emotions`, `virtues`,
  `sins`) — the Vices ride the Virtue Wheel as its `paint` face.

A mount's `centre` names a `zodiac.THIRTEENTHS` key. Two laws
govern whether that seat actually shows: a CALENDAR-DRIVEN centre
(Ophiuchus/Sol/Modrenik/The Cat) keeps its own narrow appearance
window (`core.blue_moon`); an ALWAYS-CENTRE
(`zodiac.AXLE_ALWAYS_CENTERS`) is unconditionally present on every
date instead.

## Design Decisions

- **The registry stays one dict, `CALENDAR_MOUNTS`.** Every legal
  `Settings.calendar_mount` value derives from its keys, so adding a
  roster never needs a second edit.
- **The seat law is one formula, not per-seat data.** A 12-set seats
  one member per wedge at that wedge's centre; a 24-set seats two per
  wedge at ±a quarter wedge — both fall out of
  `render.layers.calendar_mount_angle`, nothing is tabulated per seat.
- **What did NOT move here.** The split map named `THIRTEENTHS` and
  `CHINESE_MONTH_BRANCH_ANIMALS` as expected carves from "Weekday body
  themes" — as verified against the current code, neither name lives
  in `config/defaults.py`: both, along with `AXLE_ALWAYS_CENTERS`,
  `OPHIUCHUS_WINDOW`, `SOL_WINDOW` and `MODRENIK_WINDOW_HALF_DAYS`,
  live in [Pointer Geometry](pointer_geometry.md) instead.

## What THE CONSTANTS SPLIT added (2026-08-19)

**CALENDAR & ROSE STAR GEOMETRY** and **ROSE FIGURE SETS & DAYLIGHT
SWITCH** moved in from the deleted `config/constants.py`:
`CALENDAR_STAR_ARMS`, `ROSE_STAR_OFFSETS`, `AURA_WEDGE_ANCHOR_DEFAULT`,
`ROSE_AURA_WEDGE_ANCHOR`, `ROSE_STAR_SETS`, `ROSE_ARM_SYSTEMS` and
`DAYLIGHT_SWITCH_POINTERS`.

They belong with the wedge geometry this module already owns: the rose's
star offsets and aura anchors are the same kind of statement as the
twelve wedges' own, and every reader of one reads the other.

The whole 38-section map, with the reason for every destination, is
in [Config (folder)](../___config.md#the-constants-split).
