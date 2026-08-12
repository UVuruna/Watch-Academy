# Fast Travel Flash — Flow

**About:** [description](../__about/fast_travel_flash.md)

## Layout

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart LR
    subgraph TOAST["FastTravelFlash — frameless, translucent, topmost"]
        ICON["icon label (file or emoji fallback)"]
        TEXT["text label — the active option's name"]
    end
```

Positioned centered above the dial's current on-screen rectangle, or
below it when the dial sits at the top edge of its screen — OR (R-30,
`big=True`) dead centered ON the dial itself, in larger letters, with
the icon label hidden.

## Algorithm — `flash()` lifecycle

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart TB
    A["flash(dial, icon, emoji, text, big=False)"] --> B["stop any running fade + hold timer
    opacity <- 1.0"]
    B --> C[set icon/text, font size, adjustSize]
    C --> D{big?}
    D -- "no" --> D1["_position_above_or_below(dial)"]
    D -- "yes" --> D2["_position_centered(dial)"]
    D1 --> E["show(); native.assert_topmost"]
    D2 --> E
    E --> F["hold_timer.start(DURATION_S*1000 - FADE_MS)"]
    F --> G((hold timer fires))
    G --> H["fade.start() — opacity 1.0 to 0.0 over FADE_MS"]
    H --> I((fade finished))
    I --> J[hide]
    A -. "a NEW flash() call
    arrives mid-fade" .-> B
```

A repeated Ctrl+[ / Ctrl+] press always restarts at step B — the
running fade and hold timer are stopped first, so rapid presses never
stack a half-faded toast under a fresh one.
