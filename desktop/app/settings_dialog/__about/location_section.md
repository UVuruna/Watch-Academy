# Location Section

**Script:** [Location Section (script)](../location_section.py) · **Flow:** [diagram](../__flow/location_section.md)

## Purpose

`_LocationSectionMixin` — the **Location** nav section: the cascading
city-picker over the bundled 45,650-city database plus the user's own
**Quick Jump cities** list. Plain-Python mixin (no base class); composed
onto [Settings Dialog](dialog.md)'s `QDialog` shell.

- **Location** — cascading Continent → Subregion → Country → Region → City
  combos over the bundled 45,650-city database (mixed depth: countries may
  hold cities directly AND under admin regions — the Region combo offers
  "—" for the direct ones), a search box that jumps the combos to a found
  city, and lat/lng fine-tune spinboxes (the chosen city fills them; the
  user may nudge them to precise coordinates — the city's IANA timezone is
  kept). Country selection also pins that country's MAJOR cities into the
  results list (`_show_major_cities`: a city named like the last segment of
  its own IANA timezone is that zone's canonical city — flags London for
  the UK for free).
- **Quick Jump cities** (Session 16, owner slika 12) — the user's own places
  for Quick Jump ▸ Location: a search box over the SAME 45k-city machinery
  as the home picker (`fold_name` matching, the same results-list pattern)
  whose pick ADDS to the jump list instead of touching the home combos
  (navigating the home picker to add a jump city would silently change home
  on OK — the deliberate design reason for the separate box), plus the
  current list and a Remove button. Each saved city jumps the OBSERVER
  there; the moment stays. The list itself carries NO height cap (R-29) —
  the enclosing Location page gives this group the layout's stretch
  factor (`dialog.py`'s section table), so it fills every pixel left
  below the Location group instead of sitting capped in empty space.
  Each saved city is a whole `Place`, so a DOUBLE-CLICK (R-32) simply
  REPLACES the dialog's place with it, through the SAME `_apply_place`
  body a home combo pick runs (Rule #5).

## THE STARRED CITY (owner sheet 2026-08-16)

His rules, and they are ONE mechanism rather than three:

- the list holds many cities but ALWAYS at least one, and exactly one
  wears the star — the place the watch is showing right now;
- a city is added from the Location picker ABOVE, so the Add row is a
  BUTTON and not a second search field (there used to be one here, over
  the same 45k cities with the same folding: two ways to name a city on
  one page, one of which silently did not move the watch);
- "Make Main" — and a double-click — move the star;
- Remove refuses the starred city and the last remaining one, and says
  so by DISABLING itself rather than declining after the click.

The star is not a flag stored beside the list: `self._place` IS the
starred city (`_is_main` compares them) and `_refresh_jump_list` seeds
the list from it when absent. One answer to "where is this watch",
rendered — never a second copy that could drift, which is exactly how
`city_path` drifted away from `city_name`.

## THE COMBOS ARE NAVIGATION (owner decree 2026-08-16)

`self._place` — one `data.locations.Place` — is this section's answer,
and `_apply_place()` is the only thing that writes it. The
Continent/Subregion/Country/Region/City combo boxes walk the user to a
record and are NEVER read back to build the result.

They used to be. `result_settings()` took the name and coordinates from
the stored settings but the PATH from `_current_path()`, i.e. from
wherever the cascade happened to sit — and on a watch that had never
picked a city the cascade sits on the alphabetically first entry,
Africa ▸ Eastern Africa ▸ Burundi ▸ Bubanza. Pressing OK without
touching anything therefore saved Burundi's path beside the name
"Belgrade", and the crown drew "BELGRADE BURUNDI". Two further guards
follow from the same rule: `_on_city()` returns unless
`_suggestions_armed` (the construction cascade is not a user pick), and
`_apply_place()` blocks the coordinate spin boxes' signals so seeding
them is not mistaken for a hand tune.

A hand-tuned coordinate (`_on_coordinate_tuned`) keeps the name and the
zone but DROPS the path: those coordinates are no longer the database
record that path names, and a path that no longer describes its own
place is the very lie this design exists to make unwritable.

`_current_place()` and `_restore_path()` (walking the combos to the
stored place on open, presentation only) are called from the shell's
`__init__`/`result_settings()` across the mixin boundary — resolved via
ordinary attribute lookup since both classes compose onto the same
`self`.

## Connections

### Uses
- [Locations](../../../data/__about/locations.md) — `LocationRepository` (owned by
  the shell), `fold_name` (the search folding used here and by the Quick
  Jump search)
- [Config (folder)](../../../config/___config.md) — `constants.LATITUDE_RANGE`/
  `LONGITUDE_RANGE`

### Used by
- [Settings Dialog](dialog.md) — the shell's `__init__` calls
  `_build_location_group()`/`_build_jump_cities_group()` and
  `_restore_path()`; `result_settings()` calls `_current_place()`

## Classes

### _LocationSectionMixin
- `_build_location_group() -> QGroupBox`: the Location group (combos +
  search + lat/lng)
- `_fill(combo, path, cities=False)`: repopulates one combo from the
  location tree at `path`
- `_group_path() -> tuple[str, ...]`: the navigable path up to (and
  including) the Region combo
- `_on_level(level)`: repopulates everything below the changed combo
- `_show_major_cities()`: pins a country's IANA-canonical cities into the
  results list on country change
- `_on_city()`: hands the selected city's whole record to
  `_apply_place` — a no-op until `_suggestions_armed`, so the
  construction cascade can never become the watch's place
- `_apply_place(place)`: the ONE body that lands a `Place` on this
  dialog — `_on_city()` and `_apply_jump_city_as_location()` (R-32)
  both call it; blocks the coordinate spin boxes' signals while seeding
  them
- `_restore_path(path)`: re-selects a stored city path on dialog open
- `_filter_cities(text)`: live search over all 45k cities
- `_fit_results()`: wraps the suggestion box height to its row count
- `_pick_result(item)`: jumps the combos to a clicked search result
- `_restore_search(path)`: walks the combos to a found city
- `_on_coordinate_tuned()`: a hand-typed coordinate — keeps name and
  zone, drops the path
- `_current_place() -> Place`: this dialog's answer on OK, straight from
  `self._place`; never assembled from the combos
- `_build_jump_cities_group() -> QGroupBox`: the Quick Jump cities group
- `_is_main(city)`: is this the STARRED city — i.e. `self._place`
- `_add_jump_city()`: adds the city the Location picker above shows
- `_remove_jump_city()`: removes the selected row — never the starred
  one, never the last one
- `_make_main_selected()` / `_make_main(city)`: the star moves, through
  `_apply_place`
- `_refresh_jump_buttons()`: both buttons say what they can do BEFORE
  they are pressed
- `_apply_jump_city_as_location(item)`: R-32 — double-click applies the
  clicked jump-list row as the location, via `_apply_place`
- `_refresh_jump_list()`: repaints the jump list from `self._jump_cities`
