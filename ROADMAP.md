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
- **Suite:** 242 green tests (`python -m pytest tests`).
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
15. **The Observatory — the statistics window (owner 2026-07-16).**
   A right-click sibling of the Encyclopedia showing CHARTS over
   the long data (Session 17): season-duration oscillations with
   per-series checkboxes (the owner's own Anno Lucis graph, live in
   the app), the light−dark envelope with the eras marked, the
   eclipse timeline, the local day-length curve; dark
   QPainter-drawn, series toggles, bundled compact JSON series.
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
6. Root registration — README.md + PROJECTS.md entries; logo copy
   `logos/DOMYWatch.svg` (already present, verify current).
7. Release — smoke the installer on a clean profile, then
   `git tag v{version}` + `gh release create` with
   `dist/DOMYWatch_Setup.exe` as the artifact.
