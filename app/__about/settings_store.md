# Settings Store

**Script:** [Settings Store (script)](../settings_store.py) · **Flow:** [diagram](../__flow/settings_store.md)

## Purpose
The only module that reads or writes user runtime state — one plain
JSON file per watch under `%APPDATA%/DOMY Watch/` (inspectable,
diffable, survives reinstall). `SettingsStore` itself is watch-agnostic;
one watch's file-numbering scheme lives in `config.paths`, not here.

**Per-watch file scheme** (ADD WATCH round): watch 1 keeps the
pre-multi-watch `settings.json`; watch N (2+) gets its own
`settings.<N>.json` — `config.paths.settings_path(watch_index)` resolves
either form, and `config.paths.discover_watch_indices()` scans the user
dir at startup for every file that exists, so [Watch Manager](watch_manager.md)
rebuilds the full roster across a restart.

## Connections

### Uses
- [Config (folder)](../../config/___config.md) — schema version, diameter
  limits, `settings_path`/`discover_watch_indices`, every enum table a
  field validates against (`constants`, `dial`, `calendar_mounts`)
- [Rings (data)](../../data/__about/rings.md) — `ring_presets`, `validate_preset`

### Used by
- [Watch Controller](controller.md) — one `SettingsStore` per watch
- [Watch Manager](watch_manager.md) — seeds a new watch's file directly
  before constructing it

## Classes

### Settings
Frozen dataclass — the ONE table of every persisted user choice: window
geometry (`window_x`/`window_y`/`diameter`), visibility Z mode
(`z_mode`), the ring preset/tint/finish and its per-preset metal-split
and eye-shine dicts, the pointer/palette/umbra/calendar-mount choices,
the Pointers REWORK phase-1 quartet (`pointer_shape`, `polygon_curvature`,
`polygon_edge`, `hide_night_borders`), the three Slots (mode/style/theme/
roster each), theme rotation, art source, metal shades, translation
language, the year-line trio (`era_notation`/`show_era_suffix`/`third_era`),
`jump_cities`, the location block, every element-size/saturation slider,
opacity overrides and custom palettes. See `__flow/settings_store.md`
for the full field tree.

### SettingsStore
- `load() -> Settings`: missing file → default `Settings` (documented
  first-run behavior); corrupt/unreadable file → raises
  `SettingsCorruptError` — the caller must surface it visibly (Rule #1),
  never reset silently. Every enum field is checked against its closed
  set (`ValueError` on an unknown value — a bad value would otherwise
  `KeyError` deep inside a paint pass, where Qt swallows exceptions).
- `save(settings)`: atomic write (`tmp` + `os.replace`)
- `quarantine() -> Path`: renames a corrupt file to `.bak` (overwriting
  an older one) so a fresh default file can be reseeded

### SettingsCorruptError(Exception)
Carries the offending `path` and the original parse/validation `cause`.

## Functions
- `replace(settings, **changes) -> Settings`: convenience wrapper over
  `dataclasses.replace` for the frozen dataclass
- `rotation_themes(settings) -> tuple[str, ...]`: the themes the daily
  rotation cycles — a kinship group from `pantheon.WEEKDAY_MENU_GROUPS`,
  the custom checkbox list, or none at all

## Design Decisions
- **External user data gets migration, never a compatibility shim in
  code** (Rule #6 governs code, not files already on disk). `load()`
  carries a dozen one-time migrations inline — old ring preset names
  (`_LEGACY_RING_NAMES`/`_fold_ring_name`), the retired `paint`/`light`/
  `cube` wheel-slot words (`RETIRED_SLOTS`/`_migrate_palette_key`), the
  old South-slot combined values (`legacy_slot`), the old bool pair for
  `earth_label` (`_load_earth_label`), and the `palette_saturation` →
  `pointer_saturation` rename — each documented at its own call site
  rather than collected in one changelog, so the reason lives beside the
  code that still needs it.
- **A hand-edited `"false"` string is corruption, not `True`**
  (`_load_bool`): a real JSON boolean or absent only — never coerced.
