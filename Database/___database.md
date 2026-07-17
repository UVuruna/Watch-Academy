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

### `deep_time.sqlite` (~57 MB, GITIGNORED — Session 16, owner 2026-07-17)
The OPTIONAL full-span Deep Time pack: every solstice/equinox
(~120k), every principal moon phase (~1.5M) and both eclipse catalogs
(~141k, solar with greatest-eclipse geometry) over −12997…+16993,
extracted from the research events database by
`setup/make_deep_time.py` (rerunnable; regenerate locally — the M7
FULL installer bundles it, the partial installation ships without it).
Detected at startup (`config.paths.deep_time_path()`): present → Time
Travel spans the whole pack; absent → the bundled span with the
friendly clamp. Read ONLY by the
[Deep Time Repository](../data/deep_time.md); coverage lives in its
`meta` table (from the data, never hardcoded).

### `seasons_large.json`
Moved to [Research (folder)](../research/___research.md) — an oversized
variant kept for analysis only, not bundled.

### `symbolism.json`
Machine-readable blurbs AND the full encyclopedic `articles` of the
dial's symbolic cosmology (per theme × body with pointer/palette
variant paragraphs, plus zodiac, Chinese, element and trio articles).
The narrative canon lives in [DOMY Symbolism](../SYMBOLISM.md); the
weekday and slot hovers read it via the
[Symbolism Repository](../data/symbolism.md).

### `encyclopedia.json`
The Encyclopedia's OWN content (owner expansion 2026-07-13), separate
from the dial articles: the eight INSTRUMENT functionality articles
(the dial, solar rotation, twilight, the year wheel, lunations,
Paint/Light, metals, the ring letters), the seven WEEK day pages and
the 24 VIRTUES/SINS/MOODS emblem entries. Read by the
[Encyclopedia Repository](../data/encyclopedia.md); translated through
`encyclopedia/<section>/<key>/...` overlay keys.

### `ring_presets.json`
The bundled ring styling cards — DOMY, MORPH and NUMBERS — loaded by
[Ring Presets](../data/rings.md) together with the user's custom cards.

### `translations/`
BUNDLED ORIGINAL translations (owner decision 2026-07-11): English is
the shipped source, `sr-Latn.json` the hand-written Serbian original —
`{hashes: sha1(EN) per key, texts}`, consumed by
[Translations](../data/translations.md); every other language machine-
translates into the user's cache instead.

## Connections

### Used by
- [Data (folder)](../data/___data.md) — the only readers
- [DOMY Symbolism](../SYMBOLISM.md) — `symbolism.json` is its
  machine-readable companion (no repository yet; future in-app info)
