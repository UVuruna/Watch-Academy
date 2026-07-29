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
cross 4 / octa 8 / trio 3 / rose 8 HUES, aurora and calendar armless;
display names Prism / Quaternity / Compass / Trinity / Rose / Aurora /
Calendar, each shown with what the READER counts on the glass —
`POINTER_DIAL_COUNTS`, 3 · 4 · 6 · 7 · 8 · 12 · 24, which is NOT the
palette size for the Rose, Aurora or the Calendar; the
Calendar's twelve 2-hour wedges via `CALENDAR_WEDGES`/`CALENDAR_WEDGE_DEG`
(its `CALENDAR_LIGHTING_MODES` were DELETED with the lit-wedge feature
itself, owner decree 2026-07-29, and its mount registry lives in
`defaults.CALENDAR_MOUNTS`), and `GREGORIAN_MONTH_NAMES` (January-first,
the ONE month list every month-keyed mount rotates into seat order)
with
their weekday slot layouts (slots rotate
WITH the star; shared slots resolve by the next-upcoming-day rule
over `SUNDAY_FIRST_INDEX`; the octa's bottom arm holds the SERVANT face
of Sunday, not the info slot — a stale sentence claiming otherwise
misled a session on 2026-07-27 and died with the behavior it used to
describe, see `SOUTH_SLOT_ANGLE`'s own comment; the info slot's modes
are `OCTA_SLOT_MODES`; the trio pairs Faith 12h =
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
Ring ▸ "Two metals" toggle (Dollar True, every other eligible preset
False, `app.controller._ring_two_metals` resolves it against the
user's own stored `Settings.ring_two_metals` choice first). THE EYE
AT THE APEX (DOLLAR/EYE round, owner decree 2026-07-27):
`RING_EYE_GLYPH`/`RING_EYE_SHINE_FILE`/`RING_EYE_SHINE_DEFAULT` — the
Dollar's adaptive Eye-of-Providence glyph, its glory-of-rays master
stem and the per-preset "Shine" default (Dollar True), plus the four
explicit `👁 …` variants in `RING_LETTER_FILES`/`RING_LETTER_GROUPS`
for the custom builder; `RING_EYE_SHINE_ENLARGE` (CROSS-WORDS/SHINE
round, owner UV inbox 2026-07-27; REMEASURED same day on the
triangle's real apex/base rows after the alpha-channel measure proved
blind to the opaque glow — gpt 2.11, gem 1.67, and the shine masters
are center-padded on disk) — the per-source height multiplier that
keeps the shine master's TRIANGLE the same size as the no-light
master (the rays pad the frame), stamped into
`SkinDefinition.ring.letter_zoom` by `app.controller.build_skin`.
THE THEMATIC FINISH (ENLARGE/THEMATIC round, owner 2026-07-27):
`RING_FINISHES` grows a 4th value "thematic" — the letters wear the
ACTIVE preset's own theme color through the recolor transformer
(`RING_THEMATIC_SHADES`: DOMY cross red, PILOT cross blue, Dollar
green, The One moon indigo, Templar black; a CUSTOM ring picks its
OWN color on its card — any transformer ramp, metals included
(copper, brass, rose gold, steel, pewter, iron, …; owner: "iron,
copper... sve") — else the moon indigo); the colors are colored RAMPS
beside the metal ramps
(`recolor/presets/metals.json`, `defaults.METAL_SHADES["thematic"]`,
`METAL_SHADE_NAMES["thematic"]` — never offered in the Settings shade
pickers, the ring choice IS the choice), and outside the ring band
the thematic finish reads as gold (containment,
`app.controller.apply_display_settings`). THE NINTH
TABLE AND ITS SOLAR WINDOWS (round R3b item 3): `WEEKDAY_THEME_NINTHS`
— the (display name, plate path) per weekday theme, extracted out of
`app.encyclopedia`'s own ninths loop so [Layers](../render/layers.md)
and [Compositor](../render/compositor.md) can read the SAME table for
the CENTER seat's solar-window face law (Rule #5) — and
`CENTER_WINDOW_HOURS` (owner seal 2026-07-29: ±30 min around solar
noon AND solar midnight; the Ninth shows in both, day/night decides
Ruler/Servant outside them). **THE CONTINENTS theme**
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
[Continents](../core/continents.md)'s law. **COMPLETION WAVE I**
(Session 31, 2026-07-29): three casts whose art had sat on disk
unregistered — `age_of_heroes` (Greek Monsters), `celestial_court`
(Chinese Mythology) and `corporate` (The Corporation) — registered
across the SAME standard weekday tables plus `METAL_THEMES` (all three
are bronze primaries with a `colored/` sibling), each with its own
blurb and article set, its own Ninth (Pegasus / Buddha / The Founder),
an existing picker group (Ancient Gods, Ancient Gods, Society) and a
card of its own in `encyclopedia_tree`. The same commit DELETED
`taxonomy.THEME_KEY_RENAMES["monsters"]` and `["chinese_myth"]`: a
rename table migrates stored user settings, and neither key was ever
selectable. The law this pays is project [CLAUDE.md](../CLAUDE.md)
§THE THEME COMPLETION LAW. **COMPLETION WAVE II, WoW half** (Session
32, same day): `wow_alliance`, `wow_horde` and `wow_evil` registered
across the same tables, with `METAL_THEMES` (bronze relief masters with
`colored/` siblings), their own blurb and article sets, their Ninths
(Turalyon / Rexxar / Medivh) and the NEW "Gaming" picker group in
`WEEKDAY_MENU_GROUPS` — matching `taxonomy.WEEK_GROUPS["gaming"]` on
disk, and shared with the Cyberpunk casts when they land. THREE dial
themes but ONE Encyclopedia card: a franchise's casts hold the SAME
nine seats with different people, so `encyclopedia_tree.VARIANT_SOURCES`
merges them into `wow` with an Alliance | Horde | Evil switcher, and
`TOPIC_ALIASES` derives each cast's own Spacebar target from that
merge. None of the three needed a `THEME_KEY_RENAMES` deletion — their
folder names were always their code keys. **COMPLETION WAVE II,
Cyberpunk half** (Session 32, same day): `cp_gangs`, `cp_street` and
`cp_corpo` registered across the same tables and `METAL_THEMES`, with
their own blurb and article sets, their Ninths (NetWatch / V / Alt
Cunningham), an APPEND to the "Gaming" group rather than a new one, and
a second merged card, `cyberpunk`, with a Gangs | Street | Power
switcher. These three are the only casts in the registry whose SEATS
carry a roster: **`defaults.WEEKDAY_SEAT_ROSTERS`** declares a seat's
several named figures (canonical first) and `rotating_art_file` — the
one chokepoint every weekday consumer already calls — turns through
them by the shared date modulo, so the dial, the hover legend, the
Encyclopedia and the pickers rotate together with no app-code change of
any kind. The universal `_v2` convention pools a SECOND ARTWORK OF ONE
FIGURE; this pools DIFFERENT FIGURES ON ONE SEAT, which is the only way
twelve of that franchise's plates are reachable at all. Declared order
is the rotation order, which is what keeps the Power cast's
Throne/Mirror/Ninth triad in lockstep. A roster seat's display name in
`WEEKDAY_THEME_NAMES` lists every member, so the label can never
disagree with the plate; Sunday keeps the Ruler · Servant law and names
its rotating partners in the two face texts. **COMPLETION WAVE III**
(Session 33, same day) closes the backlog: `sw_jedi`, `sw_sith` and
`sw_dyad` registered across the same tables and `METAL_THEMES`, with
their own blurb and article sets, their Ninths (Yoda / Darth Plagueis /
The Ghosts), the NEW "Films" picker group — the second and last group
the checklist named, matching `taxonomy.WEEK_GROUPS["films"]` on disk —
and a third merged card, `starwars`, with a Jedi | Sith | Dyad
switcher. Two things are new here. First, a `WEEKDAY_SEAT_ROSTERS` seat
that holds PLACES rather than people: the Dyad's Ninth turned between
The Ghosts and Exegol by plain date rotation — SUPERSEDED, see THE
DOUBLE NINTH LAW below. Second, the same PERSON seated in two casts at
different ages — Anakin in the Sith Mirror and the Jedi Mirror, Leia
and Han in a cast each of their own — which is why the per-cast blurb
and article sets are not an over-engineering: a shared franchise set
would have had to describe one of the two ages wrongly on every hover.
None of the three needed a `THEME_KEY_RENAMES` deletion. The wiring
table of the
[Theme Staging Ledger](../research/theme_staging.md) is now EMPTY; its
second table records the plates these three casts are still owed.

**THE DOUBLE NINTH LAW** (standing law, owner decree 2026-07-29): a
theme may mount a DOUBLE NINTH only with a DEFINED alternation
mechanism, and every reader shows ONLY the currently active face, never
both. `NINTH_MECHANISMS` (theme -> mechanism name) is the registry;
`NINTH_MECHANISM_KINDS` the vocabulary a dispatch actually implements.
Three sealed mechanisms today:

- **`continents` -> `"easter_egg"`** — unchanged, `core.continents`'s
  sky trigger, now WIDENED to every principal moon phase (see
  [Continents](../core/continents.md)).
- **`sw_dyad` -> `"daynight"`** — RESOLVED 2026-07-29, superseding
  Session 33's provisional date rotation: the Ninth is a DAYLIGHT/NIGHT
  switch (the owner's words: "the duality of that theme pulling the
  actors to one of two sides"), day The Ghosts
  (`WEEKDAY_THEME_NINTHS`), night Exegol (the NEW
  `WEEKDAY_THEME_NINTH_NIGHT` table, same shape as the easter-egg one).
  `WEEKDAY_SEAT_ROSTERS["sw_dyad"]["ninth"]` is GONE — the mechanism no
  longer rides a seat roster at all.
- **`cp_corpo` -> `"term_weekly"`** — RESOLVED 2026-07-29 (scope
  extension the same session): THE WEEKLY MANDATE — the traveled date's
  ISO calendar week PARITY, not the daily ordinal, decides which half
  of the Throne/Mirror/Ninth triple rules (even week Arasaka/canonical,
  odd week NUSA) — Rule #5's "one rotation mechanism" stays true: no new
  alt table, `_pick_weekly_mandate` is a CADENCE swap inside the SAME
  `rotating_art_file` chokepoint (`constants.NINTH_MECHANISMS.get(theme)
  == "term_weekly"` is the only new branch). `cp_gangs`/`cp_street`
  stay on the plain daily cadence untouched.

`render.layers.theme_ninth`/`ninth_table_for`/`ninth_alt_active` and
`render.compositor._center_ninth_alt` are the DIAL's dispatch;
`app.encyclopedia.builders._live_ninth_face` and `_weekday_topic`'s
`travel_date` thread are the ENCYCLOPEDIA's — see
[Topic Builders](../app/encyclopedia/builders.md). Guarded by
`tests/test_ninth_mechanisms.py`: no double ninth (found in ANY
registry shape) may lack a `NINTH_MECHANISMS` entry, and no entry may
name an unimplemented mechanism.

**THE BLUE MOON LAW**
(owner-sealed 2026-07-22, R12; extended by **THE AXLE LAW**, CANON §The
Axle, owner-sealed 2026-07-29): `THIRTEENTHS` — key → (display name,
encyclopedia family, encyclopedia entry name), the SAME two-level shape
`WEEKDAY_THEME_NINTHS` uses, read by both the dial
(`render.layers.thirteenth_plate`) and its hover — now ten keys: the
four calendar-driven ("ophiuchus"/"sol"/"modrenik"/"chinese") PLUS the
six ALWAYS-CENTERS ("hestia"/"jesus"/"prudence"/"cunning"/"peace"/
"hardness_of_heart", `AXLE_ALWAYS_CENTERS` — renamed from the
2026-07-29 `PERSON_CENTERS`, whose word stopped being true once Peace
and Hardness of Heart, STATES rather than persons, joined it; always
present per `core.blue_moon.thirteenth_candidates`'s own union — no
trigger, no window); an always-center's family/article are `None` where
no Encyclopedia article exists yet (Hestia alone reuses her existing
"wider" entry) —
`render.compositor._thirteenth_tooltip` treats `None` as graceful-absent,
never a crash. `OPHIUCHUS_WINDOW`/`SOL_WINDOW` (year-agnostic (month, day)
bounds) and `MODRENIK_WINDOW_HALF_DAYS` (14, computed from the REAL
December solstice instant, never a fixed date) — each calendar-driven
13th's own short window; `CHINESE_MONTH_BRANCH_ANIMALS` (Gregorian month
→ the traditional solar-term branch animal — Feb Tiger … Dec Rat, the
December-solstice month — fixing ONE animal per Gregorian month for
the "chinese" calendar mount, `render.layers.calendar_mount_entries`).
The trigger/window/precedence law itself lives in
[Blue Moon](../core/blue_moon.md); pinned by `tests/test_blue_moon.py`.
**R5 MENU REWORK**:
`POINTER_PALETTE_LABELS` — the RAW English wheel label per pointer, and
the ONLY place a wheel's meaning is written (Court/Family/Genesis,
Temperaments/Elements/**Seasons** for the Quaternity, **Walks**/Ages/
Character — the Compass tail dropped 2026-07-28 — **Persons**/One
Soul/Council for the Prism, Warm/Cool, Zodiac/Almanac,
Legacy/Prophecy, and a `"default"` **Primary/Secondary/Tertiary**
fallback — three labels for a three-position slot — for a pointer whose
wheels have no names of their own),
extracted so `app.controller._build_menu`'s translated copy and
`app.controller.watch_title`'s UNTRANSLATED name reading both draw
from the ONE table (Rule #5); `SLOT_COMPLICATION_TITLES` — the four
Complication mode display titles (Digital Time/Date/Day length/
Seconds), read by [Slot Theme](../app/slot_theme.md)'s own tab.
**THE METAL SHADES (names unchanged by the 2026-07-27 transformer
rewrite):** `METAL_SHADE_NAMES` (metal → its shade-name tuple, gold
five/bronze three/silver three), `METAL_SHADE_DEFAULT` (the per-metal
install default) and `METAL_SHADE_TITLES` (shade → its Settings-combo
display title) — the validation/enumeration surface, and the reason the
user's Settings pick kept working across the rewrite untouched. What a
shade RESOLVES to changed: `defaults.METAL_SHADES` now maps it to the
name of a RAMP in `recolor/presets/metals.json` instead of holding a
numeric recipe (see that file's own entry, and
[Recolor (folder)](../recolor/___recolor.md) for the full algorithm).

### `palette.py` — The Colour Law
**Documentation:** [Palette](palette.md)

EVERY colour in the program, and nothing else — one file, nine fixed
sections, a pointer's three wheels always together. Born 2026-07-29
from the owner's own audit of `defaults.py`: 77 colour-bearing names
strewn between line 48 and line 3526 with no rule, PRISM's primary and
secondary wheels in one place and its Council 36 lines away inside
another pointer's block. `tests/test_palette_law.py` fails the build
if a colour literal appears anywhere else, if `PALETTE_PRESETS` spells
a hue out instead of naming a wheel, or if a pointer's wheels are ever
split apart again.

### `dial.py` — Dial Geometry and Window Sizing
**Documentation:** [Dial](dial.md)

Session 36 (THE CONFIG SPLIT, [Work Plan Structure](../WORKPLAN-STRUCTURE.md))
carved this module out of `defaults.py`: the window/diameter presets,
the procedural fallback geometry, the ring band (face, tick, letters,
motto arc), hand reach, the subdial/slot seating geometry, and
`OMEGA_HIT_RADIUS_FRACTION`.

### `shortcuts.py` — Keyboard Input and Fast Travel
**Documentation:** [Shortcuts](shortcuts.md)

Session 36: `SHORTCUTS`, `shortcut_display()`, `FAST_TRAVEL_THEMES` and
the Fast Travel Flash overlay's geometry/timing constants.

### `pantheon.py` — The Weekday Theme Registry
**Documentation:** [Pantheon](pantheon.md)

Session 36: every `WEEKDAY_*` table, `weekday_art()` and its rotation/
roster siblings, the title-plate resolver. **Over the 1,000-line
threshold and not yet ratcheted** — see that module's own doc for the
full arithmetic; this is an open item for the owner, not a silent gap.

### `calendar_mounts.py` — The Calendar's Dozen and Its Mounts
**Documentation:** [Calendar Mounts](calendar_mounts.md)

Session 36: the Calendar pointer's wedge/arrow geometry, the Slavic
Months 12-set, and THE CALENDAR MOUNT REGISTRY (`CalendarMount`,
`CALENDAR_MOUNTS`, `CALENDAR_MOUNT_MODES` and their geometry).

### `encyclopedia_ui.py` — The Reading Surfaces
**Documentation:** [Encyclopedia UI](encyclopedia_ui.md)

Session 36: legend term highlighting, the computed diagrams
(`CUBE_DIAGRAM_*`/`CANON_DIAGRAM_*`/`INSTRUMENT_DIAGRAM_*`), the
Encyclopedia's own card/gallery/reader/article sizing, the shared
`UI_BUTTON_*`/`THEME_RADIUS_*` chrome, the hover warm-sweep tuning.
Session 28: `CUBE_MODEL_GLASS_OPACITY` — the 3D Cube view's glass shell
weight, matching the gadget's own demo (`preview3d.cube_model.
GLASS_OPACITY`) without importing it.

### `glow.py` — Event Glow and Eclipse Rendering
**Documentation:** [Glow](glow.md)

Session 36: the season/moon turning-point glow constants and the whole
`ECLIPSE_*` family (state machine, art, type emblems).

### `continents.py` — The Continents Theme Family
**Documentation:** [Continents](continents.md)

Session 36's ONE deterministic fallback when `pantheon.py` still
exceeded the threshold after its own carves: the region roster, Earth
art resolution and day/night face resolvers `pantheon.py` imports
downhill (this module is subordinate to it, not a DAG peer).

### `defaults.py` — Developer Tunables (the Session 36 remnant)
Everything tunable that fits no single new module's charter, plus a
handful of COORDINATOR values/functions that legitimately need more
than one new module's data — the fixed import DAG lets a new module
import only stdlib + `config.{paths, constants, palette}`, never each
other and never this file, so a value two new modules both need either
duplicates (forbidden, Rule #5) or stays here, which may import every
new module downhill. Landed at 812 lines (from ~3,700) — its
`tests/test_structure_law.py` ratchet entry was deleted the same
commit, per that law's own designed shrink.

What stays: `DEFAULT_CITY`, tick scheduling, settings persistence, tray/
app presentation, UI icon chrome (`ICON_DIR`/`ICON_FILES`/`icon_path`),
`WORKING_SET_CEILINGS` (the asset-downscaling ceilings — not a colour,
not weekday, not dial-specific), the Session-27-drift Report/
Observatory/Guide/Translate/Time-Travel/Quick-Jump constants (none of
which fit any of the six new modules' charters), the METAL recolor
mapping (`METAL_SHADES`/`METAL_SOURCE_*`/`METAL_MASK_*`/`METAL_SWAP_*`
— recolor RECIPES, not colours, the colour law's own boundary),
`SUBDIAL_RECOLOR_*` (explicit remnant per the split map's pre-answered
Q&A), `DEFAULT_SKIN` (+ the "Default render config" comment,
relocated here from the dead banner that used to precede it) — a fully
typed [Manifest](../skins/manifest.md) `SkinDefinition` serialized
verbatim to `assets/skins/domy/skin.json`, reaching `dial.RING_FACE_
DIR`/`dial.HAND_*_REACH_FRACTION` and `pantheon.weekday_art`/
`continents.EARTH_ART_DIR`/`continents._CONTINENTS` downhill — the Pole
emoji windows, and three eclipse-icon names (`ECLIPSE_SOLAR_ART`,
`ECLIPSE_LUNAR_TYPE_ICON` + `eclipse_lunar_type_icon()`, `ECLIPSE_
SOLAR_TYPE_ICON_SOURCE`) that each need a name from a different new
module (`pantheon.weekday_art` or the remnant's own `ICON_DIR`) and so
could not live in `glow.py` beside their `ECLIPSE_*` siblings without
either module importing another (the fixed DAG forbids it).

**The move was proven value-identical**, the palette move's own method
repeated: the pre-split `defaults.py` was recovered from git HEAD and
imported under a private module name; all 351 of its public names
(values, functions, classes) were compared against their new homes in
one process — 0 differences.

**Everything that used to be documented here in prose about code that
MOVED — the PANTHEON roster, the weekday themes' completion waves, the
R5 menu rework's shortcut/Fast-Travel tables, THE CALENDAR MOUNT
REGISTRY, THE METAL SHADES, the WEEKDAY ALT ROTATION — now lives beside
the code it describes**, in the new module whose Files entry names it
above. (THE DOUBLE NINTH LAW and THE BLUE MOON LAW were never part of
this section — they document `constants.py` tables, untouched by this
session, and stay in that file's own entry above.)

### `archetypes.py` — The Archetype Mode
THE ARCHETYPE MODE's one configuration home (owner sealed package
2026-07-16): the (pointer, palette_style) → archetype grid — ELEVEN
archetypes over four pointers since the Cube wave (owner seal
2026-07-26, CUBE.md: Genesis / Council / Character on the "cube"
wheels), none on Aurora/Calendar — the
per-archetype figure tables (arm angle, stained-glass drop path, the
two-row names, article entity, encyclopedia target), the center table
(Eye / Hearth / Seal / Union / Throne / Beginning / Lord's Day — Compass
none, both wheels), the article-set
names Session 6 fills (the three Cube sets are Session 21's), the
Ages' two image registers and the render
tunables (figure heights, name sizing, the 1×1-placeholder threshold,
the Earth day-label geometry, the pending line). See
[Archetypes](archetypes.md).

### `doctrine.py` — Doctrine
The canon tables that are neither coordinates (cube) nor wheels
(archetypes): the two four-station crosses with their English mnemonics
and assembled ciphers, and the Double Trinity's twenty-four office /
process fields. Transcribed once from the sealed text so the computed
diagrams read data instead of prose. See [Doctrine](doctrine.md).

### `cube.py` — Character Cube Canon Data
The Character Cube's table as data (CUBE.md §The Thirteen Axes): thirteen
axes, twenty-six extremities with their luminous and fallen names, the
centre — the 65 sealed terms. Also the six poles' sealed Rose hues, the
Rose-24 ring in ray order, and the two laws from which the whole
Calendar-12 is computed. Coordinates only: every family, index, kinship
and antipode is DERIVED in [Cube Seating](../core/cube_seating.md), never
stored (root Rule 19). See [Character Cube](cube.md).

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
sites (`render.assets.AssetCache._recolored` for badges,
`render.asset_recolor.letter_metal_file` for ring letters), never threaded as
a parameter. **Session 28:** `preview3d_gadget_dir()` — the sibling 3D
Preview gadget's repo root, a monorepo-relative guess (`Gadgets/3D
Preview` beside `Gadgets/DOMY Watch`), `None` on a checkout without it
or a frozen build — [Cube Preview3D Bridge](../render/cube_preview3d.md)
treats `None` as the documented fallback, never an error.

**THE ROSE — the seventh pointer (owner seal 2026-07-27, [The Cube
Canon](../CUBE.md) §The Rose).** Its tables live beside every other
pointer's, so registering it registered it everywhere (settings
validation, the Design window, the palette editor):
`POINTER_POINTS["rose"] = 8` — EIGHT hues, not 24: the Rose is one
octa star drawn three times, never 24 independent arms (Rule #19).
The READER, however, counts 24 rays, and the Design window now says so:
`POINTER_DIAL_COUNTS["rose"] = 24` (owner correction 2026-07-28 — the
pill used to read "Rose (8)", the palette size leaking into a place
that answers a different question);
`POINTER_ARM_HALF_ANGLE_DEG["rose"] = 22.5` (the octa arm shape, so
45°-wide rays on a 15° pitch OVERLAP exactly as the owner draws them);
`POINTER_PALETTE_LABELS["rose"] = ("Legacy", "Prophecy")` — two wheels
that turn the star GEOMETRY and the figure sets, never the colors;
`POINTER_ARM_LABELS["rose"]` speaks the YEAR (four turning points on
the cardinals, four season centres on the diagonals — exactly where
`core.year_wheel` puts them). `ROSE_STAR_OFFSETS` places the three
stars in DRAW order, bottom of the z-stack first — Legacy
(−30°, −15°, 0°) leans wholly behind the hour, Prophecy
(−15°, +15°, 0°) rides the FUTURE over the PAST; the 0° star is last
on both, so the dominant fully-visible arm always points at true 12h.
`ROSE_STAR_SETS` says which figure set each star carries — in the canon's
own three words (`cube.FIGURE_SETS`: archetypal, historical, modern), so
the star, the roster and the disk register name the same thing — and
`ROSE_ARM_SYSTEMS` which character system its arms read (Legacy the 2D
Character wheel, Prophecy the 3D Cube vertices).
`POINTER_WEEKDAY_SLOTS["rose"]` is the COLOR LAW — the seat is the hue,
the Prism primary canon with the two Sunday hues lightened (MON cyan,
FRI rose) because Sunday needs blue and red for its own two faces;
`SERVANT_SEAT_ANGLE` gives the Servant the blue 06h arm there and on
every other horizontal-duality wheel (the Compass's Character wheel;
24h on the vertical wheels) and the Ruler keeps red at 18h.
`DAYLIGHT_SWITCH_POINTERS` names the two pointers — Calendar and Rose
— whose reader may turn the day/night law off.

**THE POINTERS REWORK, phase 1 (owner sheet `UV/Pointers.png`, sealed
2026-07-29):** `POINTER_SHAPES` ("star" | "polygon", default
`POINTER_SHAPE_DEFAULT` = "star") — the drawn wheel is the diamond star
or the plain polygon of the same arms; `POLYGON_POINTERS`
(trio/cross/hexa/octa) names the four whose polygon really IS a polygon
and therefore the only ones the curvature touches — the Calendar's
twelve-point and the Rose's twenty-four-point polygons are stars with
touching arms. `POLYGON_CURVATURE_RANGE` (0.0–1.0, default
`POLYGON_CURVATURE_DEFAULT` = 0.0) pulls each outer edge's midpoint
inward, `POLYGON_EDGE_MODES` ("smooth" the concave arc | "notched" the
V, default `POLYGON_EDGE_DEFAULT`) says how it is drawn.
`CALENDAR_STAR_ARMS` = 6 — the Calendar's star shape is TWO hexagrams
30° apart (the polygon shape is one twelve-point star,
`POINTER_DIAL_COUNTS`). `WHEEL_ARM_OFFSET_DEG` is now the ONE table of
wheels that seat their arms off the pointer's defaults —
`GENESIS_ARM_OFFSET_DEG` 180° on trio tertiary, and the new
`SEASONS_ARM_OFFSET_DEG` 45° on cross tertiary, which puts the Seasons'
colour BOUNDARIES on 12h/3h/6h/9h (astronomical seasons; the cross's
other two wheels stay meteorological). Geometry and consumers:
[The Pointer Shapes](../render/layers.md#the-pointer-shapes).

**THE CORRECTION ROUND (owner 2026-07-29).** The Prophecy assembly
shift of the round above was REVOKED on sight of the live watch —
`ROSE_RAY_PITCH_DEG` and `ROSE_WHEEL_ASSEMBLY_OFFSET_DEG` are DELETED,
and both Rose wheels keep every ray tip on a FULL hour
(`ROSE_STAR_OFFSETS`, untouched). The per-wheel law moved into the
BACKGROUND: `AURA_WEDGE_ANCHOR_DEFAULT` (−½, +½ spans — the wedge
CENTRED on its hue's lead ray, every one-star pointer) and
`ROSE_AURA_WEDGE_ANCHOR` ({Legacy (−1, 0) — the wedge TRAILS the lead
ray, boundaries on the lead-ray hours; Prophecy (−½, +½) — centred}).
The owner's own golden numbers, for the yellow group: Legacy tips
10h/11h/12h with the background 9h → 12h, Prophecy tips 11h/12h/13h
with the background 10:30 → 13:30. Read by
`render.layers.aura_wedge_anchor` alone — see
[The Aura wedge anchor](../render/layers.md#the-aura-wedge-anchor).

**THE DUAL SUNDAY WHEEL MAP + DUALITY-AXES CONFIG (owner decree
2026-07-28, SEALED IN FULL 2026-07-29 — [The Cube Canon](../CUBE.md)
§The Thirteen Axes — Display Plans):** the duality is a property of
the WHEEL. `CENTER_DUALITY_WHEELS` (cross tertiary — the Seasons'
diagonal arms leave no 12h/24h seat, its Sunday joins the
Trinity/Prism center law) and `HORIZONTAL_DUALITY_WHEELS` (octa
tertiary — the Character wheel wears the Rose's own hues, its Sunday
rides the blue<->red 06h/18h axis and its bodies take the Rose's hue
seats) extend the pointer-wide defaults (hexa/trio center, rose
horizontal, everything else vertical 12h/24h). Two per-theme flip
sets — root Rule #4, no per-theme values hardcoded into the render
layer: `DUALITY_RULER_ON_COLD_POLE` ("religion", the Sacred Axis proof
case on every HORIZONTAL wheel — Christianity, the Ruler, is the
LUMINOUS COLD member and pulls to blue/06h; Satanism the FALLEN WARM
one to red/18h) and `DUALITY_SERVANT_ON_TOP` ("continents", the
geographic flip on the VERTICAL wheels — the Arctic IS the north:
Arctic/Servant 12h, Antarctica/Ruler 24h). All 23 dual themes were
polled one by one and sealed 2026-07-29; every other theme is
STANDARD (Ruler top+red, Servant bottom+blue).
`render.layers.ruler_seat_angle`/`servant_seat_angle` are the two
readers; a flip swaps which arm each face's own plate/name/article
rides, never the identities themselves. Regression pins:
`tests/test_dual_sunday_wheels.py`.

## Connections

### Used by
- [App (folder)](../app/___app.md) — window/tray/settings read across
  the whole folder
- Core, data, skins, render (M2+) — invariants and paths

## Design Decisions
- Python modules, not JSON: constants need typing, expressions (e.g. `sqrt`)
  and direct imports.
- Three tiers by ownership: developer config here, declarative skin config in
  `skin.json` per skin (M5), user runtime state in `settings.json`.
