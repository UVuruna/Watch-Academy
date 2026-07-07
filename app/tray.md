# Tray Controller

**Script:** [Tray Controller (script)](tray.py)

## Purpose
System tray presence: icon, tooltip and the shared context menu. The icon is
drawn procedurally until `assets/logo.svg` exists (M7).

## Connections

### Uses
- [Config (folder)](../config/___config.md) — icon size and palette

### Used by
- [App Controller](controller.md) — creates it with the shared menu

## Classes

### TrayController
Wraps `QSystemTrayIcon`, keeping strong Python references to the icon and
menu (Qt does not own them; the GC would destroy the menu mid-use).

#### Methods
- `show()` / `hide()`
