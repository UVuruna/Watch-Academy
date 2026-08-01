# Build Roster

**Script:** [Build Roster (script)](../build_roster.py) ·
**Flow:** [diagram](../__flow/build_roster.md)

## Purpose

Generates the root [Master Systematics](../../ROSTER.md) (owner 2026-07-15):
every weekday theme's seven figures + Sunday dual + Ninth, the Pantheon vs
Planetary per-seat comparison, the zodiac families (astrology + Chinese) and
the flat badge/emblem groups, each cell checked against the actual files on
disk **per source** (Gemini / ChatGPT) — the one place to see what art is
still missing.

## Usage

```bash
python research/build_roster.py
```

Run from the project root. Regenerate after any theme-table change or art
drop — `ROSTER.md` is a build artifact, never hand-edited.

## Connections

### Uses
- `config.constants`, `config.defaults` — `WEEKDAY_THEME_*` tables,
  `WEEKDAY_PANTHEON`, `WEEKDAY_THEME_NINTHS`, `ZODIAC_*`, `CHINESE_ANIMALS`,
  `METAL_THEMES` — the same live tables the app itself reads (Rule #5: no
  parallel copy)
- Files under `assets/` — existence checks only, per source suffix
  (`_gem`/`_gpt`)

### Used by
- The owner, to see per-source art coverage; nothing in the app imports this
  script — it is a report generator, run by hand

## Functions

- `mark(source, rel)` / `suffix_mark(source, rel)` — ✔ / — for one
  theme-relative or assets-relative path, per source; a miss is recorded in
  the module-level `missing` list
- `theme_dir`, `colored_dir` — resolve a theme's base/colored art directory
- `weekday_sections()` — the seven-seat + dual + Ninth table per weekday
  theme, in `THEME_ORDER`
- `pantheon_sections()` — Pantheon-vs-Planetary candidate coverage for the
  four Pantheon themes (greek/norse/egypt/slavic)
- `zodiac_sections()` — astrology (12 signs + Ophiuchus) and Chinese (12
  animals + the Cat) coverage
- `flat_section()` / `flat_mark()` — the flat Badges/Emblems groups
- `main()` — assembles every section and writes `ROSTER.md`

## Known issue (flagged, not fixed)

`NINTHS` is built from `constants.WEEKDAY_THEME_NINTHS` (the one live
table, per the script's own comment warning against a stale parallel copy)
— this is correct today. No other drift found while reading the current
code.
