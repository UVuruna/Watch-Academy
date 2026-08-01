# Paths

**Script:** [Paths (script)](../paths.py) · **Flow:** [diagram](../__flow/paths.md)

## Purpose

Frozen-safe path resolution — the single place every other module
derives a filesystem path from, never from the current working
directory. Handles both a source checkout and a PyInstaller `--onedir`
bundle (PyInstaller 6 places bundled data in `_internal/` and exposes
it via `sys._MEIPASS`).

Also hosts the ART SOURCE resolver (Gemini vs ChatGPT generations
coexisting on disk, owner 2026-07-14) and the per-watch DISPLAY
CONTEXT (art source, subdial set, metal shades) — a thread-local
bundle so multiple open watches, and a background warm thread, never
see each other's art choices.

Layer: config — pure, no Qt, no wall clock.

## Contents

### Bundled-resource roots
- `app_root()` — `sys._MEIPASS` when frozen, else two parents up from
  this file.
- `database_dir()`, `assets_dir()`, `bundled_skins_dir()`.
- `preview3d_gadget_dir()` — the sibling 3D Preview gadget's repo root
  (a monorepo-relative guess), `None` when absent or frozen — the
  documented fallback the Cube pages' 2D drawer keeps.
- `deep_time_path()` — the optional Deep Time data pack.

### Per-user state
- `user_dir()` — `%APPDATA%/DOMY Watch`.
- `settings_path(watch_index=1)` — watch 1 keeps `settings.json`, watch
  N (2+) gets `settings.<N>.json`.
- `discover_watch_indices()` — every watch whose settings file already
  exists on disk, sorted; a brand-new install yields `[1]`.

### The Display Context
- `DisplayContext` — a frozen dataclass: `art_source`, `subdial_set`,
  `metal_shades` (a `MappingProxyType`). One watch's art choices,
  immutable — a settings change builds a NEW context rather than
  mutating the live one.
- `display_context(...)` — the validating factory; raises on an
  unknown art source, subdial set or shade.
- `DEFAULT_DISPLAY` — what a caller outside any watch's scope sees.
- `current_display()` / `display(context)` (context manager) /
  `in_display(method)` (decorator) — the thread-local install/read
  machinery.
- `art_source()`, `subdial_set()`, `metal_shade(metal)` — the
  convenience readers every render call site actually uses.

### Art file resolution
- `ART_SUFFIX` — `{"gemini": "gem", "chatgpt": "gpt"}`, the terminal
  filename suffix per source.
- `art_file(path)` — resolves a canonical (suffix-less) art path to the
  file that actually exists on disk: active source first, the other
  source as cross-source fallback, then the suffix-less name (owner
  hand-made art); returns the canonical path unchanged when nothing
  exists (the caller keeps its own missing-art fallback).

## Connections

### Uses
- [Config (folder)](../___config.md) — `constants` (`ART_SOURCES`,
  `SUBDIAL_SETS`, `METAL_SHADE_NAMES`, `METAL_SHADE_DEFAULT`,
  `DEEP_TIME_DB_FILENAME`, `APP_NAME` — the validation source for
  `display_context`)

### Used by
- Every module in the project that touches disk: [Config (folder)](../___config.md)
  siblings (`pantheon.py`, `continents.py`, `defaults.py`,
  `archetypes.py`, `calendar_mounts.py`), [Render (folder)](../../render/___render.md)
  (`AssetCache`, `asset_recolor`, every layer that resolves art),
  [App (folder)](../../app/___app.md) (`controller.WatchController`,
  `settings_store`, `watch_manager`)

## Classes

### DisplayContext
One watch's art choices. Immutable — carried on the watch's SKIN;
every entry point that resolves art installs it for the duration of
its work via `with paths.display(context):`.

#### Attributes
- `art_source`: `"gemini"` or `"chatgpt"`, default `constants.
  ART_SOURCE_DEFAULT`
- `subdial_set`: one of `constants.SUBDIAL_SETS`
- `metal_shades`: `Mapping[str, str]`, metal → chosen shade name

#### Methods
- `shade(metal)`: this context's shade for `metal`, falling back to
  `constants.METAL_SHADE_DEFAULT[metal]`

## Design Decisions

- **Thread-local, not module-global.** Before this design, the art
  source, subdial set and metal shades were three module globals that
  `apply_display_settings` overwrote on every skin install — last-writer-
  wins across multiple open watches. The owner's report (2026-07-28): a
  DOMY watch and a PILOT watch, both on the `thematic` ring finish, came
  out the SAME RED — DOMY's shade, because DOMY was built last. A
  `DisplayContext` per watch, installed thread-locally for the duration
  of that watch's own paint/hover/dialog work, closes the hazard.
- **`display_context` is the one validating door.** The retired `set_*`
  functions each validated their own argument; centralizing the check
  means an unknown source/set/shade fails loudly at the point of
  choice, not as missing art at paint time.
- **`art_file` never raises on a missing file.** It falls through
  active source → cross-source → suffix-less → the canonical path
  itself, unchanged — the caller (never this module) owns the
  documented missing-art fallback (Rule #1).
