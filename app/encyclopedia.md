# Encyclopedia

**Script:** [Encyclopedia (script)](encyclopedia.py)

## Purpose
The article BROWSER (owner spec 2026-07-12; menu Encyclopedia… below
Time Travel…): every legend readable without hovering the dial, on two
screens —

1. **Topics** — a gallery in the owner's FIVE SECTIONS (`_TOPIC_GROUPS`,
   owner-approved decision sealed 2026-07-20, round R3 — supersedes the
   nine-group 2026-07-12/13 layout): **The Celestial Engine** (the
   clock topics + Zodiac + Cosmos — Planets and Planet Signs are ONE
   card, distinguished by the Planets/Signs/Art look switcher),
   **The Divine** (gods + the Wider Pantheon + Creeds/Mysteries +
   Scripture), **The Human Wheel** (Virtues, Sins, Moods, the Nine
   Intelligences, Professions, Trinity and THE TWO TRIANGLES — the
   Judas–Lucifer scale of self, owner 2026-07-13; its Lucifer/Judas
   badges ROTATE by date, see Scale Rotation below), **The Living
   World** (Wolf/Bee/Elephant/Alchemy/Japanese week) and **The
   Archetypes** (its OWN section, empty until a future session gives
   the archetypes their own topics — see round R3 below) — EVERYTHING
   centered (owner 2026-07-13: headers and card rows alike) and the
   cards RESPONSIVE: `_rescale_topics` grows/shrinks the icons with
   the window between `ENCYCLOPEDIA_TOPIC_ICON_MIN/MAX_PX`. LAYOUT fix
   round R3: a group never lays out more than
   `ENCYCLOPEDIA_GALLERY_MAX_COLUMNS` (4) cards per row — it WRAPS
   into further rows instead of spilling sideways, and the dialog's
   own `setMinimumWidth` (4 tiles) keeps a full row readable even at
   the minimum icon size — a horizontal scrollbar can no longer happen;
   the vertical scrollbar is the only overflow this gallery ever needs.
2. **Articles** — a SLIDER (owner plan round E, 2026-07-14): one entry
   per page, ← Previous / Next → wrap around with a counter between
   them; the chrome wears the shared gradient pills ([UI
   Style](ui_style.md)) — ⌂ Home top-left back to the gallery,
   ⬇ Download top-right saves the open entry's image(s) and text, and
   (round R3) a persistent FINISH SWITCHER between them — see
   below. The entity image(s) — Astrology shows the sign LOGO and its
   CONSTELLATION side by side, every theme's DUAL page's RULER/SERVANT
   pair stands side by side, while the WEEK pages STACK each pair
   (owner 2026-07-14: Ruler on top, its Servant directly under,
   themes as columns) — then the NAME as a bold title and the full
   base article, translated through the active overlay and with the
   canon terms highlighted exactly like the dial legends (virtues
   blue, vices red, moods yellow, the entity's own arm hue), the
   `[[Subhead]]` markers drawn as centered bold headings hugging
   their paragraph.

**ROUND R3 — the owner's fix-round batch, folder `UV/Encyclopedia`
(owner-approved decisions sealed 2026-07-20):**

- **THE CONTINENTS topic** (`_continents_topic`, owner-sealed matrix
  2026-07-21, round R7a): a CUSTOM weekday-shaped topic that OVERWRITES
  the generic `_weekday_topic` build for `"continents"` right after the
  weekday loop, so it can carry the **world-map title page**
  (`defaults.CONTINENTS_TITLE_IMAGE`, also the gallery card icon) and the
  **Atmosphere/Clean · Day/Night look switcher** (four looks per earth-
  face page — the generic build gives only a single unlabeled look).
  The eleven pages keep the SAME restructured order (title, Monday..
  Saturday continents, duality title, Antarctica the Ruler, Arctic the
  Servant, Ninth) so the Spacebar remap and the article-order canon still
  hold. The six continent bodies and the two poles reuse the dial's OWN
  Earth faces (`assets/earth/`, sealed owner exception — see
  [Assets](../assets/___assets.md)); their prose is the SAME
  `symbolism.json` `articles.continents` set the dial hover reads (Rule
  #5), the poles through the `sun` body's ruler/servant `faces`. The
  Ninth is **LIVING**: Zealandia the Unfound normally, **Pangea** on a
  Pangea day (`core.continents.ninth_is_pangea_from_repos` against the
  traveled date + the bundled Seasons/Moon data — an eclipse, a season
  turning point, or a full/new moon day); both `ninths` articles exist,
  the plate graceful-absent until the owner's art lands. The shared
  static ninths loop SKIPS `"continents"` (it builds its own living
  Ninth). It rides the **The Celestial Engine** hall (the Earth taking
  its seat among the celestial bodies — the theme IS the dial's own
  Earth marker read as the week). The look-switcher's live-sky default
  belongs to the dial (the static gallery opens on "Atmosphere" and
  offers all four looks — documented honest choice).
- **ARTICLE ORDER restructure** (`_weekday_topic`): every weekday-
  structured theme (the 18 `WEEKDAY_THEME_TITLES` keys minus virtues/
  sins/moods, which the emblem-family pass overwrites) now opens
  `[Title, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday,
  Week-Duality title, Dual page, (Ninth if the theme has one)]` —
  entry 0 is the theme's OWN title page (`Database/encyclopedia.json`
  new `theme_title` section, one text per theme; the plate is a
  documented graceful-absent slot for a future theme plate — owner:
  "sliku koju ćemo napraviti"), Monday leads the week (owner: "Uvek…
  Ponedeljak PRVI"), and Sunday's old single "sun" page is now TWO
  pages: a `week_duality` title page introducing the theme's dual
  center, then the DUAL PAGE itself (`entry["dual"] = True`).
- **DUAL ARTICLE LAYOUT** (owner INSTRUCTION #6, encyclopedia side
  only): the dual page shows the Ruler's plate LEFT / Servant's plate
  RIGHT (the pre-existing side-by-side image row, unchanged) and, NEW,
  TWO TEXT COLUMNS underneath — Ruler LEFT, Servant RIGHT, a `QFrame`
  VLine divider between, each under its own bold name
  (`defaults.WEEKDAY_DUAL_NAMES[theme]`). The texts come from
  `SymbolismRepository.article(...)["faces"]` (`{"ruler", "servant"}`
  — every one of the 18 themes' Sunday article already carried this,
  ground-truthed this round) via the new `_article_faces` (mirrors
  `_article_text`, resolves through "faces" instead of "base"). Each
  column is a `(label, columns=2)` entry in `self._text_labels` —
  `_rescale` reserves its HALF-share of the block width the same law
  the full-width case uses (see THE INVISIBLE CLIPPER below).
- **THE SPACE-JUMP INDEX REMAP** (item 9, `_WEEKDAY_DUAL_PAGE_INDEX`):
  `render.compositor._weekday_encyclopedia_target` (out of this
  round's scope) still emits the OLD raw index — sun=0, moon=1..
  saturn=6. The new order happens to leave Monday..Saturday at that
  SAME index (Title only pushes in at 0; Sunday moves OUT to the end)
  — only raw index 0 needs remapping, to the merged dual page's new
  seat (index 8). Applied once in `__init__`, gated on
  `_WEEKDAY_RESTRUCTURED_TOPICS` so non-weekday topics (moon phases,
  seasons, eclipses, zodiac…) are never touched.
- **THE FINISH SWITCHER moves to the TOP row** (owner fix, Color
  Switcher.png): ONE persistent widget trio (`self._look_back` /
  `_look_caption` / `_look_forward`, built once in `__init__`, never
  rebuilt per entry like the old per-block arrows) sits between Home
  and Download; `_show_entry` points `self._look_state` at the open
  entry and shows/hides the trio. Restyled from the old filled
  gradient pill to a BORDER-ONLY frame in the finish's own color
  (`app.ui_style.style_finish_frame`, `defaults.
  ENCYCLOPEDIA_FINISH_BORDER_COLORS`) — "Colored" wears a swept-
  spectrum gradient border (`ENCYCLOPEDIA_FINISH_GRADIENT`: lavender→
  blue→cyan→green→yellow→orange→red, faked via QSS `border-color:
  qlineargradient(...)`, verified rendering offscreen); a non-finish
  arrow-cycle (Planets/Signs/Art, the Week's kinship groups) wears the
  neutral accent border instead — the gradient is reserved for the
  literal Colored option.
- **FINISH PERSISTENCE** (owner INSTRUCTION #3): `self.
  _preferred_look_label` remembers the last finish the user picked
  (`_cycle_look`); every subsequent `_show_entry` opens on that label
  if the new entry offers it (`titles.index(...)`), falling back to
  index 0 (the entry's own default) otherwise — never a silent reset
  to Colored on a page turn or topic change.
- **THE NINTH'S OWN FINISH SWITCHER** (owner bug, Gaia screenshot: the
  9th member's page carried NO color switcher at all): `_ninth_looks`
  gives every METAL_THEMES ninth (Gaia, Yggdrasil, the Polymath,
  Sigma, the Swarm, the Graveyard, the Big Bang) the SAME Colored/
  Bronze/Gold/Silver cycle its seated eight already had, and the
  Chinese Ninth (The Cat) the SAME Bronze-first cycle the other eleven
  animals wear; a theme with no per-metal art (egypt, slavic, the
  plain-color families) correctly keeps its Ninth a single plain
  plate — nothing to switch.
- **IMAGE HOVER names the plate** (owner spec, critical on multi-image
  pages like the era calendars): every article image's `QLabel` now
  carries `setToolTip(_image_tooltip(path))` — the filename stem,
  underscores opened to spaces, Title-Cased only when the stem itself
  carries no capital (so "Byzantine", "KaliYuga" and "Solar_Total" →
  "Solar Total" are left as drawn, "sigma" → "Sigma").
- **THE UNFOUND** (owner decree — the Ninth seat's philosophical
  name): documented as a module-level constant beside the ninths loop,
  with the discussed-and-rejected alternatives (The Uncalled, The
  Ninth Door, The Seeker, The Unclaimed) in the comment there.
- **THE INVISIBLE CLIPPER, root cause found** (owner bug, "Nevidljivi
  element seče pasus The Lesson" — the WORST of the three reported
  element-intersection bugs): ground-truthed offscreen by reproducing
  the EXACT single-frame timing a real Next/Previous click sees
  (`QApplication.processEvents()` pumped ONCE, matching a click
  handler that never yields to the event loop) — the scrollbar's
  range came back **0**, provably matching "blocking scroll because
  the text counts as in view". Root cause: `QScrollArea`'s
  `widgetResizable` path sizes a FRESHLY `setWidget()`-ed
  heightForWidth-dependent widget to the VIEWPORT on its first layout
  pass and only grows it to the true `sizeHint` on a SECOND pass —
  which a single click handler never gets. THREE changes close it
  together: (1) `_show_entry` now calls `_rescale()` BEFORE
  `self._scroll.setWidget(content)` (the width/font/pixmap fit
  resolves on widgets that are not yet the scroll area's tracked
  widget, so `setWidget` only ever sees one, final, geometry); (2)
  text/name labels get their font via `QFont`/`setFont` instead of a
  `setStyleSheet` font-size rule (a stylesheet change only takes
  effect on the widget's NEXT style polish, so `heightForWidth`
  queried immediately after still measured the OLD font); (3) every
  text label reserves its own full height
  (`label.setFixedHeight(label.heightForWidth(width))`), the same law
  `ROADMAP queue #9` already applied to images. The SAME timing bug
  plausibly explains the other two element-intersection screenshots
  (the title overlapping the image, the color switcher overlapping
  the medallion) — the color-switcher case is additionally made
  structurally impossible by moving the switcher out of the per-entry
  block entirely (see above).
- **DEFERRED to round R3b**: the Planetary+Pantheon dual-block merge
  for Greek/Norse/Egyptian/Slavic — implemented below, see ROUND R3b.

**ROUND R3b — the DUAL DOCTRINE round (owner verdicts 2026-07-21):**

- **THE DUAL PAGE SPLITS IN TWO (item 1, owner verdict A — supersedes
  the R3 merged two-column page above)**: `_weekday_topic`'s Sunday
  entry is no longer ONE page with two text columns — it is TWO
  ordinary pages, each shaped exactly like a Monday..Saturday page
  (one plate, one text, full block width): the **GOOD** half (entry
  8, the Ruler's own plate + `article_face` ref reading the "ruler"
  face) then the **EVIL** half (entry 9, the Servant's OWN plate via
  the new `evil_looks_for` — mirrors `looks_for`'s per-metal/per-
  planets-look cycle exactly, built from `_theme_dual_art` instead of
  `_theme_body_art`). A theme with a Ninth appends it at entry 10 —
  every restructured theme is now 10 pages (no Ninth: title+6+duality
  title+good+evil) or 11 (with one). The OLD `entry["dual"]`/
  `entry["theme"]` keys, `_article_faces`, and `_show_entry`'s/
  `_download_entry`'s two-column-in-one-page branches are DELETED
  whole (Rule #6) — a GOOD/EVIL page now flows through the exact same
  code path every other page does. `self._text_labels` drops its
  `(label, columns)` tuple shape too — every label is a plain `QLabel`
  spanning the full block width now, since `columns=2` never occurs
  again. `_article_text` gains an `"article_face"` kind: `("article_
  face", article_set, body, face)` resolves through the SAME "faces"
  register the dial hover reads (`render.compositor._sun_face_
  tooltip`), falling back to "base" — one shared read, never a second
  path. `_WEEKDAY_DUAL_PAGE_INDEX` (still 8 — the arithmetic happens
  to land the GOOD half on the SAME raw index the old merged page
  occupied, pure coincidence, not a second meaning) still remaps the
  Spacebar jump's raw "sun" index onto GOOD only — the jump does NOT
  yet follow the live solar window onto EVIL/NINTH (a deliberate scope
  cut this round, see the round report's doubts).

- **THE PANTHEON/PLANETARY MERGE (item 2, `Ency INSTRUCTIONS.txt`
  rule 5 — the piece R3 deferred)**: the four themes with a
  documented Pantheon roster (`defaults.WEEKDAY_PANTHEON` —
  greek/norse/egypt/slavic, `_PANTHEON_MERGED_THEMES`) become ONE
  topic of 22 pages: pages 1-11 the Planetary run `_weekday_topic`
  already builds, pages 12-22 the SAME 11-page shape again
  (`_pantheon_topic`, `_PANTHEON_BLOCK_SIZE = 11`) for the culture's
  OWN hierarchy — sourced through `defaults.pantheon_seat`'s existing
  safety law (a missing pantheon seat/dual keeps the WHOLE planetary
  bundle, file+name+article together — never a pantheon name over
  planetary art). BOTH blocks close on the IDENTICAL Ninth entry (the
  SAME dict object, appended twice) — CANON.md names ONE Ninth per
  theme, outside BOTH rosters, never a second seatless figure per
  roster. The Pantheon block's own title/week-duality pages resolve
  through NEW `Database/encyclopedia.json` keys, `"<theme>_pantheon"`
  (`greek_pantheon`/`norse_pantheon`/`egypt_pantheon`/`slavic_
  pantheon`), written this round — the culture's OWN throne-room
  argument (RANK inside the pantheon) rather than the day-ruler
  canon. A LOGO BUTTON (`self._roster_button`, between Home and the
  finish switcher) appears ONLY on these four themes: its icon shows
  the roster a click would SWITCH TO (`_svg_icon` rasterizes two
  INLINE SVG marks — `_PLANETARY_ORBIT_SVG`, `_PANTHEON_TEMPLE_SVG` —
  via `QSvgRenderer`, mirroring `app.tray._rasterize_logo`'s recipe
  for a literal SVG string instead of a file; a future ImageGeneration
  pass may replace these placeholder-grade marks without touching the
  call sites), `_switch_roster` jumps `entry_index ± _PANTHEON_
  BLOCK_SIZE` (the SAME day/page in the other block), and
  `_update_roster_button` — called from every `_show_entry`, so
  Next/Previous crossing the 11/12 boundary flips the icon with no
  separate boundary-watch — restyles it per page.

- **THE NINTH TABLE MOVES TO `config/constants.py`
  (`WEEKDAY_THEME_NINTHS`, item 3 groundwork)**: the 15 weekday
  themes' (name, plate) ninths — previously an inline tuple only
  `_topics()`'s ninths loop read — are now the ONE shared table
  [Compositor](../render/compositor.md) and
  [Layers](../render/layers.md) also read for the CENTER seat's
  solar-window face law (Rule #5); the two ZODIAC-only ninths
  (Chinese "The Cat", Astrology "Ophiuchus" — no weekday Sunday
  duality) stay local to `_topics()`, since render never needs them.

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

**NON-MODAL lifecycle (ITEM 1, R4 owner instruction batch 2026-07-20 —
"kada su otvoreni Sat treba da ostane MOGUC ZA INTERAKCIJU"):** the
controller `.show()`s this dialog instead of `.exec()`ing it — `exec()`
forced APPLICATION modality (blocking the dial too, not just this
window) for as long as it stayed open; `.show()` never does.
`WA_DeleteOnClose` tears the C++ object down the moment the window
closes; the controller keeps the ONE live instance as its own
`self._encyclopedia` attribute, raising it (`raise_()` +
`activateWindow()`) instead of opening a duplicate on a second request,
and clears the attribute on this dialog's `finished` signal. The OLD
re-entrancy guard (owner 15h item 3C — back when a second SPACE jump
dispatched inside `exec()`'s nested loop risked stacking a second
modal) is now `navigate_to(topic, entry)`: a themed second jump moves
the SAME live window to the new target instead of being swallowed — a
strict improvement, not just a safe no-op.

**OPENING SIZE (owner DESIGN #1):** A4 portrait (210:297) at 80% of the
screen's available height (`app.theme.size_to_screen`) — the round R3
MIN WIDTH law (4 gallery tiles) still wins when it is the wider of the
two ("whichever is larger wins", the documented resolution), so the
4-column gallery row never spills sideways even on a narrow-but-tall
screen.

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
  [UI Style](ui_style.md)'s own gradient pills; the round R3 finish
  switcher uses that module's `style_finish_frame` border-only frames)
- [Config (folder)](../config/___config.md) — art directories, accent
  tables; `defaults.weekday_theme_body_art` (R5 MENU REWORK — moved
  here FROM this module's own `_theme_body_art`, which is now a plain
  alias, since [Pointer Theme](pointer_theme.md)/[Slot Theme](slot_theme.md)
  need the SAME per-theme preview art for their picker grids, Rule #5)

### Used by
- [Watch Controller](../app/controller.md) — opens it from the menu
  with the translation overlay

## Classes

### EncyclopediaDialog
- `__init__(translations, travel_date=None)`: builds the topic gallery,
  the MIN WIDTH (round R3: 4 gallery tiles) and the styled chrome
  (Home / finish switcher / Download / ← Previous / counter / Next →);
  `travel_date` (the controller's `_effective_travel_date()`, today
  when omitted) drives the Scale Rotation entries; the Spacebar jump
  applies the round R3 index remap for restructured weekday topics
- `_show_topic(key)`: opens the topic slider at its first entry
- `navigate_to(topic, entry)`: jumps this LIVE window to a new
  (topic, entry) target (ITEM 1, R4) — the exact placement logic
  `__init__` used to run once inline, extracted so the controller can
  call it again on a second SPACE jump instead of treating the window
  as re-entrancy-locked; `topic=None` or an unknown topic is a no-op
  (the menu's plain re-open leaves the current page untouched)
- `_step(delta)` / `_show_entry()`: the pager — one entry per page,
  wraps both ways, pager hidden on single-entry topics; `_show_entry`
  branches on `entry["poem"]` / the normal path (round R3b item 1: the
  old `entry["dual"]` two-column branch is gone — GOOD/EVIL are
  ordinary pages now) and calls `_update_roster_button()`
- `_cycle_look(step)` / `_update_look_caption()`: the persistent TOP-
  ROW finish switcher (round R3) — cycles `self._look_state` and
  records the pick as `self._preferred_look_label` (finish
  persistence, owner INSTRUCTION #3)
- `_switch_roster()` / `_update_roster_button()` (round R3b item 2):
  the PANTHEON/PLANETARY logo button — jumps `entry_index ±
  _PANTHEON_BLOCK_SIZE`, and shows/restyles the button per page
  (hidden outside `_PANTHEON_MERGED_THEMES`)
- `_download_entry()`: saves the open entry's current-look image(s)
  and its text (headings as `[Label]` lines) into a picked folder
- `_rescale()`: live sizing on resize — gallery cards through
  `_rescale_topics()` (round R3: WRAPS at
  `ENCYCLOPEDIA_GALLERY_MAX_COLUMNS`, width-driven only); entry pages
  re-fit fonts and pixmaps (`_resize_cell`) without rebuilding the
  grid, and reserve each text label's own height/width
  (THE INVISIBLE CLIPPER fix, round R3)
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
