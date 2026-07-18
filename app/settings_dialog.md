# Settings Dialog

**Script:** [Settings Dialog (script)](settings_dialog.py)

## Purpose
The M6 settings window (menu "Settings…") for everything the tray
submenus cannot express.

### Layout — the navigation rework (owner ROADMAP 15h item 1, 2026-07-18)
The dialog used to be one long scroll of group boxes. It is now a
`QListWidget` NAVIGATION COLUMN on the left (each row a section title
with a trailing right arrow "▸") plus a `QStackedWidget` on the right —
clicking a title shows THAT section's panel; `self._nav_list.
currentRowChanged` drives `self._stack.setCurrentIndex`. Every existing
control still exists — none dropped, `result_settings()` untouched —
just filed under one of SEVEN sections (`__init__` builds each as a
`(title, [group_boxes])` pair; related groups SHARE one title exactly
where the owner's own example applies — Palette + Clock tint = Colors):

| Section | Groups |
|---|---|
| Location | Location, Quick Jump cities |
| Display | Opacity, Element sizes |
| Colors | Palette, Clock (ring) tint |
| Custom art | Custom ring, Custom hands |
| Themes | Theme rotation, Artwork |
| Language | Language, Calendar eras |
| System | System (autostart + Visibility Z mode) |

Each panel is wrapped in its OWN `QScrollArea` (`panel_scroll`,
`setWidgetResizable(True)`) — the scroll cap that used to sit around
the WHOLE dialog now sits around each panel individually, since only
one panel is visible at a time; a tall panel still scrolls internally.
The dialog's own size is `max(sizeHint)` over every panel's inner
content widget (not the wrapping scroll area) plus the nav column's
fixed width (`defaults.SETTINGS_NAV_WIDTH_PX`), capped to the screen
like before.

### The groups

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
  element under the cursor grows by it; 100% disables the effect) and
  the custom DIAMETER control (owner 2026-07-17 ROADMAP 15e, exact
  spinbox added 2026-07-18 ROADMAP 15h item 12b): a slider spanning the
  smallest to the largest menu preset (360…1440, the fixed Size presets
  stay in the menu) PLUS a `QSpinBox` (`self._diameter_spin`, same
  range) synced TWO-WAY with it — either widget moving drags the other
  along (`sync_spin`/`sync_slider`, each guarded with `blockSignals` to
  avoid feedback) — applied together on OK exactly like a menu preset
  pick.
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
- **Quick Jump cities** (Session 16, owner slika 12) — the user's own
  places for Quick Jump ▸ Location: a search box over the SAME
  45k-city machinery as the home picker (`fold_name` matching, the
  same results-list pattern) whose pick ADDS to the jump list instead
  of touching the home combos (navigating the home picker to add a
  jump city would silently change home on OK — the deliberate design
  reason for the separate box), plus the current list and a Remove
  button. Each saved city jumps the OBSERVER there; the moment stays.
- **Custom hands** (owner spec 2026-07-12) — the hand-pack builder:
  three PNGs pointing UP, a pivot per hand and a bottom-up z-order; Add
  writes the pack folder immediately (files, not settings) — it appears
  under Design ▸ Hands.
- **Theme rotation** (owner spec 2026-07-12) — cycle the CHECKED
  weekday themes on a timer (None / one kinship group / Custom
  checkbox grid), plus the per-theme METAL each bronze-plate theme
  wears (or "Follow ring color").
- **Artwork** (owner 2026-07-14) — the ART SOURCE pick (Gemini vs
  ChatGPT generations): one combo switches every plate, emblem and
  badge; files missing in the chosen source fall back to the other.
- **Language** — all provider languages; the first pick translates
  the whole corpus in the background and caches it. The Default
  button jumps back to English (the shipped originals).
- **Calendar eras** (Session 16, owner amendment 2026-07-17; placed
  under Language — the documented call) — the year-line choices: the
  official era labels (BCE/CE default vs BC/AD), the "write the era
  after positive years too" opt-in (default off — the world writes
  "2026" bare), and the optional THIRD calendar combo
  (None/AUC/Byzantine A.M./Hebrew A.M./Anno Hegirae — the epoch fine
  print lives in the combo tooltips only). Anno Lucis is NOT an
  option: it always accompanies the official year.
- **System** — Start with Windows (the HKCU Run entry) plus the
  VISIBILITY Z mode combo (owner 2026-07-17, ROADMAP 15e): the THREE
  modes — below all windows (the desktop layer, default), a normal window
  (above only while focused), or always on top; the controller swaps the
  window flags on OK via `ClockWidget.set_z_mode` (which re-asserts native
  topmost for "top").

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
- `__init__(settings, skin)`: builds the seven sections (see the layout
  map above) prefilled from the current settings (combos restored from
  the stored city path), wires `self._nav_list`/`self._stack` and sizes
  the dialog from the widest/tallest panel's inner content
- `result_settings() -> Settings`: the edited values as a new frozen
  Settings (valid only after Accepted)
