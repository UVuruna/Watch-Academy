# Tray Controller

**Script:** [Tray Controller (script)](../tray.py)

## Purpose
System tray presence — icon, tooltip, the shared context menu — and the
home of the app's two icon shapes: the tray icon (rasterized per watch,
ADD WATCH round) and the single app-wide window icon. Both derive from
the owner's gold watch (`assets/logo.svg`) or its rose-gold sibling
(`assets/logo-setup.svg`); a missing or broken logo raises loudly
instead of showing an empty tray or a generic window icon.

## Connections

### Uses
- [Config (folder)](../../config/___config.md) — `defaults.TRAY_ICON_SIZE`,
  `LOGO_ASSET`/`LOGO_SETUP_ASSET`, `WINDOW_ICON_SIZES_PX`
- [Palette (config)](../../config/__about/palette.md) — `TRAY_COLOR_WHEEL`
  (ADD WATCH round, watch 3+)
- [Asset Recolor](../../render/__about/asset_recolor.md) — `tinted_pixmap()`, the
  same tritone recolor ring/hand tints use, reached here without pulling
  in the render pipeline

### Used by
- [Watch Controller](controller.md) — builds its own tray with
  `logo_icon(watch_index)`; sets the app-wide window icon from
  `window_icon()`

## Functions

- `_rasterize_logo(size, asset=LOGO_ASSET) -> QPixmap`: the shared
  `QSvgRenderer` rasterizer behind both icon shapes — aspect kept and
  centered on a transparent `size`×`size` canvas; raises `ValueError` on
  a missing/broken SVG
- `_logo_asset(watch_index)` / `_tray_tint(watch_index)`: the per-watch
  identity rule — watch 1 the gold master untouched; watch 2 the
  pre-existing rose-gold master (a second master, not a recolor); watch
  3+ the gold master tinted, cycling `palette.TRAY_COLOR_WHEEL` forever
- `logo_icon(watch_index=1) -> QIcon`: the tray icon, one fixed size
- `window_icon() -> QIcon`: the app-wide window icon — one `QIcon`
  carrying every size in `defaults.WINDOW_ICON_SIZES_PX` (16–256px), so
  Windows picks the sharpest match per context instead of blurrily
  scaling a single size; passed to `QApplication.setWindowIcon`, so
  every dialog inherits it with no per-dialog wiring

## Classes

### TrayController
Wraps `QSystemTrayIcon`, keeping strong Python references to the icon
and menu (Qt does not own them; the GC would otherwise destroy the menu
mid-use).

#### Methods
- `show()` / `hide()`
- `set_menu(menu)`: swaps the context menu (rebuilt after Settings)
- `set_tooltip(text)`: the hover tooltip — `watch_title(settings, full=True)`,
  the full multi-attribute name, unlike the menu's own TITLE row which
  stays short until more than one watch exists
- `on_double_click(callback)`: wires `callback()` to a tray icon
  double-click (`QSystemTrayIcon.ActivationReason.DoubleClick`) — the
  "Show" affordance's second trigger
- `notify(title, message, critical=True)`: non-blocking balloon — errors
  by default, `critical=False` for progress notes
