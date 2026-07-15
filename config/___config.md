# config/

The single home for every constant and tunable in the project (monorepo
Rule #4). No other module may contain a numeric literal that is not a loop
index or an enum value. Read-only at runtime — user-changeable state lives in
the settings file owned by [Settings Store](../app/settings_store.md).

## Files

### `constants.py` — Product Invariants
Values that define what DOMY Watch is and never change: app identity, the
24h dial convention (noon at top, clockwise, 180° offset), time constants,
the weekday → celestial body mapping, the pointer variants (hexa 6 /
cross 4 / octa 8 / trio 3 arms; display names Prism / Seasons /
Compass / Trinity) with their weekday slot layouts (slots rotate
WITH the star; shared slots resolve by the next-upcoming-day rule
over `SUNDAY_FIRST_INDEX`; the octa bottom arm is reserved for the info
slot with its `OCTA_SLOT_MODES`; the trio pairs Faith 12h =
Jupiter+Saturn, Love 20h = Venus+Mars, Hope 4h = Moon+Mercury with the
Sun centered — each arm tip is the CENTER of its hue, thirds
8-16 / 16-24 / 0-8), the star arm half-angles (the cross
borrows the octa arm shape; the trio is half of hexa), the Umbra forms (fine 30 / coarse 24
sections — single lightest/darkest centered on noon/midnight — or the
continuous gradient) and contrast variant names (full/half/light/dark), the
palette style names, the tropical zodiac table (signs are
30° arcs of the year wheel — Cancer's first point IS the summer
solstice), the Chinese zodiac cycle (animals, elements, the CNY new-
moon window), the octa slot modes with their art folders, the Earth
style names, the season/moon glow windows (±12 h / ±6 h) and event names,
sun thresholds (civil depression, horizon/twilight elevations), the six
year-anchor angles, moon phase → fraction mapping, and the bundled
database coverage ranges.

### `defaults.py` — Developer Tunables
Window sizing, the spontaneous-hide watchdog delay, tick scheduling
(epsilon, clock-jump threshold), `DEFAULT_CITY` (Belgrade preset until the
M6 picker), settings schema version and write debounce, the procedural
render geometry block (tick/font sizes with legibility floors, pen widths,
marker borders), `PALETTE_PRESETS` (the five Star+Aura palettes measured
from the owner's art: hexa/octa paint+light, cross seasons), the Umbra
contrast spans, the octa slot text width fraction, the event glow
rendering (white core/warm mid/halo scale), tray icon geometry, the
PANTHEON roster tables (`WEEKDAY_PANTHEON`: per theme the candidate
plate paths, seated names, article set and the Sunday dual) with
`pantheon_seat(theme, body)` — the shared safety-law resolver (first
EXISTING candidate plate wins with the pantheon identity; None keeps
the planetary bundle whole) consumed by the classic unit, the seated
slots and the hovers alike — and
`DEFAULT_SKIN` — a fully typed [Manifest](../skins/manifest.md)
`SkinDefinition` instance that is serialized verbatim to
`assets/skins/domy/skin.json` (re-serialize after editing it).

### `winapi.py` — Win32 Literals
The only sanctioned home for Win32 API constants (documented enum-exception
to Rule #4). Consumed by `app/native.py` from M4.

### `profiling.py` — Profiling
The `@timed` / `measure()` execution-time statistics store behind the
hidden Report (owner 2026-07-15) — cumulative since the installation,
flushed by the controller. See [Profiling](profiling.md).

### `paths.py` — Frozen-Safe Paths
Resolves `Database/`, `assets/skins/` and `%APPDATA%/DOMY Watch/` from
`Path(__file__)` / `sys._MEIPASS` — never from the working directory, so a
PyInstaller `--onedir` bundle finds its data. Also hosts the ART SOURCE
resolver (owner 2026-07-14: the Gemini and ChatGPT generations coexist
under `assets/<root>/<source>/`): `set_art_source(source)` switches the
active source and `art_file(path)` maps a canonical source-less path
into it, falling back to the other source where the file is missing —
every disk boundary (asset cache, hover images, Encyclopedia, manifest
validation) resolves through it.

## Connections

### Used by
- [App (folder)](../app/___app.md) — window/tray/settings read all four files
- Core, data, skins, render (M2+) — invariants and paths

## Design Decisions
- Python modules, not JSON: constants need typing, expressions (e.g. `sqrt`)
  and direct imports.
- Three tiers by ownership: developer config here, declarative skin config in
  `skin.json` per skin (M5), user runtime state in `settings.json`.
