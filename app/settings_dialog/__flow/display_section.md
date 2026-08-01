# Display Section — Flow

**About:** [description](../__about/display_section.md)

## Layout

📦 **Opacity** (`QGroupBox`, `QFormLayout`)
  🎚️ Star slider (0–100%) + % label + "Skin default" reset
  🎚️ Aura — sunlight slider + % label + reset
  🎚️ Aura — twilight slider + % label + reset (disabled when pointer == "aurora")
  🎚️ Moon — below horizon slider (plain 0–100%, default 50%) + reset

📦 **Element sizes** (`QGroupBox`, `QFormLayout`)
  🎚️ Earth scale slider (50–200%, default 100%) + reset
  🎚️ Moon scale slider + reset
  🎚️ Slot scale slider + reset
  🎚️ Ring letters scale slider + reset
  🎚️ Hover enlarge slider (100–200%, default 120%) + reset
  🎚️↔️🔢 Diameter slider (360–1440 px) + label + spinbox (two-way synced) + reset

📦 **Archetype** (`QGroupBox`, `QFormLayout`)
  ☑️ Archetype names
  ☑️ Cube look (Court / Genesis / Council)
  ☑️ Daylight - Night

## Behaviour (pseudocode)

    _slider_row(value, default, which):
        build a slider + "%" label + "Skin default" button
        ON slider moved: update the label; mark self._{which}_override = True
        ON reset clicked: slider ← default; mark self._{which}_override = False
        RETURN slider, row

    Diameter two-way sync (signal-guarded to avoid feedback loops):
        ON slider changed(v):
            IF spin.value() != v → set spin (signals blocked) to v
        ON spin changed(v):
            IF slider.value() != v → set slider (signals blocked) to v
