# Glow — Flow

**About:** [description](../__about/glow.md)

## Sections

```
📁 glow.py
  Season/moon event glow      GLOW_CORE_ALPHA, GLOW_MID_ALPHA, GLOW_MID_STOP,
                               GLOW_RADIUS_SCALE
  Eclipse invisibility         ECLIPSE_INVISIBLE_STRENGTH_FACTOR
  Lunar fringe geometry        ECLIPSE_LUNAR_FRINGE_STOP / _HALF_WIDTH / _ALPHA
  Magnitude -> strength ramp   ECLIPSE_MAGNITUDE_MIN/MAX, ECLIPSE_GLOW_STRENGTH_MIN/MAX
  Eclipse TYPE -> STATE table  ECLIPSE_TYPE_STATE, ECLIPSE_STATE_FALLBACK
  Per-STATE fixed triad        ECLIPSE_STATE_MOON_BRIGHTNESS
                               ECLIPSE_STATE_GLOW_STRENGTH
                               ECLIPSE_STATE_FRINGE
  Category emblem              ECLIPSE_ART_DIR, ECLIPSE_TYPE_EMBLEM
  Hover badge                  ECLIPSE_TYPE_ICON_PX
```

## The eclipse type -> render state dispatch

```mermaid
flowchart TB
    A["catalog (kind, type)\ne.g. (solar, hybrid)"] --> B{ECLIPSE_TYPE_STATE has it?}
    B -- yes --> C[fixed render STATE\ne.g. solar_total]
    B -- no / unknown --> D["ECLIPSE_STATE_FALLBACK[kind]\ne.g. solar_partial"]
    C --> E{state == solar_partial?}
    D --> E
    E -- yes --> F[glow strength = MAGNITUDE-linear\nECLIPSE_MAGNITUDE_MIN..MAX]
    E -- no --> G["glow strength = ECLIPSE_STATE_GLOW_STRENGTH[state]\n(fixed)"]
    C --> H["moon brightness = ECLIPSE_STATE_MOON_BRIGHTNESS[state]\n(lunar states only)"]
    C --> I["fringe drawn? = ECLIPSE_STATE_FRINGE[state]"]
```

Pseudocode:

    resolve_eclipse_state(kind, catalog_type):
        state <- ECLIPSE_TYPE_STATE.get((kind, catalog_type))
        IF state is None:
            state <- ECLIPSE_STATE_FALLBACK[kind]
        RETURN state

    eclipse_glow_strength(state, magnitude):
        IF state == "solar_partial":
            RETURN linear_map(magnitude, MAGNITUDE_MIN..MAGNITUDE_MAX,
                               GLOW_STRENGTH_MIN..GLOW_STRENGTH_MAX)
        RETURN ECLIPSE_STATE_GLOW_STRENGTH[state]

`hybrid` solar eclipses fold into `solar_total` (the nearest sealed
state — a hybrid eclipse shows true totality along most of its ground
track) but keep their OWN category emblem in `ECLIPSE_TYPE_EMBLEM`, so
the Encyclopedia chapter still distinguishes it even though the render
state does not.
