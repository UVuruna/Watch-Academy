# Graph Years

**Script:** [Graph Years (script)](../graph_years.py)

## Purpose

Exploratory matplotlib plotting of the season/year duration dataset —
deviation from the mean, across the −13000…+17000 span, for the light/dark
halves, the four seasons and the whole year. A quick-look companion to the
ephemeris pipeline's numbers; not a maintained tool (no CLI, no docstring —
which functions run is chosen by editing the calls at the bottom of the
file).

## Usage

```bash
python research/graph_years.py
```

Opens interactive matplotlib windows. Which graphs are drawn is controlled
by which `singleY_graph(...)` / `multiY_graph(...)` calls are left
uncommented at the bottom of the file.

## Connections

### Uses
- Intends to read `research/seasons_large.json` (the extended season
  dataset also described in [Research (folder)](../___research.md)) — see
  the bug note below
- `matplotlib`, `numpy`

### Used by
- Nobody; ad hoc, run manually for a quick chart

## Known issue (flagged, not fixed)

Line 6 opens `'Database/seasons_large.json'`, but no such file exists —
`Database/` never held it. The actual data lives at
`research/seasons_large.json` (confirmed on disk, ~11 MB). Running the
script from the project root today raises `FileNotFoundError` before any
plotting happens. Likely a stale path left over from before the file moved
into `research/`; not fixed here per this migration's docs-only scope.
