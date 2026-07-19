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
Sunday counted twice) and the DUALITY family (owner 2026-07-13: "The
Two Triangles" — Lucifer, Judas and The Union, the scale of self
whose zero no individual reaches).

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
  ninths/intelligence/wider article (the WIDER family holds the
  seatless A-list pantheon figures — WORKPLAN Session 8)
