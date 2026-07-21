# Tray Controller

**Script:** [Tray Controller (script)](tray.py)

## Purpose
System tray presence: icon, tooltip and the shared context menu. Also
the home of the app's icon shapes — the tray icon rasterized PER WATCH
(ADD WATCH round, owner INSTRUCTION.txt item 2B) and the single
app-wide window icon — all ultimately from the owner's gold watch
(`assets/logo.svg`) or its rose-gold sibling (`assets/logo-setup.svg`);
a missing or broken logo raises loudly instead of an empty tray / a
generic window icon.

## Connections

### Uses
- [Config (folder)](../config/___config.md) — icon sizes, `LOGO_ASSET`/
  `LOGO_SETUP_ASSET`, `TRAY_COLOR_WHEEL` (ADD WATCH round)
- [Assets (folder)](../assets/___assets.md) — logo.svg, logo-setup.svg
- [Assets](../render/assets.md) — `tinted_pixmap()` (ADD WATCH round): the
  SAME tritone recolor ring/hand tints use, reached here without pulling
  in the render pipeline

### Used by
- [Watch Controller](controller.md) — creates its own tray with
  `logo_icon(watch_index)`; sets the app-wide window icon from
  `window_icon()` (owner screenshot 2026-07-20: without this AND
  `app.native.set_app_user_model_id`, Encyclopedia/Guide/Observatory/
  Settings/Time Travel windows fell back to python.exe's own logo in the
  Windows taskbar) — called once per watch construction, redundant past
  the first (harmless: idempotent, one process-wide identity)

## Functions

- `_rasterize_logo(size, asset=LOGO_ASSET)`: the shared QSvgRenderer
  rasterizer behind both icon shapes below — aspect kept and centered on
  a transparent `size`x`size` canvas; raises `ValueError` on a missing/
  broken SVG. `asset` (ADD WATCH round) lets `logo_icon` rasterize the
  rose-gold master for watch 2 instead of the default gold one
- `_logo_asset(watch_index)` / `_tray_tint(watch_index)` (ADD WATCH
  round, owner INSTRUCTION.txt item 2B): the per-watch identity rule —
  watch 1 the gold master untouched; watch 2 the pre-existing rose-gold
  master (`LOGO_SETUP_ASSET`, a SECOND master, not a recolor); watch 3+
  the gold master tinted (`tinted_pixmap`) cycling
  `defaults.TRAY_COLOR_WHEEL` forever, starting PURPLE `#8000FF`
  (R:G:B 1:0:2) then BLUE `#0000FF` (R:G:B 0:0:1) — the CALENDAR
  pointer's own MONTH wheel (`UV/Color Wheels.png`), read from January
  (Rule #19 — computed from the one wheel already in the codebase, never
  a new generated icon)
- `logo_icon(watch_index=1)`: the TRAY icon for `watch_index` — one fixed
  size (`defaults.TRAY_ICON_SIZE`), the tray never asks for another
- `window_icon()`: the APP-WIDE window icon (owner screenshot
  2026-07-20) — one `QIcon` carrying EVERY size in
  `defaults.WINDOW_ICON_SIZES_PX` (16 through 256 px), so Windows picks
  the sharpest match per context instead of blurrily scaling a single
  size. Passed to `QApplication.setWindowIcon`; every dialog inherits
  it automatically — no per-dialog wiring needed. Stays the ONE gold
  identity regardless of watch (see [Watch Manager](watch_manager.md)'s
  own Design Decisions for why a per-watch window icon was not worth
  chasing).

## Classes

### TrayController
Wraps `QSystemTrayIcon`, keeping strong Python references to the icon and
menu (Qt does not own them; the GC would destroy the menu mid-use).

#### Methods
- `show()` / `hide()`
- `set_menu(menu)`: swaps the context menu (rebuilt after Settings)
- `set_tooltip(text)` (R5 MENU REWORK, owner INSTRUCTION.txt item
  2A): the hover tooltip — `app.controller.watch_title(settings,
  full=True)`, the FULL multi-attribute name, unlike the menu's own
  TITLE row which stays short until more than one watch exists
- `notify(title, message)`: non-blocking critical balloon (mid-run
  settings-save failures)
- `on_double_click(callback)` (owner 2026-07-18, ROADMAP 15h, Session
  21-C): wires `callback()` to a tray icon DOUBLE-CLICK
  (`QSystemTrayIcon.activated`, filtered to `ActivationReason.
  DoubleClick`) — the "Show" affordance's second trigger. The
  controller registers `_show_if_normal_z_mode` here (a no-op outside
  "normal" z-mode).
