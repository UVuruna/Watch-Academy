# Design Window

**Script:** [Design Window (script)](design_window.py)

## Purpose

The mini WINDOW replacing the old Design submenu's deep chain — Pointer
(variant + palette style, SHAPE since the Pointers REWORK phase 2,
owner decree 2026-07-29 — the Calendar's lighting row went with the
deleted feature and its MOUNT row moved to the
[Pointer Theme](pointer_theme.md) window, where the other roster
galleries live; phase 3, same owner sheet, ADDED the Star/Polygon
switch, the curvature slider + Smooth-concave/V-notched edge switch
— polygon pointers in "Polygon" shape only — and the Hide-night-
borders toggle, every row but Aurora, see "THE POINTER SHAPE ROWS"
below), Ring (preset + finish — gold/silver/bronze/THEMATIC, the 4th
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

**THE POINTER SHAPE ROWS (Pointers REWORK phase 3, owner sheet
`UV/Pointers.png`, 2026-07-29):** three rows follow the wheel row, each
gated by reading the CURRENT `settings.pointer`/`pointer_shape` fresh
on every build — a pointer switch alone re-gates them on the next
live-apply rebuild, no extra wiring needed (`_build()` already reruns
every tab from scratch on any pick, see `DesignDialog` below):
- **Shape** (`constants.POINTER_SHAPES`, "Star"/"Polygon" pills) —
  every pointer EXCEPT Aurora, which draws no pointer at all and
  ignores the choice; the row is omitted outright on Aurora, the same
  "just don't add the widget" idiom the Ring tab's own conditional
  Two-metals/Shine rows already use (Rule #5).
- **Curvature** (a percent slider over `POLYGON_CURVATURE_RANGE`,
  commits on `sliderReleased` like the Size tab's diameter slider) +
  **Edge** ("Smooth concave"/"V-notched" pills, `POLYGON_EDGE_MODES`)
  — shown together, ONLY when the active pointer is a TRUE polygon
  (`constants.POLYGON_POINTERS` — trio/cross/hexa/octa) AND the active
  shape is "polygon". The Calendar's and the Rose's own "polygon"
  reading are touching-arm STARS (owner spec) that never curve, so
  they never show this pair even in Polygon shape.
- **Hide night borders** (a `QCheckBox`, `Settings.hide_night_borders`)
  — every pointer except Aurora, same gate as Shape. Since the owner's
  correction round (2026-07-29) it is **DISABLED (greyed, never
  hidden)** whenever it cannot act: the Calendar and the Rose may switch
  the day/night law off entirely, and with no night there is no night
  border to hide. The gate is `render.layers.daylight_active(settings)`
  — the ONE law, asked of the raw `Settings` object the window already
  holds (it answers on `pointer` + `daylight` alone), never a second
  copy of the pointer list (Rule #5). Enabled in every other state.

Every row's pick routes through `_setters["pointer_shape"/
"polygon_curvature"/"polygon_edge"/"hide_night_borders"]` — plain
entries in `_design_setters()` wrapping the controller's existing
generic `_set_display_choice(key, value)`, the SAME mechanism
`umbra_form`/`umbra_contrast`/`subdial_style`/`earth_style` already use
(Rule #5 — no new setter method). Pinned in `tests/test_design_window.py`
(the row gating matrix + which widget calls which setter with which
value) and `tests/test_pointer_shapes.py`
(`test_the_four_design_rows_persist_and_reach_the_live_skin` — the
real controller: a pick persists to `Settings` AND reaches the
installed skin).

## Connections

### Uses
- [Theme](theme.md) — `apply_theme`, `size_to_screen`, the tab styling.
- [Config (folder)](../config/___config.md) — `RING_LAYOUTS`,
  `POINTER_POINTS`, `POINTER_DISPLAY_NAMES`, `POINTER_PALETTE_LABELS`,
  `UMBRA_FORMS`, `UMBRA_CONTRAST_VARIANTS`, `SIZE_PRESETS`.
- `data.rings.ring_presets`, `data.hands.hand_packs` — the preset/pack
  catalogs the Ring and Hands tabs list.
- [Layers](../render/layers.md) — `daylight_active`, the ONE reader of
  the day/night switch, used to grey out "Hide night borders" when no
  night exists.

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
current without closing the window. Exactly ONE greyed row exists (owner
correction 2026-07-29): "Hide night borders" while the active pointer's
daylight law is switched off — see the Pointer tab above.
