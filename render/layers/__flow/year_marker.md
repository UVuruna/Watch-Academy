# Year Marker Layer — Flow

**About:** [description](../__about/year_marker.md)

## Algorithm

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart TB
    A[paint] --> B{show_earth AND gate earth?}
    B -- yes --> C[_draw_earth]
    A --> D{show_moon AND gate moon?}
    D -- yes --> E[_draw_moon path]

    subgraph EARTH["_draw_earth"]
        C1[year_angle: almanac wedge or shared season wheel] --> C2{season/solar-eclipse\nevent window active?}
        C2 -- yes --> C3[relocate to ring band, glow: gold/red,\nmuted if not visible]
        C2 -- no --> C4[normal orbit_fraction radius]
        C3 --> C5
        C4 --> C5{almanac?}
        C5 -- yes --> C6[draw day arrow]
        C5 -- no --> C7
        C6 --> C7[variant = earth_style_region_day-or-night]
        C7 --> C8{asset exists?}
        C8 -- yes --> C9[clip to disc, draw pixmap, draw label per earth_label mode]
        C8 -- no --> C10[draw plain colored circle]
    end

    subgraph MOON["_draw_moon path (in paint)"]
        M1[moon_angle from moon_fraction] --> M2[opacity: transit + below-horizon dim]
        M2 --> M3{event/eclipse window active?}
        M3 -- yes --> M4[relocate to ring band, glow: silver/bronze,\nmuted if not visible]
        M3 -- no --> M5[normal moon_orbit_fraction radius]
        M4 --> M6
        M5 --> M6[_draw_moon: image or disc, lit-region mask,\neclipse darken if applicable]
    end
```

Pseudocode (language-neutral):

    IF show_earth AND gate("earth"): _draw_earth()
    IF show_moon AND gate("moon"):
        moon_angle = moon_cycle_angle(tick.moon_fraction)
        opacity = moon_transit_opacity(...) IF show_earth ELSE 1.0
        IF NOT tick.is_moon_up: opacity *= moon_hidden_alpha
        eclipse = tick.eclipse_event IF kind == "lunar" ELSE None
        glowing = tick.moon_event is not None OR eclipse is not None
        orbit = ring-band radius IF glowing ELSE moon_orbit_fraction
        pos = dial_point(moon_angle, radius * orbit)
        IF glowing:
            color, strength = eclipse colors/magnitude, or plain moon-glow
            IF eclipse is real but NOT visible from here: mute to silver
            draw_event_glow(pos, size, color, strength)
        _draw_moon(pos, size, darken_state=eclipse render state)

    FUNCTION _draw_earth():
        year_angle = almanac_marker_angle(date) IF Calendar+almanac wheel
                     ELSE tick.year_angle
        eclipse = tick.eclipse_event IF kind == "solar" ELSE None
        glowing = tick.season_event is not None OR eclipse is not None
        orbit = ring-band radius IF glowing ELSE spec.orbit_fraction
        pos = dial_point(year_angle, radius * orbit)
        IF glowing: draw_event_glow(pos, size, color, strength)  # gold/red
        IF almanac: draw the day arrow at this tick
        variant = f"{earth_style}_{earth_region(latitude, default)}_{day_or_night}"
        asset = eclipse art IF a solar eclipse is active ELSE variant's asset
        IF asset exists:
            clip to the marker disc; draw it; draw the label (one of 4 modes)
        ELSE:
            draw a plain bordered circle in the day/night color

    FUNCTION _draw_moon(pos, size, darken_state):
        draw the moon image or a dark disc
        lit = moon_lit_region(fraction, radius)      # union/difference geometry
        fill the lit region (or subtract it as a shadow over the image)
        IF darken_state is not None:
            multiply the WHOLE disc by a neutral (or copper, for totality)
            gray — a true brightness cut, not a translucent color wash

    FUNCTION earth_region(latitude, default) -> region_name:
        IF latitude at/beyond the pole threshold: RETURN "north_pole"/"south_pole"
        ELSE: RETURN default                          # the active continent
