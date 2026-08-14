# Rondel Prompts — one round plate per hover PARAGRAPH

**THE HOVER LAW (owner decree 2026-08-04).** A hover card is built the
same way every time: the tall stained-glass LANCET stands in the left
column at the card's full height, and to its right stand the figure's
paragraphs — one, two or three, as many as that figure owns. Each
paragraph is a column of three things: a ROUND plate on top, a short
text under it, and at the bottom the shortcut that opens that
paragraph's own Encyclopedia article.

The shortcuts are not new. They are THE ARTICLE-DEPTH LAW
([CUBE.md](../../../../CUBE.md) §Display laws): `Space` primary,
`Shift+Space` secondary, `Ctrl+Space` tertiary — which is exactly why a
figure carries one, two or three paragraphs and never four.

**THE DIAL LAW that comes with it (same decree).** On the dial, in the
diamonds, a seat may hold ONLY a round (or square) plate at 1:1 — never
a lancet, never anything stretched. Saturn is the documented exception
(its rings overflow the frame on purpose). The lancets are not surplus:
their place is the hover's left column, which is what this sheet's
companion plates are for.

---

## What a paragraph is — read from the data, never invented

A paragraph is `rows[i]` of the figure's entry in
`Database/symbolism.json` → `articles.archetype_*`. The count is already
fixed there and this sheet does not change it:

| Wheel | Family folder | Figures | rows / figure |
|-------|---------------|---------|---------------|
| trinity_primary | `trinity` | 3 | 2 |
| trinity_secondary | `family` | 3 | 2 |
| quaternity_primary | `temperaments` | 4 | 2 |
| quaternity_secondary | `tetramorph` | 4 | 3 |
| prism_primary | `persons` | 6 | 2 |
| prism_secondary | `one_soul` | 6 | 2 |
| compass_primary | `walks` | 8 | 2 |
| compass_secondary | `life` | 8 | 1 |
| trinity_genesis | `genesis` | 3 | 2 |
| prism_council | `council` | 6 | 2 |
| compass_character | `character` | 8 | 2 |
| rose_vertices | `vertices` | 8 | 2 |

## What is NOT drawn again (Rule #19 — one image, one place)

- **Paragraph 1 of every figure reuses the figure's own 1:1 badge**
  (`<family>/circle/colored/<Stem>.png`, written by
  [Badge 1:1 Prompts](../badge/badge_1to1_prompts.md) and largely
  generated). Row one IS the figure, and the figure already has a round
  plate — drawing a second one would be the same image under a second
  name.
- **The Tetramorph's paragraph 2 reuses the EVANGELIST rondels**
  (`evangelist/primary/colored/{Mark,Luke,John,Matthew}.png`, drawn and
  the only rondels wired today). Row two of each creature IS its
  evangelist.
- The 13 rondels already drawn — `trinity` (Judge, Prosecutor,
  Advocate), `family` (Heart, Shield), `walks` (all eight objects) —
  stay as they are.

**This sheet therefore commissions 46 new plates**, listed below.

## Register, recipe and drop path

**Register:** the SAME house night-window stained-glass family as the
parent lancet — a rondel is not a new look, it is the paragraph's own
subject rendered in the parent figure's exact palette and border-motif
vocabulary, so plate and lancet read as one window and one hand.

**Recipe, every entry:** ONE round composition, aspect exactly 1:1, one
subject filling the frame, leaded border, no lettering anywhere in the
image (the paragraph carries its own text beside it), readable at
roughly 96 px across since that is the size the hover column gives it.
Where the paragraph names a FALL or a SHADOW, the plate keeps the
parent's palette and darkens it — the fall is the same colour gone
wrong, never a different colour.

**Drop path:** `masters/archetypes/<family>/primary/colored/Rondel_<Stem>.png`
— beside the lancet, in the family's own primary register, exactly
where the 13 existing rondels already sit. Where a figure owns three
paragraphs the third takes a `_3` suffix.

---

## family — 1 plate

**Rondel_Anchor** — the Child's paragraph. A small anchor of blue-white
morning glass set in a rising sun's first ray, held by the same leaded
circle the Hearth rosette uses. NAME NOTE: the plate on disk today is
`Rondel_Dawn` while `config.archetypes` declares the row-2 name "The
Anchor" — the config name is authoritative; either the file is renamed
or this plate replaces it.

## temperaments — 4 plates

Each is an AGE of a life in that temperament's own season colour, and
each of the four must be distinguishable at a glance by light alone.

- **Rondel_Prime** — the Choleric's noon: summer gold at its full, a
  sun standing dead centre with no shadow anywhere in the frame, powers
  at their height.
- **Rondel_Middle_Age** — the Melancholic's turn: autumn olive, a low
  evening sun over a counted harvest, the first long shadow of the set.
- **Rondel_Old_Age** — the Phlegmatic's still evening: winter water
  blue, an unbroken lake surface under the longest night, no ripple.
- **Rondel_Childhood_Youth** — the Sanguine's morning: spring pale
  white-yellow, blossom opening into a breeze, all beginning and no
  ending in the frame.

## tetramorph — 4 plates (the ELEMENT, paragraph three)

The four elements as pure matter, each in the exact hue its own
paragraph names, and each kept deliberately apart from the temperament
wheel's season colours above.

- **Rondel_Mark_3** — FIRE: live coals in scorched flame-red, hot and
  dry, kept clear of the summer gold beside it.
- **Rondel_Luke_3** — EARTH: turned soil in olive green-brown, the
  heaviest and most inward glass of the four.
- **Rondel_John_3** — WATER: a frozen lake in deep water blue, calm
  that outlasts every storm.
- **Rondel_Matthew_3** — AIR: near-weightless pale white-yellow glass,
  a breeze full of light, the lightest of the four.

## persons — 6 plates

Each paragraph is the person's VIRTUE or its ruin stated as one emblem,
on the prism arm's own hue.

- **Rondel_Love** — the source, not the sentiment: a single flame held
  whole in cupped hands, every other arm's colour visible as a facet
  inside it.
- **Rondel_Courage** — a sword raised for someone else, not swung; the
  fighting virtue in its right use, between despair and rage.
- **Rondel_Pride** — a crown lifted higher than the head it belongs to,
  the ascent that ends in the fall (Isaiah's "I will ascend").
- **Rondel_Hatred** — Love's exact negation on the vertical axis: the
  same flame inverted and burning black at midnight.
- **Rondel_Weakness_Fear** — a hand letting a rope go: despair as the
  refusal of Hope, never as cowardice in battle.
- **Rondel_Humility** — a bowed head under a lowered lamp, the descent
  answering Pride's climb.

## one_soul — 6 plates (the SHADOW of each pillar)

The bond's six poisons. Each keeps the pillar's own colour and sours
it — the same glass, gone cold.

- **Rondel_Taking_for_Granted** — a full table nobody looks at, the
  giving received as if owed.
- **Rondel_Fight** — two hands that were joined now braced against each
  other, courage turned on the partner instead of the trouble.
- **Rondel_Jealousy** — Passion's flame seen through a keyhole, the
  fire turned to watching.
- **Rondel_Score_keeping** — a ledger of small marks where a gift
  should be, love keeping the record it is told never to keep.
- **Rondel_Suspicion** — a sentry's lantern at a door that was never
  going to open, Fear conjugated into vigilance.
- **Rondel_Contempt** — a face turned slightly downward and away, the
  bond's deadliest poison drawn as a single angle.

## genesis — 3 plates

The three motions of the creation triangle, drawn INVERTED like their
wheel.

- **Rondel_Creator** — a first light struck over an unlit deep, the
  making that precedes light rather than following it.
- **Rondel_Preserver** — two hands holding a shape steady between a
  making and an unmaking, neither adding nor taking.
- **Rondel_Destroyer** — an ordered form coming apart along its own
  seams, unmaking that waits for the verdict and does not run ahead of
  it.

## council — 6 plates (the OFFICE, not the person)

The Council's six offices as court furniture and instruments — never a
face, since the persons already hold the lancets.

- **Rondel_Judge** — an empty scale at rest, perfectly level, at noon.
- **Rondel_Creator** — a compass opened over dark water, at the darkest
  hour.
- **Rondel_Prosecutor** — an accusing document sealed and presented,
  the instrument that forces a case to be heard.
- **Rondel_Advocate** — an open hand placed between the accusation and
  the accused.
- **Rondel_Preserver** — a keystone held in place, the seat whose whole
  work is continuance.
- **Rondel_Destroyer** — a sentence executed: the same document, now
  struck through.

## character — 8 plates (the FALL of each direction)

Each is the direction's virtue walked one step past its measure. Same
hue as the virtue, one shade harder.

- **Rondel_Tribalism** — one rule for us and another for everyone else:
  a covenant circle drawn closed with everything outside it in shadow.
- **Rondel_Favoritism** — a patron's weight placed on the bond instead
  of the work: a hand on one shoulder while other work waits.
- **Rondel_Self_Worship** — a throne set above the stars, the office and
  the man confused.
- **Rondel_Dogmatism** — a principle kept after it stopped being
  examined: a sealed book on a lectern, never opened.
- **Rondel_Legalism** — the letter of a law outliving its reason: a
  measuring line drawn straight through the thing it was meant to
  protect.
- **Rondel_Mortification** — subtraction continued past anything left
  to subtract: an empty cell with the discipline still running.
- **Rondel_Self_Annihilation** — the correct estimate of one's own worth
  concluded as zero: a figure's outline emptied of its glass.
- **Rondel_Martyrdom** — the self spent on the bond until the spending
  became the point: a house pulled down by the one still inside it.

## vertices — 8 plates (the FALL of each corner)

The Rose's eight corners, each shown by the DEED its paragraph names —
one act, no portrait (the people live in the rose_round badges).

- **Rondel_Submissive_Enabler** — the keeper disappeared into the
  keeping: an outline of a person left inside a devotion still standing.
- **Rondel_Fanatical_Martyr** — a rescue with nobody being rescued: the
  temple coming down at Gaza on rescuer and crowd alike.
- **Rondel_Tribal_Warlord** — the prize taken while the army dies of
  plague: honour with no measure outside itself.
- **Rondel_Complacent_Nepotist** — the map divided by praise: government
  conducted as a test of affection, the watch turned into a chair.
- **Rondel_Cold_Elitist** — the calm speech that explains why the
  governed cannot be trusted with what governs them.
- **Rondel_Messianic_Tyrant** — six hundred chariots turned out into
  water that has already opened for somebody else.
- **Rondel_Puritanical_Zealot** — the ultimatum at the cathedral door:
  the cleansing become an appetite.
- **Rondel_Paralyzed_Purist** — the drawn sword sheathed at the chapel
  on a refinement: reasoning that stays excellent and never acts.

---

## What this sheet does NOT cover — and what still owes a sheet

- **`vertices` has NO ART AT ALL** — neither `primary/colored/` nor
  `circle/colored/` holds a single file, while every other family has
  both. This is NOT a missing prompt: the briefs are written and sealed
  in [Cube Vertex Arm Plates](../../rose_round/vertices_prompts.md),
  which already declares the lancet AND the 1:1 circle for all eight
  corners. What that round owes is generation, not writing — and under
  the dial law above the Rose's Prophecy wheel cannot seat anybody until
  the eight circles exist.
- The **`life` register's** eight ages own one paragraph each, so they
  need no rondel — the badge covers them.
- The **Animals register** of the Ages, still unwired, keeps the
  round-two note its own sheets already carry.
