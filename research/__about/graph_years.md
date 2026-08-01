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
- Reads `research/seasons_large.json` (the extended season dataset also
  described in [Research (folder)](../___research.md)), resolved via
  `Path(__file__).resolve().parent` — same-directory, frozen-CWD-safe,
  matching the sibling research scripts' `Path(__file__)`-based path
  resolution (e.g. `seating_preview.py`'s `OUT_DIR`)
- `matplotlib`, `numpy`

### Used by
- Nobody; ad hoc, run manually for a quick chart

## Fixed issue (2026-08-01)

Line 6 used to open the raw literal `'Database/seasons_large.json'`, which
never existed — `Database/` never held this file; only
`research/seasons_large.json` does (~11 MB). Running the script from the
project root raised `FileNotFoundError` before any plotting happened —
a stale path left over from before the file moved into `research/`.
Fixed by resolving the path relative to the script's own location instead
of the working directory. Verified: `MPLBACKEND=Agg python
research/graph_years.py` now runs to completion (loads the JSON, builds
both graphs, reaches `plt.show()`) with exit code 0 — `Agg` only avoids
blocking on the interactive window for this headless verification, the
script itself is unchanged in that regard.
