# Themes & Slots Section — Flow

**About:** [description](../__about/themes.md)

## Layout

🔘 FACE LAYOUT row — Full face / 1 subdial / 2 subdials / 3 subdials
   (`slot_layout_target(settings)` marks the active pill)
🥇🥈🥉 SLOT PICKER row — one medal per `slot_descriptors()` entry,
   disabled when `descriptor.enabled_value` is False
☑️ "Names" (bound to the active descriptor's `names_value`/`set_names`)
📦 [Content Tree](theme_tree.md) — bound to the active descriptor;
   `full_face=True` when NO descriptor is enabled
🔘 Subdial plate pills — Theme background / Classic black
   (`settings.subdial_style`)
🎚️ Theme rotation — amount + unit spinbox/combo, ☑️ "Follow ring color"

## Behaviour (pseudocode)

    ON a FACE LAYOUT pill click:
        setters["slot_layout"](target)         # a REAL setter

    ON a medal button click:
        _active_slot = descriptor.index        # pure navigation
        rebuild in place

    active_descriptor = the descriptor at _active_slot IF its
        enabled_value is True, ELSE descriptor 1 (its data still
        pre-picks slot 1's content — see themes.md Design Decisions)
    full_face = TRUE when no descriptor.enabled_value is True

    ON the Names checkbox toggle:
        active_descriptor.set_names(checked)   # a REAL setter

    ON a subdial plate pill click:
        setters["subdial_style"](style)

    ON the rotation amount/unit change:
        setters["theme_rotation_minutes"](amount * unit_factor)

    ON the Follow ring color toggle:
        setters["theme_metal_follow_ring"](checked)

State (`_active_slot`, module-level — see themes.md Design Decisions):
which slot's medal is selected, surviving an unrelated live-apply pick
elsewhere in the window.
