# Instrument Diagrams

**Script:** [Instrument Diagrams (script)](../instrument_diagrams.py) · **Flow:** [diagram](../__flow/instrument_diagrams.md)

## Purpose
The clock explaining itself. Eight Encyclopedia pages carry a figure of
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
| `ring_letters` | Δ·M·Y·Ω at the hour of its alphabet place | `doctrine.RING_LETTER_SEATS`, `angles.ring_position_angle` |
| `oscillations` | the La2004 amplitude envelope over ±200,000 years | `data.observatory.ObservatoryData.laskar_envelope()` |

## Connections

### Uses
- [Config (folder)](../../config/___config.md) — every constant and
  palette the figures read
- [Core (folder)](../../core/___core.md) — `angles`, the one dial-angle
  mapping
- [Observatory Data](../../data/__about/observatory.md) — the La2004
  envelope bundle (the `oscillations` figure alone)

### Used by
- [Diagrams](diagrams.md) — the one door a page's `(kind, key)` goes
  through
- `app.encyclopedia.tree` — imports `INSTRUMENT_FIGURES` so a page can
  only declare a figure that exists

## Design Decisions
- **One kind, `"instrument"`; the KEY names the figure.** The facade
  routes by kind, so this module answers exactly one kind with eight
  keys.
- **`INSTRUMENT_FIGURES` is the single source of truth** — the topic
  tree imports it instead of keeping a parallel list (Rule #5).
- **Labels are measured, not guessed** (`_text` reads
  `QFontMetricsF`) — a guessed width once clamped short labels ("06h")
  to the middle of the figure.
- **The ink is the app's own theme colour**, so the figures read on the
  Encyclopedia's dark surface and follow a re-themed palette.
