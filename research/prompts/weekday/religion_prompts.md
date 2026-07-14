# Creeds — the Seven Faiths Weekday Theme (silver plates)

The Creeds set — Freemasonry, Islam, Buddhism, Taoism, Hinduism,
Christianity, Judaism, plus the Sunday dual The Rough Ashlar — predates
the prompt-sheet convention entirely; this sheet regenerates all eight
plates from the canon in `Database/symbolism.json`
(`articles.religion.<body>.base` / `.faces`) so the owner can drop
fresh renders straight over the existing files. Menu title (owner
rename 2026-07-13): `WEEKDAY_THEME_TITLES["religion"] = "Creeds"`.

**Border identity:** silver-on-black, NOT the warm-bronze register the
other legacy themes share. Rather than one shared ring imposed across
six living world religions and a fraternal order, **each faith keeps
its OWN canonical emblem and border** straight from its own canon
paragraph — Freemasonry's chain of working tools, Islam's geometric
strapwork, Buddhism's lotus rim, Taoism's bagua-and-yin-yang rim,
Hinduism's Om-rosette rim, Christianity's grapevine-and-fish rim,
Judaism's leaf-and-star rim. That is the respectful choice: a borrowed
ring would flatten seven distinct traditions into one costume; their
own symbols carry the family resemblance instead, unified only by the
shared silver-on-black material.

**Style note:** silver sculptural relief on black marble/stone is the
base register (per the canon's own Freemasonry Servant-face line: "the
silver sculptural relief and black marble field of the owner's own
Masonic medallion"). This set stays **single-look silver** — no
gold/silver hue-swap, no `colored/` companion set.

**Respect non-negotiables (every plate):** no legible text, script, or
lettering of any kind — where the canon prose mentions an alphabet
(Hebrew on the Star of David bands) the plate keeps the metal plain or
abstractly textured instead, since asking an image model for readable
script only produces garbled type. Islam stays strictly
calligraphy-free and never depicts the Prophet or any person —
geometric strapwork, crescent and star only. Buddhism keeps the wheel,
the lotus, and a seated meditating silhouette, never a caricature.
Freemasonry keeps the square-and-compasses/ashlar language, no other
order's symbols borrowed in.

Files land in the SHARED `assets/weekday/religion/` folder — both
`religion` and `religion_alt` point at the same directory per
`WEEKDAY_THEME_DIRS`, and the fourteen stems plus two duals never
collide. Stems below are exact and lowercase, matching
`WEEKDAY_THEME_FILES["religion"]`, so new art overwrites in place.

| Day | Body | Creed | File |
|---|---|---|---|
| Sunday | sun | Freemasonry (dual: The Rough Ashlar) | `freemasonry.png` / `dual/rough_ashlar.png` |
| Monday | moon | Islam | `islam.png` |
| Tuesday | mars | Buddhism | `buddhism.png` |
| Wednesday | mercury | Taoism | `taoism.png` |
| Thursday | jupiter | Hinduism | `hinduism.png` |
| Friday | venus | Christianity | `christianity.png` |
| Saturday | saturn | Judaism | `judaism.png` |

---

## Silver plates

**Sunday — Freemasonry** → `freemasonry.png`

*The golden compasses-over-square and the All-Seeing Eye — the
article's opening image, moved off the arms onto the white-gold
center.*

```
Ornate circular medallion, silver sculptural relief on black marble, photorealistic render, perfectly centered, isolated on white background, square 1:1 aspect ratio. Center: golden compasses held open above a golden square against a starry night ground, the All-Seeing Eye blazing in a triangle of rays directly between the compass legs. Border: a chain of silver working tools — gavels, trowels, plumb lines — linked edge to edge like a roll of the brotherhood. Palette: silver relief and black marble dominant; the compasses, square and eye the only warm gold accent. No text, no watermark.
```

**Sunday (dual) — The Rough Ashlar** → `dual/rough_ashlar.png`

*The Servant face: the stone fresh from the quarry, the work not yet
begun, per the article's own Servant paragraph.*

```
Ornate circular medallion, silver sculptural relief on black marble, photorealistic render, perfectly centered, isolated on white background, square 1:1 aspect ratio. Center: a rough-hewn cubic stone block resting on a tracing board, its faces still cracked and unworked, a gavel and chisel leaning against its base and a plumb line hanging beside it; high above in the gloom the All-Seeing Eye watches faintly, one thin ray touching only the stone's top edge — the work not yet begun, the light only promised. Border: the same chain of silver working tools, darker and quieter. Palette: darkened silver relief and black marble dominant; the single thin ray of light the only bright accent. No text, no watermark.
```

**Monday — Islam** → `islam.png`

*The golden crescent filled with arabesque vinework, no image of the
divine, only pattern — the article's own rule.*

```
Ornate circular medallion, silver sculptural relief on deep lapis-blue stone, photorealistic render, perfectly centered, isolated on white background, square 1:1 aspect ratio. Center: a golden crescent moon filled with intricate arabesque vinework, a five-pointed star nested in its embrace like a rosette — pattern and geometry only, nothing figural, no calligraphy, no depiction of any person. Border: silver rim tiled with small repeating eight-point geometric star medallions (girih strapwork). Palette: silver relief and deep lapis-blue stone dominant; the crescent and star the only warm gold accent. No text, no calligraphy, no watermark.
```

**Tuesday — Buddhism** → `buddhism.png`

*The eight-spoked Dharma wheel with the seated Buddha at its hub, per
the article's opening image.*

```
Ornate circular medallion, silver sculptural relief on lapis-blue stone, photorealistic render, perfectly centered, isolated on white background, square 1:1 aspect ratio. Center: a golden eight-spoked Dharma wheel, a serene silver Buddha seated cross-legged in meditation at its hub, hands resting in his lap, eyes closed, utterly still. Border: a rim of silver lotus blossoms rising in low relief, clean petals lifting as if straight out of unseen mud. Palette: silver relief and lapis-blue stone dominant; the golden wheel the only warm accent. No text, no watermark.
```

**Wednesday — Taoism** → `taoism.png`

*The taijitu cut in gold and dark metal, clouds against mountains and
waves — the article's own image.*

```
Ornate circular medallion, silver-and-gold sculptural relief on near-black marble, photorealistic render, perfectly centered, isolated on white background, square 1:1 aspect ratio. Center: a taijitu cut in gold and dark silver-toned metal, the bright half engraved with scrolling clouds, the dark half with mountains and waves — heaven turning inside earth. Border: silver rim alternating eight bagua trigram marks with small yin-yang roundels. Palette: silver-and-black relief dominant; the taijitu's gold half the only warm accent. No text, no watermark.
```

**Thursday — Hinduism** → `hinduism.png`

*The golden Om with the crescent and bindu floating above it like the
sound's last trace, per the article.*

```
Ornate circular medallion, silver sculptural relief on amber-toned stone, photorealistic render, perfectly centered, isolated on white background, square 1:1 aspect ratio. Center: a golden Om symbol raised in fine filigree, a crescent and dot floating above its curve like the sound's last trace. Border: silver rim stringing flower rosettes with small Om-shaped roundels set at the four quarters. Palette: silver relief and amber stone dominant; the golden Om the only warm accent. No text, no watermark.
```

**Friday — Christianity** → `christianity.png`

*The glowing white cross with the Chi-Rho at the crossing and the
crown of thorns at its foot, per the article.*

```
Ornate circular medallion, silver sculptural relief on black stone, photorealistic render, perfectly centered, isolated on white background, square 1:1 aspect ratio. Center: a glowing white cross, a simple Chi-Rho monogram at the crossing point, a crown of thorns resting quietly at the cross's foot. Border: silver rim weaving grapevines with tiny fish shapes threaded between the leaves. Palette: black stone and silver relief dominant; the cross's soft white glow the only bright accent. No text, no watermark.
```

**Saturday — Judaism** → `judaism.png`

*The Star of David woven from two interlocked triangles, per the
article — bands left plain rather than lettered.*

```
Ornate circular medallion, silver sculptural relief on dark slate, photorealistic render, perfectly centered, isolated on white background, square 1:1 aspect ratio. Center: a golden Star of David formed from two interlocked triangles, its bands left smooth and finely fluted, deliberately free of any inscription. Border: silver rim circling small leaf and six-point-star roundels. Palette: silver relief and dark slate dominant; the golden star the only warm accent. No text, no script, no watermark.
```

---

## The Ninth — The Unknown God (`unknown_god.png`)

Owner 8+1 extension (2026-07-14): the Unknown God is the Ninth of the
Creeds set, kept in the same single-look silver-on-black register as
the other seven — this theme has no colored arc to extend. Use
undecided: legend third plate / Compass ninth seat / Prism triptych.
It is the Athenian altar Paul found inscribed "to the unknown god"
(Acts 17) — the seat every creed quietly keeps open for what it does
not know — rendered dignified and faceless, with a bare unlettered
altar rather than any of the other six emblems, since no duality or
trinity reading from this dial's Judas–Lucifer axis has a natural
claim on it.

```
Ornate circular medallion, silver sculptural relief on black marble, photorealistic render, perfectly centered, isolated on white background, square 1:1 aspect ratio. Center: a plain stone altar standing alone on bare black marble, its face left completely smooth and unlettered where an inscription would sit, a single thin curl of incense smoke rising from its top into empty space above — no idol, no symbol, no figure of any kind resting on or behind it. Border: a plain unbroken silver rim, quietly polished, carrying none of the other six faiths' emblems — no chain of tools, no strapwork, no lotus, no bagua, no Om, no cross, no star. Palette: silver relief and black marble dominant; the single rising thread of smoke the only bright accent. No text, no script, no watermark.
```
