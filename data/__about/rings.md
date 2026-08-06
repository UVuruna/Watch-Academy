# Ring Presets

**Script:** [Ring Presets (script)](../rings.py) ·
**Flow:** [diagram](../__flow/rings.md)

## Purpose

Loads the ring preset "cards" — bundled ones from
`Database/ring_presets.json` plus the user's CUSTOM cards from
settings. THE COMPOSITIONAL RING MODEL (owner decree 2026-08-05): one
card = one dial styling, `{name, outer, letters}`, plus the optional
fields below. `outer` names a `constants.RING_OUTERS` entry directly —
the outer band whose empty hour fields the letters stand in; the
INNER band and any CROWN TEXT are Settings-level choices
(`app.settings_store.Settings.ring_inner`/`custom_ring_crown_text`),
not card fields. Each of the SIX bundled presets is LOCKED to exactly
one outer (`constants.RING_OUTER_LOCK` — DOMY/LOOP/Dollar/Templar/The
One plus CHI, ring_rework's own sixth preset, added 2026-08-06 on
`"full"`) — a custom ring may pick any outer freely. Validation is loud
(Rule #1): an unknown outer, an unknown glyph, a count mismatch or a
duplicate name raises naming the offending card.

### Optional card fields (all validated by `validate_preset`)

- **`thematic`** — the card's own color under the Thematic ring finish;
  must be one of `constants.METAL_SHADE_NAMES["thematic"]` (CHI's own
  is `"ceramic"`, the ring-rework round's new porcelain ramp).
- **`triangle`** — a 3-position override of the `"hexa"` outer's own
  metal triangle (splits a 6-letter preset into two 3-letter metal
  groups); only valid when the card's own outer is `"hexa"`.
- **`legend`** — `position → {name, reading}`, the per-letter hover
  legend text. Since the 2026-08-05 decree every bundled card carries
  one (The One's eight hour-stations, Templar's four watches — CANON.md
  §THE HOUR RING / §THE TEMPLAR RING); every bundled reading now closes
  with its own alphabet-ordinal line (ring_rework §3, owner ruling
  2026-08-06, research/crown_content.md §2).
- **`crown_text`** — a list of crown-text entries; see
  [flow](../__flow/rings.md) for the three mutually exclusive forms
  (pinned / centered / free-form crown text) and their angle-solving.
  Each entry may also carry an optional `reading` {title, text} — THE
  ONE TERM ONE HOVER LAW (ring_rework §3, owner ruling 2026-08-06):
  when present, `render.compositor._ring_word_legend_tooltip` shows
  THIS for every word of the entry instead of falling back to the
  seat's own letter legend (fixes the reported bug where ANNUIT
  COEPTIS's hover narrated the Anointed Aegis letter under it instead
  of the Latin motto itself).
- **`about`** — theme-and-name marketing copy for the Settings preset
  picker (ring_rework §5, owner ruling 2026-08-06), never a seat
  listing; optional (a custom ring need not carry one). All six bundled
  cards ship it verbatim from research/crown_content.md §5.

## Connections

### Uses
- [Config (folder)](../../config/___config.md) —
  `constants.RING_OUTERS`, `constants.RING_OUTER_LOCK`,
  `constants.RING_LETTER_FILES`, `constants.METAL_SHADE_NAMES`,
  `paths.database_dir()`
- [Crown Text](../../core/__about/crown_text.md) — `crown_glyph_angles`,
  `centered_word_angles`, `free_arc_angles`, `_occurrence_index` — the
  per-glyph angle solve for the optional `crown_text` field

### Used by
- [Watch Controller](../../app/__about/controller.md) — `build_skin` resolves
  the active preset
- [Settings Store](../../app/__about/settings_store.md) — imports
  `ring_presets` to fold a stored ring name
- [Settings Ring](../../app/__about/settings_ring.md) — imports
  `validate_preset` to check a stored custom card
- [Watch Face — Ring section](../../app/watch_face/__about/ring.md) — lists
  loaded preset names
- [Custom Art Section](../../app/settings_dialog/__about/custom_art_section.md)
  — `validate_preset` checks the custom-ring builder's input

## Functions

- `ring_presets(custom=())`: `name → validated card` for every bundled
  + custom preset (`{name, positions, letters, outer, triangle,
  legend, crown_text, thematic, about}`); a duplicated name raises.
- `validate_preset(entry)`: the shared card validator — see
  [flow](../__flow/rings.md).
- `_validate_crown_text(name, raw, positions)` (private): the `crown_text`
  field's own validator and angle solver.

### _bundled_presets()
The bundled presets, parsed and validated ONCE per process (owner bug
2026-08-06). `ring_presets(custom)` sits on the skin-install path, so
every settings change on every watch re-read and re-validated the whole
file. The bundled entries are identical for every watch; the CUSTOM list
and the pick are per-watch, and the custom entries are still validated
fresh on every call.
