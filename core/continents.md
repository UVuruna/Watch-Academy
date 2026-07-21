# Continents — the Ninth Easter-Egg Law

**Script:** [Continents (script)](continents.py)

## Purpose

Decides, for one day, whether the Continents weekday theme's Ninth seat
shows **Zealandia** (the default — the true continent 94% drowned,
unrecognized until 2017) or **Pangea** (the easter-egg — the deep-time
supercontinent that was once all land and, by the supercontinent cycle,
will be again). Owner-sealed matrix, 2026-07-21.

Pangea replaces Zealandia only while the sky is DOING something on the
traveled day. The rule is one boolean over three triggers:

- an **eclipse** near the traveled moment,
- a **season turning point** (a solstice/equinox day), or
- a **full/new moon day** (~1/11 of the year).

Pure module — no Qt, no wall clock (purity-gated by
[Purity test](../tests/test_purity.py)). Astronomy is never recomputed
here: both callers hand in facts they already hold.

## Connections

### Uses
- [Constants (script)](../config/constants.py) — `MOON_PHASE_FRACTIONS`
  (the New/Full syzygy fractions are read, never hardcoded).

### Used by
- [Layers](../render/layers.md) — `theme_ninth(theme, pangea=...)` and
  the `CenterBodyLayer` feed the DIAL flags (`DayContext.season_events`/
  `moon_events`, `TickState.eclipse_event`) through
  `ninth_is_pangea_from_events`.
- [Compositor](../render/compositor.md) — the center hover reads the
  same law for the same swap.
- [Encyclopedia](../app/encyclopedia.md) — the Continents topic's Ninth
  page follows `ninth_is_pangea_from_repos` against the traveled date
  and the bundled Seasons/Moon repositories.

## Functions

- `pangea_over_zealandia(has_eclipse, is_turning_point, is_full_or_new_moon)`
  — THE LAW: the single OR of the three triggers. Everything else feeds
  it.
- `date_has_turning_point(on_date, season_events)` /
  `date_has_full_or_new_moon(on_date, moon_events)` — the DIAL forms,
  reading the day's already-built anchor lists (UTC dates; moon side
  matches on the principal phase NAME).
- `turning_point_on(on_date, seasons_repo)` /
  `full_or_new_moon_on(on_date, moon_repo)` — the ENCYCLOPEDIA forms,
  deriving the two calendar triggers from the bundled repositories (moon
  side matches on the fraction 0.0/0.5); a date outside coverage answers
  False, graceful.
- `ninth_is_pangea_from_events(...)` — the DIAL wrapper (live eclipse
  flag threaded in).
- `ninth_is_pangea_from_repos(...)` — the ENCYCLOPEDIA wrapper
  (`has_eclipse` defaults False — the eclipse catalog is the optional
  Deep Time pack).

## Design Decisions

- **One law, two input shapes.** The dial holds pre-built event lists on
  its `DayContext`; the Encyclopedia holds only a date and the
  repositories. Rather than rebuild a full day context in the gallery
  (heavy, and it would recompute astronomy), each side derives the two
  calendar flags in whatever form is cheapest for it and both funnel
  through the one `pangea_over_zealandia` boolean (Rule #5).
- **The eclipse trigger is real only on the dial.** The eclipse catalog
  ships with the optional Deep Time pack, so the Encyclopedia's Ninth
  page keys off the two always-bundled triggers; the dial, which already
  carries a live `eclipse_event`, passes the true flag.
