# Dialog — Flow

**About:** [description](../__about/dialog.md)

## Layout

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart TB
    subgraph WIN["ObservatoryDialog — A4 portrait, 80% of screen height"]
        HEADER["dual-calendar header — the effective moment's date"]
        subgraph SCROLL["QScrollArea"]
            subgraph SPLIT["QSplitter (vertical) — 5 draggable panels"]
                P1["1. Season durations
                checkbox filter row · Collapse · Enlarge"]
                P2["2. Light − dark envelope
                Days/Hours filter row · Collapse · Enlarge"]
                P3["3. Eclipse timeline
                Collapse · Enlarge"]
                P4["4. Day length over the year
                Collapse · Enlarge"]
                P5["5. Laskar long envelope (±200,000y)
                Collapse · Enlarge"]
            end
        end
        CLOSE["Close"]
    end
    HEADER --> SCROLL --> CLOSE
```

Each panel's chart is one `ChartBase` subclass instance; "Enlarge"
reparents that SAME instance into a separate `EnlargeDialog` (16:9 at
50% of screen height) and back on close.

## Algorithm — Enlarge / close cycle (the fixed crash)

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart TB
    A["_open_enlarged(panel)"] --> B["record panel's splitter index
    hide panel.title_label"]
    B --> C["panel.setParent(enlarge_dialog)"]
    C --> D["enlarge_dialog.show() — non-modal"]
    D --> E((user closes the Enlarge dialog))
    E --> F["_close_enlarged — finished signal"]
    F --> G["panel.setParent(None)"]
    G --> H["splitter.insertWidget(index, panel)  — FIRST"]
    H --> I["restore panel.title_label"]
    I --> J["enlarge_dialog.deleteLater()  — ONLY AFTER the reparent"]
```

The crash this pins: `EnlargeDialog` must NOT carry
`WA_DeleteOnClose` — that flag queues the dialog's own C++ destruction,
and since `panel` was a real Qt child of it, the queued deletion could
destroy `panel` before step H ran. Reparenting back BEFORE the explicit
`deleteLater()` call is what makes the order safe.
