# Encyclopedia

**Script:** [Encyclopedia (script)](encyclopedia.py)

## Purpose
The article BROWSER (owner spec 2026-07-12; menu Encyclopedia… below
Time Travel…): every legend readable without hovering the dial, on two
screens —

1. **Topics** — a gallery in the owner's GROUPS (`_TOPIC_GROUPS`):
   The Clock, Gods, Zodiac, Themes, Religions, Animal Societies and
   The Inner Wheel (Virtues, Sins, Moods and THE TWO TRIANGLES — the
   Judas–Lucifer scale of self, owner 2026-07-13; its Lucifer/Judas
   badges ROTATE by date, see Scale Rotation below) — EVERYTHING
   centered (owner 2026-07-13: headers
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
phase, the Earth at its season, and — during an eclipse window — the
Earth/Moon marker at the active eclipse CATEGORY, see the Eclipses
section below).

**The Eclipses (fix round F, owner order 2026-07-19, "posebno za mesec
i sunce"):** TWO topics in The Clock group — **Solar Eclipses**
(`eclipse_solar`) and **Lunar Eclipses** (`eclipse_lunar`), one per
body. Each opens with a per-body OVERVIEW page (the entry-zero — the
whole phenomenon, its geometry and how the dial shows it — a reader
meets before the specifics; justified as its own entry-zero because
"posebno" wants each body introduced on its own terms) then one chapter
per CATEGORY the dial distinguishes: solar **Total / Annular / Partial /
Hybrid**, lunar **Total / Partial / Penumbral** — nine chapters total in
the `eclipse` section of `encyclopedia.json` (`data/encyclopedia.py`
`eclipse(key)`). Every chapter DESCRIBES its exact sealed state-table
representation (the black-sun art + red glow, the annular ring-of-fire
orange, the copper blood-moon disc at ~7 %, the turquoise ozone fringe,
the honest penumbral 60 % veil, the silver muted not-visible glow with
its hover reason) so the reader's page and the render can never drift
apart. Each category chapter wears its own emblem
(`assets/eclipse/<Stem>.png`, `defaults.ECLIPSE_ART_DIR`,
graceful-absent — `research/prompts/eclipse/eclipse_prompts.md`); the
overview strings its body's category emblems as a strip, the same
`isinstance(art, tuple)` `images` mechanism the Eras essay uses.
`_ECLIPSE_SOLAR_ENTRIES`/`_ECLIPSE_LUNAR_ENTRIES` fix the chapter ORDER,
kept in lockstep with `compositor._ENC_ECLIPSE_SOLAR_ORDER` /
`_ENC_ECLIPSE_LUNAR_ORDER` so the Spacebar jump indexes the active
type's chapter (hybrid keeps its OWN chapter here even though the render
state table folds it into `solar_total`). `_article_text` /
`_entry_name` gain an `"eclipse"` / `"eclipse_title"` branch.

**The Great Oscillations (fix round F, owner "bravo"):** a Clock-group
ESSAY appended to the `era` topic (a new `era/The_Great_Oscillations`
entry, read through the existing `era(key)`) on the season-length
oscillations and the Milankovitch cycles — eccentricity / obliquity /
precession, what the Observatory's fifth-chart envelope shows, and the
HONEST ice-age line (low eccentricity = muted seasonal forcing, the
~100 k glacial pacing correlation, the +28,000 minimum at ~±1.1 d —
never "an ice age starts then"), naming Milutin Milankovitch. Like the
Eras essay it carries NO plate of its own (`_ERA_ENTRIES` last entry,
`None` → empty `images`).

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
— 16h/8h — sits high, near the crown), and the seal layout (Omega,
Mason) the interlaced hexagram — Solomon's Seal, the same six-point
star Freemasonry and the Templars both carry. `[[The Banknote]]` tells
the Mason preset's own origin (CANON.md §The Banknote — the owner's
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
- `__init__(translations, travel_date=None)`: builds the topic gallery
  and the styled chrome (Home / Download / ← Previous / counter /
  Next →); `travel_date` (the controller's `_effective_travel_date()`,
  today when omitted) drives the Scale Rotation entries
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

**Scale Rotation (owner decree 2026-07-19/20, CANON.md
one-image-one-place amendment — "koje cemo koristiti na smenu"):** the
"duality" topic's Lucifer and Judas entries no longer point at one
fixed master. `_topics(travel_date)` calls
`defaults.scale_variant_file("Lucifer"/"Judas", travel_date)`, which
DISCOVERS every version actually on disk for the active art source
(the metal-cameo `badge/<source>/scale/` root AND its `glass/`
stained-glass register, tolerant of the owner's naming zoo — a bare
stem file, `_v`, `_v1`, `_v2`, `_v3` all count) and picks one by
`travel_date`'s proleptic ordinal modulo the count found, falling back
to the original `Judas_Triangle.png`/`Lucifer_Triangle.png` path
(`or ...`) when nothing is discovered. The Union entry stays FIXED —
only the two poles rotate, called with the SAME date so they advance
in step (independent counts, one shared index driver). `__init__`
takes `travel_date` from the controller
(`self._effective_travel_date()` — the Time Travel simulation's date
while one runs, else today), the SAME law the poles' Quick Jump
light/dark glyph already follows. `ROTATION_DAYS` (THE UNIVERSAL
ROTATION CONVENTION's shared cadence, owner decree 2026-07-20 — see
[Assets (folder)](../assets/___assets.md)) and `SCALE_ART_STEMS` live
in `config/defaults.py` beside `SCALE_ART_DIR`.

**The Eras of the World carries TEN calendar emblems (six from owner
fix-round B, 2026-07-19, TASK 3; Maya added the MAYA round, owner
2026-07-20 — "Jel Maje nisu imale kalendar?"; Kali Yuga/Olympiad/Unix
added the ERA-TRIO round, owner 2026-07-20 — "može sve 3"):** the
comparative essay still has no plate of its OWN, but `_ERA_ENTRIES`'s
last entry now supplies a TUPLE of ten `assets/era/calendar/*.png`
paths (AUC, Byzantine, Hebrew, Hegirae, Buddhist, Huangdi, Maya, Kali
Yuga, Olympiad, Unix — one per calendar the essay compares) instead of
`None`; `_topics()`'s `"images"` comprehension branches on
`isinstance(art, tuple)` to build every path (Rule #5 — the SAME
`images` tuple mechanism `_article_html` already draws side-by-side
art with, e.g. the dual Sunday plates). Graceful-absent like every
other era plate — none of the ten PNGs exist yet
(research/prompts/era/era_prompts.md carries the new prompts); a
future Settings/era-picker use of the same art is noted in that sheet.
The Maya/Olympiad/Kali's OWN `third_era` setting (the year-line third
calendar) is a separate mechanism — see [Deep Time](../core/deep_time.md).

**The calendar strip ALSO rotates now (ERA-TRIO round, owner
2026-07-20 — ground-truthed and fixed):** every calendar-tuple entry
used to bypass `rotating_art_file` entirely, a straight
`ERA_ART_DIR / a` lookup — since the six Age/Starry plates already
routed through the shared `_era_image` helper, the calendar strip
should have too (THE UNIVERSAL ROTATION CONVENTION is meant to be
universal); `_topics()`'s `isinstance(art, tuple)` branch now calls
`_era_image(a)` per path instead. This makes the owner's Byzantine v2
emblem (`assets/era/calendar/alt/Byzantine.png`, the tetragrammatic
cross with four firesteels) an actual rotation partner for the
canonical `Byzantine.png` once both land — see
[Assets (folder)](../assets/___assets.md).

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
Report. The Seasons entry's badge, `assets/badge/<source>/season/
Poem.png`, does not exist on disk yet (owner art pending, per the
WORKPLAN "Missing owner art" rule) — PURGE round 2026-07-19 removed
the committed 1x1 stand-in that used to sit there (it was giving
PromptPainter and the roster the false idea the art already existed);
the entry renders through the SAME `resolved.exists()` filter every
other image reference goes through (`_render_cell`), so the poem's
text and title show with no image at all until the real plate lands —
a genuinely missing file, never a placeholder pretending to be one.
