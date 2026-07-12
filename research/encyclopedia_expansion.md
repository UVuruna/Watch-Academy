# Encyclopedia Expansion

A design + copy spec for the full DOMY Watch Encyclopedia. The owner's
brief: *the Encyclopedia should pull out EVERYTHING interesting about
this clock — not only the logos but the functionality: how and why it
is the way it is; why that color order; why the morning is blue and the
evening red; what twilight is.* Today the Encyclopedia only browses the
symbol art. This document adds the missing half — the instrument itself
— plus three new character sections and a whole new weekday MODE.

Everything below is ship-ready English in the voice of the existing
`Database/symbolism.json` articles (learned, unhurried, astronomy and
myth woven together, the design reasoning always given, not just the
fact). Nothing here modifies code, articles, `SYMBOLISM.md` or
`INSTRUCTION.txt` — it is the copy and the layout the owner can pour
into `app/encyclopedia.py` and the JSON.

## Table of Contents

- [What Changes](#what-changes)
- [A — The Instrument (functionality group)](#part-a)
  - [The 24-Hour Dial](#a-dial)
  - [Solar Rotation and the Hexagram](#a-hexagram)
  - [Twilight](#a-twilight)
  - [The Year Wheel](#a-year)
  - [The Moon Wheel and the Lunations](#a-moon)
  - [Paint and Light](#a-paintlight)
  - [Gold, Silver, Bronze](#a-metals)
  - [The Ring Letters](#a-letters)
- [B — Virtues, Sins, Moods (three new sections)](#part-b)
  - [Virtues](#b-virtues)
  - [Sins](#b-sins)
  - [Moods](#b-moods)
- [C — The Weekdays Mode](#part-c)
  - [Page anatomy](#c-anatomy)
  - [Sample page — Sunday](#c-sunday)
  - [Sample page — Tuesday](#c-tuesday)
- [D — Where the twilight explanation surfaces](#part-d)
- [Implementation notes for app/encyclopedia.py](#impl)

<a id="what-changes"></a>

## What Changes

The Encyclopedia gains a **top-level MODE switch** (a segmented control
above the current title):

- **Topics** — the gallery that exists today, with **two new groups**
  added to the four (Gods / Zodiac / Themes / Religions):
  - **The Instrument** — the eight functionality articles of Part A.
  - **The Inner Wheel** — the three character sections of Part B
    (Virtues / Sins / Moods). *(Alternative name if "Inner Wheel"
    reads too poetic: "The Cross" — for the cross-cure axes that bind
    the three. It could also nest inside the existing Themes group;
    the owner picks.)*
- **The Week** — the new mode of Part C: seven scrollable pages, one
  per weekday, each gathering everything that day owns.

Proposed group name for the functionality articles: **The Instrument**
— it matches the project's own description of itself (an astronomical
instrument, where a slow correct answer beats a fast plausible one).
The runner-up was "The Workings"; "How It Works" felt too much like a
manual and not enough like the rest of the book.

---

<a id="part-a"></a>

## A — The Instrument (functionality group)

Eight articles. Each is drafted below in full, ready to drop into
`Database/symbolism.json` under a new `instrument_articles` block
(`{base}` per entry, same shape as `trio_articles`). The voice matches
the weekday `articles` set: flowing paragraphs, no bullet lists.

<a id="a-dial"></a>

### The 24-Hour Dial

> Every clock you have ever read divides the day in two and makes you
> supply the missing half — is it eight in the morning or eight at
> night? This dial refuses the ambiguity. It carries all twenty-four
> hours on one face, so the single stroke that marks the time can only
> mean one thing. Noon sits at the very top, midnight at the very
> bottom, and the hours run clockwise down the right side through the
> afternoon and up the left through the small hours — 18h due right,
> 06h due left, the whole day laid out the way the sun actually walks
> it.
>
> Because a full turn now takes a full day, the hands change roles. The
> hour hand sweeps the entire circle just once from midnight to
> midnight, moving at a patient fifteen degrees an hour — slow enough
> that its angle alone tells you where you are in the day at a glance,
> high and bright near the top at noon, buried at the bottom at three
> in the morning. The minute hand keeps its ordinary pace, one turn an
> hour. There is deliberately no seconds hand: this is a clock for
> reading the shape of a day, not for timing a race.
>
> The rim is machined like a real instrument. Around the circle run
> exactly 360 marks — one for every degree, because the whole
> twenty-four-hour turn is 360°, which makes each degree worth precisely
> four minutes of time. Twelve white glow-arrows fall on the odd hours,
> and a thirteenth crowns 12h — noon's own arrow, the brightest of all,
> standing directly under the gold tip of the star. Eleven short gray
> ticks take the remaining even hours, midnight quietly among them. The
> hours filled, the minute divisions fill the gaps: forty-eight medium
> marks at the thirds of each hour and two hundred eighty-eight fine
> ones between them. Thirteen and eleven make the twenty-four hours;
> forty-eight and two hundred eighty-eight make the three hundred
> thirty-six minute marks; all of it sums to 360, one clean tooth per
> degree.
>
> The reward for the strangeness is a clock you read like a sundial
> made honest. When the hour hand stands straight up, the sun is at its
> height; when it hangs straight down, you are at the dead middle of the
> night. The colored arc, the twilight bands, the weekday star and the
> season marker all hang on this one frame — twenty-four hours, top to
> bottom, the day drawn as it is lived.

<a id="a-hexagram"></a>

### Solar Rotation and the Hexagram

> The six-pointed star at the center is not decoration and it does not
> sit still. Its top vertex is a pointer, and what it points at is
> **true solar noon** — the actual instant the sun crosses the meridian
> and stands at its highest, which is almost never the 12:00 your phone
> shows. So on most days the star is tipped a few degrees off vertical,
> and that tilt is a real measurement, not a wobble.
>
> Clock noon and sun noon disagree for three honest reasons, and the
> star sums all three. You usually live east or west of the exact line
> your time zone is named for, which slides your solar noon earlier or
> later. The Earth's tilted, elliptical orbit runs the sun a little fast
> or slow against the clock through the year — the equation of time,
> worth up to a quarter hour either way. And half the year daylight
> saving shoves the whole civil clock an hour off the sun. The star
> takes the day's true noon, measured in seconds since local midnight,
> and rotates by `(noon_secs − 43200) / 240` degrees — a positive,
> clockwise turn whenever solar noon falls after 12:00 (deep in the
> western edge of a zone, or under summer time).
>
> Everything mounted on the star turns with it. The weekday bodies ride
> in diamond slots that rotate as one rigid piece, so the day's planet
> is always correctly placed relative to the real sun, not the
> bureaucratic one. The top vertex therefore does double duty: it is the
> noon pointer and it is the anchor from which the whole symbolic wheel
> hangs. Look at the star's lean and you are reading, directly off the
> glass, how far your civil clock has drifted from the sky.

<a id="a-twilight"></a>

### Twilight

> Day does not switch to night; it dissolves into it. After the sun's
> disc drops below the horizon the sky stays lit for a while by
> sunlight bent and scattered over the edge of the world, and that
> lingering glow is twilight. Astronomers cut it into three bands by how
> far the sun has sunk. **Civil twilight** runs from the horizon to 6°
> below it — bright enough to walk, read a little, see the brightest
> stars. **Nautical twilight** reaches to 12°, the old depth at which a
> sailor could still fix both the horizon line and the stars for a
> sextant sight. **Astronomical twilight** ends at 18°, past which the
> last faint wash of sun is gone and the sky is truly dark. DOMY draws
> the civil band — the one a person actually notices, the pale margin
> before sunrise and after sunset when there is light but no sun.
>
> Those 6° take longer than you would guess. If the sun fell straight
> down it would cross 6° of altitude in about twenty-four minutes, but
> it almost never falls straight down. Away from the equator the sun
> sets at a slant, sidling toward the horizon rather than dropping onto
> it, so it spends far longer in each degree of depression — at
> mid-latitudes civil twilight lasts roughly 37 minutes. On this dial,
> which turns a steady fifteen degrees per hour, 37 minutes of time is
> 9.25° of arc, a band you can see with your eye. Push the clock toward
> the poles and the slant grows shallower still: the band stretches to
> an hour, then hours, and in high summer the sun may never sink the
> full six degrees at all — which is exactly why the dial's twilight
> arcs swell so dramatically when you move it north to Tromsø.
>
> The colors are physics, not mood-painting. Sunlight scatters off the
> air more strongly the shorter its wavelength — blue far more than red,
> the Rayleigh law that makes the daytime sky blue in the first place.
> At twilight the sun's direct light must graze the whole thick edge of
> the atmosphere, an enormously long path that scatters the blue clean
> out and lets only the reddened remainder through — the same reddening
> that turns the low sun itself orange and, laid over haze and dust,
> browns the western sky at dusk. The morning's cool blue has a second,
> subtler cause: high in the atmosphere ozone absorbs in the
> yellow-orange (its Chappuis band), so the deep-twilight light that has
> travelled farthest through it comes back tinted blue — the painters'
> and photographers' "blue hour."
>
> Both ends of the day own both effects, but the dial gives each its
> signature: the dawn band wears blue on the left, at the 06h sunrise
> arm, and the dusk band brown on the right, at the 18h sunset. It is
> honest to the light — a
> waking sky leads with the blue hour, an ending one leads with the
> red — and it rhymes with the clock's whole emotional canon, where the
> pre-dawn arm is Calm and Hope and the sunset arm is Passion and
> Longing.

<a id="a-year"></a>

### The Year Wheel

> Behind the day sits a second, far slower clock: a marker that creeps
> once around the same face in a year, standing at the top at midsummer
> and at the bottom in the dark of the December solstice. Its four
> cardinal points are the hinges of the year — the two solstices top and
> bottom, the two equinoxes left and right — and they are not
> approximated. Each is placed on the real astronomical instant, read
> from the bundled ephemeris of season crossings, so the equinox marker
> lights up on the exact day the sun crosses the equator.
>
> Yet every season is drawn as an equal quarter. Real seasons are
> unequal — northern summer runs several days longer than winter because
> the Earth moves slower when it is farther from the sun — but on this
> wheel each of the six anchor-to-anchor spans is stretched or squeezed
> to fill exactly 90°, so the equinoxes land precisely at 90° and 270°
> and the solstices exactly at top and bottom. Between any two anchors
> the marker moves at a constant rate (a straight, piecewise-linear
> interpolation); it simply runs a hair faster through the longer
> seasons and slower through the shorter ones to keep the corners square.
>
> The choice is the owner's, and it is a legibility choice: a viewer
> should be able to read "we are a third of the way through spring" off
> the angle without a calendar, and equal quarters make that possible
> while the corners stay astronomically true. The tropical zodiac rides
> this same wheel — twelve 30° signs anchored on the real season
> instants, Cancer opening at the summer solstice at the very top,
> Capricorn at the winter solstice below — so the ring of signs inherits
> the wheel's honest hinges and its tidy geometry at once.

<a id="a-moon"></a>

### The Moon Wheel and the Lunations

> A third marker keeps the moon. It rides the year wheel at the moon's
> own position and carries the current phase — new, waxing, full, waning
> — with a soft glow at each of the four principal phases as they fall.
> The moon is the fastest of the dial's slow hands, closing its cycle of
> phases every 29.53 days, and its light on the face is always the sun's
> light handed on: the wheel shows you, at a glance, where in its month
> the moon stands and how much of the night it will own.
>
> DOMY also numbers the moons of the year, and the rule is exact. The
> year's **first Moon is the first New Moon that falls on or after
> January 1**; the second is the next, and so on. The days at the very
> start of January, before that first new moon, do not belong to Moon
> One — they belong to the **previous** year's last lunation, its
> twelfth or thirteenth, still running out its cycle across the
> New Year. A lunation, in other words, is counted by the year its new
> moon opens in, not by the calendar days it happens to touch.
>
> Which is why a year has twelve moons or thirteen. Twelve lunar months
> run about 354 days — some eleven days short of the solar year — so the
> new moons drift steadily earlier each year until, roughly once in
> three years, a thirteenth new moon squeezes in before December is out.
> Most years therefore close on their twelfth Moon; about one in three
> reaches a thirteenth (the "blue moon" years of folklore). The dial
> simply follows the sky: it starts counting at the first new moon of
> January and lets the arithmetic of an eleven-day shortfall decide
> whether the tally ends at twelve or thirteen.

<a id="a-paintlight"></a>

### Paint and Light

> Every colored palette on the dial comes in two readings, and the two
> are a small history of how humanity understood color. Before Newton,
> color meant PIGMENT: yellow, red and blue were the primaries, and
> orange, green and purple were mixed from them — the painter's wheel of
> six, the world of matter. After Newton split a sunbeam with a prism, a
> second world opened: red, green and blue LIGHT, with cyan, magenta and
> yellow between them — six hues again, the world of energy. DOMY's two
> palette styles are exactly these two wheels.
>
> Switching between them keeps every positional meaning and only
> re-tunes the hues. The arm that means Calm stays at the pre-dawn
> hour whether it is painted the ancients' deep pigment blue or lit as
> the prism's pure primary; Sorrow stays at midnight, but its mourning
> purple becomes magenta — the one color that lives in no rainbow,
> existing only where the two ends of the spectrum are joined by the
> eye. The most telling case is the center. In paint, the six arm hues
> pile together into mud, and the white-gold Sun at the hub is the one
> shade a painter can never mix — so it stays empty of color, the
> unmixable source. In light, the same six beams thrown inward SUM back
> to white, and the Sun is vindicated: it is literally the sum of its
> own dial. Same week, same meanings, two ways of seeing.

<a id="a-metals"></a>

### Gold, Silver, Bronze

> Alchemy gave each of the two great lights a metal — **gold to the Sun,
> silver to the Moon** — and the dial keeps the pairing where it
> belongs. On the star, the top tip may be crowned in gold and the
> bottom tip in silver: the day metal above at noon, the night metal
> below at midnight. These are accents of TIME, not colors of any arm —
> they mark the two poles of the day rather than a mood or a virtue.
>
> A third metal, **bronze**, is a matter of finish rather than symbol.
> Several of the owner's art sets — the Greek and Norse gods, the guild
> professions, the ring letters — are drawn on bronze plate, and each
> can be worn as bronze (the art exactly as struck), as gold, or as
> silver. The gold and silver looks are computed live: a warm-hue
> detector finds only the bronze pixels of a medallion and shifts them
> toward gold or cool silver, leaving the gray stone and engraving
> untouched, so the plate changes metal without the scene changing.
> The ring letters follow the same three-metal logic — a gold master
> and a pre-rendered silver, with bronze a straight warm multiply — and
> on the ring the triangle of one metal is always set against its
> counter-metal, so the six-letter Seal reads as a true two-tone
> hexagram.

<a id="a-letters"></a>

### The Ring Letters

> Four letters ride the outer ring of the standard dial and spell the
> clock's name: **D, O, M, Y**. The O is written as the Greek **Ω**
> (omega), which looks like the reason it is there — but the real reason
> is hidden in the numbers, and once seen it cannot be unseen. Each of
> the four is a Greek letter, and each sits at the hour equal to its
> place in the Greek alphabet. **Δ** delta is the 4th letter, and it
> stands at 4h. **M** mu is the 12th, and it crowns 12h at the top.
> **Y** upsilon is the 20th, and it marks 20h in the evening. **Ω**
> omega is the 24th and last, and it takes the bottom, 24h, midnight —
> the end of the alphabet at the end of the day. The brand name and the
> clock face are the same object: DOMY is four Greek ordinals that each
> point to their own hour.
>
> That is why omega closes the word and the day together — the last
> letter guarding the darkest hour — and why the top of the ring is an
> M: mu, twelfth of twenty-four, exactly halfway, standing where noon
> stands. The trio of virtues reads straight off these letters, too:
> Faith points up from the M at 12h, Love closes the word at the Y at
> 20h, Hope waits at the D at 4h before the dawn.
>
> The feminine variant ring, **MORPH**, is built on the same secret. Its
> glyphs are mu (12th) at 12h, pi (16th) at 16h, omega (24th) at 24h and
> eta (8th) at 8h — every letter again seated at its alphabetical hour,
> a different word written in the same hidden clock. The number ring is
> the plain confession of the trick: it simply prints 12, 16, 20, 4 and
> 8 at those hours and keeps omega at 24, the one hour whose letter has
> always been its number.

---

<a id="part-b"></a>

## B — Virtues, Sins, Moods

Three new sections, each an **eight-entry list**. The dial has seven
bodies, but **Sunday is the dual day**: the Sun sits in the center as
one figure with two faces — the servant-king, black and white in one
body — so the center carries two of everything. Every list below
therefore has eight items, Sunday counted twice (the bright Ruler face
and the dark Servant face). Each entry gets a 1–2 paragraph brief;
the logo art arrives separately.

The three sections are the three character-layers that ride the same
arms as the colors: the color is the **mood**, and under it sit the
**virtue** and its shadow the **sin**. Reading a single arm top to
bottom — hue, mood, virtue, vice — is reading one hour of the day as a
whole small person.

<a id="b-virtues"></a>

### Virtues

Eight virtues, one per body, the Sun twice (Ruler · Servant).

| # | Virtue | Body / Day | Cured vice (across the dial) |
|---|--------|-----------|------------------------------|
| 1 | Justice | Sun · Ruler (Sunday) | cures the Servant's Servility (inside the center) |
| 2 | Humility | Sun · Servant (Sunday) | cures the Ruler's Pride (inside the center) |
| 3 | Serenity | Moon (Monday) | quells Mars' Wrath |
| 4 | Courage | Mars (Tuesday) | cures the Moon's Fear |
| 5 | Wisdom | Mercury (Wednesday) | curbs Jupiter's Excess |
| 6 | Generosity | Jupiter (Thursday) | cures Mercury's Greed |
| 7 | Love | Venus (Friday) | dissolves Saturn's Envy |
| 8 | Patience | Saturn (Saturday) | heals Venus' Jealousy |

> **Justice** — the virtue a ruler PRACTICES. It is Solomon dividing
> the child, the heart weighed against Ma'at's feather, the sun that
> falls on everyone alike: light and law that do not play favorites.
> Justice is the bright face of the center's calling, the Ruler's own
> discipline — and it is a cure, though it never leaves home. Crosswise
> inside the center it straightens the Servant's Servility: what is
> right is exactly what a bent spine needs.

> **Humility** — the virtue that SAVES the ruler. The one who stands at
> the middle of everything is the one most tempted to believe the light
> is his; humility is the source remembering it is not the whole.
> Amaterasu drawn from her cave by her own reflection is its oldest
> picture — the sun shown that it is a light among lights. It is the
> Servant's grace, and it cures the Ruler's Pride across the center's
> inner axis: the dial's one seat that is both its own disease and its
> own medicine.

> **Serenity** — the Moon's calm, the settled surface of a mind at
> peace in the dark. It rules the hour before dawn, when there is
> nothing left of yesterday and nothing yet of tomorrow; whoever is at
> peace then is truly at peace. Its work is a cure sent across the dial:
> the night-watch's stillness quells the Wrath burning on Mars' arm —
> the calm hand laid on the raised one.

> **Courage** — Mars' fire pointed the right way. The same flame that
> can burn a house down tempers the steel; courage is that fire
> mastered, the soldier who holds the line rather than the one who
> loses his temper. It answers the Moon straight across the wheel: the
> day's nerve reaches over the center to cure the Fear that pools before
> dawn. The warrior steadies the frightened.

> **Wisdom** — Mercury's clear sight, the mind that weighs the day
> honestly at midnight because no one is watching. It is Odin's eye
> given for a drink at Mimir's well, understanding bought at a price.
> Its cure travels the dial's whole vertical spine: from the bottom it
> curbs Jupiter's Excess overhead — knowing, at the height of the feast,
> when enough is enough.

> **Generosity** — Jupiter's open hand, the jovial king's table spread
> for everyone. It is faith practiced with the hands, giving before any
> return is proven. Its cure pours straight down the dial's spine to the
> midnight arm: the full hand answers Mercury's Greed, the giving top
> curing the grasping floor.

> **Love** — Venus' virtue and the greatest of the three theological
> virtues, the one word that belongs both to the seven pairs and to
> Faith-Hope-Love. It is passion given patience enough to become form —
> the artist's work, and the lover's. Across the dial it dissolves
> Saturn's Envy: warmth loosening the cold grip on what the neighbor
> has.

> **Patience** — Saturn's slow art, learned from a planet that takes
> thirty years to close one circle. It is the farmer who sows and waits
> and does not stare too long at the next field. Its cure crosses to the
> evening arm and heals Venus' Jealousy — insecurity waited out, not
> argued with; the two slow arts, waiting and loving, mending each
> other.

<a id="b-sins"></a>

### Sins

Eight vices, the dark face of each arm, the Sun twice (Ruler · Servant).
Each is cured by the virtue directly across the dial — the arm opposite
is always the medicine.

| # | Sin | Body / Day | Cured by (across the dial) |
|---|-----|-----------|----------------------------|
| 1 | Pride | Sun · Ruler (Sunday) | the Servant's Humility (inside the center) |
| 2 | Servility | Sun · Servant (Sunday) | the Ruler's Justice (inside the center) |
| 3 | Fear | Moon (Monday) | Mars' Courage |
| 4 | Wrath | Mars (Tuesday) | the Moon's Serenity |
| 5 | Greed | Mercury (Wednesday) | Jupiter's Generosity |
| 6 | Excess | Jupiter (Thursday) | Mercury's Wisdom |
| 7 | Jealousy | Venus (Friday) | Saturn's Patience |
| 8 | Envy | Saturn (Saturday) | Venus' Love |

> **Pride** — the self at the center of everything, the oldest sin
> because it is the center's own. The star that gives all light
> mistaking itself for the light's owner: Phaethon seizing the reins,
> the king who forgets he serves. Its only cure is Humility, and the
> cure never leaves the center — the middle heals itself or nothing
> does.

> **Servility** — humility curdled. Where the Servant's grace is a spine
> bent in service of the truth, servility is a spine with no bones at
> all, serving the throne instead of what is right, faithful sunrise
> gone slack into mere routine. Its cure is the Ruler's own Justice,
> reaching crosswise inside the center: what is right straightens what
> has gone limp.

> **Fear** — the Moon's dark face, older than any list of sins. It is
> the same unlit night that, once accepted, is Serenity; dreaded, it is
> the oldest terror, the frightened mind waking in the small hours. Its
> full cure stands straight across the dial: the Soldier's Courage
> reaches over the center to steady it.

> **Wrath** — Mars' fire loosed on its own side, the shout on the war
> god's face and the lion on his shield read as ruin instead of
> defense. It is courage with no hand on the reins. Its cure comes from
> the pre-dawn arm: the Moon's Serenity, the calm that banks a furnace
> before it spills.

> **Greed** — Mercury's shadow, the merchant's cleverness turned to mere
> counting; the same mind that understands the world begins only to
> tally it. It grasps upward. Its cure falls the whole height of the
> dial: Jupiter's Generosity, the open hand answering the closed one.

> **Excess** — Jupiter's vice, the royal table that overflows, the
> gluttony of a king who cannot stop giving or taking past the point of
> sense. It is generosity with no floor. Its cure rises from the
> opposite pole: Mercury's Wisdom, the deep mind teaching the high hand
> when to stop reaching.

> **Jealousy** — Venus' shadow, not love's opposite but love's fear: the
> dread of losing what is loved, the mirror where comparison begins.
> Love that has started to grip what it should only warm. Its cure
> crosses from the morning arm: Saturn's Patience, insecurity outwaited
> rather than argued.

> **Envy** — Saturn's bitter green, the oldest failure of those who
> wait: the covetous glance at the neighbor's richer field, Loki's
> grudge against Baldr. It is patience gone sour. Its cure reaches from
> the evening: Venus' Love, warmth dissolving the cold arithmetic of
> what someone else has.

<a id="b-moods"></a>

### Moods

Eight moods — the colors read as feeling. Six ride the arms as the hue
of their hour; the center carries two, the sky's own pair. The moods
breathe in opposites: Joy faces Sorrow across the dial, Zeal faces
Calm, Passion faces Renewal.

| # | Mood | Body / Day | Hour / color |
|---|------|-----------|--------------|
| 1 | Glory | Sun · Ruler (Sunday) | the sun at full noon (white-gold) |
| 2 | Eclipse | Sun · Servant (Sunday) | the hour the king's light fails |
| 3 | Calm | Moon (Monday) | 4h, pre-dawn blue |
| 4 | Zeal | Mars (Tuesday) | 16h, afternoon orange |
| 5 | Sorrow | Mercury (Wednesday) | midnight, mourning purple |
| 6 | Joy | Jupiter (Thursday) | noon, yellow |
| 7 | Passion | Venus (Friday) | 20h, evening red |
| 8 | Renewal | Saturn (Saturday) | 8h, morning green |

> **Glory** — the bright mood of the center, the sun at its full height:
> the day given more than it asked for, the king's light at its widest.
> It is the white-gold blaze from which every arm color is only a piece
> broken off. Glory is not one hour but the sum of all of them seen at
> their best.

> **Eclipse** — Glory's dark twin, the hour the king's light fails. Not
> a color but its absence: Amaterasu sealed in the cave and the world
> gone dark, the sun the sky can stage against itself. It is the
> center's warning that the source, too, can be shadowed — and, like the
> cave, it opens from the inside.

> **Calm** — the Moon's blue, the still and moonlit hour before dawn,
> the temperature of a world asleep. It rules 4h because that is where
> calm is earned: nothing left of yesterday, nothing yet of tomorrow,
> only borrowed silver light. The phlegmatic hour of the old humors.

> **Zeal** — Mars' orange, the ember of the working afternoon. Not
> noon's blaze and not evening's blood-red but the fuel-fire of effort,
> the second wind. Zeal rules 16h because that is when a task is won or
> lost: morning's freshness spent, evening's rest not yet earned, only
> the stubborn ember carrying the work to its end.

> **Sorrow** — Mercury's purple, midnight, red mourning dissolved in
> blue stillness. Not despair but depth: the mind's hour, when the day
> is dead and tomorrow unborn and thought runs on alone. The hour of
> honest accounting, kept by the god who guided souls across the last
> border.

> **Joy** — Jupiter's yellow, noon, the day's own generosity: the most
> light, the most warmth, the peak. "Jovial" means, literally, "of
> Jupiter," and the top of this dial is where the star points at true
> solar noon. Joy rules the crown because the crown is the hour the
> world is handed more than it needs.

> **Passion** — Venus' red, the evening, the sky turned blood-red as the
> evening star opens over the sunset. It rules 20h because evening is
> when the day stops demanding and starts desiring: the work lets go and
> what remains is what one actually loves. The reddest hour on the wheel.

> **Renewal** — Saturn's green, the morning, dew and growth on turned
> soil. The paradox of the wheel — the slowest planet given the freshest
> hour — is its whole point: no body knows better than Saturn that
> mornings return. Renewal rules 8h, the week's day of rest keeping that
> hour on behalf of all the others; whatever was buried in the dark
> comes up green.

*(The Compass pointer adds two more sky-moods on the dawn/dusk arms —
**Hope** at sunrise cyan and **Longing** at sunset orange, true
opposites, one facing what comes and one what has passed. They belong
to the eight-armed extension rather than the core eight, and can be
noted at the foot of this section rather than counted in the list.)*

---

<a id="part-c"></a>

## C — The Weekdays Mode

The owner calls this the important one. **The Week** is a second
Encyclopedia mode: seven scrollable pages, one per weekday, in week
order Sunday → Saturday. Where the Topics mode slices the dial by
LAYER (all the gods together, all the signs together), the Week mode
slices it by DAY — each page gathers everything a single day owns and
weaves it into one reading: its planet and the planet's glyph, its arm
color and mood, its virtue and vice and the partner day that cures
them, its profession, the gods it wears across every mythology, its
alchemical metal and its Japanese element.

The point is connection, so the copy is flowing prose, never a table of
attributes. The images are curated, never dumped: eleven themes ship a
medallion for each day, but a page that showed all eleven would be a
contact sheet, not an article. Each page earns four to six images, no
more, chosen for story and variety.

<a id="c-anatomy"></a>

### Page anatomy (shared skeleton, all seven)

A single vertical scroll, everything centered and rescaling with the
window like the current article blocks:

```
📄 Weekday page
  🖼️ HERO — the planet portrait (the "planets" body art), large,
       with the day name + planet glyph as the title and a small
       arm-color chip beside it
  📝 Opening paragraph — body, arm, hour, color, mood (what the day
       IS on the dial)
  🖼️ THE FACES — a curated 2×2 (or 1×4 on wide windows) of medallions:
       the day's THREE-to-FOUR strongest mythic/among-themes portraits,
       not all of them
  📝 The mythology paragraph — the gods woven together, the day's
       religion(s) named in passing
  🖼️ THE CALLING & THE METAL — a paired row: the profession badge
       (colored, in the arm hue) beside the alchemy metal medallion
  📝 The character paragraph — profession, virtue, vice, the cross-cure
       partner day, the Japanese element
  📝 Closing line — where the day stands to its opposite on the wheel
```

**Curation rules (what earns a spot):**

- **Always** the planet portrait as the hero — it is the literal thing
  on the dial, and the one image every viewer will recognize.
- **Always** the profession badge and the alchemy metal — one crest,
  one still-life; together they give the page visual variety against a
  row of god-faces.
- **Three or four god medallions**, chosen per day for how well that
  tradition tells THIS day, and for spread across the sets — favor the
  Greek (the dial's root), the owner's home Slavic, and whichever of
  Egyptian / Norse / Japanese is most iconic for the day. Include the
  Japanese medallion when its element scene (Fuji, the great wave, the
  sacred pine) carries the element point visually.
- **Skip** the planet-signs set (redundant with the glyph in the
  title), skip whichever religion set is the weaker portrait, and skip
  any medallion that only repeats what a stronger one already says.
- **Sunday is the exception** — the dual day gets the yin-yang framing
  and may run to six images to seat both faces (see below).

<a id="c-sunday"></a>

### Sample page — Sunday (the dual day)

**Title:** Sunday · the Sun · ☉  — color chip: white-gold

**Hero image:** the Sun portrait (seething white-gold plasma).

**Curated faces (2×3, the one page that earns six):** Helios (Greek),
Ra (Egyptian), Amaterasu / Nichiyōbi (Japanese), Dažbog (Slavic) — four
sun-kings — plus the two that carry the duality: the Ruler · Servant
profession crest and the Gold medallion. *(Norse Sól and Mithraism sit
this page out; four solar faces already make the point, and the page
needs room for the two-faced center.)*

> Sunday does not sit among the days — the days sit around Sunday. Every
> other weekday takes an arm of the star; the Sun takes the center,
> white-gold, because it is not one color among six but the sum of all
> of them. The six arm-hues are its light decomposed, the star is the
> prism, and Sunday is what goes into it. It rules no single hour
> because it rules all of them: the Joy of noon, the Passion of evening,
> the Calm before dawn are one light seen at different angles, and the
> center is where they all still belong to each other. That is why the
> Sun keeps no colored arm and no single mood, but the two the sky
> itself stages — Glory at full noon and Eclipse when the light fails.
>
> No pantheon could resist fusing this day's god with kingship, and the
> page wears four of them. Helios drives the quadriga and sees
> everything done under the open sky — witnesses swore their oaths by
> the one nothing escapes. Ra sails the day-barque from horizon to
> horizon and dies into the Duat each night to be reborn at dawn, sun
> and king and temple in one body. Amaterasu, from whom Japan's emperors
> claim descent, shut herself in the cave of Ama-no-Iwato and left the
> world in the dark until her own reflection in a mirror drew her out —
> the day called Nichiyōbi, sun-day, its very glyph 日 the one that opens
> the name of Japan. And Dažbog, the giving sun of the owner's home
> mythology, pours grain and gold and warmth from the center and keeps
> nothing back — the Slavs called themselves his grandchildren. Four
> faiths sit on this day for one reason each: Christianity because
> Constantine made the day of the Sun the day of rest, and Mithraism
> underneath it, whose *dies Solis* crowned the Unconquered Sun through
> seven planetary grades.
>
> The center's calling is the Ruler — but it is a DOUBLE calling, one
> figure with two faces, the dial's own yin-yang. As the bright Ruler
> the Sun practices Justice, the light that falls on everyone alike, and
> is stalked by Pride, the self at the middle mistaking itself for the
> source of the light. As the dark Servant it practices Humility, the
> source remembering it is not the whole, and is stalked by Servility,
> faithful sunrise gone slack into mere routine. And here the cure that
> everywhere else crosses the dial stays home: the Servant's Humility
> cures the Ruler's Pride, the Ruler's Justice straightens the Servant's
> Servility, an angel and a devil on the same shoulders, each the
> other's medicine. Its metal is Gold, the incorruptible, laid on as
> leaf and never mixed — the unmixable center made a goldsmith's fact —
> crowning the star's top tip at noon. Its element, on the Japanese
> week, is not one of the five but the sun itself, 日, heralded by
> Yatagarasu the three-legged crow who rides the solar disc.
>
> So Sunday is the one seat on the wheel with no opposite to answer to,
> because it is its own opposite: king and servant, glory and eclipse,
> the disease and the medicine in a single white-gold body. Every other
> day is cured from across the dial. Sunday is cured from within.

<a id="c-tuesday"></a>

### Sample page — Tuesday (Mars, an ordinary day)

**Title:** Tuesday · Mars · ♂  — color chip: ember orange

**Hero image:** the Mars portrait (rust globe scarred by its great
canyon).

**Curated faces (2×2):** Ares (Greek), Tyr (Norse), Svetovid (Slavic),
Kayōbi / the fire-day kabuto (Japanese). *(Egyptian Montu and the two
war-religions are named in the prose but sit out; Ares and Tyr already
carry the classical pair, Svetovid brings the owner's home set, and the
Japanese fire-scene earns its place by showing the element.)* The
paired row below adds the Soldier crest (in orange) and the Iron
medallion.

> Tuesday belongs to the red planet, and the portrait is honest about
> the name: Mars is the color of iron oxide and dried blood, a vast dark
> canyon torn across its equator so the god of war actually looks
> wounded. Yet its arm at 16h is not red but ember ORANGE, because the
> arm colors belong to the hours, and 16h is the working afternoon —
> the mood of Zeal. Orange is fire domesticated: past noon's blaze, far
> from evening's blood-red, the fuel-fire of effort. Zeal rules the
> afternoon because that is where work is won or lost — morning's
> freshness spent, evening's rest not yet earned, only the stubborn
> ember carrying a task to its end. Mars, the planet of drive, is
> exactly the body to stoke it.
>
> The war gods gather thickest on this day, and the page wears the ones
> who complicate the rage. Ares is battle whole — the Greeks gave him a
> planet and a weekday while keeping him at arm's length; in the Iliad
> Zeus calls him the most hateful of the gods, and the courage belongs
> to the soldier who masters him. Tyr corrects the picture: the
> one-handed Norse god of war AND justice, who laid his own right hand
> in the wolf Fenrir's jaws to seal a binding oath — courage in the
> service of order, the reason the day carries Freemasonry, the Craft
> sworn on oaths and built with a soldier's discipline. Svetovid, from
> the owner's Slavic set, keeps four faces and a white divining horse at
> Arkona, the war-arm's watchman facing every direction at once. And on
> the Japanese week the day is Kayōbi, fire-day: its planet 火星 Kasei is
> literally the "fire star," and its medallion crosses two katana under
> a horned kabuto in a wreath of flame — for fire, like Mars, is birth
> and war in one, the element that tempers steel and burns the house
> down with the same heat. Beneath these the alternate faith is
> Zoroastrianism, whose sacred fire Atar guards *asha*, the truth that
> is the courage of the flame against the lie; Montu, Thebes' falcon war
> god, stands with them unshown.
>
> The calling is the Soldier, and no profession wears its virtue and
> vice so plainly, because they are the body's own: Courage, the flame
> that defends, and Wrath, the same flame let loose on its own side. A
> soldier is precisely that pair walking. Its metal is Iron — the
> blade, the armor, and the iron that genuinely runs red in the blood,
> so Mars flows breath by breath in every vein. And its cure hangs
> straight across the dial at 4h, on Monday's arm: the Moon's Serenity
> reaches over the center to quell Mars' Wrath, while Mars sends Courage
> back down the same axis to cure the Moon's Fear. The warrior and the
> night-watch physician heal each other — day's nerve steadying night's
> unease, night's calm banking day's fire.
>
> That axis is the whole of Tuesday's place on the wheel. It is an
> ordinary working day, an arm and not a center, and it knows exactly
> where its medicine lives: not within, as Sunday's does, but on the far
> side of the dial, in the still blue hour before dawn. Mars burns; the
> Moon cools it. Courage and Calm are one line drawn through the center
> of the day.

---

<a id="part-d"></a>

## D — Where the twilight explanation surfaces

The civil-twilight material lands in **two** places, and they already
agree — the deep explanation is new, the naming already exists:

1. **The Encyclopedia — "Twilight" article** (Part A above): the full
   account. Civil = the Sun 6° below the horizon; nautical 12° and
   astronomical 18° named for completeness; why 6° takes ~37 minutes =
   9.25 dial degrees at mid-latitudes (the oblique sun, the dial's
   15°/hour); and the color physics — Rayleigh scattering, the long
   low-sun path reddening the direct beam, the ozone Chappuis blue of
   the morning "blue hour." This is where a curious owner-viewer goes
   to learn *what twilight is*.

2. **The live dial's twilight hover** (already shipped — do not
   duplicate, just cross-reference): the pale bands on the face already
   name themselves. The morning band's hover reads it as the **civil
   dawn** — "the sun is below the horizon but the sky already carries
   light" — and gives both boundary times (when dawn begins, when the
   sun appears); the evening band's hover is the matching dusk. The
   day-length legend labels the two bands **Morning Twilight** and
   **Evening Twilight** and the extended span **With Twilight**. So the
   dial already *names* the civil band at the point of use; the
   Encyclopedia article is the one place that *explains* it. The
   Encyclopedia entry should open with a one-line pointer back to the
   dial ("the pale band the dial calls civil dawn is drawn here") so the
   two never drift apart.

---

<a id="impl"></a>

## Implementation notes for `app/encyclopedia.py`

Kept short — copy and layout are the deliverable above; this is only the
wiring.

- **Mode switch.** Add a segmented control (two `QToolButton`s or a
  `QButtonGroup`) above `self._title`: **Topics** (the current gallery)
  and **The Week**. Store `self._mode`; route `_show_topics()` /
  `_show_week()` from it. The `← Back` button already exists — in Week
  mode it returns to the mode's index page (or is hidden if Week opens
  directly to the seven-page scroll).
- **Two new topic groups** in `_TOPIC_GROUPS`: `("The Instrument",
  (...8 functionality keys...))` and `("The Inner Wheel", ("virtues",
  "sins", "moods"))`. The grid already wraps at 4 per row (`index // 4`,
  `index % 4`), so eight instrument cards fill two rows without layout
  changes.
- **New article kinds** in `_article_text()`: extend the `kind` switch
  with `"instrument"`, `"virtue"`, `"sin"`, `"mood"` reading from new
  `SymbolismRepository` accessors over new JSON blocks
  (`instrument_articles`, `virtue_articles`, `sin_articles`,
  `mood_articles`) — each `{base}`-shaped like `trio_articles`, no
  per-style variants. The functionality articles carry no entity image;
  the virtue/sin/mood entries take their logo art when it lands
  (`images` tuple, empty until then — the existing `if images:` guard
  already handles the no-art case).
- **Accents.** Reuse the highlight pass: virtues/sins/moods each accent
  their body's hue (`BODY_ACCENT_HUES`), so the canon terms glow like
  the dial legends; functionality articles can pass empty accents.
- **The Week mode** is a new render path, not a topic. Data: a
  `WEEK_PAGES` table keyed by body in Sunday-first order, each row
  pulling the day's existing pieces (planet art, curated medallion
  paths, profession + alchemy medallions, the arm color chip) plus a
  new `week_articles/<body>` `{base}` text. Layout reuses the existing
  block-per-entry scroll and `_rescale()` — the only new widgets are the
  hero image, the curated `QGridLayout` "faces" block (2×2 / 1×4 by
  width) and the paired calling+metal row. Cap the faces grid at the
  curated set; do not iterate all eleven themes.
- **No hardcoded strings on the dial side.** Page titles, group names
  and the mode labels join the translation corpus the way `guide_page/N`
  and the topic titles already do, so the whole expansion translates
  through the active overlay like everything else.
