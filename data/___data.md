# data/

**Planned — implemented in M2.** Three repositories over `Database/*.json` —
the only code that knows the file schemas. Loud failures with the supported
range in the message (Rule #1); plain dataclasses out, no Qt.

## Planned Files

### `locations.py` — Location Repository
LAZY over the 4 MB `world_locations.json` (loaded only while the picker is
open, released after). Must handle MIXED depth: 127 of 241 countries mix
direct-city children with admin-nested children — children are classified by
the presence of a `latitude` field. Yields `CityRecord` — the only thing
persisted after selection.

### `seasons.py` — Seasons Repository
EAGER extract-and-discard at startup; builds `YearAnchors` from season start
instants (careful: `winter.start` belongs to the NEXT winter — never pair
`winter.duration` with the same year's `start`).

### `moon_phases.py` — Moon Phase Repository
LAZY windowed extraction (current year ± boundary months); normalizes
"Last Quarter" → "Third Quarter"; filters non-month keys.

### `_io.py` — Shared Loader
`load_json_checked()` — a plain function, not an ABC (two repositories do
not justify a class hierarchy).

## Connections

### Uses
- [Config (folder)](../config/___config.md) — paths
- [Database (folder)](../Database/___database.md) — the JSON files

### Used by
- [App (folder)](../app/___app.md) — controller (M3) and location picker (M6)
