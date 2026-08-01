# Taxonomy

**Script:** [Taxonomy (script)](../taxonomy.py) · **Flow:** [diagram](../__flow/taxonomy.md)

## Purpose

The ONE hierarchy (RESTRUCTURE.md, owner-sealed 2026-07-22): five
categories → groups → themes. The Encyclopedia halls, the Settings
panels and the `assets/` tree all mirror THIS module — halls/groups are
edited here, in one table, and read everywhere else.

Layer: config — pure, no Qt, no wall clock.

## Contents

- `CATEGORIES` — the five root category keys (`calendars`, `weeks`,
  `archetypes`, `celestial`, `instrument`) → display names.
- `WEEK_GROUPS` — the `weeks` category's own groups: group key →
  (display name, ordered theme-folder tuple). Eight groups
  (`celestial_bodies`, `myth`, `faith`, `crafts`, `societies`,
  `inner_wheel`, `gaming`, `films`) covering every weekday theme
  folder.
- `THEME_TO_GROUP` — derived reverse of `WEEK_GROUPS`: theme folder
  name → its group. Used by `weeks_dir` to place theme-relative art.
- `THEME_KEY_RENAMES` — old settings/code theme KEY → new key, applied
  by `app.settings_store` on load (an external-user-data migration,
  not a Rule #6 compatibility shim).
- `THEME_FOLDER` — code theme KEY → on-disk FOLDER name, where the two
  differ because several register-topics share one folder (e.g.
  `ancient_religions` and `bible_ii` both fold into their primary
  theme's folder; `virtues`/`sins`/`moods`/`intelligences` fold to
  their singular Inner Wheel folders).
- `theme_folder(theme)`, `weeks_root()`, `weeks_dir(theme_folder_name)`,
  `inner_wheel_dir()` — the resolvers every art/settings consumer calls
  through.

## Connections

### Uses
- [Config (folder)](../___config.md) — `paths.assets_dir()`

### Used by
- [Pantheon](pantheon.md) — `weekday_art()` and `theme_title_art()`
  resolve a theme's group folder through `weeks_dir`
- [Encyclopedia Tree](encyclopedia_tree.md) — mirrors this hierarchy on
  the reading side (the `weeks` category's groups become Encyclopedia
  whole/theme seating, independently curated but describing the same
  themes)
- [App (folder)](../../app/___app.md) — the Weekday submenu groups,
  Settings validation

## Design Decisions

- **One hierarchy, read everywhere.** Before this module the
  Encyclopedia halls, the Settings menu groups and the `assets/` tree
  each kept their own idea of "which themes belong together"; a themes
  addition needed three edits to stay consistent. `WEEK_GROUPS` is now
  the single edit.
- **`weeks_dir` raises on an unknown folder.** A typo in a theme-folder
  name fails loudly at the call site rather than resolving to a ghost
  path nothing ever populates (Rule #1).
- **Renames are a migration table, not a permanent alias.** Rule #6 (no
  backward-compatibility wrappers) does not apply here — `THEME_KEY_
  RENAMES` translates STORED USER DATA (an old settings file), never a
  live code path; a rename is deleted from the table once no shipped
  version could still hold the old key.

## Known doc drift

`taxonomy.py`'s own docstring says "Documentation: config/taxonomy.md"
— that file never existed in this repository at any point this
migration could find. It is a stale forward-reference the module
carried since it was written; this migration is what finally gives the
module real documentation, at its new address
(`__about/taxonomy.md` / `__flow/taxonomy.md`), so the docstring's
claim is now true in spirit if not in the literal path it names.
