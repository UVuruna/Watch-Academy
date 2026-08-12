# Background Layer — Flow

**About:** [description](../__about/background.md)

## Algorithm

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart TB
    subgraph UMBRA["Umbra pass (rotated with the star)"]
        A[rotate by ctx.rotation] --> B{spec.base_asset?}
        B -- yes --> C[draw pixmap centered]
        B -- no --> D{daylight_active?}
        D -- no --> E[flat: one full circle, lightest shade]
        D -- yes --> F{umbra_form}
        F -- gradient --> G[conical gradient light-dark-light]
        F -- sections --> H[mirrored pie wedges, umbra_ladder]
    end
    UMBRA --> I{ctx.skin.pointer}
    I -- aurora --> J[aurora_bands: hue bands over sunlit arc] --> Z[return]
    I -- calendar --> K[12 fixed wedges, rotation=0 + optional mount] --> Z
    I -- other --> L{ctx.skin.colorful?}
    L -- yes --> M[per-hue wedge bounds: aura_wedge_bounds]
    L -- no --> N[one COLORFUL_OFF_COLOR wedge]
    M --> O[_paint_aura]
    N --> O
    O --> P{daylight_active?}
    P -- no --> Q[full circle at day_alpha]
    P -- yes --> R[per lit_region: clip arc, draw wedges at that alpha]
```

Pseudocode (language-neutral):

    rotate painter by ctx.rotation
    IF background has a base image asset:
        draw it centered, 2x umbra_radius
    ELSE IF daylight law is off:
        fill one full circle in the lightest contrast shade
    ELSE IF umbra_form is "gradient":
        conical gradient: lightest at top, darkest at bottom, lightest again
    ELSE:                                   # discrete sections
        FOR EACH mirrored pair of sections around the wheel:
            draw pie slice pair at the section's shade
    restore rotation

    IF pointer == "aurora":
        FOR EACH (start, end, hue, alpha) IN aurora_bands(sun, palette):
            draw pie slice at that hue/alpha (rotated if solar-framed)
        RETURN
    IF pointer == "calendar":
        paint 12 fixed 2-hour wedges at rotation 0
        IF calendar_mount != "off": draw the mount
        RETURN

    hues = colorful ? palette : (COLORFUL_OFF_COLOR,)
    wedges = aura_wedge_bounds(skin, hues)      # each hue's own lead-ray span
    _paint_aura(radius=aura_radius, hues, wedges, rotation=ctx.rotation)

    FUNCTION _paint_aura(radius, hues, wedges, rotation):
        IF daylight law is off:
            set opacity = day_alpha; rotate by `rotation`
            FOR EACH (hue, wedge) IN zip(hues, wedges): draw pie slice
        ELSE:
            FOR EACH (start, end, alpha) IN lit_regions(sun, spec):
                clip to that arc; set opacity = alpha; rotate by `rotation`
                FOR EACH (hue, wedge) IN zip(hues, wedges): draw pie slice
