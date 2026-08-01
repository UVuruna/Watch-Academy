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
| `calendar_mounts.py` | Algorithmic | the Calendar pointer's wedge geometry and THE CALENDAR MOUNT REGISTRY (every roster that may ride the twelve wedges) — [about](__about/calendar_mounts.md) · [flow](__flow/calendar_mounts.md) |
| `constants.py` | Algorithmic | product-defining invariants — dial identity, eras, pointer/wheel tables, the weekday-theme master list, THE BLUE MOON/AXLE LAW — [about](__about/constants.md) · [flow](__flow/constants.md) |
| `continents.py` | Algorithmic | THE CONTINENTS theme's region roster and day/night Earth-face resolvers — [about](__about/continents.md) · [flow](__flow/continents.md) |
| `cube.py` | Algorithmic | the Character Cube's canon table — thirteen axes, the 108+48-seat roster, the two seatings — [about](__about/cube.md) · [flow](__flow/cube.md) |
| `defaults.py` | Algorithmic | developer tunables that fit no single peer module, plus the cross-module coordinators (`DEFAULT_SKIN`, window-margin math) — [about](__about/defaults.md) · [flow](__flow/defaults.md) |
| `dial.py` | Algorithmic | dial geometry and window sizing — ring band, hand reach, subdial/slot seating — [about](__about/dial.md) · [flow](__flow/dial.md) |
| `doctrine.py` | Algorithmic | the Two Crosses and the Twenty-Four Fields — canon tables neither coordinates nor wheels — [about](__about/doctrine.md) · [flow](__flow/doctrine.md) |
| `encyclopedia_tree.py` | Algorithmic | the Encyclopedia's three-level tree — nine Wholes, theme cards, variant switcher loops — [about](__about/encyclopedia_tree.md) · [flow](__flow/encyclopedia_tree.md) |
| `encyclopedia_ui.py` | Algorithmic | the reading surfaces — article/legend sizing, term-highlight patterns, the computed diagrams — [about](__about/encyclopedia_ui.md) · [flow](__flow/encyclopedia_ui.md) |
| `glow.py` | Algorithmic | event glow windows and the whole eclipse type→render-state machine — [about](__about/glow.md) · [flow](__flow/glow.md) |
| `palette.py` | Algorithmic | THE COLOUR LAW — every colour in the program, nine fixed sections, nothing else — [about](__about/palette.md) · [flow](__flow/palette.md) |
| `pantheon.py` | Algorithmic | the weekday theme registry and THE UNIVERSAL ROTATION CONVENTION engine — [about](__about/pantheon.md) · [flow](__flow/pantheon.md) |
| `paths.py` | Algorithmic | frozen-safe path resolution, the art-source suffix resolver, the per-watch thread-local Display Context — [about](__about/paths.md) · [flow](__flow/paths.md) |
| `profiling.py` | Algorithmic | `@timed`/`measure()` execution-time statistics behind the hidden Report — [about](__about/profiling.md) · [flow](__flow/profiling.md) |
| `shortcuts.py` | Algorithmic | the keyboard shortcut table and Fast Travel's theme/option jumps — [about](__about/shortcuts.md) · [flow](__flow/shortcuts.md) |
| `taxonomy.py` | Algorithmic | THE ONE HIERARCHY — five categories → groups → weekday themes — [about](__about/taxonomy.md) · [flow](__flow/taxonomy.md) |
| `ui_text.py` | Algorithmic | the UI text catalog — every translatable chrome string, one flat tuple — [about](__about/ui_text.md) · [flow](__flow/ui_text.md) |
| `winapi.py` | Standard | Win32 API literals and the keyboard-hook ABI, the one enum-exception to Rule #4 — [about](__about/winapi.md) |

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
  36 (THE CONFIG SPLIT, [Work Plan Structure](../WORKPLAN-STRUCTURE.md))
  carved `dial.py`, `shortcuts.py`, `pantheon.py`, `calendar_mounts.py`,
  `encyclopedia_ui.py` and `glow.py` out of a ~3,700-line
  `defaults.py` god-file as PEERS that may import only `paths`/
  `constants`/`palette` and never each other; `continents.py` is
  `pantheon.py`'s own deterministic fallback (a subordinate, not a
  seventh peer); `defaults.py` itself is the one remnant allowed to
  import every peer downhill, holding whichever coordinator value
  needs more than one peer's data. The older files this DAG rule does
  NOT bind (`archetypes.py`, `cube.py`, `doctrine.py`, `encyclopedia_
  tree.py`, `taxonomy.py`, `ui_text.py`, `winapi.py`, `constants.py`)
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
