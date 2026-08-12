# Language & System Section — Flow

**About:** [description](../__about/language_system_section.md)

## Layout

📦 **Language** (`QGroupBox`, `QHBoxLayout`)
  🔽 Language combo (originals on top, separator, machine-translated
     languages below, alphabetical)
  🔘 "Default" button (jumps the combo to English)
  🏷️ note label

📦 **Calendar eras** (`QGroupBox`, `QFormLayout`)
  🔽 Era labels combo (BCE/CE vs BC/AD)
  ☑️ "Write the era after positive years too (2026 CE)" checkbox
  🔽 Third calendar combo (None / AUC / Byzantine A.M. / Hebrew A.M. /
     Anno Hegirae / Huangdi / Maya Long Count — epoch fine print as
     per-item tooltips)
  🏷️ note label

📦 **System** (`QGroupBox`, `QFormLayout`)
  ☑️ "Start with Windows" checkbox (reads the live HKCU Run state)
  🔽 Visibility combo (below all windows / normal window / always on top)

## Behaviour (pseudocode)

    autostart_selected() -> bool:
        RETURN the current checkbox state
        # read by the Watch Controller AFTER exec() — NOT folded into
        # result_settings(); it drives a registry write, not a persisted
        # Settings field
