# Ramp — Flow

**About:** [description](../__about/ramp.md)

## Algorithm

```mermaid
flowchart TB
    A["metal.stops: (position, hex) pairs"] --> B["sort by position"]
    B --> C["lab_stops = linear_to_oklab(hex_to_linear(color)) per stop"]
    C --> D["for L, a, b: np.interp(lightness, positions, lab_stops[:,channel])"]
    D --> E["lab = stacked [L, a, b]"]
    E --> F["linear_rgb = clip(oklab_to_linear(lab), 0, None)"]
    F --> G[("sample(metal, lightness)")]

    G --> H{"specular.strength <= 0?"}
    H -- yes --> I["unchanged"]
    H -- no --> J["span = max(1 - start, 1e-6)"]
    J --> K["weight = smoothstep((lightness - start) / span) * strength"]
    K --> L["result = lerp(linear_rgb, white, weight)"]
    I --> M[("add_specular result")]
    L --> M
```

`body_color(metal, position)` is `sample(metal, position)` reshaped to
`(3,)` — the ramp sampled at one scalar position.

Pseudocode (language-neutral):

    SAMPLE(metal, lightness):
        positions, colors = metal.stops, sorted by position
        lab_stops = [OKLAB(HEX_TO_LINEAR(color)) for color in colors]
        FOR each of L, a, b:
            interpolate PIECEWISE-LINEAR at `lightness` over (positions, lab_stops[channel])
                -- np.interp clamps outside the stop range, both ends
        RETURN clip(OKLAB_TO_LINEAR(stacked lab), 0, None)

    BODY_COLOR(metal, position) = SAMPLE(metal, position)

    ADD_SPECULAR(rgb, lightness, specular):
        IF specular.strength <= 0: RETURN rgb unchanged
        span   = max(1 - specular.start, 1e-6)
        weight = SMOOTHSTEP((lightness - specular.start) / span) * specular.strength
        RETURN LERP(rgb, white, weight)
