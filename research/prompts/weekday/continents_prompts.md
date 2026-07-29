# Continents — the two Ninths

The Continents weekday theme (owner-sealed matrix 2026-07-21) is the
one theme whose seated art the owner supplies himself: the six weekday
continents ride his own Earth globes in
`assets/celestial/earth/` (`earth_clean_*` / `earth_atmo_*`, day and
night per region), and the theme's title page reads the wired
`world.png`. **No prompt is written for any of those** — they exist, and
they are photographs of a real planet, not a style this project
generates.

What the theme still owes is its **two Ninths**, and only those:

| Ninth | When it shows | File |
|---|---|---|
| **Zealandia** | the ordinary Ninth seat | `assets/celestial/earth/zealandia.png` |
| **Pangea** | INSTEAD of Zealandia when the sky is doing something — an eclipse, a solstice or equinox, a full or new moon (`core.continents`, the owner's Easter egg) | `assets/celestial/earth/pangea.png` |

Both are wired ahead of the art and both articles are written
(`Database/encyclopedia.json` §`ninths`). Pangea is the file the Session
27 coverage law names; Zealandia is written in the same sheet because
it is the same seat in the same family, and splitting them would open a
second round for one image.

## The family's own look — read this first

These two are NOT medallions, rose windows or stained glass. They join a
family of **photoreal globes**, and they must sit beside
`earth_clean_europe_day.png` without announcing themselves as
illustrations:

- ONE globe, centred, filling the frame the way the existing Earth
  plates do, **isolated on a transparent/black background** — no
  vignette, no frame, no ornament, no border ring.
- Photographic satellite look: real ocean colour, real cloud and
  atmospheric limb, terminator shading consistent with a single sun.
- **NO lettering anywhere** — no country names, no labels, no scale bar,
  no compass rose. The names live in the articles.
- The one place they may differ from the six seated globes is the
  GEOGRAPHY itself, which is the whole point of each.

## Derivation check (Rule #19)

**Not derivable — two new images.** Neither is a tint, an angle, a
phase or a transform of any Earth plate we own: one shows land that is
94% under water and the other shows the continents fused as they stood
300 million years ago. Nothing in the existing globe set contains that
geography to be recovered from it.

**What IS derived and must not be commissioned:** the day/night pair.
The dial already picks the `_day` / `_night` variant per moment for
every seated continent, and the same law covers these two — generate
each Ninth ONCE, in the family's day lighting, and let the instrument do
what it already does with the rest.

---

**Zealandia — the Unfound** →
`assets/celestial/earth/zealandia.png`

*A true continent, 94% drowned and unrecognized until 2017 — the Ninth
that is really there and is simply not seen.*

```
Photorealistic satellite view of Earth from orbit, ONE globe centred and filling the frame, isolated on a plain transparent black background, no border, no frame, no ornament, no lettering of any kind. The globe is turned to the southwest Pacific with New Zealand and New Caledonia at the centre of the disc. The submerged continent of Zealandia is shown as it actually is: a vast continuous continental shelf reading clearly THROUGH the water as a pale blue-green shallow mass roughly the size of Australia, its true coastline unmistakable beneath the surface, with only New Zealand, New Caledonia and a scatter of small islands breaking above it into open air. Deep ocean around it stays dark indigo, so the drowned landmass reads as one whole continent seen through water rather than as scattered islands. Real ocean colour, real cloud, a soft atmospheric limb at the edge of the disc, single-sun daylight with a natural terminator at the rim. No labels, no place names, no scale, no compass.
```

**Pangea — the deep-time Ninth** →
`assets/celestial/earth/pangea.png`

*Was one, is many, will be one again — the whole wheel of continents as
a single body, 300 million years ago.*

```
Photorealistic satellite view of Earth from orbit, ONE globe centred and filling the frame, isolated on a plain transparent black background, no border, no frame, no ornament, no lettering of any kind. The globe shows the planet as it stood in the late Palaeozoic: the single supercontinent Pangea occupying the visible face as one continuous landmass in its correct reconstructed shape, the great Tethys ocean biting into it from the east as a wide gulf, and the world ocean Panthalassa filling everything else. Surface reads as real terrain photographed from orbit — vast red-brown interior desert far from any coast, mountain chains raised where the plates have collided along the join, green only in the coastal belts and along river systems, polar ice at the southern extreme. Real cloud systems, a soft atmospheric limb, single-sun daylight with a natural terminator at the rim. No labels, no place names, no modern coastlines, no scale, no compass.
```

---

## Status

- New sheet (Session 27 coverage round, 2026-07-29). Neither image
  exists; both seats are wired and graceful-absent today, and
  `tests/test_pointer.py` documents the Zealandia seat as the one
  remaining pending-art exception in the ninths table.
- The six seated continents and the theme title need NO prompts — the
  owner's own Earth photography already fills them.
- Verify with `python main.py "research/prompts/weekday/continents_prompts.md" --dry-run`
  from `Gadgets/PromptPainter/` before handing the sheet to the owner
  (2 images expected).
