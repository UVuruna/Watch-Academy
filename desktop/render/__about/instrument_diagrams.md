# Instrument Diagrams

**Script:** [Instrument Diagrams (script)](../instrument_diagrams.py) · **Flow:** [diagram](../__flow/instrument_diagrams.md)

## Purpose
The clock explaining itself. Twelve Encyclopedia pages carry a figure of
the instrument's OWN behaviour, and every one is drawn live from the
same numbers the dial is drawn from — never painted, so a moved
constant can never leave a stale illustration on the page (root Rule
#19's derivation check, applied to documentation art).

| Figure | What it shows | Where its numbers come from |
|---|---|---|
| `dial` | 24 hours on ONE turn, both hands at a sample moment | `constants.DIAL_OFFSET_DEG`, `core.angles` |
| `solar_rotation` | the hexagram tipped to true solar noon | the project's own golden tilt |
| `world_modes` | the two modes at the same tilt — one turns the star, the other the world | `core.world.world_offset_deg` / `pointer_rotation_deg`, `dial.WORLD_MODE_LABELS` |
| `twilight` | the three bands at their real depressions | `constants.CIVIL_DEPRESSION` + the band table |
| `year_wheel` | four equal quarters, each anchor at its real instant | `PALETTE_PRESETS[("cross", "tertiary")]` |
| `moon_lunations` | eight phases around the wheel, terminator and all | `core.angles.moon_cycle_angle`, `MOON_PHASE_NAMES` |
| `metals` | gold at noon, silver at midnight; three finishes below | `ENCYCLOPEDIA_FINISH_BORDER_COLORS` |
| `ring_jewels` | Δ·M·Y·Ω at the hour of its alphabet place | `doctrine.RING_JEWEL_SEATS`, `angles.ring_position_angle` |
| `ring_presets` | the six bundled seatings — each outer's EMPTY fields against the seats a numeral fills | `data.rings.ring_presets`, `constants.RING_OUTERS` |
| `pointers` | the seven pointers at their own arm counts and default hues | `constants.POINTER_*`, `palette.PALETTE_PRESETS` |
| `oscillations` | the La2004 amplitude envelope over ±200,000 years | `data.observatory.ObservatoryData.laskar_envelope()` |
| `chi` | the real `"full"` outer band plate, X seated at 24h in its own ceramic finish | `render.numeral_bands.band_plate`, `render.assets.shared_cache`, `constants.RING_THEMATIC_SHADES["CHI"]` |

`chi` is the one figure among the twelve that is not a sketch of the
program's geometry: every other drawer reads the SAME angles/values the
dial reads but paints them with this module's own primitives
(`_on_dial`, `_text`, plain pens); `chi`'s article is about what a real
recolored finish looks like, so it composes the ACTUAL outer plate
(`render.numeral_bands.band_plate`, the fidelity engine `render.layers.
ring.RingLayer` blits on the live dial) and recolors the real X master
through the real asset cache (`render.assets.shared_cache`) — a
schematic X would not teach "ceramic" at all.

## Connections

### Uses
- [Config (folder)](../../config/___config.md) — every constant and
  palette the figures read
- [Core (folder)](../../core/___core.md) — `angles`, the one dial-angle
  mapping
- [Observatory Data](../../data/__about/observatory.md) — the La2004
  envelope bundle (the `oscillations` figure alone)
- [Numeral Bands](numeral_bands.md) — `band_plate`, the outer plate's
  own fidelity engine (the `chi` figure alone)
- [Assets](assets.md) — `shared_cache`, the process-wide recolor cache
  (the `chi` figure alone)

### Used by
- [Diagrams](diagrams.md) — the one door a page's `(kind, key)` goes
  through
- `app.encyclopedia.tree` — imports `INSTRUMENT_FIGURES` so a page can
  only declare a figure that exists

## Design Decisions
- **One kind, `"instrument"`; the KEY names the figure.** The facade
  routes by kind, so this module answers exactly one kind with twelve
  keys.
- **`INSTRUMENT_FIGURES` is the single source of truth** — the topic
  tree imports it instead of keeping a parallel list (Rule #5).
- **Labels are measured, not guessed** (`_text` reads
  `QFontMetricsF`) — a guessed width once clamped short labels ("06h")
  to the middle of the figure.
- **The ink is the app's own theme colour**, so the figures read on the
  Encyclopedia's dark surface and follow a re-themed palette.
- **The three ROW figures are drawn WIDE, not square** (2026-08-13,
  THE SPACE & LEGIBILITY LAW). A square master could only ever be
  granted the reader's height ceiling, so ring presets, pointers and
  world modes arrived on screen ~208 px wide inside a ~1123 px text
  column, their own caption line illegible and 915 px of that column
  empty. They are now ONE ROW on a canvas shaped like the space they
  are given (`INSTRUMENT_DIAGRAM_GRIDS` declares columns, label lines
  and aspect); the reader's width bound then decides their size and the
  same tiles arrive four to five times larger. `_Row` owns the whole
  derivation: the height is the width over the aspect, the margins,
  label stack and caption band take their declared shares of it, and
  the tile RADIUS is exactly what is left — add a label line and the
  circles shrink to make room, so nothing can overlap.
- **A tile's own details are ratios of its RADIUS**, never of the
  plate — seat dots, ring pens, arm outlines. That is what let the
  three figures be reshaped without redrawing a single tile.
- **They still label sparingly.** Everything countable (the numeral
  tally, the wheel names per pointer) stays in the ARTICLE beside the
  figure rather than crowded into a tile.
- **A caption SHRINKS TO FIT, never clips.** `_caption` word-wraps
  inside its band and steps the font down until the drawn text fits
  both dimensions. Before that, a caption longer than the plate was
  drawn straight past both edges and lost its first and last words in
  silence — the exact failure the law names.
- **Aurora is a STRIP, not a wheel.** Its seven hues run across the real
  sunrise-to-sunset arc, whose width changes with the season; seven
  equal wedges of a 24 h face would state a seating that does not
  exist.
