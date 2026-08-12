# Size Section

**Script:** [Size Section (script)](../size.py) · **Flow:** [diagram](../__flow/size.md)

## Purpose
The Watch Face window's Size page: the diameter slider + spinbox +
Default + the five `dial.SIZE_PRESETS` buttons (the SAME two-way
slider/spinbox sync `display_section._build_sizes_group` uses, plus
`design_window.DesignDialog._size_tab`'s preset row) and every element
scale slider — Earth, Moon, Complications (`slot_scale`), Jewels
(`ring_jewels_scale`), Crown Text (`crown_text_scale`, R-24/Phase-6-debt
correction, owner 2026-08-05), Hover enlarge — wired to the SAME
stored setting keys the Settings dialog's "Element sizes" group uses
(Rule #5, no renamed keys this phase; only the on-screen labels read
"Complications"/"Jewels" instead of "Slot"/"Ring Jewels"). The Crown
Text row multiplies `crown_text_scale` ON TOP OF `ring_jewels_scale`
(unaffected) and greys itself out with a tooltip
(`setters["ring_has_crown_text"]`) when the active ring preset carries no
crown text.

## Connections

### Uses
- [Watch Face Shared Widgets](widgets.md) — `pill`
- [Config (folder)](../../../config/___config.md) — `dial.SIZE_PRESETS`,
  `dial.DEFAULT_DIAL_DIAMETER`, `dial.MENU_SIZE_SLIDER_STEP`,
  `constants.ELEMENT_SCALE_RANGE`, `constants.HOVER_ENLARGE_RANGE`

### Used by
- `app.watch_face.window` — registered as the Size section's builder

## Design Decisions
- Every scale slider commits on `sliderReleased` (matching
  `design_window.py`'s curvature slider's own commit timing) — the
  Default button both resets the slider AND applies immediately, since
  this window is live-apply, unlike the Settings dialog's transactional
  "Default" (which only resets the widget; OK commits later).
