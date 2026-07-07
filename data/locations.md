# Locations

**Script:** [Locations (script)](locations.py)

## Purpose
Lazy repository over `world_locations.json` for the location picker and
the CLI selftest. The chosen `CityRecord` will be persisted into settings
by the M6 picker; the widget never re-reads the file afterwards.

## Connections

### Uses
- [Config (folder)](../config/___config.md) — database path
- `_io.load_json_checked`

### Used by
- Location picker dialog (M6), [Core (folder)](../core/___core.md) CLI,
  [Tests (folder)](../tests/___tests.md)

## Classes

### CityRecord
Frozen leaf: full path tuple, name, latitude, longitude, IANA timezone.

### LocationNode
One child at any tree level; `is_city` distinguishes selectable leaves
from navigable groups (continent/subregion/country/admin).

### LocationRepository
- `load()` / `release()`: parse on demand, drop when the picker closes
- `children(path)`: children of any node, shape-classified (mixed depth
  safe); unknown path segments raise `KeyError` with the full path
- `find_city(name)`: folded full walk (search box, CLI) — diacritic
  spellings match the ASCII transliterations in the database ("Niš" →
  "Nis", "Tromsø" → "Tromso")
