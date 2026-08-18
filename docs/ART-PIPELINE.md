# The Art Pipeline — masters → bakery → assets

Read this before touching art, a prompt sheet, `shared/assets/`, or anything
that globs image files. Script docs: [Make Art
Bake](../desktop/setup/__about/make_art_bake.md). Sibling docs:
[Decisions](DECISIONS.md) · [The Dial](DIAL.md) · [Enforcement](ENFORCEMENT.md)

## THE ART BAKERY (decree 2026-08-12) — the fourth top-level folder is not in git

`masters/` is the owner's gitignored inbox: every research prompt writes its
full-resolution output there, and nothing ever reads it except
`desktop/setup/make_art_bake.py`, which downscales to the area's
`WORKING_SET_CEILINGS` entry and re-encodes to WebP q90 into
`shared/assets/` — the small, committed tree BOTH platforms read.

Consequences, all of them load-bearing:

**(a)** Never edit art under `shared/assets/`. Edit the master and re-run
`python -m setup.make_art_bake` (incremental, keyed by the master's sha256 in
`shared/assets/_bake_manifest.json`).

**(b)** The shipped art is `.webp`; every config table still names the
canonical `.png` and `paths.art_file` does the translation. It is the single
door — do not add a second.

**(c)** Never write `rglob("*.png")` over the assets tree — use
`paths.art_files_under` / `paths.is_art_file`. A `*.png` glob now matches
NOTHING in the baked areas and would pass a guard in silence. (This exact
trap had already rotted `shared/research/build_roster.py`, which reported
every baked file as missing until 2026-08-18.)

**(d)** `_baked/letters/` is lossless WebP of the EAGER roster only
(`defaults.EAGER_BAKED_SHADES`, 17 of the 34 pairs); the rest derive at
runtime as they always could.

**(e)** A clone without `masters/` is a complete, working program — that is
the whole point.

**(f) THE SYNC FLOW (order 2026-08-13):** a bake run RECONCILES before it
bakes — a master taken away takes its shipped file and its manifest entry
with it, and an emptied folder goes too. The prune's reach is exactly the
top-level names that exist under `masters/` (`governed_subtrees`), never
`instrument/letters` or anything else the bakery did not make; an unclaimed
file inside a governed area is REPORTED, and only `--prune-strays` deletes
it. `--check` is the build gate: it writes nothing, exits non-zero on drift,
and is called first thing by `setup/make_contract_pack.py` and by every
future build. The arrow is one-way — nothing is ever written back into
`masters/`.

## THE HALF-GOVERNED AREA (verdict 2026-08-14)

The bakery claims the top-level names under `masters/` — EXCEPT those in
`make_art_bake.DEEP_GOVERNED_ROOTS`, where authority is claimed one level
deeper. `instrument` is the only member and must stay one:
`shared/assets/instrument/` also holds the 59 letter plates of THE ONE PLATE
LAW plus guide/hands/icons/ring — ~147 files no master will ever claim — so
whole-area governance would make every one of them a stray, hold `--check`
red forever, and let a single `--prune-strays` delete the program's alphabet.

`VERBATIM_SUBTREES` does NOT protect against this: it exempts from
re-encoding, not from the prune.

## THE MASTERS PREFIX (ballot verdict 2026-08-14)

A prompt sheet's drop path names where a GENERATION LANDS, so it reads
`masters/…` — never `assets/…`, which named a folder that existed nowhere in
the repo once the bakery was born, leaving PromptPainter with no folder its
owner could select. **Its Output field is the repo root**; the sheet's own
path supplies the rest.

1,475 paths across 66 sheets were rewritten. The tooth is
`desktop/tests/test_prompt_paths.py`: it reads the `masters/` convention and
reduces both prefixes to one canonical form (the bakery mirrors the trees
name for name), while still checking folder existence against
`shared/assets/` so a clone without `masters/` grades the same.

## THE THEME COMPLETION LAW

A theme is finished when it is SEEN, not when its art exists. The law, the
failure it was born from and its guard live in
[Enforcement](ENFORCEMENT.md#theme-completion).
