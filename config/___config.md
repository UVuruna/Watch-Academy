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
Calendar's twelve 2-hour wedges via `CALENDAR_WEDGES`/`CALENDAR_WEDGE_DEG`,
its `CALENDAR_LIGHTING_MODES` (hour/year, owner 2026-07-16) and its
`CALENDAR_MOUNT_MODES` (off/zodiac/months/chinese, the DESIGN ZODIAC
law's 12-set mount, R9a round 2026-07-21, "chinese" added owner R12)
with
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
those windows around solar noon/midnight. **THE CONTINENTS theme**
(owner-sealed matrix 2026-07-21, round R7a): registered across the
standard weekday tables (`WEEKDAY_THEMES`, `_TITLES`, `_NAMES`, `_DIRS`
= `"../earth"`, `_FILES`, `_DUAL_NAMES`/`_FILES` = the poles, `_ARTICLES`
= `"continents"`, `_BLURBS`, `_NINTHS` = Zealandia) PLUS its own
`CONTINENTS_REGIONS` (body → continent), `earth_face_art` /
`continents_body_art` / `continents_dual_art` (the live earth_style ×
day/night resolvers), `CONTINENTS_TITLE_IMAGE` (the world map), and
`WEEKDAY_THEME_NINTH_EASTER_EGG` (Pangea, the easter-egg face). Its
bodies reuse the dial's own `assets/earth/` faces (owner exception to
one-image-one-place) and its Ninth switches Zealandia/Pangea by
[Continents](../core/continents.md)'s law. **THE BLUE MOON LAW**
(owner-sealed 2026-07-22, R12): `THIRTEENTHS` — key ("ophiuchus"/
"sol"/"modrenik"/"chinese") → (display name, encyclopedia family,
encyclopedia entry name), the SAME two-level shape `WEEKDAY_THEME_NINTHS`
uses, read by both the dial (`render.layers.thirteenth_plate`) and its
hover; `OPHIUCHUS_WINDOW`/`SOL_WINDOW` (year-agnostic (month, day)
bounds) and `MODRENIK_WINDOW_HALF_DAYS` (14, computed from the REAL
December solstice instant, never a fixed date) — each 13th's own short
window; `CHINESE_MONTH_BRANCH_ANIMALS` (Gregorian month → the
traditional solar-term branch animal — Feb Tiger … Dec Rat, the
December-solstice month — fixing ONE animal per Gregorian month for
the "chinese" calendar mount, `render.layers.calendar_mount_entries`).
The trigger/window/precedence law itself lives in
[Blue Moon](../core/blue_moon.md); pinned by `tests/test_blue_moon.py`.
**R5 MENU REWORK**:
`POINTER_PALETTE_LABELS` — the RAW English wheel-pair label per
pointer (Court/Family, Temperaments/Elements, Walks of Life/Ages,
Warm/Cool, Zodiac/Almanac, a `"default"` Paint/Light fallback),
extracted so `app.controller._build_menu`'s translated copy and
`app.controller.watch_title`'s UNTRANSLATED name reading both draw
from the ONE table (Rule #5); `SLOT_COMPLICATION_TITLES` — the four
Complication mode display titles (Digital Time/Date/Day length/
Seconds), read by [Slot Theme](../app/slot_theme.md)'s own tab.
**THE METAL SHADES (R8a round, owner spec 2026-07-21 night):**
`METAL_SHADE_NAMES` (metal → its shade-name tuple, gold five/bronze
three/silver three), `METAL_SHADE_DEFAULT` (the per-metal install
default) and `METAL_SHADE_TITLES` (shade → its Settings-combo display
title) — the validation/enumeration surface; the numeric
(hue, saturation, reference value) recipe per shade lives in
`defaults.METAL_SHADES` (see that file's own entry, and
[Assets](../render/assets.md) for the full algorithm).

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
the Calendar-pointer 12-SET MOUNT (owner-sealed R7b 2026-07-21
registration, R9a 2026-07-21 render + picker):
`SLAVIC_MONTHS` (the twelve Croatian months as (croatian, gloss, ascii
stem, gregorian-month) rows — the first mount-set beyond the zodiac
signs / Chinese animals the pointer already reads), `MONTHS_ART_DIR`
(the canonical **sourceless** `assets/months/` root, OUTSIDE
`ART_SOURCED_ROOTS` — the subdial precedent; graceful-absent, a future
prompt sheet), `CALENDAR_MOUNT_RADIUS_FRACTION` (0.65, the DESIGN
ZODIAC law's 60-70% mount radius), `CALENDAR_MOUNT_MARK_SCALE` (the
mark's own drawn height), `CALENDAR_MOUNT_ALPHA`/
`CALENDAR_MOUNT_LIT_DELTA` (the current-mark emphasis, reaching exactly
1.0) and `CALENDAR_MOUNT_DIMMED_ALPHA` (0.20, owner R12 — The Cat's
dimming law, below the resting alpha but never zero) —
`constants.CALENDAR_MOUNT_MODES` ("off"/"zodiac"/"months"/"chinese",
Settings-validated) is the mode enum; the render itself
(`render.layers._draw_calendar_mount`/`calendar_mount_entries`/
`calendar_mount_angle`, the Design ▸ Pointer tab's mount row) is covered
in [Layers](../render/layers.md)'s own Calendar Pointer section (see
[Encyclopedia](../app/encyclopedia.md) for the Slavic Months topic),
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
**THE METAL SHADES (R8a round, owner spec 2026-07-21 night — the redo
after an adaptive percentile-stretch attempt, `GOLD_RAMP_HUE_DEG` /
`GOLD_RAMP_SAT_VAL_STEPS` / `ADAPTIVE_METAL_PERCENTILES` /
`ADAPTIVE_METAL_RECOLOR_VERSION`, was reverted the same day it landed
for flattening every relief into a wash):** `METAL_SHADES` — per metal
(gold/bronze/silver) a table of selectable shade name →
`(hue_deg, saturation, reference_value)`; gold's five bands are sampled
directly off `UV/DESIGN/gold pallete.png` (hue flat ~44.9deg, only
saturation/reference-value step dark-amber to pale/champagne — the
bright three share reference_value 0.85 rather than the swatch's own
flat-color 1.00, tuned against real ring letters during this round's
verification so their highlights stop over-clipping), bronze ramps
around `BRONZE_LETTER_TINT`'s own hue/saturation, silver ramps at
saturation EXACTLY 0.0. `METAL_RECOLOR_GAIN_RANGE` — the ONE bounded
global gain every shade's `reference_value` is nudged toward from a
masked region's own mean (never a per-pixel remap — the lesson of the
reverted attempt). `METAL_SWAP_VERSION` — the cache-key salt
`letter_metal_file` and `metal_variant_file` fold in (alongside the
active shade name) so a shade switch or a recolor-math change never
serves a stale PNG. `METAL_SWAP_HUE_WINDOW`/`_SOFT`/`METAL_SWAP_SAT_RAMP`
(the badge medallion MASK — unchanged by this round) and
`METAL_SWAP_TARGETS` (now just the membership tuple `("gold",
"silver")` — badges never bronze-swap) stay as before. `constants.py`
holds the shade NAME tables (`METAL_SHADE_NAMES`, `METAL_SHADE_DEFAULT`,
`METAL_SHADE_TITLES`) since `defaults.py` is downstream of `paths.py`'s
validation needs. Full recipe: [Assets](../render/assets.md).
**ECLIPSE TYPE ICONS (same round):** `ECLIPSE_LUNAR_TYPE_ICON` +
`eclipse_lunar_type_icon(type_)` — the owner-APPROVED red/gold/blue
mapping (total/partial/penumbral) riding
`assets/icons/moon_eclipse_{red,gold,blue}.png`; `
ECLIPSE_SOLAR_TYPE_ICON_SOURCE` + `render.asset_variants.
eclipse_solar_type_icon(type_)` — a PROPOSED (not owner-confirmed)
shape-matched mapping over the owner's three `sun_eclipse{,1,2}.png`
variants, annular computationally tinted toward
`GLOW_ECLIPSE_SOLAR_ANNULAR_COLOR`; `ECLIPSE_TYPE_ICON_PX` — the small
inline badge size `render.compositor._eclipse_type_icon_tag` embeds
before the hover-card's eclipse line title, distinct from the big
category EMBLEM plate (`ECLIPSE_TYPE_EMBLEM`, untouched this round).
**THE CALENDAR WHEEL ICON (same round):** `CALENDAR_ICON_WEDGE_COUNT`/
`_WEDGE_COLORS`/`_RING_COLOR`/`_RING_WIDTH_FRACTION` feed `render.
asset_variants.calendar_wheel_icon_file(size)` — a Rule #19 COMPUTED 12-wedge
glyph replacing the Fast Travel Flash's plain 📅 fallback for the
Calendar theme (`app.controller._flash_fast_travel`'s one special
case — Sun/Moon keep their existing eclipse-glyph icon_keys).
**R5 MENU REWORK (owner "OSMISLITI ŠTA SVE" — design the full
shortcut map; EXTENDED by the R5b FINAL MAP round, owner spec sealed
2026-07-21):** `SHORTCUTS` — the ONE keyboard-shortcut table
(action_id, `Qt.Key` NAME, `Qt.KeyboardModifier` NAME tuple,
description; config stays Qt-free, [Clock Widget](../app/widget.md)
resolves it once at import time like `HOVER_BYPASS_MODIFIER` already
does) and `shortcut_display(action_id)` (the "Ctrl+R" menu-column
label, pure/Qt-free). Every entry carries a modifier by construction
so it can never feed `HIDDEN_MODE_SECRET`'s printable-no-modifier
buffer; an action_id may appear TWICE (`fast_travel_future`) when two
physical combos fire the same action. R5b's SEALED map: Settings moved
off Ctrl+, onto Ctrl+M (Rule #6, no leftover binding); SLOTS
(Ctrl+1/2/3 Complication, Ctrl+Alt+1/2/3 Weekday theme, per slot); FAST
TRAVEL (Ctrl+[/Ctrl+] the theme/option pickers, Ctrl+minus/Ctrl+plus —
bound to BOTH the main-row "=" and the numpad "+" — the past/future
step), config'd by `FAST_TRAVEL_THEMES` (Sun/Moon/Calendar, each a
tuple of `{id, title, jump_stem}` options — `app.controller.
_compute_jump`'s SUN/MOON branch grew an optional phase-filter suffix
this round to answer the narrower Solstice/Equinox/New/Full/Quarter
`jump_stem`s, the Calendar and Moon-Eclipse options reuse EXISTING
`_UNIT_JUMPS`/`_ECLIPSE_JUMPS` kinds verbatim); LOCATIONS (Ctrl+Up/Down
poles, Ctrl+Space Greenwich, Ctrl+Left/Right the user's custom Quick
Jump cities). `FAST_TRAVEL_FLASH_*` — geometry/timing constants for
[Fast Travel Flash](../app/fast_travel_flash.md), the small transient
overlay the theme/option pickers flash above the dial. Three new
`ICON_FILES` entries (`north_pole`/`south_pole`/`compass`) for the
[Time Travel](../app/time_travel.md) Quick Jump rows' pole/Greenwich
icons (R5b's Fast Travel flash reuses the EXISTING `eclipse_sun`/
`eclipse_moon` entries instead of adding new ones — UI chrome may
answer more than one spot), `TIME_TRAVEL_ROW_ICON_PX`/
`TIME_TRAVEL_ARROW_BUTTON_PX` (the row icon/arrow-button pixel sizes),
and `weekday_theme_body_art(theme, body, on_date=None, colored=False)`
— one theme's representative plate (moved here FROM `app.encyclopedia.
_theme_body_art`, Rule #5, since [Pointer Theme](../app/pointer_theme.md)/[Slot Theme](../app/slot_theme.md)
need the SAME resolution for their picker-grid previews; `colored`
folded in the SAME round, replacing the `theme_dir`/colored-folder
expression three render call sites used to re-type — see the WEEKDAY
ALT ROTATION note below). `on_date` (default None, every caller before
this round) opts the resolved plate into THE UNIVERSAL ROTATION
CONVENTION.

**WEEKDAY ALT ROTATION (owner 2026-07-20/21):** the universal rotation
convention (`rotating_art_file`, [Assets (folder)](../assets/___assets.md))
reaches the weekday tree — `assets/weekday/{gemini,chatgpt}/bible/
dark/alt/` (11 files each) is the first weekday register to ship
`alt/` siblings. `weekday_theme_body_art` is now the ONE weekday-body
resolver (Rule #5): `render.layers._draw_weekday_slot`, `render.
compositor`'s hover legend and `app.controller._themed_weekday_set`'s
baked bodies dict all used to re-type the SAME `theme_dir /
f"{WEEKDAY_THEME_FILES[theme][body]}.png"` expression inline —
consolidated into this one function. Rotation itself applies at THREE
render-adjacent points via the raw `rotating_art_file` utility
(mirroring exactly how the era badges and the Tetramorph figures
already opt in): `render.layers.draw_weekday_body` (the main slot +
center pass, overriding whatever `spec.bodies[body]` was BAKED to at
settings-apply time — baking never carries a date, since the skin can
outlive midnight), `_draw_weekday_slot` (the 2nd/3rd slot, resolved
fresh every paint already), and the hover legend/dual/Ninth plate in
`render.compositor` (`theme_ninth` also grew an `on_date` parameter,
same law). `render/assets.md`'s Assets doc covers the sourced-vs-
sourceless distinction this rides on top of.

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
validation) resolves through it. `settings_path(watch_index=1)` /
`discover_watch_indices()` (ADD WATCH round, owner INSTRUCTION.txt item
2, sealed 2026-07-21): the per-watch settings-file scheme — watch 1's
plain `settings.json`, watch N (2+) its own `settings.<N>.json`, and a
startup scan finding every one that already exists on disk (see
[Settings Store](../app/settings_store.md) for the full rule and
[Watch Manager](../app/watch_manager.md) for the roster it rebuilds).
Also hosts the active SUBDIAL SET (`set_subdial_set`/`subdial_set`) and,
R8a round (owner spec 2026-07-21 night), the active METAL SHADE per
metal (`set_metal_shade(metal, shade)`/`metal_shade(metal)`) — the
SAME module-global pattern as the art source: ONE global per metal
because it is a single user preference reached from many render call
sites (`render.assets.AssetCache._metal_swapped` for badges,
`render.asset_recolor.letter_metal_file` for ring letters), never threaded as
a parameter.

## Connections

### Used by
- [App (folder)](../app/___app.md) — window/tray/settings read all four files
- Core, data, skins, render (M2+) — invariants and paths

## Design Decisions
- Python modules, not JSON: constants need typing, expressions (e.g. `sqrt`)
  and direct imports.
- Three tiers by ownership: developer config here, declarative skin config in
  `skin.json` per skin (M5), user runtime state in `settings.json`.
