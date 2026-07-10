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

## Connections

### Uses
- [Config (folder)](../config/___config.md) — letter file table and art dir

### Used by
- Nobody at runtime — the app loads the generated PNGs like any asset.
