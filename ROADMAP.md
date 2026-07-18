# Roadmap — What Remains to Ship DOMY Watch

The taxative list of everything between today and the GitHub release
(owner request 2026-07-16). Tasks are RECORDED here, not started —
each one is its own round. The seating doctrine behind the theme work
lives in [The DOMY Canon](CANON.md).

## Table of Contents

- [Where We Stand](#where-we-stand)
- [Owner's Queued Feature Tasks](#owner-queue)
- [Engineering Backlog](#engineering-backlog)
- [Waiting on Owner Art](#waiting-on-art)
- [M7 — Build & Release Pipeline](#m7-build-release)

<a id="where-we-stand"></a>

## Where We Stand

- **M1 shell ✓ M2 computation core ✓ M3 living dial ✓** — and the
  M4–M6 goals have landed along the way: single-instance mutex,
  spontaneous-hide watchdog, autostart (HKCU Run), the full theme/
  metal/roster skin system, Settings with the city picker,
  Encyclopedia, Guide, Time Travel, translations (SR bundle synced).
- **Suite:** 331 green tests (`python -m pytest tests`; Session 16
  added the Deep Time and analytic-illumination goldens).
- **Autostart today runs SOURCE** — the HKCU Run entry launches
  `pythonw.exe main.py`; the M7 installer will point it at the EXE.
- **`dist/DOMYWatch/DOMYWatch.exe` is an ad-hoc PyInstaller test
  build from 2026-07-08** — stale (predates the roster/slots/Union
  arcs), unsigned, no icon/version resource, no installer. Not a
  release artifact.

<a id="owner-queue"></a>

## Owner's Queued Feature Tasks (2026-07-16)

1. **Hidden hover only at the top.** The HIDDEN hover trigger moves
   to 12h only — the letter/sign/number seated at the top; nowhere
   else on the ring.
2. **Omega double-click = reveal week.** Double-click on Omega (24h)
   raises the opacity of ALL weekday bodies to full — ghosts AND the
   center body where one exists (Trinity, Prism) — with the center
   Z-ORDER above the hands. Lasts 60 s after the LAST double-click.
   Applies only to non-active weekday bodies (everything else is
   already 100%). Purpose: see the whole theme at once, laid out by
   color.
3. **Gray out Paint/Light where it does nothing.** Trinity and
   Seasons have no separate paint/light palette variants — the
   palette style option must be GRAYED (unavailable) while they are
   the active pointer.
4. **Pointer archetypes — SEVEN, one per (pointer, palette)**
   (owner 2026-07-16: seven layouts, rhyming with the week; paint =
   the world's order, light = the home's). The grid, content canon,
   the Trinity light Family palette (green/blue/red), and the
   PROPOSED Compass palette rework (paint = the Walks' materials,
   light = the Eight Ages) are in [The DOMY Canon](CANON.md) — read
   it first. Trinity paint image prompts are READY:
   `research/prompts/archetype/trinity_prompts.md` (stained-glass
   register, drop at `assets/archetype/<source>/trinity/`). Also
   queued here: the per-theme CANONICAL POINTER note "under the
   asterisk" (Encyclopedia/menu). Display rules:
   - Visible only during GLOW windows: one of the 4 moon phases
     (~every 7 days) or one of the 4 sun events (~every 90 days).
   - Moon window: revealed ONLY by double-click on Omega.
   - Sun window: appears as a theme option in the slot submenus and
     in the Encyclopedia, and also on Omega double-click.
   - Trinity archetype articles run in TWO ROWS (like the hexa
     zodiac diamonds in Prism): the person (God/Devil/Jesus) and the
     calling (Judge/Prosecutor/Advocate).
   - Prism: the diagonals carry the OPPOSITIONS (Love–Hatred,
     Humility–Pride, Fear–Courage).
   - Works with Time Travel in any mode.
   - Seasons and Compass archetypes: owner still deciding — do not
     invent them.
5. **Turning-point glow rework** (owner 2026-07-16). At a GLOW
   event (a moon phase / a sun event) the MARKER relocates to the
   RING BAND CENTERLINE — the radius where the hour numerals and
   letters sit — at its event position (New Moon at 12h). The glow
   then straddles the ring (shines inside AND outside the circle),
   so it can be SMALL and any color: today it must be huge to
   survive e.g. a white Compass tip, and a yellow sun-glow fights
   the yellow top arms. New colors: the **Sun glows GOLDEN, the
   Moon glows SILVER**.
6. **The poem Easter egg** (owner 2026-07-16). The owner's
   four-greeting poem (text in [The DOMY Canon](CANON.md), Seasons
   archetype section) stays HIDDEN behind the existing typed
   cipher — when the code is entered, the poem appears in the
   Encyclopedia, bound to the Seasons.
7. **Calendar wedge hovers wear OUR logos** (owner 2026-07-16,
   with screenshots): the wedge tooltip must show the CHINESE
   COLORED medallion for the double-hour animal and the zodiac
   COLORED LOGO for the sign — never plain text or a unicode glyph.
8. **SPACEBAR opens the Encyclopedia at the hovered topic** (owner
   2026-07-16): while any themed hover is active (with or without
   the legend visible), Space opens the Encyclopedia on that
   topic's page. **OWNER CORRECTION (same day): "sve znači SVE" —
   every hover text that has an encyclopedia page must open it**:
   weekday bodies in SEATED slots and under the Calendar's pinned
   layout (per-slot theme AND roster), the Compass/Seasons arm
   events (equinoxes, solstices, seasons → the Sun/Seasons pages),
   the Moon marker → its CURRENT phase's page, the Earth marker,
   the Chinese slot — everything with a page.
8b. **The Moon topic grows to EIGHT pages** (owner 2026-07-16): one
   per phase — the four turning points and the four between (waxing
   crescent/gibbous, waning gibbous/crescent) — each with a
   description and a mythological/astrological connection; plus the
   TIDES explained: spring tide at new/full (Sun and Moon pulling
   the water together/apart), neap tide at the quarters.
9. **Image clipping in the Encyclopedia — REPEAT COMPLAINT** (owner
   2026-07-16, "OVO NIJE PRVI PUT!"): the title above and the
   style/nav row below overlap the medallion image. The layout must
   RESERVE the image's full space at every window size — verify
   with screenshots at the owner's sizes.
10. **Encyclopedia: split the Seasons topic into THREE** (owner
    2026-07-16): Moon (the lunations — currently MISSING an
    article), Seasons, and Sun (equinoxes/solstices).
11. **Per-pointer wheel-pair names** (owner 2026-07-16): replace
    the universal Paint/Light labels per the CANON proposal table
    (Court/Family, Seasons/Elements, Walks/Ages — Zodiac/Almanac
    already sealed) once the owner picks.
12. **The Ephemeris project — Anno Lucis** (owner 2026-07-16,
    prompt.txt + `Anno Lucis.png`): DE441-span data (via Swiss
    Ephemeris, −13000…+17000) → a research pipeline extracting all
    solstices/equinoxes (~122k) and moon phases (~1.5M), pinning
    the exact ANNO LUCIS year (the smoothed crossing where the
    light half-year outgrows the dark, ≈4000 BCE — the owner's
    figure is an EXAMPLE, not a measurement; the pipeline
    determines the true year, and if it differs from the masonic
    traditional 4000 BCE, THE TRUE YEAR WINS — owner doctrine
    2026-07-16: "as January 1st differs from December 22nd when
    the day actually starts growing") — then TWO calendars
    everywhere (AD and Anno Lucis), and eventually TWO
    INSTALLATIONS (full = the whole span for Time Travel, partial
    = the current bundle). **MEASURED AND SEALED (owner definition,
    2026-07-16): ANNO LUCIS = 4079 BCE** — the first year of the
    unbroken light era after the 11-year dawn flicker (first light
    year 4089 BCE, last dark year 4080 BCE, then 10,501 light years
    in a row until +6423 CE); **A.L. = CE + 4079 → 2026 = A.L.
    6105**; details in `research/ephemeris/anno_lucis.json`.
    **Encyclopedia article queued — "the Eras of the World":** ours
    (4079 BCE, the only MEASURED one, with the flicker story — "even
    nature hesitated for eleven years"), the masonic Anno Lucis
    (4000 BCE — Anderson 1723, rounded from biblical creation
    chronology), Ussher (4004 BCE), the Hebrew Anno Mundi
    (3761 BCE, Masoretic genealogies), and the BYZANTINE Anno Mundi
    (1 September 5509 BCE — owner ask: from the SEPTUAGINT's longer
    patriarch ages, tuned so Christ arrives ~year 5500 ("the middle
    of the sixth millennium" — the new Adam on the sixth day), and
    COMPUTATIONALLY so the 19-year lunar, 28-year solar and 15-year
    indiction cycles all stand at 1 in year 1 — 19×28×15 = 7980,
    the Julian Period). The article draws the parallel: every
    tradition sought the world's year one in its scriptures or its
    arithmetic; this dial measured it in the sky (owner: "!!! TO
    !!!" — the thesis, sealed). Flavor thread (owner, with a wink):
    the sixth millennium after the light — we are just past A.L.
    6000 — but per OUR canon the One is not a person returning
    every 6000 years: God is the CALLING that keeps being filled
    (NOVUS ORDO SECLORUM), so the sixth millennium finds not one
    returning Christ but the ever-returning Judge. Also in the
    comparison: the ALEXANDRIAN era (5493 BCE — the same Septuagint
    arithmetic, an earlier Alexandrian rounding) and the HEBREW
    Anno Mundi (3761 BCE — the Masoretic text's shorter patriarch
    ages, Seder Olam Rabbah, 2nd c. CE).
    **Era terminology SEALED (owner 2026-07-16): AGE OF LIGHT and
    AGE OF DARKNESS** — AND the starry-season terms live INSIDE
    the eras as their halves: rising half = starry SPRING, falling
    half = starry SUMMER (light era); the dark era mirrors with
    starry AUTUMN and WINTER. MEASURED TRANSITIONS (from our own
    base, smoothed peaks; the owner's "~1000" guess landed EXACTLY):
    starry winter … → 4079 BCE (the dawn); **starry SPRING 4079 BCE
    → 1000 CE (the peak, +7.94 d)**; **starry SUMMER 1000 → 6423 —
    WE LIVE IN THE STARRY SUMMER**; starry autumn 6423 → 10990 (the
    dark peak, −5.5 d); starry winter 10990 → 16429 (the next
    dawn). The prior dark era peaked 9561 BCE (−9.1 d).
    **The THREE PRECISION TIERS must be documented in-app (owner
    2026-07-16):** (i) the bundled core 1560–2640 — minute-exact;
    (ii) the Deep Time span −13000…+17000 — physics exact, local
    clock ±hours (ΔT); (iii) beyond — Laskar: era lengths and
    amplitudes only, no dates.
    **SESSION 16 DELIVERED (2026-07-17):** the Deep Time data pack
    (`setup/make_deep_time.py` → `Database/deep_time.sqlite`, 56.6 MB,
    coverage −12997…+16993, gitignored — the M7 FULL installer bundles
    it), startup detection with repository chaining, Time Travel over
    the whole span incl. BCE (proxy-frame moment editor), the reworked
    Quick Jump tree with the ECLIPSE navigation and unit jumps, the
    year line pairing Anno Lucis everywhere (owner amendment same day:
    official + always-A.L. + optional third calendar), the precision
    tiers documented in-app, and the TRUE analytic moon illumination.
    Still open from this item: the Eras-of-the-World Encyclopedia
    article, the Observatory charts (Session 17), the on-dial eclipse
    display (14a).
    **Phase III (OPTIONAL research, owner interest 2026-07-16):**
    the LONG envelope. Beyond DE441 the day-exact ephemerides are
    unreliable, but the ENVELOPE's drivers (eccentricity, climatic
    precession) are solved for millions of years — Laskar's La2004/
    La2010 orbital solutions (public, IMCCE) give e(t) and e·sinϖ
    at 1000-year steps; from them the light−dark amplitude and the
    era lengths can be plotted over e.g. ±200,000 years WITHOUT
    pretending day-level dates: the amplitude breathes with the
    ~100,000-year (and 405k) eccentricity cycles — currently
    FALLING toward a deep minimum in ~25–30 millennia, then rising
    — exactly the longer cyclicity the owner suspects. **Phase II — ECLIPSES (owner 2026-07-16):**
    the same Swiss Ephemeris files carry them; pyswisseph has direct
    finders (`swe.sol_eclipse_when_glob` / `swe.lun_eclipse_when`
    with types total/annular/hybrid/partial and total/partial/
    penumbral; `_loc` variants for visibility from a place). Volume:
    ~230–240 eclipses per century ≈ ~140k events over the span —
    small next to the moon phases. Stored per solar eclipse (owner
    2026-07-16: an eclipse is not the same everywhere on the
    planet): the instant, the TYPE, the MAGNITUDE and the
    GEOGRAPHIC POINT of greatest eclipse (lat/lon) — the finders
    return them — so the app can say where it was total and compute
    local circumstances on demand; lunar eclipses are visible from
    the whole night side (only "was the moon up" is local). ΔT
    caveat is SHARPER here: THAT an eclipse happens, its date and
    type are robust across the whole span; WHERE its shadow path
    falls (local visibility) is only trustworthy within a few
    millennia of the present, because hours of ΔT slide the path in
    longitude. Dial ideas: the Eclipse
    already exists in our canon as the NINTH MOOD — eclipse events
    can join the glow system and Time Travel's famous-moments list.
13. **The Calendar pointer** (owner 2026-07-16, `Dozen.png`). A
   twelve-wedge pointer, its two wheels **Zodiac / Almanac** in the
   Paint/Light menu slot: Zodiac (sign boundaries on the axes,
   15°-shifted RGB wheel) and Almanac (axis-centered wedges, pure
   primaries; its OWN real-calendar year mapping — one ring tick ≈
   one day, the 1st of each month on a wedge line; the Earth
   marker's day-ARROW pointing at its exact tick). NO wedge
   medallions — the pinned 1/2/3 slot layout carries user content;
   a wedge lights by raising opacity, with BOTH lighting modes
   user-selectable (by the hand's Chinese double-hour, and by the
   year — month/sign). Full doctrine and palettes in
   [The DOMY Canon](CANON.md) §The Calendar.
13b. **The named moons (owner 2026-07-16).** The Almanac's month
   articles adopt the FULL-MOON FOLK NAMES (January the Wolf Moon —
   our Wolf theme's own month! — Snow, Worm, Pink, Flower,
   Strawberry, Buck, Sturgeon, Harvest, Hunter's, Beaver, Cold),
   plus the two calendar specials: the BLUE MOON (the second full
   moon inside one calendar month — every ~2.7 years, "once in a
   blue moon"; the moon is not actually blue) and the BLOOD MOON
   (the total lunar eclipse's true red — already the eclipse
   display's color). Display idea (owner): the full-moon marker may
   wear a SUBTLE tint or tinted glow on the special moons —
   silver-blue on a Blue Moon, the eclipse red already covered.
14a. **Eclipse Quick Jump + on-dial display (owner 2026-07-16).**
   Quick Jump grows FOUR groups — Moon, Moon Eclipse, Sun, Sun
   Eclipse — each with prev/next (dropdown + arrow), fed by the
   eclipse catalog (Session 16). Icons: no true eclipse emoji
   exists — 🌑 (solar) / 🌘 (lunar) stand in until the owner draws
   two small PNGs/SVGs. ON-DIAL DISPLAY — v2 after the owner's
   correction (there is no "Sun marker" — the display anchors to
   the MOON and EARTH markers): during the eclipse window (owner:
   ±3h or ±6h, like the glow windows) — **the EARTH marker is
   REPLACED by the ECLIPSE image** (the Ninth Mood emblem art), and
   **the MOON marker wears the PHENOMENON**: at a solar eclipse
   (new moon — the marker at the moon ring's TOP) a black disc
   with a GOLDEN CORONA ring; at a lunar eclipse (full moon — the
   marker at the BOTTOM) the moon turns BLOOD-RED with a silver-red
   halo (totality truly is red). Both together = SEALED (owner
   2026-07-16): window ±3h; the Earth swap uses the EXISTING
   Eclipse art from the PLANETS theme (the Eclipsed-Sun dual); the
   corona is GLOW-drawn (confirmed — no new art): solar = black
   disc in a golden glow ring, lunar = fully darkened moon in the
   corona glow. The Eclipse is already the
   NINTH MOOD in the emblem canon — the articles link there.
15. **The Observatory — the statistics window (owner 2026-07-16) —
   DONE (Session 17, 2026-07-18).** A right-click sibling of the
   Encyclopedia (🔭 Observatory… beside 🏛️ Encyclopedia…) of dark,
   QPainter-drawn interactive CHARTS over the long data: the
   season-duration oscillations with per-series checkboxes (four seasons
   + the light/dark half-year pair — the owner's own Anno Lucis graph,
   live in the app), the light−dark envelope with the Anno Lucis dawn
   and the Age-of-Light/Darkness bands + starry-season transitions
   marked, the eclipse timeline (nearest past/next solar+lunar from the
   traveled moment when the Deep Time pack is present; the bundled
   density + per-type summary otherwise), and the current location's
   day-length curve over the year (live from the observer, honoring Time
   Travel). Series ship as compact COMMITTED JSON under `Database/`
   (`observatory_seasons.json` ~55 KB bin-mean decimated,
   `observatory_eclipses.json` ~2 KB) built by
   `setup/make_observatory.py` — the charts never require
   `deep_time.sqlite` (the split is documented). Each chart: one y-axis,
   fixed per-series canon colors (season cross-wheel hues; light/dark
   gold vs slate), a legend, a crosshair readout, the filter row above.
   See [Observatory](../app/observatory.md).
15a2. **The year line doctrine (owner 2026-07-17).** Everywhere a
   year shows, BOTH forms show: the official year and the Anno
   Lucis year ("2026 · 6105. Anno Lucis"). Settings govern the
   official labels (BCE/CE default or BC/AD; positive years BARE by
   default — "2026", the suffix only on opt-in or for negative
   years) and an optional THIRD era on the line: AUC (CE+753),
   Byzantine AM (CE+5509), Hebrew AM (CE+3760), Anno Hegirae
   (lunar, display-grade approximation) — amendment sent into
   Session 16. The ±200,000-year Laskar span is CHARTS-ONLY
   (Observatory) — Time Travel stays within the precise
   −13000…+17000 pack (owner confirmed: not precise enough for
   dates beyond).
15a3. **Era terms in the Encyclopedia + their LOGOS (owner
   2026-07-17).** "Age of Light", "Age of Darkness" and the STARRY
   SEASONS (spring/summer/autumn/winter of the eras, with the
   measured transitions) each get an Encyclopedia article — and a
   PROMPT SHEET for their LOGOS/emblems (a new
   research/prompts/era/ sheet: an emblem per era and per starry
   season, house register). The "Eras of the World" article grows
   the owner's list: AUC, Byzantine AM, Hebrew AM, AH — plus the
   Chinese count and the Buddhist Era (543 BCE) as my additions.
15b. **The MASON G ring (owner 2026-07-16).** A new bundled ring
   preset on the seal layout: **G(12) S(16) M(20) Ω(24) N(4)
   A(8)** — the banknote's letters on the dial (CANON §The
   Banknote). Plus: HOVER LEGEND per letter (what G, S, M, Ω, N, A
   each stand for), and ENCYCLOPEDIA lore for the ring presets'
   own symbolism — DOMY traces the INVERTED cross, MORPH the
   upright cross, MASON G / NUMBERS / Templar the hexagram/seal
   (owner: "malo legende oko tih naših odabira").
15c. **THE PUNCH LIST (owner 2026-07-17, with screenshots) — Session
   18, runs AFTER Deep Time (both edit the controller menu):**
   - **Archetype figures must inherit the SLOT behavior** (slika 8):
     the image CLAMPS inside the diamond (never overflows) and
     HOVER-ENLARGES exactly like every other slot — same sizing
     family, same lift.
   - **Omega double-click hit = the FULL circle** around the letter
     (slika 9): today only the glyph (even just its lower part)
     answers; the whole round area at the 24h seat must.
   - **Earth Date + Weekday switches live in Design ▸ Earth**
     (slika 10): move the archetype Earth-weekday toggle there,
     beside Clean/Atmosphere/Date — two switches: Date, Weekday.
   - **Wheel-pair naming rework (ROADMAP 11) IMPLEMENTS NOW**
     (slika 11) + owner seals: the Calendar-only lighting entries
     are NON-VISIBLE on other pointers (never grayed-visible); on
     the Calendar they appear INLINE only while it is active (no
     extra dropdown level). Seasons stops being fully grayed: its
     pair becomes **Seasons / Elements** — implement the ELEMENTS
     wheel (fire/air/water/earth hues, canon) and seat the
     TETRAMORPH figures on it (Man/Angel, Lion, Ox, Eagle —
     placeholders per the house rule), un-graying the pair.
   - **The THREE-SIDE article** (owner): a three-column article
     layout — total width stays the TWO-SIDE width, columns
     narrower, text wraps more; first use: the Ages archetype
     shows BOTH registers at once (age text + the Tree + the
     Menagerie — owner: "oba odmah").
   - **Window margin derived from the LIVE settings** (slike 1–3):
     yesterday's derived margin uses a fixed max-marker constant —
     it over-reserves at default sizes and still clips at max
     Earth size × max hover. Recompute the margin from the user's
     ACTUAL earth/moon scale × hover-enlarge × glow constants on
     every settings change — exact reservation, no waste, no clip.
   - **TRUE moon illumination** (slike 4–7): today's illumination
     interpolates LINEARLY between the four bundled principal
     phases — exact at the principals, up to ~1.5–3 p.p. off
     mid-phase (ours 10.3% vs the true ~11.5% on 2026-07-17).
     Replace with a compact analytic elongation series (pure
     Python, no data files), golden-tested against our own
     events.sqlite instants; rise/set already match to the minute.
15d. **Visibility: two Z modes (owner 2026-07-17, Settings).**
   1 — the current: the clock always BELOW everything except the
   desktop (WindowStaysOnBottom); 2 — NEW: always ON TOP of
   everything (max Z) — a small clock the user always sees whatever
   he does. A Settings choice (and the window flags swap needs the
   documented Windows re-parenting care: flags change before
   show(), or hide/re-show).
15e. **THE VERIFICATION ROUND II (owner 2026-07-17, screenshots) —
   Session 19:**
   - **Earth Date/Weekday are EXCLUSIVE** (slike 1–2): Weekday
     alone must work (today it draws nothing without Date); both
     together is wrong — clicking one unchecks the other (either,
     or neither).
   - **Margin gap** (slika 4): the hovered glowing Earth still
     stops short of the window edge — diagnose the formula term by
     term (epsilon? max(earth,moon) reserving for the larger
     unhovered marker? glow reserve when no glow?) and tighten;
     explain the final formula in the report.
   - **TRUE always-on-top** (owner test): the Qt StaysOnTop hint
     degrades to normal-window behavior after toggling (flags
     recreate the native window). THREE z-modes now: "bottom" /
     "normal" (the accidental middle mode — keep it, the owner
     liked it) / "top" enforced NATIVELY (SetWindowPos
     HWND_TOPMOST via app/native, re-asserted after every flag
     swap and show). Also reconnect screenChanged after the swap
     (the S18 caveat).
   - **Top-level slot ordinals CLICK = ENABLE** (slika 3): clicking
     1st/2nd/3rd Slot in the main menu must do exactly what their
     dropdown Enable does (the 1→2→3 chain still gates); today it
     only flips the checkmark visually.
   - **Elements top-level CLICK = all on / all off**: the check
     shows ONLY when every element is on; clicking then turns all
     off.
   - **Custom SIZE slider** (owner ask): beside the fixed presets
     (360…1440), a Settings slider for any diameter in that range.
   - **Tetramorph three-side** (owner: "sva 3 ako se podudaraju"):
     the tetramorph article uses the three-side layout — creature +
     evangelist + element.
   - **Wheel-pair naming refinements** (owner primedbe): Seasons
     pair renames to "Temperaments / Elements" (kills the
     Seasons-inside-Seasons duplicate); Aurora gets its OWN pair
     instead of a second Paint/Light — "Warm / Cool" (its paint
     leans orange-warm, its light cyan-cool; aurora uses 3 primary
     + 2 secondary + 2 darkened twilight hues, not the full
     palette) — flagged changeable if the owner prefers other
     words.
15f. **THE HOVER PERFORMANCE ROUND (owner 2026-07-17, with the
   profiling report) — Session 20.** The owner's report: Composite
   rebuild 2,083 calls × 38.9 ms avg (max 725 ms), total 81 s —
   because the weekday bodies and archetype figures live INSIDE the
   cached DAILY composite, every hover enter/leave rebuilds the
   whole composite (the long-known "split the weekday layer out of
   the static composite" debt, now due). THE FIX: move the
   hover-variable layers (weekday bodies, archetype figures) OUT of
   the composite into live per-paint drawing (their pixmaps are
   already rasterize-cached — a handful of blits); hover then
   rebuilds NOTHING. Targets: zero composite rebuilds on hover;
   paint frame stays in single-digit ms at 720 px; measure
   before/after with the existing @timed instrumentation and report
   the numbers. Secondary: Hover text max 622 ms first-hover spikes
   — check the article image loads ride the working-set downscales
   and consider caching the built article HTML per (element, day).
15g. **ARCHETYPE FIGURE SIZES UNIFORM (owner 2026-07-17, measured
   radii in UV/prompt.txt) — rides Session 20.** On the hexa
   (Persons) dial today the six outer figures render at ~144 px
   radius while the CENTER figure is ~170 px in the normal state and
   SHRINKS to ~114 px after the Omega double-click (reveal mode).
   Owner rule: ALL figures the SAME dimensions in BOTH situations —
   one shared figure size for the outer arms and the center, and no
   size change between normal and reveal. The same rule applies to
   the trio (Trinity) dial. One sizing path: the center figure uses
   the SAME computed size as the diamond-clamped outer figures, and
   reveal mode must not alter it.
15h. **THE OWNER ROUND OF 2026-07-18 (UV/prompt.txt, nine points) —
   Session 21 material.** DONE the same day: the Earth label trio
   (Date / Weekday / Full Date — accepted names, both-bools = full);
   **Session 21-E reworked this into the FOUR-mode `earth_label` enum**
   (Date / Weekday / Date & Weekday / Full Date — Date & Weekday is the
   OLD combined "Full Date" meaning, renamed now that a true Full Date
   — date over the YEAR — exists; see [Layers](render/layers.md));
   the tetramorph files moved to the config path
   (`archetype/<source>/tetramorph/<Creature>.png`) with the sheet
   corrected and the missing Throne + Seal center prompts written.
   RECORDED, in owner priority order:
   1. **Menu rework — DONE (Session 21-B):** the SETTINGS DIALOG (the
      owner's actual ask — the tray menu itself is a separate, deeper
      nested-submenu tree the owner did not flag) left column becomes a
      `QListWidget` NAVIGATION of section TITLES (each with a trailing
      "▸"), each opening its panel on a `QStackedWidget` to the right;
      related groups SHARE one title exactly per the owner's example —
      Palette + Clock tint = one "Colors" section (seven sections total,
      layout map in [Settings Dialog](../app/settings_dialog.md)). Every
      existing control kept, `result_settings()` untouched, each panel
      keeps its own scroll cap. The tray-menu SIZE slider (item 12 below)
      covers "if he means the MENU too."
   2. **SPACE without focus** — the encyclopedia jump works only
      after the widget was clicked (Qt keyboard focus); owner rule:
      it must work whenever the HOVER works. Needs a key path that
      does not depend on focus (native hook or focus-on-hover).
      → **Session 21-A:** a native low-level keyboard hook
      (`native.KeyboardHook`, `WH_KEYBOARD_LL`) armed ONLY while the
      cursor hovers a page-bearing element — SPACE without focus, no
      focus theft. Needs an owner real-machine check (see the M7
      Defender note above). Click-through mode SPACE-on-hover is NOT
      covered (the widget takes no input there; the poller could drive
      the hook as a follow-up).
   3. **Top-mode bugs**: (A) with the clock focused the HOVER popup
      opens BEHIND the topmost dial — invisible (not focused → fine);
      the popup must ride above the TOPMOST window. (B) with the
      clock focused SPACE opens the encyclopedia even off the themed
      elements ("i za osnovnog sata") — investigate the fallthrough.
      (C) occasional CRASH on SPACE, not reproducible — add crash
      logging (faulthandler to a user-dir file) so the next one
      leaves a trace.
      → **Session 21-A:** (A) the [Legend Popup](../app/legend_popup.md)
      now carries `WindowStaysOnTopHint` AND re-asserts native topmost on
      every show (`SWP_NOACTIVATE`) — owner real-machine check needed.
      (B) FIXED — the SPACE fallthrough was a STALE `_last_hover` that
      survived the cursor leaving the dial; `_last_hover` is now cleared
      on `leaveEvent` and the hover-bypass path, so SPACE off-target is
      inert (pinned by a test). (C) crash logging landed
      (`faulthandler` + `sys.excepthook` → `%APPDATA%/DOMY Watch/crash.log`);
      the likeliest crasher (re-entrant modal opens on repeated SPACE) is
      hardened directly with a re-entrancy guard + auto-repeat de-dupe.
   4. **Archetype names — DONE (Session 21-B), REWORKED (Session
      21-C, owner verdict 2026-07-18):** (a) the figures'
      names were ALREADY `show_weekday_names` end to end
      (`ArchetypeLayer` reads it directly) — the bug was that its only
      menu switch (1st Slot ▸ Weekday ▸ Names) goes unreachable the
      instant Archetype mode grays the whole slot submenu tree; fixed
      with one more reachable action for the SAME key
      ("Archetype names", enabled exactly opposite the buried one — the
      least-new-surface option) — **SUPERSEDED the same round (Session
      21-C): the menu twin is GONE; "nemoj ispod nego u Settings —
      ON/OFF"** — the figures' names are now `archetype_names`, an
      INDEPENDENT setting with its own Settings ▸ Display checkbox,
      separate from the weekday bodies' `show_weekday_names`. (b) a MAX
      FONT SIZE cap
      (`defaults.NAME_LABEL_MAX_PX = 40`, reasoned from the 720-dial
      short-weekday "TUE" look) now applies to BOTH the weekday body
      label and the archetype figure label through ONE shared helper,
      `render.layers.draw_name_label` (Rule #5 — the weekday path used
      to ignore text length entirely, the archetype path fit-to-width
      with no ceiling) — STILL STANDS. (c) two-word names WRAP to two
      centered lines (e.g. the Compass Walks) exactly when that reads
      LARGER than the single-line fit — **SUPERSEDED (Session 21-C,
      owner verdict 2026-07-18): the wrap is REVOKED** (his slika: the
      Compass Ages dial showed "Youth" huge beside a tiny "Childhood" —
      ugly); `_wrap_name_lines` and its tests are deleted whole (Rule
      #6). Replaced by the SET-UNIFORM law: every name of ONE SET (the
      archetype layout's figures, arms AND center together; the weekday
      bodies of a dial) wears the size of the SMALLEST fitted member,
      computed ONCE per paint (`render.layers.weekday_label_set_px` /
      `archetype_label_set_px`) — pinned in `tests/test_archetype.py`.
   5. **Archetype center display trigger — SEALED AND DONE (owner
      pick 2026-07-18):** the solar-noon window EXTENDED to both
      poles of the axis — the center burns FULL within ±1h of TRUE
      solar noon AND true solar midnight (4 of 24 h, ~16.7%), ghost
      otherwise; the Omega reveal still shows it full
      (`ARCHETYPE_CENTER_WINDOW_DEG`, `archetype_center_lit`).
   6. **Hover color-theme alignment — VERIFIED CANONICAL, closed
      (2026-07-18):** an offscreen probe of every cross arm proved
      the CURRENT code already speaks the humoral pairing on both
      wheels (top Summer↔Fire `#E8391E`, right Autumn↔Earth
      `#6B8E3A`, bottom Winter↔Water `#1E74D0`, left Spring↔Air
      `#EFE9B0`; paint = the seasons hues) and the season NAMES
      match the hues on every arm — the owner's 1-2/5 grade came
      from his pre-restart build. Nothing changed; the owner
      re-grades after restarting. (His green-vs-brown instinct:
      the autumn hue is already the muddy olive green-BROWN soil.)
   8. **Click-cycles in the menu — DROPPED** (owner 2026-07-18: "ne"):
      the cycle-on-click idea (Seasons click → Temperaments↔Elements;
      Ring/Umbra/Earth top-bottom pairs; Planetary/Pantheon via the
      color entry) does not go forward. The caught BUG — **FIXED
      (Session 21-B):** both sub-options (e.g. Planetary/Pantheon)
      could show UNCHECKED (slika 2). ROOT CAUSE was a STALE BUILD-TIME
      SNAPSHOT, not Qt's own exclusive `QActionGroup` (verified safe on
      its own): a metal pick (Gold/Bronze/…) activates a pantheon theme
      WITHOUT touching its roster, and nothing resynced the roster
      pair's checkmarks afterward. Fixed at the source (`metal_pick`/
      `resync_roster` in `app/controller.py`, reading the LIVE
      `weekday_roster`/`info_slot_roster`/`third_slot_roster` per slot)
      plus a CENTRAL defense (`_guard_exclusive_choice`, wired into both
      `_add_choice_group` and `slot_action` — every exclusive
      `QActionGroup` in the app menu): a click on the already-checked
      member of ANY exclusive group is now a guaranteed no-op. One
      member always holds.
   9. **Articles for the new themes** — Session 6 (Opus) queued next;
      the master list lives in WORKPLAN/ROADMAP so nothing is lost.
   10. **Location emoji** (owner 2026-07-18): the North/South Pole
      entries in the location picker show ☀️/❄️ with the polar-day and
      polar-night FROM–TO dates beneath (computed from the seasons/
      twilight data, the most precise calculation available); Greenwich
      gets a mark that says "the center" — SEALED 🌐 (a globe with
      meridians = the prime meridian, owner pick 2026-07-18). Explanation of
      the owner's observed transition dates (3 Mar / 9 Oct north, 5 Apr
      / 7 Sep south): at the poles the sun's elevation equals its
      declination (sign-flipped for the south), so those four dates are
      the sun crossing ±6° declination — the CIVIL TWILIGHT boundary,
      not sunrise; they sit ~2.5 weeks off the equinoxes, and the
      north/south spans are asymmetric because Earth runs fastest near
      the January perihelion (orbital eccentricity). TRUE sunrise/sunset
      at a pole is only days from the equinox (atmospheric refraction
      ~34′ + the solar semi-diameter 16′ lift the visible sun).
   11. **Eclipse display — DONE (2026-07-18, ECLIPSE DISPLAY round);
      OPTION C sealed (2026-07-18, Session 21-E).** Refines the sealed
      glow-metal triad. A SOLAR eclipse shows the Planets-theme eclipse
      art
      (`assets/weekday/planets/primary/dual/sun_eclipse.png`, source-
      mapped by `paths.art_file`) on the EARTH marker with a RED glow
      ring (instead of the plain golden season glow); a LUNAR eclipse
      shows the MOON marker darkened (a bronze wash over the whole
      disc) with a BRONZE glow (the blood-moon copper — physically
      true, the exact `BRONZE_LETTER_TINT` hex reused, not a new
      color) plus a thin TURQUOISE FRINGE at the glow's outer edge —
      OPTION C, the real ozone-band color at the umbra's rim during
      totality (`ECLIPSE_LUNAR_FRINGE_COLOR`/`_STOP`/`_HALF_WIDTH`/
      `_ALPHA`; `draw_event_glow()`'s optional `fringe_color` param
      adds three extra gradient stops — transparent → peak →
      transparent — after the bronze mid stop, before the transparent
      edge; None for every other glow caller, unchanged). The ±3h event
      window (`constants.ECLIPSE_GLOW_WINDOW_H`)
      stands; the glow STRENGTH scales with the eclipse MAGNITUDE from
      `Database/deep_time.sqlite`'s eclipse catalog
      (`render.layers.eclipse_glow_strength`, linear between
      `ECLIPSE_GLOW_STRENGTH_MIN/MAX` over `ECLIPSE_MAGNITUDE_MIN/MAX`).
      Data path: `data.deep_time.DeepTimeRepository.eclipses_near()`
      (two indexed jd_ut lookups per kind, never a table scan) feeds
      `core.clock_state.EclipseEvent` candidates into `DayContext.
      eclipses` → `TickState.eclipse_event`; the ABSENCE RULE holds —
      without the optional Deep Time pack `eclipses` stays `()` and no
      eclipse ever renders, identical to before this round. The hover
      text (Earth/Moon) NAMES the eclipse (type, magnitude, local
      instant). **MARKER-PRIORITY NOTE (Session 21-C, 2026-07-18)
      resolved as predicted:** the eclipse window rides the SAME
      relocation-to-ring-band mechanic as the season/moon glow, so
      `render.compositor._element_at` hit-tests it for free — only the
      NEW glow/art condition was needed, no new hit-test path. Tests:
      `tests/test_eclipse.py` (window on/off, magnitude mapping, solar
      art swap + red glow + hit-test, lunar darkening + bronze glow +
      hit-test, hover naming, the golden 2026-08-12 total solar eclipse
      against the real pack when built, and the absent-pack path).
   12. **SIZE slider in the right-click menu — DONE (Session 21-B):** a
      COMPACT `QWidgetAction`-hosted `QSlider` lives in Design ▸ Size
      itself (360–1440, `singleStep` 10, narrow width — coarse tune,
      fine tuning stays in Settings), applying ONLY on `sliderReleased`
      — never mid-drag; a preset pick keeps it synced. The Settings
      dialog's diameter slider ADDS an exact `QSpinBox` beside it
      (`self._diameter_spin`), synced two-way, same 360–1440 range,
      applied together on OK.
   13. **Archetype figures — THE TWO-TYPE LAW — DONE 2026-07-18**
      (this round, TASK A, round two after owner screenshots): NOT
      everything wears the slot size — the art divides into TWO TYPES,
      classified once by its OWN aspect ratio (width/height), via the
      new `archetype_figure_size(skin, radius, art_file)`, the ONE
      sizing entry for `ArchetypeLayer` AND `ArchetypeCenterLayer`
      (and the compositor's center hit disc): CIRCLE type (aspect ≥
      `ARCHETYPE_PORTRAIT_ASPECT_MAX` — rondels, medallions, the
      square Scale glass, and WIDE art like Saturn's rings, plus any
      missing/placeholder art) wears `weekday_body_size(skin, radius)`
      — identical to the weekday bodies, wide art overflowing the
      frame on purpose (owner: "planeta istih dimenzija kao ostale,
      prstenovi vire"); PORTRAIT type (aspect below the threshold —
      the tall lancet vitraž windows: persons, temperaments) wears
      `ARCHETYPE_FIGURE_HEIGHT_OF_TIP[pointer]` of the star tip,
      uniform for every portrait in the set. The 15g per-art CLAMP
      machinery (`archetype_set_height`, `archetype_figure_height`,
      `archetype_fit_height`) is deleted; `ARCHETYPE_FIGURE_HEIGHT_
      OF_TIP` survives, repurposed for the portrait type.
   17. **SATURATION slider — DONE (Session 21-C, owner 2026-07-18):** a
      new Settings ▸ Display slider (0–100%, `palette_saturation`
      0.0–1.0) scales the active Star+Aura palette's HSV saturation at
      the ONE spot both flow through, `render.layers.palette_for` — the
      pointer diamonds and the Aura wedges move together; Umbra (gray)
      and the ring/letters are untouched. Config-driven range/step
      (`constants.PALETTE_SATURATION_RANGE`), store-validated, pinned
      by a render test (0.0 grays the star+aura hues, ring/letters
      unaffected).
   18. **"Show" affordance for the normal Z-mode — DONE (Session 21-C,
      owner 2026-07-18):** in "normal" z-mode the dial rides above other
      windows only while focused — the owner loses it under other
      windows otherwise. A "Show" entry now sits at the very TOP of the
      right-click/tray menu, VISIBLE only while `z_mode == "normal"`
      (hidden, not grayed, in "bottom"/"top" where it means nothing;
      `_refresh_menu_gating` keeps it in sync), and a tray icon
      DOUBLE-CLICK does the same thing — both call
      `ClockWidget.raise_and_focus()` (`raise_()` + `activateWindow()`,
      focus theft accepted here — the user explicitly asked to see the
      clock) through the shared `_show_if_normal_z_mode()` guard.
   19. **Marker-before-ring hover priority bug — FIXED (Session 21-C,
      owner slika 3, 2026-07-18):** during a GLOW event the Moon/Earth
      marker RELOCATES to the ring band centerline (owner's 2026-07-16
      turning-point rework) — hovering it there used to answer with the
      RING TICK reading instead of the marker's own hover. ROOT CAUSE
      (verified): `render.compositor._element_at`'s marker hit-test
      checked only the marker's NORMAL orbit position, never the
      relocated one `YearMarkerLayer.paint` actually draws during
      `tick.moon_event`/`tick.season_event` — a relocated marker missed
      its own hit circle and fell through to `_tick_tooltip`. FIX: the
      hit-test now branches on the SAME event check the render layer
      uses, testing the marker at `GLOW_RING_RADIUS_FRACTION` whenever
      it glows (Rule #5, reusing the render layer's own relocation
      logic/constant rather than re-deriving it) — the owner's law
      ("the MARKERS outrank the ring wherever they sit") now holds
      during glow windows too; `encyclopedia_target` inherits the fix
      for free (shares `_element_at`). Pinned by a hover test at a real
      full-moon glow instant in `tests/test_pointer.py`.
16. **Easter egg — APPROVED (owner 2026-07-16):** the owner's birth
   moment — **20 June 1990, 11:45, Ptuj, Slovenia** — the double
   Horse, sitting at the very TOP of the Calendar dial twice over
   (11:45 inside the Horse double-hour centered on noon; the
   June-20 solstice tick). A future hidden touch honors that spot.

<a id="engineering-backlog"></a>

## Engineering Backlog

- **Wider Pantheon Encyclopedia topics** — one per culture for the
  A-list figures no seat could hold (retired ninths stay in
  `encyclopedia.json` for this wave).
- **The Bond theme** (relationship pillars, owner notes 2026-07-16)
  — definition draft in `research/bond_theme.md`; the Child ninth
  and the family triangle approved; the NAME still open
  (One Soul / The Vow / The Bond).
- **OPEN STRATEGIC QUESTION (owner, 2026-07-16):** partition the
  themes per pointer (each pointer only its naturally-aligned
  themes, ≥4 groups, +paint/light = 6) versus keeping themes
  universal. The standing recommendation (agent, same day): keep
  the WEEK layer (weekday themes, 7 bodies) universal; give each
  pointer its native content on the DAY layer (the archetypes —
  already per-pointer); add soft "natural home" pointer
  recommendations per theme instead of hard walls. Owner verdict
  pending — do not restructure until he rules.
- **`research/build_roster.py`** — add pantheon + glass columns,
  regenerate [Roster](ROSTER.md).
- **Compass palette pair implementation** — the APPROVED hues live
  in [The DOMY Canon](CANON.md) (paint = the Walks' materials,
  light = the Eight Ages); replace the two near-identical octa
  presets in `PALETTE_PRESETS` and pin with a test.
- **Win+D WorkerW glue (optional)** — the only workaround for the
  Show Desktop layer; ship or consciously drop.
- **Docs freshness pass** — README status line, PROJECTS.md entry;
  `research/pantheon_roster_report.md` still describes the old
  global roster combo (historical, superseded banner already in
  place).

<a id="waiting-on-art"></a>

## Waiting on Owner Art

Prompt sheets are ready under `research/prompts/` (one theme = one
file). Wiring is live and falls back gracefully until each drop:

- Pantheon plates per the theme sheets (Greek/Norse/Egypt/Slavic).
- Creeds: the Satanism Sunday dual; Ancient religions: Eleusis.
- The scale GLASS set (6 files incl. Union_Meeting + Union).
- Cat (thirteenth) and Ophiuchus; season badges.

<a id="m7-build-release"></a>

## M7 — Build & Release Pipeline

Follow the monorepo build conventions (root CLAUDE.md):

1. `setup/svg_to_ico.py` — multi-res ICO from `assets/logo.svg`
   (+ `logo-setup.svg` for the wizard icon).
2. `setup/app_info.json` — name, version, exe/installer names;
   company data comes from the root `company.json`.
3. `setup/build.py` — version-info generation, PyInstaller
   `--onedir --windowed` (no UAC; exclude unused modules), signing.
4. `setup/create_cert.py` — one-time self-signed cert
   (`setup/cert/`, gitignored, back up externally).
5. `setup/installer.nsi` — NSIS LZMA installer: desktop shortcut +
   autostart sections; autostart via HKCU Run (standard user, no
   elevation) replacing the dev pythonw entry.
   - **Defender exclusion (Session 21):** the app now installs a
     low-level keyboard hook (`SetWindowsHookEx(WH_KEYBOARD_LL)` — the
     SPACE-without-focus feature, see [Native](../app/native.md)). Per
     the root CLAUDE.md build conventions, apps using low-level system
     hooks add a Defender exclusion in the installer; pair it with the
     code-signing step so SmartScreen/AV heuristics do not flag the
     `SetWindowsHookEx` usage on first run.
6. Root registration — README.md + PROJECTS.md entries; logo copy
   `logos/DOMYWatch.svg` (already present, verify current).
7. Release — smoke the installer on a clean profile, then
   `git tag v{version}` + `gh release create` with
   `dist/DOMYWatch_Setup.exe` as the artifact.
