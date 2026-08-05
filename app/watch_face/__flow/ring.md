# Ring Section — Flow

**About:** [description](../__about/ring.md)

## Layout

📦 Preset gallery — one tile per `ring_presets(custom_rings)` entry,
   icon = `thumbs.art_thumbnail(RING_FACE_DIR / face)`
🔘 finish pills (gold / silver / bronze / thematic)
☑️ "Two metals" — only when the active card's layout carries a triangle
☑️ "Shine" — only when the active card seats the adaptive Eye glyph
🔘 "Custom ring…" button

## Behaviour (pseudocode)

    ON a preset tile click:
        setters["ring"](name)

    ON "Custom ring…" click:
        setters["open_custom_ring"]()   # opens the EXISTING SettingsDialog
                                        # navigated to "Custom art"
