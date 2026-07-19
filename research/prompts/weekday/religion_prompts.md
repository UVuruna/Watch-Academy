# Creeds — the Seven Faiths Weekday Theme (silver plates)

**Rework (owner GO 2026-07-15, `research/pantheon_catalog.md` → "The
Religion rework"):** Christianity takes the Sunday throne (moved off
Friday, its existing plate reused), Sikhism takes the seat Christianity
leaves on Friday (moved in from the Ancient Religions tree, its existing
plate reused), and Freemasonry steps down from Sunday to become the
Ninth — "not a religion, yet present and powerful: the lodge where men
of every creed sit together" (its existing plate reused). The Sunday
dual becomes **Christianity / Satanism** — the faith and its adversary
as its shadow face — the ONE genuinely new plate this sheet needs. The
old dual, The Rough Ashlar (Freemasonry's Servant face), is
**SUPERSEDED**: it no longer renders on the dial, but its plate stays
on disk as historical art. The old Ninth, The Unknown God, **relocates**
to Ancient Religions (see `religion_alt_prompts.md`) — the God behind
all creeds now sits behind the OLDER creeds instead. This sheet is the
ONE complete generation-and-reuse manifest for the reworked roster: all
seven roster prompts below, the new Dual, and the new Ninth, so the
owner never has to cross-reference the pre-rework file. Canon source
remains `Database/symbolism.json` (`articles.religion.<body>.base` /
`.faces`) for the six unmoved plates; Christianity's, Sikhism's and
Freemasonry's canon paragraphs still live under their OLD body keys
until a later symbolism.json round re-homes the prose — this sheet only
reseats the ART. Menu title stays `WEEKDAY_THEME_TITLES["religion"] =
"Creeds"` (unchanged by this rework — only the roster inside it moves).

**Border identity:** silver-on-black, NOT the warm-bronze register the
other legacy themes share. Rather than one shared ring imposed across
six living world religions and a fraternal order, **each faith keeps
its OWN canonical emblem and border** straight from its own canon
paragraph — Christianity's grapevine-and-fish rim, Islam's geometric
strapwork, Buddhism's lotus rim, Taoism's bagua-and-yin-yang rim,
Hinduism's Om-rosette rim, Sikhism's lotus-and-khanda rim, Judaism's
leaf-and-star rim — plus Freemasonry's chain of working tools, which now
frames the Ninth instead of the Sunday throne. That is the respectful
choice: a borrowed ring would flatten seven distinct traditions into one
costume; their own symbols carry the family resemblance instead, unified
only by the shared silver-on-black material.

**Style note:** silver sculptural relief on black marble/stone is the
base register (per the canon's own Freemasonry Servant-face line: "the
silver sculptural relief and black marble field of the owner's own
Masonic medallion"). This set stays **single-look silver** — no
gold/silver hue-swap, no `colored/` companion set — with two flagged
exceptions carried over as written, not smoothed to match: Sikhism keeps
its own gold-and-silver-on-starry-midnight material (it is a byte-
identical reuse of the Ancient Religions plate, register and all), and
the new Satanism dual deliberately pulls into a **dark-red register** —
the shadow face earning its own color the same way Ancient Religions'
Shamanism and Voodoo already break THEIR set's gold-and-silver default.

**Respect non-negotiables (every plate):** no legible text, script, or
lettering of any kind — where the canon prose mentions an alphabet
(Hebrew on the Star of David bands) the plate keeps the metal plain or
abstractly textured instead, since asking an image model for readable
script only produces garbled type. Islam stays strictly
calligraphy-free and never depicts the Prophet or any person —
geometric strapwork, crescent and star only. Buddhism keeps the wheel,
the lotus, and a seated meditating silhouette, never a caricature.
Freemasonry keeps the square-and-compasses/ashlar language, no other
order's symbols borrowed in. The new Satanism dual keeps the theme's
dignified-shadow-face rule — a logo-like emblem, not gore: the horned
head and a faint inverted pentagram only, no ritual violence, no other
imagery.

Files land in `assets/weekday/religion/primary/` — the `religion` theme's
OWN directory (`WEEKDAY_THEME_DIRS["religion"] = "religion/primary"`).
`religion_alt` (Ancient Religions) has its own sibling directory,
`religion/secondary/` — the two do NOT share one folder; they sit side
by side under the shared `religion/` family. This rework moves three
files, and every one of those moves is **implementation work (a config
edit, and for Sikhism a file copy across the primary/secondary
boundary) — not art regeneration**:

- **christianity.png** — stays exactly where it is
  (`religion/primary/christianity.png`); only the body key it is
  attached to changes, venus → sun. Zero file move.
- **sikhism.png** — a real cross-tree move,
  `religion/secondary/sikhism.png` → `religion/primary/sikhism.png`,
  plus the matching config edit (drops out of `religion_alt`, joins
  `religion` at venus).
- **freemasonry.png** — stays exactly where it is
  (`religion/primary/freemasonry.png`); only its role changes, from the
  Sunday-seat file to the Ninth-topic plate (the `app/encyclopedia.py`
  ninth entry repoints from `unknown_god.png` to `freemasonry.png`).
  Zero file move.

Stems below are exact and lowercase, matching
`WEEKDAY_THEME_FILES["religion"]`, so new art overwrites in place.

| Day | Body | Creed | File |
|---|---|---|---|
| Sunday | sun | Christianity (dual: Satanism) | `assets/weekday/religion/primary/christianity.png` / `assets/weekday/religion/primary/satanism.png` |
| Monday | moon | Islam | `assets/weekday/religion/primary/islam.png` |
| Tuesday | mars | Buddhism | `assets/weekday/religion/primary/buddhism.png` |
| Wednesday | mercury | Taoism | `assets/weekday/religion/primary/taoism.png` |
| Thursday | jupiter | Hinduism | `assets/weekday/religion/primary/hinduism.png` |
| Friday | venus | Sikhism | `assets/weekday/religion/primary/sikhism.png` |
| Saturday | saturn | Judaism | `assets/weekday/religion/primary/judaism.png` |

Freemasonry no longer occupies a weekday seat at all — it moves to
The Ninth, below.

---

## The roster — seven plates

**Sunday — Christianity** → `assets/weekday/religion/primary/christianity.png`

*REUSE, moved from Friday (venus → sun) — file and prompt untouched.
The glowing white cross with the Chi-Rho at the crossing and the crown
of thorns at its foot, per the article.*

```
Ornate circular medallion, silver sculptural relief on black stone, photorealistic render, perfectly centered, isolated on white background, square 1:1 aspect ratio. Center: a glowing white cross, a simple Chi-Rho monogram at the crossing point, a crown of thorns resting quietly at the cross's foot. Border: silver rim weaving grapevines with tiny fish shapes threaded between the leaves. Palette: black stone and silver relief dominant; the cross's soft white glow the only bright accent. No text, no watermark.
```

**Monday — Islam** → `assets/weekday/religion/primary/islam.png`

*KEEP verbatim. The golden crescent filled with arabesque vinework, no
image of the divine, only pattern — the article's own rule.*

```
Ornate circular medallion, silver sculptural relief on deep lapis-blue stone, photorealistic render, perfectly centered, isolated on white background, square 1:1 aspect ratio. Center: a golden crescent moon filled with intricate arabesque vinework, a five-pointed star nested in its embrace like a rosette — pattern and geometry only, nothing figural, no calligraphy, no depiction of any person. Border: silver rim tiled with small repeating eight-point geometric star medallions (girih strapwork). Palette: silver relief and deep lapis-blue stone dominant; the crescent and star the only warm gold accent. No text, no calligraphy, no watermark.
```

**Tuesday — Buddhism** → `assets/weekday/religion/primary/buddhism.png`

*KEEP verbatim. The eight-spoked Dharma wheel with the seated Buddha at
its hub, per the article's opening image.*

```
Ornate circular medallion, silver sculptural relief on lapis-blue stone, photorealistic render, perfectly centered, isolated on white background, square 1:1 aspect ratio. Center: a golden eight-spoked Dharma wheel, a serene silver Buddha seated cross-legged in meditation at its hub, hands resting in his lap, eyes closed, utterly still. Border: a rim of silver lotus blossoms rising in low relief, clean petals lifting as if straight out of unseen mud. Palette: silver relief and lapis-blue stone dominant; the golden wheel the only warm accent. No text, no watermark.
```

**Wednesday — Taoism** → `assets/weekday/religion/primary/taoism.png`

*KEEP verbatim. The taijitu cut in gold and dark metal, clouds against
mountains and waves — the article's own image.*

```
Ornate circular medallion, silver-and-gold sculptural relief on near-black marble, photorealistic render, perfectly centered, isolated on white background, square 1:1 aspect ratio. Center: a taijitu cut in gold and dark silver-toned metal, the bright half engraved with scrolling clouds, the dark half with mountains and waves — heaven turning inside earth. Border: silver rim alternating eight bagua trigram marks with small yin-yang roundels. Palette: silver-and-black relief dominant; the taijitu's gold half the only warm accent. No text, no watermark.
```

**Thursday — Hinduism** → `assets/weekday/religion/primary/hinduism.png`

*KEEP verbatim. The golden Om with the crescent and bindu floating
above it like the sound's last trace, per the article.*

```
Ornate circular medallion, silver sculptural relief on amber-toned stone, photorealistic render, perfectly centered, isolated on white background, square 1:1 aspect ratio. Center: a golden Om symbol raised in fine filigree, a crescent and dot floating above its curve like the sound's last trace. Border: silver rim stringing flower rosettes with small Om-shaped roundels set at the four quarters. Palette: silver relief and amber stone dominant; the golden Om the only warm accent. No text, no watermark.
```

**Friday — Sikhism** → `assets/weekday/religion/primary/sikhism.png`

*REUSE, moved in from Ancient Religions (jupiter → venus, a real
cross-tree file move — see the header) — file and prompt untouched,
gold-and-silver register kept as written, the flagged exception to this
set's silver-only rule. The golden Khanda inside the chakkar with
crossed kirpans, per the article's opening image.*

```
Ornate circular medallion, gold-and-silver relief on a starry midnight field, photorealistic render, perfectly centered, isolated on white background, square 1:1 aspect ratio. Center: a golden Khanda — a double-edged sword upright inside a circular chakkar ring, two curved kirpans crossed behind it — set against a starry midnight field. Border: silver rim alternating lotus flowers with small khanda-shaped roundels. Palette: gold-and-silver relief on starry midnight stone dominant; the Khanda the brightest accent. No text, no watermark.
```

**Saturday — Judaism** → `assets/weekday/religion/primary/judaism.png`

*KEEP verbatim. The Star of David woven from two interlocked triangles,
per the article — bands left plain rather than lettered.*

```
Ornate circular medallion, silver sculptural relief on dark slate, photorealistic render, perfectly centered, isolated on white background, square 1:1 aspect ratio. Center: a golden Star of David formed from two interlocked triangles, its bands left smooth and finely fluted, deliberately free of any inscription. Border: silver rim circling small leaf and six-point-star roundels. Palette: silver relief and dark slate dominant; the golden star the only warm accent. No text, no script, no watermark.
```

---

## Dual — Christianity / Satanism (`assets/weekday/religion/primary/satanism.png`)

**NEW plate (this rework)** — the faith's adversary as its shadow face:
the red horned Devil rendered as a dignified, logo-like emblem, not a
gore prop. Inverted-pentagram motifs are allowed as a faint background
mark. This is the one plate the set deliberately pulls into a
**dark-red register**, breaking the silver-only rule the way Ancient
Religions' Shamanism and Voodoo already break gold-and-silver — kept as
written, not smoothed over. The border mirrors Christianity's own
grapevine-and-fish rim, inverted rather than borrowed from elsewhere,
matching how this theme's other duals (see the superseded Rough Ashlar
below) always echo their bright face's border, dimmed or reversed.

```
Ornate circular medallion, dark-red sculptural relief on black stone, photorealistic render, perfectly centered, isolated on white background, square 1:1 aspect ratio. Center: a horned devil's head rendered as a clean, logo-like emblem — twin curved horns, a goat-bearded jaw, eyes closed in cold repose — facing forward at the medallion's heart, a small inverted pentagram traced faintly in the stone behind the crown of the horns. Border: the same grapevine-and-fish rim as the bright face, cast in the same dark-red metal, the vines withered and the fish turned tail-first, circling the opposite way. Palette: dark-red relief and black stone dominant, the theme's one deliberate break from its silver register; no other bright accent. No text, no watermark.
```

**SUPERSEDED — The Rough Ashlar** (Freemasonry's old Servant face, now
flat at `assets/weekday/religion/primary/rough_ashlar.png`): no longer
wired into the theme now that Freemasonry has left Sunday for the
Ninth. The plate stays on disk as historical art — nothing to delete,
nothing to regenerate. Prompt kept here for the record only:

```
Ornate circular medallion, silver sculptural relief on black marble, photorealistic render, perfectly centered, isolated on white background, square 1:1 aspect ratio. Center: a rough-hewn cubic stone block resting on a tracing board, its faces still cracked and unworked, a gavel and chisel leaning against its base and a plumb line hanging beside it; high above in the gloom the All-Seeing Eye watches faintly, one thin ray touching only the stone's top edge — the work not yet begun, the light only promised. Border: the same chain of silver working tools, darker and quieter. Palette: darkened silver relief and black marble dominant; the single thin ray of light the only bright accent. No text, no watermark.
```

---

## Ninth — Freemasonry (`freemasonry.png`)

**REUSE**, moved from the Sunday seat — file and prompt untouched. The
ninth reading: not a religion, yet present and powerful — the lodge
where men of every creed sit together, the union the seven faiths
themselves cannot form. (Freemasonry keeps its own compasses-and-eye
imagery below; nothing about the artwork needed to change for the seat
to change.)

```
Ornate circular medallion, silver sculptural relief on black marble, photorealistic render, perfectly centered, isolated on white background, square 1:1 aspect ratio. Center: golden compasses held open above a golden square against a starry night ground, the All-Seeing Eye blazing in a triangle of rays directly between the compass legs. Border: a chain of silver working tools — gavels, trowels, plumb lines — linked edge to edge like a roll of the brotherhood. Palette: silver relief and black marble dominant; the compasses, square and eye the only warm gold accent. No text, no watermark.
```

**RELOCATED — The Unknown God** (the theme's old Ninth,
`unknown_god.png`): moves OUT of Creeds entirely and becomes Ancient
Religions' Ninth instead — see `religion_alt_prompts.md`, which carries
its full prompt and the file-move note
(`religion/primary/unknown_god.png` → `religion/secondary/unknown_god.png`).
Nothing of it remains active here.

---

## Historical / optional appendix — do not generate by default

Superseded and optional companion plates, moved verbatim from the
retired `sunday_duality.md`, kept for the record only. None of these
are wired into the current roster; the generation-order checklist below
does not include them — the owner generates from this appendix only by
deliberate choice.

**The Rough Ashlar** (Freemasonry's old Servant face) is already
documented above under "Dual — Christianity / Satanism" as SUPERSEDED
— not repeated here to avoid two copies of the same plate.

**Washbasin — Christianity's retired dual** (now flat at
`assets/weekday/religion/primary/washbasin.png`):
before this rework, Christianity's Sunday dual was the washbasin-and-
towel pairing ("the king who washes feet, the God who empties
himself... the king of kings who kneels to wash feet is the
servant-king in one body") rather than Satanism. Superseded by the
Satanism dual above; the plate stays on disk as historical art.

```
Circular medallion, polished silver relief on black marble stone, photorealistic render, perfectly centered, isolated on transparent background — same finish and grapevine-and-ichthys border as christianity.png. Center: a plain silver washbasin and folded linen towel resting on black marble, water rippling in the basin catching a soft glow, a simple wooden staff leaning beside it where the cross stood in the christianity.png plate, the crown of thorns now resting loose and open beside the basin instead of at a cross's foot; the same soft glow that lit the cross in christianity.png now lighting the water's surface. Border: identical silver grapevine-and-ichthys knotwork ring to christianity.png. Palette: polished silver, deep black marble, soft warm-white glow — matching the christianity.png plate's finish exactly, no bright colors.
```

**Perfect Ashlar — optional bright counterpart to the Rough Ashlar**
(now flat at `assets/weekday/religion/primary/perfect_ashlar.png`, only
if the owner wants the pair as TWO new images instead of reusing
`freemasonry.png`):

```
Circular medallion, polished silver sculptural relief on black marble, photorealistic render, perfectly centered, isolated on transparent background — same finish and border family as the owner's freemasonry religion medallion. Center: a perfectly squared and polished cubic ashlar on a masonic tracing board, its faces mirror-smooth and returning the light, suspended from a lewis hook above a builder's level; the All-Seeing Eye within a radiant triangle blazes directly over it, its glory rays breaking on the cube's edges into small stars. Border: silver ring bearing small roundels that alternate the square-and-compasses with a tiny radiant delta. Palette: silver, graphite black, radiant white-gold rays — matching the religion set's black-stone finish exactly.
```

**Optional main-medallion upgrade** — square, compasses AND the Eye
(would replace `freemasonry.png`, the current Ninth plate):

```
Circular medallion, polished silver sculptural relief on black marble, photorealistic render, perfectly centered, isolated on transparent background — same finish and border family as the other religion medallions (black stone, silver relief). Center: the square and compasses opened over an open book of constitutions, the letter G at their crossing; above them the All-Seeing Eye within a radiant triangle, its glory rays fanning down so the tools work literally UNDER the Eye's light; two small columns flank the composition at the edges. Border: silver ring with small roundels alternating a radiant delta, a trowel and a plumb line. Palette: silver, graphite black, pale white-gold rays.
```

---

## Generation-order checklist

1. **Generate NEW art — one plate:** the Satanism dual
   (`assets/weekday/religion/primary/satanism.png`). Everything else in this theme already exists.
2. **Move — sikhism.png**: copy `assets/weekday/religion/secondary/sikhism.png`
   → `assets/weekday/religion/primary/sikhism.png` (implementation
   work, no regeneration).
3. **Reassign — christianity.png**: file stays put; only the venus→sun
   seat mapping in code changes.
4. **Reassign — freemasonry.png**: file stays put; only its role
   changes from the Sunday seat to the Ninth-topic plate.
5. **Move out — unknown_god.png**: relocates to Ancient Religions
   (documented in full over there).
6. **Leave on disk, unused — `assets/weekday/religion/primary/rough_ashlar.png`**: the superseded
   Freemasonry dual, now flat; historical art, not wired into the theme anymore.
7. Islam, Buddhism, Taoism, Hinduism, Judaism: unchanged, no action
   needed.
