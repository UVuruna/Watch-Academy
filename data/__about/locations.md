# Location Repository

**Script:** [Location Repository (script)](../locations.py) ·
**Flow:** [diagram](../__flow/locations.md)

## Purpose

Lazy repository over the ~4 MB `Database/world_locations.json` for the
location picker and the core CLI selftest. The hierarchy is
`Continent → Subregion → Country → [Admin →] City` with MIXED depth —
121 of 241 countries hold both direct city leaves and admin sub-dicts
in the same children mapping — so every child is classified by SHAPE
(`"latitude" in value` = a city leaf), never by depth. The parsed tree
is loaded only while the picker needs it and released afterwards; the
chosen `CityRecord` is the only thing the rest of the app ever sees.

## Connections

### Uses
- [Config (folder)](../../config/___config.md) —
  `paths.database_dir()`, `constants.CITY_NAME_TRANSLITERATIONS`

### Used by
- [Location Section](../../app/settings_dialog/__about/location_section.md)
  — imports `fold_name` directly
- [Settings Dialog](../../app/settings_dialog/__about/dialog.md) — the
  picker
- [Core (folder)](../../core/___core.md) CLI (`core/__main__.py`)
- [Tests (folder)](../../tests/___tests.md)

## Classes

### CityRecord
Frozen leaf: `path` (full tuple from continent to city), `name`,
`latitude`, `longitude`, `timezone` (IANA name).

### LocationNode
One child at any tree level: `name`, `record` (set only for city
leaves). `is_city` is `record is not None`.

### LocationRepository
- `load()` / `release()`: parse the tree on demand, drop it when the
  picker closes.
- `children(node_path=())`: the `LocationNode` children of any node
  (empty tuple = continents); an unknown path segment raises `KeyError`
  naming the full path and the depth.
- `all_cities()`: `(folded name, display name, path)` of EVERY city —
  one full walk, feeding the picker's live search filter.
- `find_city(name)`: every `CityRecord` whose folded name matches —
  diacritic spellings match their ASCII transliteration ("Niš" finds
  "Nis", "Tromsø" finds "Tromso").

## Functions

- `fold_name(text)`: NFKD-decomposes, strips combining marks, casefolds,
  then maps the single-codepoint letters NFKD cannot decompose (ø, đ,
  ł, …) through `constants.CITY_NAME_TRANSLITERATIONS` — the search-
  folding key shared by `find_city` and the picker's own filter.
- `_is_city_leaf(value)` (private): `"latitude" in value`.
