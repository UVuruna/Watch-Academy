# Cube Preview3D Bridge

**Script:** [Cube Preview3D Bridge (script)](../cube_preview3d.py) · **Flow:** [diagram](../__flow/cube_preview3d.md)

## Purpose
The GUARDED bridge to the sibling 3D Preview gadget (WORKPLAN Session
28): imports the gadget, builds and validates the Character-Cube model,
and hands back a ready-to-show 3D panel for one of four page kinds —
or `None`, for any reason at all, which is the reader's own signal to
keep its computed 2D plate ([Cube Diagrams](cube_diagrams.md)).

## Connections

### Uses
- `data.cube_model_export` — the Qt-free model builder this module
  validates and mounts
- `config.paths.preview3d_gadget_dir()` — the sibling folder guess
- The sibling gadget's own `preview3d` package
  (`Preview3DLightWidget`, `validate`) — imported lazily, guarded,
  never at module import time

### Used by
- `app.encyclopedia.reader` — `build_widget(kind, key)` on every
  diagram page; `None` keeps the existing [Cube
  Diagrams](cube_diagrams.md) plate

## The four kinds, and what each shows
| Kind | Key | Gadget view |
|---|---|---|
| `cube` | — | `"cube"` — everything, glass at 0.12 |
| `axes` | — | a 3-button switcher (Primary/Secondary/Tertiary) |
| `axis` | axis name | `"axis:<name>"` — that axis lit, the rest faint |
| `pole` | seat name | `"pole:<name>"` — that one seat lit |

## Design Decisions
- **`build_widget()` answers `None` and logs, never raises**, for every
  failure mode: no gadget folder beside the project, an import failure,
  a schema-invalid exported model, an out-of-scope `kind`
  (`terms`/`sets`/`hexagram`/`banknote` stay computed 2D), or a
  build/mount exception. This is root Rule #1's documented fallback
  path, not error masking — the failure is logged, and the reader's own
  2D drawer is the intended degradation.
- **Nothing runs at import time.** Importing this module does no work —
  the gadget import and the model build+validate each happen ONCE,
  cached, the first time a page actually asks for a widget (the
  Encyclopedia never-block law).
- **`_CubePreviewPanel` is the ONE widget contract** for every
  cube-family page — the reader only ever asks for a widget and calls
  `set_square_size(side)`.
- **Render layer, not app layer** — imports `config`, `core`, `data`
  and the gadget, never `app`, keeping the one-way flow intact.
