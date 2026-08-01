# Themes Section — Flow

**About:** [description](../__about/themes_section.md)

## Layout

📦 **Theme rotation** (`QGroupBox`)
  🔽 Group combo (None / one kinship family / Custom)
  ▦ checkbox grid — one box per weekday theme (visible only when group == Custom)
  ⏱️ "Every [N] [minutes/hours]" row (spinbox + unit combo)
  🔽 per-metal-theme combo row (each combo visible only while its theme is
     IN the current rotation selection)
  ☑️ "Follow ring color" checkbox (disables every metal combo when checked)

📦 **Artwork** (`QGroupBox`)
  🔽 Art source combo (Gemini / ChatGPT)

📦 **Subdial plate** (`QGroupBox`)
  🔽 Subdial set combo (Set 1 / 2 / 3 / 4 / Solo)

📦 **Metal shades** (`QGroupBox`, `QFormLayout`)
  🔽 Gold shade combo
  🔽 Bronze shade combo
  🔽 Silver shade combo

## Behaviour (pseudocode)

    _rotation_selection():
        IF group == "custom": RETURN the checked theme keys
        ELSE: RETURN the picked kinship group's fixed theme list

    ON rotation group changed / any checkbox toggled:
        show the checkbox grid only when group == "custom"
        FOR EACH metal-theme row:
            visible only if that theme ∈ _rotation_selection()
