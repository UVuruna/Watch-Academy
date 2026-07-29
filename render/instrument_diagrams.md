# Instrument Diagrams

**Script:** [Instrument Diagrams (script)](instrument_diagrams.py)

## Purpose
The clock explaining itself. Eight Encyclopedia pages carry a figure of
the instrument's OWN behaviour, and every one of them is drawn live from
the same numbers the dial is drawn from — never painted.

| Figure | What it shows | Where its numbers come from |
|---|---|---|
| `dial` | 24 hours on ONE turn, both hands at the sample moment | `constants.DIAL_OFFSET_DEG`, `SECONDS_PER_DAY`, `core.angles` |
| `solar_rotation` | the hexagram tipped so its top vertex points at true solar noon | the project's own golden tilt, `+10.76°` (Belgrade under DST) |
| `twilight` | the three bands under the west horizon at their real depressions | `constants.CIVIL_DEPRESSION` + the band table |
| `year_wheel` | four EQUAL quarters, each anchor on its real instant | the season hues of `PALETTE_PRESETS[("cross", "tertiary")]` |
| `moon_lunations` | eight phases around the wheel, terminator and all | `core.angles.moon_cycle_angle`, `constants.MOON_PHASE_NAMES` |
| `metals` | gold at noon, silver at midnight; three finishes below | `ENCYCLOPEDIA_FINISH_BORDER_COLORS` |
| `ring_letters` | Δ · M · Y · Ω, each at the hour of its alphabet place | `doctrine.RING_LETTER_SEATS`, `angles.ring_position_angle` |
| `oscillations` | the La2004 amplitude envelope over ±200,000 years | `data.observatory.ObservatoryData.laskar_envelope()` |

## The derivation check, written (Rule #19)

The coverage law owed these eight pages a plate, and the ledger was
about to commission eight briefs. The rule's own question stopped it:
**if changing a constant would make the painted plate a LIE, the plate
must not be painted.**

Every one of these figures fails that test as art. Move
`DIAL_OFFSET_DEG` and a commissioned dial illustration is silently
wrong. Re-tune a season hue and a painted year wheel disagrees with the
dial beside it. Re-bundle the ephemeris and a painted envelope chart is
a picture of a number that has changed. So they are COMPUTED, and the
eight files they used to name are not owed to anyone.

`paint_light` is the counter-example and keeps its picture: it
illustrates a doctrine, not a geometry.

## Connections

### Uses
- [Config (folder)](../config/___config.md) — every constant and palette the figures read
- [Core (folder)](../core/___core.md) — `angles`, the one dial-angle mapping
- [Observatory Data](../data/observatory.md) — the La2004 envelope bundle (the `oscillations` figure alone)

### Used by
- [Diagrams](diagrams.md) — the one door a page's `(kind, key)` goes through
- [Topic Tree](../app/encyclopedia/tree.md) — imports `INSTRUMENT_FIGURES` so a page can only declare a figure that exists

## Design Decisions
- **One kind, `"instrument"`; the KEY names the figure.** The facade
  routes by kind, so this module answers exactly one.
- **`INSTRUMENT_FIGURES` is the single source of truth.** The topic
  tree imports it instead of keeping a parallel list of the same names
  (Rule #5) — a page cannot declare a drawer nobody wrote.
- **Labels are measured, not guessed.** `_text` takes the width from
  `QFontMetricsF` and clamps the box to the plate. The first version
  guessed a width, and the guess clamped short labels ("06h") to the
  middle of the figure — a clamp is only as honest as the width it is
  given.
- **Every figure is cached per (kind, key, size)** like the other two
  diagram modules: the reader re-fits on every resize and must never
  redraw the same figure twice.
- **The ink is the app's own theme colour**, so the figures read on the
  Encyclopedia's dark surface and follow a re-themed palette.
