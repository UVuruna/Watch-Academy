# Encyclopedia Tree — Flow

**About:** [description](../__about/encyclopedia_tree.md)

## The three-level tree

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart TB
    subgraph HOME["Home — 9 Whole cards, 3x3 grid, no scroll"]
        W1[instrument]
        W2[sky]
        W3[cosmos]
        W4[gods]
        W5[faith]
        W6[cube]
        W7[inner]
        W8[living]
        W9[worlds]
    end
    subgraph THEMES["Themes — the chosen Whole's own cards, Y scroll"]
        T1[theme card 1]
        T2[theme card 2]
        Tn[...]
    end
    subgraph ARTICLE["Article — the page slider"]
        P1[page 1]
        P2[page 2]
        SW[variant switcher\nif VARIANT_SOURCES has this topic]
    end
    HOME -->|tap a Whole| THEMES
    THEMES -->|tap a theme card| ARTICLE
    SW -.->|jump to another\nregister's pages| ARTICLE
```

## Variant switcher arithmetic

```
ON variant switch (direction d):
    offset ← current page − start of current variant
    next   ← (current variant + d) MOD variant count
    page   ← start of next + MIN(offset, length of next − 1)
```

The offset is what carries across a switch — Monday stays Monday when
the roster changes, and a shorter variant (the Wider Court has 4 pages
against Planetary's 11) clamps to its own last page instead of
overrunning.

## Jump resolution

```mermaid
flowchart TB
    A[dial theme key\ne.g. bible_dark] --> B{in TOPIC_ALIASES?}
    B -- yes --> C["(topic, variant index)\ne.g. (bible, 2)"]
    D[old flat Cube index\ne.g. 35] --> E["cube_target(35)"]
    E --> F{35 falls in which\nCUBE_TOPICS range?}
    F -- "6<=35<29" --> G["(cube_axes, 35-6)"]
    F -- past the end --> H[clamp to last projection page]
```

`cube_target` never raises — the caller is the dial, and a stale wheel
target must not take the window down.
