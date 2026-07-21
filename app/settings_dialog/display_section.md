# Display Section

**Script:** [Display Section (script)](display_section.py)

## Purpose

`_DisplaySectionMixin` — the **Display** nav section: Opacity, Element
sizes and Archetype groups. Plain-Python mixin (no base class);
composed onto [Settings Dialog](dialog.md)'s `QDialog` shell.

## The groups

- **Opacity** — three sliders (percent): Star (its twilight alpha
  scales proportionally with the day value), plus Aura sunlight and
  Aura twilight as two INDEPENDENT overrides (owner spec — no coupling
  ratio between them). "Skin default" resets a slider and clears its
  override. The Moon marker's below-horizon dimming is a plain 0-100%
  scale (owner spec 2026-07-12), not an override.
- **Element sizes** (owner EXTRAS) — five multiplier sliders (Earth,
  Moon, Weekday/Slot, Ring letters; 50–200%, default 100%) plus the
  shared Hover enlarge slider (100–200%, default 120% — the element
  under the cursor grows by it; 100% disables the effect) and the
  custom DIAMETER control (owner 2026-07-17 ROADMAP 15e, exact spinbox
  added 2026-07-18 ROADMAP 15h item 12b): a slider spanning the
  smallest to the largest menu preset (360…1440, the fixed Size
  presets stay in the menu) PLUS a `QSpinBox` (`self._diameter_spin`,
  same range) synced TWO-WAY with it — either widget moving drags the
  other along (`sync_spin`/`sync_slider`, each guarded with
  `blockSignals` to avoid feedback) — applied together on OK exactly
  like a menu preset pick. The SATURATION slider that used to live
  here moved OUT (owner verdict, Session 21-D) into [Colors Section]
  (colors_section.md).
- **Archetype** (owner 2026-07-18, Session 21-C — "nemoj ispod nego u
  Settings — ON/OFF, spreman sam za predloge") — one checkbox,
  "Archetype names": its OWN independent switch (`archetype_names`) for
  the archetype figures' display names, separate from the weekday
  bodies' own Names option; `render.layers.ArchetypeLayer` reads it
  directly. The whole control for now — the owner is open to a richer
  dropdown here later.

`_slider_row()` is the shared percent-slider-with-reset-button builder
used only by `_build_opacity_group` (Colors' saturation sliders build
their own inline row instead — see [Colors Section](colors_section.md)).

## Connections

### Uses
- [Config (folder)](../../config/___config.md) — `constants.
  ELEMENT_SCALE_RANGE`/`HOVER_ENLARGE_RANGE`, `defaults.SIZE_PRESETS`/
  `DEFAULT_DIAL_DIAMETER`

### Used by
- [Settings Dialog](dialog.md) — the shell's `__init__` calls
  `_build_opacity_group()`, `_build_sizes_group()`,
  `_build_archetype_group()`; `result_settings()` reads
  `self._star_slider`/`_aura_day_slider`/`_aura_twilight_slider`/
  `_moon_alpha_slider`/`_size_sliders`/`_diameter_slider`/
  `_archetype_names_check`

## Classes

### _DisplaySectionMixin
- `_build_opacity_group() -> QGroupBox`: Star/Aura/Moon opacity sliders
- `_slider_row(value, default, which)`: one percent slider + label +
  "Skin default" reset button, wired to set/clear `self._{which}_override`
- `_build_archetype_group() -> QGroupBox`: the Archetype names checkbox
- `_build_sizes_group() -> QGroupBox`: the five size sliders + the
  synced Diameter slider/spinbox pair
