# Marker Marks — Flow

**About:** [description](../__about/marker_marks.md)

## The pointer's three shapes (`draw_pointer`)

```mermaid
flowchart TD
    A["edge = orbit_fraction + half_size_fraction\n(the body's OWN outer edge on the dial)"] --> B["tip  = radius * (edge + PROTRUSION)"]
    A --> C["base = radius * (edge - half_size * RECESS)"]
    B --> D{shape}
    C --> D
    D -- triangle --> E["polygon: dial_point#40;a, tip#41;, dial_point#40;a±HALF_DEG, base#41;"]
    D -- chevron --> F["two strokes from dial_point#40;a±HALF_DEG, base#41;\nmeeting at dial_point#40;a, tip#41;"]
    D -- gem --> G["diamond centred on the RING line at dial_point#40;a, tip#41;\n+ a hairline down to the body"]
    E --> H["white MARKER_BORDER outline, then the theme fill"]
    F --> H
    G --> H
```

Every vertex is a `dial_point(angle, radius)` — the mark rides the
body's own angle on the circle, never a fixed screen "up".

## The four stations (`draw_station_mark`)

    FUNCTION draw_station_mark(style, station):
        SWITCH style:
          uniform      -> the one silver halo, identical at all four   # what shipped
          arc_grammar  -> birth  : a dashed seed ring
                          youth  : an arc opening on the waxing side
                          zenith : a full corona of radial rays
                          age    : the arc closing from the other side
          inner_glow   -> outer, inner = MOON_STATION_GLOW[station]
                          draw the halo at a CONSTANT radius, alpha *= outer
                          IF inner > 0:
                              clip to moon_face.dark_region(...)        # only the unlit half glows
                              draw an inward gradient, alpha *= inner

The Sun's twin adds two more styles: `uniform_seasonal` takes the same
halo in `palette.INSTRUMENT_SEASON_COLORS[season]`, and
`day_night_wedge` fills a ring arc to the day's own length.

## The solar eclipse (`draw_solar_eclipse`)

    FUNCTION draw_solar_eclipse(style, state, magnitude):
        IF style == "halo": RETURN            # the caller already drew it
        IF style == "magnitude_arc":
            draw the body, then a ring gauge filled clockwise to magnitude
            RETURN
        # "bite" — the magnitude becomes geometry
        IF state == "solar_total":
            corona rays + a black disc                     # not a bright Sun at all
        ELSE:
            paint_face, then clip to the disc and lay a dark occulting
            circle offset by (1 - magnitude) — a bite when partial, a
            concentric ring of fire when annular
