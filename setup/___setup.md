# setup/

Build tooling and one-time asset generators. Today it holds the two
data-pack generators that build bundled `Database/*.json`/`*.sqlite`
content from the research extraction; the full M7 build pipeline
(`build.py`, `installer.nsi`, `svg_to_ico.py`, certificates — see the
monorepo root [CLAUDE.md](../../../CLAUDE.md) Build & Release System)
has not landed here yet.

## Files

| File | Tier | One line |
|------|------|----------|
| `make_deep_time.py` | Algorithmic | builds the gitignored full-span `Database/deep_time.sqlite` from the research events database — [about](__about/make_deep_time.md) · [flow](__flow/make_deep_time.md) |
| `make_observatory.py` | Algorithmic | builds the three committed, decimated Observatory chart bundles — [about](__about/make_observatory.md) · [flow](__flow/make_observatory.md) |
| `app_info.json` | — | installer metadata seed (name/description/version/exe names) — plain config, not a code file |

## Connections

### Uses
- [Research Ephemeris (subfolder)](../research/ephemeris/___ephemeris.md)
  — the events database and companion JSON files both generators read

### Used by
- Nobody at runtime — both scripts are one-time (rerunnable) tools the
  owner runs manually from the command line. Their outputs are read by
  [Deep Time Repository](../data/__about/deep_time.md) and
  [Observatory Data](../data/__about/observatory.md); see
  [Database (folder)](../Database/___database.md) for what each
  generated file contains

## Design Decisions

- **`app_info.json` seeds the M7 naming decision ahead of `build.py`.**
  Session 22 (the Renaming, 2026-07-27) set `name`/`description` to
  **Watch Academy** — the sealed application name (CUBE.md §The Name)
  — while `exe_name`/`installer_name` stay DOMY-based
  (`DOMYWatch.exe`/`DOMYWatch_Setup.exe`), matching the folder/mutex/
  AppUserModelID identity that never changed. `version` is a static
  seed (no single version source wired to runtime code yet — Rule
  #23 does not yet apply here); whoever writes `build.py` bumps it to
  the real release version before packaging. Pinned by
  `tests/test_app_info.py`.
- **Both generators are rerunnable, not append-only.** Each recreates
  its output from scratch on every run (`make_deep_time.py` drops and
  rebuilds the sqlite file; `make_observatory.py` overwrites its three
  JSON files) — safe to rerun after the research extraction changes,
  never accumulates stale rows.
- **The LIVE-RENDER CLEANUP retired three former generators whole**
  (owner decree 2026-07-19, "bolje crtati na licu mesta nego 15MB
  fajlova" — better to draw on the spot than 15MB of files): the ring
  letter metal generators (`make_silver_letters.py` /
  `make_bronze_letters.py`) and the moon phase plate generator
  (`make_moon_phases.py`) are DELETED (Rule #6, no leftovers) — their
  ~22 MB combined output is now computed live and disk-cached
  (`render.asset_recolor.letter_metal_file`,
  `render.asset_variants.moon_phase_file`) instead of shipped as
  pre-rendered files. This is Rule #19 (Compute, Don't Generate)
  applied retroactively: a recolor/geometry formula replaced a file
  tree.
