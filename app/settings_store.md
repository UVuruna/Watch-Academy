# Settings Store

**Script:** [Settings Store (script)](settings_store.py)

## Purpose
The only module that reads or writes user runtime state:
`%APPDATA%/DOMY Watch/settings.json` (plain JSON — inspectable, diffable,
survives reinstall). Schema v1 holds the window position and diameter
plus the additive keys; the city picker arrives with M6.

## Connections

### Uses
- [Config (folder)](../config/___config.md) — schema version, diameter limits

### Used by
- [App Controller](controller.md)

## Classes

### Settings
Frozen dataclass: `schema_version`, `window_x`/`window_y` (`None` = first
run), `diameter`, plus the additive keys (still schema 1 — absent in
older files they take their defaults): `click_through` (False), `ring`
("domy" — the ring preset), `ring_tint` (None or #RRGGBB — the whole-body
recolor), `ring_finish` ("gold" | "silver" letter art), and the display
choices, each validated against its closed
set, `language` ("en" = the shipped originals; any
`TRANSLATION_LANGUAGES` code triggers the translate-once cache), the
element size multipliers `earth_scale` / `moon_scale` /
`weekday_scale` / `octa_slot_scale` (1.0, range 0.5–2.0) and
`hover_enlarge` (1.2, range 1.0–2.0 — the element under the cursor
grows by it; 1.0 disables the effect) (a bad value would otherwise KeyError inside a paint pass, where Qt
swallows exceptions): `pointer` ("hexa"), `umbra_form` ("fine"),
`umbra_contrast` ("full"), `palette_style` ("paint"), `solar_rotation`
(True), `octa_slot` ("time"), `earth_style` ("clean"), `weekday_theme`
("planets"), `legend` (True), plus the six Elements switches (all True:
`show_earth`, `show_moon`, `show_weekday`, `show_pointer`, `colorful`,
`show_seconds`). The M6 keys:
the location block (`city_name`, `city_path` for combo restore,
`latitude`/`longitude` range-checked, `timezone` verified against
zoneinfo), the opacity overrides `star_alpha`, `aura_day_alpha` and
`aura_twilight_alpha` (null = skin default, else 0..1; the two Aura
values are independent) and `palettes` (custom hues keyed
"pointer_style", every color and count validated).

### SettingsStore
- `load()`: missing file → default `Settings` (documented first-run
  behavior); corrupt file → raises `SettingsCorruptError` — caller must
  surface it visibly
- `save()`: atomic write (tmp + `os.replace`)
- `quarantine()`: renames a corrupt file to `.bak` so defaults can be reseeded

### SettingsCorruptError
Carries the offending path and the original parse error.

## Functions

- `replace(settings, **changes)`: convenience wrapper over
  `dataclasses.replace` for the frozen `Settings` (used by the controller
  when capturing the window position)
