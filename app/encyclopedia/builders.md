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
