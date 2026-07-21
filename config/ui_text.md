# UI Text Catalog

**Script:** [UI Text Catalog (script)](ui_text.py)

## Purpose
Translation Phase 2 (owner spec): every user-visible CHROME string —
menu items, dialog labels, tray balloons, hover legend labels and the
name tables (days, months, signs, animals, entities) — collected in
ONE catalog so the translation pipeline covers the whole app, not just
the reading content.

The design keeps the ENGLISH string itself as the key: the corpus
entry is `ui/<english text>`, and `ui(overlay, text)` returns the
active language's version with the English original as the fallback.
No invented key names, duplicates collapse for free, and an English
edit re-translates exactly that entry (the hash mechanism in
[Translations](../data/translations.md)).

Protected terms stay English in every language (product and brand
words): DOMY Watch, DOMY / MORPH / Omega, Trinity / Seasons /
Prism / Compass, Paint / Light, Umbra, Aura, Flame / Chalice / Seal,
Gold / Silver as finish names inside composed labels.

## Connections

### Uses
- nothing (a pure data module — importable everywhere)

### Used by
- [Translations](../data/translations.md) — `collect_corpus()` folds
  `UI_STRINGS` into the corpus as `ui/<text>` entries
- [App Controller](../app/controller.md) — menu labels, tooltips,
  tray balloons, error boxes
- [Settings Dialog](../app/settings_dialog.md),
  [Time Travel](../app/time_travel.md), [Guide](../app/guide.md),
  [Design Window](../app/design_window.md),
  [Pointer Theme](../app/pointer_theme.md),
  [Slot Theme](../app/slot_theme.md),
  [Weekday Theme Grid](../app/weekday_theme_grid.md) — dialog chrome
- [Compositor](../render/compositor.md) — hover legend labels and
  name tables (via the Symbolism Repository's shared overlay)

## Functions

- `ui(overlay, text)`: the translated form of `text` from the overlay
  (key `ui/<text>`), or `text` itself — English is the shipped source
- `UI_STRINGS`: the frozen catalog tuple; a test pins that every
  `ui(...)` literal in the codebase is present here
