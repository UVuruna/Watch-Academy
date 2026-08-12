# Daylight

**Script:** [Daylight (script)](../daylight.py) · **Flow:** [diagram](../__flow/daylight.md)

## Purpose
Day, night and twilight geometry — the lit arcs of the dial. The
sunlit regions for a day (including the polar regimes), the border
clips between them, the Aurora pointer's hue bands over the lit part,
and the Umbra brightness ladder. The Moon marker's transit opacity
lives here too — it is a function of where the Moon stands against the
lit day.

## Connections

### Uses
- [Skin Geometry](skin_geometry.md) — `daylight_active`
- [Core (folder)](../../core/___core.md) — `angles`,
  `SunDay`/`DaylightRegime`
- [Config (folder)](../../config/___config.md) — `dial`, `palette`

### Used by
- [Layers (subfolder)](../layers/___layers.md) — `BackgroundLayer`
  (`lit_regions`, `umbra_ladder`), `StarLayer` (`lit_regions`,
  `border_clips`), `YearMarkerLayer` (`moon_transit_opacity`)

## Functions
- `lit_regions(sun, spec)`: (start, end, alpha) sunlit arcs of the day
  in wall-clock dial space — full alpha between sunrise/sunset,
  twilight alpha over the dawn/dusk bands, robust to a missing
  boundary on transitional high-latitude days.
- `border_clips(skin, sun)`: where the drawn wheel's outline strokes
  are allowed — the whole circle by default, or the sunlit arcs alone
  under `hide_night_borders`.
- `aurora_bands(sun, palette, day_alpha)`: the Aurora pointer's five day
  hues spread evenly across the sunrise–sunset arc, with dawn/dusk
  bands in the palette's first/last hue.
- `umbra_ladder(shades, contrast)`: shade values (lightest first) for
  the gray brightness wheel — endpoint-inclusive at full contrast,
  bin-centered at reduced contrast.
- `moon_transit_nearness(spec, year_angle, moon_angle)`: how deeply the
  Moon has entered the Earth's seat on the shared lane — 0.0 clear,
  rising to 1.0 concentric. THE ONE MEASURE all three of the owner's
  2026-08-10 crossing styles read, so a re-tuned marker size moves
  every style together.
- `moon_transit_opacity(spec, year_angle, moon_angle)`: the RETIRED
  translucent pass's opacity. The owner crossed that behaviour out on
  the proposals page (two bodies bleeding through each other were never
  legible), so no layer calls this any more; it is kept because it owns
  the touch-angle derivation `moon_transit_nearness` reuses and because
  its golden test still pins that derivation.

## Design Decisions
- **Every regime handles a missing boundary by collapsing the band to
  zero width**, never crashing mid-paint — real high-latitude
  transitions (a sunrise with no sunset that day, etc.) produce partial
  data and the geometry must still resolve.
- **`aurora_bands` returns a `solar_frame` flag** for regimes whose
  bands have no real sunrise/sunset boundary (polar day, one-sided
  white nights) — those run midnight-to-midnight in the SOLAR frame and
  the caller rotates them with the star.
