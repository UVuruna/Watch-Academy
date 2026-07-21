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
(`GREGORIAN_CYCLE_YEARS`, `PROXY_WINDOW_FIRST`). THE METAL-SPLIT OPTION
(TASK 3, MASON/ICONS round, owner verdicts 2026-07-19, third batch):
`RING_TWO_METALS_DEFAULT` — the per-preset default for the Design ▸
Ring ▸ "Two metals" toggle (Mason True, every other eligible preset
False, `app.controller._ring_two_metals` resolves it against the
user's own stored `Settings.ring_two_metals` choice first). THE NINTH
TABLE AND ITS SOLAR WINDOWS (round R3b item 3): `WEEKDAY_THEME_NINTHS`
— the (display name, plate path) per weekday theme, extracted out of
`app.encyclopedia`'s own ninths loop so [Layers](../render/layers.md)
and [Compositor](../render/compositor.md) can read the SAME table for
the CENTER seat's solar-window face law (Rule #5) — and
`CENTER_NOON_WINDOW_HOURS` / `CENTER_MIDNIGHT_WINDOW_HOURS` /
`CENTER_MIDNIGHT_WINDOW_HOURS_NO_NINTH`, the tunable hour-widths of
those windows around solar noon/midnight. **R5 MENU REWORK**:
`POINTER_PALETTE_LABELS` — the RAW English wheel-pair label per
pointer (Court/Family, Temperaments/Elements, Walks of Life/Ages,
Warm/Cool, Zodiac/Almanac, a `"default"` Paint/Light fallback),
extracted so `app.controller._build_menu`'s translated copy and
`app.controller.watch_title`'s UNTRANSLATED name reading both draw
from the ONE table (Rule #5); `SLOT_COMPLICATION_TITLES` — the four
Complication mode display titles (Digital Time/Date/Day length/
Seconds), read by [Slot Theme](../app/slot_theme.md)'s own tab.

### `defaults.py` — Developer Tunables
Window sizing (`dial_window_margin_fraction(skin)` is COMPUTED LIVE —
owner slike 1–3, 2026-07-17 — as the larger of the ring-letter overhang
(at the letter-scale slider), the event-glow extent (the larger of the
Earth/Moon markers at their user scale, relocated to the ring band,
hover-enlarged) and, when the active preset carries one (TASK 1, owner
"može radi" 2026-07-19), the outer MOTTO ARC's own outer reach
(`RING_MOTTO_RADIUS_FRACTION`/`_STEP`/`_SIZE` — a no-op term for every
preset without a `motto`), so neither the letters nor a bottom-of-ring
halo nor the motto text can be square-cut and any size/hover/letter
slider re-sizes the window to fit exactly), `RING_MOTTO_LETTER_STEP_DEG`
(ANNUIT WORD-GAP round, owner correction 2026-07-19, third batch: the
tight per-character step `core.motto._tight_two_pin_angles` advances a
2-pin motto at, derived from NOVUS ORDO SECLORUM's own pin geometry —
60°/9 chars), the Time Travel
coverage-warning color and the
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
(ROADMAP 15h item 10, owner reminder 2026-07-19; fix round E,
2026-07-19: the emoji became ⚪/⚫, never 🔆/🌑): `pole_is_light(pole,
on_date)` / `pole_emoji(pole, on_date)` — a simple CALENDAR date-window
check (`POLE_LIGHT_WINDOW`, no astronomy call) the Quick Jump ▸
Location submenu reads for the North/South Pole row's own light/dark
state; `GREENWICH_EMOJI` is the sealed 🌐 pick for the Greenwich row.
**UI ICON CHROME** (TASK 4, MASON/ICONS round, owner icon list
2026-07-19 approvals): `ICON_DIR`/`ICON_FILES`/`icon_path(name)` — the
four owner-approved reusable menu/hover glyphs (light/dark pole state,
solar/lunar eclipse), copied from his `UV/icons/` staging into
`assets/icons/` under canonical names; `icon_path` is graceful-absent
(None when the file has not landed, Rule #1) so every consumer keeps
its OWN documented emoji fallback. `pole_icon_name(pole, on_date)`
mirrors `pole_emoji`'s own light/dark split so the two never disagree.
These are UI CHROME, not ART — the one-image-one-place law (owner
2026-07-19) applies to the dial's own ART only; a UI icon may
legitimately answer in more than one menu spot.
**SCALE ROTATION** (owner decree 2026-07-19/20, CANON.md
one-image-one-place amendment — Judas–Lucifer is a MAIN theme, kept
"na smenu"): `ROTATION_DAYS` (THE UNIVERSAL ROTATION CONVENTION's
shared cadence — generalized 2026-07-20, see
[Assets (folder)](../assets/___assets.md)), `SCALE_ART_STEMS` (the
known filename stems per figure — the owner's naming stayed irregular
across batches) and `scale_variant_file(figure, on_date)` — DISCOVERS
every version actually on disk for the active source, in both
`SCALE_ART_DIR` and its `glass/` register, tolerant of `_v`/`_v1`/
`_v2`/`_v3` suffixes, and rotates by the date's proleptic ordinal.
Sole consumer: the [Encyclopedia](../app/encyclopedia.md)'s "The Two
Triangles" duality topic.
**R5 MENU REWORK (owner "OSMISLITI ŠTA SVE" — design the full
shortcut map):** `SHORTCUTS` — the ONE keyboard-shortcut table
(action_id, `Qt.Key` NAME, `Qt.KeyboardModifier` NAME tuple,
description; config stays Qt-free, [Clock Widget](../app/widget.md)
resolves it once at import time like `HOVER_BYPASS_MODIFIER` already
does) and `shortcut_display(action_id)` (the "Ctrl+R" menu-column
label, pure/Qt-free). Every entry carries a modifier by construction
so it can never feed `HIDDEN_MODE_SECRET`'s printable-no-modifier
buffer. Three new `ICON_FILES` entries (`north_pole`/`south_pole`/
`compass`) for the [Time Travel](../app/time_travel.md) Quick Jump
rows' pole/Greenwich icons, `TIME_TRAVEL_ROW_ICON_PX`/
`TIME_TRAVEL_ARROW_BUTTON_PX` (the row icon/arrow-button pixel sizes),
and `weekday_theme_body_art(theme, body)` — one theme's representative
plate (moved here FROM `app.encyclopedia._theme_body_art`, Rule #5,
since [Pointer Theme](../app/pointer_theme.md)/[Slot Theme](../app/slot_theme.md)
need the SAME resolution for their picker-grid previews).

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
