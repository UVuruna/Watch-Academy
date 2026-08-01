# Continents — the Ninth Easter-Egg Law

**Script:** [Continents (script)](../continents.py) · **Flow:** [diagram](../__flow/continents.md)

## Purpose

Decides, for one day, whether the Continents weekday theme's Ninth seat
shows **Zealandia** (the default — the true continent 94% drowned,
unrecognized until 2017) or **Pangea** (the easter-egg — the deep-time
supercontinent that was once all land and, by the supercontinent cycle,
will be again). Owner-sealed matrix 2026-07-21; WIDENED to every
principal moon phase, owner verdict 2026-07-29.

Pangea replaces Zealandia only while the sky is doing something on the
traveled day — one boolean over three triggers: an **eclipse** near the
moment, a **season turning point** (solstice/equinox day), or a
**principal moon-phase day** (New, First Quarter, Full, or Third
Quarter — widened 2026-07-29 from Full/New alone).

Pure module — no Qt, no wall clock, purity-gated by
[Purity Test (script)](../../tests/test_purity.py). Astronomy is never
recomputed here: both callers hand in facts they already hold.

## Connections

### Uses
- [Config (folder)](../../config/___config.md) — `MOON_PHASE_FRACTIONS`
  (the New/Full/Quarter fractions are read, never hardcoded)

### Used by
- [Layers](../../render/layers/___layers.md) — `theme_ninth(theme, active_alt=...)`
  and `CenterBodyLayer` feed the dial flags (`DayContext.season_events`/
  `moon_events`, `TickState.eclipse_event`) through
  `ninth_is_pangea_from_events`
- [Compositor](../../render/__about/compositor.md) — the center hover reads the
  same law for the same swap
- [Encyclopedia (subfolder)](../../app/encyclopedia/___encyclopedia.md) —
  the Continents topic's Ninth page follows `ninth_is_pangea_from_repos`
  against the traveled date and the bundled Seasons/Moon repositories

## Functions

- `pangea_over_zealandia(has_eclipse, is_turning_point, is_principal_phase)`
  — THE LAW: the single OR of the three triggers.
- `date_has_turning_point(on_date, season_events)` /
  `date_has_principal_phase(on_date, moon_events)` — the DIAL forms,
  reading the day's already-built anchor lists (UTC dates; moon side
  matches on the principal-phase NAME).
- `turning_point_on(on_date, seasons_repo)` /
  `principal_phase_on(on_date, moon_repo)` — the ENCYCLOPEDIA forms,
  deriving the two calendar triggers from the bundled repositories (moon
  side matches on the fraction); a date outside coverage answers False.
- `ninth_is_pangea_from_events(on_date, season_events, moon_events, has_eclipse)`
  — the dial wrapper.
- `ninth_is_pangea_from_repos(on_date, seasons_repo, moon_repo, has_eclipse=False)`
  — the Encyclopedia wrapper (`has_eclipse` defaults False — the eclipse
  catalog is the optional Deep Time pack).

## Design Decisions

- **One law, two input shapes.** The dial holds pre-built event lists on
  its `DayContext`; the Encyclopedia holds only a date and the
  repositories. Each side derives the two calendar flags in whatever
  form is cheapest for it, and both funnel through the one
  `pangea_over_zealandia` boolean (root Rule #5).
- **The eclipse trigger is real only on the dial.** The Encyclopedia's
  Ninth page keys off the two always-bundled triggers; the dial, which
  already carries a live `eclipse_event`, passes the true flag.
