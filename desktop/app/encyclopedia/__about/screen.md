# Encyclopedia Screen

**Script:** [Encyclopedia Screen (script)](../screen.py)

## Purpose
`EncyclopediaScreen(QWidget)` — one SCREEN of the Encyclopedia stack,
and the three things all of them are.

The dialog is a stack of three: [Home](home.md) (the nine wholes),
[Themes](themes.md) (one whole's cards) and [Reader](reader.md) (the
article slider). They are the same KIND — each is built from
`(topics, encyclopedia, tr)`, each holds a zoom factor, and each
re-lays itself out when that factor changes — and until R8 of the [OOP
audit](../../../../docs/AUDIT-OOP-2026-08-18.md) they were three
unrelated `QWidget` subclasses that each wrote those three things
again.

Worse, the zoom protocol had FORKED into two spellings: `fit(zoom=None)`
on the two grid screens, `set_zoom(zoom)` on the reader. Nothing made
them agree, so [Dialog](dialog.md) branched on which screen was
showing — `if screen == _HOME: … elif _THEMES: … else: …` — in three
places, including `_apply_zoom`, whose whole body was that branch.

## Connections

### Uses
- `PySide6.QtWidgets.QWidget` — nothing else

### Used by
- [Home](home.md) · [Themes](themes.md) · [Reader](reader.md) — the
  three screens
- [Dialog](dialog.md) — `self._stack.currentWidget().apply_zoom(zoom)`,
  with no idea which screen answered

## The protocol
- `apply_zoom(zoom=None)` — `None` means "same factor, lay out again"
  (what a resize asks for); a number means the user turned Ctrl+wheel
  and every screen must remember it, showing or not, because the dialog
  zooms the WHOLE encyclopedia and the screen behind must already be
  right when it comes forward.
- `_relayout()` — each screen's own answer to "lay yourself out at the
  zoom you are holding". Home measures from its own box (the 3×3 never
  scrolls, so height is an input); Themes measures the scroll
  viewport's WIDTH only (the gallery scrolls, so height is an output);
  the Reader has no grid and rescales its page — font, images and
  diagrams together.

## Design Decisions
- **The base owns `_zoom`; subclasses never assign it.** A screen that
  set the factor itself is how the two spellings drifted apart in the
  first place.
- **`opened = Signal(str)` stays on the two GRID screens**, not on the
  base. The reader emits `page_changed`/`zoomed` instead — it opens
  nothing. A signal on the base that one subclass can never emit would
  be a promise the kind does not keep.
- **The reader's extra collaborator stays in its own `__init__`.** It
  needs the symbolism book; the other two do not. The base takes the
  three every screen has and no more.
