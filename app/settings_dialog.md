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
- **Palette** — one BIG color circle per hue of the ACTIVE (pointer,
  style) preset (owner spec 2026-07-11: Paint-style swatches);
  hovering a circle names the arm position it colors (Top / Bottom
  Left — the Compass speaks compass: North-East…, from
  `constants.POINTER_ARM_LABELS`); clicking opens QColorDialog. Edited
  palettes are saved as the user's custom preset for that combination
  ("Reset" returns to the owner preset).
- **Element sizes** (owner EXTRAS) — five multiplier sliders (Earth,
  Moon, Weekday, Octa slot, Ring letters; 50–200%, default 100%) plus
  the shared Hover enlarge slider (100–200%, default 120% — the
  element under the cursor grows by it; 100% disables the effect).
- **Ring tint** — one hue for the whole clock body (ring art, hands,
  Umbra; the letter art stays untouched): TWO labeled Paint-style
  grids from `defaults.RING_TINT_GROUPS` (owner 2026-07-15: the flat
  palette read too light) — **Lighter** (the gold palette, silvers and
  pastels) and **Darker** (the deep ring variants plus the fashion
  darks: Navy/teget, Oxford Blue, Petrol, Gunmetal, Graphite, Iron,
  Pewter, Dark Olive, Aubergine, Bordeaux — subtle wardrobe hues,
  owner-tunable; names live in the tooltips, the active swatch wears
  a white ring, "Gray" = the untouched art) plus a free QColorDialog
  picker.
- **Custom ring** — the ring card builder: a layout (Flame /
  Chalice / Seal), a library letter per position and a unique name;
  the per-position dropdown is GROUPED (owner spec 2026-07-11) into
  Latin (the full A–Z), Greek, Numbers (1–10, 20 — growing) and
  Symbols sections with unselectable headers
  (`constants.RING_LETTER_GROUPS`). Add validates the card and OK
  persists it (it appears under Theme ▸ Ring).
- **Language** — all provider languages; the first pick translates
  the whole corpus in the background and caches it. The Default
  button jumps back to English (the shipped originals).

OK applies and persists everything; Cancel discards. The dialog loads
the location tree on open and releases it on close (the repository's
documented lifecycle). All chrome strings resolve through the
[UI Text Catalog](../config/ui_text.md) (translation Phase 2) — the
controller passes the active overlay.

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
- `__init__(settings, skin)`: builds the four groups prefilled from
  the current settings (combos restored from the stored city path)
- `result_settings() -> Settings`: the edited values as a new frozen
  Settings (valid only after Accepted)
