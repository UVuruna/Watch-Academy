# Encyclopedia Dialog — Flow

**About:** [description](../__about/dialog.md)

## Layout sketch

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart TB
    subgraph WINDOW["EncyclopediaDialog (QDialog, non-modal)"]
        subgraph HEADER["header_row — ONE QHBoxLayout, three groups"]
            direction LR
            CRUMBS["crumbs_group (stretch 1)<br/>⌂ Home · breadcrumb"]
            TITLE["title_group (stretch 0)<br/>◀ Title — Register ▶"]
            DOWNLOAD["download_group (stretch 1)<br/>⬇ Download"]
        end
        subgraph STACK["QStackedWidget"]
            HOME["0 · HomeScreen"]
            THEMES["1 · ThemeScreen"]
            READER["2 · ReaderScreen"]
        end
    end
    HEADER --> STACK
```

## Navigation state machine

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart LR
    A[Home] -- opened whole key --> B[Themes]
    B -- opened topic key --> C[Reader]
    C -- ⌂ Home button --> A
    B -- ⌂ Home button --> A
    C -- breadcrumb click --> B
    C -- ◀ ▶ variant switch --> C
```

## Algorithm — `navigate_to(topic, entry)`

    IF topic is None: RETURN                 # plain re-open, leave the window where it is
    target <- resolve_target(topics, topic, entry)
    IF target is None: RETURN                 # unknown/stale key, never raises
    key, index <- target
    reader.open_topic(key, index)
    stack.currentIndex <- READER
    reader.set_zoom(zoom)
    refresh_header()

## Algorithm — `_refresh_header()`

    screen <- stack.currentIndex
    home_button.visible <- screen != HOME
    download.visible    <- screen == READER
    MATCH screen:
        HOME    -> crumbs = "", title = "Encyclopedia"
        THEMES  -> crumbs = "› {whole.title}", title = whole.title, accent = whole.accent
        READER  -> crumbs = "› {whole.title}"
                   title  = "{topic.title}" (+ " — {register label}" if >1 variant)
                   accent = whole.accent
    variant_buttons.visible <- (screen == READER AND topic has >1 variant)
