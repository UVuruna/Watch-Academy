# UI Text Catalog

**Script:** [UI Text Catalog (script)](../ui_text.py) · **Flow:** [diagram](../__flow/ui_text.md)

## Purpose

Translation Phase 2 (owner spec): every user-visible CHROME string —
menu items, dialog labels, tray balloons, hover legend labels and the
name tables (weekdays, months, moon phases, zodiac signs, Chinese
animals, entity names) — collected in ONE catalog, `UI_STRINGS`, so
the translation pipeline covers the whole app, not just the reading
content.

The design keeps the ENGLISH string itself as the key: the corpus
entry is `ui/<english text>`, and `ui(overlay, text)` returns the
active language's version with the English original as the fallback.
No invented key names, duplicates collapse for free, and an English
edit re-translates exactly that entry.

Protected terms stay English inside translated sentences (product and
brand words): Watch Academy, DOMY, Trinity / Seasons / Prism /
Compass, Umbra, Aura, Flame / Chalice / Seal, and the wheel names.

Layer: config — pure, no Qt, no wall clock.

## Contents

`UI_STRINGS` is one flat tuple of ~450 English strings, grouped by
comment banner in source order: Menu, Settings dialog, Time Travel /
Guide, Tray balloons / error boxes, Hover legend labels, Name tables
(weekdays/months/moon phases/zodiac/Chinese animals/elements), the
Observatory chart chrome. `ui(overlay, text)` is the module's only
function.

## Connections

### Uses
- nothing (a pure data module — importable everywhere)

### Used by
- `data.translations` — `collect_corpus()` folds `UI_STRINGS` into the
  corpus as `ui/<text>` entries
- [Watch Controller](../../app/__about/controller.md) — menu labels, tooltips,
  tray balloons, error boxes
- The Settings Dialog, Time Travel, Design Window, Pointer Theme, Slot
  Theme and Weekday Theme Grid windows (all under [App (folder)](../../app/___app.md))
  — dialog chrome
- [Compositor](../../render/__about/compositor.md) — hover legend labels and
  name tables (via the Symbolism Repository's shared overlay)

## Functions

- `ui(overlay, text)`: the translated form of `text` from the overlay
  (key `ui/<text>`), or `text` itself — English is the shipped source

## Design Decisions

- **The English string IS the key.** No synthetic key namespace to
  keep in sync with the displayed text — an English edit changes the
  corpus key and therefore re-triggers translation for exactly that
  string, never silently serving a stale one under an unrelated key.
- **One flat tuple, not a nested structure.** Every consumer just needs
  "is this string in the catalog" and "what's its translated form" —
  a test pins that every `ui(...)` call site's literal argument is
  present here, so the tuple's own shape (flat, order-only-for-
  humans) is sufficient.
