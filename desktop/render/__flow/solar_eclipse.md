# Solar Eclipse — Flow

**About:** [description](../__about/solar_eclipse.md)

## One door, six pictures (`draw_solar_eclipse`)

```mermaid
flowchart TD
    A["draw_solar_eclipse#40;style, radius, state, magnitude, distance_km#41;"] --> B["covered = clamp#40;magnitude, 0, 1#41;"]
    B --> C["resolve_eclipse_style#40;'solar', style#41;\n#40;THE DOOR — never trust the raw name#41;"]
    C --> D{effective style}
    D -- bite --> E["the owner's two body plates composited\n#40;occulter size + offset = solar_occulter_geometry#41;"]
    D -- magnitude_arc --> F["ring gauge at 1.18 radii, filled clockwise to covered"]
    D -- halo --> G["soft pearl ring OUTSIDE the body\n#40;radius, width and alpha all rise with covered#41;"]
    D -- totality_path --> H["arc at 1.30 radii — length AND brightness from the observer's nearness"]
    D -- type_emblem --> I["badge on the lower limb — the type's own glyph"]
    D -- dial_shadow --> J["a dark well around the body\n#40;reach 1.05..1.36, alpha 0.25..0.80#41;"]
    E --> K{"state == solar_hybrid?"}
    F --> K
    G --> K
    H --> K
    J --> K
    K -- yes --> L["the both-at-once mark: a second lane / ring / rim\nin the ring-of-fire orange"]
    K -- no --> M[done]
    I --> M
    L --> M
```

## The totality path's one honest number (`totality_path_reach`)

    FUNCTION totality_path_reach(covered, distance_km):
        IF distance_km IS NULL:
            # No observer, or a catalog row with no ground point.
            # The catalog magnitude is the eclipse's GREATEST magnitude
            # somewhere on Earth — it is what is on offer, never what
            # THIS observer gets. So it is an ESTIMATE and the caller
            # draws it DASHED.
            RETURN clamp(covered, 0, 1), measured = FALSE
        # The real quantity: the observer's great-circle distance to the
        # catalog's greatest-eclipse ground point, already on the event.
        # NOT the distance to the nearest point of the central PATH —
        # the catalog holds one point, not the track — so this
        # UNDER-reads for an observer far along the path. Under is the
        # safe direction; over would be a lie.
        RETURN clamp(1 - distance_km / ECLIPSE_SOLAR_VISIBILITY_KM, 0, 1),
               measured = TRUE

    FUNCTION _totality_path(state, covered, distance_km):
        reach, measured = totality_path_reach(covered, distance_km)
        span  = max(MIN_SPAN_DEG, reach * 360)        # LENGTH  = nearness
        alpha = ALPHA_MIN + reach * (ALPHA_MAX - ALPHA_MIN)   # BRIGHTNESS too
        width = ARC_WIDTH; IF state is partial: width *= PARTIAL_WIDTH
        IF state == solar_hybrid:
            outer lane, span/2, centred at the TOP,    corona pearl
            inner lane, span/2, centred at the BOTTOM, ring-of-fire orange
        ELSE:
            one lane, full span, centred at the TOP, _totality_light(state)
        # every lane DASHED when measured is FALSE — the estimate, said aloud

## The type emblem (`_type_emblem`)

    FUNCTION _type_emblem(state):
        stamp a night backing disc on the body's lower limb
        SWITCH state:
          solar_total   -> a FILLED disc      # nothing of the Sun is left
          solar_partial -> a filled disc MINUS an offset disc-sized bite
          solar_annular -> ONE ring           # the ring of fire
          solar_hybrid  -> the same ring, plus a SECOND inside it

    # One grammar: how much of the emblem's centre is open says how much
    # of the Sun survives.
