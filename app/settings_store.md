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
recolor), `ring_finish` ("gold" | "silver" | "bronze" letter art), and
the display choices, each validated against its closed
set, `language` ("en" = the shipped originals; any
`TRANSLATION_LANGUAGES` code triggers the translate-once cache), the
element size multipliers `earth_scale` / `moon_scale` / `slot_scale`
(1.0, range 0.5–2.0 — ONE slider for every slot; migrated from the old
`weekday_scale`) and
`hover_enlarge` (1.2, range 1.0–2.0 — the element under the cursor
grows by it; 1.0 disables the effect) (a bad value would otherwise KeyError inside a paint pass, where Qt
swallows exceptions): `pointer` ("hexa"), `umbra_form` ("fine"),
`umbra_contrast` ("full"), `palette_style` ("paint" — on the Calendar
pointer paint = Zodiac wheel, light = Almanac wheel),
`calendar_lighting` ("hour" | "year", owner 2026-07-16),
`archetype_mode` (False — THE ARCHETYPE MODE, owner sealed package
2026-07-16: the diamonds carry the active wheel's archetype figures
and the weekday model and all three slots switch OFF at the render
level only, so every slot key here keeps the user's choice for the
toggle-back), `earth_weekday` (False — the abbreviated day under the
Earth marker's date, a GENERAL Earth option since 2026-07-17 working in
both modes; renamed from `archetype_earth_day`, which the load migrates)
and `z_mode` ("bottom" | "top" — the visibility Z mode, owner 2026-07-17
ROADMAP 15d: below all windows or always on top),
`solar_rotation`
(True), `earth_style` ("clean"), `legend` (True), plus the six
Elements switches (all True: `show_earth`, `show_moon`, `show_weekday`,
`show_pointer`, `colorful`, `show_seconds`). The THREE SLOTS (owner
matrix 2026-07-14): per-slot mode / astrology style / theme —
`weekday_slot`+`weekday_slot_style`+`weekday_theme` (1st),
`octa_slot`+`octa_slot_style`+`info_slot_theme` (2nd),
`third_slot`+`third_slot_style`+`third_slot_theme` (3rd) — with the
enable chain `show_weekday` → `show_octa_slot` → `show_third_slot`,
per-theme metals (`theme_metals`, `theme_metal_follow_ring`) and the
PER-SLOT figure roster (`weekday_roster` / `info_slot_roster` /
`third_slot_roster`, each "planetary" | "pantheon"; owner 2026-07-15:
picked inside the theme's own dropdown like the metals, so slot 1 can
wear Greek Planetary beside slot 2 in Greek Pantheon).
`art_source` ("gemini" | "chatgpt") picks the art world;
`theme_rotation_group` (None or a kinship group / "custom") drives the
daily theme rotation; `subdial_style` ("theme" | "black") picks the
complication plate look (owner A/B spec 2026-07-15). THE YEAR LINE
(Session 16, owner amendment 2026-07-17): `era_notation` ("bce_ce"
default | "bc_ad" — the OFFICIAL labels only; Anno Lucis always
accompanies the official year and is not a mode), `show_era_suffix`
(False — positive years render bare unless opted in) and `third_era`
("none" | "auc" | "byzantine" | "hebrew" | "hegirae" — the optional
third calendar on the line). `jump_cities` (Session 16, owner slika
12): the user's own Quick Jump ▸ Location places — validated
{name, latitude, longitude, timezone} dicts picked from the location
database in Settings. The hidden mode is deliberately NOT here (owner
2026-07-15): the unlock lives per session in the controller. The M6
keys: the location block (`city_name`, `city_path` for combo restore,
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
