# Contract Pack Generator

**Script:** [Contract Pack Generator (script)](../make_contract_pack.py) ·
**Flow:** [diagram](../__flow/make_contract_pack.md)

## Purpose

THE BAKERY (ANDROID.md §The Bakery, Phase 1 of the Pocket Watch charter):
one-time, rerunnable generator that builds `shared/contract/` — the
CONTRACT PACK the future Kotlin `:core` port and every other consumer of
this repo's shared truth reads instead of re-typing it:

```bash
python desktop/setup/make_contract_pack.py
```

Every golden vector is produced by IMPORTING the real `desktop/core`
(pure, no Qt, no wall clock) and calling its actual functions — never
typed by hand. Every table export calls the actual registry the app
itself reads (`config/registry/week.py`, `config/registry/
availability.py`, `config/registry/pointers.py`, `config/palette.py`,
`config/encyclopedia_tree.py`, `data/rings.py`), so a registry edit with
no re-export is exactly what `desktop/tests/test_contract_pack.py` (THE
PARITY LAW's guard, ANDROID.md §parity) catches.

Outputs (into `shared/contract/`):

- `golden_vectors.json` — seven named vector groups (`belgrade_dst`,
  `tromso_regimes`, `moon_illumination`, `mockup_day`, `equinoxes`,
  `hand_angles`, `hexagram_rotation`), each vector carrying `inputs`,
  `expected` and an explicit `tolerance`. Mirrors the exact golden
  values `desktop/tests/test_sun.py`, `test_angles.py`, `test_moon.py`
  and `test_year_wheel.py` already pin — "the port of an algorithm is
  DONE when its vectors are green" (ANDROID.md).
- `tables/week_themes.json` — `config.registry.week.WEEK` verbatim plus
  `MENU`/`MENU_TOP`.
- `tables/availability.json` — the sealed base-pack table
  (`config.registry.availability`).
- `tables/ring_presets.json` — the bundled ring cards, re-serialized
  through `data.rings._bundled_presets()` (the same loader the app
  itself calls; `shared/Database/ring_presets.json` is already this
  table's one JSON source).
- `tables/pointers.json` — the pointer permission matrix
  (`config.registry.pointers`).
- `tables/palette_numeral_parity.json` — `config.palette.
  NUMERAL_PARITY_COLORS`.
- `tables/encyclopedia_tree.json` — the wholes → cards STRUCTURE
  (`config.encyclopedia_tree`), no article bodies.
- `manifest.json` — `pack_version`, `created_at` (taken from `git log -1
  --format=%cI`, never wall clock), a sha256 per exported file, and the
  list of vector group names.

## Connections

### Uses
- `core.angles`, `core.sun`, `core.moon`, `core.year_wheel` — the pure
  functions every vector calls
- `data.locations`, `data.moon_phases`, `data.seasons`, `data.rings` —
  the repositories that back the vectors and the ring-presets table
- `config.registry.week`, `config.registry.availability`,
  `config.registry.pointers`, `config.palette`, `config.
  encyclopedia_tree` — the registry tables exported verbatim

### Used by
- Nobody at runtime — a one-time (rerunnable) tool the owner/session
  reruns whenever a shared layer changes. Its output is read by
  [Contract Pack Guard](../../tests/___tests.md) (`test_contract_pack.py`)
  and, once Phase 2 opens, the Kotlin `:core` test suite in the Pocket
  Watch repo.

## Design Decisions

- **No new config module.** Every table export reads an EXISTING
  registry module through its own real accessor — this generator never
  authors data, it only re-serializes what the app already treats as
  truth (THE CONFIG SECTION LAW stays untouched; nothing here patches a
  section after its own definition).
- **`tables/ring_presets.json` is a re-export of an already-JSON
  source**, not a hand transcription: `shared/Database/ring_presets.json`
  is itself the bundled cards' one source, loaded by
  `data.rings._bundled_presets()`; the contract-pack copy travels
  through that same function so a future change to the loader (a
  migration, a field rename) is caught by the guard rather than by two
  files silently drifting.
- **`created_at` is git history, never `datetime.now()`.** A pack
  timestamp that can't be reproduced from the repo itself is a claim
  the guard could never verify (root CLAUDE.md's honesty rule).
- **Deliberately no per-theme art baking here.** ANDROID.md's Bakery
  also names "baked art — phone-resolution downscale + WebP,
  recolored HERE" and "Databases as-is". Both are real work with their
  own shape (image pipeline, byte-for-byte binary copies) and are
  recorded as open debt in [PARITY.md](../../../PARITY.md) rather than
  folded into this generator, which stays JSON-only.
