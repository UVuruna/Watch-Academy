# app/

The Qt application shell: window, input, tray, timing and persistence.
Knows nothing about astronomy ([Core (folder)](../core/___core.md)) or
skin internals ([Skins (folder)](../skins/___skins.md)) — it consumes
their outputs through the render compositor.

## Files

| File | Tier | One line |
|------|------|----------|
| `__init__.py` | Trivial | bare module docstring — no re-exports |
| `controller.py` | Algorithmic | composition root for ONE watch — state, wiring, the tick, the translation overlay; the other five responsibilities are the mixins below (WA-R14, off the ratchet) — [about](__about/controller.md) · [flow](__flow/controller.md) |
| `controller_shortcuts.py` | Standard | mixin — every keyboard shortcut the watch answers, and the flashes they raise — [about](__about/controller_shortcuts.md) |
| `controller_menu.py` | Algorithmic | mixin — the right-click / tray menu: builds it, keeps its checks and gray states in step — [about](__about/controller_menu.md) · [flow](__flow/controller_menu.md) |
| `controller_display.py` | Standard | mixin — one visual choice in, a rebuilt skin out; the single `Settings` writer menu, window and shortcuts share — [about](__about/controller_display.md) |
| `controller_dialogs.py` | Standard | mixin — the watch's own windows: opens, re-raises, forgets, and builds each one's payload — [about](__about/controller_dialogs.md) |
| `controller_simulation.py` | Algorithmic | mixin — the moment the watch shows when it is not now: jump arithmetic, simulation lifecycle, the Time Travel dialog — [about](__about/controller_simulation.md) · [flow](__flow/controller_simulation.md) |
| `skin_builder.py` | Algorithmic | THE SKIN BUILDER — settings + location in, a `SkinDefinition` out — [about](__about/skin_builder.md) · [flow](__flow/skin_builder.md) |
| `watch_manager.py` | Standard | process-wide `AppController` — builds/tears down the watch roster, arms the shared warm — [about](__about/watch_manager.md) |
| `observatory/` | (package) | the statistics sibling of the Encyclopedia — 5 interactive QPainter charts, split into charts / panels / dialog — [folder](observatory/___observatory.md) |
| `widget.py` | Algorithmic | the frameless, transparent dial window — [about](__about/widget.md) · [flow](__flow/widget.md) |
| `settings_store.py` | Algorithmic | the `Settings` data table + its atomic JSON store — [about](__about/settings_store.md) · [flow](__flow/settings_store.md) |
| `settings_ring.py` | Standard | ring-name resolution + custom-ring-card normalization, split out of `settings_store.py` (THE STRUCTURE LAW) — [about](__about/settings_ring.md) |
| `settings_fields.py` | Standard | the per-field validators + stored-data migrations, split out of `settings_store.py` (THE STRUCTURE LAW) — [about](__about/settings_fields.md) |
| `time_travel.py` | Algorithmic | the scenario-tester dialog + its Quick Jump rows — [about](__about/time_travel.md) · [flow](__flow/time_travel.md) |
| `rebuild.py` | Standard | the ONE door a live rebuild throws a widget away through — `hide()` before `setParent(None)`, because an orphan QWidget IS a top-level window (owner bug 2026-08-15/16) — [about](__about/rebuild.md) |
| `slot_descriptor.py` | Standard | the shared `SlotDescriptor` dataclass the controller builds and the Watch Face window reads — [about](__about/slot_descriptor.md) |
| `weekday_theme_grid.py` | Algorithmic | the shared image+name gallery builders (the weekday-body gallery, the Calendar mount gallery) the Watch Face window uses — [about](__about/weekday_theme_grid.md) · [flow](__flow/weekday_theme_grid.md) |
| `legend_popup.py` | Algorithmic | the scrollable hover window replacing QToolTip — [about](__about/legend_popup.md) · [flow](__flow/legend_popup.md) |
| `fast_travel_flash.py` | Algorithmic | the transient icon+text toast for Ctrl+[ / Ctrl+] — [about](__about/fast_travel_flash.md) · [flow](__flow/fast_travel_flash.md) |
| `report.py` | Algorithmic | the hidden efficiency report — table + bar chart + sparkline — [about](__about/report.md) · [flow](__flow/report.md) |
| `shortcuts_window.py` | Standard | R-37 read-only Shortcuts reference table, enumerated off `config.shortcuts.SHORTCUTS` — [about](__about/shortcuts_window.md) |
| `section_host.py` | Algorithmic | the ONE nav-list-beside-a-page-stack — measured sidebar, per-page scroll, computed minimum; the Watch Face window and the Settings dialog both build theirs with it — [about](__about/section_host.md) · [flow](__flow/section_host.md) |
| `dialog_base.py` | Standard | `AcademyDialog` — the overlay, the `tr`, the title and the stay-on-top flag every top-level window shares — [about](__about/dialog_base.md) |
| `theme.py` | Algorithmic | the shared dark QSS + the one dialog-opening-size algorithm — [about](__about/theme.md) · [flow](__flow/theme.md) |
| `native.py` | Algorithmic | the only module touching user32/kernel32 — hit test, click-through, the keyboard hook — [about](__about/native.md) · [flow](__flow/native.md) |
| `scheduler.py` | Algorithmic | the self-correcting minute/second tick timer — [about](__about/scheduler.md) · [flow](__flow/scheduler.md) |
| `warm.py` | Algorithmic | the one background warm, four ordered phases — [about](__about/warm.md) · [flow](__flow/warm.md) |
| `encyclopedia_warm.py` | Algorithmic | pre-materializes every derived Encyclopedia image — [about](__about/encyclopedia_warm.md) · [flow](__flow/encyclopedia_warm.md) |
| `tray.py` | Standard | the tray icon/tooltip/menu wrapper + both icon shapes — [about](__about/tray.md) |
| `ui_style.py` | Standard | the shared vivid gradient-pill button styling — [about](__about/ui_style.md) |
| `encyclopedia/` | — | the article browser, on three levels — [Encyclopedia (subfolder)](encyclopedia/___encyclopedia.md) |
| `settings_dialog/` | — | the M6 settings window, one mixin per nav section — [Settings Dialog (subfolder)](settings_dialog/___settings_dialog.md) |
| `watch_face/` | — | the consolidated Watch Face window (Phase ①+②) — [Watch Face (subfolder)](watch_face/___watch_face.md) |

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
  `%APPDATA%/Watch Academy/crash.log` under a timestamped session header.
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
  Controller](__about/controller.md), [Observatory](observatory/___observatory.md))
  — both carry a `tests/test_structure_law.py` ratchet entry; a split is
  owed, not yet done (Rule #20).
