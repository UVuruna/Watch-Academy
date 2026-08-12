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
below it when the dial sits at the top edge of its screen. ONE position
for every flash since the owner's order of 2026-08-12 — a LOCATION change
used to take a second look (big font letters centered ON the dial, no
icon) and now wears the same plates in the same place, with its own logo.

## Algorithm — `flash()` lifecycle

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart TB
    A["flash(dial, icon, emoji, text)"] --> B["stop any running fade + hold timer
    opacity <- 1.0"]
    B --> C["icon: rasterize at 4x, smooth-scale down
    (the rays die at 1x)"]
    C --> C2["_set_plate_text(text) — gold head, silver tail"]
    C2 --> C3{"every glyph has a plate?"}
    C3 -- "no" --> C4["styled font for THIS text
    + the character named on stderr"]
    C3 -- "yes" --> D1["_position_above_or_below(dial)"]
    C4 --> D1
    D1 --> E["show(); native.assert_topmost"]
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
