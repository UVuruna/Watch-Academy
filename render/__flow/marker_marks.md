# Marker Marks — Flow

**About:** [description](../__about/marker_marks.md)

## The pointer's three shapes (`draw_pointer`)

```mermaid
flowchart TD
    T["tip_radius param\n(None: measured plate ratio; the 360 tips' own radius when the body rode onto the ring band)"] --> N{"dial_radius * orbit_fraction > tip?"}
    N -- yes, body OUTSIDE the tips' circle --> INW["inward: arrow FLIPS to point IN\nedge = orbit_fraction - half_size_fraction"]
    N -- no, body INSIDE (ordinary orbit) --> OUTW["outward: arrow points OUT, as before\nedge = orbit_fraction + half_size_fraction"]
    INW --> C["base = edge*radius + depth\n(hidden under the disc — drawn BEFORE the body)"]
    OUTW --> C
    C --> D{shape}
    D -- triangle --> E["polygon: dial_point#40;a, tip#41;, dial_point#40;a±HALF_DEG, base#41;"]
    D -- chevron --> F["two strokes from dial_point#40;a±HALF_DEG, base#41;\nmeeting at dial_point#40;a, tip#41;"]
    D -- gem --> G["diamond spanning body_edge..tip\n#40;the WHOLE gem between the two circles, height >= width#41;"]
    E --> H["clip out the body's own disc, then\nwhite MARKER_BORDER outline, then the theme fill"]
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
        # "bite" (owner correction 2026-08-11) — drawn AS SEEN, on top
        # of config.defaults.ECLIPSE_SOLAR_ART (the owner's own icon)
        IF state == "solar_total" AND covered >= 1.0:
            RETURN                              # the icon alone is the look
        IF state == "solar_annular":
            draw the ring of fire around the black disc
        ELSE:
            visible = 1 - covered
            phase = acos(1 - 2*visible) / (2*pi)      # invert moon_lit_region's own mapping
            draw moon_lit_region(phase, radius) as a bright crescent  # the SAME terminator the Moon's phases use
