# setup/

Build tooling and one-time asset generators. Today it holds the two
data-pack generators that build bundled `Database/*.json`/`*.sqlite`
content from the research extraction; the full M7 build pipeline
(`build.py`, `installer.nsi`, `svg_to_ico.py`, certificates — see the
monorepo root [CLAUDE.md](../../../../CLAUDE.md) Build & Release System)
has not landed here yet.

## Files

| File | Tier | One line |
|------|------|----------|
| `make_deep_time.py` | Algorithmic | builds the gitignored full-span `Database/deep_time.sqlite` from the research events database — [about](__about/make_deep_time.md) · [flow](__flow/make_deep_time.md) |
| `make_observatory.py` | Algorithmic | builds the three committed, decimated Observatory chart bundles — [about](__about/make_observatory.md) · [flow](__flow/make_observatory.md) |
| `make_art_bake.py` | Algorithmic | THE ART BAKERY — downscales and WebP-encodes the gitignored `masters/` inbox into the committed `shared/assets/` tree both platforms read — [about](__about/make_art_bake.md) · [flow](__flow/make_art_bake.md) |
| `make_letter_bake.py` | Algorithmic | bakes the plate library into every EAGER metal/thematic finish under `assets/_baked/letters` — [about](__about/make_letter_bake.md) · [flow](__flow/make_letter_bake.md) |
| `make_contract_pack.py` | Algorithmic | THE BAKERY (ANDROID.md Phase 1) — builds `shared/contract/`: golden test vectors for the Kotlin `:core` port plus JSON exports of the registry tables — [about](__about/make_contract_pack.md) · [flow](__flow/make_contract_pack.md) |
| `app_info.json` | — | installer metadata seed (name/description/version/exe names) — plain config, not a code file |

## Connections

### Uses
- [Research Ephemeris (subfolder)](../research/ephemeris/___ephemeris.md)
  — the events database and companion JSON files both generators read
- `core`, `data`, `config.registry` — `make_contract_pack.py` imports
  the real desktop packages to compute its golden vectors and re-export
  its tables (see its own [about](__about/make_contract_pack.md))

### Used by
- Nobody at runtime — all three scripts are one-time (rerunnable) tools
  the owner runs manually from the command line. `make_deep_time.py`/
  `make_observatory.py`'s outputs are read by
  [Deep Time Repository](../data/__about/deep_time.md) and
  [Observatory Data](../data/__about/observatory.md); see
  [Database (folder)](../../shared/Database/___database.md) for what each
  generated file contains. `make_contract_pack.py`'s output
  (`shared/contract/`) is read by
  [Contract Pack Guard](../tests/___tests.md) (`test_contract_pack.py`)
  and, from Phase 2 on, the Kotlin `:core` port — see the repo-root
  [ANDROID.md](../../ANDROID.md) and [PARITY.md](../../PARITY.md).

## Design Decisions

- **`app_info.json` seeds the M7 naming decision ahead of `build.py`.**
  Session 22 (the Renaming, 2026-07-27) set `name`/`description` to
  **Watch Academy** — the sealed application name (CUBE.md §The Name)
  — while the binaries then stayed DOMY-based; THE RENAMING (owner
  decree 2026-08-10) superseded that split and moved the WHOLE binary
  identity — `exe_name`/`installer_name`
  (`WatchAcademy.exe`/`WatchAcademy_Setup.exe`), mutex, AppUserModelID,
  the migrated %APPDATA% folder — onto the same name. `version` is a static
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
  (`render.asset_recolor.jewel_metal_file`,
  `render.asset_variants.moon_phase_file`) instead of shipped as
  pre-rendered files. This is Rule #19 (Compute, Don't Generate)
  applied retroactively: a recolor/geometry formula replaced a file
  tree.
