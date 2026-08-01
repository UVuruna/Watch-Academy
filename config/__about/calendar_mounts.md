# Calendar Mounts

**Script:** [Calendar Mounts (script)](../calendar_mounts.py) · **Flow:** [diagram](../__flow/calendar_mounts.md)

## Purpose

The Calendar's dozen, its mounts, and the thirteenths' own wedge
geometry — one of six modules Session 36 (THE CONFIG SPLIT,
[Work Plan Structure](../../WORKPLAN-STRUCTURE.md)) carved out of
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
  `art_stems`, optional `follows`), `almanac_seat_order(by_month)` (the
  June-first rotation every month-keyed mount shares), `EMOTIONS_
  DOZEN`, and `CALENDAR_MOUNTS` — the ONE dict of every roster that may
  ride the twelve wedges: `zodiac`, `almanac`, `months` (Slavic),
  `chinese`, `emotions`, `olympians`, `apostles`, `virtues`, `vices`,
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
- [Config (folder)](../___config.md) — `constants` (`CalendarMount`
  builds `CALENDAR_MOUNTS["chinese"]` from `constants.CHINESE_MONTH_
  BRANCH_ANIMALS`, `CALENDAR_MOUNTS["zodiac"]` from `constants.
  ZODIAC_SIGNS`, `["almanac"]` from `constants.GREGORIAN_MONTH_NAMES`),
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
  `vices`, `sins`).

A mount's `centre` names a `constants.THIRTEENTHS` key. Two laws
govern whether that seat actually shows: a CALENDAR-DRIVEN centre
(Ophiuchus/Sol/Modrenik/The Cat) keeps its own narrow appearance
window (`core.blue_moon`); an ALWAYS-CENTRE
(`constants.AXLE_ALWAYS_CENTERS`) is unconditionally present on every
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
  live in [Constants](constants.md) instead.
