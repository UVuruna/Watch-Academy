# Tray Controller

**Script:** [Tray Controller (script)](tray.py)

## Purpose
System tray presence: icon, tooltip and the shared context menu. The icon
is the owner's gold watch (`assets/logo.svg`) rasterized to the tray size
— a missing or broken logo raises loudly instead of an empty tray.

## Connections

### Uses
- [Config (folder)](../config/___config.md) — icon size, `LOGO_ASSET`
- [Assets (folder)](../assets/___assets.md) — logo.svg

### Used by
- [App Controller](controller.md) — creates it with the shared menu

## Classes

### TrayController
Wraps `QSystemTrayIcon`, keeping strong Python references to the icon and
menu (Qt does not own them; the GC would destroy the menu mid-use).

#### Methods
- `show()` / `hide()`
- `notify(title, message)`: non-blocking critical balloon (mid-run
  settings-save failures)
- `on_double_click(callback)` (owner 2026-07-18, ROADMAP 15h, Session
  21-C): wires `callback()` to a tray icon DOUBLE-CLICK
  (`QSystemTrayIcon.activated`, filtered to `ActivationReason.
  DoubleClick`) — the "Show" affordance's second trigger. The
  controller registers `_show_if_normal_z_mode` here (a no-op outside
  "normal" z-mode).
