# settings_dialog/

The M6 settings window (menu "Settings…") for everything the tray submenus
cannot express: location, display, colors, custom art, themes, language and
system — one dialog, seven navigation sections.

**MIXIN PILOT** (God-File Split Phase 2 Step 2, `research/REFACTOR_PLAN.md`
§7): this package replaces the old flat `app/settings_dialog.py` (1,566
lines). The dialog already self-organized into seven nav sections — the
cleanest split boundary in the plan (UI-given, not inferred) — so each
section's group-builder methods and their private helpers moved VERBATIM
into their own plain-Python mixin class, composed onto the `QDialog` shell
via multiple inheritance. Every control, every signal connection, every line
of `result_settings()` is byte-identical to before the split — only the file
each method lives in changed.

## Files

| File | Tier | One line |
|------|------|----------|
| `dialog.py` | Algorithmic | composition-root `QDialog` shell — nav wiring, sizing, lifecycle, `result_settings()` — [about](__about/dialog.md) · [flow](__flow/dialog.md) |
| `location_section.py` | Algorithmic | cascading 45,650-city picker + Quick Jump cities — [about](__about/location_section.md) · [flow](__flow/location_section.md) |
| `display_section.py` | Algorithmic | Opacity, Element sizes, Archetype groups — [about](__about/display_section.md) · [flow](__flow/display_section.md) |
| `colors_section.py` | Algorithmic | Saturation, Palette, Clock (ring) tint groups — [about](__about/colors_section.md) · [flow](__flow/colors_section.md) |
| `custom_art_section.py` | Algorithmic | Custom ring and Custom hands builders — [about](__about/custom_art_section.md) · [flow](__flow/custom_art_section.md) |
| `themes_section.py` | Algorithmic | Theme rotation, Artwork, Subdial plate, Metal shades — [about](__about/themes_section.md) · [flow](__flow/themes_section.md) |
| `language_system_section.py` | Algorithmic | Language, Calendar eras, System groups — [about](__about/language_system_section.md) · [flow](__flow/language_system_section.md) |
| `__init__.py` | Trivial | bare module docstring — no re-exports (Rule #6); every caller imports `SettingsDialog` from `dialog.py` directly |

## Layout — the navigation rework (owner ROADMAP 15h item 1, 2026-07-18)

The dialog used to be one long scroll of group boxes. It is now a
`QListWidget` NAVIGATION COLUMN on the left (each row a section title with a
trailing right arrow "▸") plus a `QStackedWidget` on the right — clicking a
title shows THAT section's panel; `self._nav_list.currentRowChanged` drives
`self._stack.setCurrentIndex`. Every existing control still exists — none
dropped, `result_settings()` untouched — just filed under one of SEVEN
sections built in `dialog.py.__init__` as a `(title, [group_boxes])` pair;
related groups SHARE one title exactly where the owner's own example
applies — Palette + Clock tint = Colors:

| Section | Groups | Mixin |
|---|---|---|
| Location | Location, Quick Jump cities | `_LocationSectionMixin` |
| Display | Opacity, Element sizes, Archetype | `_DisplaySectionMixin` |
| Colors | Palette, Clock (ring) tint, Saturation | `_ColorsSectionMixin` |
| Custom art | Custom ring, Custom hands | `_CustomArtSectionMixin` |
| Themes | Theme rotation, Artwork, Subdial plate, Metal shades | `_ThemesSectionMixin` |
| Language | Language, Calendar eras | `_LanguageSystemSectionMixin` |
| System | System (autostart + Visibility Z mode) | `_LanguageSystemSectionMixin` |

Each panel is wrapped in its OWN `QScrollArea` (`panel_scroll`,
`setWidgetResizable(True)`) — the scroll cap that used to sit around the
WHOLE dialog now sits around each panel individually, since only one panel
is visible at a time; a tall panel still scrolls internally.

**OPENING SIZE (owner DESIGN #1, R4 instruction batch 2026-07-20):** square
(1:1) at 50% of the screen's available height (`app.theme.size_to_screen`,
`defaults.DIALOG_SQUARE_HEIGHT_FRACTION`) — content-driven width
(`max(sizeHint)` over every panel's inner content widget plus the nav
column's fixed width `defaults.SETTINGS_NAV_WIDTH_PX`) is the `min_width`
FLOOR passed into `size_to_screen` ("whichever is larger wins", the same
resolution the Encyclopedia's gallery min-width applies) — it wins over the
square width whenever the busy panels would otherwise need a horizontal
scrollbar to fit, but the HEIGHT always stays the requested 50% exactly
(each panel's own vertical `QScrollArea` already absorbs any height it does
not fit in).

OK applies and persists everything; Cancel discards. The dialog loads the
location tree on open (`dialog.py.__init__`) and releases it on close
(`dialog.py.done`) — the repository's documented lifecycle. All chrome
strings resolve through the [UI Text Catalog](../../config/__about/ui_text.md)
(translation Phase 2) via `dialog.py._tr`, inherited by every mixin — the
controller passes the active overlay.

## Connections

### Uses
- [Locations](../../data/__about/locations.md) — the hierarchy and city
  records (`location_section.py`)
- [Rings](../../data/__about/rings.md), [Hands](../../data/__about/hands.md)
  — the custom ring/hand-pack machinery (`custom_art_section.py`)
- [Settings Store](../__about/settings_store.md) — reads/writes the chosen values
  (`dialog.py`)
- [Theme](../__about/theme.md) — the Rule #16 POLISH round's dark QSS: nav column,
  group-box cards, every slider/combo/spinbox/checkbox, OK/Cancel (`dialog.py`)
- [Config (folder)](../../config/___config.md) — palette presets, ranges,
  weekday/theme titles (every mixin)
- [Asset Variants](../../render/__about/asset_variants.md), [Asset Recolor]
  (../../render/asset_recolor.md) — the derivation the Subdial plate / Metal
  shade pickers feed (`themes_section.py`)
- `app.native` — autostart state (`language_system_section.py`)

### Used by
- [Watch Controller](../__about/controller.md) — opens it from the menu; applies the
  result (new observer/timezone → day-context rebuild, display overrides →
  skin reinstall)

## Design Decisions

- **Mixins are PLAIN PYTHON — never `QObject`-derived** (`research/
  REFACTOR_PLAN.md`'s split-technique policy #2): every `_*SectionMixin`
  class declares no base (`class _LocationSectionMixin:`); only
  `dialog.SettingsDialog` derives from `QDialog`. Mixing two `QObject`-branch
  bases would break shiboken's metaclass — this is why the section classes
  stay ordinary Python classes composed by multiple inheritance, never
  parallel `QWidget` subclasses.
- **No re-export barrel.** `__init__.py` stays a bare module docstring
  (monorepo Rule #6) — every caller imports `SettingsDialog` from
  `app.settings_dialog.dialog`, never from the package root.
- **Method bodies moved verbatim** — an AST-based marker extraction
  (start-of-decorator..`end_lineno` per method) proved a byte-exact,
  lossless partition of the original 52 methods across the shell + 6 mixins
  before any file was written (same discipline as [Asset Recolor]
  (../../render/asset_recolor.md)'s step-1 precedent).
- **Inline section-banner comments were NOT carried over.** The original
  file's `# --- Section ---` banners had already drifted out of sync with
  the nav-section groupings by the time of this split — most notably a
  `# --- Language ---` banner that actually preceded the Artwork/Subdial
  plate/Metal shades methods (a Themes-section concern), a pre-existing
  documentation bug the split makes newly visible rather than propagates.
  Each method's own docstring was already the authoritative explanation, so
  the per-file `__about/` docs rely on those plus this folder doc's tables
  above.
