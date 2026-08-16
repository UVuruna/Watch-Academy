# app/settings_fields.py

The per-field validators and the stored-data migrations every key of
`settings.json` passes through on its way in.

## Purpose

`app/settings_store.py` was holding two responsibilities at once: the
`Settings` TABLE plus its atomic file I/O, and the rules that decide
whether a stored value is acceptable. THE STRUCTURE LAW forced the
question when the live numeral bands added their own settings, and the
answer was to split the second responsibility out rather than to keep
growing one file.

What lives here:

- **Shape validators** — `load_bool` (a real JSON boolean, because a
  hand-edited `"false"` string would otherwise coerce to True silently),
  `load_scale` (a number inside its declared range), `load_alpha` (an
  opacity override that may be null), `load_hex` (`#RRGGBB`),
  `load_choice` (a closed vocabulary), `load_palettes` (a custom palette
  with the right number of valid hues).
- **External-data migrations** — `load_earth_label` (the old
  `show_earth_date`/`earth_weekday` bool pair folded onto the label
  enum), `load_rotation_group` (the pre-2026-07-14 Enabled checkbox),
  `migrate_palette_key`/`RETIRED_SLOTS` (the wheel slots renamed
  2026-07-28), `MERGED_MOUNTS` (a calendar mount that was absorbed by
  another) and `RETIRED_SLOT_MODES` (a slot MODE that was renamed).
  These exist so a settings file written by an older release loads clean
  instead of reading as corrupt and offering the user a reset.

  `RETIRED_SLOT_MODES` was written the day the rule proved itself:
  `"astrology"` was a legal `weekday_slot` from 0.14.159 ("the weekday
  POSITION can now carry an astrology badge instead of the bodies —
  Bodies / Astrology / Ascendant"), the mode list later renamed it
  `"zodiac"`, and nobody wrote the migration. It was found on
  2026-08-16 in the OWNER'S OWN live file, which had been reading as
  corrupt on every launch and offering him the one button that throws
  away every stored watch. The mechanism was already here; the entry
  was missing. Tooth:
  `desktop/tests/test_settings_migrations.py`, which also checks that
  every retired name in every one of these tables lands on a value the
  program still accepts.
- **`load_numerals` / `save_numerals`** — the live numeral bands' own
  group, as one list read on the way in and on the way out, so a field
  can never be loaded and then silently not saved.

## The one rule everything here obeys

An absent key is the documented default; a PRESENT key that is wrong is
CORRUPT and says so by raising. Nothing is quietly coerced — a settings
file naming a roster face that no longer exists must surface, not
silently become another face the user never chose (Rule #1).

Nothing here knows the settings FILE exists: every function takes the
raw parsed dict and answers with a validated value.

## Connections

### Uses
- `config.constants`, `config.dial`, `config.pantheon` — the
  vocabularies and ranges being validated against

### Used by
- [Settings Store](settings_store.md) — the only caller
