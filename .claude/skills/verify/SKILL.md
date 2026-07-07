---
name: verify
description: Build/launch/drive recipe for verifying DOMY Watch (transparent PySide6 desktop widget) end-to-end on this Windows machine.
---

# Verifying DOMY Watch

## Launch

```powershell
python main.py    # from the project root; PySide6 6.10 is installed globally
```

Run it as a background task; the process keeps running until Exit is chosen
from the widget/tray menu (clean exit code 0).

## Drive & observe (GUI surface = real desktop pixels)

A reusable Win32 driver lives in the session scratchpad pattern
`drive.ps1` (recreate if missing): SetProcessDPIAware + FindWindowW/
GetWindowRect/MoveWindow/SetCursorPos/mouse_event/keybd_event +
CopyFromScreen capture helpers.

Gotchas learned the hard way (2026-07-07):

- **FindWindowW from PowerShell:** pass `[NullString]::Value` for the class,
  NOT `$null` (PowerShell marshals `$null` as empty string → no match).
  Better: enumerate windows by PID — an Explorer window open on the project
  folder also has the exact title "DOMY Watch".
- **Always capture at the window's CURRENT GetWindowRect**, never at a
  remembered position — and re-read the rect immediately before each capture.
- **IsWindowVisible lies:** it stays TRUE for covered and minimized windows.
  To decide "is it really on screen", pixel-sample a distinctive widget pixel
  (the yellow noon triangle at window top-center, ~(cx, top+15px) physical;
  expect ≈ RGB 202,168,64 over dark wallpaper) via GetPixel.
- **Wallpaper slideshow** changes the background between captures — never
  compare screenshots to judge presence; use pixel sampling.
- **Monitors:** 2× 3840×2160; primary at 125% (logical 3072×1728), so
  360 logical = 450 physical on the primary. Settings store logical coords.
- **Win+D ground truth (Win11 24H2):** the widget gets NO Qt events; the OS
  raises the desktop layer above ALL windows (TOPMOST included). Nothing
  window-level restores visibility until Show Desktop mode ends. Do not
  chase this as a bug.
- **The owner is often at the machine** — expect live human interference
  (windows dragged, menus clicked). Their interaction is bonus end-to-end
  evidence; synthetic clicks may land on moved windows, so re-read rects.

## State

- Settings: `%APPDATA%\DOMY Watch\settings.json` (atomic writes, debounce
  750 ms after a move). Corrupt it (truncate mid-JSON) to test the recovery
  dialog: Reset quarantines to `settings.json.bak` and reseeds defaults.
- The corrupt-settings dialog is parentless — find it by PID (it exists
  before the widget window does).

## Flows worth driving

1. Launch → placeholder dial visible, transparent corners (capture at rect).
2. MoveWindow → wait >750 ms → settings.json updated with logical coords.
3. Relaunch → window restored at saved position (clamped on-screen).
4. Right-click widget → menu (Exit) → clean exit 0 + position flushed.
5. Corrupt settings → launch → dialog → Reset → .bak + defaults.
