# Watch Face Window — Flow

**About:** [description](../__about/window.md)

## Layout

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart TB
    subgraph WIN["WatchFaceDialog — square, 50% of screen height"]
        direction LR
        NAV["QListWidget sidebar
        Pointer / Ring / Hands / Umbra & Aura /
        Opacity* / Themes & Slots* / Colors* / Size
        (* = placeholder page this phase)"]
        STACK["QStackedWidget
        one page per section"]
    end
    NAV -- currentRowChanged --> STACK
```

## Algorithm — rebuild on every pick

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart TB
    A["refresh(settings, setters)"] --> B["previous <- nav_list.currentRow()"]
    B --> C["clear the body layout"]
    C --> D["FOR title, builder IN _SECTIONS"]
    D --> E["nav_list.addItem(title)"]
    E --> F{"builder is None?"}
    F -- yes --> G["page <- placeholder page"]
    F -- no --> H["page <- builder(settings, setters, tr)"]
    G --> I["stack.addWidget(page)"]
    H --> I
    I --> D
    D --> J["nav_list.setCurrentRow(clamp(previous))"]
```

    FUNCTION _build():
        previous <- nav_list.currentRow() if nav_list exists else 0
        clear the body layout (old nav_list/stack deleteLater)
        nav_list, stack <- fresh QListWidget, QStackedWidget
        FOR title, builder IN _SECTIONS:
            nav_list.addItem(tr(title))
            page <- placeholder_page(tr) IF builder is None
                    ELSE builder(settings, setters, tr)
            stack.addWidget(page)
        nav_list.currentRowChanged -> stack.setCurrentIndex
        nav_list.setCurrentRow(clamp(previous, 0, count-1))
