# setup/

Build tooling and one-time asset generators (the full M7 pipeline —
build.py, installer.nsi, svg_to_ico.py, certificates — lands here).

## Files

### `make_silver_letters.py` — Silver Letter Generator
One-time (rerunnable) generator: rasterizes each ACTIVE gold ring
letter at high resolution, desaturates it offline (grayscale with the
alpha kept) and saves `<Stem>_silver.png` beside the gold master in
`assets/ring/letters/`. Run it again whenever a new letter becomes
active in a ring preset (owner decision: silver is pre-rendered art,
not a runtime effect).

### `make_bronze_letters.py` — Bronze Letter Generator
Derives `<Stem>_bronze.png` from each pre-rendered silver letter: a
slight darkening (`BRONZE_LETTER_BRIGHTNESS`) then a straight multiply
with `BRONZE_LETTER_TINT` — the letters are already bright, so the
medallion tritone recipe would blow their detail out (owner direction
2026-07-12). Run AFTER `make_silver_letters.py` whenever a letter
master changes.

## Connections

### Uses
- [Config (folder)](../config/___config.md) — letter file table and art dir

### Used by
- Nobody at runtime — the app loads the generated PNGs like any asset.
