# Reader Screen

**Script:** [Reader Screen (script)](../reader.py) · **Flow:** [diagram](../__flow/reader.md)

## Purpose
Level three — the article slider: one entry's image row (or grid), its
bold name, the full article, the look/finish switcher and the pager. The
⬇ Download BUTTON sits in the dialog's header row (owner 2026-07-29),
but the DEED stays here as the public `download_entry()` — it saves the
open page, and the open page lives on this screen.

Everything that SIZES an article moved here VERBATIM from the retired
single `app/encyclopedia.py` — the block-width formula, the em-like font
growth, the image-height ceiling, the lazy decode cache and THE
INVISIBLE CLIPPER fix. Those carry a long tail of ground-truthed owner
bug fixes and must not be re-derived.

What is genuinely NEW here is the variant step: `switch_variant` walks
the theme's registers keeping the reader's position inside the block
(Monday stays Monday), replacing the retired Pantheon/Planetary roster
button, which only knew how to do this for exactly four themes.

## Connections

### Uses
- [Text Resolution](text.md) — `article_text`, `entry_name`, `flow_html`, `image_tooltip`
- [Topic Tree](tree.md) — `switch_variant`, the pure offset law
- [Asset Recolor](../../../render/__about/asset_recolor.md) — `ensure_variant`, `variant_pending`
- [Asset Variants](../../../render/__about/asset_variants.md) — `scaled_variant_file`, the decode-ceiling downscale
- [Diagrams](../../../render/__about/diagrams.md) — `diagrams.plate`, the computed 2D plate every diagram page falls back to
- [Cube Preview3D Bridge](../../../render/__about/cube_preview3d.md) — `build_widget(kind, key)`, tried FIRST for a diagram page (Session 28); `None` keeps the 2D plate exactly as before
- [Compositor](../../../render/__about/compositor.md) — `_HEX_NOTE`, `_SUBHEAD`, shared with the Download path's text formatting

### Used by
- [Encyclopedia Dialog](dialog.md) — the third stacked screen

## Classes

### ReaderScreen
`QWidget`, `page_changed = Signal()`, `zoomed = Signal(float)`.

- `__init__(topics, symbolism, encyclopedia, tr)`
- `topic_key` / `entry_index` / `topic` / `look_state` (properties):
  the open page's reading position and its current look/finish state
  (`None` when the page has only one look)
- `open_topic(key, index=0)`: opens a topic, index clamped to its length
- `step(delta)`: ← Previous / Next →, wraps around
- `switch_variant(delta)`: the ◀ / ▶ VARIANT step — delegates the
  arithmetic to `tree.switch_variant`, pure and tested without a widget
- `set_zoom(zoom)`: applies the session zoom and re-scales
- `_show_entry()`: rebuilds the current page — image cells, name, text,
  look switcher, diagram/3D panel — into one centered block
- `_block_width()` / `_rescale()`: the article block's width formula and
  the live font/pixmap re-fit on every resize
- `_diagram_side(block_width)`: the square a computed diagram (2D plate
  or 3D panel) fits inside — the same height ceiling art images obey
- `_pixmap(path)`: the decoded-image cache behind the lazy looks
- `_render_cell(state, block_width)` / `_resize_cell(state, block_width)`:
  build a look's image grid once, then only re-scale it on resize
- `_cycle_look(step)` / `_update_look_caption()`: the LOOK switcher —
  distinct from the VARIANT switcher (see below)
- `download_entry()`: saves the open page's current-look image(s) and
  article text into a folder the user picks
- `resizeEvent(event)` / `eventFilter(obj, event)`: live re-fit on
  resize; Ctrl+wheel-over-viewport zoom (a plain wheel scrolls untouched)

## Two switchers, deliberately unalike

| Control | Where | Changes |
|---|---|---|
| VARIANT | beside the title (the dialog) | which REGISTER is read |
| LOOK | the reader's own top row | the ART REGISTER of this page |

## Design Decisions
- **The horizontal bar is switched off** and `_block_width` clamps to
  the viewport — the no-X-scroll law, enforced twice.
- **A pending metal variant counts as PRESENT** (owner order
  2026-07-26): its source is on disk and the pixels build on first
  display, so a cold cache never hides the Gold/Silver looks.
- **`_rescale()` runs BEFORE `setWidget`** — the fix for THE INVISIBLE
  CLIPPER: a fresh widget handed to a `QScrollArea` is sized on a first
  pass and only corrected on a second, which a page turn's single click
  handler never reaches.
- **THE 3D SWAP is lazy and additive** (Session 28, the never-block
  law): `cube_preview3d.build_widget()` is called only inside
  `_show_entry()` — never at dialog construction — and only for the
  page actually being shown; its `None` path is byte-identical to what
  this screen did before the gadget existed.
- **Finish persistence** (owner INSTRUCTION #3): `_preferred_look_label`
  rides every following entry that offers the same look, never resets
  silently on a page turn or topic change.
