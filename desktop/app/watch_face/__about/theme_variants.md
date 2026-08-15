# The Variant Panel

**Script:** [Theme variants (script)](../theme_variants.py)

## Purpose
Ballot verdicts **3A + 8A** (owner, 2026-08-15): one permanent panel
under the content tree carrying everything the active slot's theme can
wear — Style, Metal, Source, Roster — and printing only the rows that
theme can actually offer.

## Connections

### Uses
- [Theme Plate Previews](theme_thumbs.md) — `theme_style_icon` (the
  theme's Sun plate in each look) and `art_source_icon` (the composite
  the retired Artwork group drew), plus `theme_art_sources` to know
  whether a Source row exists at all
- [Controls](controls.md) — `picture_group` for the rows that pick a
  PICTURE
- [Widgets](widgets.md) — `flow_row`/`pill` for the rows that pick a word
- [Config (folder)](../../../config/___config.md) —
  `registry.week.WEEK` (kinship and `title_plate`),
  `constants.METAL_THEMES`/`theme_metals`/`FIGURE_ROSTERS`/
  `ART_SOURCE_TITLES`, `pantheon.WEEKDAY_PANTHEON`

### Used by
- [Themes & Slots](themes.md) — builds it directly under the content
  tree, in the seat the standalone Artwork group used to hold

## Design Decisions

- **Why it exists.** "Variant of a theme" was FOUR mechanisms that could
  not see each other: the Planets variants were separate registry keys
  (so the gallery showed one card and hid the relatives), the per-theme
  METAL was chosen in combo boxes buried inside Theme rotation and only
  for themes in the rotation, the art SOURCE was a group of its own, and
  the Pantheon/Planetary pair appeared and vanished for want of a
  permanent seat.
- **The defect this round exists for, measured not assumed:** of the 34
  registered themes, exactly two — `planet_signs` and `planets_art` —
  are reachable from NO picker group. `planets_art` does not even carry
  a title. The Style row is their first door. A tooth pins that set
  against the registry, so if the owner wires them into a menu group
  later the test says so rather than going quietly stale.
- **NO SETTINGS MIGRATION, deliberately.** A `ThemeSelection` that
  became a new stored shape would have to rewrite every existing
  profile — the one irreversible step in the whole programme. It is not
  needed: the coordinates already map onto keys the settings have always
  held, so this module is a VIEW over them. Picking a style writes the
  relative's own registry key, exactly what `weekday_theme` has always
  contained.
- **Kinship is DERIVED.** Two keys are relatives when they share an
  `articles` set (the same entities carry the same encyclopedia) and
  both declare a `title_plate` (the look they wear). Nothing is listed
  twice, so a family the owner grows in the registry appears here with
  no second edit.
- **It varies the ACTIVE SLOT's theme**, through that slot's own
  `SlotDescriptor.set_weekday` — never a global key. A watch may wear a
  different theme per slot, and a panel that wrote a global would
  silently retheme the wrong one.
- **VERDICT 8A, both halves.** A row with nothing to offer is NOT
  printed — that is structure, not state (Continents shows no panel at
  all: one style, no metals, no pantheon, one art cast on disk).
  An option that EXISTS but cannot be taken right now is greyed with its
  reason: the Metal row greys while "Follow ring color" drives it. Note
  that Virtues looked like a no-panel candidate and is not one — it
  carries two art casts, so it earns a Source row. That distinction is
  why the rule measures instead of listing.
- **Rows that pick a picture ARE pictures.** Style and Source are card
  groups (the owner's standing law: a picker shows what it picks);
  Metal and Roster are captioned pill rows, because a metal name and a
  roster name are words. Folding Artwork into this panel must not cost
  him the preview he asked for in the first place, so the Source row
  draws the same base-plus-Sunday-dual composite that group drew.
