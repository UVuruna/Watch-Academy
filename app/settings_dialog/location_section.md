# Location Section

**Script:** [Location Section (script)](location_section.py)

## Purpose

`_LocationSectionMixin` — the **Location** nav section: the cascading
city-picker over the bundled 45,650-city database plus the user's own
**Quick Jump cities** list. Plain-Python mixin (no base class); composed
onto [Settings Dialog](dialog.md)'s `QDialog` shell.

## The groups

- **Location** — cascading Continent → Subregion → Country → Region →
  City combos over the bundled 45,650-city database (mixed depth:
  countries may hold cities directly AND under admin regions — the
  Region combo offers "—" for the direct ones), a search box that jumps
  the combos to a found city, and lat/lng fine-tune spinboxes (the
  chosen city fills them; the user may nudge them to precise
  coordinates — the city's IANA timezone is kept). Country selection
  also pins that country's MAJOR cities into the results list
  (`_show_major_cities`: a city named like the last segment of its own
  IANA timezone is that zone's canonical city — flags London for the UK
  for free).
- **Quick Jump cities** (Session 16, owner slika 12) — the user's own
  places for Quick Jump ▸ Location: a search box over the SAME
  45k-city machinery as the home picker (`fold_name` matching, the
  same results-list pattern) whose pick ADDS to the jump list instead
  of touching the home combos (navigating the home picker to add a
  jump city would silently change home on OK — the deliberate design
  reason for the separate box), plus the current list and a Remove
  button. Each saved city jumps the OBSERVER there; the moment stays.

`_current_path()` (the combo cascade's current selection) and
`_restore_path()` (re-selecting a stored city path on open) are called
from the shell's `__init__`/`result_settings()` across the mixin
boundary — resolved via ordinary attribute lookup since both classes
compose onto the same `self`.

## Connections

### Uses
- [Locations](../../data/locations.md) — `LocationRepository` (owned by
  the shell), `fold_name` (the search folding used here and by the
  Quick Jump search)
- [Config (folder)](../../config/___config.md) — `constants.
  LATITUDE_RANGE`/`LONGITUDE_RANGE`

### Used by
- [Settings Dialog](dialog.md) — the shell's `__init__` calls
  `_build_location_group()`/`_build_jump_cities_group()` and
  `_restore_path()`; `result_settings()` calls `_current_path()`

## Classes

### _LocationSectionMixin
- `_build_location_group() -> QGroupBox`: the Location group (combos +
  search + lat/lng)
- `_fill(combo, path, cities=False)`: repopulates one combo from the
  location tree at `path`
- `_group_path() -> tuple[str, ...]`: the navigable path up to (and
  including) the Region combo
- `_on_level(level)`: repopulates everything below the changed combo
- `_show_major_cities()`: pins a country's IANA-canonical cities into
  the results list on country change
- `_on_city()`: fills lat/lng/timezone from the selected city's record
- `_restore_path(path)`: re-selects a stored city path on dialog open
- `_filter_cities(text)`: live search over all 45k cities
- `_fit_results()`: wraps the suggestion box height to its row count
- `_pick_result(item)`: jumps the combos to a clicked search result
- `_restore_search(path)`: walks the combos to a found city
- `_current_path() -> tuple[str, ...]`: the combo cascade's current
  full path
- `_build_jump_cities_group() -> QGroupBox`: the Quick Jump cities group
- `_filter_jump_cities(text)`: live search feeding the jump results list
- `_add_jump_city(item)`: appends a picked city to the jump list
- `_remove_jump_city()`: removes the selected jump-list row
- `_refresh_jump_list()`: repaints the jump list from `self._jump_cities`
