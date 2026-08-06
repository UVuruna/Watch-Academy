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

## Functions
- `pack_grid(grid, columns)`: left-packs a gallery grid — GUIDE_SPACING
  gaps plus a trailing stretch column that swallows the window's
  surplus, so tiles keep their own size instead of drifting apart with
  every extra pixel (the owner's 2026-08-06 screenshots: tiles scattered
  across a 4K window). Every section gallery routes through it.
- `pill(label, checked, on_click)`: a small `QPushButton`, "next" style
  when checked, else "neutral"
- `tile(label, icon, checked, on_click)`: a `QToolButton` with
  text-under-icon layout; `icon` is a pre-built `QIcon` (the caller
  supplies it, typically via `thumbs.py`) rather than a raw path — the
  one difference from `design_window._tile`, which loaded the `QIcon`
  itself from a `Path`
