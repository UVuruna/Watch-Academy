# Encyclopedia

**Script:** [Encyclopedia (script)](encyclopedia.py)

## Purpose
The article BROWSER (owner spec 2026-07-12; menu Encyclopedia… below
Time Travel…): every legend readable without hovering the dial, on two
screens —

1. **Topics** — a gallery in the owner's GROUPS (`_TOPIC_GROUPS`):
   The Clock, Gods, Zodiac, Themes, Religions, Animal Societies and
   The Inner Wheel (Virtues, Sins, Moods and THE TWO TRIANGLES — the
   Judas–Lucifer scale of self, owner 2026-07-13; its badge art is
   wired ahead of landing) — EVERYTHING centered (owner 2026-07-13: headers
   and card rows alike) and the cards RESPONSIVE: `_rescale_topics`
   grows/shrinks the icons with the window between
   `ENCYCLOPEDIA_TOPIC_ICON_MIN/MAX_PX`; only below the minimum does
   the scrollbar take over.
2. **Articles** — a SLIDER (owner plan round E, 2026-07-14): one entry
   per page, ← Previous / Next → wrap around with a counter between
   them; the chrome wears the shared gradient pills ([UI
   Style](ui_style.md)) — ⌂ Home top-left back to the gallery,
   ⬇ Download top-right saves the open entry's image(s) and text.
   The entity image(s) — Astrology shows the sign LOGO and its
   CONSTELLATION side by side, every Sunday RULER/SERVANT pair stands
   side by side on THEME pages, while the WEEK pages STACK each pair
   (owner 2026-07-14: Ruler on top, its Servant directly under,
   themes as columns) — then the NAME as a bold title and the full
   base article, translated through the active overlay and with the
   canon terms highlighted exactly like the dial legends (virtues
   blue, vices red, moods yellow, the entity's own arm hue), the
   `[[Subhead]]` markers drawn as centered bold headings hugging
   their paragraph.

**The Clock group split (owner 2026-07-16, ROADMAP queue #10):** the one
Seasons topic became THREE — **Moon** (the lunations), **Seasons** (the
quarters, the tropics' halves and the meteorological block — the hidden
poem still closes it) and **Sun** (the solstices and equinoxes). The
turning-point entries moved from the `seasons` section of
`encyclopedia.json` to a new `sun` section, and a `moon` section was
added; the repository reads all three through the shared `_section()`
helper. The topic titles Moon/Seasons/Sun reuse existing `ui/` keys.

**The Moon topic grows to EIGHT pages (owner 2026-07-16, ROADMAP queue
#8b):** the `moon` section of `encyclopedia.json` now holds one
house-voice article per phase, keyed by and ordered as
`constants.MOON_PHASE_NAMES` — New Moon, Waxing Crescent, First Quarter,
Waxing Gibbous, Full Moon, Waning Gibbous, Third Quarter, Waning Crescent.
Each carries the phase's geometry and rough rise/set, its
mythological/astrological anchor (Selene/Luna, the Islamic crescent,
Diana/Artemis, Hecate, the full-moon folklore, with real quote anchors
where they fit) and how the Moon marker shows it (new at the ring's top,
full at the bottom), and the TIDES are woven where they belong — the wide
SPRING tides at the New and Full syzygies, the weak NEAP tides at the
Quarters. The topic builds its entries straight from
`constants.MOON_PHASE_NAMES`, so a phase's list index IS its page index —
the same order `compositor` uses for the Moon-marker Spacebar jump. The
single moon plate backs every page until per-phase art lands.
(Serbian translations are NOT written this session — a dedicated
pre-build Translation session covers the sr-Latn bundle; the old single
`moon/Moon` SR keys were pruned as orphans.)

**The Spacebar jump (owner 2026-07-16, ROADMAP queue #8; "sve znači
SVE"):** the dialog accepts an `initial_topic`/`initial_entry`; when set
it skips the gallery and opens straight onto that entry (an unknown topic
falls back to the gallery). The controller passes the (topic, entry) the
widget's Space key resolved through `compositor.encyclopedia_target()` —
which now covers EVERY hover with a page (seated-slot and pinned weekday
bodies in their own theme, the Compass/Seasons arms, the Moon at its
phase, the Earth at its season).

The window is RESIZABLE: each entry is ONE block spanning
`ENCYCLOPEDIA_TEXT_WIDTH_FRACTION` of the width, CENTERED with even
side margins (owner 2026-07-14 — supersedes the 2026-07-13 left-hug),
images share the block, and the font grows with the width at the
gentle em-like coefficient (`ENCYCLOPEDIA_FONT_GROWTH`, capped).

It is a NORMAL window (owner 2026-07-13: no stay-on-top). The look
images decode LAZILY through the `_pixmap` cache (owner 2026-07-13:
The Week opened far too slowly when every look decoded upfront). The
image grid is built ONCE per look (`_render_cell`); window resizes
only RE-FIT the pixmaps in place (`_resize_cell`) — tearing the grid
down per resize left ghost labels and stale container heights that
CLIPPED the art (owner bug 2026-07-14: the full-size crop).

**Reserving the image rectangle (owner REPEAT complaint 2026-07-16,
ROADMAP queue #9):** `_resize_cell` now fixes each image LABEL to its
scaled pixmap (`setFixedSize`). This makes the whole image grid's
MINIMUM size equal the art, so the surrounding `QVBoxLayout` can never
squeeze the container below it — the entry title above and the
style-carousel ("◄ Colored ►") below can no longer cut into the
medallion, and the art is never clipped. When vertical space is tight
the existing `READER_IMAGE_MAX_HEIGHT_FRACTION` ceiling has already
scaled the WHOLE image down. Every topic entry (gallery-driven, poem,
instrument and Spacebar-jumped alike) flows through this one path.

**The ring presets' own symbolism (ROADMAP 15b, owner "malo legende oko
tih naših odabira"):** the EXISTING `instrument/ring_letters` article
(Rule #5 — no new topic key, `_INSTRUMENT_KEYS` stays at 8) grows two
more `[[Subhead]]` sections. `[[The Shapes]]` reads the ring layouts'
own geometry: DOMY's flame triangle (12/20/4) traces the INVERTED
cross (its base — 20h/4h — sits low, near the bottom, St Peter's own
cross), MORPH's chalice triangle (8/16/24) the UPRIGHT cross (its base
— 16h/8h — sits high, near the crown), and the seal layout (NUMBERS,
MASON G) the interlaced hexagram — Solomon's Seal, the same six-point
star Freemasonry and the Templars both carry. `[[The Banknote]]` tells
the MASON G preset's own origin (CANON.md §The Banknote — the owner's
`InGodWeTrust_UVS_BIG.png` hexagram, G+MASON out of the Great Seal's
mottos) and closes with the two-triangle reading: G-M-N (12/20/4) is
the TRINITY read as a court, S-Ω-A (16/24/8) is the UNION of Alpha and
Omega — the same split `app.controller._letter_metal` now draws in
metal on the dial itself, see [Ring Presets](../data/rings.md).

## Connections

### Uses
- [Symbolism Repository](../data/symbolism.md) — articles (overlay
  applied)
- [UI Text Catalog](../config/ui_text.md) — chrome + entity names
- [Compositor](../render/compositor.md) — `_article_body_html` (the
  one wrap/highlight implementation, Rule #5)
- [Theme](theme.md) — the dark dialog surface (buttons stay on
  [UI Style](ui_style.md)'s own gradient pills)
- [Config (folder)](../config/___config.md) — art directories, accent
  tables

### Used by
- [App Controller](../app/controller.md) — opens it from the menu
  with the translation overlay

## Classes

### EncyclopediaDialog
- `__init__(translations)`: builds the topic gallery and the styled
  chrome (Home / Download / ← Previous / counter / Next →)
- `_show_topic(key)`: opens the topic slider at its first entry
- `_step(delta)` / `_show_entry()`: the pager — one entry per page,
  wraps both ways, pager hidden on single-entry topics
- `_download_entry()`: saves the open entry's current-look image(s)
  and its text (headings as `[Label]` lines) into a picked folder
- `_rescale()`: live sizing on resize — gallery cards through
  `_rescale_topics()`; entry pages re-fit fonts and pixmaps
  (`_resize_cell`) without rebuilding the grid
- `_pixmap(path)`: the decoded-image cache behind the lazy looks

## Design Decisions

**The hidden poem (owner 2026-07-16, ROADMAP queue #6):** when
`hidden_unlocked` is true, `__init__` appends TWO extra entries from
`Database/verses.json` — one closing the Trinity topic (the owner's
full four-stanza verses, Serbian throughout, an existing reading), and
one closing the Seasons topic, the poem's CANONICAL home (CANON.md —
the four greetings sit on the four temperament arms): the CANON's
three-line quote, verbatim Serbian, with a short English framing of
the four faces (day = the present lit by faith; evening = life
flowing in love; good night = the peaceful death, full of
understanding; new morning = rebirth without the past). Both entries
carry `"poem": True`, which routes them through the centered-stanza
renderer instead of the normal justified article flow. Neither entry
exists in `_topics()` at all when locked — the SAME cipher unlocks
both (there is no second code); the unlock is SESSION-only, like the
Report. The Seasons entry's badge is a 1×1 px placeholder at
`assets/badge/<source>/season/Poem.png` (owner art pending, per the
WORKPLAN "Missing owner art" rule).
