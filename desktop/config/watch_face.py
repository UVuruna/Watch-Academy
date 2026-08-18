"""THE WATCH FACE CONTROL VOCABULARY — which of the window's controls
write a setting and nothing else.

Most of the Watch Face window's ~72 controls do exactly one thing when
the owner picks a value: store it under its key and rebuild the skin.
That path is `WatchController._set_display_choice(key, value)`, and it
never varies. Until the OOP audit of 2026-08-18 the wiring was written
out fifty-six times —
`"pointer": wrap(lambda v: self._set_display_choice("pointer", v))` — a
three-line block per new setting, in a 4,400-line file, where the only
thing that changed was the key repeated twice on one line. That is a
table pretending to be code, which ONE KIND, ONE CLASS forbids: the
knowledge here is WHICH KEYS take the plain path, and knowledge is data.

The controls that are NOT here need a real method of their own — because
they touch more than one key (`ring`, `hands`, `palettes`), open a
window (`open_custom_ring`), or answer a question instead of setting
anything (`slot_descriptors`, `ring_has_crown_text`). Those stay written
out in `WatchController._watch_face_setters`, one line each, which is
where a reader should look to see that they are special.

Adding a plain setting is now ONE line: its key, in its section below.

Layer: config — pure data, imports nothing.
"""

# ═══════════════════════════ THE PLAIN DISPLAY CHOICES ═══════════════════════════
#
# Grouped by the Watch Face section that shows them, in the order the
# window builds them. Every key here is applied by
# `_set_display_choice(key, value)` and by nothing else; the eight
# MOVING BODY menus take the same path but are named by their own
# registry (`constants.MOVING_BODY_MENUS`) and are spliced in beside
# these rather than re-listed, so a body can never be added in one place
# and forgotten in the other.
DISPLAY_CHOICE_KEYS: tuple[str, ...] = (
    # --- Pointer -------------------------------------------------------
    "pointer",
    "palette_style",
    "pointer_shape",
    "polygon_curvature",
    "polygon_edge",
    "hide_night_borders",
    # `daylight` (R-05) moved here from the Settings dialog's Archetype
    # group under the SAME stored key — only its home changed.
    "daylight",
    # THE UNIFIED NAMES SWITCH (owner review 2026-08-09: the Names
    # switcher applies to the ARCHETYPE wheel too) — the stored keys stay
    # separate; the Watch Face checkbox writes this one alongside the
    # slot's own set_names.
    "archetype_names",
    # --- Ring ----------------------------------------------------------
    "ring_finish",
    # THE CALENDAR MOUNT (owner decree 2026-07-29): WHICH roster rides
    # the Calendar's twelve wedges — ported here from the retired Pointer
    # Theme window (Phase 6 FINAL cleanup); the SAME `_set_display_choice`
    # path, same stored key.
    "calendar_mount",
    # --- Bodies --------------------------------------------------------
    "umbra_form",
    "umbra_contrast",
    "earth_style",
    "transit_shadow",
    "transit_shrink",
    "transit_rim",
    "show_marker_pointer",
    "moon_band_mode",
    "moon_band_style",
    # --- Size (R- Size section: LIVE here, where the Settings dialog only
    # ever applied these on OK) ------------------------------------------
    "earth_scale",
    "moon_scale",
    "slot_scale",
    "ring_jewels_scale",
    "hover_enlarge",
    # --- Themes & Slots (Phase ③, R-17/R-18/R-19/R-20) ------------------
    "theme_rotation_minutes",
    "theme_metal_follow_ring",
    # Phase 6 FINAL cleanup: the rotation GROUP picker + the per-theme
    # metal combos, ported from the retired Settings dialog Themes
    # section (same stored keys — only the picker's home and its
    # live-vs-on-OK timing changed).
    "theme_rotation_group",
    "theme_rotation_themes",
    "art_source",
    # THE DEAD PILL (owner crash 2026-08-16): the Themes page's "Subdial
    # plate" row asked for `subdial_style` and it was never bound, so
    # clicking either pill raised KeyError — invisibly, because the
    # lookup sat inside the click callback and only fired if somebody
    # clicked. A key listed here is bound at build time, which is what
    # turns that latent crash into a window that will not open. Tooth:
    # tests/test_watch_face.py::test_every_page_key_has_a_setter.
    "subdial_style",
    "subdial_set",
    # --- Colors (Phase 4, R-21..R-25) -----------------------------------
    "pointer_saturation",
    "ring_saturation",
    "hands_saturation",
    "umbra_saturation",
    "ring_tint",
    "umbra_tint_mode",
    "umbra_tint",
    "aura_off_tint_mode",
    "aura_off_tint",
    "hands_tint",
    "jewels_tint",
    # --- The LIVE NUMERAL BANDS (ring_rework.md §5) ---------------------
    # Every knob of the two hand-drawn bands: persist, rebuild the skin,
    # and the render side re-renders both plates ONCE under the new cache
    # key.
    "numeral_outer_size",
    "minutes_size",
    "numeral_outer_ring_size",
    "numeral_face",
    "minutes_face",
    "numeral_seating",
    "numeral_relief",
    "numeral_depth",
    "numeral_light",
    "numeral_darkness",
    "numeral_contact_blur",
    "numeral_border",
    "crown_time_format",
    # THE WORLD MODE (ring_rework.md §1) rides the same path: persist,
    # rebuild the skin, and the fresh compositor snaps to the phase on
    # its first paint.
    "world_mode",
    # ... and so does WHAT THE ROTATION CARRIES (owner ballot verdict
    # 2026-08-13): the band plate's cache key carries the occluded seats,
    # so a fresh skin is all it takes to recompose the whole outer band.
    "world_rotation_scope",
    # --- Crown Text (R-24/Phase-6-debt correction, owner 2026-08-05: the
    # outer Great Seal crown text arc's own controls) --------------------
    "ring_tint_inner",
    "crown_text_alpha",
    "crown_text_scale",
    "crown_text_tint",
    "metal_shade_gold",
    "metal_shade_bronze",
    "metal_shade_silver",
    # --- Opacity (Phase 4, R-15/R-35/R-36 + the moved rows) -------------
    "star_alpha",
    "aura_day_alpha",
    "aura_twilight_alpha",
    "moon_hidden_alpha",
    "umbra_alpha",
    "moon_transit_alpha",
    "ghost_alpha",
)
