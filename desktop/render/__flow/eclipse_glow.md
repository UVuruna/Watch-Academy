# Eclipse Glow — Flow

**About:** [description](../__about/eclipse_glow.md)

## The glow gradient (`draw_event_glow`)

```mermaid
flowchart LR
    A[QRadialGradient\nradius = marker_radius * GLOW_RADIUS_SCALE] --> B["stop 0.0: core color @ CORE_ALPHA*strength"]
    B --> C["stop GLOW_MID_STOP: mid color @ MID_ALPHA*strength"]
    C --> D{fringe_color given?}
    D -- yes --> E["3 extra stops around FRINGE_STOP:\ntransparent -> peak -> transparent"]
    D -- no --> F[skip]
    E --> G["stop 1.0: transparent"]
    F --> G
    G --> H[drawEllipse at the gradient's radius]
```

## The eclipse state lookup

    FUNCTION eclipse_render_state(event):
        state = ECLIPSE_TYPE_STATE.get((event.kind, event.type))
        IF found: RETURN state
        RETURN ECLIPSE_STATE_FALLBACK[event.kind]      # documented degrade, never raise

    FUNCTION eclipse_state_glow_strength(state, magnitude):
        IF state == "solar_partial":
            RETURN eclipse_glow_strength(magnitude)      # the one magnitude-linear exception
        RETURN ECLIPSE_STATE_GLOW_STRENGTH[state]         # every other state: fixed fraction
