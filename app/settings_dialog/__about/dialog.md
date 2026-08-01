# Settings Dialog

**Script:** [Settings Dialog (script)](../dialog.py) · **Flow:** [diagram](../__flow/dialog.md)

## Purpose

The composition-root shell of the M6 settings window: builds the seven-section
navigation (`QListWidget` + `QStackedWidget` — see [settings_dialog
(subfolder)](../___settings_dialog.md) for the full layout and per-group
narrative), composes the six section mixins via multiple inheritance, and
owns the dialog's own cross-section concerns — translation lookup, the
location-repository lifecycle, and assembling the final `Settings` on OK.

`__init__` calls every `_build_*_group()` method (one per mixin) to construct
the seven `(title, [group_boxes])` sections; those calls resolve through the
MRO onto whichever mixin actually defines the method — the shell itself
defines none of the group builders.

## Connections

### Uses
- [Location Section](location_section.md), [Display Section](display_section.md),
  [Colors Section](colors_section.md), [Custom Art Section](custom_art_section.md),
  [Themes Section](themes_section.md), [Language & System Section]
  (language_system_section.md) — the six mixins composed onto this shell's
  class statement
- [Locations](../../../data/__about/locations.md) — `LocationRepository`, constructed
  in `__init__`, released in `done`
- [Settings Store](../../__about/settings_store.md) — `Settings`, `replace`
- [Theme](../../__about/theme.md) — `apply_theme`, `size_to_screen`, `style_dialog_buttons`
- [Config (folder)](../../../config/___config.md) — `constants`, `defaults`,
  `palette.effective_palette_style` (normalizes a stray stored "cube" style
  before the preset lookup), `palette.PALETTE_PRESETS`
- [UI Text Catalog](../../../config/__about/ui_text.md) — `ui()`, wrapped by `_tr`

### Used by
- [Watch Controller](../../__about/controller.md) — opens it from the menu; applies
  the result (new observer/timezone → day-context rebuild, display overrides
  → skin reinstall)

## Classes

### SettingsDialog(QDialog, _LocationSectionMixin, _DisplaySectionMixin, _ColorsSectionMixin, _CustomArtSectionMixin, _ThemesSectionMixin, _LanguageSystemSectionMixin)

- `__init__(settings, skin, overlay=None, parent=None)`: builds the seven
  sections (see the [folder doc](../___settings_dialog.md)'s layout table)
  prefilled from the current settings (combos restored from the stored city
  path), wires `self._nav_list`/`self._stack` and sizes the dialog from the
  widest/tallest panel's inner content
- `_tr(text) -> str`: the active language's form of a chrome string (Phase 2)
  — inherited by every mixin, none of which re-declare it
- `done(result)`: releases the location tree before closing (the
  repository's documented lifecycle)
- `result_settings() -> Settings`: the edited values as a new frozen
  `Settings` (valid only after Accepted) — reads instance state set by every
  mixin (`self._hues`, `self._ring_tint`, `self._rotation_group`,
  `self._custom_rings`, `self._language_combo`, `self._jump_cities`,
  `self._art_source_combo`, `self._size_sliders`, …)
