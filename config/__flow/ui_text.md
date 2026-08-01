# UI Text Catalog — Flow

**About:** [description](../__about/ui_text.md)

## Shape

```
UI_STRINGS: tuple[str, ...]      # ~450 flat entries, grouped by comment banner only
  ├─ Menu                         ("Design", "Hands", "Pointer", ...)
  ├─ Settings dialog               ("Location", "Opacity", "Diameter", ...)
  ├─ Time Travel / Guide           ("Moment:", "Quick Jump", "Eclipse", ...)
  ├─ Tray balloons / error boxes   ("Translating", "Settings could not be saved", ...)
  ├─ Hover legend labels           ("Sunrise", "Sunset", "Angle", ...)
  ├─ Name tables                   weekdays, months, moon phases, zodiac,
  │                                 Chinese animals, elements, entity names
  └─ Observatory chart chrome      ("Season durations", "Anno Lucis", ...)
```

## Lookup

```mermaid
flowchart LR
    A["ui(overlay, text)"] --> B["key = 'ui/' + text"]
    B --> C{"key in overlay?"}
    C -- yes --> D[return overlay's translated string\n{}-placeholders intact]
    C -- no --> E[return text unchanged\n— English is the fallback source]
```

## Corpus build (data.translations, not this module)

    collect_corpus():
        FOR EACH text IN UI_STRINGS:
            corpus["ui/" + text] <- text     # English seed, awaiting translation

`ui_text.py` itself performs no translation and touches no network or
disk — it only names the strings that need one, and reads back
whatever `overlay` (built elsewhere, per active language) supplies.
