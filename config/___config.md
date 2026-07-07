# config/

The single home for every constant and tunable in the project (monorepo
Rule #4). No other module may contain a numeric literal that is not a loop
index or an enum value. Read-only at runtime — user-changeable state lives in
the settings file owned by [Settings Store](../app/settings_store.md).

## Files

### `constants.py` — Product Invariants
Values that define what DOMY Watch is and never change: app identity, the
24h dial convention (noon at top, clockwise, 180° offset), time constants,
the weekday → celestial body mapping and the hexagram diamond slot angles
(the slots rotate WITH the hexagram), sun thresholds (civil depression,
horizon/twilight elevations), the six year-anchor angles, moon phase →
fraction mapping, and the bundled database coverage ranges.

### `defaults.py` — Developer Tunables
Window sizing, the spontaneous-hide watchdog delay, tick scheduling
(epsilon, clock-jump threshold), `DEFAULT_CITY` (Belgrade preset until the
M6 picker), settings schema version and write debounce, the procedural
render geometry block (tick/font sizes with legibility floors, pen widths,
marker borders), tray icon geometry, and `DEFAULT_SKIN` — a fully typed
[Manifest](../skins/manifest.md) `SkinDefinition` instance that drives all
rendering until it is serialized to `assets/skins/domy/skin.json` in M5.

### `winapi.py` — Win32 Literals
The only sanctioned home for Win32 API constants (documented enum-exception
to Rule #4). Consumed by `app/native.py` from M4.

### `paths.py` — Frozen-Safe Paths
Resolves `Database/`, `assets/skins/` and `%APPDATA%/DOMY Watch/` from
`Path(__file__)` / `sys._MEIPASS` — never from the working directory, so a
PyInstaller `--onedir` bundle finds its data.

## Connections

### Used by
- [App (folder)](../app/___app.md) — window/tray/settings read all four files
- Core, data, skins, render (M2+) — invariants and paths

## Design Decisions
- Python modules, not JSON: constants need typing, expressions (e.g. `sqrt`)
  and direct imports.
- Three tiers by ownership: developer config here, declarative skin config in
  `skin.json` per skin (M5), user runtime state in `settings.json`.
