# Text Resolution

**Script:** [Text Resolution (script)](text.py)

## Purpose
Prose in, HTML out — the four widget-free functions the reader, the
Download path and the tests all share:

- `article_text(ref, ...)` — the article ref to the prose behind it
- `entry_name(entry, ...)` — THE ONE BUILD POINT for a page's display name
- `flow_html(text, tr)` — reflowing, justified article HTML with the
  spine terms bolded and `[[Subhead]]` markers drawn as headings
- `image_tooltip(path)` — the plate's own name on hover

## Connections

### Uses
- [Symbolism Repository](../../data/symbolism.md), [Encyclopedia Repository](../../data/encyclopedia.md)
- [Compositor](../../render/compositor.md) — `_highlight_terms` and the shared subhead/hex-note patterns (Rule #5: the reader highlights exactly like the dial legends)

### Used by
- [Reader Screen](reader.md)

## Design Decisions
- **The weekday suffix is appended here and ONLY here** — "Selene -
  Monday". No other call site needs to know the convention exists.
- **Inline-data refs** (`verses`, `guide`) carry their prose in the ref
  itself: content that lives outside `encyclopedia.json` is read where it
  is, not copied into it.
