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
chosen `Place` is the only thing the rest of the app ever sees.

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

### Place
WHERE A WATCH IS, as ONE frozen object: `path` (full tuple from
continent to city), `name`, `latitude`, `longitude`, `timezone` (IANA
name), plus a `country` property (the path's country segment, `""` when
the place carries no path).

Named `CityRecord` until 2026-08-16. It became `Place` when it also
became the ONLY way a location can exist: `Settings` used to carry the
same five values as five independent fields, and the Settings dialog
read the name and coordinates from the settings while reading the PATH
off its own combo boxes — so a watch that had never picked a city saved
the alphabetically-first cascade position (Burundi) beside the name
"Belgrade", and the crown drew "BELGRADE BURUNDI". The five fields are
gone; `Settings.place` is one object, and a half-location has nowhere
to be written.

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
- `find_city(name)`: every `Place` whose folded name matches —
  diacritic spellings match their ASCII transliteration ("Niš" finds
  "Nis", "Tromsø" finds "Tromso").

## Functions

- `fold_name(text)`: NFKD-decomposes, strips combining marks, casefolds,
  then maps the single-codepoint letters NFKD cannot decompose (ø, đ,
  ł, …) through `constants.CITY_NAME_TRANSLITERATIONS` — the search-
  folding key shared by `find_city` and the picker's own filter.
- `default_place()`: the Belgrade preset as a whole place, WITH its
  real database path — the factory location and the repair value.
- `place_from_mapping(raw)`: THE ONE DOOR for a location arriving from
  outside the database (a stored `settings.json`, a hand edit, an older
  version's file). Answers with a whole `Place` or with `None`, never a
  partial one. A path naming a different city than `name` is discarded
  rather than trusted; a place left pathless then asks `_resolve_path`
  for the database's own path, so a repaired location comes back WHOLE
  and the crown reads "BELGRADE, SERBIA" instead of falling back to the
  timezone region.
- `_resolve_path(name, latitude, longitude)` (private): the database
  path for a city known only by name and coordinates, matched within
  `_SAME_CITY_DEG` (1.0°, enough to tell Belgrade/Serbia from
  Belgrade/Montana). Empty — an honest answer the crown renders — when
  the name is unknown, the coordinates were hand-tuned away from any
  record, or the database cannot be read.
- `_is_city_leaf(value)` (private): `"latitude" in value`.

## Process-wide, reference counted (owner bug 2026-08-06)

`world_locations.json` is 5.6 MB — the largest bundled JSON — and the
tree it parses to is identical for every watch: only the city each one
PICKS differs. Two Settings dialogs open at once used to hold two
independent parsed trees, and reopening the same dialog reparsed from
scratch every time.

- `shared_locations()` — THE process-wide repository.
- `acquire()` / `release()` — the picker's hold. `load()` stays the
  plain "ensure parsed" every query calls, so it must NOT count as a
  hold.
- The count is why `release()` cannot be a bool: the FIRST picker to
  close must not pull the tree out from under a sibling still open.

Shared does NOT mean resident forever — the last release still frees the
5.6 MB, which was the owner's original intent for this repository.
