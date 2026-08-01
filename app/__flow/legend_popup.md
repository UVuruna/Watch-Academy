# Legend Popup — Flow

**About:** [description](../__about/legend_popup.md)

## Layout

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart TB
    subgraph WIN["LegendPopup — frameless ToolTip-class window, topmost band"]
        SCROLL["QScrollArea (vertical only)"]
        LABEL["QLabel, RichText, fixed width
        links accessible by mouse (LEARN MORE footer)"]
    end
    SCROLL --> LABEL
```

## Algorithm — `show_html(content, anchor)`

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart TB
    A[show_html content, anchor] --> B{content changed since last show?}
    B -- no --> H[reposition only]
    B -- yes --> C["cap = screen.width * LEGEND_MAX_WIDTH_FRACTION"]
    C --> D["measure content in an offscreen QTextDocument
    at textWidth = cap -> idealWidth"]
    D --> E["label.setFixedWidth(idealWidth + padding)"]
    E --> F{idealWidth + padding > cap?}
    F -- yes --> G[enable horizontal scrollbar]
    F -- no --> G2[keep it off]
    G --> I[label.setText, adjustSize]
    G2 --> I
    I --> J["resize popup to
    min(label size, screen fraction caps)"]
    J --> H
    H --> K["clamp position beside anchor,
    fully on-screen"]
    K --> L[show + assert_topmost]
```

Pseudocode:

    FUNCTION show_html(content, anchor):
        IF content == last shown content:
            reposition only, RETURN
        cap <- screen(anchor).width * LEGEND_MAX_WIDTH_FRACTION
        document.setHtml(content); document.setTextWidth(cap)
        wanted <- ceil(document.idealWidth()) + 2*LEGEND_PADDING_PX
        label.setFixedWidth(max(wanted, 1))
        scrollbar.horizontal <- (wanted > cap) ? AsNeeded : AlwaysOff
        label.setText(content); label.adjustSize()
        popup.resize(min(label.width + frame, cap),
                     min(label.height, screen.height * LEGEND_MAX_HEIGHT_FRACTION))
        position popup beside anchor, clamped to the screen
        show(); native.assert_topmost(popup)
