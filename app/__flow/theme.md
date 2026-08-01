# Theme — Flow

**About:** [description](../__about/theme.md)

## Algorithm — `size_to_screen`

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart TB
    A["size_to_screen(dialog, aspect_w, aspect_h,
    height_fraction, min_width=0)"] --> B{"dialog.windowHandle()
    exists (already shown)?"}
    B -- yes --> C[screen = handle.screen]
    B -- no --> D[screen = primaryScreen]
    C --> E
    D --> E{screen is None? (headless)}
    E -- yes --> F[keep Qt defaults, RETURN]
    E -- no --> G["available = screen.availableGeometry()"]
    G --> H["height = min(available.height * height_fraction,
    available.height)"]
    H --> I["width = min(
    max(height * aspect_w/aspect_h, min_width),
    available.width)"]
    I --> J["dialog.resize(width, height)
    dialog.move(available.center - dialog.rect.center)"]
```

Pseudocode:

    FUNCTION size_to_screen(dialog, aspect_w, aspect_h, height_fraction, min_width):
        screen <- dialog's own window handle's screen, else the primary screen
        IF screen is None: RETURN                    # headless test platform
        available <- screen.availableGeometry()
        height <- min(available.height * height_fraction, available.height)
        width  <- min(max(height * aspect_w / aspect_h, min_width), available.width)
        dialog.resize(width, height)
        dialog.move(available.center - dialog.rect.center)   # centered

`min_width` is the ONLY input that can make the result wider than the
pure aspect ratio — the height is never re-derived from a wider width,
so a min-width dialog reads as a wider-than-aspect rectangle at the same
height, never a taller one. Callers: A4 portrait (210:297) at 80% height
for Encyclopedia/Observatory; a 1:1 square at 50% height for Settings/
Time Travel/Design/Pointer Theme/Slot Theme/Report.
