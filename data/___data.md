# data/

Four repositories over `Database/*.json` — the only code that knows the
file schemas. Loud failures with the supported range in the message
(Rule #1); plain dataclasses out; no Qt (enforced by the purity test).

## Files

### `locations.py` — Location Repository
LAZY over the 4 MB `world_locations.json` (45,650 cities; loaded on
demand, released when the picker closes). Handles the MIXED depth — 127
of 241 countries mix direct-city leaves with admin sub-dicts — by
classifying every child by shape (`"latitude" in value`), never by depth.
Yields `CityRecord`, the only thing persisted after selection.
See [Locations](locations.md).

### `seasons.py` — Seasons Repository
Extract-and-discard over `seasons_utc.json` (1560–2640): parses once per
year, keeps a tiny `YearAnchors`, drops the dict. Handles the verified
field trap: a year's `winter.start` is the December solstice OF that year
(ending the entry), while `winter.duration` describes the winter that
BEGAN it — the two are never paired. `coverage()` returns the (first,
last) years straight from the data. See [Seasons](seasons.md).

### `moon_phases.py` — Moon Phases Repository
Windowed extraction over `moonPhases_utc.json` (1551–2649): the target
year plus both neighbors, month keys filtered with `isdigit()` (year
entries mix month dicts with aggregate count keys), "Last Quarter"
normalized to "Third Quarter". `coverage()` returns the (first, last)
years straight from the data. See [Moon Phases](moon_phases.md).

### `symbolism.py` — Symbolism Repository
Per-body blurbs and the full ARTICLE corpus from `symbolism.json` (the
machine-readable companion of [DOMY Symbolism](../SYMBOLISM.md)) — the
hover articles per theme, sign, animal, element and Trinity virtue.
See [Symbolism Repository](symbolism.md).

### `encyclopedia.py` — Encyclopedia Repository
The Encyclopedia's own content from `Database/encyclopedia.json`
(instrument articles, week day pages, virtue/sin/mood entries),
overlay-localized. See [Encyclopedia Repository](encyclopedia.md).

### `translations.py` — Translations
Translate-once-then-cache (owner spec: we ship only English): corpus
collection, the keyless gtx client, the hash-tracked per-language
cache and the Serbian Cyrillic→Latin transliteration.
See [Translations](translations.md).

### `rings.py` — Ring Presets
The ring preset cards (bundled `ring_presets.json` + the user's custom
cards from settings): `{name, positions, letters}`, layouts resolved by
the positions signature, loud validation. See [Ring Presets](rings.md).

### `hands.py` — Hand Packs
The hand packs (owner spec 2026-07-12): a folder of hours/minutes/
seconds images pointing UP plus `hands.json` (name, per-hand pivot,
bottom-up z-order); bundled `assets/hands/<pack>/` + the user's own
packs beside the settings file. See [Hand Packs](hands.md).

### `_io.py` — Shared Loader
`load_json_checked()` — a plain function, not a base class (a few small
repositories do not justify a hierarchy). `year_bounds(data)` reads the
(first, last) integer year keys of a bundled database, so coverage is
never hardcoded (Rule #4) — a Deep Time pack widens the file alone.

## Connections

### Uses
- [Config (folder)](../config/___config.md) — paths and coverage ranges
- [Core (folder)](../core/___core.md) — `YearAnchors`, `MoonWindow`
- [Database (folder)](../Database/___database.md) — the JSON files

### Used by
- [App (folder)](../app/___app.md) — controller (M3), location picker (M6)
- [Core (folder)](../core/___core.md) CLI selftest
- [Tests (folder)](../tests/___tests.md) — run against the LIVE files
