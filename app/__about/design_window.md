# Design Window

**Script:** [Design Window (script)](../design_window.py) · **Flow:** [diagram](../__flow/design_window.md)

## Purpose
The mini window replacing the old Design submenu's deep chain — Pointer
(variant + palette style + shape), Ring (preset + finish + two-metals +
eye shine), Umbra (form + contrast), Complications (plate style), Hands,
Earth (style + label mode) and Size — as ONE tabbed window, with images
wherever real preview art exists (R5 MENU REWORK item 3D).

**Asset honesty:** only Ring (the layout's own face art), Hands (each
pack's own hour-hand file) and Earth (a representative continent plate)
have real preview images; Pointer variants, Umbra and Complications have
no dedicated preview art (they are procedural/abstract), so those tabs
use styled pill buttons instead of inventing art that does not exist.

## Connections

### Uses
- [Theme](theme.md) — `apply_theme`, `size_to_screen`
- [Config (folder)](../../config/___config.md) — `constants.RING_LAYOUTS`,
  `POINTER_POINTS`, `POINTER_DISPLAY_NAMES`, `POINTER_PALETTE_LABELS`,
  `POINTER_SHAPES`, `POLYGON_POINTERS`, `UMBRA_FORMS`,
  `UMBRA_CONTRAST_VARIANTS`, `SIZE_PRESETS`
- [Rings (data)](../../data/__about/rings.md) — `ring_presets`
- [Hands (data)](../../data/__about/hands.md) — `hand_packs`
- `render.skin_geometry.daylight_active` — the one law "does this
  pointer currently show a night to hide a border in", read from the
  raw `Settings` object (pointer + daylight) so the Pointer tab's "Hide
  night borders" row can grey out honestly instead of lying

### Used by
- [Watch Controller](controller.md) — `_open_design` (non-modal, one
  live instance, raised on a second open); `_design_setters()` wraps
  every existing `_set_*` controller method so a pick both applies AND
  refreshes the open window

## Classes

### DesignDialog(QDialog)
Non-modal, LIVE-APPLY — every tab's pick calls its setter immediately;
there is nothing to commit, no OK/Cancel.

#### Methods
- `refresh(settings, setters)`: re-supplies the live settings after a
  pick applies, then rebuilds — called by the controller
- `_build()`: rebuilds the `QTabWidget` from scratch on every pick,
  KEEPING the previously open tab index (a fresh `QTabWidget` would
  otherwise always reopen at index 0)
- `_pointer_tab()`: pointer-variant pills (sorted by their own arm
  count), the palette-style wheel-pair pills (`palette_styles_for`,
  widened to three pills on the Cube pointers), and — every pointer
  except Aurora — the Shape row (star/polygon), the Curvature slider +
  Edge pills (only on a TRUE polygon in "polygon" shape), and the "Hide
  night borders" checkbox (enabled only when `daylight_active(settings)`)
- `_ring_tab()`: preset tiles (icon = the layout's own face art), the
  finish pills, and — only when the active card's layout carries a
  triangle — the "Two metals" checkbox, and — only when the active
  card seats the adaptive Eye glyph — the "Shine" checkbox
- `_umbra_tab()` / `_complications_tab()` / `_hands_tab()` / `_earth_tab()` /
  `_size_tab()`: pill/tile grids over their own closed option sets; the
  Size tab also carries a live diameter slider (commits on
  `sliderReleased`, matching the Design ▸ Pointer curvature slider's
  own commit timing)

## Design Decisions
- Every scalar Design pick (`pointer_shape`, `polygon_curvature`,
  `polygon_edge`, `hide_night_borders`, `umbra_form`, `umbra_contrast`,
  `subdial_style`, `earth_style`) routes through the SAME controller
  method, `_set_display_choice(key, value)` — no new setter method per
  new row (Rule #5).
