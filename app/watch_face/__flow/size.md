# Size Section — Flow

**About:** [description](../__about/size.md)

## Layout

🔘 5 diameter preset buttons (`dial.SIZE_PRESETS`)
🎚️ diameter slider (synced two-way with) 🔢 diameter spinbox, + Default
🎚️ Earth scale slider, + Default
🎚️ Moon scale slider, + Default
🎚️ Complications scale slider (`slot_scale`), + Default
🎚️ Indices scale slider (`ring_letter_scale`), + Default
🎚️ Hover enlarge slider, + Default

## Behaviour (pseudocode)

    ON diameter slider release OR spinbox editingFinished:
        setters["diameter"](value)

    ON a preset button click:
        setters["diameter"](preset)

    ON a scale slider release:
        setters[key](slider.value() / 100)

    ON a scale "Default" click:
        slider.setValue(default); setters[key](default / 100)   # live-apply,
        # unlike the Settings dialog's transactional Default
