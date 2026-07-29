# Continents

**Script:** [Continents (script)](continents.py)

## Purpose

THE CONTINENTS weekday theme's own region roster, Earth art resolution
and day/night face resolvers — split out of `config/pantheon.py` by
Session 36's ONE deterministic fallback (WORKPLAN-STRUCTURE.md: "if
`wc -l` still shows pantheon over 1,000, move the whole CONTINENTS
family... to config/continents.py as its own cohesive module. No other
improvisation"). It was applied; `config/pantheon.py` is still over the
threshold regardless — see [Pantheon](pantheon.md)'s own account.

Layer: config — pure, no Qt, no wall clock.

## What lives here

- `_CONTINENTS` — the six continent keys.
- `EARTH_POLE_LATITUDE`, `EARTH_ART_DIR` — the Earth art root
  (`assets/earth/`, reused from the dial's own Earth faces — owner
  exception to one-image-one-place, 2026-07-21).
- `CONTINENTS_REGIONS` (body → continent), `CONTINENTS_DUAL_REGION`
  (the Sunday dual's own region), `CONTINENTS_PREVIEW_STYLE`,
  `CONTINENTS_TITLE_IMAGE` (the world map).
- `earth_face_art()`, `continents_body_art()`, `continents_dual_art()`
  — the live `earth_style` × day/night resolvers.

## Connections

### Uses
- [Config (folder)](___config.md) — `paths`

### Used by
- [Config (folder)](___config.md) — `pantheon.py` imports this module
  downhill (a fallback carved OUT of pantheon.py, not one of the six
  DAG-peer modules, so pantheon depending on it is the split working
  as designed) for `WEEKDAY_THEME_FILES["continents"]`, `weekday_art`'s
  `"../earth/..."` branch and the continents dual-file entry;
  `defaults.py`'s `DEFAULT_SKIN` reads `EARTH_ART_DIR`/`_CONTINENTS`
  downhill too
- [Render (folder)](../render/___render.md), [App (folder)](../app/___app.md)
  — the Continents theme's own rendering and Encyclopedia article art

## Design Decisions

- **This module is subordinate to pantheon.py, not a peer.** It exists
  purely to shed lines off `pantheon.py`, so — unlike the six modules
  the split map fixes as a DAG with no cross-imports — `pantheon.py`
  is allowed to import `continents.py` downhill.
