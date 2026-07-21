# Language & System Section

**Script:** [Language & System Section (script)](language_system_section.py)

## Purpose

`_LanguageSystemSectionMixin` — TWO nav sections sharing one mixin
file (both small, both simple pickers with no cross-group state):
**Language** (Language, Calendar eras groups) and **System** (System
group). Plain-Python mixin (no base class); composed onto [Settings
Dialog](dialog.md)'s `QDialog` shell.

## The groups

- **Language** — all provider languages; the ORIGINALS ride the top
  (owner spec 2026-07-11): English and Serbian Latin ship hand-written
  in the app; everything below the separator machine-translates on
  first pick (internet needed once) and then works offline. The
  Default button jumps back to English (the shipped originals).
- **Calendar eras** (Session 16, owner amendment 2026-07-17; placed
  under Language — the documented call) — the year-line choices: the
  official era labels (BCE/CE default vs BC/AD), the "write the era
  after positive years too" opt-in (default off — the world writes
  "2026" bare), and the optional THIRD calendar combo
  (None/AUC/Byzantine A.M./Hebrew A.M./Anno Hegirae/Huangdi (China)/
  Maya Long Count — the epoch fine print lives in the combo tooltips
  only). Maya is the odd one out — a TRUE day count
  (`core.deep_time.maya_long_count`), not a year offset (see
  [Deep Time](../../core/deep_time.md)). Anno Lucis is NOT an option:
  it always accompanies the official year.
- **System** — Start with Windows (the HKCU Run entry, read live via
  `app.native.autostart_enabled`, applied by the controller on OK)
  plus the VISIBILITY Z mode combo (owner 2026-07-17, ROADMAP 15e): the
  THREE modes — below all windows (the desktop layer, default), a
  normal window (above only while focused), or always on top; the
  controller swaps the window flags on OK via `ClockWidget.set_z_mode`.

`autostart_selected()` is a small public accessor the controller calls
after `exec()` (the autostart checkbox state is read directly, not
folded into `result_settings()`'s `Settings` — it drives a registry
write, not a persisted field).

## Connections

### Uses
- [Config (folder)](../../config/___config.md) — `constants.
  Z_MODES`/`Z_MODE_TITLES`/`ERA_NOTATIONS`/`ERA_NOTATION_TITLES`/
  `THIRD_ERAS`/`THIRD_ERA_TITLES`/`THIRD_ERA_NOTES`/
  `TRANSLATION_LANGUAGES`/`TRANSLATION_ORIGINALS`
- `app.native` — `autostart_enabled()` (deferred import in
  `_build_system_group`)

### Used by
- [Settings Dialog](dialog.md) — the shell's `__init__` calls
  `_build_language_group()`, `_build_era_group()`,
  `_build_system_group()`; `result_settings()` reads
  `self._language_combo`/`_era_combo`/`_era_suffix_check`/
  `_third_era_combo`/`_z_mode_combo`
- [Watch Controller](../controller.md) — calls `autostart_selected()`
  after the dialog closes Accepted

## Classes

### _LanguageSystemSectionMixin
- `_build_system_group() -> QGroupBox`: the autostart checkbox +
  Visibility Z mode combo
- `_build_era_group() -> QGroupBox`: the era labels/suffix/third
  calendar controls
- `autostart_selected() -> bool`: the autostart checkbox's current state
- `_build_language_group() -> QGroupBox`: the language combo + Default
  button
