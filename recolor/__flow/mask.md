# Mask — Flow

**About:** [description](../__about/mask.md)

## Algorithm

```mermaid
flowchart TB
    A["linear_rgb, alpha, body_linear, tuning, mode"] --> B{"mode?"}
    B -- "alpha" --> C["weight = (alpha > 0)"]
    B -- "chroma" --> D["lab = linear_to_oklab(linear_rgb)"]
    D --> E["lightness = lab[...,0]"]
    D --> F["chroma, hue = oklab_chroma_hue(lab)"]
    E --> G["saturation = chroma / max(lightness, floor)"]
    F --> G
    D --> H["body_hue = oklab_chroma_hue(linear_to_oklab(body_linear))[1]"]
    F --> I["distance = hue_distance(hue, body_hue)"]
    H --> I
    I --> J["hue_weight = 1 - smoothstep((distance - half_width) / soft)"]
    G --> K["sat_weight = smoothstep((saturation - low) / (high - low))"]
    J --> L["weight = hue_weight * sat_weight * (alpha > 0)"]
    K --> L
    C --> M[("weight in [0,1]")]
    L --> M
    B -- "anything else" --> N["raise ValueError"]
```

Pseudocode (language-neutral):

    METAL_WEIGHT(linear_rgb, alpha, body_linear, tuning, mode):
        opaque = (alpha > 0)
        IF mode == "alpha":
            RETURN opaque
        IF mode != "chroma":
            RAISE error "unknown mask mode"

        lab               = OKLAB(linear_rgb)
        lightness         = lab.L
        chroma, hue       = CHROMA_HUE(lab)
        saturation        = chroma / max(lightness, BLACK_FLOOR)

        body_hue          = CHROMA_HUE(OKLAB(body_linear)).hue
        distance          = HUE_DISTANCE(hue, body_hue)          -- shortest angle, degrees

        hue_weight        = 1 - SMOOTHSTEP((distance - hue_half_width_deg) / hue_soft_deg)
        sat_weight        = SMOOTHSTEP((saturation - sat_low) / (sat_high - sat_low))

        RETURN hue_weight * sat_weight * opaque
