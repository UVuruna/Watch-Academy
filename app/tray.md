# Tray Controller

**Script:** [Tray Controller (script)](tray.py)

## Purpose
System tray presence: icon, tooltip and the shared context menu. Also
the home of the app's TWO icon shapes, both rasterized from the
owner's gold watch (`assets/logo.svg`) — a missing or broken logo
raises loudly instead of an empty tray / a generic window icon.

## Connections

### Uses
- [Config (folder)](../config/___config.md) — icon sizes, `LOGO_ASSET`
- [Assets (folder)](../assets/___assets.md) — logo.svg

### Used by
- [App Controller](controller.md) — creates the tray with `logo_icon()`;
  sets the app-wide window icon from `window_icon()` (owner screenshot
  2026-07-20: without this AND `app.native.set_app_user_model_id`,
  Encyclopedia/Guide/Observatory/Settings/Time Travel windows fell back
  to python.exe's own logo in the Windows taskbar)

## Functions

- `_rasterize_logo(size)`: the shared QSvgRenderer rasterizer behind
  both icon shapes below — aspect kept and centered on a transparent
  `size`x`size` canvas; raises `ValueError` on a missing/broken SVG
- `logo_icon()`: the TRAY icon — one fixed size
  (`defaults.TRAY_ICON_SIZE`), the tray never asks for another
- `window_icon()`: the APP-WIDE window icon (owner screenshot
  2026-07-20) — one `QIcon` carrying EVERY size in
  `defaults.WINDOW_ICON_SIZES_PX` (16 through 256 px), so Windows picks
  the sharpest match per context instead of blurrily scaling a single
  size. Passed to `QApplication.setWindowIcon`; every dialog inherits
  it automatically — no per-dialog wiring needed.

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
