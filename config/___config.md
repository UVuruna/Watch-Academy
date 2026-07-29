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
that holds PLACES rather than people: the Dyad's Ninth turns between
The Ghosts and Exegol, which the canon expressly permits (a Ninth need
not be a person) and which the same table serves with no new mechanism
— the alternative, reusing `core.continents`'s Zealandia/Pangea
trigger, is recorded as a PROVISIONAL owner call in the staging ledger
rather than half-wired beside it. Second, the same PERSON seated in two
casts at different ages — Anakin in the Sith Mirror and the Jedi
Mirror, Leia and Han in a cast each of their own — which is why the
per-cast blurb and article sets are not an over-engineering: a shared
franchise set would have had to describe one of the two ages wrongly on
every hover. None of the three needed a `THEME_KEY_RENAMES` deletion.
The wiring table of the
[Theme Staging Ledger](../research/theme_staging.md) is now EMPTY; its
second table records the plates these three casts are still owed.
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

### `defaults.py` — Developer Tunables
Everything tunable that is NOT a colour (colours live in
[Palette](palette.md) — including the wheel tables `PALETTE_PRESETS`,
`RING_TINT_GROUPS`, `THEME_COLORS`, `TRAY_COLOR_WHEEL` and the
`DEFAULT_SKIN`'s own hues, which the skin now references by name).

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
marker borders), `ROSE_RAY_HALF_DEG`/`ROSE_RAY_BORDER` (the Rose ray
GEOMETRY — its hues moved out, see [Palette](palette.md)),
`ARM_OUTLINE_WIDTH` (the LEAD LINE's width, the twin of
`palette.ARM_OUTLINE` — every drawn arm wears it since the owner's
correction round 2026-07-29), the Almanac day-arrow geometry
(`CALENDAR_ARROW_*`; the Calendar's own wedge opacity is GONE — its
wedges wear the standard Aura alphas now),
the CALENDAR MOUNT (owner-sealed R7b 2026-07-21 registration, R9a
2026-07-21 render + picker, GENERALIZED 2026-07-29, the four new Dozens
+ THE AXLE LAW wired the same day):
`SLAVIC_MONTHS` (the twelve Croatian months as (croatian, gloss, ascii
stem, gregorian-month) rows), `EMOTIONS_DOZEN` (CANON's own hour-seated
Dozen), `MONTHS_ART_DIR`
(the canonical **sourceless** `assets/months/` root, OUTSIDE
`ART_SOURCED_ROOTS` — the subdial precedent; graceful-absent, a future
prompt sheet), `CALENDAR_MOUNT_RADIUS_FRACTION` (0.65, the DESIGN
ZODIAC law's 60-70% mount radius), `CALENDAR_MOUNT_MARK_SCALE` (the
mark's own drawn height, halved per extra seat per wedge), `CALENDAR_MOUNT_ALPHA`/
`CALENDAR_MOUNT_LIT_DELTA` (the current-mark emphasis, reaching exactly
1.0) and `CALENDAR_MOUNT_DIMMED_ALPHA` (0.20, owner R12 — The Cat's
dimming law, below the resting alpha but never zero) — and above all
**`CALENDAR_MOUNTS`**, the ONE registry of every roster that may ride
the twelve wedges (`CalendarMount(title, system, members, art_dir,
centre, art_stems, follows)`, plus `CALENDAR_MOUNT_SEATS_PER_WEDGE` and
the `almanac_seat_order()` rotation), from which the Settings-validated
`CALENDAR_MOUNT_MODES` is DERIVED — ten entries as of 2026-07-29:
`zodiac`/`almanac`/`months`/`chinese`/`emotions` plus the five Dozens
CANON sealed the same day, `olympians`/`apostles`/`virtues`/`vices`/
`sins` (`virtues`/`vices` are TWO ENTRIES of Aristotle's one Virtue
Wheel, light and paint registers of the identical seat table; `sins` is
the Christian catalogue of SIN, a different tradition on its own wheel
— Pride crown, Treachery root, axle Hardness of Heart — and the first
roster registered with no art on disk at all, every plate
graceful-absent); the render itself
(`render.layers._draw_calendar_mount`/`calendar_mount_entries`/
`calendar_mount_angle`, and the Pointer Theme window's Calendar mount
tab) is covered
in [Layers](../render/layers.md)'s own Calendar Pointer section (see
[Encyclopedia (subfolder)](../app/encyclopedia/___encyclopedia.md) for the Slavic Months topic),
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
Sole consumer: the [Encyclopedia (subfolder)](../app/encyclopedia/___encyclopedia.md)'s "The Two
Triangles" duality topic.
**THE METAL RECOLOR (rewritten 2026-07-27, owner verdict
"prihvaceno"):** the numeric recipe is GONE from this file. `METAL_SHADES`
is now only a MAPPING — per metal (gold/bronze/silver), a selectable
shade name → the name of a RAMP in `recolor/presets/metals.json`, where
the numbers live as DATA (a new metal costs one JSON entry and zero
code). Silver's three shades map to ramps that exist as metals in their
own right (gunmetal / silver / platinum); gold's and bronze's are named
`gold_*` and `bronze_*`. `METAL_SOURCE_BADGE` / `METAL_SOURCE_LETTER`
name the metal each art family was DRAWN in (bronze and gold
respectively) — the transform is source-agnostic and must be told where
it starts; `METAL_MASK_BADGE` / `METAL_MASK_LETTER` pick the mask mode
(`chroma` for art mixing metal with gray stone, `alpha` for glyphs).
`METAL_SWAP_VERSION` (bumped to 6 here) — the cache-key salt
`letter_metal_file` and `metal_variant_file` fold in (alongside the
active shade name) so a shade switch or a recolor-math change never
serves a stale PNG. `METAL_SWAP_TARGETS` stays the membership tuple
`("gold", "silver")` — badges never bronze-swap. RETIRED with the old
kernel: `METAL_RECOLOR_GAIN_RANGE` (its 1.90 ceiling clipped 11.87% of a
gold plate to one flat maximum on real art) and `METAL_SWAP_HUE_WINDOW` /
`_SOFT` / `METAL_SWAP_SAT_RAMP` (the mask's window now lives in the
presets' `tuning` block, in Oklab, where a hue angle survives the
shadows). `constants.py` still holds the shade NAME tables
(`METAL_SHADE_NAMES`, `METAL_SHADE_DEFAULT`, `METAL_SHADE_TITLES`) since
`defaults.py` is downstream of `paths.py`'s validation needs. Full
recipe: [Recolor (folder)](../recolor/___recolor.md) and
[Assets](../render/assets.md).
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
poles, Ctrl+0 Greenwich (the zero meridian; moved off Ctrl+Space
2026-07-27 — CUBE.md's ARTICLE-DEPTH LAW took Space and its
modifiers), Ctrl+Left/Right the user's custom Quick
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
a parameter.

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
- [App (folder)](../app/___app.md) — window/tray/settings read all four files
- Core, data, skins, render (M2+) — invariants and paths

## Design Decisions
- Python modules, not JSON: constants need typing, expressions (e.g. `sqrt`)
  and direct imports.
- Three tiers by ownership: developer config here, declarative skin config in
  `skin.json` per skin (M5), user runtime state in `settings.json`.
