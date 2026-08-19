# Complications

**Script:** [Complications (script)](../complications.py)

## Purpose

THE SOUTH SLOT and what it may show. A complication is a small reading
the dial carries beside the time; this module is the vocabulary of the dial
slots' CONTENT.

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

- **What a slot may show** — `OCTA_SLOT_MODES` (the South slot),
  `WEEKDAY_SLOT_MODES` (the weekday slot) and
  `SLOT_COMPLICATION_TITLES`, the menu names those modes wear.
- **Where the content hangs** — `SLOT_SEAT_TOP_ANGLE`,
  `SLOT_SEAT_RIGHT_ARM_ANGLE`, `SLOT_SEAT_LEFT_ARM_ANGLE`.
- **How a sign complication is drawn** — `ZODIAC_SLOT_STYLES`,
  `CHINESE_SLOT_STYLES`, `SLOT_STYLE_VALUES`, and the two art-directory
  maps `ZODIAC_STYLE_ART_DIRS` / `CHINESE_STYLE_ART_DIRS`.
- **`EARTH_STYLES`** — the Earth marker's own style list.

## Connections

### Uses
- nothing — a leaf module.

### Used by
- [Render (folder)](../../render/___render.md) — the slot layer and
  slot layout
- [App (folder)](../../app/___app.md) — the menu, the shortcuts, the
  Watch Face window, the settings store's slot validation
- `shared/research/build_roster.py` — the zodiac and chinese art dirs

## Design Decisions

- **Its twin is `config/registry/slots.py`, and the two never overlap.**
  THE SLOT REGISTRY answers WHICH `Settings` field each of the three
  slots stores its answers in; this module answers what the answers may
  BE. One is plumbing, one is vocabulary.
- **Standard tier, no flow doc.** Flat mode/style/art-dir tables keyed by
  slot and style — a diagram would restate them.
