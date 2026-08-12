# Assets — Flow

**About:** [description](../__about/assets.md)

## The rasterize-and-recolor routing (`pixmap_by_height`)

```mermaid
flowchart TB
    A[pixmap_by_height path, height, dpr, tint, metal, saturation] --> B{height fits under\nthis subtree's working ceiling?}
    B -- yes --> C[decode the once-per-file\nDOWNSCALED working copy]
    B -- no --> D[decode the ORIGINAL full-res source]
    C --> E{metal given?}
    D --> E
    E -- yes --> F[_recolored: Oklab metal swap\nvia recolor.transform, disk-cached]
    E -- no --> G[skip]
    F --> H{desaturate?}
    G --> H
    H -- yes --> I[_desaturated: gray for a\nuser hand pack under a tint]
    H -- no --> J[skip]
    I --> K{tint given?}
    J --> K
    K -- yes --> L[_tinted: tritone black-tint-white multiply]
    K -- no --> M[skip]
    L --> N{saturation != 1.0?}
    M --> N
    N -- yes --> O[_saturated: HSV scale of the FINAL pixmap]
    N -- no --> P[return pixmap, devicePixelRatio set]
    O --> P
```

Pseudocode:

    FUNCTION pixmap_by_height(path, height, dpr, tint, desaturate, metal, saturation):
        source = downscaled working copy IF height <= working_ceiling(path) ELSE original
        image = rasterize(source, height, dpr)          # PNG scale or SVG render
        IF metal:      image = _recolored(image, metal, source_metal, mask_mode)
        IF desaturate: image = _desaturated(image)
        IF tint:       image = _tinted(image, tint)
        IF saturation != 1.0: image = _saturated(image, saturation)
        RETURN image as QPixmap with devicePixelRatio = dpr

The four optional steps are ORDER-FIXED: metal swap first (it operates
on the source's own cast), desaturate second (grays user art before a
tint has to work on it), tint third (the ring/hand recolor), saturation
last (the Ring Saturation slider scales the fully-recolored result).
