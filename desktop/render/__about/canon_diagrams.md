# Canon Diagrams

**Script:** [Canon Diagrams (script)](../canon_diagrams.py) · **Flow:** [diagram](../__flow/canon_diagrams.md)

## Purpose
The second wave of the computed-diagram verdict (owner 2026-07-29).
Where [Cube Diagrams](cube_diagrams.md) draws the Cube's own geometry,
this module draws what the rest of the doctrine is shaped like — seven
Encyclopedia pages from five drawers, all computed from
`config.doctrine`/`config.cube`/`config.archetypes` data, never from
prose.

## Connections

### Uses
- [Config (folder)](../../config/___config.md) — `doctrine` (the two
  paths, the two ciphers, the twenty-four fields), `cube` (the thirteen
  axes), `archetypes` (the Court/Genesis wheels)
- [Core (folder)](../../core/___core.md) — `angles.ring_position_angle`

### Used by
- [Diagrams](diagrams.md) — the facade a page's `(kind, key)` goes
  through

## The drawers
| Kind | Pages | What it draws |
|---|---|---|
| `crosses` | 3 | the two four-station roads on the hexagram's arms |
| `trinity` | 1 | the Court upright and Genesis inverted, on the same six arms |
| `terms` | 1 | 13 axes × (cold, its fall, warm, its fall) = the 65 |
| `sets` | 1 | the three figure sets and what fills each |
| `fields` | 1 | three persons × four office/process pairs = the 24 |

One drawer serves all three `crosses` pages — the stations, the English
mnemonic and the assembled cipher are the SAME two roads read three
ways.

## Functions
- `crosses(page, size)`: one of the three cross pages.
- `double_trinity(size)`: the Court/Genesis six-arm figure.
- `sixty_five_terms(size)` / `three_sets(size)` / `union_fields(size)`:
  the three table-shaped pages, all through one shared table drawer
  (`_draw_table`).
- `plate(kind, key, size)` / `kinds()`: the module's door, read by
  [Diagrams](diagrams.md).

## Design Decisions
- **Nothing parses an article.** The stations and fields were prose
  until this wave; they are `config/doctrine.py` data now, so a diagram
  reads the same table every other drawing in this project reads
  (Rule #4).
- **The arms come from `core.angles`** — a station stands on a ring
  hour like any other seat, so the page and the dial can never
  disagree.
- **One table drawer serves the terms, the sets and the fields**
  (Rule #5); cells elide rather than overflow.
