# Design Window

**Script:** [Design Window (script)](design_window.py)

## Purpose

The mini WINDOW replacing the old Design submenu's deep chain — Pointer
(variant + palette style + Calendar lighting + the Calendar's 12-set
mount), Ring (preset + finish — gold/silver/bronze/THEMATIC, the 4th
pill coloring the letters in the active preset's own theme color,
ENLARGE/THEMATIC round 2026-07-27 — + Two metals, now offered for the
4-letter DOMY/PILOT too, + the Eye's Shine, DOLLAR/EYE round
2026-07-27 — the Shine checkbox shows only when the active card seats
the adaptive eye glyph), Umbra (form + contrast),
Complications (plate style), Hands and Earth (style + label mode) and
Size — as ONE tabbed window with images wherever real preview art
exists (R5 MENU REWORK item 3D, owner spec: "Isto kao sada samo u
lepsem meniju u Window sa slikama kao i kod ostalih").

**Asset honesty note:** only Ring (the layout's own face art,
`assets/ring/`), Hands (each pack's own hour-hand file) and Earth
(a representative continent plate) have real preview images today —
Pointer variants, Umbra and Complications have no dedicated preview art
(they are procedural/abstract), so those tabs use styled pill buttons
instead of inventing art that does not exist (`Owner Assets Are
Authoritative` — never code around an asset gap silently).

**THE CUBE THIRD WHEELS (owner seal 2026-07-26, CUBE.md; WORKPLAN
Session 20):** the Pointer tab's wheel row zips
`constants.palette_styles_for(pointer)` with the pointer's
`POINTER_PALETTE_LABELS` — the three Cube pointers show THREE pills
(Court/Family/**Genesis**, **Persons**/One Soul/**Council**,
Walks/Ages/**Character**), everything else keeps its two. The Prism's
paint pill reads **Persons** since 2026-07-27 (owner "ok.") — the wheel
has its own canon name and no longer wears the generic default label.

## Connections

### Uses
- [Theme](theme.md) — `apply_theme`, `size_to_screen`, the tab styling.
- [Config (folder)](../config/___config.md) — `RING_LAYOUTS`,
  `POINTER_POINTS`, `POINTER_DISPLAY_NAMES`, `POINTER_PALETTE_LABELS`,
  `UMBRA_FORMS`, `UMBRA_CONTRAST_VARIANTS`, `SIZE_PRESETS`.
- `data.rings.ring_presets`, `data.hands.hand_packs` — the preset/pack
  catalogs the Ring and Hands tabs list.

### Used by
- [Controller](controller.md) — `_open_design` (non-modal, one live
  instance, raised on a second open); `_design_setters` wraps every
  existing `_set_*` method (ring/pointer/palette/umbra/hands/earth/
  diameter) so a pick both applies AND refreshes the open window.

## Classes

### DesignDialog
Non-modal, LIVE-APPLY (same justification as
[Pointer Theme](pointer_theme.md)/[Slot Theme](slot_theme.md)): every
tab's pick calls its setter immediately, matching the menu chain it
replaces. `refresh(settings, setters)` re-supplies the live state after
a pick (called by the controller) so every tab's highlighted pick stays
current without closing the window. No gating — Design has no owner-
specified gray condition.
