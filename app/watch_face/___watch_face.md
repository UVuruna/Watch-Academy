# watch_face/

The Watch Face window — the owner-approved "Watch Face & Settings UI
rework": ONE window consolidating what USED TO BE four separate windows
(Design, Pointer Theme, Slot Theme, and the Settings dialog's own visual
groups — ALL DELETED by Phase 6 FINAL cleanup) into a single left-sidebar
+ right-page shell (the same list+stack shape [Settings Dialog]
(../settings_dialog/___settings_dialog.md) still uses for its own three
remaining sections) with EIGHT sections.

**Phase ①+② built the frame plus five real sections** (Pointer, Ring,
Hands, Umbra & Aura, Size) and the thumbnail service. **Phase ③ (R-17/
R-18/R-19/R-20) added the sixth: Themes & Slots** — the FACE LAYOUT row,
the SLOT PICKER, the breadcrumb content tree, the subdial plate pills
and the theme rotation controls. **Phase ④ (R-15/R-21..R-25/R-35/R-36)
replaced the last two placeholders: Colors and Opacity** — every
section had a real builder by then. **Phase 6 (FINAL cleanup) DELETED**
the old Design/Pointer Theme/Slot Theme windows and the Settings
dialog's Display/Colors/Themes sections outright, porting into the
Themes & Slots and Colors sections the few pieces they still solely
owned (the theme rotation GROUP picker + per-theme metal combos, the
Artwork/Subdial-set combos, the Calendar mount gallery) so nothing was
silently dropped.

## Files

| File | Tier | One line |
|------|------|----------|
| `__init__.py` | Trivial | bare module docstring — no re-exports |
| `window.py` | Algorithmic | the `WatchFaceDialog` shell — sidebar + stacked pages, live-apply refresh — [about](__about/window.md) · [flow](__flow/window.md) |
| `thumbs.py` | Algorithmic | R-33: the disk-cached thumbnail service (ring/hand art + the pointer palette-swatch fallback) — [about](__about/thumbs.md) · [flow](__flow/thumbs.md) |
| `widgets.py` | Standard | shared pill/tile builders every section imports — [about](__about/widgets.md) |
| `pointer.py` | Algorithmic | R-04/R-05/R-06: pointer gallery, shape/curvature/edge, night borders, Daylight-Night, Earth — [about](__about/pointer.md) · [flow](__flow/pointer.md) |
| `ring.py` | Algorithmic | R-10/R-13: ring gallery, finish, two-metals/shine, Custom ring… — [about](__about/ring.md) · [flow](__flow/ring.md) |
| `hands.py` | Algorithmic | R-14: hand-pack gallery, large hour-hand tiles — [about](__about/hands.md) · [flow](__flow/hands.md) |
| `umbra_aura.py` | Algorithmic | umbra form + contrast pills — [about](__about/umbra_aura.md) · [flow](__flow/umbra_aura.md) |
| `size.py` | Algorithmic | diameter + every element scale slider — [about](__about/size.md) · [flow](__flow/size.md) |
| `themes.py` | Algorithmic | R-17/R-19/R-20: FACE LAYOUT row, SLOT PICKER, subdial plate + rotation — [about](__about/themes.md) · [flow](__flow/themes.md) |
| `theme_tree.py` | Algorithmic | R-17/R-18: the breadcrumb content decision tree — [about](__about/theme_tree.md) · [flow](__flow/theme_tree.md) |
| `tint_picker.py` | Standard | shared round-swatch/preset-grid/custom-row builders every color control reuses — [about](__about/tint_picker.md) |
| `colors.py` | Standard | R-21..R-25: Ring tint, Palette, Umbra/Aura/Hands/Indices color, Metal shades, Saturation — [about](__about/colors.md) |
| `opacity.py` | Standard | R-15/R-35/R-36 + the moved rows: Clock body + Bodies-on-the-ring opacity sliders — [about](__about/opacity.md) |

## Layout — the sidebar

`window.py` holds ONE registry, `_SECTIONS`: an ordered tuple of
`(title, builder)` pairs, `builder(settings, setters, tr) -> QWidget` or
`None` for a not-yet-built placeholder page. `_build()` walks it once per
(re)build: a `QListWidget` row per section, a matching page in a
`QStackedWidget`, `currentRowChanged` wired straight to
`setCurrentIndex` — the same live-apply, keep-the-open-row rebuild the
RETIRED `design_window.DesignDialog._build` used to do for its
`QTabWidget` (the identical "a fresh container always opens at index 0"
bug, guarded the same way).

## Connections

### Uses
- [Theme](../__about/theme.md) — `apply_theme`, `size_to_screen`
- [Config (folder)](../../config/___config.md) — every pointer/ring/umbra/
  size table
- [Rings (data)](../../data/__about/rings.md), [Hands (data)]
  (../../data/__about/hands.md)
- [Raster Store](../../render/__about/raster_store.md) — `thumbs.py`'s
  cache, reused verbatim (Rule #5, no second cache mechanism)
- `render.skin_geometry.daylight_active` — the same duck-typed law
  `pointer.py`'s night-borders row reads off the raw `Settings` object
- [Settings Dialog](../settings_dialog/___settings_dialog.md) — `ring.py`'s
  "Custom ring…" button opens it, navigated to the hidden Custom art
  mode (`dialog.SettingsDialog(..., initial_section="Custom art")`)
- [Slot Descriptor](../__about/slot_descriptor.md) — the shared
  `SlotDescriptor` dataclass (`themes.py`/`theme_tree.py` read the SAME
  triple `app.controller._slot_descriptors()` builds, never a second
  copy, Rule #5)

### Used by
- [Watch Controller](../__about/controller.md) — `_open_watch_face`
  (non-modal, one live instance); `_watch_face_setters()` wraps every
  setter so a pick both applies AND refreshes the open window

## Design Decisions
- **R-33 honesty note:** pointer variants carry no dedicated preview art
  (they are procedural/abstract, and no render path can compose a small
  preview without a fully-built `Skin`). `thumbs.pointer_swatch_icon`
  therefore draws a pie of the pointer's ACTIVE palette wheel's own hues
  instead — real derived content (the exact colors the pointer paints),
  not invented art. See `thumbs.md` for the full note.
- **R-13 honesty note:** the custom-ring/custom-hands flow
  (`app/settings_dialog/custom_art_section.py`) is a plain-Python mixin
  baked directly onto `SettingsDialog`, not a standalone dialog —
  embedding it here would mean duplicating its inline widgets. `ring.py`'s
  "Custom ring…" button opens the EXISTING Settings dialog instead,
  navigated straight to its hidden, no-sidebar Custom art page via the
  `initial_section` parameter (Phase 6 FINAL cleanup: since the ordinary
  sidebar shrank to Location/Language/System, this is now the ONLY way
  that page is ever reached — see `settings_dialog/dialog.md`'s Design
  Decisions).
- **Placeholder pages carry no builder module of their own** — `window.py`
  renders them inline (`_placeholder_page`) since there is nothing to
  test or extract yet; a later phase replaces the `None` registry entry
  with a real module, following the same `(title, builder)` shape.
