# Topic Builders

**Script:** [Topic Builders (script)](builders.py)

## Purpose
Turn a theme key into (icon, entries): the weekday skeleton every theme
shares, the pantheon and wider-court blocks the four god themes add, the
Continents topic's own custom build, and the Guide topic.

Moved VERBATIM from the retired single module — the Session 27 reform
changed how topics are grouped and read, never how a page is built.

## Connections

### Uses
- [Static Pages](pages.md) — the tables it walks
- [Defaults](../../config/defaults.md) — every art path helper
- [Continents](../../core/continents.md) — the living Ninth

### Used by
- [Topic Tree](tree.md)

## The weekday skeleton

```
0     the theme's own title page
1..6  Monday..Saturday          (owner: "Uvek... Ponedeljak PRVI")
7     the week-duality title
8     the Ruler half of Sunday
9     the Servant half
10    the Ninth                 (outside the week - CANON.md)
```

## The Guide
Built from `assets/instrument/guide/pages.json` + `captions.json` — one
guide PAGE becomes one entry, each caption a `[[Title]] body` block the
reader already draws as a centered heading (Rule #5: the help book's
content is read where it lives, never copied).

## THE DOUBLE NINTH LAW's Encyclopedia side (owner decree 2026-07-29)
Two additions read `constants.NINTH_MECHANISMS` so the Encyclopedia
shows only the ACTIVE face of a double ninth, never both:

- `_live_ninth_face(theme, name, plate, is_daylight, travel_date)` —
  the shared ninths-loop's own dispatch (called from
  [Topic Tree](tree.md)): "daynight" swaps to
  `constants.WEEKDAY_THEME_NINTH_NIGHT`'s face when `is_daylight` is
  False (sw_dyad); "term_weekly" rotates the SAME canonical plate
  through its seat roster by the traveled date's ISO week
  (`defaults.rotating_art_file`'s cadence override, cp_corpo); every
  other mechanism keeps the plate untouched.
- `_weekday_topic(theme, travel_date=None)` / `_theme_dual_art(theme,
  colored=False, on_date=None)` — the GOOD/EVIL (Sunday) pages thread
  `travel_date` through ONLY for a "term_weekly" theme (`mandate_date`
  local var); every other theme ignores it, so this touches cp_corpo
  alone. `looks_for`'s metal branch resolves its "Colored" sibling via
  `weekday_theme_body_art(..., colored=True)` instead of a hand-rolled
  path, so the bronze base and its colored twin always agree on which
  roster half is showing.

`continents` needs neither addition — its OWN custom `_continents_
topic` already derives Pangea/Zealandia from `travel_date` directly
(mechanism "easter_egg", pre-dating this law).
