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
- `season(key)`: `{title, base}` of one SEASONS article
- `entry(family, name)`: `{base}` of one virtues/sins/moods/duality/
  ninths/intelligence/wider article (the WIDER family holds the
  seatless A-list pantheon figures — WORKPLAN Session 8)
