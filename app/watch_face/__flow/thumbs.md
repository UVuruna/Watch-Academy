# Watch Face Thumbnails — Flow

**About:** [description](../__about/thumbs.md)

## Algorithm — art_thumbnail(source)

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart TB
    A["art_thumbnail(source)"] --> B{"source resolves and exists?"}
    B -- no --> C["return None"]
    B -- yes --> D["cache_path <- raster_cache /
    source_prefix(source) + '_thumb_v' + VERSION + '.png'"]
    D --> E{"cache_path exists?"}
    E -- yes --> F["return QIcon(cache_path)"]
    E -- no --> G["load source, scale to THUMB_SOURCE_PX"]
    G --> H["atomic_save(scaled, cache_path)"]
    H --> F
```

## Algorithm — pointer_swatch_icon(pointer, style) — the R-33 honest fallback

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart TB
    A["pointer_swatch_icon(pointer, style)"] --> B["style <- effective_palette_style(pointer, style)"]
    B --> C["hues <- PALETTE_PRESETS[(pointer, style)]"]
    C --> D["cache_path <- raster_cache /
    'pointer_swatch_' + pointer + '_' + style + '_v' + VERSION + '.png'
    (no source file — a COMPUTED name, same convention
    render.asset_variants.calendar_wheel_icon_file uses)"]
    D --> E{"cache_path exists?"}
    E -- yes --> F["return QIcon(cache_path)"]
    E -- no --> G["paint a pie of len(hues) wedges, one hue each"]
    G --> H["atomic_save(image, cache_path)"]
    H --> F
```
