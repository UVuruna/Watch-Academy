# Pointer Names

**Script:** [Pointer Names (script)](../pointer_names.py)

## Purpose

What a pointer is CALLED — every display name the pointer family wears,
in the menu, in Settings and in the hover legends.

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

- **`POINTER_DISPLAY_NAMES`** — the pointers' own names.
- **`POINTER_PALETTE_LABELS`** — the WHEEL labels: what each pointer's
  primary / secondary / tertiary wheel MEANS. This is the ONE place a
  wheel's meaning is written; `config/registry/slots.py` says only that
  the slot exists (the keys there are positional and carry no meaning of
  their own — owner decree 2026-07-28, closing the "paint"/"light" era).
- **`POINTER_ARM_LABELS`** — the labels each wheel's arms carry.
- **`ONE_SOUL_THEME_NAME` / `ONE_SOUL_THEME_TITLE`** — the one wheel
  theme whose name is quoted by the Design window and the Encyclopedia
  alike.

## Connections

### Uses
- nothing — a leaf module.

### Used by
- [Palette](palette.md) — the arm labels drive the palette rows
- [Render (folder)](../../render/___render.md) — the arm and wheel
  legends the tooltips read
- [App (folder)](../../app/___app.md) — the menu, the Watch Face
  window, the Encyclopedia

## Design Decisions

- **Standard tier, no flow doc.** Three flat label tables keyed by
  pointer: a diagram would restate the code (`rules/DOCS.md` — a flow doc
  must EARN its place).
