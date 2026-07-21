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
   **The Divine** (the four merged gods cultures + Creeds/Mysteries +
   Scripture — the old standalone Wider-Pantheon topics were DELETED
   round R8b item 6 as duplicate GALLERY tiles, then their fifteen
   ARTICLES folded back in as each merged topic's own trailing third
   block, round R8d, see below), **The Human Wheel** (Virtues, Sins,
   Moods, the Nine Intelligences, Professions, Trinity and THE TWO
   TRIANGLES — the Judas–Lucifer scale of self, owner 2026-07-13; its
   Lucifer/Judas badges ROTATE by date, see Scale Rotation below),
   **The Living World** (Wolf/Bee/Elephant/Alchemy/Japanese week) and
   **The Archetypes** (its OWN section, empty until a future session
   gives the archetypes their own topics — see round R3 below) —
   EVERYTHING centered (owner 2026-07-13: headers and card rows alike)
   and the cards RESPONSIVE: `_rescale_topics` grows/shrinks the icons
   with the window between `ENCYCLOPEDIA_TOPIC_ICON_MIN/MAX_PX`, then
   `self._zoom` (round R8b item 5b) scales that result further. LAYOUT
   fix round R3, REWORKED round R8b item 5a: a group never lays out
   more than `ENCYCLOPEDIA_GALLERY_MAX_COLUMNS` (4) cards per row — it
   WRAPS into further rows instead of spilling sideways — and the
   dialog's own `setMinimumWidth` uses the CORRECTED
   `_gallery_content_width` formula (the old ad hoc `tile * columns`
   arithmetic silently dropped the inter-card spacing and the
   gallery's own margins, reliably overflowing the frame by ~100px at
   any width below the icon's own MAX ceiling — the exact regression
   the owner's screenshot showed) — a horizontal scrollbar can no
   longer happen at ANY window width or zoom level; the vertical
   scrollbar is the only overflow this gallery ever needs. Two
   overloaded halls (The Celestial Engine, The Divine) additionally
   partition their tiles under LEFT-ALIGNED subgroup headings
   (`_GALLERY_SUBGROUPS`, item 5c — see ROUND R8b below); every row,
   full or short, centers as its own block (item 5d).
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
  entry and shows/hides the trio. Restyled round R3 from the ORIGINAL
  filled pill to a border-only frame, then back to a FILLED pill round
  R8b item 4 ("jel me stvarno zezas da ne mozes da napravis gradient
  button" — the border-only chip never rendered as a real gradient;
  QSS has no `border-color` gradient primitive) — see ROUND R8b below,
  `app.ui_style.style_look_chip`.
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

**ROUND R7b — THE INTELLIGENCES REWRITE + THE SLAVIC MONTHS
(owner-sealed 2026-07-21):**

- **THE NINE INTELLIGENCES, rewritten and reseated by the WEEKDAY LAW**
  (`Database/encyclopedia.json` `intelligence` section, `topics
  ["intelligences"]`): the old articles were plain Gardner with zero
  canon web; they now speak the day web (The Figure / On the Dial with
  the day's colour-hour-mood-column / the virtue-vice DERIVATION / the
  profession as mirror), and the six weekday intelligences move onto the
  arm whose whole bundle already fit them — **Monday Interpersonal, Tue
  Bodily-Kinesthetic, Wed Linguistic, Thu Logical-Mathematical, Fri
  Musical, Sat Naturalist** — each inheriting its arm's virtue as gift
  and vice as shadow (the mood web is read STRAIGHT from `symbolism.json`
  `arms`, so Wednesday is Sorrow and Thursday is Joy, never the shuffled
  transcript). The last three are the **Sun's three faces**: RULER =
  Visual-Spatial (the all-seeing king, the Great Seal's Eye; its shadow
  the eye that believes it IS all, Lucifer's pride), SERVANT =
  Intrapersonal (the self-mirror at solar midnight, Judas' side, where
  the proud extreme cannot look), NINTH = Existential (The Unfound, the
  only intelligence with no trade — the wish for meaning asked in the
  NOON window). The topic PAGE ORDER now follows the weekday law like
  every restructured theme: title -> Mon..Sat -> Ruler -> Servant ->
  Ninth (no separate trio-title page — the title page's own "The Sun's
  Three Faces" subhead introduces the trio; the flat emblem machinery
  wants none). The badge art stems are UNCHANGED — only each
  intelligence's dial SEAT moved. A tiny same-round MOOD MICRO-PASS on
  the continents (`symbolism.json` `articles.continents`) aligns Asia to
  Wednesday's Sorrow and Africa to Thursday's Joy (North America already
  carried Saturday's Renewal). Pinned by `tests/test_intelligences.py`.

- **THE SLAVIC MONTHS — a new Calendar-pointer 12-set + topic**
  (`topics["months"]`, `Database/encyclopedia.json` new top-level
  `months` section, `_TOPIC_GROUPS` "The Celestial Engine"): the twelve
  Croatian months as PROPER NOUNS with the English gloss ("Lipanj (the
  Linden Month)", never the Gregorian name in the title), title page +
  twelve articles — etymology, the labour/nature of the month with its
  Gregorian equivalent in prose, the pan-Slavic Czech/Polish/Ukrainian
  sibling names (the richer stories: the sickle that cuts a month later
  north, the leaf-fall that means October in Zagreb and November in
  Warsaw), and the mark's place on the Calendar-pointer wedge. Built
  from `defaults.SLAVIC_MONTHS` (one config table drives the display
  name, the article key and the plate stem, Rule #4/#5). The topic rides
  **The Celestial Engine** because it IS the year's own wheel (the same
  wheel the Almanac reads), not a myth or a craft. Art is a FUTURE
  prompt sheet under the canonical **sourceless** `months/` root
  (`defaults.MONTHS_ART_DIR`, OUTSIDE `ART_SOURCED_ROOTS` — the subdial
  precedent, see [Assets (folder)](../assets/___assets.md)),
  graceful-absent until it lands (the pointer mount draws the Croatian
  name instead in the meantime). Pinned by `tests/test_months.py`.
  **THE POINTER MOUNT** (R9a round, 2026-07-21): the DESIGN ZODIAC
  law's twelve marks now DRAW on the Calendar pointer at
  `defaults.CALENDAR_MOUNT_RADIUS_FRACTION` (60-70% radius), with a
  Settings picker for WHICH 12-set mounts (off / zodiac signs / this
  months set / the Chinese monthly animals, `SkinDefinition.
  calendar_mount`, the Design ▸ Pointer tab) — see
  [Layers](../render/layers.md)'s own "The 12-SET Mount"
  section; pinned by `tests/test_calendar.py`.
  **THE THIRTEENTH PAIR (owner-sealed 2026-07-22, R12 Blue Moon Law):**
  the topic closes with two MORE entries appended after the twelve —
  **Sol (the Sun's Month)** (Cotsworth's International Fixed Calendar,
  the real 13×28 reform Kodak ran internally 1928-1989, its inserted
  month between June and July named for the summer solstice it
  carries) and **Modrenik (the Blue Moon Month)** (this dial's own
  invented sibling — "modri mesec", the blue moon, answered in a
  Slavic tongue that never needed the word). Same "Name (Gloss)" title
  convention as the twelve real months; each article weaves the OTHER's
  name in (the owner's duality: Sol the Sun's thirteenth at the year's
  TOP, Modrenik the Moon's at its BOTTOM). Unlike the twelve, these two
  never MOUNT on the wheel at all — the Blue Moon Law keeps every
  12-set at twelve; they live only in the dial CENTER, in a blue-moon
  year, inside their own short window
  (see [Blue Moon](../core/blue_moon.md)). Pinned by
  `tests/test_months.py`/`tests/test_blue_moon.py`.

**ROUND R8b — ENCYCLOPEDIA REVIEW PACK (owner batch `UV/prompt.txt`
2026-07-21):**

- **TT LIVE TRAVEL (item 1)** lives in [Time Travel](time_travel.md)
  and [Watch Controller](controller.md) — `WatchController._dialog_jump`
  now starts/refreshes the LIVE simulation as a side effect of every
  Quick Jump row/arrow click, not just a dialog-local draft; this
  module's own `_on_jump`/`_apply_moment` were UNCHANGED (they only
  ever mirrored whatever the callback returned).
- **PANTHEON COLORED (item 3, "Panteon bogovi nemaju Colored verzije u
  switchu")**: `_colored_sibling(path)` replaces two DIFFERENT
  hardcoded guesses at where a bronze plate's `colored/` twin lives —
  `_pantheon_topic.looks_for` assumed the shallow `pantheon/colored/`
  nesting (right for a genuine Pantheon-only figure like Poseidon,
  silently missing for a seat that FALLS BACK to the shared planetary
  plate — Zeus, Thor, Loki, Tyr, none of whom grew dedicated Pantheon
  art), `_ninth_looks` assumed the deep `theme/colored/` sibling
  unconditionally (missing Gaia/Yggdrasil, both pantheon-rooted). One
  function now checks the immediate parent folder's OWN name
  (`"pantheon"` nests one level in, everything else is a sibling of
  its own immediate folder) — ground-truthed against the actual asset
  tree, not re-derived on paper.
- **FILLED-PILL SWITCHER (item 4, "jel me stvarno zezas da ne mozes da
  napravis gradient button")**: `app.ui_style.style_look_chip`
  replaces the R3 border-only `style_finish_frame` — every look now
  wears a FILL, Bronze/Gold/Silver solid in their own metal hex,
  Colored the owner's blue→red sweep as a `qlineargradient`
  BACKGROUND (not a `border-color`, which QSS can only paint at the
  corner miters — the root cause of the R3 chip's visual failure). The
  continents globe looks get their own new fills — Atmosphere leads
  sky-blue and ends warm gold (`#4FC3F7`→`#FFB74D`, the DAY pairing),
  Atmosphere · Night leads navy and ends the SAME blue Colored uses
  (`#0B1F3A`→`#3B5FE0`, family cohesion), Clean is solid ocean teal by
  day (`#0E6B8C`) and the SAME navy by night (`#0B1F3A`) — realizing
  the owner's own four suggested words ("atmosphere = sky-blue
  gradient, clean = deep ocean blue, day = warm gold, night = navy")
  as one coherent palette. Text color is derived per-fill by YIQ
  luminance (`_readable_text`), never hand-picked; see
  [UI Style](ui_style.md).
- **GALLERY LAYOUT REWORK v2 (item 5)**: (a) NO horizontal scrollbar
  can appear at any window width or zoom level — `_gallery_content_
  width`/`_gallery_icon_ceiling` (a matched pair, Rule #5) replace the
  OLD icon-sizing arithmetic, which silently dropped the
  `columns * CARD_PADDING` term from its own budget and reliably
  overflowed the live dialog's own frame by ~100px; `_show_topics`
  also sets the gallery column's margin to a KNOWN explicit
  `GUIDE_SPACING_PX` instead of relying on Qt's unstated QVBoxLayout
  default, so the formula has no hidden fudge factor left. Cards moved
  from `QGridLayout` + `setMinimumSize` to per-row `QHBoxLayout` +
  `setFixedSize` (`_build_gallery_rows`) — a card can no longer force
  its row wider than budgeted even against a long label. (b) Ctrl+
  MouseWheel ZOOMS the whole encyclopedia — `self._zoom` (module-level
  `_session_zoom` seeds each new dialog, so it survives a Home ->
  reopen within the same app run; never written to settings) scales
  article fonts/images and gallery tiles together, `ENCYCLOPEDIA_ZOOM_
  RANGE`/`_STEP` (config/constants.py) bounding it; the block width may
  grow toward the FULL viewport but never past it, so zooming in only
  ever adds vertical scroll once the block is already maxed. (c) TWO
  overloaded halls (The Celestial Engine: 14 topics; The Divine: 9,
  post item-6 deletion) partition into LEFT-ALIGNED subgroup headings,
  `_GALLERY_SUBGROUPS` — Celestial: **The Clock Bodies** (week,
  instrument, planets, astrology, chinese, cosmos, continents — the
  weekday-shaped body/instrument sets) / **The Sky Events** (moon,
  seasons, sun, eclipse_solar, eclipse_lunar — transient phenomena) /
  **The Year Wheels** (era, months — calendar/year structure); Divine:
  **Gods** (greek, norse, egypt, slavic) / **Faiths & Creeds**
  (religion, religion_alt, bible, bible2, bible_dark). Every OTHER
  hall stays one flat run of rows. (d) every row `_build_gallery_rows`
  builds is its OWN `QHBoxLayout` bracketed by a stretch on both
  sides, so a trailing short row centers exactly like a full one, no
  special case.
- **KILL THE LEFTOVER DUPLICATE TILES (item 6, "zasto i dalje imamo
  ove dve verzije")**: the WORKPLAN Session 8 Wider-Pantheon topics
  (`wider_greek`/`wider_norse`/`wider_egypt`/`wider_slavic` — titled
  bare "Greek"/"Norse"/"Egyptian"/"Slavic") sat as confusing SECOND
  tiles right beside the round-R3b merged "Greek gods"/etc. topic —
  `_WIDER_TOPICS` and its `_topics()` build loop are DELETED completely
  (Rule #6: the merged 22-page topics are the only home); their 15
  articles stay untouched in `encyclopedia.json` but are unreachable
  from the UI until a future round re-wires them. The surviving merged
  topics' GALLERY tile and reader TOP HEADER (never the shared
  `defaults.WEEKDAY_THEME_TITLES`, which the Ancient Gods menu/Weekday
  picker/Settings still read unchanged) now read the bare demonym via
  `_GOD_TOPIC_GALLERY_TITLES` — "Greek", "Norse", "Egypt", "Slavic" —
  now that the new Gods subgroup heading (item 5c) already says "Gods".
- **TITLES CARRY THE DAY AND THE SECTION (item 8, "Selene — Monday")**:
  `_entry_name` — the ONE build point — appends " — {Weekday}" when the
  entry carries a `"weekday"` key (set by `_weekday_topic`/
  `_pantheon_topic`/`_continents_topic`'s body/good/evil builders;
  never the title pages, never the Ninth, which sits OUTSIDE the
  weekday per CANON.md). A merged theme's reader TOP header
  (`_topic_display_title`) additionally names its SECTION — "Greek —
  Planetary" / "Greek — Pantheon" — reusing the SAME "Planetary"/
  "Pantheon" translation keys `_update_roster_button`'s tooltip
  already used (Rule #5); the entry caption below reads the
  DATABASE's own `theme_title` text ("Greek gods" / "Greek Pantheon"),
  a different string in a different register, so the two spots no
  longer stack the identical bare name twice (the owner's screenshot).
  The three Sunday-seat position LABELS (Ruler/Servant/Ninth-shaped)
  are UNTOUCHED this round — already one shared table
  (`defaults.WEEKDAY_DUAL_NAMES`, `NINTH_SEAT_PHILOSOPHICAL_NAME`),
  ready to relabel whenever the owner seals the universal names.

**ROUND R8d — THE WIDER COURT RE-WIRE (owner-approved 2026-07-22):**

- **THE MISDIAGNOSIS**: round R8b item 6 deleted `_WIDER_TOPICS` and
  its four standalone gallery cards whole, reading the owner's "zasto i
  dalje imamo ove dve verzije" complaint as "delete the topics" — the
  complaint was actually about the DUPLICATE gallery tiles sitting
  beside the merged culture topics, never about the fifteen articles
  themselves (Dionysus, Hephaestus, Hestia; Baldur, Heimdall, Njord;
  Set, Nut, Geb, Ptah, Sekhmet; Crnobog, Stribog, Jarilo, Rod), which
  stayed untouched, real owner-era prose, in `Database/encyclopedia.
  json`'s `wider` family the whole time — just unreachable from the UI.
  The sealed fix: fold them INTO the four merged culture topics as a
  trailing THIRD block, instead of restoring their own standalone
  topics/tiles.
- **THE WIDER COURT BLOCK (`_wider_topic`)**: each merged culture topic
  grows a third block after the Pantheon run — a section TITLE page
  (`"<theme>_wider"`, new `Database/encyclopedia.json` `theme_title`
  keys, the SAME family `"<theme>_pantheon"` already uses, 2-3
  sentences per culture in the existing title-page voice: "Nine seats…
  cannot hold every X — N more stand outside both rosters…") then one
  ordinary single-image page per figure, sourced from the SAME
  `EncyclopediaRepository.entry("wider", name)` family the deleted
  topics read (prose untouched, only its HOME moved). The page map
  (`_PANTHEON_BLOCK_SIZE = 11`, `_WIDER_BLOCK_START = 2 *
  _PANTHEON_BLOCK_SIZE = 22`): pages 1-11 Planetary, 12-22 Pantheon, 23
  The Wider Court title, 24+ the culture's wider figures (Greek/Norse
  end at 26, Slavic at 27, Egypt — five figures — at 28). NO `looks`
  key on any wider-figure entry: ground-truthed against the asset tree
  (`assets/weekday/<source>/<theme>/wider/`) — none of the fifteen
  figures has landed ANY art yet, not even a bronze master, so there is
  nothing to cycle; the page renders on `"images"` alone and stays
  gracefully absent (a name and a text, no plate) exactly like the old
  standalone topics did, until the owner's art lands.
- **THE SECTION INDICATOR LEARNS A THIRD NAME**: `_topic_display_title`
  (round R8b item 8's "Greek — Planetary" / "Greek — Pantheon" header)
  gains "Greek — Wider Court" for `entry_index >= _WIDER_BLOCK_START` —
  the same three-way `_tr("Planetary")` / `_tr("Pantheon")` /
  `_tr("Wider Court")` pattern extended, not a new mechanism.
- **THE ROSTER-SWITCH BUTTON HIDES ON THE WIDER COURT (owner's own
  call, justified)**: `_update_roster_button` now hides the button for
  `entry_index >= _WIDER_BLOCK_START` too — the SAME "hidden outside
  the merged themes" guard the button already had, not a new special
  case. Reasoning: the button's whole contract is "jump to the SAME
  day in the OTHER 11-page roster" (Monday stays Monday); The Wider
  Court is a single trailing run with no twin block the same length to
  jump to, so there is no position-preserving destination to name on
  its icon — showing an icon that claims "back to Planetary" would
  either be arbitrary (which page does it land on?) or misleading
  (implying a correspondence that does not exist). Hiding is the
  honest choice, matching how the button already behaves on every
  non-merged topic.
- **REACHABILITY, NOT REGROWTH**: `tests/test_settings_dialog.py`
  `test_wider_court_block` pins all fifteen articles reachable again BY
  TITLE, in the old standalone topics' own per-culture order;
  `test_wider_court_gallery_has_no_extra_tiles` (companion to the
  R8b `test_wider_pantheon_topics_removed_as_duplicate_tiles`, both
  kept) confirms the gallery gains no fifth "Wider Court" tile and no
  `wider_greek`/etc. topic keys return — the fold-in is PAGES inside an
  existing topic, never a new gallery card.

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
  [UI Style](ui_style.md)'s own gradient pills; the finish switcher
  uses that module's `style_look_chip` filled pill, round R8b item 4)
- [Config (folder)](../config/___config.md) — art directories, accent
  tables; `defaults.weekday_theme_body_art` (R5 MENU REWORK — moved
  here FROM this module's own `_theme_body_art`, which is now a plain
  alias, since [Pointer Theme](pointer_theme.md)/[Slot Theme](slot_theme.md)
  need the SAME per-theme preview art for their picker grids, Rule #5);
  `constants.ENCYCLOPEDIA_ZOOM_RANGE`/`_STEP` (round R8b item 5b — the
  Ctrl+wheel zoom bounds, the same RANGE-constant pattern
  `ELEMENT_SCALE_RANGE` already uses)

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
  (hidden outside `_PANTHEON_MERGED_THEMES`, AND on The Wider Court
  block, `entry_index >= _WIDER_BLOCK_START` — round R8d, see there)
- `_download_entry()`: saves the open entry's current-look image(s)
  and its text (headings as `[Label]` lines) into a picked folder
- `_rescale()`: live sizing on resize — gallery cards through
  `_rescale_topics()` (round R3: WRAPS at
  `ENCYCLOPEDIA_GALLERY_MAX_COLUMNS`, width-driven only, `_gallery_
  icon_ceiling` a HARD cap round R8b item 5a); entry pages re-fit
  fonts and pixmaps (`_resize_cell`) without rebuilding the grid, and
  reserve each text label's own height/width (THE INVISIBLE CLIPPER
  fix, round R3); `self._zoom` (round R8b item 5b) scales fonts,
  images and gallery tiles together, capped so it can never force an
  overflow (see ROUND R8b below)
- `_pixmap(path)`: the decoded-image cache behind the lazy looks
- `eventFilter(obj, event)` / `wheelEvent(event)` (round R8b item 5b):
  Ctrl+MouseWheel zooms — the SAME guard installed both on the scroll
  area's own viewport (an event filter, since Qt delivers wheel events
  to whichever widget sits under the cursor) and on the dialog itself
  (for cursor positions over its own chrome); plain wheel is untouched
  either way, so normal scrolling is unaffected

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
