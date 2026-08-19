# config/

The single home for every constant and tunable in the project
(monorepo Rule #4). No other module may contain a numeric literal that
is not a loop index or an enum value. Read-only at runtime —
user-changeable state lives in the settings file owned by
[Settings Store](../app/__about/settings_store.md); a skin's own declarative
shape lives in `skin.json` per skin.

Layer: config — pure Python, no Qt import, no wall-clock read. Every
other layer (`core → data → skins → render → app`) may import from
here; nothing here imports from them.

## Files

| File | Tier | One line |
|------|------|----------|
| `__init__.py` | Trivial | package docstring only |
| `archetypes.py` | Algorithmic | THE ARCHETYPE MODE — the (pointer, wheel) → figure grid, the eleven archetypes' figure/center tables — [about](__about/archetypes.md) · [flow](__flow/archetypes.md) |
| `bakery.py` | Algorithmic | BAKE-TIME POLICY — the art bake's WebP quality and the letter bake's eager finish roster; read at setup, never at runtime — [about](__about/bakery.md) |
| `calendar_mounts.py` | Algorithmic | the Calendar pointer's wedge geometry and THE CALENDAR MOUNT REGISTRY (every roster that may ride the twelve wedges) — [about](__about/calendar_mounts.md) · [flow](__flow/calendar_mounts.md) |
| `complications.py` | Standard | THE SOUTH SLOT and what it may show — the slot modes, their titles, the seat angles, the zodiac/chinese slot styles, the Earth marker style — [about](__about/complications.md) |
| `continents.py` | Algorithmic | THE CONTINENTS theme's region roster and day/night Earth-face resolvers — [about](__about/continents.md) · [flow](__flow/continents.md) |
| `cube.py` | Algorithmic | the Character Cube's canon table — thirteen axes, the 108+48-seat roster, the two seatings — [about](__about/cube.md) · [flow](__flow/cube.md) |
| `defaults.py` | Algorithmic | developer tunables that fit no single peer module, plus the cross-module coordinators (`DEFAULT_SKIN`, window-margin math) — [about](__about/defaults.md) · [flow](__flow/defaults.md) |
| `dial.py` | Algorithmic | dial geometry and window sizing — ring band, hand reach, subdial/slot seating — [about](__about/dial.md) · [flow](__flow/dial.md) |
| `doctrine.py` | Algorithmic | the Two Crosses and the Twenty-Four Fields — canon tables neither coordinates nor wheels — [about](__about/doctrine.md) · [flow](__flow/doctrine.md) |
| `encyclopedia_tree.py` | Algorithmic | the Encyclopedia's three-level tree — nine Wholes, theme cards, variant switcher loops — [about](__about/encyclopedia_tree.md) · [flow](__flow/encyclopedia_tree.md) |
| `encyclopedia_ui.py` | Algorithmic | the reading surfaces — article/legend sizing, term-highlight patterns, the computed diagrams — [about](__about/encyclopedia_ui.md) · [flow](__flow/encyclopedia_ui.md) |
| `eras.py` | Algorithmic | ERA NOTATION & THIRD CALENDARS — how a year is WRITTEN: the notation, the named eras, the four third calendars and the place a date is written for — [about](__about/eras.md) · [flow](__flow/eras.md) |
| `glow.py` | Algorithmic | event glow windows and the whole eclipse type→render-state machine — [about](__about/glow.md) · [flow](__flow/glow.md) |
| `identity.py` | Standard | what this build IS and calls itself — the app names, the mutex and AppUserModelID, the hidden-mode word, the artwork generations it ships — [about](__about/identity.md) |
| `ninth.py` | Algorithmic | THE NINTH, the seat outside the circle — its per-theme tables, THE DOUBLE NINTH LAW's mechanisms, THE DUAL/NINTH TIME WINDOW — [about](__about/ninth.md) · [flow](__flow/ninth.md) |
| `palette.py` | Algorithmic | THE COLOUR LAW — every colour in the program, nine fixed sections, nothing else — [about](__about/palette.md) · [flow](__flow/palette.md) |
| `pantheon.py` | Algorithmic | the weekday theme registry and THE UNIVERSAL ROTATION CONVENTION engine — [about](__about/pantheon.md) · [flow](__flow/pantheon.md) |
| `pointer_geometry.py` | Algorithmic | what a pointer IS as a shape — arm and wedge counts, arm half-angles, shape and polygon edges — [about](__about/pointer_geometry.md) · [flow](__flow/pointer_geometry.md) |
| `pointer_names.py` | Standard | what a pointer is CALLED — display names, wheel labels (the one place a wheel's MEANING is written), arm labels — [about](__about/pointer_names.md) |
| `registry/` | (package) | THE REGISTRY — one dictionary of all themes, grouped by KIND; every legacy table derived from it in one assignment — [folder](registry/___registry.md) |
| `paths.py` | Algorithmic | frozen-safe path resolution, the art-source suffix resolver, the per-watch thread-local Display Context — [about](__about/paths.md) · [flow](__flow/paths.md) |
| `profiling.py` | Algorithmic | `@timed`/`measure()` execution-time statistics behind the hidden Report — [about](__about/profiling.md) · [flow](__flow/profiling.md) |
| `ring.py` | Algorithmic | THE RING VOCABULARY's own tables — finishes and metal shades, subdial plates, outers/inners/letters, the theme metal looks — [about](__about/ring.md) · [flow](__flow/ring.md) |
| `shortcuts.py` | Algorithmic | the keyboard shortcut table and Fast Travel's theme/option jumps — [about](__about/shortcuts.md) · [flow](__flow/shortcuts.md) |
| `sky.py` | Algorithmic | the sky the dial reads — sun depressions, the year-wheel anchors, the lunation, the season event names, the tropics, the Deep Time filename — [about](__about/sky.md) · [flow](__flow/sky.md) |
| `taxonomy.py` | Algorithmic | THE ONE HIERARCHY — five categories → groups → weekday themes — [about](__about/taxonomy.md) · [flow](__flow/taxonomy.md) |
| `ui_ranges.py` | Standard | what the user-facing CONTROLS may be set to — the language roster, the zoom/scale/saturation ranges and their slider steps — [about](__about/ui_ranges.md) |
| `umbra.py` | Algorithmic | THE UMBRA WHEEL, the band of shadow — moon bands, eclipse styles, the sun and moon STATIONS, the tint modes — [about](__about/umbra.md) · [flow](__flow/umbra.md) |
| `watch_face.py` | Standard | THE WATCH FACE CONTROL VOCABULARY — every control whose setter is just "store this key" — [about](__about/watch_face.md) |
| `ui_text.py` | Algorithmic | the UI text catalog — every translatable chrome string, one flat tuple — [about](__about/ui_text.md) · [flow](__flow/ui_text.md) |
| `winapi.py` | Standard | Win32 API literals and the keyboard-hook ABI, the one enum-exception to Rule #4 — [about](__about/winapi.md) |
| `zodiac.py` | Algorithmic | ZODIAC & CHINESE CALENDAR — the two sign systems the mounts and slots ride, and THE THIRTEENTHS — [about](__about/zodiac.md) · [flow](__flow/zodiac.md) |

## Connections

### Uses
- Nothing outside the project's own `skins/manifest.py` — `defaults.py`
  imports the typed skin dataclasses (`SkinDefinition`, `RingSpec`,
  etc.) to build `DEFAULT_SKIN`.

### Used by
- [App (folder)](../app/___app.md) — window/tray/settings/dialogs read
  across the whole folder
- `core`, `data`, `skins`, `render` — invariants and paths downhill

## Design Decisions

- **Python modules, not JSON.** Constants need typing, expressions
  (e.g. `sqrt`, derived dicts) and direct imports between config
  modules — a data format cannot express any of that.
- **Three tiers by ownership.** Developer config lives here; a skin's
  own declarative shape lives in `skin.json` per skin (M5); user
  runtime state lives in `settings.json`.
- **A fixed, PARTIAL import DAG governs six of these files.** Session
  36 (THE CONFIG SPLIT, [Work Plan Structure](../../docs/archive/WORKPLAN-STRUCTURE.md))
  carved `dial.py`, `shortcuts.py`, `pantheon.py`, `calendar_mounts.py`,
  `encyclopedia_ui.py` and `glow.py` out of a ~3,700-line
  `defaults.py` god-file as PEERS that may import only `paths`/
  `constants`/`palette` and never each other; `continents.py` is
  `pantheon.py`'s own deterministic fallback (a subordinate, not a
  seventh peer); `defaults.py` itself is the one remnant allowed to
  import every peer downhill, holding whichever coordinator value
  needs more than one peer's data. The older files this DAG rule does
  NOT bind (`archetypes.py`, `cube.py`, `doctrine.py`, `encyclopedia_
  tree.py`, `taxonomy.py`, `ui_text.py`, `winapi.py`)
  import freely among themselves and the base layer.
- **THE COLOUR LAW is enforced, not advisory.** Every colour value in
  the program lives in `palette.py` alone; `tests/test_palette_law.py`
  fails the build if a hex literal or RGBA tuple appears anywhere
  else — see [Palette](__about/palette.md).
- **`pantheon.py` is 1,549 lines, over the god-file threshold, and is
  an open item.** This migration is docs-only and cannot split code;
  see [Pantheon](__about/pantheon.md)'s own account of why the
  Session 36 split map's estimate fell short and what a follow-up
  split session would need to decide.

<a id="the-constants-split"></a>

## THE CONSTANTS SPLIT (owner's map, 2026-08-19)

`config/constants.py` is GONE. It had grown to **38 top-level sections**
— app identity, era notation, weekday bodies, pointer geometry, ring
finishes, zodiac, translation languages, UI scale, seating — under one
docstring, and the [OOP audit](../../docs/AUDIT-OOP-2026-08-18.md)'s R15
named it what it was: a junk drawer, not a directory. Its SIZE was never
the problem (770 logic lines, 645 of them declarative tables, under every
guard's wall since [THE ONE
ARITHMETIC](../../docs/ENFORCEMENT.md#the-measure)); its SHAPE was.

The owner ruled on **2026-08-19** and named every destination module
himself. Each section moved WHOLE, with its comments; **1,070 references
across 142 files** were repointed to the real module; **no re-export shim
was left behind** (`rules/CODE.md` — No backward compatibility), so
`constants.NAME` does not resolve anywhere any more — the name tells you
which module owns it.

Where each of the 38 sections went, and why:

| Section(s) in the old `constants.py` | Now in | Why there |
|---|---|---|
| APP IDENTITY (names, mutex, AppUserModelID), HIDDEN MODE, ARTWORK SOURCES | **NEW** [`identity.py`](__about/identity.md) | what this build IS and calls itself — fixed product facts, no geometry, no theme; a LEAF so `paths.py` can read `APP_NAME` without a cycle |
| APP IDENTITY (the dial-identity block: `HOURS_PER_REVOLUTION`, `DIAL_TOP_HOUR`, `SECONDS_*`, `DIAL_OFFSET_DEG`, `SOLAR_NOON_SECS`, `SECONDS_PER_DEGREE`, `HAND_HUB_OFFSET_UNITS`) | [`dial.py`](__about/dial.md) | these numbers ARE the dial convention ([The Dial](../../docs/DIAL.md)) and the module already owns dial geometry — they sit at its top, above its first section |
| APP IDENTITY (Sun, Year wheel, Moon, Deep Time filename) · SEASON EVENT NAMES · TROPICS | **NEW** [`sky.py`](__about/sky.md) | the numbers of the SKY, not of the drawn face; `core/` computes with them and `dial.py` needs none of them |
| ERA NOTATION & THIRD CALENDARS | **NEW** [`eras.py`](__about/eras.md) | one subject, whole: how a year is WRITTEN, and every calendar it can be written in |
| WEEKDAY BODIES · FIGURE ROSTERS · WEEKDAY INDEX · WEEKDAY SLOTS PER POINTER | [`registry/week.py`](registry/__about/week.md) | THE WEEK REGISTRY already declares all 35 themes' weekday seats; the weekday vocabulary belongs with them |
| WEEKDAY THEMES · THEME BLURBS & ARTICLES | *deleted* → `registry.THEMES` / `.BLURBS` / `.ARTICLES` | see [the one deviation](#the-one-deviation) below |
| POINTER ARM & WEDGE COUNTS · ARM HALF-ANGLES · POINTER SHAPE & POLYGON EDGES | **NEW** [`pointer_geometry.py`](__about/pointer_geometry.md) | what a pointer IS as a shape — form, and only form |
| POINTER DISPLAY NAMES · WHEEL LABELS · ARM LABELS | **NEW** [`pointer_names.py`](__about/pointer_names.md) | what a pointer is CALLED; a rename is a copy decision, a half-angle is a drawing decision, and the two change for different reasons |
| CALENDAR & ROSE STAR GEOMETRY · ROSE FIGURE SETS & DAYLIGHT SWITCH | [`calendar_mounts.py`](__about/calendar_mounts.md) | the module already owns the twelve wedges and THE CALENDAR MOUNT REGISTRY |
| WATCH FACE CONTENT KINDS (R-18) | [`watch_face.py`](__about/watch_face.md) | THE WATCH FACE CONTROL VOCABULARY's own module |
| TRIO & GENESIS ARM THEMES | [`archetypes.py`](__about/archetypes.md) | THE ARCHETYPE MODE's (pointer, wheel) grid already answers what those arms show |
| THE UMBRA WHEEL | **NEW** [`umbra.py`](__about/umbra.md) | the largest section in the old file (31 names) and one subject: what the band of shadow looks like right now |
| WHEEL SLOTS · WHEEL ARM OFFSETS | [`registry/slots.py`](registry/__about/slots.md) | THE SLOT REGISTRY now holds BOTH slot vocabularies — the three DIAL slots and the three WHEEL slots — so the word's two meanings are in one place instead of colliding across two |
| THE CUBE LOOK | [`cube.py`](__about/cube.md) | the Cube canon's own module |
| SOUTH SLOT & COMPLICATIONS · EARTH MARKER STYLE | **NEW** [`complications.py`](__about/complications.md) | what a slot may SHOW; its twin `registry/slots.py` says only which `Settings` field each slot stores the answer in |
| RING FINISHES & METAL SHADES · SUBDIAL PLATES · RING OUTERS, INNERS & LETTERS · THEME METAL LOOKS | **NEW** [`ring.py`](__about/ring.md) | THE RING VOCABULARY ([The Dial](../../docs/DIAL.md#ring-vocabulary)) — the ring's declarative half; its GEOMETRY stays in `dial.py`, which owns everything measured in pixels |
| THE NINTH TABLES · NINTH MECHANISMS · DUAL/NINTH TIME WINDOW | **NEW** [`ninth.py`](__about/ninth.md) | the seat outside the circle; the window rides with the tables because it decides WHICH FACE the centre seat wears, which is not geometry |
| ZODIAC & CHINESE CALENDAR | **NEW** [`zodiac.py`](__about/zodiac.md) | both answer "which sign is this instant in" and are ridden by the same seats |
| GLOW WINDOWS & ECLIPSE VISIBILITY | [`glow.py`](__about/glow.md) | the module already owns the whole eclipse type→render-state machine |
| TRANSLATION LANGUAGES · UI SCALE & SATURATION RANGES | **NEW** [`ui_ranges.py`](__about/ui_ranges.md) | every entry answers "what values may the user pick in this control" — see below for why NOT `ui_text.py` |
| DUALITY SEATING | [`doctrine.py`](__about/doctrine.md) | the Two Crosses and the Twenty-Four Fields already live there — canon tables that are neither coordinates nor wheels |

### The three judgement calls the owner left open

- **`HIDDEN_MODE_SECRET` and `ART_SOURCES*` went to `identity.py`.** Both
  identify the BUILD rather than anything drawn: the word that unlocks
  the hidden extras is as fixed a product fact as the mutex name, and the
  art sources say which AI generations of the owner's art this build
  ships. Putting them in a module that imports NOTHING is also what lets
  `config/paths.py` — which resolves the art suffix at every disk
  boundary — read them without reaching back into a sibling that could
  reach forward.
- **`ui_ranges.py` was created rather than folding into `ui_text.py`.**
  `ui_text.py` is THE UI STRING CATALOG: one flat tuple of every
  translatable chrome string plus the `ui()` lookup. A bound is not a
  string. All the two share is that a control reads them; merging would
  have made the catalog a mixed bag the moment a range needed changing.
  The language ROSTER counts as a range for the same reason the zoom
  bounds do — it is the set of values one control may be set to.
- **`GREGORIAN_MONTH_NAMES` stayed with the wedge count** in
  `pointer_geometry.py` rather than moving to `pointer_names.py`: twelve
  wedges and twelve month names are one fact stated twice, and splitting
  them lets the two disagree.

<a id="the-one-deviation"></a>

### The one deviation from the map, and its proof

The owner's map sent **WEEKDAY THEMES** and **THEME BLURBS & ARTICLES**
to `registry/week.py`. Those three names were not tables — they were
one-line aliases of THE REGISTRY's own derived tables:

```python
WEEKDAY_THEMES         = registry.THEMES
WEEKDAY_THEME_BLURBS   = registry.BLURBS
WEEKDAY_THEME_ARTICLES = registry.ARTICLES
```

They could not go to `registry/week.py`: `config/registry/__init__.py`
imports `week.py` (`from config.registry.week import MENU, MENU_TOP,
WEEK`), so a `week.py` that read `registry.THEMES` back would be an
import cycle. Re-deriving them from `WEEK` inside `week.py` instead would
have given one truth two homes — exactly the drift THE REGISTRY was
created to end.

So the three aliases were **deleted** and their 42 call sites in 13 files
now read `registry.THEMES`, `registry.BLURBS` and `registry.ARTICLES`
directly. Each alias's explanatory comment moved to the derivation site
in `registry/__init__.py`, where the table is actually made. A second
name for the same object IS a re-export shim, and this round's whole rule
was that there are none.

The registry-derived tables the owner's map sent to NEW modules —
`ninth.py`'s `WEEKDAY_THEME_NINTHS` family and `ring.py`'s
`METAL_THEMES` — stayed as mapped: those modules CAN import
`config.registry` without a cycle, and each carries a long doctrinal
comment that belongs with its subject rather than with the derivation.

### What this cost, and what it bought

- `config/registry/week.py` is now **987 logic lines** against
  `test_config_cohesion.py`'s 1,000-line wall. It is the tightest module
  in the folder: **the next weekday table added there needs a split, not
  a row.**
- Nothing else in `config/` is near the wall. The eleven new modules run
  from 62 to 420 raw lines.
- `config/paths.py` gained two sibling imports (`identity`, `ring`,
  `sky`) where it had one (`constants`). All three are leaves or import
  only `config.registry`, so `paths → ring → registry` closes without
  touching `paths` again; `python -c "import config.paths"` was run after
  every step of the split.
