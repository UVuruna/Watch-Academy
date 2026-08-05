# Settings Dialog

**Script:** [Settings Dialog (script)](../dialog.py) · **Flow:** [diagram](../__flow/dialog.md)

## Purpose

The composition-root shell of the M6 settings window — Phase 6 FINAL cleanup
narrowed it to THREE nav sections (`QListWidget` + `QStackedWidget` — see
[settings_dialog (subfolder)](../___settings_dialog.md) for the full layout
and per-group narrative): Location, Language, System. The Display, Colors and
Themes sections' whole content now lives LIVE-APPLY in the Watch Face window
(`app.watch_face`) instead. This shell composes the three remaining section
mixins via multiple inheritance and owns the dialog's own cross-section
concerns — translation lookup, the location-repository lifecycle, and
assembling the final `Settings` on OK.

`__init__` branches on `initial_section == "Custom art"`: the ORDINARY path
calls every `_build_*_group()` method (one per remaining mixin) to construct
the three `(title, [group_boxes])` sections; the HIDDEN path instead builds
ONLY the Custom art mixin's two groups (ring + hands) in a single scrollable
page with no nav column at all — see the Design Decisions below. A section's
group entry may instead be a `(group_box, stretch)` pair (R-29): the page's
`QVBoxLayout` gives that ONE group the layout's stretch factor instead of the
trailing spacer, so it consumes every pixel of leftover vertical space — used
by the Location page's Quick Jump cities group, whose own list otherwise sat
capped in a mostly-empty page.

## Connections

### Uses
- [Location Section](location_section.md), [Custom Art Section]
  (custom_art_section.md), [Language & System Section]
  (language_system_section.md) — the three mixins composed onto this shell's
  class statement
- [Locations](../../../data/__about/locations.md) — `LocationRepository`, constructed
  in `__init__`, released in `done`
- [Settings Store](../../__about/settings_store.md) — `Settings`, `replace`
- [Theme](../../__about/theme.md) — `apply_theme`, `size_to_screen`, `style_dialog_buttons`
- [Config (folder)](../../../config/___config.md) — `constants`, `defaults`
- [UI Text Catalog](../../../config/__about/ui_text.md) — `ui()`, wrapped by `_tr`

### Used by
- [Watch Controller](../../__about/controller.md) — opens it from the menu (the
  ordinary 3-section path); applies the result (new observer/timezone →
  day-context rebuild)
- [Watch Face — Ring section](../../watch_face/__about/ring.md) — opens it with
  `initial_section="Custom art"` (the hidden path)

## Classes

### SettingsDialog(QDialog, _LocationSectionMixin, _CustomArtSectionMixin, _LanguageSystemSectionMixin)

- `__init__(settings, skin, overlay=None, parent=None, initial_section=None)`:
  ordinarily builds the three sections (see the [folder doc]
  (../___settings_dialog.md)'s layout table) prefilled from the current
  settings (combos restored from the stored city path), wires
  `self._nav_list`/`self._stack` and sizes the dialog from the widest/tallest
  panel's inner content. `initial_section="Custom art"` instead sets
  `self._custom_art_only = True`, skips the nav column/`_stack` entirely
  (both left `None`) and builds a single scrollable page holding just the
  Custom ring/hands groups — used by `app.watch_face.ring`'s "Custom ring…"
  button so it never needs to duplicate that mixin's inline widgets
  (Structure Law: one editor, one owner, reached two ways).
- `_tr(text) -> str`: the active language's form of a chrome string (Phase 2)
  — inherited by every mixin, none of which re-declare it
- `done(result)`: releases the location tree before closing (the
  repository's documented lifecycle) — safe to call in EITHER mode, since
  `LocationRepository()` is always constructed even when its widgets are not
- `result_settings() -> Settings`: the edited values as a new frozen
  `Settings` (valid only after Accepted). In the hidden Custom-art-only mode
  it touches ONLY `custom_rings`; otherwise it touches Location/Language/
  System's own fields — every OTHER field (every one the retired Display/
  Colors/Themes sections used to own, now live-applied through the Watch
  Face window) is simply omitted from `replace()`, so it passes through
  UNCHANGED from `self._settings` rather than being clobbered by a widget
  that no longer exists.

## Design Decisions

- **Custom art stays reachable but hidden from the sidebar** (Phase 6): the
  custom-ring/custom-hands editor
  (`app.settings_dialog.custom_art_section._CustomArtSectionMixin`) is a
  plain-Python mixin baked directly onto this shell, not a standalone dialog
  — duplicating its inline widgets inside `app.watch_face` would violate
  Rule #5 (no second copy of the same editor). Rather than leaving it as a
  fourth visible sidebar row (which would misleadingly suggest the retired
  Display/Colors/Themes groups might return beside it), the dialog offers a
  SEPARATE construction path: `initial_section="Custom art"` skips the nav
  column outright and shows just that one page. The only caller
  (`app.watch_face.ring`'s "Custom ring…" button) always wants exactly this,
  never the ordinary three-section view.
