# Star Layer — Flow

**About:** [description](../__about/star.md)

## Algorithm

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart TB
    A[paint] --> B{pointer == aurora?}
    B -- yes --> Z[return: no geometry, Background IS the pointer]
    B -- no --> C[FOR EACH clip IN border_clips]
    C --> D["_paint_pass(fill=False, alpha=border_alpha, clip)"]
    D --> E{daylight_active?}
    E -- no --> F["_paint_pass(fill=True, alpha=day_alpha, clip=None)"] --> Y[return]
    E -- yes --> G[FOR EACH start,end,alpha IN lit_regions]
    G --> H["_paint_pass(fill=True, alpha, clip=start,end)"]
    subgraph PASS["_paint_pass(fill, alpha, clip)"]
        P1[save + optional setClipPath] --> P2[setOpacity alpha]
        P2 --> P3[rotate by wheel_rotation] --> P4[_draw_arms fill] --> P5[restore]
    end
    subgraph ARMS["_draw_arms(fill)"]
        R1[FOR EACH arms-pass IN drawn_arms z-order] --> R2[FOR EACH theta,color IN arms]
        R2 --> R3[shape = arm_shape_path] --> R4{fill?}
        R4 -- yes --> R5[stroke lead pen + fill color, draw path]
        R4 -- no --> R6[clip to shape INTERSECT, stroke 2x border_width]
    end
```

Pseudocode (language-neutral):

    IF pointer == "aurora": RETURN   # armless — the Background layer IS it

    FOR EACH clip IN border_clips(skin, sun):      # usually the whole circle
        _paint_pass(fill=False, alpha=border_alpha, clip)

    IF daylight law is off:
        _paint_pass(fill=True, alpha=day_alpha, clip=None)   # flat full color
        RETURN
    FOR EACH (start, end, alpha) IN lit_regions(sun, spec):
        _paint_pass(fill=True, alpha, clip=(start, end))

    FUNCTION _paint_pass(fill, alpha, clip):
        IF clip is not None: set clip path to that dial arc
        set opacity = alpha
        rotate by wheel_rotation(skin, ctx.rotation)
        _draw_arms(fill)

    FUNCTION _draw_arms(fill):
        FOR EACH arm-pass IN drawn_arms(skin, palette):    # z-order within the star
            FOR EACH (theta, color) IN arm-pass:
                shape = arm_shape_path(skin, tip, theta)
                IF fill:
                    stroke the shared lead pen, fill `color`, draw `shape`
                ELSE:
                    clip (intersect) to `shape`; stroke at 2x border width,
                    no brush — only the inner half of the stroke shows
