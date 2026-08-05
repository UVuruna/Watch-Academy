# Ring Section — Flow

**About:** [description](../__about/ring.md)

## Layout

📦 Preset gallery — one tile per `ring_presets(custom_rings)` entry,
   icon = `thumbs.art_thumbnail(RING_OUTER_ART_DIR / RING_OUTERS[outer]["file"])`,
   tooltip = "Locked outer: {outer}"
🔘 finish pills (gold / silver / bronze / thematic)
☑️ "Two metals" — only when the active card's outer carries a triangle
☑️ "Shine" — only when the active card seats the adaptive Eye glyph
📦 Inner gallery — one tile per `RING_INNERS` entry, icon =
   `thumbs.art_thumbnail(RING_INNER_ART_DIR / f"{inner}.png")`
📝 Crown text group — bundled preset: read-only joined motto text;
   custom ring: a text field + top/bottom orientation pills
🔘 "Custom ring…" button

## Behaviour (pseudocode)

    ON a preset tile click:
        setters["ring"](name)

    ON an inner tile click:
        setters["ring_inner"](inner_name)   # keyed by the active preset name

    ON the crown text field losing focus (custom ring only):
        setters["custom_ring_crown_text"](text)

    ON an orientation pill click (custom ring only):
        setters["custom_ring_crown_orientation"]("top" | "bottom")

    ON "Custom ring…" click:
        setters["open_custom_ring"]()   # opens the EXISTING SettingsDialog
                                        # navigated to "Custom art"
