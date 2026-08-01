# Shapes — Flow

**About:** [description](../__about/shapes.md)

## The drawn wheel (`drawn_arms`)

```mermaid
flowchart TB
    A[drawn_arms skin, colors] --> B{pointer == calendar?}
    B -- yes --> C[centers = the 12 active wedges' midpoints]
    C --> D{polygon shape?}
    D -- yes --> E[ONE pass: 12 arms, hue i on wedge i]
    D -- no --> F[TWO passes: odd wedges' hexagram\nfirst, even one painted over it]
    B -- no --> G[stars = rose_star_offsets or single 0]
    G --> H[FOR EACH star: arm k at offset+star+k*360/N]
    H --> I{polygon shape AND\nmore than one star Rose?}
    I -- yes --> J[ONE pass: all rays merged\nthey touch, no z-stack needed]
    I -- no --> K[one pass per star, table order]
```

## The curved polygon edge (`_append_edge` / `_pulled_midpoint`)

    FOR EACH outer edge of the figure:
        mid    = chord midpoint of the straight edge
        target = the pointer's OWN star inner radius
        mid'   = mid pulled along ITS OWN radius toward target,
                 by the curvature fraction (0 -> mid, 1 -> target)
        IF edge_mode == "notched":
            draw two straight segments meeting at mid'
        ELSE ("smooth"):
            draw one quadratic curve whose CONTROL point is 2*mid' - chord_mid
            (so the CURVE, not the control point, passes through mid')

At curvature 0 both modes collapse to the plain straight polygon edge;
at curvature 1 the smooth hexagon becomes the hexagram.
