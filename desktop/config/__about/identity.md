# Identity

**Script:** [Identity (script)](../identity.py)

## Purpose

What this build IS and calls itself — the fixed strings that name the
product to Windows, to the filesystem and to itself. Nothing here is drawn
and nothing here is user-tunable.

Layer: config — pure Python, no Qt, no wall clock.

## Why it exists

`config/constants.py` carried **38 top-level sections** — app identity,
era notation, weekday bodies, pointer geometry, ring finishes, zodiac,
translation languages, UI scale, seating — under one docstring. That is a
junk drawer, not a directory: nobody could say what the module was ABOUT,
and every session that needed one constant read past thirty-seven
subjects it did not care about. The [OOP audit](../../../docs/AUDIT-OOP-2026-08-18.md)'s
R15 asked for a topic split; the owner ruled on **2026-08-19**, naming
each destination module himself, and this file is one of them.

The move was mechanical and total: each section travelled WHOLE, with
its comments, and every caller was repointed to the real module. **No
re-export shim was left behind** (`rules/CODE.md` — No backward
compatibility), and `config/constants.py` was deleted in the same round.

## Contents

- **The names** — `APP_NAME` ("Watch Academy"), `ORGANIZATION`,
  `SINGLE_INSTANCE_MUTEX` and `APP_USER_MODEL_ID`. The last one exists
  because without an explicit AppUserModelID, Windows groups every
  window this interpreter opens under `python.exe`'s own identity and
  can show ITS icon on the taskbar button.
- **`APP_NAME_LEGACY`** ("DOMY Watch") — the retired product name, kept
  ONLY so the two one-time migrations can still recognise an existing
  install (the `%APPDATA%` folder and the `HKCU\...\Run` value). THE
  RENAMING, owner decree 2026-08-10.
- **`HIDDEN_MODE_SECRET`** — the character sequence that, typed on the
  focused dial, unlocks the hidden extras. It is an identity of the
  BUILD, not a UI range or a dial rule: one string the owner sets.
- **The artwork sources** — `ART_SOURCES`, `ART_SOURCE_DEFAULT`,
  `ART_SOURCE_TITLES`. Which AI generations of the owner's art this
  build ships (`_gem` / `_gpt` filename suffixes) and which one is
  preferred. `config.paths.art_file` resolves the suffix at every disk
  boundary.

## Connections

### Uses
- nothing. This module is a LEAF: it imports no sibling, which is what
  lets `config/paths.py` read `APP_NAME` and `ART_SOURCE_DEFAULT`
  without a cycle.

### Used by
- `main.py` — the single-instance mutex, the legacy user-dir migration
- [App (folder)](../../app/___app.md) — the tray, the window titles,
  the settings store's art-source field, the hidden-mode unlock
- [Paths](paths.md) — `%APPDATA%\\<APP_NAME>` and the art suffix

## Design Decisions

- **Why the art sources sit beside the app names.** They answer the
  same kind of question — what this BUILD is made of — and they are read
  by `paths.py`, which must stay near the bottom of the import order.
  Putting them in a module that imports nothing keeps `paths.py` free of
  any sibling that could reach back.
- **Why the hidden-mode word is not in `ui_ranges.py`.** It is not a
  value the user may pick; it is a fixed property of the build, like the
  mutex name.
