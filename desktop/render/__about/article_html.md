# Article HTML

**Script:** [Article HTML (script)](../article_html.py)

## Purpose
THE ARTICLE HTML VOCABULARY — prose in, rich text out. Every string the
program shows a reader as an ARTICLE is built here: a hover legend, the
Encyclopedia's reflowing page, a downloaded `.txt`'s paragraph split.

The rules are the owner's and they are SHARED — THE LEGEND BOLD LAW (the
spine terms in plain bold, hex notes stripped), THE HOVER TEASER LAW (a
hover speaks its thesis, never the whole article), the `[[Subhead]]`
marker, the justified column, the LEARN MORE footer. They lived inside
[Compositor](compositor.md), a 3,800-line painting module, which is
exactly why the Encyclopedia had to import PRIVATE names out of the
render layer to reuse them — findings **L1** and **L2** of the [OOP
audit](../../../docs/AUDIT-OOP-2026-08-18.md), which named them one
finding: *"the free HTML helpers want `render/article_html.py`, after
which the encyclopedia imports a public name from a module that is about
text."*

Nothing here paints, measures a widget or knows a window.

## Connections

### Uses
- [Config (folder)](../../config/___config.md) — `encyclopedia_ui`
  (article sizing, subhead gaps, the legend term patterns), `palette`
  (the LEARN MORE link colours), `defaults` (the hover badge width),
  `paths`
- [Asset Variants](asset_variants.md) — `scaled_variant_file`, so an
  embedded article image is a downscaled copy and not the master

### Used by
- [Compositor](compositor.md) — every tooltip and hover legend it builds
- [Encyclopedia Text](../../app/encyclopedia/__about/text.md) —
  `flow_html` is `article_paragraphs` inside a `<div>`
- [Encyclopedia Reader](../../app/encyclopedia/__about/reader.md) —
  `HEX_NOTE` / `SUBHEAD` when writing an article out as plain text
- `tests/test_skins.py`, `tests/test_eclipse.py` — the law-level
  assertions (bolding, teaser truncation, the footer's two roads)

## Functions

- `centered(*lines)` / `centered_html(*lines)`: centered tooltip rich
  text — the first escapes, the second takes lines that are already
  safe HTML. Each line owns one full-width no-wrap row, because
  QToolTip otherwise wraps at its own narrow heuristic.
- `ordinal(n)`: `9<sup>th</sup>`, the raised suffix of the hover rework.
- `HEX_NOTE` / `SUBHEAD`: the two article MARKERS as compiled patterns —
  a trailing ` (#F8E600)` colour note (never displayed) and a leading
  `[[Subhead]]`. Public because three readers need them.
- `highlight_terms(escaped)`: THE LEGEND BOLD LAW applied to an already
  escaped line.
- `teaser(text)`: THE HOVER TEASER LAW — the first
  `LEGEND_TEASER_SENTENCES` of the first paragraph, ellipsised.
- `learn_more_footer(tr)`: the separated LEARN MORE link plus the SPACE
  hint.
- `article_paragraphs(text, tr)`: the justified paragraphs with subheads
  — the shared body every article view is built from.
- `article_body_html(text, tr)`: those paragraphs in one fixed-width
  table cell (the legend popup measures the document and honors it).
- `hover_title(text_html)`: the bigger, bold, centered title line.
- `article_html(image, title_html, text, tr)`: one whole ARTICLE hover —
  art, optional title, teaser.
- `hover_badge(path)`: the emblem above an arm hover; empty when the art
  is missing.

## Design Decisions
- **Public names, on purpose.** These are read by the app layer. A
  private name imported across a layer boundary is the defect L1
  recorded; making them public is not cosmetics, it is the fix.
- **`_crown_arc_centre` and `_greetings` did NOT come along.** One is
  dial geometry and one reads a JSON book; neither turns prose into
  HTML, so both stayed in the compositor where their callers are.
- **The `<div>` wrapper stayed with its caller.** The Encyclopedia's
  reflowing page needs a block element and the hover legend's
  fixed-width table does not — that one difference is the whole of
  `text.flow_html`, which was otherwise a line-for-line copy of
  `article_paragraphs`.
