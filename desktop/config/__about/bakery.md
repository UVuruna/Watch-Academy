# Bakery

**Script:** [bakery.py](../bakery.py)

## Purpose

BAKE-TIME POLICY: what the setup bakeries encode, and how well. Two
names, both owner decrees of 2026-08-12 — the art bakery's WebP quality
and the letter bake's eager finish roster.

It exists as a peer module rather than as more of `defaults.py` on THE
STRUCTURE LAW's own terms. These values are read at SETUP, by
[Make Art Bake](../../setup/__about/make_art_bake.md),
[Make Letter Bake](../../setup/__about/make_letter_bake.md) and the teeth
that check their output. Nothing in the running dial ever asks them
anything. That is a different responsibility from the developer tunables
`defaults.py` holds — and it earned its own file the moment adding it
made that file 1,001 lines long, one over the god-file threshold.

## What is here

| Name | What it decides |
|------|-----------------|
| `ART_BAKE_QUALITY` | the WebP quality of every lossy area of the art bake — **90**, chosen on measurement |
| `EAGER_BAKED_SHADES` | which `(metal, shade)` letter finishes are baked at setup — **17 of 34**, the rest derived on first ask |

Both carry their measurements and their reasoning in place, because both
are numbers a future round will be tempted to change without knowing
what was already tried.

## What is deliberately NOT here

**The pixel ceilings.** They stay in `defaults.WORKING_SET_CEILINGS`,
where the RUNTIME working set reads them. The bakery asks *"how big may
this ship?"*; the runtime asks *"is this bigger than the dial can ever
draw it?"* — the same question at two moments, and they must never be
able to disagree. One table, two readers.
`tests/test_art_bake.py::test_the_bakery_has_no_ceilings_of_its_own`
fails a future round that copies one here.

## Connections

### Uses
- nothing — pure data, no imports at all. It sits at the very top of
  `config`'s import DAG.

### Used by
- [Make Art Bake](../../setup/__about/make_art_bake.md) —
  `ART_BAKE_QUALITY`
- [Make Letter Bake](../../setup/__about/make_letter_bake.md) —
  `EAGER_BAKED_SHADES`, validated against `defaults.METAL_SHADES` on the
  way out
- `tests/test_art_bake.py`, `tests/test_startup_cost.py`
