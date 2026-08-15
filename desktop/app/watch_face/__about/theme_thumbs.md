# Theme Plate Previews

**Script:** [Theme plate previews (script)](../theme_thumbs.py)

## Purpose
The two Themes & Slots previews that are ASSEMBLED FROM PLATES ON DISK
rather than painted: the Subdial plate set card (its three metal plates
side by side) and the Artwork cards (one per art source, each carrying
that source's Sun plate AND its Sunday dual in the same image).

Split out of [Thumbnails](thumbs.md) on 2026-08-15, when the Artwork
rework carried that module past THE STRUCTURE LAW's threshold. The
boundary is RESPONSIBILITY, not the line count that forced the issue:
what stays in `thumbs.py` is COMPUTED — icons this app paints through
the render vocabulary (moon faces, eclipse plates, marker marks,
swatches) — and what lives here READS PLATES and composes them. The
single-plate case, `art_thumbnail`, stays in `thumbs.py` because the
computed side needs it too; this module borrows it rather than keeping
a second copy (Rule #5).

## Connections

### Uses
- [Thumbnails](thumbs.md) — `art_thumbnail`, `THUMB_SOURCE_PX` and the
  shared disk-cache location/version, so both halves of the service
  invalidate together
- [Raster Store](../../../render/__about/raster_store.md) —
  `source_prefix`/`atomic_save`, the same content-fingerprint cache
- [Config (folder)](../../../config/___config.md) —
  `pantheon.weekday_theme_body_art`, `pantheon.weekday_dual_rel`
  (the ONE roster→Sunday door, shared with the compositor),
  `paths.display`/`art_file`/`existing_art_file`,
  `constants.ART_SOURCES`
- [Asset Variants](../../../render/__about/asset_variants.md) —
  `subdial_plate_file`, so a derived plate is computed, never invented

### Used by
- [Themes & Slots](themes.md) — `theme_art_sources` (whether to print
  the Artwork group at all), `art_source_icon`, `subdial_set_icon`

## Functions

| Function | One line |
|---|---|
| `subdial_set_icon(set_name)` | one set's gold/bronze/silver plates in one tile; sets 1–4 read their files, the solo set derives its gold/bronze from its silver master |
| `theme_art_sources(theme)` | the sources this theme has genuinely DISTINCT plates for — `()` when there is nothing to choose |
| `art_source_icon(source, theme, roster)` | one card per source: the Sun plate plus, when the theme has one, the roster's Sunday dual beside it |
| `_sun_plate` / `_dual_plate` | the two plate lookups, each with the dial's own fallback/absence rule |

## Design Decisions

- **A choiceless row is not printed** (owner ballot verdict 8A, first
  real case his 2026-08-15 report on Planets Photo). `theme_art_sources`
  resolves the theme's Sun plate under every source through the app's
  OWN resolver and returns `()` when they all land on the same file —
  Planets carries one cast, so the picker was offering four ways to
  choose one picture. Absence, not grey: a row with nothing to offer is
  STRUCTURE, and grey-with-a-reason is reserved for an option that
  exists but cannot be taken right now. Measured, never a hand-kept
  list — 30 of the registered themes do have two casts.
- **One card per source, the dual inside it** (owner order 2026-08-15,
  "po principu SUBDIAL gde u jednoj slici ima prikazane sve 3 opcije").
  The picker used to add a second card per source for the dual — four
  cards keyed back to two settings. `subdial_set_icon` already had the
  grammar; `art_source_icon` composes the same way (equal slots, each
  plate centred, aspect kept).
- **The dual follows the ROSTER.** Planetary and Pantheon do not share
  a Sunday, and the preview used to ask nothing at all. The rule lives
  once, in `pantheon.weekday_dual_rel` — the pantheon plate wins only
  when it is on disk, otherwise the whole planetary pair stays (the
  classic unit's Sunday law) — and `render.compositor` was moved onto
  that same door in the same round rather than being left as a second
  copy.
