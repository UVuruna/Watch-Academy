# Continents

**Script:** [Continents (script)](../continents.py) · **Flow:** [diagram](../__flow/continents.md)

## Purpose

THE CONTINENTS weekday theme's own region roster, Earth art resolution
and day/night face resolvers — split out of `config/pantheon.py` by
Session 36's deterministic fallback (WORKPLAN-STRUCTURE.md: "if the
line count still shows pantheon over 1,000, move the whole CONTINENTS
family... to config/continents.py as its own cohesive module"). It was
applied; `config/pantheon.py` is still over the god-file threshold
regardless — see [Pantheon](pantheon.md)'s own account.

Layer: config — pure, no Qt, no wall clock.

## Contents

- `_CONTINENTS` — the six continent keys plus the two polar views.
- `EARTH_POLE_LATITUDE` — beyond this `|latitude|` the Earth marker
  wears the POLE art instead of the continent's.
- `EARTH_ART_DIR` — the Earth art root (`assets/celestial/earth/`,
  reused from the dial's own Earth faces — owner exception to
  one-image-one-place, sealed 2026-07-21).
- `CONTINENTS_REGIONS` (body → continent), `CONTINENTS_DUAL_REGION`
  (the Sunday dual's own region, the Arctic), `CONTINENTS_PREVIEW_
  STYLE`, `CONTINENTS_TITLE_IMAGE` (the flat world map).
- `earth_face_art(style, region, phase)` — pure path construction for
  one Earth-marker face.
- `continents_body_art(body, earth_style, is_daylight)` — the live
  weekday body plate, resolving the body's region and the sky's
  current phase.
- `continents_dual_art(earth_style, is_daylight)` — the live SERVANT
  plate (the Arctic, the Antarctic Ruler's antiphase mirror).

## Connections

### Uses
- [Config (folder)](../___config.md) — `paths.assets_dir()`

### Used by
- [Config (folder)](../___config.md) — `pantheon.py` imports this
  module downhill (a fallback carved OUT of pantheon.py, not one of
  the DAG-peer modules, so pantheon depending on it is the split
  working as designed) for `WEEKDAY_THEME_FILES["continents"]`,
  `weekday_art`'s `"../earth/..."` branch and the continents dual-file
  entry; `defaults.py`'s `DEFAULT_SKIN` reads `EARTH_ART_DIR`/
  `_CONTINENTS` downhill too
- [Render (folder)](../../render/___render.md), [App (folder)](../../app/___app.md)
  — the Continents theme's own rendering and Encyclopedia article art

## Functions

- `earth_face_art(style, region, phase="day")`: the `{style}_{region}_
  {phase}` Earth face path — existence is the caller's concern.
- `continents_body_art(body, earth_style, is_daylight)`: one weekday
  body's live plate — looks up the body's region, then the day/night
  face.
- `continents_dual_art(earth_style, is_daylight)`: the Servant plate
  (always the `north_pole`/Arctic region), same day/night law.

## Design Decisions

- **This module is subordinate to pantheon.py, not a peer.** It exists
  purely to shed lines off `pantheon.py`, so — unlike the DAG-peer
  modules Session 36 carved (`dial.py`, `shortcuts.py`, `pantheon.py`
  itself, `calendar_mounts.py`, `encyclopedia_ui.py`, `glow.py`, which
  never import each other) — `pantheon.py` is allowed to import
  `continents.py` downhill.
