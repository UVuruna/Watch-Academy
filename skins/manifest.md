# Manifest

**Script:** [Manifest (script)](manifest.py)

## Purpose
The typed skin definition — six overridable units (background, hexagram,
ring, weekday_set, year_marker, hands) plus the noon marker. Pure
dataclasses with no I/O: `DEFAULT_SKIN` in config is an instance of these,
and M5's `skin.json` loading/validation targets the same types, so
extraction is serialization, not redesign.

## Connections

### Uses
- Nothing (stdlib dataclasses only — importable from anywhere)

### Used by
- [Config (folder)](../config/___config.md) — `DEFAULT_SKIN`
- [Render (folder)](../render/___render.md) — layers read the specs

## Classes

- `SkinDefinition` — name, `z_order`, one spec per unit
- `BackgroundSpec` — mode (colors / light_dark), 6-sector palette,
  twilight/night shades, radius fraction
- `HexagramSpec`, `NoonMarkerSpec` — asset-or-procedural + geometry
- `RingSpec` — colors, width, per-hour letter substitutions (D-Ω-M-Y)
- `WeekdaySpec` — body images/colors, display mode (ghost / center_only),
  ghost opacity, sizes, orbit
- `YearMarkerSpec` — earth / moon_phase mode, day+night variants per
  continent, orbit, scale
- `HandSpec` / `HandsSpec` — asset, MANDATORY pivot fractions, reach
