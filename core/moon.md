# Moon

**Script:** [Moon (script)](moon.py)

## Purpose
Moon cycle fraction and illumination from bundled principal-phase
instants — exact at the anchors, ~0.0001 cycle accurate in between.
`astral.moon.phase()` is day-granular (off by up to ~0.3 day near the
instants) and deliberately not used.

## Connections

### Uses
- [Config (folder)](../config/___config.md) — `MOON_PHASE_FRACTIONS`,
  `MOON_CYCLE_QUARTER`

### Used by
- [Moon Phases Repository](../data/moon_phases.md) — constructs `MoonWindow`
- [Clock State](clock_state.md), the year-marker layer in moon mode (M3)

## Classes

### MoonWindow
Frozen: sorted `(instant_utc, cycle_fraction)` events spanning the
period of interest plus margins.

## Functions
- `phase_fraction(now, window)`: 0.0 new … 0.5 full … wraps at 1.0;
  waxing below 0.5, waning above; raises outside the window span
- `illumination(fraction)`: lit fraction of the disc, `(1−cos 2πf)/2`
