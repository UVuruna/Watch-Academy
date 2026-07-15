# Omitted Figures — the Consolidated Roster Report

**Owner request (2026-07-15):** one report that says exactly WHAT each
theme omitted, WHY it was omitted, and HOW to fit the missing figures
in — folding in and correcting the Haiku research pass
(`MISSING_DEITIES.md`, `OMITTED_THEMES_ANALYSIS.md`, both superseded
by this file). The owner's own proposal, adopted below: **two
selectable rosters per theme — "most important figures" vs "best fit
for our seats" — so nothing ships out; new figures and texts ship in.**

---

## 1. Why anything was omitted at all — the one honest sentence

Every weekday theme maps exactly SEVEN figures onto the seven
CLASSICAL DAY-RULERS (Sun, Moon, Mars, Mercury, Jupiter, Venus,
Saturn — the planetary week the whole dial is built on). A figure won
its seat by matching a day-ruler's domain, not by cultural rank — so
top-tier figures with NO classical planet/day (Poseidon, Athena,
Horus, Hel…) lost to lesser figures that fit a seat perfectly
(Montu fits Mars; Horus does not). That is the entire story of every
omission below. Uranus/Neptune/Pluto fall out the same way: real
planets, but NO weekday — the planetary week has seven rulers.

## 2. Audit of the Haiku pass — keep, correct, discard

The research direction was right; the roster inventory was not
checked against our data. Corrections against
`Database/symbolism.json` and the live theme tables:

| Haiku claim | Reality |
|---|---|
| "Thoth — CONFIRMED MISSING" | **PRESENT** — Egyptian Wednesday (mercury seat) since the theme landed |
| "Ra — should have been included" | **PRESENT** — Egyptian Sunday |
| "Morana — MISSING" | **PRESENT** — Slavic Saturday |
| "Makosh — MISSING" | **PRESENT** — Mokoš, Slavic Friday |
| "Healer/Physician — MISSING" | **PRESENT** — Professions Monday is the Physician |
| "Farmer — MISSING as a theme" | **PRESENT** — Professions Saturday |
| "Hades — status unclear" | **SEATED as the Greek NINTH** (the excluded-one doctrine: the god who is not depicted keeps the empty ninth seat — he must NOT also join a seven-roster) |
| "Baldr — MISSING" | **SEATED as the Norse NINTH** (the dead god whose absence defines the myth) |
| Set, Crnobog "missing" | **SEATED as the Egyptian and Slavic NINTHS** |
| Eris, Poseidon, Athena, Apollo-as-figure, Artemis, Horus, Isis*, Hel, Heimdall, Svarog, Stribog, Nut, Geb, Ptah, Sekhmet, Anubis, Hestia, Demeter, Hephaestus, Dionysos | genuinely absent — triaged below |

\* Isis never appeared in the Haiku pass at all — arguably the single
most important Egyptian goddess; found by this audit.

The Haiku prompt drafts (bronze medallion style) are serviceable as
raw material but do NOT follow the theme sheets' border-identity
rules (Greek meander, Egyptian cartouche band, Slavic kolovrat…) —
whoever generates from them should re-base onto the theme sheet
conventions first.

## 3. The mechanism — two rosters, one switch (owner's proposal, adopted)

- New setting **`figure_roster`**: `"canon"` (default — today's
  day-fit seats, untouched) | `"pantheon"` (the culture's most
  important figures). One global dropdown in Settings (beside the
  Artwork source), translated; per-slot complexity is NOT needed —
  the roster is a worldview, not a slot decoration.
- Wiring is the EXISTING theme machinery: a second file table per
  theme (`WEEKDAY_THEME_FILES_PANTHEON`, only for themes that have
  one) resolving to `assets/weekday/<theme>/pantheon/…`, plus
  pantheon articles in `symbolism.json` under the same entity-keyed
  shape. Themes WITHOUT a pantheon roster (most of them) fall back to
  canon — documented fallback, no gray menus needed.
- The NINTHS stay ninths in both rosters (Hades/Baldur/Set/Crnobog
  are doctrine, not roster candidates).
- Duals: the Sunday dual follows the seated sun figure; where the
  pantheon sun changes (Greek), a pantheon dual plate is needed too.

## 4. Per-theme triage — what is missing, why, and the proposed pantheon seat

### Greek — the strongest case for a pantheon roster
Canon: Helios, Selene, Ares, Hermes, Zeus, Aphrodite, Cronus. The
day-fit rule seated two TITAN luminaries (Helios/Selene) and Cronus,
so four Olympian heavyweights lost: **Apollo, Artemis, Athena,
Poseidon** (and Hades, resolved as the Ninth).

| Seat | Canon | Pantheon proposal | Why |
|---|---|---|---|
| Sun | Helios | **Apollo** | the Olympian light, prophecy and music — the classical Sol conflation |
| Moon | Selene | **Artemis** | the Olympian moon-huntress — the classical Luna conflation |
| Mars | Ares | Ares ✓ | already the most important war figure |
| Mercury | Hermes | Hermes ✓ | already top-tier |
| Jupiter | Zeus | Zeus ✓ | already the king |
| Venus | Aphrodite | Aphrodite ✓ | already top-tier |
| Saturn | Cronus | **Poseidon** | the third brother takes the week's deep end; earth-shaker gravity fits Saturday's weight (honest note: the weakest day-affinity in this whole report — alternative: **Demeter**, harvest = direct Cronus continuity) |

Cost: 3 new plates (+dual `apollo_helios`-style sun dual) + colored
trio + 3 articles. Hestia/Demeter/Dionysos/Hephaestus/Eris: see §5.

### Egyptian — two surgical swaps
Canon: Ra, Khonsu, Montu, Thoth, Amun, Hathor, Osiris. The day-fit
rule seated the obscure war-falcon MONTU over **Horus** and the
cow-sky HATHOR over **Isis**.

| Seat | Canon | Pantheon proposal | Why |
|---|---|---|---|
| Mars | Montu | **Horus** | the avenger of Osiris — the actual falcon the world knows; his war is the war that matters |
| Venus | Hathor | **Isis** | the great mother of magic — the most venerated Egyptian goddess, period |
| others | Ra, Khonsu, Thoth, Amun, Osiris ✓ | unchanged | already the culture's first rank |

Cost: 2 plates + 2 articles. Nut/Geb/Ptah/Sekhmet/Anubis/Hapi: §5.

### Slavic — one debatable swap, honestly presented
Canon: Dažbog, Hors, Svetovid, Veles, Perun, Mokoš, Morana — already
essentially the top seven attested figures. The one heavyweight out
is **Svarog** (the father-smith, fire of heaven). No seat is clearly
weaker than him: Svetovid (mars) is a major god; Morana (saturn)
carries the winter-transformation reading the owner likes.
**Proposal:** mars seat Svetovid → Svarog (celestial fire over the
four-faced war idol), and ONLY if the owner agrees — otherwise no
Slavic pantheon roster; Svarog and Stribog join the Encyclopedia (§5).

### Norse — explicitly NO second roster
Sól, Máni, Tyr, Odin, Thor, Freya, Loki — the week is literally named
after this roster; canon IS the pantheon. Heimdall and Hel are real
omissions but neither outranks an incumbent for any seat; Baldr is
the Ninth. → Heimdall + Hel go to the Encyclopedia (§5).

### Professions, Cosmos, and the closed sets
- **Professions** is a CONSTRUCTED estate roster, not a pantheon —
  nothing was "omitted", the seven estates were chosen. Scribe,
  Builder and Hunter are good FUTURE estates but would need seats
  argued from scratch; park them.
- **Cosmos** maps deep-sky objects; candidates are endless (black
  hole and supernova already carry the bible_dark canon; Big Bang is
  the Ninth). No roster change proposed.
- **Alchemy (7 metals), Japan (7 elements), Zodiac (12), Chinese
  (12+Cat)** — closed by nature; nothing is omitted.
- **Bible** already runs THREE rosters (bible, bible2, bible_dark) —
  it is the existing proof that multiple rosters per world work.

### Eris — the special case
Not a seven-seat candidate (discord has no day) and not a ninth
(Hades holds it). Eris belongs with the **dwarf planets** — if the
owner ever wants an "outer bodies" extension (Eris, Pluto†, Haumea,
Makemake), it is an ENCYCLOPEDIA topic or a Cosmos variant arc, not a
weekday seat. († Pluto-the-planet duplicates Hades-the-Ninth — one
more reason this stays out of the week.)

## 5. The Encyclopedia tier — figures that matter but seat nowhere

The owner's instinct "add without removing" has a second, cheaper
lane: an Encyclopedia topic per culture ("The Wider Pantheon") for
figures that are IMPORTANT but should not displace a seat — Hestia,
Demeter, Hephaestus, Dionysos (Greek); Nut, Geb, Ptah, Sekhmet,
Anubis, Hapi (Egyptian); Heimdall, Hel (Norse); Svarog†, Stribog
(Slavic). Article + one plate each, browsable, zero dial impact.
(† unless the Slavic swap in §4 is approved.)

## 6. Execution checklist (waiting on the owner's GO)

1. Approve/adjust the pantheon tables in §4 (Greek Saturday:
   Poseidon or Demeter; Slavic: swap or skip).
2. I extend the theme prompt sheets with the approved pantheon
   figures (border identities preserved) + colored variants where the
   theme has them; the owner generates.
3. Articles: I draft `symbolism.json` pantheon entries in the house
   voice (base + pointer variants + SR translations).
4. Code: `figure_roster` setting + `WEEKDAY_THEME_FILES_PANTHEON` +
   Settings dropdown + tests (one round).
5. Optional second wave: the Encyclopedia "Wider Pantheon" topics
   (§5).
