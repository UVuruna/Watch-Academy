# Database/

Bundled astronomical and location data (shipped with the app). Read
exclusively through the repositories in [Data (folder)](../data/___data.md)
(from M2).

## Files

### `world_locations.json` (~4 MB)
Hierarchy `Continent → Subregion → Country → [Admin?] → City`; 45,649 cities,
each with `latitude`, `longitude` and an IANA `timezone`. MIXED depth: 121 of
241 countries have both direct-city children and admin-nested children.
Curated 2026-07: the nine chaotic countries (UK 186 counties → 12 ITL1
regions, Japan 47 prefectures → 8 regions, Russia → 8 federal districts,
Turkey → 7, Thailand → 6, Romania → 8, Philippines/Vietnam/Algeria → 3
each) re-nested under standard macro regions; Tokyo's Shibuya-ku
duplicate removed.

### `seasons_utc.json` (~0.5 MB)
Per-year (1560–2640) exact season data: year `start`/`end`/`duration`,
`winter`/`spring`/`summer`/`autumn` (each with `start` instant and
`duration`), `Light`/`Dark` totals. Note: a year's `winter.start` is the
December solstice of that year — the winter that STARTS in it, not the one
it began with.

### `moonPhases_utc.json` (~3 MB)
Principal moon phase instants (UTC), 1551–2649, keyed by year/month.

### `seasons_large.json`
Moved to [Research (folder)](../research/___research.md) — an oversized
variant kept for analysis only, not bundled.

### `symbolism.json`
Machine-readable blurbs of the dial's symbolic cosmology (one to three
sentences per day/god/religion/profession/color/virtue/vice, plus the
axes and philosophy notes). The narrative canon lives in
[DOMY Symbolism](../SYMBOLISM.md); the hexa diamond hover shows the
active theme's blurb via the
[Symbolism Repository](../data/symbolism.md).

## Connections

### Used by
- [Data (folder)](../data/___data.md) — the only readers
- [DOMY Symbolism](../SYMBOLISM.md) — `symbolism.json` is its
  machine-readable companion (no repository yet; future in-app info)
