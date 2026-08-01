# Text Resolution

**Script:** [Text Resolution (script)](../text.py) · **Flow:** [diagram](../__flow/text.md)

## Purpose
Prose in, HTML out — four widget-free functions the reader, the
Download path and the tests all share. They used to be methods on the
old monolithic dialog class; nothing about them needed a window, so
they moved out here (Rule #5).

## Connections

### Uses
- [Symbolism Repository](../../../data/__about/symbolism.md), [Encyclopedia Repository](../../../data/__about/encyclopedia.md) — the prose these functions resolve against
- [Compositor](../../../render/__about/compositor.md) — `_HEX_NOTE`, `_SUBHEAD`, `_highlight_terms` (Rule #5: the reader highlights exactly like the dial's hover legends)

### Used by
- [Reader Screen](reader.md) — every page's name, text and image tooltips resolve through here

## Functions

- `flow_html(text, tr=None) -> str`: article prose that reflows with the
  window — hex notes stripped, spine terms bolded, `[[Subhead]]` markers
  drawn as centered bold headings, everything else justified
- `image_tooltip(path) -> str`: the plate's filename stem, underscores
  opened to spaces, Title-Cased only when the stem carries no capital of
  its own
- `article_text(ref, symbolism, encyclopedia, tr=None) -> str`: the ONE
  resolver from an entry's `("kind", ...)` article ref to its prose —
  every surface (the page, the Download file, the tests) reads through
  this single dispatch
- `entry_name(entry, symbolism, encyclopedia, tr) -> str`: THE ONE BUILD
  POINT for a page's display name — database-titled pages take their
  title from the encyclopedia database, everything else translates
  through the UI overlay; a `"weekday"` key on the entry appends
  `" — {Weekday}"` here and only here

## Design Decisions
- **The weekday suffix is appended here and ONLY here** ("Selene —
  Monday") — no other call site needs to know the convention exists.
- **Inline-data refs** (`"verses"`, `"guide"`) carry their prose in the
  ref tuple itself — content that lives outside `encyclopedia.json` is
  read where it already is, never copied into it.
- **`article_face` falls back to `"base"`** when a theme's GOOD/EVIL
  split has not landed a `"faces"` register yet (Rule #1 — a documented
  graceful path, never a `KeyError`).
