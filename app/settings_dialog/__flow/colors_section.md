# Colors Section — Flow

**About:** [description](../__about/colors_section.md)

## Layout

📦 **Saturation** (`QGroupBox`, `QFormLayout`)
  🎚️ Aura slider (0–100%, default 100%) + % label + "Default" reset
  🎚️ Ring slider (0–100%, default 100%) + % label + "Default" reset

📦 **Palette — {pointer} {style}** (`QGroupBox`)
  🎨 one round color chip per hue of the active preset (click → `QColorDialog`)
  🔘 "Reset to preset" button

📦 **Clock tint — dial, hands and Umbra (letters excluded)** (`QGroupBox`)
  🏷️ "Lighter" label + grid of round tint chips
  🏷️ "Darker" label + grid of round tint chips
  🔘 "Custom…" button (`QColorDialog`) + active-tint label

## Behaviour (pseudocode)

    ON palette chip clicked(i):
        color = QColorDialog.getColor(current hues[i])
        IF accepted: hues[i] = color; repaint the chip + its tooltip

    ON "Reset to preset":
        hues = the preset's original hues; repaint every chip

    ON a tint chip / "Custom…" clicked:
        ring_tint = the preset's hue, OR a picked custom hue, OR None
        relabel: preset name + hex / bare hex if custom / "Gray (default)" if None
        repaint every swatch — the one matching ring_tint gets a white
        selection ring
