# Hands & Bodies Section — Flow

**About:** [description](../__about/bodies.md)

## Layout

📦 **Hands** — one LARGE tile per `hand_packs()` entry, icon =
   `thumbs.art_thumbnail(pack["files"]["hours"])`

📦 **Earth**
  🖼️ Clean / Atmosphere tiles
  🔘 Date / Weekday / Date & Weekday / Full Date pills (enabled only
     when diameter >= FULL_TEXT_MIN_DIAMETER)
  ☑️ "Position pointer"
  🖼️ Pointer-shape gallery (Triangle / Chevron / Gem), enabled only
     while "Position pointer" is checked

📦 **Moon**
  🖼️ Unlit-half gallery (Cut+rim / Cut+ghost / Solid), icon =
     `thumbs.moon_dark_style_icon`
  🖼️ Crossing gallery (Lane split / Occultation / Shrink & pass), icon =
     `thumbs.moon_transit_style_icon`
  🖼️ Moon Horizon Band mode gallery (Horizon / Dim only / Always full)
  IF mode == "horizon":
    🖼️ Moon Horizon Band style gallery (Inverted / Silver thread /
       Ticks / Glow)

📦 **Eclipses**
  🖼️ Solar gallery (Bite / Magnitude arc / Halo)
  🖼️ Lunar gallery (Umbra sweep / Horizon band / Halo)

📦 **Stations**
  🖼️ Moon stations gallery (Arc grammar / Inner glow / Uniform)
  🖼️ Sun stations gallery (Arc grammar / Seasonal / Day-night wedge / Gold)

## Behaviour (pseudocode)

    ON a Hands tile click:
        setters["hands"](name)

    ON an Earth style/label tile or the Position-pointer checkbox:
        setters["earth_style"|"earth_label"|"show_marker_pointer"](value)

    ON a pointer-shape tile click:
        setters["marker_pointer_shape"](shape)

    ON a Moon/Eclipse/Station tile click:
        setters[<the menu's Settings key from constants.MOVING_BODY_MENUS>](value)

    ON a Moon Horizon Band tile click:
        setters["moon_band_mode"|"moon_band_style"](value)
