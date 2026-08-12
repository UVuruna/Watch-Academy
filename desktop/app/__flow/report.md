# Report -- Flow

**About:** [description](../__about/report.md)

## Layout

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart TB
    subgraph WIN["ReportDialog window -- 760x620, stay-on-top"]
        TITLE["Top functions by total time"]
        BAR["_BarChart -- horizontal bars, top N by total_ns"]
        SPARK["_Sparkline -- selected row's recent durations"]
        TABLE["QTableWidget -- Function | Calls | Average | Min | Max | Total | Last
        sortable, one row selectable"]
        BUTTONS["Reset   Download                    Close"]
    end
    TITLE --> BAR --> SPARK --> TABLE --> BUTTONS
    TABLE -- "itemSelectionChanged" --> SPARK
```

## Algorithm -- refresh cycle (every configured interval)

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart TB
    A[QTimer tick] --> B["snap = profiling.snapshot()"]
    B --> C["remember selected row NAME and sort column/order"]
    C --> D["rebuild table rows from snap
    (sorting disabled during rebuild)"]
    D --> E["re-select the row with the remembered name, if still present"]
    E --> F["re-enable sorting, re-apply sort column/order"]
    F --> G[refresh charts]
    G --> H["bar chart <- top N rows by total_ns"]
    G --> I["sparkline <- snap[selected]['recent'] if selected in snap else empty"]
```

Selection is tracked by function NAME, never by row index -- the table
re-sorts every cycle, so an index-based "selected row" would silently
point at a different function a moment later.
