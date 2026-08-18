# Charts — Flow

**About:** [description](../__about/charts.md)

## Algorithm — zoom / pan (`ChartBase`)

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart TB
    A[wheelEvent] --> B["_zoom_at(cursor_x_px, factor)"]
    B --> C["new span = current span / factor,
    clamped to _zoom_floor(full_span)"]
    C --> D["re-center the visible x range on cursor_x_px"]
    D --> E["_fit_y_to_view() — y axis fits the new x slice"]
    E --> F[repaint]
    G[mouse drag while zoomed] --> H[pan the visible x range]
    H --> E
    I[double-click] --> J["_reset_view() — full span, un-zoomed"]
    J --> E
```

`_zoom_floor(full_span)` is the overridable seam: `LineChart` floors at
the median gap between consecutive x samples of its first visible
series (so a decimated 20-year-stride bundle cannot be zoomed to a
misleading 1-year view of interpolated points); `EclipseChart` floors
at the median gap between eclipse years, or the density bucket width.
