# Japanese Week — the Yōbi Weekday Theme (wa-motif plates)

The Japanese-week set — Amaterasu, Tsukuyomi's moon rabbit, the
fire-god's kabuto, Ryujin, the sacred pine, Yata no Kagami, Fuji and
its rice terraces, plus the Sunday dual Ama-no-Iwato — predates the
prompt-sheet convention entirely; this sheet regenerates all eight
plates from the canon in `Database/symbolism.json`
(`articles.japan.<body>.base` / `.faces`) so the owner can drop fresh
renders straight over the existing files. Menu title:
`WEEKDAY_THEME_TITLES["japan"] = "Japanese week"`.

**Border identity:** a shared **seigaiha (scalloped wave) band** frames
every plate's outer rim, unifying the set the way the wave-pattern
already IS Wednesday's own canonical border (Suiyobi, the water-day).
Inside that shared band each plate keeps its own secondary motif from
canon — chrysanthemum (kiku) crests for the Sun, the moon's own
phase-cycle for the Moon, tomoe swirls for Mars, koi for Mercury,
bamboo/maple/pine for Jupiter, ginkgo-and-koban-coin for Venus,
rice-ear-and-asanoha for Saturn. Wherever the canon calls for a roundel
"stamped" with a day-kanji, this sheet substitutes a small **kiku
(chrysanthemum) roundel** instead — kanji-free by design (see below).

**Style note:** each plate keeps its OWN natural material straight
from canon rather than one uniform metal — gold for the Sun, silver
for the Moon, dark bronze for Mars, silver-and-teal for Mercury,
green-patina bronze for Jupiter, warm gold for Venus, aged
iron-and-silver for Saturn. Single-look set: no gold/silver hue-swap
variant, no `colored/` companion set — **none has ever existed for
Japan and none is planned**, so this sheet is the whole art brief.

**Non-negotiable:** NO kanji, no kana, no legible characters of any
kind anywhere on any plate. The canon's own prose repeatedly calls for
"roundels each stamped [kanji]"; every one of those becomes a plain
kiku roundel instead. This is not a stylistic preference — asking an
image model to render readable Japanese script fails reliably and
produces garbled marks, so the kiku roundel keeps the rim's rhythm
without ever attempting text.

Files land in `assets/weekday/japan/`. Stems below are the exact
lowercase romaji stems from `WEEKDAY_THEME_FILES["japan"]` (macrons and
the apostrophe already folded — `kinyobi`, not `kin'yōbi`); the Sunday
dual sits at `dual/ama_no_iwato.png` per
`WEEKDAY_DUAL_FILES["japan"]`.

| Day | Body | Yōbi figure | File |
|---|---|---|---|
| Sunday | sun | Amaterasu (dual: Ama-no-Iwato) | `nichiyobi.png` / `dual/ama_no_iwato.png` |
| Monday | moon | Tsukuyomi's moon rabbit | `getsuyobi.png` |
| Tuesday | mars | Kagutsuchi / samurai kabuto | `kayobi.png` |
| Wednesday | mercury | Ryujin | `suiyobi.png` |
| Thursday | jupiter | the sacred pine (shinboku) | `mokuyobi.png` |
| Friday | venus | Yata no Kagami (the sacred mirror) | `kinyobi.png` |
| Saturday | saturn | Fuji and the rice terraces | `doyobi.png` |

---

## Wa-motif plates

**Sunday — Amaterasu (Nichiyobi)** → `nichiyobi.png`

*The rising-sun fan with Yatagarasu across the disc and the torii
below it, per the article's opening image.*

```
Ornate circular medallion, gold relief against a crimson sun-orb, photorealistic render, perfectly centered, isolated on white background, square 1:1 aspect ratio. Center: a blaze of gold — a rising-sun fan of cream-and-amber rays spreading behind a glossy crimson sun-orb, a black three-legged crow standing across the orb with wings flung wide, a vermilion torii gate marking the threshold beneath the disc. Border: a thin seigaiha wave band framing the rim, chrysanthemum crests alternating with plain kiku roundels. Palette: gold relief dominant against the crimson sun-orb; the torii's vermilion the only cool-toned accent. No kanji, no text, no watermark.
```

**Sunday (dual) — Ama-no-Iwato** → `dual/ama_no_iwato.png`

*The sealed cave with one sliver of gold light leaking through, per
the article's own Servant-face paragraph.*

```
Ornate circular medallion, near-black relief, photorealistic render, perfectly centered, isolated on white background, square 1:1 aspect ratio. Center: a sealed boulder filling the frame in near-total darkness, the gold sunburst rays behind it snuffed to cold gray-black, a round mirror propped against the rock catching one last thin glint of light, a sprig of sakaki hung with jewels beside it, one sliver of warm gold light just beginning to leak from where the boulder has not quite sealed. Border: the same seigaiha wave band and kiku roundels, darkened. Palette: near-black relief dominant; the single sliver of gold light the only bright accent. No kanji, no text, no watermark.
```

**Monday — Tsukuyomi's moon rabbit (Getsuyobi)** → `getsuyobi.png`

*The rabbit mid-pound at the mortar beneath the full moon, per the
article's opening image.*

```
Ornate circular medallion, silver relief on a deep navy field, photorealistic render, perfectly centered, isolated on white background, square 1:1 aspect ratio. Center: worked in silver over a deep navy field strewn with stars — a bright lunar orb carrying a rabbit in silhouette, mallet raised above a mortar, caught mid-pound, silver cloud-scrolls drifting past. Border: a thin seigaiha wave band, the outer rim cycling the moon through its phases (waxing crescent, half, full, waning) alternating with small kiku roundels. Palette: silver relief on deep navy dominant; the lunar orb the brightest accent. No kanji, no text, no watermark.
```

**Tuesday — Kagutsuchi / samurai kabuto (Kayobi)** → `kayobi.png`

*The horned kabuto over crossed katana wreathed in flame, per the
article's opening image.*

```
Ornate circular medallion, dark bronze relief against a black-and-crimson field, photorealistic render, perfectly centered, isolated on white background, square 1:1 aspect ratio. Center: forged in dark bronze under a red glow — a samurai kabuto helmet, wide crescent horns curving up, set over two crossed katana, orange flames wreathing the whole arrangement. Border: a thin seigaiha wave band, tomoe (comma-shaped swirl) motifs alternating with small kiku roundels, tongues of flame set between them. Palette: dark bronze relief dominant; the flame-glow the only warm bright accent. No kanji, no text, no watermark.
```

**Wednesday — Ryujin (Suiyobi)** → `suiyobi.png`

*The Great Wave with the tide-jewel dragon rising from its curl, per
the article's opening image.*

```
Ornate circular medallion, silver-and-teal relief, photorealistic render, perfectly centered, isolated on white background, square 1:1 aspect ratio. Center: worked in silver and blue-green — a great wave rearing and breaking, a coiled dragon rising from its curl lifting a glowing white tide-jewel in its claws. Border: a seigaiha wave band (the water-day's own wave-pattern, doubled as the family rim), koi swimming between small kiku roundels. Palette: silver-and-teal relief dominant; the tide-jewel's glow the only bright accent. No kanji, no text, no watermark.
```

**Thursday — the sacred pine (Mokuyobi)** → `mokuyobi.png`

*The wind-bent shinboku pine girdled with shimenawa rope, per the
article's opening image.*

```
Ornate circular medallion, green-patina bronze relief, photorealistic render, perfectly centered, isolated on white background, square 1:1 aspect ratio. Center: green patina over bronze — an ancient wind-bent pine gripping a mossy rock, a shimenawa rope hung with white zigzag shide streamers wound around its trunk. Border: a thin seigaiha wave band, bamboo stalks, maple leaves and pine-sprays alternating with small kiku roundels. Palette: green-patina bronze relief dominant; the white shide streamers the only pale accent. No kanji, no text, no watermark.
```

**Friday — Yata no Kagami (Kinyobi)** → `kinyobi.png`

*The polished mirror on its lotus pedestal with falling ginkgo leaves,
per the article's opening image.*

```
Ornate circular medallion, warm gold relief, photorealistic render, perfectly centered, isolated on white background, square 1:1 aspect ratio. Center: warm gold throughout — a round polished mirror standing upright on a lotus-blossom pedestal, golden ginkgo leaves drifting down around it. Border: a thin seigaiha wave band, ginkgo scrollwork alternating with koban-coin shapes and small kiku roundels. Palette: warm gold relief dominant; the mirror's polished glint the only bright accent. No kanji, no text, no watermark.
```

**Saturday — Fuji and the rice terraces (Doyobi)** → `doyobi.png`

*Mount Fuji behind the stone-walled paddies and the weathered stone
lantern, per the article's opening image.*

```
Ornate circular medallion, iron-and-silver relief on an earthen brown field, photorealistic render, perfectly centered, isolated on white background, square 1:1 aspect ratio. Center: aged iron and silver over an earthen brown field — Mount Fuji rising snow-capped behind terraced rice paddies walled with fitted stone, a weathered stone lantern standing in the foreground. Border: a thin seigaiha wave band, heavy rice-ears bowing with grain and asanoha hemp-leaf-star patterns alternating with small kiku roundels. Palette: iron-and-silver relief on earthen brown dominant; Fuji's snow-cap the only pale-bright accent. No kanji, no text, no watermark.
```
