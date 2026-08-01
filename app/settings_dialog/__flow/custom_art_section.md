# Custom Art Section — Flow

**About:** [description](../__about/custom_art_section.md)

## Layout

📦 **Custom ring** (`QGroupBox`)
  🔽 Layout combo (Flame / Chalice / Seal)
  ✏️ Unique name field
  🔘 "Add ring" button
  🔽 Thematic color combo (Auto / any metal or theme-color ramp)
  🔤 per-position letter combo row (rebuilt on layout change — grouped
     Latin / Greek / Numbers / Symbols; Numbers capped to the position's
     own hour)
  🏷️ status label ("N custom ring(s) saved")

📦 **Custom hands** (`QGroupBox`)
  🏷️ note (PNGs pointing UP; tip-to-pivot length sets size)
  per hand (hours / minutes / seconds):
    🔘 "Browse…" button (file picker)
    🔢 Pivot X spinbox (-1 shown as "center")
    🔢 Pivot Y spinbox
  🔽 Z-order combo (bottom → top permutations)
  ✏️ Unique name field
  🔘 "Add hands" button
  🏷️ status label ("N hand set(s) saved")

## Behaviour (pseudocode)

    ON ring layout changed:
        clear the slot row
        FOR EACH position in the chosen layout:
            add a grouped letter combo (its Numbers section limited to
            THIS position's own hour)

    ON "Add ring":
        build a candidate card {name, positions, letters, thematic?}
        validate it (data.rings.validate_preset)
        IF invalid (duplicate name, bad glyphs): show the error in the
            status label, stop
        append the card to the working custom_rings list; clear the name field

    ON "Add hands":
        require: a unique name AND all three PNGs picked
        IF missing: status ← "Unique name"; stop
        create the pack folder under the user hands directory
        copy the three PNGs into it
        write hands.json {pivot per hand, z_order}
        clear the name field
