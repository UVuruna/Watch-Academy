# app/

The Qt application shell: window, input, tray, timing and persistence.
Knows nothing about astronomy ([Core (folder)](../core/___core.md)) or
skin internals ([Skins (folder)](../skins/___skins.md)) — it consumes
their outputs through the render compositor.

## Files

| File | Tier | One line |
|------|------|----------|
| `__init__.py` | Trivial | bare module docstring — no re-exports |
| `controller.py` | Algorithmic | composition root for ONE watch — skin building, Qt shell, dialogs, shortcuts, time travel, tick plumbing (documented god-file, ratchet entry) — [about](__about/controller.md) · [flow](__flow/controller.md) |
| `watch_manager.py` | Standard | process-wide `AppController` — builds/tears down the watch roster, arms the shared warm — [about](__about/watch_manager.md) |
| `observatory.py` | Algorithmic | the statistics sibling of the Encyclopedia — 5 interactive QPainter charts (documented god-file, ratchet entry) — [about](__about/observatory.md) · [flow](__flow/observatory.md) |
| `widget.py` | Algorithmic | the frameless, transparent dial window — [about](__about/widget.md) · [flow](__flow/widget.md) |
| `settings_store.py` | Algorithmic | the `Settings` data table + its atomic JSON store — [about](__about/settings_store.md) · [flow](__flow/settings_store.md) |
| `time_travel.py` | Algorithmic | the scenario-tester dialog + its Quick Jump rows — [about](__about/time_travel.md) · [flow](__flow/time_travel.md) |
| `design_window.py` | Algorithmic | the tabbed Pointer/Ring/Umbra/Complications/Hands/Earth/Size window — [about](__about/design_window.md) · [flow](__flow/design_window.md) |
| `pointer_theme.py` | Algorithmic | the 1st Slot weekday-body (+ Calendar mount) picker window — [about](__about/pointer_theme.md) · [flow](__flow/pointer_theme.md) |
| `slot_theme.py` | Algorithmic | the three-medal per-slot picker window — [about](__about/slot_theme.md) · [flow](__flow/slot_theme.md) |
| `weekday_theme_grid.py` | Algorithmic | the shared image+name gallery builders both mini windows use — [about](__about/weekday_theme_grid.md) · [flow](__flow/weekday_theme_grid.md) |
| `legend_popup.py` | Algorithmic | the scrollable hover window replacing QToolTip — [about](__about/legend_popup.md) · [flow](__flow/legend_popup.md) |
| `fast_travel_flash.py` | Algorithmic | the transient icon+text toast for Ctrl+[ / Ctrl+] — [about](__about/fast_travel_flash.md) · [flow](__flow/fast_travel_flash.md) |
| `report.py` | Algorithmic | the hidden efficiency report — table + bar chart + sparkline — [about](__about/report.md) · [flow](__flow/report.md) |
| `theme.py` | Algorithmic | the shared dark QSS + the one dialog-opening-size algorithm — [about](__about/theme.md) · [flow](__flow/theme.md) |
| `native.py` | Algorithmic | the only module touching user32/kernel32 — hit test, click-through, the keyboard hook — [about](__about/native.md) · [flow](__flow/native.md) |
| `scheduler.py` | Algorithmic | the self-correcting minute/second tick timer — [about](__about/scheduler.md) · [flow](__flow/scheduler.md) |
| `warm.py` | Algorithmic | the one background warm, four ordered phases — [about](__about/warm.md) · [flow](__flow/warm.md) |
| `encyclopedia_warm.py` | Algorithmic | pre-materializes every derived Encyclopedia image — [about](__about/encyclopedia_warm.md) · [flow](__flow/encyclopedia_warm.md) |
| `tray.py` | Standard | the tray icon/tooltip/menu wrapper + both icon shapes — [about](__about/tray.md) |
| `ui_style.py` | Standard | the shared vivid gradient-pill button styling — [about](__about/ui_style.md) |
| `encyclopedia/` | — | the article browser, on three levels — [Encyclopedia (subfolder)](encyclopedia/___encyclopedia.md) |
| `settings_dialog/` | — | the M6 settings window, one mixin per nav section — [Settings Dialog (subfolder)](settings_dialog/___settings_dialog.md) |

## Connections

### Uses
- [Config (folder)](../config/___config.md) — constants, defaults, paths
- [Core (folder)](../core/___core.md) — day/tick state, deep time
- [Data (folder)](../data/___data.md) — seasons, moon phases, symbolism,
  observatory series, translations
- [Render (folder)](../render/___render.md) — the compositor and every
  asset/recolor helper that paints or derives an image
- [Skins (folder)](../skins/___skins.md) — `SkinDefinition`, hand/ring specs

### Used by
- `main.py` — creates the [Watch Manager](__about/watch_manager.md) and
  runs the Qt event loop

## Design Decisions
- **Crash forensics:** `main.py` installs permanent crash logging at
  startup — `faulthandler` (native fatal-error dumps) plus a
  `sys.excepthook` (unhandled Python tracebacks), both appending to
  `%APPDATA%/DOMY Watch/crash.log` under a timestamped session header.
  It only ADDS a trace; the original excepthook still runs.
- **All window flags are set before the first `show()`** — changing
  them later re-parents and hides the window on Windows.
- **Win+D on Windows 11 24H2 (verified empirically):** the window
  receives NO events — the OS raises the desktop layer above everything
  (even TOPMOST cannot pierce it) and un-covers the widget when Show
  Desktop mode ends. The spontaneous-hide watchdog in [Clock
  Widget](__about/widget.md) covers other shell actions; staying visible
  DURING Show Desktop would require an optional WorkerW glue mode (not
  built).
- **One `QMenu` is shared** by the tray icon and the widget's own
  right-click popup.
- **Two files remain documented god-files** ([Watch
  Controller](__about/controller.md), [Observatory](__about/observatory.md))
  — both carry a `tests/test_structure_law.py` ratchet entry; a split is
  owed, not yet done (Rule #20).
