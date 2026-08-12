# Watch Face Opacity Section

**Script:** [Opacity Section (script)](../opacity.py)

## Purpose
Phase ④ (R-15/R-36 + the moved rows): the Watch Face window's real
Opacity page — every render alpha channel this Phase's render hooks
make speakable, grouped "Clock body" (Pointer, Aura sunlight/twilight,
Umbra) and "Bodies on the ring" (Moon below horizon, Inactive icons,
Crown Text). LIVE-APPLY, sliders apply on release.

Three rows were MOVED from the RETIRED `app.settings_dialog.
display_section._build_opacity_group` (Phase 6 FINAL cleanup deleted
that copy outright). Two are NEW: R-15 Umbra opacity (owner-requested,
a layer-alpha multiplier), R-36 "Inactive icons" (the weekday ghost
bodies' existing opacity). A third, "Crown Text" (`crown_text_alpha`,
R-24/Phase-6-debt correction, owner 2026-08-05), was added the same
round the Phase ④ debt note calling "Crown Text" nonexistent was
corrected — the outer Great Seal crown text arc IS this element
(`skin.ring.crown_text`, `RingLayer._draw_crown_text`); a direct row
like `umbra_alpha`, greyed out with a tooltip
(`setters["ring_has_crown_text"]`) on crown-text-less presets.

**THE MOON HORIZON BAND MOVED OUT (owner verdict 2026-08-10):** its
group used to sit FIRST on this page (owner verdict 2026-08-09, ALG-7
ROW OCCUPANCY); it now lives in [Hands & Bodies](bodies.md)'s "Moon"
group beside the rest of what the Moon carries.

**THE MOON TRANSIT OPACITY ROW IS DEAD (owner verdict 2026-08-10):**
the translucent Moon/Earth transit dimming this row ("Moon — hover over
Earth", `moon_transit_alpha`) used to control was RETIRED outright when
`moon_transit_style` gained three geometry-only crossing treatments —
none of them dims. The row is REMOVED from this page;
`Settings.moon_transit_alpha` stays defined so an old settings file
still loads without a migration, but no render hook reads it.

## Connections

### Uses
- [Watch Controller](../../__about/controller.md) —
  `setters["opacity_skin_defaults"]()`, a data PROVIDER (not a scalar
  setter, Rule #5) supplying the active skin's own values for every
  None-override slider's "Skin default" reset

### Used by
- `app.watch_face.window` — registered as the Opacity section's builder

## Design Decisions
- **None-override rows** (`star_alpha`, `aura_day_alpha`,
  `aura_twilight_alpha`, `ghost_alpha`): "Skin default" resets the
  STORED override to `None`, not merely the slider position, so the
  render side actually stops overriding — mirrors `app.settings_dialog.
  display_section`'s existing pattern exactly.
- **Direct rows** (`moon_hidden_alpha`, `umbra_alpha`, `crown_text_alpha`):
  no None state, "Default" resets to the field's own documented default.
- **Open-list note (every alpha channel found through R-15/R-35/R-36):**
  the rows above were every alpha a `Settings`-reachable render hook
  could bind to at the time. Two more alpha-shaped fields turned up and
  are NOT wired, both owner-tuned ART CONSTANTS with no settings hook
  anywhere today (not even in the OLD Settings dialog): `skins.manifest.
  YearMarkerSpec.moon_shadow_alpha` (the terminator darkness over the
  Moon disc) and the reveal-week opacity ramp tied to
  `defaults.REVEAL_WEEK_DURATION_S`. Wiring either now would be a new
  feature this task never asked for, not a move — left alone, undebted
  (no control anywhere points at them for this round to remove).
