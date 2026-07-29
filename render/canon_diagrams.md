# Canon Diagrams

**Script:** [Canon Diagrams (script)](canon_diagrams.py)

## Purpose

The second wave of the computed-diagram verdict (owner 2026-07-29).
Where [Cube Diagrams](cube_diagrams.md) draws the Cube's geometry, this
module draws what the rest of the doctrine is shaped like — seven pages
from five drawers.

## Connections

### Uses
- [Doctrine](../config/doctrine.md) — the two paths, the two ciphers and
  the twenty-four fields, as data
- [Cube](../config/cube.md) — the thirteen axes behind the term grid
- [Archetypes](../config/archetypes.md) — the Court and Genesis wheels
  the Double Trinity page draws
- [Angles](../core/angles.md) — `ring_position_angle`, the ONE mapping
  every fixed ring hour already shares

### Used by
- [Diagrams](diagrams.md) — the facade a page asks

## The drawers

| Kind | Pages | What it draws |
|---|---|---|
| `crosses` | 3 | the two four-station roads on the hexagram's arms |
| `trinity` | 1 | the Court upright and Genesis inverted, on the same six arms |
| `terms` | 1 | 13 axes × (cold, its fall, warm, its fall) = the 65 |
| `sets` | 1 | the three figure sets and what fills each |
| `fields` | 1 | three persons × four office/process pairs = the 24 |

**One drawer serves all three cross pages.** The stations, the English
mnemonic (FALL / STAR) and the assembled cipher (DOMY / SAFE) are the
SAME two roads read three ways — which is exactly what the three
articles argue, so drawing them three separate ways would have
contradicted the canon rather than illustrated it.

## The chiasm, drawn

```
bright: 08h Hope -> 12h Faith -> 16h Love -> 24h Salvation
dark:   20h Fear -> 24h Anger -> 04h Hate  -> 12h Suffering
```

Each road ends in the OTHER's hour — the bright at midnight, the dark at
noon. The dark road is pulled slightly inward so the two never overdraw
where they share an arm, and they share two: the sharing IS the figure.

## Design Decisions

- **Nothing parses an article.** The stations and fields were prose
  until this wave; they are `config/doctrine.py` now, transcribed once
  from the sealed text, so a diagram reads data like every other drawing
  in this project (Rule #4).
- **The arms come from `core.angles`** — a station stands on a ring hour
  like any other seat, so the page and the dial can never disagree.
- **One table drawer** serves the terms, the sets and the fields
  (Rule #5); cells elide rather than overflow.
