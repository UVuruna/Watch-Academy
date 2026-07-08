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
older files they take their defaults): `click_through` (False), `skin`
("domy"), and the display choices, each validated against its closed
set (a bad value would otherwise KeyError inside a paint pass, where Qt
swallows exceptions): `pointer` ("hexa"), `umbra_form` ("fine"),
`umbra_contrast` ("full"), `palette_style` ("paint"), `solar_rotation`
(True), `octa_slot` ("time").

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
