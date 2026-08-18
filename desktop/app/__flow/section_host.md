# Section Host — Flow

**About:** [description](../__about/section_host.md)

## Layout — what the host builds

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart LR
    subgraph HOST["SectionHost (a QWidget, margins 0)"]
        NAV["QListWidget
        fixed width = max(SETTINGS_NAV_WIDTH_PX,
        longest title + SETTINGS_NAV_CHROME_PX)"]
        STACK["QStackedWidget
        one QScrollArea per section"]
    end
    NAV -- currentRowChanged --> STACK
    STACK --> P1["QScrollArea -> (page_holder) -> page 1"]
    STACK --> P2["QScrollArea -> (page_holder) -> page 2"]
    STACK --> PN["QScrollArea -> (page_holder) -> page N"]
```

The window hands in `(label, page)` pairs. It never hands in a builder:
the pages are built by whoever owns their state, so nothing has to be
passed out of the host and back again.

## Algorithm — the declared minimum

```mermaid
flowchart TB
    A["polish_pages(): every page and child ensurePolished()
    — the theme's paddings are part of the real size
    (measured 20px on the Colors groups)"] --> B{"measure_minimum?"}
    B -- "True (Watch Face:
    flow galleries reflow)" --> C["hint = page.minimumSizeHint()"]
    B -- "False (Settings:
    panels do not reflow)" --> D["hint = page.sizeHint()"]
    C --> E["content_width = max(hint.width)
    tallest = max(hint.height)"]
    D --> E
    E --> F["width = nav_width + content_width
    + scrollbar extent + the WINDOW's own chrome"]
    E --> G["height = tallest + the WINDOW's own chrome
    (its margins, and its button row where it has one)"]
    F --> H["min(width, SCREEN_FLOOR.w)"]
    G --> I["min(height, SCREEN_FLOOR.h)"]
    H --> J[("setMinimumSize")]
    I --> J
```

The floor is THE SPACE & LEGIBILITY LAW's ladder step 4: past it the
pages scroll, because the window is genuinely full. The host answers for
the sidebar, the widest page and the scrollbar — the three numbers both
windows had written out identically; each window still adds the chrome
only it knows about.

## The live-pick rebuild (Watch Face only)

```mermaid
flowchart LR
    A["a pick applies"] --> B["controller.refresh()"]
    B --> C["previous = host.current_row()
    scrolls = host.capture_scrolls()"]
    C --> D["rebuild.clear_layout(body)
    — hide BEFORE setParent(None),
    or the old host flashes as a window"]
    D --> E["build nine pages, new SectionHost"]
    E --> F["host.set_current_row(previous)"]
    F --> G["host.restore_scrolls(scrolls)
    twice: now, and queued after the layout pass
    (a scrollbar's range is still 0 until then)"]
```

A pick may change the WATCH and nothing else — never the section, never
the scroll, never the focused side of the window (owner decree
2026-08-10).
