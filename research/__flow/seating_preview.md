# Seating Preview — Flow

**About:** [description](../__about/seating_preview.md)

## Algorithm

```mermaid
flowchart TB
    A[QApplication + ensure a readable font] --> B[draw_rose]
    B --> C[3 octa stars, 15° apart, one arm per seat from core.cube_seating]
    C --> D[paint each seat's diamond, colored by hue index]
    D --> E[ladder-layout labels per side so neighbours never overlap]
    E --> F[draw_calendar]
    F --> G[12 wedges: pie slice + outer/axis/inner radial label rows]
    G --> H[save both QImages as PNG under research/seating/]
```

Pseudocode (language-neutral):

    ENSURE a usable font (native Qt plugin; else load a bundled system TTF)

    DRAW ROSE:
        FOR EACH of the 3 stars (offset -15 / 0 / +15 degrees):
            FOR EACH seat ON that star:
                paint its diamond arm, colored by the seat's hue index
        LAY OUT ray labels in per-side ladders (sorted by height, pushed
        apart to a minimum gap) so neighbouring rays never overwrite text

    DRAW CALENDAR:
        FOR EACH of the 12 monthly wedges:
            paint the pie slice
            paint three radial label rows: outer end, axis name, inner end

    SAVE both QImages as PNG under research/seating/
