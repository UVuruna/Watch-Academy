# settings_dialog/

The M6 settings window (menu "Settings…") for what the tray submenus and the
Watch Face window cannot express: location, language and system — one
dialog, THREE navigation sections (Phase 6 FINAL cleanup narrowed this from
seven — see below).

**MIXIN PILOT** (God-File Split Phase 2 Step 2, `research/REFACTOR_PLAN.md`
§7): this package replaces the old flat `app/settings_dialog.py` (1,566
lines). The dialog originally self-organized into seven nav sections — the
cleanest split boundary in the plan (UI-given, not inferred) — so each
section's group-builder methods and their private helpers moved VERBATIM
into their own plain-Python mixin class, composed onto the `QDialog` shell
via multiple inheritance.

**PHASE 6 FINAL CLEANUP (Watch Face & Settings UI rework, R-02)** retired
three of those seven nav sections outright: Display, Colors and Themes.
Their whole content — Opacity, Element sizes, the Archetype group's
names/daylight/cube-look switches, Palette, Ring/Clock tint, Saturation,
Theme rotation, Artwork, Subdial plate set, Metal shades — now lives
LIVE-APPLY in the Watch Face window (`app.watch_face`, see [Watch Face]
(../watch_face/___watch_face.md)) instead of this dialog's on-OK commit; the
`display_section.py`/`colors_section.py`/`themes_section.py` mixins and their
docs are DELETED, not deprecated in place (Rule "No Backward Compatibility").
The Custom art section is the one survivor with a twist: its editor
(`custom_art_section.py`) still lives here — Structure Law forbids a second
copy of the same editor inside `watch_face` — but it is no longer a visible
sidebar row. It is reached only through a HIDDEN, no-sidebar construction
mode (`initial_section="Custom art"`, see [dialog.md](__about/dialog.md)'s
Design Decisions) that the Watch Face Ring section's "Custom ring…" button
opens.

## Files

| File | Tier | One line |
|------|------|----------|
| `dialog.py` | Algorithmic | composition-root `QDialog` shell — nav wiring, sizing, lifecycle, `result_settings()` — [about](__about/dialog.md) · [flow](__flow/dialog.md) |
| `location_section.py` | Algorithmic | cascading 45,650-city picker + Quick Jump cities — [about](__about/location_section.md) · [flow](__flow/location_section.md) |
| `custom_art_section.py` | Algorithmic | Custom ring and Custom hands builders — reachable ONLY via the hidden `initial_section="Custom art"` mode since Phase 6 — [about](__about/custom_art_section.md) · [flow](__flow/custom_art_section.md) |
| `language_system_section.py` | Algorithmic | Language, Calendar eras, System groups — [about](__about/language_system_section.md) · [flow](__flow/language_system_section.md) |
| `__init__.py` | Trivial | bare module docstring — no re-exports (Rule #6); every caller imports `SettingsDialog` from `dialog.py` directly |

## Layout — the navigation rework (owner ROADMAP 15h item 1, 2026-07-18; narrowed Phase 6)

The dialog used to be one long scroll of group boxes, then seven nav
sections; Phase 6 FINAL cleanup narrowed the ORDINARY path to three. It is a
`QListWidget` NAVIGATION COLUMN on the left (each row a section title with a
trailing right arrow "▸") plus a `QStackedWidget` on the right — clicking a
title shows THAT section's panel; `self._nav_list.currentRowChanged` drives
`self._stack.setCurrentIndex`. Every remaining control lives under one of
THREE sections built in `dialog.py.__init__` as a `(title, [group_boxes])`
pair:

| Section | Groups | Mixin |
|---|---|---|
| Location | Location, Quick Jump cities | `_LocationSectionMixin` |
| Language | Language, Calendar eras | `_LanguageSystemSectionMixin` |
| System | System (autostart + Visibility Z mode) | `_LanguageSystemSectionMixin` |

Each panel is wrapped in its OWN `QScrollArea` (`panel_scroll`,
`setWidgetResizable(True)`) — the scroll cap that used to sit around the
WHOLE dialog now sits around each panel individually, since only one panel
is visible at a time; a tall panel still scrolls internally.

A SEPARATE, HIDDEN construction path (`initial_section="Custom art"`) skips
this nav column outright: `self._nav_list`/`self._stack` stay `None`, and the
dialog shows a single `QScrollArea` holding just the Custom art mixin's two
groups (Custom ring, Custom hands). Nothing ever routes a user there by
browsing — only `app.watch_face.ring`'s "Custom ring…" button opens it.

**OPENING SIZE (owner DESIGN #1, R4 instruction batch 2026-07-20):** square
(1:1) at 50% of the screen's available height (`app.theme.size_to_screen`,
`defaults.DIALOG_SQUARE_HEIGHT_FRACTION`) — content-driven width
(`max(sizeHint)` over every panel's inner content widget plus the nav
column's fixed width `defaults.SETTINGS_NAV_WIDTH_PX`, zero in the hidden
Custom-art-only mode) is the `min_width` FLOOR passed into `size_to_screen`
("whichever is larger wins", the same resolution the Encyclopedia's gallery
min-width applies) — it wins over the square width whenever the busy panels
would otherwise need a horizontal scrollbar to fit, but the HEIGHT always
stays the requested 50% exactly (each panel's own vertical `QScrollArea`
already absorbs any height it does not fit in).

OK applies and persists Location/Language/System's own fields (or, in the
hidden mode, `custom_rings` alone) — every OTHER `Settings` field passes
through UNCHANGED, since the Watch Face window already applies it live and
an OK here must never clobber that pick with a stale default; Cancel
discards everything. The dialog loads the location tree on open
(`dialog.py.__init__`, ordinary mode only) and releases it on close
(`dialog.py.done`, safe in either mode) — the repository's documented
lifecycle. All chrome strings resolve through the [UI Text Catalog]
(../../config/__about/ui_text.md) (translation Phase 2) via `dialog.py._tr`,
inherited by every mixin — the controller passes the active overlay.

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
- [Config (folder)](../../config/___config.md) — city/timezone data, era/
  language tables (every remaining mixin)
- `app.native` — autostart state (`language_system_section.py`)

### Used by
- [Watch Controller](../__about/controller.md) — opens it from the menu (the
  ordinary Location/Language/System path); applies the result (new
  observer/timezone → day-context rebuild)
- [Watch Face — Ring section](../watch_face/__about/ring.md) — opens it with
  `initial_section="Custom art"` (the hidden path)

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
- **Phase 6 deleted, never deprecated-in-place** (Rule "No Backward
  Compatibility"): `display_section.py`, `colors_section.py` and
  `themes_section.py` are GONE, not kept as dead code behind a flag — every
  caller (`dialog.py`'s class statement and `sections` list,
  `tests/test_settings_dialog.py`) was grepped and updated in the same
  round. Three real gaps this surfaced (the rotation GROUP picker + per-theme
  metal combos, the Artwork combo, the Subdial plate SET combo — R-20 had
  deferred exactly these three "until Phase 6") were PORTED into
  `app.watch_face.themes` rather than silently dropped — see that module's
  own docstring.
- **Custom art stays reachable but hidden from the sidebar** (Phase 6): see
  [dialog.md](__about/dialog.md)'s Design Decisions for the full reasoning —
  in short, duplicating the editor inside `watch_face` would violate Rule #5
  (no second copy), so the ordinary dialog offers a SEPARATE, sidebar-free
  construction path instead.