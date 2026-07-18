# Symbolism Repository

**Script:** [Symbolism Repository (script)](symbolism.py)

## Purpose
Read-only access to `Database/symbolism.json` — the machine-readable
companion of [DOMY Symbolism](../SYMBOLISM.md). The hexa diamond hover
appends the active weekday theme's encyclopedic blurb (two-three
sentences weaving the god/religion/profession with its virtue, vice,
color and mood) below the two zodiac sign lines.

## Connections

### Uses
- [Data (folder)](___data.md) shared JSON loader
- `Database/symbolism.json` ([Database (folder)](../Database/___database.md))

### Used by
- [Compositor](../render/compositor.md) — the hexa arm hover text

## Classes

### SymbolismRepository
- `arm_blurbs(body) -> dict[str, str]`: the blurb texts of one weekday
  body ("day", "greek", "norse", "religion", "color", "virtue_vice",
  "profession"); the center (sun) and the six arms are all addressable
  by body name. Raises KeyError for an unknown body — loudly, per
  Rule #1.
- `archetype_article(article_set, entity) -> dict | None` (owner
  sealed package 2026-07-16): the ARCHETYPE MODE's two-row article —
  `articles.<set>.<entity>` holding `{"rows": [row1, row2]}`. The set
  names live in [Archetypes](../config/archetypes.md)
  (`archetype_trinity_paint` … `archetype_compass_light`), the entity
  keys per figure plus `"center"`. **Session 6 WROTE all seven sets
  (2026-07-18): 48 entities in total** — the two-row layouts carry both
  rows (person+calling, member+hearth-role, temperament+age,
  person+quality, pillar+shadow, estate+object), while the two
  three-side wheels carry more per node. `archetype_compass_light` (the
  Ages) carries a SINGLE row (`rows[0]` — the age text; the compositor
  draws both life-register beings from config). `archetype_seasons_light`
  (the Tetramorph) carries THREE rows per creature (Tetramorph completion
  round 2026-07-18): `rows[0]` the creature, `rows[1]` the evangelist it
  became (Mark/Luke/John/Matthew), `rows[2]` the element its arm holds
  (Fire/Earth/Water/Air, humoral season reading) — one row per three-side
  column; the creature glass and the evangelist rondel come from config,
  the element hue from the wheel. Centers
  exist for all sets EXCEPT the two Compass wheels (the rose is the
  wheel); the Seasons Throne is one shared article under both seasons
  sets. A still-unknown set/entity returns **None** and the hover shows
  the figure's name with the pending line — the documented graceful
  path, never a KeyError. Translated rows overlay under
  `articles/<set>/<entity>/rows/<i>` (the SR bundle is brought to
  coverage in the pre-build Translation session, not here).

The JSON also carries the `articles` set (35 encyclopedic texts, one
per entity per theme) — not yet surfaced in the app; the owner decides
where they display.
