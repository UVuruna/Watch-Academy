# Text Resolution — Flow

**About:** [description](../__about/text.md)

## Algorithm — `article_text(ref, ...)`, the one dispatch every page reads through

```mermaid
%%{init: {'flowchart': {'subGraphTitleMargin': {'top': 0, 'bottom': 35}}}}%%
flowchart TB
    A[ref = kind, ...] --> B{kind}
    B -- verses --> C[Serbian verses + explanation + commentary, joined]
    B -- guide --> D[inline prose from the ref itself]
    B -- article --> E[symbolism.article set, body .base]
    B -- article_face --> F[symbolism.article ...faces.face, falls back to base]
    B -- zodiac / chinese / element --> G[symbolism.*_article / chinese_element]
    B -- week / instrument / season / sun / moon / era / eclipse --> H[encyclopedia.section key .base]
    B -- emblem --> I[encyclopedia.entry family, name .base]
    B -- theme_title / week_duality --> J[encyclopedia.theme_title / week_duality .base]
    B -- else --> K[symbolism.trio_article virtue .base]
```

Pseudocode:

    FUNCTION article_text(ref, symbolism, encyclopedia, tr):
        kind <- ref[0]
        MATCH kind:
            "verses"       -> join(verses, explanation, commentary)
            "guide"        -> ref[1]                       # already localized prose
            "article"      -> symbolism.article(set, body).base
            "article_face" -> symbolism.article(set, body).faces[face] OR .base
            "zodiac" | "chinese" | "element" -> the matching symbolism lookup
            "week" | "instrument" | "season" | "sun" | "moon" | "era" | "eclipse"
                           -> encyclopedia.<kind>(key).base
            "emblem"       -> encyclopedia.entry(family, name).base
            "theme_title" | "week_duality" -> encyclopedia.<kind>(key).base
            DEFAULT        -> symbolism.trio_article(virtue).base

## Algorithm — `flow_html(text, tr)`

    strip every _HEX_NOTE occurrence
    FOR EACH paragraph IN text split on blank lines:
        IF paragraph starts with a [[Subhead]] marker:
            emit a centered bold heading (label translated via tr)
            paragraph <- the remainder after the marker
        emit paragraph, justified, with spine terms bolded (_highlight_terms)
    wrap the whole result in one <div>
