# Eclipse Category Prompts — the seven category emblems

The ECLIPSES ENCYCLOPEDIA set (fix round F, owner order 2026-07-19:
"posebno za mesec i sunce"): one emblem for each eclipse CATEGORY the
dial distinguishes — SOLAR total / annular / partial / hybrid, and
LUNAR total / partial / penumbral. Seven medallions reading as ONE set,
the doctrine of each state drawn as image alone. The Encyclopedia
chapter pages carry these (`app/encyclopedia.py` `eclipse_solar` /
`eclipse_lunar` topics) AND the on-dial Earth/Moon hover card shows the
active category's emblem beside the eclipse line during an eclipse
window (`render/compositor.py` `_eclipse_emblem`, graceful-absent).

**Register:** the house night-window family (the same stained-glass
register as the archetype and era sheets — see
[Era Prompts](../era/era_prompts.md) and
[Trinity Prompts](../archetype/trinity_prompts.md)) — so the eclipse
emblems sit beside the pointer archetypes and the era medallions
without a style break. All seven are ROUND rose-window medallions on
deep midnight-black night glass, each holding ONE eclipsed body caught
at the defining instant of its category. The two families are told
apart at a glance: the four SOLAR emblems ring a jet-black Sun-disc with
its category's own crown of light; the three LUNAR emblems hold a Full
Moon disc darkened by Earth's round shadow to its category's own depth.

**Drop paths:** `assets/eclipse/` — `Solar_Total.png`,
`Solar_Annular.png`, `Solar_Partial.png`, `Solar_Hybrid.png`,
`Lunar_Total.png`, `Lunar_Partial.png`, `Lunar_Penumbral.png`. No
`<source>` split (a single generation batch, like the emblem/badge/era
families) — the app reads `assets/eclipse/<Name>.png` directly
(`config/defaults.py` `ECLIPSE_ART_DIR`).

**House rules carried from every other sheet:** photorealistic render,
isolated background (no transparency-checkerboard artifact — a clean
isolated field, not a partial cutout), the circular window shape IS the
frame, NO lettering anywhere in any image. Every emblem stays true to
the dial's own sealed state table (see
[Layers](../../../render/layers.md) §THE STATE TABLE): the copper blood
moon for lunar total, the ring of fire for annular, the pearl corona
for solar total, the honest faint veil for penumbral.

---

## The four SOLAR emblems

The Sun belongs to the EARTH marker on the dial; each solar emblem rings
a jet-black lunar silhouette over the Sun with the light its category
actually leaves.

**Total Solar Eclipse** — the pearl corona → `assets/eclipse/Solar_Total.png`

```
ROUND rose-window stained-glass medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. A perfect jet-black disc fills the medallion's center — the Moon covering the Sun completely — ringed by the Sun's pearl-white CORONA blazing outward in soft radiant streamers of white and palest gold glass, its million-degree crown the whole point of the image. A single ruby-red bead (the chromosphere's diamond flash) glints at the disc's lower rim. The surrounding night glass is at its very darkest, stars pricked faintly into it — noon turned to night. Border: a candle-flicker-and-tick leadwork rim, small flame-tick tesserae evenly spaced, brightest where the corona reaches it. Palette: jet black core, radiant pearl-white and pale-gold corona, one ruby bead, deep midnight-black field. NO lettering anywhere.
```

**Annular Solar Eclipse** — the ring of fire → `assets/eclipse/Solar_Annular.png`

```
ROUND rose-window stained-glass medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. A jet-black disc sits dead-center, and around it — unbroken, complete, brilliant — a single blazing RING of hot orange-gold sunlight, the ring of fire, the Moon too small to cover the whole Sun. The ring is the hottest colour in the whole set, molten orange-red glass shading to white-gold at its inner edge. The sky glass around it dims but never falls to full night — a deep dusk-indigo, no stars, the ring too bright for them. Border: the shared candle-flicker-and-tick leadwork rim, lit hot orange by the ring's glow. Palette: jet black core, blazing orange-gold ring of fire, dusk-indigo field, warm dark-gold lead. NO lettering anywhere.
```

**Partial Solar Eclipse** — the curved bite → `assets/eclipse/Solar_Partial.png`

```
ROUND rose-window stained-glass medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. A bright golden Sun-disc fills the medallion, and a jet-black lunar silhouette slides across it from the upper right, biting a clean curved crescent out of the disc — the Sun reduced to a thick golden crescent, no more, its light merely dimmed. Small crescent-shaped dapples of light scatter faintly in the lower field (the pinhole-projection motif — light through leaves). The sky glass is a lightly dimmed blue-grey, still daylight. Border: the shared candle-flicker-and-tick leadwork rim, warm gold. Palette: bright gold Sun crescent, jet-black covering disc, dimmed daylight blue-grey field, warm dark-gold lead. NO lettering anywhere.
```

**Hybrid Solar Eclipse** — total and annular at once → `assets/eclipse/Solar_Hybrid.png`

```
ROUND rose-window stained-glass medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. A jet-black disc at center caught on the knife-edge between the two solar states: along one half of the disc's rim the pearl-white corona of totality feathers outward, and along the other half a hair-thin brilliant ring of orange-gold fire completes the circle — one eclipse wearing both faces at once, sorted by the curve of the Earth. Deep night glass, a few faint stars on the coronal side. Border: the shared candle-flicker-and-tick leadwork rim, pearl-white on one side, hot orange on the other. Palette: jet black core, pearl-white corona blending into an orange-gold fire ring, deep midnight field, dark-gold lead. NO lettering anywhere.
```

---

## The three LUNAR emblems

The Moon belongs to the MOON marker on the dial; each lunar emblem holds
a Full Moon disc darkened by Earth's round umbral shadow to the exact
depth its category reads on the dial.

**Total Lunar Eclipse** — the blood moon → `assets/eclipse/Lunar_Total.png`

```
ROUND rose-window stained-glass medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. A full lunar disc fills the medallion, wholly inside Earth's dark umbra and glowing a deep, dim COPPER-RED — the blood moon — its maria faintly visible through the ruddy shadow, unmistakably dark AND unmistakably red. A thin band of pale TURQUOISE edges the disc along its upper-left rim (the ozone-filtered light at the umbra's edge, the one blue note in the whole set). The surrounding night glass is at its darkest, stars close around the dimmed disc. Border: the shared candle-flicker-and-tick leadwork rim, dark and coppered. Palette: deep copper-red disc, one thin turquoise rim-band, near-black field, dark-bronze lead. NO lettering anywhere.
```

**Partial Lunar Eclipse** — the round shadow's bite → `assets/eclipse/Lunar_Partial.png`

```
ROUND rose-window stained-glass medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. A full lunar disc, bright silver-white across most of its face, with a clean CURVED bite of Earth's round umbral shadow crossing its lower portion — the shadow's edge visibly, perfectly circular (the oldest proof the Earth is a sphere). The bitten, shadowed part glows a faint copper-red where the umbra covers it; the rest stays bright silver. A whisper of turquoise touches the shadow's leading edge. The night field is dark, a scatter of stars. Border: the shared candle-flicker-and-tick leadwork rim. Palette: bright silver-white moon, a copper-red round shadow bite, faint turquoise edge, dark field, aged-silver lead. NO lettering anywhere.
```

**Penumbral Lunar Eclipse** — the faint veil → `assets/eclipse/Lunar_Penumbral.png`

```
ROUND rose-window stained-glass medallion, night-window register, photorealistic render, isolated background, the circular window shape IS the frame. A full lunar disc, still plainly a bright Moon, with only the very faintest grey VEIL dimming one edge — the Moon in Earth's soft outer penumbra, no dark bite, no red, no drama, just a subtle shading a careful eye barely catches. The disc stays about three-fifths as bright as a clear full Moon, honestly gentle. The night field is dark and calm, stars steady around it. Border: the shared candle-flicker-and-tick leadwork rim, quiet and pale. Palette: bright silver-white moon with a faint grey veil at one edge, dark night field, aged-silver lead — the gentlest emblem of the set. NO lettering anywhere.
```

---

## Status

- New sheet (fix round F, owner order 2026-07-19); the seven category
  emblems NOT yet generated.
- Wiring is LIVE and graceful-absent: `assets/eclipse/<Name>.png` backs
  both the Encyclopedia chapter pages (`app/encyclopedia.py`) and the
  eclipse-window Earth/Moon hover badge (`render/compositor.py`); until
  the art lands the chapters read text-only and the hover shows no
  badge (no crash, no placeholder).
- Verify with `python main.py "research/prompts/eclipse/eclipse_prompts.md" --dry-run`
  from `Gadgets/PromptPainter/` before handing the sheet to the owner
  (7 images expected).
