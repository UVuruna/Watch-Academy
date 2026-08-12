# Make Art Bake

**Script:** [Make Art Bake (script)](../make_art_bake.py) · **Flow:** [diagram](../__flow/make_art_bake.md)

## Purpose

THE ART BAKERY. It turns the owner's full-resolution research masters
into the small, application-sized art the two platforms actually read —
once, here, by us, instead of on every user's machine at every install.

Owner order, 2026-08-12. His idea, and his reason, are worth recording
in his own words:

<!-- lang-ok-begin: the owner's decree, quoted verbatim — this block is the record of WHY this script exists, and a translation would make it evidence of nothing -->
> *"neka moja zamisao da ne bismo lupali glavu koja slika je optimizovana
> a koja nije jer da imamo 1 folder koji je git ignor gdje ja ubacujem
> slike kada ih napravim iz research svim promptovi vode u tu lokaciju a
> odatle mi pravimo kompresovanje verzije smanjene koliko je potrebno za
> našu aplikaciju u foldere koje koriste aplikacija android i desktop"*
<!-- lang-ok-end -->

In English: one gitignored folder is the inbox every research prompt
writes into; from there WE produce the compressed, downscaled versions,
into the folders the desktop and Android applications read.

The problem it solves is not only disk. It is **doubt**: with masters
and shipped art in the same tree, no one could tell by looking which
file had been optimized and which had not. The bakery removes the
question by making the two trees different places, with a one-way arrow
between them.

```
   masters/                        GITIGNORED — the owner's inbox.
   |                               Every research prompt writes here.
   |                               Full resolution, PNG, never touched by us.
   |
   |   python -m setup.make_art_bake
   |     1. downscale to the area's WORKING-SET ceiling
   |     2. re-encode (WebP for photographic plates, PNG where lossless matters)
   |     3. record source sha256 + output size in the manifest
   v
   shared/assets/                  COMMITTED — the only art the program sees.
   |
   +--> desktop/  (Qt reads WebP natively)
   +--> android/  (Compose reads WebP natively)
```

## Why this is not the runtime working set

It is the SAME downscale, moved. `render.asset_variants`' working set
(owner 2026-07-15) already builds a downscaled copy per file — but on
the USER's machine, on first sight of each plate. That is what produced
the owner's report of a dead clock for 75 seconds, and the whole lazy
working-set ledger built to hide it. Work done once by us is work no
user pays. The runtime machinery STAYS — a master dropped in by hand
still gets handled — it simply stops having anything to do on a shipped
tree, because every file already arrives at or under its ceiling.

The ceilings are read from `defaults.WORKING_SET_CEILINGS`, the very
table the runtime uses. There is no second list. Teaching this script
its own ceilings would be the second source of truth that
[Make Letter Bake](make_letter_bake.md) already explains the cost of.

## What is baked, and how

| Area | Ceiling | Encoding | Why |
|------|---------|----------|-----|
| `weeks`, `archetypes`, `calendars`, `celestial/seasons`, `celestial/era`, `celestial/eclipse` | **512 px** | WebP, lossy | every drawn area, one number |
| `celestial/earth` | **full resolution** | WebP, lossy | the owner's Globe decree of 2026-07-15 — see `FULL_RESOLUTION_SUBTREES` |
| `instrument/letters` | — | **PNG, untouched** | see below |
| everything else | — | **copied verbatim** | hands, guide, logos, skins |

**One ceiling, 512, for everything the dial draws** (owner decrees of
2026-08-13). He first lowered the 800 to 512; shown that the 1200 seats
are visibly softer at their worst case, he ruled that such a dial is a
situation nobody will ever use — and that anyone who insists on one
should simply get the upscaling done on the spot. That is
[Upscale](../../render/__about/upscale.md): a request above the shipped
size is served by a real stepped-and-sharpened upscaler, cached on that
machine, instead of by shipping pixels every ordinary user carries and
nobody sees.

**`instrument/letters` is deliberately exempt.** Those plates are the
GOLD MASTERS of THE ONE PLATE LAW: the transformer reads them and runs
an oklab pass with a guided box filter and a specular ramp over their
pixels. A lossy encode there would not cost one image its crispness —
it would bake compression artifacts into all 34 finishes of every
glyph, everywhere the program draws text. They are also already small
(palette PNGs, tens of KB). Nothing to win, everything to lose.

## The manifest

`shared/assets/_bake_manifest.json` records, per baked file, the
sha256 of its SOURCE master plus the output's dimensions and byte size.
Two things follow:

- **Incremental by construction.** A master whose hash is unchanged is
  not re-baked. Re-running after adding twenty images costs twenty
  images.
- **Provenance survives the gitignore.** The masters are not in the
  repo, so the repo could not otherwise say which master a shipped file
  came from, or notice that one was silently replaced. The hash says
  both.

## Connections

### Uses
- [Config (folder)](../../config/___config.md) —
  `defaults.WORKING_SET_CEILINGS` (THE ceiling table, shared with the
  runtime), `defaults.ART_BAKE_QUALITY`, `paths.assets_dir`,
  `paths.masters_dir`

### Used by
- nobody at runtime — a setup/maintenance script, like
  [Make Letter Bake](make_letter_bake.md) and
  [Make Deep Time](make_deep_time.md)
- its OUTPUT is what every art consumer reads, resolved through
  `paths.art_file` (which learned `.webp` in the same round)

## Running it

```
python -m setup.make_art_bake            # bake what changed
python -m setup.make_art_bake --force    # rebuild everything
python -m setup.make_art_bake --list     # report the plan, no work
```

**When to re-run:** whenever the owner drops new art into `masters/`.
Nothing else.

## Design Decisions

- **One-way arrow, never a round trip.** The bakery reads `masters/`
  and writes `shared/assets/`. It never reads its own output and never
  writes back to the masters. A master is the owner's file; we do not
  own it.
- **The canonical path stays `.png` everywhere in config.** The suffix
  change lives entirely inside `paths.art_file`, which already probed
  disk for the `_gem`/`_gpt` source suffix. Adding one extension to that
  probe changed one function instead of every art table in `config/`.
- **A mixed tree is legal, forever.** `.webp` wins where it exists,
  `.png` still resolves where it does not. The migration therefore has
  no flag day, and a hand-made PNG dropped in by the owner keeps working.
- **Files outside a ceiling'd area are COPIED, not skipped.** The
  shipped tree must be complete on its own — a consumer reading
  `shared/assets/` must never need `masters/` to exist.
