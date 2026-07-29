# WORKPLAN-STRUCTURE — The Structural Arc (Sessions 35 & 36)

**This is a SEPARATE plan with its own agent.** The Theme Backlog arc —
Sessions 30–34 in [Work Plan](WORKPLAN.md) §The Theme Backlog — belongs
to ITS agent, runs on ITS board in ITS order, and this file changes
NOTHING there (owner order 2026-07-29: *"ti praviš svoj plan, a ne
prepravljaš njegov"*).

## THE GATE — read before opening either session

**Nothing in this file starts until the Theme Backlog arc is CLOSED**
— its agent has delivered the Session 34 report and the final owner
report. The two arcs overlap on `config/encyclopedia_tree.py` and the
`defaults.WEEKDAY_*` tables; overlapping work WAITS for the other
agent to finish (owner order 2026-07-29).

Verifiable gate check, run it FIRST in either session: the twelve cast
keys (`age_of_heroes`, `celestial_court`, `corporate`, `wow_alliance`,
`wow_horde`, `wow_evil`, `cp_gangs`, `cp_street`, `cp_corpo`,
`sw_jedi`, `sw_sith`, `sw_dyad`) are present in
`constants.WEEKDAY_THEMES` and the staging ledger
(`research/theme_staging.md`) carries no owed-items row for them. If
that is not true, **STOP and tell the owner the gate is not open** —
do not start, do not "prepare".

**Order inside this arc: 35 → 36.** Both entries were adversarially
red-teamed on 2026-07-29 (three simulated session agents hunting
ambiguities against the live code); every finding is folded in below.

Context, not tasks: the same owner verdict day already shipped the
Encyclopedia resize fix (0.14.571) and THE COLOUR LAW
(`config/palette.py` + `tests/test_palette_law.py`, 0.14.572). Session
36 works UNDER that law.

---

## Session 35 — The Nine Wholes → **Sonnet**

**Say:** *"Radi Sesiju 35 iz WORKPLAN-STRUCTURE.md — devet celina."*

**Why:** the owner's 2026-07-29 verdicts. (1) The six-whole home
grouped poorly and had no room for the incoming casts; the owner chose
3×3: *"može i 9 grupacija sa ovim novim velikim sekcijama"*. (2)
Colors: *"koristi ROSE paletu + neka boja Silver kao moon"* — all
eight Rose hues plus the Moon's silver, seated symbolically.

**Reads:** this entry (the tables below are the SPEC — transcribe, do
not redesign); `config/encyclopedia_tree.py` + its `.md`;
`app/encyclopedia/home.py` + `home.md` + `cards.py`;
`data/encyclopedia.py` (`whole()`); `Database/encyclopedia.json`
§wholes; `tests/test_encyclopedia_tree.py`;
`tests/test_theme_completeness.py` (Session 30's guard — its
look-only exception set is reused below); `config/palette.py` §1 and
§6; `config/palette.md`.

### The nine wholes — the exact table (FINAL)

Keys, titles, accents, memberships and hour arguments are sealed
(owner shown 2026-07-29, seating verdicts presented with the veto open
and not vetoed: trinity+duality → `faith`, profession → `worlds`,
alchemy+japan STAY in `living`). Six wholes keep their inherited Rose
hues; the two unspent Rose hues are now spent; the ninth accent is the
Moon's silver.

| # | key | title | accent | themes | hour argument (transcribe into the table's comments) |
|---|---|---|---|---|---|
| 1 | `instrument` | The Instrument | `ROSE_PALETTE[0]` | week, instrument, era, months, guide | 12h yellow — noon, the hour the watch is built around (unchanged) |
| 2 | `sky` | The Sky | `MOON_SILVER` | sun, moon, seasons, eclipses | the Moon's own silver — the near sky's face; eclipses ARE sun–moon (owner: "Silver kao moon") |
| 3 | `cosmos` | The Cosmos | `ROSE_PALETTE[5]` | planets, cosmos, continents, astrology, chinese, celestial_court | 03h cyan — deep night, when the far sky is read (inherited from the old `celestial`) |
| 4 | `gods` | The Gods | `ROSE_PALETTE[4]` | greek, norse, egypt, slavic, age_of_heroes | 24h moon-violet — midnight, the sacred hour (inherited from `divine`) |
| 5 | `faith` | The Faith | `ROSE_PALETTE[3]` | bible, creeds, trinity, duality | 21h rose — the vesper hour; Love's red thinned by moonlight (the Rose canon's own reading) |
| 6 | `cube` | The Character Cube | `ROSE_PALETTE[6]` | cube_doctrine, cube_axes, cube_figures, cube_projections, double_trinity, crosses, one_soul | 06h blue — the Cube's axis blue (CUBE.md colour law, unchanged) |
| 7 | `inner` | The Inner Wheel | `ROSE_PALETTE[2]` | virtues, sins, moods, intelligences | 18h red — sunset, the human fire, Lucifer's hue on the Scale (inherited from `human`) |
| 8 | `living` | The Living World | `ROSE_PALETTE[7]` | wolf, bee, elephant, alchemy, japan | 09h green — spring's centre, life (unchanged) |
| 9 | `worlds` | The Worlds | `ROSE_PALETTE[1]` | profession, corporate, + the three FRANCHISE cards | 15h orange — the working afternoon, the Merchant's copper; worlds PEOPLE build: trades and fictions |

**The franchise cards in `worlds`:** the backlog waves registered one
merged card per franchise (WoW, Cyberpunk, Star Wars — backlog
structural answer 2) under keys THE WAVES chose. Discover the actual
keys in `config/encyclopedia_tree.py` (`VARIANT_SOURCES` / the topics
table) and RESEAT those cards — never rename them, never split them.

**RESEAT, don't re-wire:** the waves already seated every new card
somewhere in the six-whole world. This table SUPERSEDES those seats —
each card moves to its row above; articles, variants and dial wiring
are untouched.

### Delivers, in order

1. **`config/palette.py` §1:** promote the Moon's dial colour to a
   named hue — `MOON_SILVER = "#C9CDD4"` — and make
   `SKIN_PLANET_BODY_COLORS["moon"]` (§6) reference it. One value,
   three readers (skin body, whole accent, and whoever comes third).
   Do NOT invent a different silver: the owner's "Silver kao moon" IS
   the hue the Moon body already wears on the dial.
2. **`config/encyclopedia_tree.py`:** replace the whole table with the
   nine from the spec — every accent an EXPRESSION
   (`palette.ROSE_PALETTE[i]` / `palette.MOON_SILVER`, never a hex
   literal — the colour law), every whole's comment carrying its hour
   argument. `THEME_TO_WHOLE` / `WHOLE_BY_KEY` derive unchanged.
   Rewrite the `ROSE_ACCENTS_USED` comment: all eight Rose hues spent
   plus the silver, uniqueness 9.
3. **`Database/encyclopedia.json` §wholes:** nine entries keyed by the
   NEW keys. Reuse the existing `base` lines for `instrument`, `cube`,
   `living` verbatim; write these six (house voice, final — do not
   restyle):
   - `sky`: "The near sky the dial answers to every minute: the Sun's arc, the Moon's faces, the turning seasons, and the moments the two lights cross."
   - `cosmos`: "The far sky and its readers: the wandering planets, the deep heavens, the turning Earth, and the zodiacs and courts hung upon them."
   - `gods`: "The courts that named the week — Greek, Norse, Egyptian, Slavic — and the age of heroes beneath them."
   - `faith`: "The written faiths: the Bible's cast, the world's creeds, and the trinities and dualities they orbit."
   - `inner`: "The wheel inside a person: virtues against sins, the moods of a day, and the ways a mind is strong."
   - `worlds`: "The worlds people build: the trades and their offices, and the invented worlds of games and film."
   DELETE the `celestial`, `divine`, `human` entries (Rule #6 — no
   ghost keys).
4. **Home 3×3:** `ENCYCLOPEDIA_HOME_COLUMNS` STAYS 3 — only its
   comment changes ("3 rows × 3 columns = the nine wholes"). Geometry
   holds at the 1280×720 minimum: 3 rows × `ENCYCLOPEDIA_CARD_MIN_
   HEIGHT_PX`(150) + 4 × 20 gaps = 530px — the existing no-scroll
   tests keep binding. While in `home.py`, pluralize the card footer
   properly (`theme`/`themes`, `page`/`pages`).
5. **The stale-count and dead-key sweep** — TWO greps, both required
   (red-team finding: the first alone leaves the suite red):
   - `grep -rni "six wholes\|2x3\|3x2" --include=*.py --include=*.md`
     — fix prose/docstring counts (`home.py`, `cards.py`, `dialog.py`,
     `data/encyclopedia.py` `whole()` docstring, the `.md`s);
   - `grep -rn "\"celestial\"\|\"divine\"\|\"human\"" tests/ app/
     config/ render/` — every OLD WHOLE KEY as a string must go.
     Known sites the red team pinned: `tests/test_settings_dialog.py`
     ~L1168 (`"divine"` → `"gods"`) and ~L1408/L1514 — where the old
     single-`celestial` membership asserts must be SPLIT per the new
     table (`eclipses` → `sky`; `astrology`/`chinese`/`planets`/
     `cosmos`/`continents` → `cosmos`); `tests/test_continents.py`
     ~L208 (`"celestial"` → `"cosmos"`);
     `tests/test_encyclopedia_tree.py` ~L131
     (`show_whole("divine")` → `show_whole("gods")`). Line numbers are
     as of 2026-07-29 — re-grep, don't trust them.
6. **Tests (`tests/test_encyclopedia_tree.py`):**
   - the six-wholes count test becomes NINE (none empty);
   - the accent test becomes: eight accents ∈ `palette.ROSE_PALETTE`,
     the ninth == `palette.MOON_SILVER`, all nine DISTINCT;
   - **THE REACHABILITY LAW (new):** every key in
     `constants.WEEKDAY_THEMES` — EXCEPT the look-only keys that
     Session 30's `test_theme_completeness.py` already names in its
     own exception set (reuse THAT set, Rule #5, one source;
     `planets_art` is the known member) — resolves, directly or
     through `tree.TOPIC_ALIASES`, to a topic seated in a whole. No
     dial theme unreachable from Home ever again (the owner's exact
     2026-07-29 complaint). Boundary: Session 30's guards own
     REGISTRATION (art ↔ key ↔ ledger); this law owns REACHABILITY
     (registered key ↔ a seat on Home).
7. **Docs:** `config/encyclopedia_tree.md`, `app/encyclopedia/home.md`,
   `tests/___tests.md` — counts, the new accents, the reachability
   law's rationale.

**Pre-answered questions (do not ask these):**
- *A whole key equals a theme key (`cosmos`, `instrument`)?* Allowed —
  `instrument` already does it; wholes and topics are separate
  namespaces (`show_whole` vs `show_topic`).
- *Migration for stored keys?* None — whole keys are navigation-only,
  never persisted in settings.
- *The twelve landed casts?* RESEAT their cards per the table; never
  rewrite their articles, variants, or dial wiring.
- *`assets/instrument/wholes/` plates?* Empty as of 2026-07-29; any
  drawn plate uses the NEW keys (`sky.png`, `gods.png` …).
- *Does the Guide stay in `instrument`?* Yes — untouched.

**Done when:** the suite is green, Home shows 3×3 with the nine
accents, the reachability law passes, and neither grep from item 5
returns a live old-key or stale-count site.

---

## Session 36 — The Config Split → **Sonnet**

**Say:** *"Radi Sesiju 36 iz WORKPLAN-STRUCTURE.md — podela config
fajla."*

**Runs:** after Session 35. The waves have grown the weekday tables by
twelve casts — the split moves the BIGGER tables once, instead of the
waves and the split racing each other.

**Why:** the owner's 2026-07-29 structural rage, second half. The
colour law fixed the COLOURS; `defaults.py` remains a ~3,000-line
god-file (Rule #20 violation). His words stand over this session:
*"kada se implementira nova funkcionalnost… ne prati nikakvu strukturu
nego samo nabaci novu promenljivu na kraj dokumenta."*

**Reads:** this entry; `config/defaults.py` — outline FIRST, fresh
(`grep -n "^# ---" config/defaults.py`; the waves have moved every
line number, so headers and NAMES are the contract, never lines);
**`config/palette.md` §Design Decisions — the PROVEN METHOD this
session repeats**; [Refactor God-Files](REFACTOR-GODFILES.md);
`tests/test_palette_law.py` (guard style); `tests/test_purity.py`.

### The split map

Assignment is by SECTION HEADER — except the one section the red team
proved is MIXED, which gets an explicit carve list. Every section not
named here STAYS in `defaults.py`.

| new module | takes | one responsibility |
|---|---|---|
| `config/pantheon.py` | "The PANTHEON roster" whole; from "Weekday body themes": every `WEEKDAY_*` table, `weekday_art` and its sibling helpers, the roster/cast tables the waves added, `CONTINENTS_*`, `_CONTINENTS`, `EARTH_ART_DIR` | the weekday THEME registry — who sits on which day, in which art |
| `config/calendar_mounts.py` | "Calendar pointer", "Calendar-pointer 12-sets: the Slavic Months", "THE CALENDAR MOUNT REGISTRY"; from "Weekday body themes": `THIRTEENTHS`, `CHINESE_MONTH_BRANCH_ANIMALS` and any other 13th/mount table | the Calendar's dozen, its mounts, and the thirteenths |
| `config/encyclopedia_ui.py` | "Legend term highlighting", "THE COMPUTED DIAGRAMS", "THE SESSION 27 REWORK" (minus the one named exception below), "THE INSTRUMENT'S OWN DIAGRAMS", "Hover article warm sweep" | the reading surfaces — encyclopedia, legend, computed diagrams |
| `config/dial.py` | "Window", "Procedural FALLBACK geometry", "Moon/Earth rim transit", "Ring faces" (incl. the ring-tint swatch-size leftovers — the tint HUES are palette's), "Hand sizing", + `OMEGA_HIT_RADIUS_FRACTION` (the named exception: it is dial HIT geometry computed from `RING_LETTER_ART_SCALE`, so it moves here, out of the Session 27 section) | dial geometry and window sizing |
| `config/shortcuts.py` | "Keyboard shortcuts", "Fast Travel", "Fast Travel FLASH" | keyboard input and the fast-travel it drives |
| `config/glow.py` | "Season/moon event glow rendering"; from "Weekday body themes": the `ECLIPSE_*` block | event glow windows and the eclipse rendering knobs |
| `defaults.py` (remnant) | everything else — Location, Tick scheduling, Settings persistence, Tray / app presentation, UI icon chrome, Shared app content, Pole emoji windows; from "Weekday body themes": `DEFAULT_SKIN` (+ its comment block) and the `METAL_SHADES`/`METAL_SHADE_NAMES`/`METAL_SOURCE_*`/`METAL_SWAP_*` block (recolor RECIPES, not colours — the colour law's own boundary) | app-level tunables |

Red-team facts this map already absorbs (do not rediscover them):
- **"Weekday body themes" is NOT one responsibility** — `DEFAULT_SKIN`,
  the `METAL_*` block, the `ECLIPSE_*` block and the thirteenth tables
  all physically live inside it; the carve list above is the answer.
- The `# --- Default render config` header (~L550) is an EMPTY
  three-line comment — it dies; its promise lives beside
  `DEFAULT_SKIN` in the remnant.
- Taken wholesale, pantheon would exceed the 1,000-line gate
  (~1,270); WITH the carves it lands under. **If `wc -l` still shows
  pantheon over 1,000, the one deterministic fallback is:** move the
  whole CONTINENTS family (`CONTINENTS_*`, `_CONTINENTS`,
  `EARTH_ART_DIR`, the earth resolvers) to `config/continents.py` as
  its own cohesive module. No other improvisation.

**Import DAG (fixed):** a new module imports ONLY stdlib +
`config.{paths, constants, palette}` (+ `skins.manifest` where a moved
value needs its types). New modules NEVER import each other and NEVER
import `defaults`. The REMNANT may import any new module (downhill) —
and it must: `DEFAULT_SKIN` reaches `RING_FACE_DIR` and the two
`HAND_*_REACH_FRACTION`s from `dial`, and `weekday_art` /
`EARTH_ART_DIR` / `_CONTINENTS` from `pantheon` (red-team-verified
list; the old "DEFAULT_SKIN touches only palette" claim was FALSE). A
cross-reference that still fights the DAG is resolved by MOVING the
referenced value into the same module — never by a back-import.

### The method — the palette move's, exactly

1. **Snapshot BEFORE:** import `config.defaults`, record every public
   name's value (normalize tuples/dicts; `repr` for dataclasses) to
   `before.json` in the scratchpad.
2. **Extract VERBATIM:** AST-cut each assigned statement with the
   comment block above it — never retype a value or a comment.
3. **Assemble** each module: docstring (purpose; `Layer: config —
   pure, no Qt, no wall clock`), then its segments in map order.
4. **Rewrite call sites by script** (AST-safe import insertion):
   `defaults.NAME` → `<module>.NAME` for every moved name, across
   app/render/skins/core/data/config/tests. Expect well over 1,300
   sites. Rule #6: zero re-export shims — a moved name accessed
   through `defaults.` must raise `AttributeError`, and that is
   CORRECT.
5. **Snapshot AFTER** from the new modules; the diff MUST be empty.
   Paste the "0 differences" line into the session report.
6. **Guard test** — new `tests/test_config_cohesion.py`: (a) every
   `config/*.py` ≤ 1,000 lines, no exemptions; (b) no moved name
   remains an attribute of `config.defaults`.
7. **Full suite green.** This session edits NO file of the Theme
   Backlog arc and NOTHING in `WORKPLAN.md` — `config/___config.md`
   is the living truth about where tables live.
8. **Docs:** one `.md` per new module (purpose, connections, what
   deliberately stayed behind — Rule #3 applies to NEW files first);
   rewrite `config/___config.md`'s `defaults.py` section to the
   remnant's true contents.

**Pre-answered questions (do not ask these):**
- *May I re-order values inside a module?* Keep extraction order
  within a section; order sections as the map lists them.
- *`weekday_art` is called by the PANTHEON tables?* It moves WITH them
  into `pantheon.py`; the remnant `DEFAULT_SKIN` imports it from there
  (downhill is the permitted direction).
- *`config/archetypes.py`, `cube.py`, `taxonomy.py`?* Untouched —
  already cohesive.
- *Cache/version tags?* `SUBDIAL_RECOLOR_*` ramps and the `METAL_*`
  recipes stay in the remnant; nothing about their values changes.
- *An import cycle the DAG cannot absorb?* STOP and report the exact
  pair of names (Rule #2) — never improvise a shim.

**Done when:** the snapshot diff is empty, the suite is green,
`wc -l config/*.py` shows every file ≤ 1,000, and each new module has
its `.md`.
