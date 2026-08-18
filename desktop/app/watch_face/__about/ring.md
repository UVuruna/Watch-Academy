# Ring Section

**Script:** [Ring Section (script)](../ring.py) · **Flow:** [diagram](../__flow/ring.md)

## Purpose
The Watch Face window's Ring page (R-10), rebuilt for THE
COMPOSITIONAL RING MODEL (owner decree 2026-08-05): preset gallery
(thumbnail tiles of each preset's own COMPUTED preview — the outer
plate with its jewels stamped at their seats, ring_rework §5, owner
ruling 2026-08-06 — tooltip stating the locked outer AND the card's own
About text), the finish pills, the Shine checkbox (unchanged; TWO
METALS retired — owner decree 2026-08-11), an INNER gallery (eight
tiles — user-changeable
independent of the locked outer), a word-wrapped label showing the
ACTIVE preset's own About (THE SPACE & LEGIBILITY LAW — never only a
tooltip) and a Crown group (read-only preset text, or a custom ring's
own typed text + top/bottom orientation) — plus R-13's "Custom ring…"
button. RING VERDICTS round (owner correction 2026-08-05) added two
things to the Crown group: the typed field's `QLineEdit` now carries a
WHITELIST `QValidator` (`_crown_text_validator`, built straight off
`constants.RING_CROWN_TEXT_CHARSET`) so an unsupported character can
never be typed at all — a tooltip states exactly what is allowed — and
every ring (preset or custom) gained a "Location" checkbox that
replaces the crown text with the active location's own "CITY,
COUNTRY" (`setters["ring_crown_location"]`).

**THE CROWN GETS ONE SEAT (ballot verdict 5C, 2026-08-15):** the group
grew from "Crown text" to "Crown" and now holds all six controls a
reader sees as one thing — text, Location, Time format
(`crown_time_format`, moved from `numerals.py`), color (`crown_text_tint`,
moved from `colors.py`), size (`crown_text_scale`, moved from
`size.py`) and opacity (`crown_text_alpha`, moved from `opacity.py`).
`_crown_time_format_row` builds the plain combo; `_crown_style_row`
builds the color popover plus two `ValueKnob`s (labeled Tint/Scale/
Alpha rather than Color/Size/Opacity — ALG-9 SECTION TAXONOMY reads
those bare words as claims on the Colors/Size/Opacity pages) and
carries the graceful-truth gate ONCE, on the whole sub-widget, for
`setters["ring_has_crown_text"]`. The text/Location/Time-format
controls stay live even with no crown text yet, on purpose: for a
custom ring the text box IS how that text gets typed in the first
place, so gating it too would lock the field shut forever.

## Connections

### Uses
- [Watch Face Thumbnails](thumbs.md) — `ring_preset_thumbnail`,
  `art_thumbnail` (fallback)
- [Controls](controls.md) — `picture_group`, `ValueKnob`/`knob_row`,
  the one gallery/knob doors
- [Watch Face Shared Widgets](widgets.md) — `pill`, `FlowLayout`
- [Tint Control](tint_control.md) — `tint_control`, the Crown color row
- [Rings (data)](../../../data/__about/rings.md) — `ring_presets`
- [Config (folder)](../../../config/___config.md) — `RING_OUTERS`,
  `RING_OUTER_LOCK`, `RING_INNERS`, `RING_INNER_PRESET_DEFAULT`,
  `RING_INNER_DEFAULT`, `RING_FINISHES`, `RING_EYE_GLYPH`,
  `RING_EYE_SHINE_DEFAULT`, `RING_CROWN_TEXT_CHARSET`,
  `CROWN_TIME_FORMATS`, `ELEMENT_SCALE_RANGE`,
  `palette.RING_TINT_GROUPS`/`RING_TINT_PICKER_SEED`

### Used by
- `app.watch_face.window` — registered as the Ring section's builder

## Design Decisions
- **Whitelist, not a hand list:** the validator's character class is
  built from `constants.RING_CROWN_TEXT_CHARSET` (every SINGLE-
  character key of `LETTER_PLATE_FILES` — the multi-character symbol
  keys are the custom-builder's own jewel picks, never typed running
  text — plus the space), the exact same set
  `app.skin_builder._location_crown_text` filters the Location crown
  through. One source, never two lists drifting apart (Rule #5).
- **R-13 honesty note:** `app/settings_dialog/custom_art_section.py`'s
  custom-ring flow is a plain-Python mixin baked directly onto
  `SettingsDialog` — there is no standalone custom-ring editor `QDialog`
  to embed. Rather than duplicate its inline widgets (a name field, a
  layout combo, a per-position jewel-combo row, thematic color, "Add
  ring"), the "Custom ring…" button opens the EXISTING Settings dialog
  through `setters["open_custom_ring"]`, navigated straight to its
  Custom art section via the new `dialog.SettingsDialog(...,
  initial_section="Custom art")` parameter — honest reuse, not a second
  editor to keep in sync.
