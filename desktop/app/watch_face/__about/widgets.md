# Watch Face Shared Widgets

**Script:** [Widgets (script)](../widgets.py)

## Purpose
The pill/tile builders every Watch Face section imports — extracted so
`pointer.py`/`ring.py`/`hands.py` never each redefine the same
`QPushButton`/`QToolButton` styling (Rule #5). Direct functional
counterpart of `design_window.DesignDialog._pill`/`_tile`, freed of the
class so a plain module function can be shared across the five section
modules instead of one method per subclass.

## Connections

### Uses
- [UI Style](../../__about/ui_style.md) — `style_button`
- [Config (folder)](../../../config/___config.md) — `palette.THEME_COLORS`
  (the selected-tile border accent)

### Used by
- `app.watch_face.pointer` / `.ring` / `.hands` / `.umbra_aura` / `.size`
- [Weekday Theme Grid](../../__about/weekday_theme_grid.md) — its `_tile`
  is a thin adapter over `tile` since 2026-08-08 (one tile look, one
  icon size, one builder)

## Functions
- `FlowLayout` / `FlowContent` / `flow_gallery(tiles)`: THE gallery
  shape since 2026-08-09 (replacing the fixed-column `pack_grid`, whose
  wrap could not satisfy both ALG-7 and the window minimum at once):
  uniform tiles (the widest label decides, ALG-5) flowing by REAL
  width, left-packed per the owner's 2026-08-06 decree, inside a host
  that publishes its true height at its current width (QScrollArea
  never consults heightForWidth on its own).
- `number_row(tr, settings, setters, key, low, high, title, form,
  decimals=0)`: the shared numeric slider row (numerals-ledger units) —
  used by the Numerals relief rows and the Size section's band-size
  rows (ALG-9 moved the three size sliders there, owner 2026-08-09).
- `pill(label, checked, on_click)`: a small `QPushButton`, "next" style
  when checked, else "neutral"
- `tile(label, icon, checked, on_click)`: a `QToolButton` with
  text-under-icon layout; `icon` is a pre-built `QIcon` (the caller
  supplies it, typically via `thumbs.py`) rather than a raw path — the
  one difference from `design_window._tile`, which loaded the `QIcon`
  itself from a `Path`. Every tile shows its icon at the shared
  `TILE_ICON_PX` (128) — set INSIDE the builder (owner instruction
  2026-08-08: every picker shows WHAT IT PICKS at a readable size, the
  Hands gallery being the model; nine call sites once relied on Qt's
  ~16px default while only Hands set its own). A tile with no icon
  reserves the same icon box transparently empty (uniform siblings,
  GUI Rules ALG-5) — an honest blank, never invented stand-in art.

## Design Decisions
- **`TILE_ICON_PX` lives in the builder, not per gallery** — the defect
  behind the owner's six 2026-08-08 screenshots was structural: a
  per-gallery `setIconSize` call that eight of nine galleries forgot.
  A default no caller can skip is the fix; a gallery genuinely needing
  another size would override AFTER `tile()` returns.
