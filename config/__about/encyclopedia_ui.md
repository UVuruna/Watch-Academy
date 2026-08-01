# Encyclopedia UI

**Script:** [Encyclopedia UI (script)](../encyclopedia_ui.py) · **Flow:** [diagram](../__flow/encyclopedia_ui.md)

## Purpose

The reading surfaces — Encyclopedia, legend and the computed diagrams —
one of six modules Session 36 (THE CONFIG SPLIT,
[Work Plan Structure](../../WORKPLAN-STRUCTURE.md)) carved out of
`config/defaults.py`.

Layer: config — pure, no Qt, no wall clock.

## Contents

- **Article hover geometry** — `ARTICLE_IMAGE_WIDTH_PX`, `ARTICLE_TEXT_
  WIDTH_PX`, `ARTICLE_COLUMN_WIDTH_PX`, `ARTICLE_THREE_COLUMN_WIDTH_PX`
  (the three-side layout, total width pinned to the two-column width),
  `ARTICLE_THREE_IMAGE_PX`, the subhead gap pair, `ASTRO_*`, `PERIOD_
  EARTH_IMAGE_PX`, `ARTICLE_TITLE_PX`.
- **Legend term highlighting** — `LEGEND_TERM_PATTERNS`: a `{category:
  regex-fragment tuple}` dict (`virtue`/`vice`/`mood`/`weekday`), each
  entry pairing an English word with its Serbian case-ending variants,
  matched case-insensitively at render time so canon terms pop bold in
  article prose (THE LEGEND BOLD LAW, owner 2026-07-26 — bold only, on
  the web's spine alone).
- **Legend popup sizing** — `LEGEND_MAX_WIDTH_FRACTION`/`_HEIGHT_
  FRACTION`, `LEGEND_CURSOR_OFFSET_PX`, `LEGEND_PADDING_PX`,
  `LEGEND_TEASER_SENTENCES` (THE HOVER TEASER LAW — a hover speaks only
  its thesis, N sentences, then closes with a Learn More footer).
- **Encyclopedia text/card sizing** — `ENCYCLOPEDIA_TEXT_WIDTH_
  FRACTION`, the responsive font-growth pair, `ENCYCLOPEDIA_TOPIC_
  ICON_MIN/MAX_PX`, the DECODE CEILING pair (card vs reader — the
  background warm pre-builds disk-cached downscales at these widths so
  entering the Encyclopedia never blocks), `ENCYCLOPEDIA_GALLERY_MAX_
  COLUMNS`, `ENCYCLOPEDIA_GALLERY_CARD_PADDING_PX`.
- **THE COMPUTED DIAGRAMS** — `CUBE_DIAGRAM_*` (the Cube's 23
  generation-exempt compositions, drawn live from `config.cube`'s
  coordinates), `CUBE_MODEL_GLASS_OPACITY` (the 3D Preview bridge's
  glass weight, transcribed rather than imported — the exporter stays
  gadget-import-free), `CANON_DIAGRAM_*` (the journeys and tables).
- **THE SESSION 27 REWORK** — the three-level Encyclopedia's own sizing
  (`ENCYCLOPEDIA_MIN_WIDTH_PX`/`_HEIGHT_PX` = 1280×720, `ENCYCLOPEDIA_
  HOME_COLUMNS` = 3, the card geometry, `ENCYCLOPEDIA_WHOLE_ART_DIR`/
  `_MOSAIC_*` — the Home tile's own 2×2 computed mosaic, root Rule #19:
  no artwork needed for the nine wholes), the shared UI chrome
  (`UI_BUTTON_*`, `THEME_RADIUS_*`), `READER_IMAGE_MAX_HEIGHT_
  FRACTION`, the hidden-mode Greetings arc geometry (`GREETINGS_*`).
- **Hover article warm sweep** — `HOVER_WARM_ANGLE_STEPS` (180) ×
  `HOVER_WARM_RADIAL_STEPS` (40), `HOVER_WARM_RING_PAUSE_S` — the
  polar probe grid `compositor.warm_hover_articles` walks to pre-build
  every hover article in the background.
- **THE INSTRUMENT'S OWN DIAGRAMS** — `INSTRUMENT_DIAGRAM_*` (the
  "how this clock works" pages, computed by
  `render/instrument_diagrams.py`), `INSTRUMENT_TWILIGHT_BANDS`
  (civil/nautical/astronomical depression bands, civil sourced from
  `constants.CIVIL_DEPRESSION`).

## Connections

### Uses
- [Config (folder)](../___config.md) — `constants`, `paths`

### Used by
- [App (folder)](../../app/___app.md) — the Encyclopedia package
  (legend popup, cards, reader, tree, home, dialog), `ui_style.py`,
  `theme.py`
- [Render (folder)](../../render/___render.md) — `canon_diagrams.py`,
  `cube_diagrams.py`, `instrument_diagrams.py`, `compositor.py`'s
  Greetings arc

## Design Decisions

- **"THE SESSION 27 REWORK" is named after WHEN it was written, not a
  stable topic** — everything a LATER session tacked on after it (with
  no fresh banner of its own) inherited its span without belonging to
  its subject. This module reads the drift honestly rather than
  dumping Report-chart, Observatory-chart, Guide-dialog and Time-Travel
  values into an "Encyclopedia" module they have nothing to do with —
  those stayed in [Defaults](defaults.md).
- **`ARTICLE_*`/`ASTRO_*`/`SCALE_ART_DIR`** physically sat inside "THE
  CALENDAR MOUNT REGISTRY"'s span in the pre-split file (article hover
  layout has nothing to do with calendar mounts) and moved here
  instead; `scale_variant_file()` itself stayed in `pantheon.py` — it
  needs the rotation engine that lives there.
