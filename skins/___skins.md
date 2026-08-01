# skins/

The typed RENDER CONFIGURATION — Qt-free so it is pytest-testable. All
rendering is driven by one `SkinDefinition` instance: `DEFAULT_SKIN` in
[Config (folder)](../config/___config.md), onto which the controller
overlays the chosen RING PRESET and the user's display choices at build
time (`build_skin` in [Watch Controller](../app/__about/controller.md)).

**DOMY and PILOT are ring preset names — nothing more** (owner
decision): a ring face in `assets/ring/` plus its Greek-ordinal letter
positions, read by `data.rings.ring_presets()` from
`Database/ring_presets.json` (five presets today: DOMY, PILOT, The One,
Templar, Dollar — PILOT was renamed from "MORPH"). There are no skin
folders and no skin.json packs; all art is shared app content under
`assets/`.

Seven dial pointer wheels exist (`manifest.SkinDefinition.pointer`,
`config.constants.POINTER_POINTS`/`POINTER_DISPLAY_NAMES`): four ARMED
wheels — **hexa/Prism** (6, the default), **cross/Quaternity** (4),
**octa/Compass** (8), **trio/Trinity** (3, half of hexa) — whose star
diamonds carry the palette, and three ARMLESS wheels — **aurora/Aurora**
(7 bands), **calendar/Calendar** (12 wedges), **rose/Rose** (an octa
star drawn three times at 15deg, 8 hues dressing 24 visible rays). Slot
layout, palette-style wiring and per-pointer render behavior are
[Render (folder)](../render/___render.md)'s concern, not this folder's —
`manifest.py` only declares which strings are valid.

## Files

| File | Tier | One line |
|------|------|----------|
| `manifest.py` | Algorithmic | the six unit dataclasses + `SkinDefinition`'s display scalars + `missing_assets()` — [about](__about/manifest.md) · [flow](__flow/manifest.md) |
| `__init__.py` | Trivial | package docstring only, no exports |

## Connections

### Uses
- Nothing (stdlib dataclasses only — importable from anywhere)

### Used by
- [Config (folder)](../config/___config.md) — `DEFAULT_SKIN` (`config/defaults.py`)
- [Render (folder)](../render/___render.md) — `compositor.py`/`layers.py` read the specs
- [Watch Controller](../app/__about/controller.md) — `build_skin` + display overlays

## Design Decisions

- **A ring preset is a NAME, nothing more** (owner decision). It is data
  (`Database/ring_presets.json`, read by `data.rings.ring_presets()`),
  never a code constant — adding a sixth preset costs a database entry,
  not a line of Python.
- **No skin folders, no `skin.json` packs.** Every asset is shared app
  content under `assets/`; `SkinDefinition` is composed in memory from
  `DEFAULT_SKIN` plus the chosen ring preset plus the user's display
  choices, never read back from a per-skin file.
- **Qt-free on purpose**, the same reason as [Recolor (folder)](../recolor/___recolor.md):
  pure dataclasses stay importable and pytest-testable with no display
  server, and the render layer (`render/layers.py`) is the only place
  that turns a `SkinDefinition` into pixels.
