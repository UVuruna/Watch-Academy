# Pointer Theme — Flow

**About:** [description](../__about/pointer_theme.md)

## Layout

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart TB
    subgraph WIN["PointerThemeDialog — square, 50% of screen height"]
        GATE["gate banner (hidden unless unavailable)"]
        subgraph BODY["body — weekday gallery alone, OR tabs on the Calendar pointer"]
            direction LR
            TAB1["Weekday bodies
            (Weekday Theme Grid)"]
            TAB2["Calendar mount
            (Weekday Theme Grid)"]
        end
    end
    GATE --> BODY
```

## Algorithm — content rebuild on refresh

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart TB
    A["refresh(theme, mount)"] --> B["old_body <- self._body"]
    B --> C["old_body.setParent(None)"]
    C --> D["old_body.deleteLater()"]
    D --> E["self._body <- _build(theme, mount)"]
    E --> F[layout.addWidget self._body]
```

    FUNCTION _build(current_theme, current_mount):
        weekday <- build_weekday_theme_grid(current_theme, on_pick, tr)
        IF current_mount is None OR on_pick_mount is None:
            RETURN weekday                       # single gallery
        RETURN QTabWidget with weekday + build_calendar_mount_grid(...)
