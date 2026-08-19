# UI Ranges

**Script:** [UI Ranges (script)](../ui_ranges.py)

## Purpose

What the user-facing CONTROLS may be set to. Every entry answers one
question — what values may the user pick in this control.

Layer: config — pure Python, no Qt, no wall clock.

## Why it exists

`config/constants.py` carried **38 top-level sections** — app identity,
era notation, weekday bodies, pointer geometry, ring finishes, zodiac,
translation languages, UI scale, seating — under one docstring. That is a
junk drawer, not a directory: nobody could say what the module was ABOUT,
and every session that needed one constant read past thirty-seven
subjects it did not care about. The [OOP audit](../../../docs/AUDIT-OOP-2026-08-18.md)'s
R15 asked for a topic split; the owner ruled on **2026-08-19**, naming
each destination module himself, and this file is one of them.

The move was mechanical and total: each section travelled WHOLE, with
its comments, and every caller was repointed to the real module. **No
re-export shim was left behind** (`rules/CODE.md` — No backward
compatibility), and `config/constants.py` was deleted in the same round.

## Contents

- **Languages** — `TRANSLATION_LANGUAGES` (the codes the provider
  accepts, code → English display name) and `TRANSLATION_ORIGINALS`, the
  two that ship hand-written and sit pinned at the top of the combo;
  every other language machine-translates on first pick.
- **Zoom** — `ENCYCLOPEDIA_ZOOM_RANGE` and `ENCYCLOPEDIA_ZOOM_STEP`, the
  Ctrl+MouseWheel factor that scales fonts, images and gallery tiles
  together. The RANGE is the fixed invariant; the live factor is
  session-only state on `app.encyclopedia`.
- **Element sizes** — `ELEMENT_SCALE_RANGE` and `HOVER_ENLARGE_RANGE`.
- **Saturation** — four independent sliders with their steps:
  `POINTER_`, `RING_`, `HANDS_` and `UMBRA_SATURATION_RANGE` /
  `_SLIDER_STEP`. 0.0 grays the target to its own brightness, 1.0 is the
  owner preset unchanged; the slider is 0–100 and the stored setting is
  the 0.0–1.0 factor.

## Connections

### Uses
- nothing — a leaf module.

### Used by
- [App (folder)](../../app/___app.md) — the Settings dialog's Colors
  and Display pages, the Encyclopedia's zoom, the settings store's
  clamping
- [Data (folder)](../../data/___data.md) — the translation corpus
- [Render (folder)](../../render/___render.md) — the saturation the
  ring, hands and Umbra recolor with

## Design Decisions

- **Deliberately NOT `config/ui_text.py`.** That module is THE UI STRING
  CATALOG — one flat tuple of every translatable chrome string plus the
  `ui()` lookup — and a bound is not a string. What the two share is only
  that a control reads them; merging them would have made the catalog a
  mixed bag the moment a range needed changing.
- **The language ROSTER is a range, not text.** It is the set of values
  the language combo may be set to, exactly like the zoom bounds are the
  set of values the zoom may take.
