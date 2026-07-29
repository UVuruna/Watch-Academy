# Encyclopedia UI

**Script:** [Encyclopedia UI (script)](encyclopedia_ui.py)

## Purpose

The reading surfaces — Encyclopedia, legend and the computed diagrams
— one of six modules Session 36 (THE CONFIG SPLIT,
[Work Plan Structure](../WORKPLAN-STRUCTURE.md)) carved out of
`config/defaults.py`.

Layer: config — pure, no Qt, no wall clock.

## What moved here

- **Legend term highlighting** — `LEGEND_TERM_PATTERNS` and the
  legend/Encyclopedia sizing constants (`LEGEND_*`, `ENCYCLOPEDIA_
  TEXT_WIDTH_FRACTION`… `ENCYCLOPEDIA_GALLERY_CARD_PADDING_PX`).
- **THE COMPUTED DIAGRAMS** — `CUBE_DIAGRAM_*`, `CANON_DIAGRAM_*`.
- **THE SESSION 27 REWORK** (minus `OMEGA_HIT_RADIUS_FRACTION`, the
  split map's named exception, which moved to `dial.py`, and minus
  `SUBDIAL_*`/`REPORT_*`/`OBSERVATORY_*`/`DIALOG_A4_*`/`GUIDE_*`/
  `TRANSLATE_*`/`TIME_TRAVEL_*`/`QUICK_JUMP_*`/`GREENWICH_*`/
  `REVEAL_WEEK_DURATION_S` — this banner had drifted well past its own
  topic by the time it reached this session; see Design Decisions) —
  the Encyclopedia's own card/gallery/reader sizing (`ENCYCLOPEDIA_
  MIN_WIDTH_PX`… `ENCYCLOPEDIA_MOSAIC_GAP_PX`), the shared UI chrome
  constants (`UI_BUTTON_*`, `THEME_RADIUS_*`), `READER_IMAGE_MAX_
  HEIGHT_FRACTION`, the Greetings arc geometry (`GREETINGS_*`).
- **`ARTICLE_*`** (image/text/column widths, subhead gaps, title size)
  and **`SCALE_ART_DIR`/`ASTRO_*`/`PERIOD_EARTH_IMAGE_PX`** — these
  drifted into "THE CALENDAR MOUNT REGISTRY"'s own span (article hover
  layout has nothing to do with calendar mounts) and moved here
  instead; `scale_variant_file()` itself stayed in `pantheon.py`
  (it needs the rotation engine that lives there — see that module's
  own Design Decisions).
- **Hover article warm sweep** — `HOVER_WARM_ANGLE_STEPS`/`_RADIAL_
  STEPS`/`_RING_PAUSE_S`.
- **THE INSTRUMENT'S OWN DIAGRAMS** — `INSTRUMENT_DIAGRAM_*`,
  `INSTRUMENT_TWILIGHT_BANDS`.

## Connections

### Uses
- [Config (folder)](___config.md) — `constants`, `paths`

### Used by
- [App (folder)](../app/___app.md) — the Encyclopedia package (legend
  popup, cards, reader, tree, home, dialog), `ui_style.py`, `theme.py`
- [Render (folder)](../render/___render.md) — `canon_diagrams.py`,
  `cube_diagrams.py`, `instrument_diagrams.py`, `compositor.py`'s
  Greetings arc

## Design Decisions

- **"THE SESSION 27 REWORK" is named after WHEN it was written, not a
  stable topic** — everything a LATER session tacked on after it (with
  no fresh banner of its own) inherited its span without belonging to
  its subject. The split map's own pre-answered Q&A already carves ONE
  such stray (`SUBDIAL_RECOLOR_*` stays remnant) — this module follows
  the same reading for the rest of the drift rather than dumping
  Report-chart, Observatory-chart, Guide-dialog and Time-Travel values
  into an "Encyclopedia" module they have nothing to do with.
