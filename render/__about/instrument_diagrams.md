# Instrument Diagrams

**Script:** [Instrument Diagrams (script)](../instrument_diagrams.py) · **Flow:** [diagram](../__flow/instrument_diagrams.md)

## Purpose
The clock explaining itself. Nine Encyclopedia pages carry a figure of
the instrument's OWN behaviour, and every one is drawn live from the
same numbers the dial is drawn from — never painted, so a moved
constant can never leave a stale illustration on the page (root Rule
#19's derivation check, applied to documentation art).

| Figure | What it shows | Where its numbers come from |
|---|---|---|
| `dial` | 24 hours on ONE turn, both hands at a sample moment | `constants.DIAL_OFFSET_DEG`, `core.angles` |
| `solar_rotation` | the hexagram tipped to true solar noon | the project's own golden tilt |
| `twilight` | the three bands at their real depressions | `constants.CIVIL_DEPRESSION` + the band table |
| `year_wheel` | four equal quarters, each anchor at its real instant | `PALETTE_PRESETS[("cross", "tertiary")]` |
| `moon_lunations` | eight phases around the wheel, terminator and all | `core.angles.moon_cycle_angle`, `MOON_PHASE_NAMES` |
| `metals` | gold at noon, silver at midnight; three finishes below | `ENCYCLOPEDIA_FINISH_BORDER_COLORS` |
| `ring_jewels` | Δ·M·Y·Ω at the hour of its alphabet place | `doctrine.RING_JEWEL_SEATS`, `angles.ring_position_angle` |
| `oscillations` | the La2004 amplitude envelope over ±200,000 years | `data.observatory.ObservatoryData.laskar_envelope()` |
| `chi` | the real `"full"` outer band plate, X seated at 24h in its own ceramic finish | `render.numeral_bands.band_plate`, `render.assets.shared_cache`, `constants.RING_THEMATIC_SHADES["CHI"]` |

`chi` is the one figure among the nine that is not a sketch of the
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
  routes by kind, so this module answers exactly one kind with nine
  keys.
- **`INSTRUMENT_FIGURES` is the single source of truth** — the topic
  tree imports it instead of keeping a parallel list (Rule #5).
- **Labels are measured, not guessed** (`_text` reads
  `QFontMetricsF`) — a guessed width once clamped short labels ("06h")
  to the middle of the figure.
- **The ink is the app's own theme colour**, so the figures read on the
  Encyclopedia's dark surface and follow a re-themed palette.
