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

### `make_moon_phases.py` — Moon Phase Plate Generator
One-time (rerunnable) generator (owner 2026-07-16): renders the
EIGHT moon-phase plates for the Encyclopedia's Moon pages from the
full-moon master, using the dial's own terminator geometry
(half-disc ∪/∖ terminator half-ellipse, the year-marker shadow
color and alpha) — output `assets/moon/<source>/<phase>.png`. Rerun
when the moon master or the shadow tunables change.

### `make_bronze_letters.py` — Bronze Letter Generator
Derives `<Stem>_bronze.png` from each pre-rendered silver letter: a
straight multiply with `BRONZE_LETTER_TINT` (brightness/contrast knobs
exist but sit at 1.0 — the owner's verdict on the live dial: darkened
candidates sat darker than the bronze medallions). Run AFTER
`make_silver_letters.py` whenever a letter master changes.

## Connections

### Uses
- [Config (folder)](../config/___config.md) — letter file table and art dir

### Used by
- Nobody at runtime — the app loads the generated PNGs like any asset.
