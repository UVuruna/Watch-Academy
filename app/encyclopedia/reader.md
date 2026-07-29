# Reader Screen

**Script:** [Reader Screen (script)](reader.py)

## Purpose
Level three — the article slider: the entry's image row or grid, its
bold name, the full article, the look/finish switcher and the pager. The
⬇ **Download BUTTON** sits in the dialog's header row (owner
2026-07-29), but the DEED stays here as the public `download_entry()` —
it saves the open page, and the open page lives on this screen.

Everything that SIZES an article moved here verbatim from the retired
single module — the block-width formula, the em-like font growth, the
image-height ceiling, the lazy decode cache and THE INVISIBLE CLIPPER
fix. Those carry a long tail of ground-truthed owner bug fixes and must
not be re-derived.

## Connections

### Uses
- [Text Resolution](text.md) — prose, names, HTML, tooltips
- [Topic Tree](tree.md) — `switch_variant`, the pure offset law
- [Asset Recolor](../../render/asset_recolor.md) / [Asset Variants](../../render/asset_variants.md) — pending metal variants and decode-ceiling downscales
- [Diagrams](../../render/diagrams.md) — the computed 2D plate every
  diagram page falls back to
- [Cube Preview3D Bridge](../../render/cube_preview3d.md) — a diagram
  page tries this FIRST (Session 28); `None` keeps the 2D plate above
  exactly as before this session

### Used by
- [Encyclopedia Dialog](dialog.md)

## Two switchers, deliberately unalike

| Control | Where | Changes |
|---|---|---|
| VARIANT | beside the title (the dialog) | which REGISTER is read |
| LOOK | the reader's own top row | the ART REGISTER of this page |

`switch_variant(delta)` applies the offset law: the page's position
inside the register is kept, and clamped when the next register is
shorter.

## Design Decisions
- **The horizontal bar is switched off** and `_block_width` clamps to the
  viewport — the no-X-scroll law, enforced twice.
- **A pending metal variant counts as PRESENT** (owner order
  2026-07-26): its source is on disk and the pixels build on first
  display, so a cold cache never hides the Gold/Silver looks.
- **`_rescale()` runs BEFORE `setWidget`** — the fix for the invisible
  clipper: a fresh widget handed to a QScrollArea is sized on a first
  pass and only corrected on a second, which page turns never reach.
- **THE 3D SWAP is lazy and additive** (Session 28, the Encyclopedia
  never-block law): `cube_preview3d.build_widget()` is called only
  inside `_show_entry()` — never at dialog construction — and only for
  the page actually being shown; its `None` path is byte-identical to
  what this screen did before the gadget existed. `_diagram_side()`
  factors the one sizing formula both the 2D plate and the 3D panel
  obey, so neither can ever push the article off screen.
