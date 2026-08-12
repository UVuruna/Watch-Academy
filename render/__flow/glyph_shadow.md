# Glyph Shadow — Flow

**About:** [description](../__about/glyph_shadow.md)

## Two edges, one module

```mermaid
flowchart TB
    A[a glyph needs an edge] --> B{ring jewel / crown tile, or dial LABEL?}
    B -- ring or crown --> C[stamp_shadow: N copies, RENORMALIZED alpha]
    C --> D[a SOFT dark halo — unchanged since 2026-08-06]
    B -- label --> E[solid_contour x2, FULL alpha]
    E --> F[light contour at LABEL_BORDER_LIGHT_PX]
    E --> G[dark contour at LABEL_BORDER_DARK_PX]
    F --> H[widest first]
    G --> I[then inwards]
    H --> J[then the ink]
    I --> J
    J --> K[a HARD two-colour BORDER — the owner's correction]
```

## How a label is built

Pseudocode:

    FUNCTION bordered_plate_text(text, height_px, metal, dpr):
        ink_px = height_px * PLATE_INK_HEIGHT_FRACTION * dpr   # plate has no em slack
        IF cached(text, ink_px, metal, dpr): RETURN it

        glyphs = letter_plates.plate_text_pixmap(text, ink_px, metal)  # RAISES if plateless
        dark_px  = LABEL_BORDER_DARK_PX  * dpr        # device px, not a fraction
        light_px = LABEL_BORDER_LIGHT_PX * dpr

        light = solid_contour(glyphs, light_px, SHADOW_STAMP_TINT_LIGHT)
        dark  = solid_contour(glyphs, dark_px,  SHADOW_STAMP_TINT)

        tile = blank(light.size)
        draw light   at 0,0                  # widest
        draw dark    centred                 # then inwards
        draw glyphs  centred                 # then the ink
        RETURN tile stamped with dpr

    FUNCTION solid_contour(glyphs, radius_px, color):
        silhouette = glyphs' alpha filled flat with color
        FOR EACH of shadow_sample_count(radius_px) angles:
            draw silhouette offset by radius_px in that direction   # alpha 1.0
        # full opacity => the union is a hard dilation, not a cushion

The two `solid_contour` calls and their ORDER are the design: the light
band survives only as the ring OUTSIDE the dark keyline, which is what
makes one label legible on both a near-black body and a near-white one.

## And when there is no plate

```mermaid
flowchart LR
    A[draw_name_label] --> B[draw_bordered_plate_text]
    B -- MissingPlate --> C[name the offending character on stderr, ONCE per process]
    C --> D[draw THAT label with the old font + outline]
    B -- ok --> E[plate ink with the two-colour border]
```

Measured: 881 of 881 figure display stems compose from plates, as do all
the weekday labels. Exactly one string in the program takes the `C -> D`
road — the archetype centre "The Lord's Day", which needs an apostrophe
the library does not have.
