# Cube Preview3D Bridge

**Script:** [Cube Preview3D Bridge (script)](cube_preview3d.py)

## Purpose

The GUARDED bridge to the sibling 3D Preview gadget (WORKPLAN Session
28, second attempt): imports the gadget, builds and validates the
Character-Cube model, and hands back a ready-to-show 3D panel for one
of the four amended page kinds — or `None`, for any reason at all,
which is the reader's own signal to keep its computed 2D plate.

## Connections

### Uses
- [Cube Model Export](../data/cube_model_export.md) — the Qt-free
  model builder this module validates and mounts
- [Frozen-Safe Paths](../config/___config.md#pathspy-frozen-safe-paths) —
  `preview3d_gadget_dir()`, the sibling folder guess
- The sibling gadget's own `preview3d` package (`Preview3DLightWidget`,
  `validate`) — imported lazily, guarded, never at module import time

### Used by
- [Reader Screen](../app/encyclopedia/reader.md) — `build_widget(kind,
  key)` on every diagram page; `None` keeps the existing
  `render.cube_diagrams` plate

## THE FALLBACK LAW

`build_widget()` answers `None`, and logs, for every one of these —
never raises:

- the gadget folder is not beside this project (a checkout without it,
  a renamed folder, a frozen build)
- the gadget package fails to import for any reason
- the exported model fails the gadget's own schema validation
- the page's `kind` is outside this session's amended scope (`cube`,
  `axes`, `axis`, `pole` only — `terms`/`sets`/`hexagram`/`banknote`
  stay computed 2D)
- building or mounting the widget itself raises

The gadget import and the model build+validate each happen ONCE,
cached — a page that already failed does not re-attempt the gadget on
every open.

## Nothing runs at import time (the Encyclopedia never-block law)

Importing this module does no work: no gadget import, no model build.
The FIRST page that actually asks for a widget pays that cost, exactly
once for the whole dialog's lifetime — never at dialog construction,
never for a page nobody opens.

## The four kinds, and what each shows

| Kind | Key | Gadget view |
|---|---|---|
| `cube` | — | `"cube"` — everything, glass at 0.12 |
| `axes` | — | a 3-button switcher (Primary/Secondary/Tertiary), opening on `"primary"` |
| `axis` | axis name | `"axis:<name>"` — that axis lit, the rest faint |
| `pole` | seat name | `"pole:<name>"` — that ONE seat lit, its axis's line full |

## Design Decisions

- **`_CubePreviewPanel` is the ONE widget contract** for every
  cube-family page — `reader.py` only ever asks for a widget and calls
  `set_square_size(side)`; whether that panel also carries a button row
  (the Thirteen Axes page alone) is this module's business, not the
  reader's.
- **Render layer, not app layer.** This module imports `config`,
  `core`, `data` and the gadget — never `app` — so the one-way flow
  (`config → core → data → skins → render → app`) holds; the tier
  buttons are styled inline rather than through `app.ui_style`.
