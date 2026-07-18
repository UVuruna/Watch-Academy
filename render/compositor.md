# Compositor

**Script:** [Compositor (script)](compositor.py)

## Purpose
Owns the layer stack and the cadence-driven cache. The z-ordered stack
is partitioned into paint STEPS (owner 2026-07-17, ROADMAP 15f): each
maximal run of hover-INVARIANT STATIC/DAILY layers becomes ONE cached
pixmap at device resolution; the MINUTE layers AND the HOVER-VARIABLE
layers (the weekday bodies, the archetype figures) paint LIVE every
frame. Because the default `z_order` seats the weekday_set BELOW the
ring, pulling it out splits the cache into TWO segments (base below the
live bodies, ring above them), so the z-order is preserved to the pixel.

### The rebuild triggers (the COMPLETE list)
A cached segment is rebuilt ONLY when the composite key changes —
`(round(size·dpr), day.cache_key, calendar_lit)`:

- **size / DPI change** — `invalidate()` (also flushes the asset cache);
- **day change** — `set_day()`;
- **skin / theme install** — the controller builds a FRESH compositor
  (`_install_skin`), so the segments start empty;
- **settings apply** — same `_install_skin` path;
- **the Calendar's intraday lit wedge** (`calendar_lit`) — the shichen
  relights ~12×/day (BackgroundLayer is cached).

A **hover** enter/leave and an **Omega reveal** toggle rebuild NOTHING —
the weekday bodies and archetype figures that vary with them are drawn
LIVE (`set_hover()` / `trigger_reveal_week()` no longer drop any cache).

## Connections

### Uses
- [Layers](layers.md), [Assets](assets.md),
  [Clock State](../core/clock_state.md), [Skins (folder)](../skins/___skins.md)

### Used by
- [Clock Widget](../app/widget.md) — `paintEvent` delegate
- [App Controller](../app/controller.md) — `set_day()` / `invalidate()`
- [Tests (folder)](../tests/___tests.md) — `render_offscreen()`

## Classes

### Compositor
- `_plan_steps(layers)`: partitions the z-ordered stack into paint STEPS
  (owner 2026-07-17, ROADMAP 15f) — runs of cacheable (non-MINUTE,
  hover-invariant) layers coalesce into one cached pixmap each; MINUTE
  and hover-variable layers become LIVE steps. Returns
  `(cached_groups, steps)`; a step is `("cache", group_index)` or
  `("live", layer)`, in z-order.
- `set_day(day)`: new day context, drops the cached segments
- `invalidate()`: size/DPI/screen change — drops the segments AND rasterized assets
- `paint(painter, size, dpr, tick)`: walk the steps — blit each cached
  segment (rebuilding it if its key changed) and paint each live layer
  in z-order; the reveal window skips the HandLayers; raises if called
  before the first day context (startup order is a controller guarantee)
- `render_offscreen(size, dpr, day, tick) -> QImage`: same path, headless
- `set_hover(x, y, size) -> bool`: tracks the element under the cursor
  for the HOVER-ENLARGE effect (owner EXTRAS — one shared factor draws
  it larger); True = target changed, the widget repaints. Rebuilds
  NOTHING (owner 2026-07-17, ROADMAP 15f: the weekday bodies and
  archetype figures paint LIVE, so the enlarge is a handful of cached
  blits on the next frame).
  `_element_at()` is the ONE geometry shared with the tooltips
  (body/seated slots/moon/earth, in hover priority — seated slots
  reuse the layer's exact seat geometry: `slot_seat_rotation` /
  `slot_seat_scale` / `slot_seat_orbit`; the classic weekday bodies
  mirror `WeekdayLayer` — `slot_seat_scale` size and the
  `weekday_body_orbit` romb-center ride, servant seat included); legend
  off or a factor of 1.0 keeps the dial inert.
  **THE MARKERS OUTRANK THE RING (owner bug fix, Session 21-C,
  2026-07-18, slika 3):** during a GLOW window (`tick.moon_event` /
  `tick.season_event`) `YearMarkerLayer` RELOCATES the Moon/Earth
  marker radially to the ring band centerline
  (`defaults.GLOW_RING_RADIUS_FRACTION` — the same radius the ring
  numerals/letters sit at, see [Layers](layers.md)'s YearMarkerLayer).
  `_element_at`'s marker hit-test used to check only the marker's
  NORMAL orbit position (`marker.moon_orbit_fraction` / `marker.
  orbit_fraction`), so a relocated marker missed its own hit circle and
  fell through to `_tick_tooltip` (the ring band) underneath it — the
  owner's report: hovering the Moon at a glow moment answered with the
  ring's angle reading instead of the Moon's own hover. FIX: the
  hit-test now branches on the SAME `moon_event`/`season_event` check
  `YearMarkerLayer.paint` uses, hit-testing the marker at
  `GLOW_RING_RADIUS_FRACTION` whenever it glows — the exact DRAWN
  position — so the marker answers first wherever it actually sits;
  `encyclopedia_target` inherits the fix for free (it calls
  `_element_at` directly).
- `hit_omega(x, y, size) -> bool` / `trigger_reveal_week()` /
  `reveal_active()` (owner 2026-07-16, REPURPOSED by the same-day
  seal): the Omega (24h) double-click hit region — the FULL ROUND AREA
  at the 24h seat (owner slika 9, 2026-07-17: a circle centered on the
  Omega letter position covering the whole letter cell,
  `OMEGA_HIT_RADIUS_FRACTION`; the old narrow annular wedge only
  answered on the glyph's lower part) — and the reveal window it
  TOGGLES:
  the first double-click starts `REVEAL_WEEK_DURATION_S` (returning
  True), the next one ends it (a toggle-off, not a restart; False).
  While it runs `paint()` SKIPS the HandLayers — the hands are
  hidden so the whole theme, pointer and dial read clean — and the
  reveal flag rides `RenderContext.reveal_active` into the LIVE
  weekday/archetype layers (owner 2026-07-17, ROADMAP 15f: no composite
  rebuild), so the WeekdayLayer redraws ghosts at full opacity and steps
  aside for CenterBodyLayer to lift the ghost center Sun above the hands;
  in ARCHETYPE MODE every figure draws full instead (the same "show me
  everything" semantics). The hidden-mode Four Greetings hover (below) moved to
  the 12h letter ONLY in the same round — Omega no longer answers it
- THE ARCHETYPE MODE plumbing (owner sealed package 2026-07-16;
  tables in [Archetypes](../config/archetypes.md), layers in
  [Layers](layers.md) §The Archetype Mode): `_archetype_lit(tick)`
  computes the hour-space figure from the live tick and feeds it into the
  LIVE ArchetypeLayer via `RenderContext.archetype_lit` (owner
  2026-07-17, ROADMAP 15f: the figures paint live now — the lit index no
  longer keys any cache, so the intraday relight is free);
  `_build_layers()` seats `ArchetypeLayer` at the weekday_set z spot
  and appends `ArchetypeCenterLayer` above the hands while the mode
  is active; `_element_at` answers `"archetype:center"` over the
  center disc AND `"archetype:<index>"` over each arm DIAMOND (owner
  slika 8, 2026-07-17: the arm figures are hover-enlarge targets
  through `_arm_angle_at`, the one arm-diamond geometry — checked
  after the Earth/Moon so the instrument keeps priority); the arm
  figures return the archetype's TWO-ROW article
  (`_archetype_arm_tooltip(index)` → `_archetype_two_rows`: the
  stained glass — real art only — the figure's name, row 1, a rule,
  the second-row name, row 2, resolved through
  `SymbolismRepository.archetype_article`; an unwritten set shows the
  name + the pending line, never a KeyError) — EXCEPT the two
  THREE-COLUMN layouts (the width of the two-side legend): the Ages
  (compass light) show `_archetype_three_side(index)` (owner slika 6,
  "oba odmah") — the age's text, the Tree register and the Menagerie
  register at once; the Tetramorph (seasons light) shows
  `_tetramorph_three_side(index)` (owner 2026-07-17, "sva 3 ako se
  podudaraju") — the creature (glass + name + text), the EVANGELIST it
  became (Mark/Luke/John/Matthew) and the ELEMENT its fixed-cross season
  arm holds (`archetypes.tetramorph_element`, in the active wheel hue from
  `palette_for`). The center answers via
  `_archetype_center_tooltip`; `encyclopedia_target` follows each
  FIGURE's own (topic, entry) — today only the Walks map onto the
  Professions pages, everything else answers None gracefully
  (Sessions 6/8 add the topics)
- `_year(when)`: every hover YEAR renders through this one method
  (Session 16, owner amendment 2026-07-17) —
  `core.deep_time.format_year_line`: the official year with the Anno
  Lucis year always beside it ("2026 · 6105. Anno Lucis") plus the
  optional third calendar, un-shifting the deep proxy frame first
  (`day.deep_cycles`). The ring-tick hover's hypothetical cycle
  reading uses `nominal_illumination` (the ring's own cosine mapping);
  the LIVE Moon hover reads the TRUE analytic `tick.moon_illumination`.
- `tooltip_at(x, y, size) -> str | None`: hover text at every dial size
  (the owner's hover-rework formats: raised `<sup>` ordinal suffixes,
  hyphens instead of long dashes) — a `@timed("Hover text")` shell over
  `_tooltip_at`, so the owner's profile measures REAL hovers only while
  the warm sweep (below) calls the impl directly — in priority order — the WEEKDAY
  BODIES (every visible body within its image region: the entity's
  NAME as a bigger bold title — Odin, Farmer, Islam… (owner spec
  2026-07-11, `defaults.ARTICLE_TITLE_PX`) — the active day adds
  "Thursday, 9th July 2026" beneath it, then the JUSTIFIED
  article (owner 2026-07-13: clean book-column edges, reflowing in a
  `defaults.ARTICLE_TEXT_WIDTH_PX` cell) — base + the active
  pointer/palette combination paragraph,
  the entity art on top). In every article the canon terms POP
  (owner spec 2026-07-12, `_highlight_terms`): virtues bold blue,
  vices bold red, moods bold yellow, color words in their own hue
  (`defaults.LEGEND_*` rules, English + Serbian originals), and hex
  notes like "(#F8E600)" are stripped from display; when the CLASSIC
  unit is driven by the 2nd slot (Seasons/Compass two-slot case) the
  body hover speaks that slot's own theme, metal AND roster. A hover
  with an explicit roster takes the weekday-set shortcut only while
  the roster matches the set as dressed (owner 2026-07-15: slot 1
  Greek Planetary beside slot 2 Greek Pantheon — same theme, two
  casts); a pantheon seat otherwise resolves identity, plate and
  article through `defaults.pantheon_seat`, planetary-whole on
  missing art, the Sunday dual pair falling back together. Then the
  seated slots
  ("slot:N" via `slot_view` — weekday seats answer the body article,
  zodiac/ascendant/Chinese their sign texts, digital faces stay
  silent) — the Astrology/Ascendant hovers lead with a bold title
  ("Ascendant" written out in full) and an image TRIO: the ACTIVE
  style's art large in the middle, the two remaining styles at
  `ASTRO_SIDE_IMAGE_FRACTION` beside it (owner 2026-07-13; text mode
  leads with the colored logo); the
  Moon marker (owner formatting round 2026-07-13: the phase NAME as
  the title — no "Phase:" label — with the exact principal instant
  beneath while its name holds, then **Illumination:** to one decimal
  and **Moonrise:**/
  **Moonset:**, a blank row, then the cycle day and the running
  lunation); the Earth marker (bold **Date:** with the Nth Day - Nth
  Week row beneath, a blank row, then **Season:** "Summer 18th of 94
  Days" — southern hemisphere flips the name — and **Sign:** with the
  zodiac span, plus the season event name while it glows); the ring
  TICK BAND (before the twilight wedges — in the overlapping annulus
  the circle wins): the 360 arrows answer in DOMY-titled sections
  separated by blank rows — **Day** (**Time:**/**Angle:** plus the
  day-period word), **Year** (**Date:** with the anchor event,
  **Season:** with the day/week ordinals) and **Moon** (the lunation
  the ANGLE belongs to — with the Moon on the dial's LEFT the right
  half of the ring already reads as the NEXT moon, December wrapping
  into the new year's 1st (owner logic 2026-07-13) — then the cycle
  reading at that angle); the twilight bands
  (bold **Morning/Evening Twilight** title, the labeled bounds in the
  order the light moves, and the span in minutes AND dial degrees —
  "37 min - 9.25°" at 15°/h); the STAR ARMS
  (hexa diamonds carry BOTH their signs SIDE BY SIDE as two columns —
  owner 2026-07-13: bold glyph-free title with the span, the COLORED
  logo, then the sign's full article from the
  [Symbolism Repository](../data/symbolism.md); trio arms give their
  theological theme, day third and weekday pair; cross/octa cardinals
  follow the image → title → space → data format — the turning-point
  badge, the bold event name, its instant and the labeled
  **Daylight:** — the cross appending, after a rule, its
  METEOROLOGICAL season block wearing its own badge with bold
  **From**/**To** at the halfway instants and the labeled
  **Duration:** in days to one decimal (the tropics' wet/dry block
  wears the same format); octa diagonals describe their season with
  "(N.N Days)" and "Heart:" as the midpoint label — a trailing * flags
  solar-rotation imprecision); and LAST the wheel itself — a mini
  Earth of the active region on top (day art on the Day side, night
  art on the Night side, atmosphere/clean per the Earth setting,
  `defaults.PERIOD_EARTH_IMAGE_PX`), then bold **Day**/**Night** with
  the duration, the labeled sun span, and the twilight-extended span
  under its own **With Twilight** / **Complete Dark** title.
  With `legend` off, tooltip_at returns None for EVERYTHING — combined
  with click-through the dial has zero interaction (owner spec). A
  switched-off Element answers no hovers either: weekday off silences
  the body spots, pointer off the arm regions and the octa slot,
  earth/moon off their markers

The Calendar wedge hover (`_calendar_tooltip`) now WEARS OUR ART (owner
2026-07-16, ROADMAP queue #7): the Almanac wedge shows the double-hour
animal's Chinese COLORED medallion, the Zodiac wedge the sign's COLORED
LOGO — a real `_hover_badge` image above the text, never a unicode glyph.

- `warm_hover_articles(size, should_stop, progress) -> int` (owner
  2026-07-18, asked twice — the FIRST hover must be as instant as the
  tenth): the background pre-build of every hover article the skin can
  speak TODAY. It walks a dense polar probe grid
  (`HOVER_WARM_ANGLE_STEPS × HOVER_WARM_RADIAL_STEPS`, pitch under half
  the smallest hover target) through the REAL `_tooltip_at` dispatch —
  no second file-resolution path to drift — so every embedded image's
  downscaled variant lands in the disk cache and the OS file cache
  before the user's first hover ever fires; ring-paced with
  `HOVER_WARM_RING_PAUSE_S` (slow and polite, image by image, per the
  owner's words). `@timed("Hover warmup")` — its cost shows in the
  owner's profile under its OWN name, never polluting "Hover text".
  The controller runs it after the working-set warmup and re-runs it
  on skin install and day change (`should_stop` aborts an obsoleted
  sweep); a warm re-run costs header reads only.

- `encyclopedia_target(x, y, size) -> (topic, entry) | None` (owner
  2026-07-16, ROADMAP queue #8, "sve znači SVE" round 2026-07-16): the
  ONE table-driven element→encyclopedia-topic mapping behind the Spacebar
  jump — EVERY hover that speaks a page opens it. It reuses the hover
  GEOMETRY, not the tooltip text, so it works with the legend OFF, and it
  follows `tooltip_at`'s own priority: `_element_encyclopedia_target`
  first (from `_element_at`), then `_arm_encyclopedia_target`, then the
  Calendar wedge.
  - **Weekday bodies** — a pinned/classic body AND a seated weekday slot
    both resolve the OWNING theme (the classic unit's `weekday_theme`, or
    the 2nd slot's `info_slot_theme` when it drives the unit; a seated
    slot's own `slot_view` theme) → that theme's Week-order body page.
    This fixes the owner's failing cases: today's body on the Calendar's
    pinned slot, and the Greek/Egyptian bodies seated on 4h/20h slots.
  - **Slots** — zodiac/ascendant → the Astrology sign page, Chinese → the
    animal page; digital faces map to None.
  - **Star arms** (`_arm_encyclopedia_target`, mirrors the `_arm_tooltip`
    diamond) — hexa diamonds → the zodiac sign; cross/octa CARDINAL arms
    → the Sun topic's solstice/equinox (`_sun_topic_index`); octa
    DIAGONAL arms → the Seasons topic's season or tropical half; trio
    arms → the Trinity virtue.
  - **Moon marker** → the Moon topic at the CURRENT phase's page
    (`phase_name` indexed into `constants.MOON_PHASE_NAMES`, the topic's
    eight-page order — ROADMAP queue #8b).
  - **Earth marker** → the Seasons topic at the current season
    (`_season_topic_index`/`_current_season_key`, mirroring `_season_row`).
  - **Calendar wedges** (`_calendar_wedge_target`) → the sign/animal page.
  - No page — the digital slots, the twilight bands and the ring band —
    returns None.

The layer stack follows `skin.z_order`, skipping the layers of
switched-off Elements (star, weekday set, year marker when both
markers are off, the seconds hand); angle-seated slots draw BELOW the
hands, while the current day's center body and a center-seated slot
are appended LAST so they draw above the hands (owner spec).
`_rotation()` feeds the shared Star/Aura/Umbra rotation into every
RenderContext: the solar offset, or 0 with solar rotation off
(upright mode) — the slot seats take it only through
`slot_seat_rotation` (armed pointers only). The letter band also
answers the FOUR GREETINGS hover on the 12h ring letter ONLY (owner
2026-07-16) once the hidden mode is unlocked for the session; the 24h
(Omega) letter instead answers a double-click — see `hit_omega`
above.
