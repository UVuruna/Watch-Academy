# Settings Dialog

**Script:** [Settings Dialog (script)](settings_dialog.py)

## Purpose
The M6 settings window (menu "Settings…") for everything the tray
submenus cannot express:

- **Location** — cascading Continent → Subregion → Country → Region →
  City combos over the bundled 45,650-city database (mixed depth:
  countries may hold cities directly AND under admin regions — the
  Region combo offers "—" for the direct ones), a search box that jumps
  the combos to a found city, and lat/lng fine-tune spinboxes (the
  chosen city fills them; the user may nudge them to precise
  coordinates — the city's IANA timezone is kept).
- **Opacity** — three sliders (percent): Star (its twilight alpha
  scales proportionally with the day value), plus Aura sunlight and
  Aura twilight as two INDEPENDENT overrides (owner spec — no coupling
  ratio between them). "Skin default" resets a slider and clears its
  override.
- **Palette** — one color chip per hue of the ACTIVE (pointer, style)
  preset; clicking a chip opens QColorDialog. Edited palettes are saved
  as the user's custom preset for that combination ("Reset" returns to
  the owner preset).

OK applies and persists everything; Cancel discards. The dialog loads
the location tree on open and releases it on close (the repository's
documented lifecycle).

## Connections

### Uses
- [Locations](../data/locations.md) — the hierarchy and city records
- [Settings Store](settings_store.md) — reads/writes the chosen values
- [Config (folder)](../config/___config.md) — palette presets, ranges

### Used by
- [App Controller](controller.md) — opens it from the menu; applies the
  result (new observer/timezone → day-context rebuild, display
  overrides → skin reinstall)

## Classes

### SettingsDialog
- `__init__(settings, skin)`: builds the three groups prefilled from
  the current settings (combos restored from the stored city path)
- `result_settings() -> Settings`: the edited values as a new frozen
  Settings (valid only after Accepted)
