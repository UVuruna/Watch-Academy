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
cross 4 / octa 8 / trio 3 arms, aurora and calendar armless; display
names Prism / Seasons / Compass / Trinity / Aurora / Calendar; the
Calendar's twelve 2-hour wedges via `CALENDAR_WEDGES`/`CALENDAR_WEDGE_DEG`
and its `CALENDAR_LIGHTING_MODES` — hour/year, owner 2026-07-16) with
their weekday slot layouts (slots rotate
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
year-anchor angles, and the moon phase → fraction mapping. The metal-
capable weekday themes (`METAL_THEMES`) and their four looks
(`THEME_METALS`: gold/bronze/silver/colored) live here too, with a
per-theme override (`THEME_METALS_OVERRIDE` + the `theme_metals(theme)`
lookup, owner 2026-07-18) for themes whose art has no `colored/`
subfolder — `planets_art` (the Planets "Art" medallion look) offers only
gold/bronze/silver; every menu/dialog/validation call site reads the
allowed set through this one function rather than the flat tuple. The bundled
database coverage is NO LONGER hardcoded here (owner 2026-07-16, Rule
#4): the repositories' `coverage()` reads the year span from the data.
DEEP TIME (Session 16, owner 2026-07-17): the pack filename, the era
notations with their labels (owner amendment: bce_ce/bc_ad only — Anno
Lucis always accompanies the official year; `ANNO_LUCIS_OFFSET` 4079,
sealed), the THIRD-calendar tables (AUC/Byzantine/Hebrew offsets on
the astronomical axis, the AH label, the epoch tooltip notes) and the
400-year Gregorian proxy cycle with its canonical window
(`GREGORIAN_CYCLE_YEARS`, `PROXY_WINDOW_FIRST`).

### `defaults.py` — Developer Tunables
Window sizing (`dial_window_margin_fraction(skin)` is COMPUTED LIVE —
owner slike 1–3, 2026-07-17 — as the larger of the ring-letter overhang
(at the letter-scale slider) and the event-glow extent (the larger of the
Earth/Moon markers at their user scale, relocated to the ring band,
hover-enlarged), so neither the letters nor a bottom-of-ring halo can be
square-cut and any size/hover/letter slider re-sizes the window to fit
exactly), the Time Travel coverage-warning color and the
Deep Time advertised span (`DEEP_TIME_YEAR_RANGE`), the spontaneous-hide
watchdog delay, tick scheduling
(epsilon, clock-jump threshold), `DEFAULT_CITY` (Belgrade preset until the
M6 picker), settings schema version and write debounce, the procedural
render geometry block (tick/font sizes with legibility floors, pen widths,
marker borders), `PALETTE_PRESETS` (the Star+Aura/wedge palettes
measured from the owner's art: hexa/octa paint+light, cross/trio
single, aurora bands, and the Calendar's two twelve-hue wheels —
paint = Zodiac, light = Almanac, owner 2026-07-16), the Calendar wedge
opacity + lit delta and the Almanac day-arrow geometry
(`CALENDAR_WEDGE_ALPHA`, `CALENDAR_WEDGE_LIT_DELTA`, `CALENDAR_ARROW_*`),
the Umbra contrast spans, the octa slot text width fraction, the event glow
rendering (owner rework 2026-07-16: the ring-band relocation radius, the
golden Sun / silver Moon colors, the alpha stops, the halo scale and the
larger-marker scale that sizes the window margin), tray
icon geometry, the
PANTHEON roster tables (`WEEKDAY_PANTHEON`: per theme the candidate
plate paths, seated names, article set and the Sunday dual) with
`pantheon_seat(theme, body)` — the shared safety-law resolver (first
EXISTING candidate plate wins with the pantheon identity; None keeps
the planetary bundle whole) consumed by the classic unit, the seated
slots and the hovers alike — and
`DEFAULT_SKIN` — a fully typed [Manifest](../skins/manifest.md)
`SkinDefinition` instance that is serialized verbatim to
`assets/skins/domy/skin.json` (re-serialize after editing it). The
hidden Report chart tokens (`REPORT_*`) and the OBSERVATORY chart
tokens (`OBSERVATORY_*`, Session 17: the bundle filenames, the fixed
per-series canon colors — season cross-wheel hues, light/dark gold vs
slate — the surface/grid/crosshair palette, the day-length sample step
and the eclipse-window size) live here too. The POLE emoji windows
(ROADMAP 15h item 10, owner reminder 2026-07-19): `pole_is_light(pole,
on_date)` / `pole_emoji(pole, on_date)` — a simple CALENDAR date-window
check (`POLE_LIGHT_WINDOW`, no astronomy call) the Quick Jump ▸
Location submenu reads to swap the North/South Pole row's season emoji
(🔆/🌑); `GREENWICH_EMOJI` is the sealed 🌐 pick for the Greenwich row.

### `archetypes.py` — The Archetype Mode
THE ARCHETYPE MODE's one configuration home (owner sealed package
2026-07-16): the (pointer, palette_style) → archetype grid — seven
archetypes over four pointers, none on Aurora/Calendar — the
per-archetype figure tables (arm angle, stained-glass drop path, the
two-row names, article entity, encyclopedia target), the center table
(Eye / Hearth / Seal / Union / Throne — Compass none), the article-set
names Session 6 fills, the Ages' two image registers and the render
tunables (figure heights, name sizing, the 1×1-placeholder threshold,
the Earth day-label geometry, the pending line). See
[Archetypes](archetypes.md).

### `winapi.py` — Win32 Literals
The only sanctioned home for Win32 API constants (documented enum-exception
to Rule #4). Consumed by `app/native.py` from M4 — the click-through /
NCHITTEST / power literals, plus the `SetWindowPos` topmost set
(`HWND_TOPMOST`, `SWP_NOMOVE`/`SWP_NOSIZE`/`SWP_NOACTIVATE`) the "top"
z-mode uses to re-assert TRUE always-on-top (owner 2026-07-17, ROADMAP 15e).

### `profiling.py` — Profiling
The `@timed` / `measure()` execution-time statistics store behind the
hidden Report (owner 2026-07-15) — cumulative since the installation,
flushed by the controller. See [Profiling](profiling.md).

### `paths.py` — Frozen-Safe Paths
Resolves `Database/`, `assets/skins/` and `%APPDATA%/DOMY Watch/` from
`Path(__file__)` / `sys._MEIPASS` — never from the working directory, so a
PyInstaller `--onedir` bundle finds its data; `deep_time_path()` names
the optional Deep Time pack the controller detects at startup
(Session 16). Also hosts the ART SOURCE
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
