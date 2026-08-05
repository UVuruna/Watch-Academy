# Pointer Section — Flow

**About:** [description](../__about/pointer.md)

## Layout

📦 Pointer gallery — one tile per `POINTER_DIAL_COUNTS` entry, ascending
   by arm count, icon = `thumbs.pointer_swatch_icon`
🔘 palette-style pills (2 or 3, `palette_styles_for(pointer)`)
IF pointer != "aurora":
  🔘 shape pills (Star / Polygon)
  IF pointer IN POLYGON_POINTERS AND shape == "polygon":
    🎚️ Curvature slider + 🔘 edge pills (Smooth concave / V-notched)
☑️ "Hide night borders" (enabled only if `daylight_active(settings)`)
☑️ "Daylight - Night" (R-05; enabled only if pointer IN DAYLIGHT_SWITCH_POINTERS)
📦 Earth group (R-06):
  🖼️ Clean / Atmosphere tiles
  🔘 Date / Weekday / Date & Weekday / Full Date pills (enabled only
     when diameter >= FULL_TEXT_MIN_DIAMETER)

## Behaviour (pseudocode)

    ON a gallery tile click:
        setters["pointer"](variant)

    ON a shape pill click:
        setters["pointer_shape"](shape)

    ON the curvature slider release:
        setters["polygon_curvature"](slider.value() / 100)

    ON the Daylight - Night checkbox toggle:
        setters["daylight"](checked)          # SAME key the old Settings
                                               # Archetype group writes
