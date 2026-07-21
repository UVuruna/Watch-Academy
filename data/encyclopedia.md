# Encyclopedia Repository

**Script:** [Encyclopedia Repository (script)](encyclopedia.py)

## Purpose

Loads `Database/encyclopedia.json` — the Encyclopedia's OWN content
(owner expansion 2026-07-13), separate from the dial articles in
`symbolism.json`: the INSTRUMENT articles (how and why the clock is
built the way it is — the dial, solar rotation, twilight, the year
wheel, lunations, Paint/Light, metals, the ring letters), the WEEK
pages (seven cross-theme day portraits — everything a day owns woven
into one prose page), the SEASONS articles, the VIRTUES / SINS /
MOODS entries (one short article per cross-cure emblem, 8 per family,
Sunday counted twice), the DUALITY family (owner 2026-07-13: "The
Two Triangles" — Lucifer, Judas and The Union, the scale of self
whose zero no individual reaches) and, since round R3, every weekday
theme's own THEME_TITLE opening page and WEEK_DUALITY title page (the
ARTICLE ORDER restructure — see [Encyclopedia Dialog](../app/encyclopedia.md)).

Every text rides the same translation overlay as the articles
(`encyclopedia/<section>/<key>/base|title` keys), so the bundled
Serbian and any machine-translated language apply automatically.

## Connections

### Uses
- [Database (folder)](../Database/___database.md) — `encyclopedia.json`
- [Translations](translations.md) — the corpus walk covers these keys

### Used by
- [Encyclopedia Dialog](../app/encyclopedia.md) — the browser UI

## Classes

### EncyclopediaRepository

#### Methods
- `instrument(key)`: `{title, base}` of one functionality article
- `week(body)`: `{title, base}` of one weekday page (body = sun..saturn)
- `season(key)` / `sun(key)` / `moon(key)`: `{title, base}` of one
  SEASONS / SUN / MOON article (the three-way split, ROADMAP queue #10)
- `era(key)`: `{title, base}` of one ERA article — the two Ages, the
  four Starry Seasons, the comparative "Eras of the World" and (fix
  round F, owner "bravo") **The Great Oscillations** — the season-length
  / Milankovitch essay near the Observatory
- `eclipse(key)`: `{title, base}` of one ECLIPSE chapter (fix round F,
  owner order 2026-07-19) — the two per-body overviews plus the seven
  categories (solar total/annular/partial/hybrid, lunar total/partial/
  penumbral), all in the `eclipse` section
- `entry(family, name)`: `{base}` of one virtues/sins/moods/duality/
  ninths/intelligence/wider/months article (the WIDER family holds the
  seatless A-list pantheon figures — WORKPLAN Session 8; the MONTHS
  family holds the Slavic-months Calendar-pointer set — owner-sealed
  R7b 2026-07-21)
- `theme_title(theme)` / `week_duality(theme)`: `{title, base}` of a
  weekday theme's OWN opening page / its WEEK-DUALITY title page
  (round R3 ARTICLE ORDER restructure — `theme_title`/`week_duality`
  sections, one entry per `WEEKDAY_THEME_TITLES` key except virtues/
  sins/moods, which the emblem-family pass keeps out of the weekday
  shape entirely). Round R3b (item 2, the PANTHEON/PLANETARY MERGE)
  adds FOUR more keys — `greek_pantheon`/`norse_pantheon`/
  `egypt_pantheon`/`slavic_pantheon` — the Pantheon block's own title
  and week-duality pages, argued from the culture's OWN throne-room
  rank rather than the day-ruler canon; `app.encyclopedia._pantheon_
  topic` reads them the same way, `f"{theme}_pantheon"` as the key.
