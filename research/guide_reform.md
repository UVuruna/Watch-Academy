# The Guide Reform — Concept

DOCUMENT ONLY. This is the draft the coordinator turns into a rendered
presentation for the owner's approval; no Guide code, page, caption or asset
is touched here (owner order, 2026-08-06). English only. Every audit claim
below carries its file/line evidence; anything not directly verified is
marked UNVERIFIED.

Read first, all fully: [Guide Redesign and Shot List](guide_shotlist.md)
(the old plan — now shown to be TWICE obsolete, see §1.3), [The Ring Rework
Ledger](ring_rework.md), [Crown Content Dossier](crown_content.md) §3, the
Encyclopedia's `config/encyclopedia_tree.py` + `app/encyclopedia/` (the
whole → theme → article model this reform borrows), and the live app —
`app/controller.py`'s menu, `app/watch_face/` (nine sections), and
`app/settings_dialog/` (now three sections).

---

## Table of Contents

- [1. Audit](#1-audit)
- [2. The New Shape](#2-the-new-shape)
- [3. The Shot Pipeline](#3-the-shot-pipeline)
- [4. Migration & Effort](#4-migration--effort)
- [5. Open Questions for the Owner](#5-open-questions-for-the-owner)

---

<a id="1-audit"></a>
## 1. Audit

### 1.1 What "the Guide" is today (architecture)

The Guide is **not a window anymore**. Owner decision, Session 27
(2026-07-28): *"jedno mesto za čitanje svega"* — it was folded into the
Encyclopedia as a topic card. `app/controller.py:3076-3084` (`_open_guide`):

> "📖 Guide… — the help book is a CARD in the Encyclopedia now... The menu
> entry survives as the SHORTCUT the owner asked for: it opens the
> Encyclopedia straight on that card, instead of raising a second reader
> with its own layout for the same content (Rule #6 — the standalone
> GuideDialog is retired, not kept alongside)."

`_guide_topic()` (`app/encyclopedia/builders.py:577-619`) builds it: reads
`assets/instrument/guide/pages.json` (14 pages) + `captions.json`, turns
each PAGE into one Encyclopedia ENTRY. It is seated in the **"instrument"**
whole alongside Week / Instrument / Era / Months
(`config/encyclopedia_tree.py:64-74`), and it is sealed with exactly **one**
variant — `topic["variants"] = (("", 0, 14),)` via `_seal_variants()`
(`app/encyclopedia/tree.py:876-881`) — so today it is a flat 14-page book
with no internal structure at all: the exact "flat chapter list" the
owner's brief objects to.

### 1.2 The 14 pages today, chapter by chapter

Source: `assets/instrument/guide/pages.json` + `captions.json` (both read
in full).

| # | Title | Images | Verdict |
|---|-------|--------|---------|
| 1 | One Dial, One Whole Day | dial_default | Accurate, general orientation |
| 2 | The Four Pointers | Prism, Seasons, Compass, Trinity | Accurate for the four shown |
| 3 | The Two Wheels | Aurora, Calendar | Accurate |
| 4 | The Archetypes | archetype_prism, archetype_reveal | Accurate |
| 5 | The Dial Speaks — Hover Cards | earth_card, tetramorph_hover | Accurate, narrow |
| 6 | Three Metals, One Theme | metal_gold/bronze/silver | **Stale** — a 4th look ("Colored") has existed since 2026-07-12, never shown |
| 7 | The Dollar Ring and the Crown Text | mason_g_crown_text | Accurate text (kept current through the Mason→Dollar rename), but shows only 1 of 6 presets and never mentions the picker or hovers |
| 8 | Eclipses on the Dial | eclipse_solar, eclipse_lunar | Accurate |
| 9 | Time Travel and Quick Jump | time_travel, quick_jump | Accurate |
| 10 | The Observatory | observatory_full | Accurate |
| 11 | Observatory — Zoom and Enlarge | observatory_zoom, observatory_enlarge | Accurate |
| 12 | The Encyclopedia | encyclopedia_gallery | **Stale** — describes a flat single gallery; the Encyclopedia has had a 3-level Home→Themes→Article structure since 2026-07-28 |
| 13 | Encyclopedia — the Chapters | encyclopedia_eclipse, moon_phases_page | Accurate |
| 14 | Settings | settings_nav | **Confirmed wrong** — describes a dialog with Display/Colors/Themes sections that no longer exist |

**The dating makes the whole picture legible.** `pages.json`'s own note:
*"REBUILT 2026-07-20... the July placeholder slides retired"* — the
current 14 pages date from 2026-07-20. Two structural reworks landed
**after** that date and **before** today (2026-08-06), and the Guide has
not been touched for either:

- **The Encyclopedia's Home → Themes → Article rework** (Session 27,
  sealed 2026-07-28, later grown to nine wholes 2026-07-29) — the exact
  model that then absorbed the Guide itself as a card, eight days after
  the Guide's screenshots were taken.
- **The Watch Face window consolidation** ("Phase 6 FINAL cleanup",
  commit `4f7d288`, 2026-08-05) — the old Design/Pointer Theme/Slot Theme
  menus and the Settings dialog's Display/Colors/Themes sections were all
  **deleted outright** and replaced by one non-modal "Watch Face…" window
  with nine sections. The Settings dialog now has three sections
  (Location, Language, System) plus a hidden Custom-art mode. Every page
  in the Guide that shows a menu path (chapter 7's ring, chapter 14's
  settings) is describing a UI that has since been deleted.
- **The Ring/World-Mode rework** (2026-08-06, this session's own subject) —
  Geocentric/Heliocentric modes, live-rendered numeral bands, six ring
  presets with a card picker, CHI + ceramic, crown-text hovers — landed
  the same day this document was written, entirely after the Guide's last
  touch.

### 1.3 `guide_shotlist.md` is not stale — it is superseded twice over

`research/guide_shotlist.md` (last touched commit `12691ee`, 0.14.362) is
usually the natural "old redesign plan" to revive, but it cannot be — it
was **never implemented**. Its whole 30-chapter/37-shot plan assumes the
pre-July right-click menu (**Design** ▸ Pointer/Ring/Umbra/Hands/Size,
**Theme** ▸ Earth/Day slot/Info slot) — a menu structure that a *different,
later* rebuild round replaced: `research/prompts/guide/GUIDE_SPISAK.md`
(commit `8ae7c44`) is what the shipped 14-page Guide was actually built
from, on 2026-07-20, and it explicitly calls the July slides "placeholder"
and retires them. `guide_shotlist.md`'s own filenames (`54_menu_top_level`
… `90_settings_system`) do not exist anywhere on disk. **Both the Design/
Theme menu it documents AND the Day-slot/Info-slot model it documents are
now gone from the app** (§1.4) — the plan is not merely outdated content,
its entire premise (the menu it screenshots) no longer exists. It should
not be revived; it is superseded reading only, kept for its careful
per-chapter *prose* voice as a style reference (§4).

### 1.4 Post-rework features the Guide does not cover, or covers wrongly

Every claim below has direct evidence; the Explore agent's parallel audit
(commit `0021137` HEAD) cross-checked and corroborated all of it
independently.

| Feature | Evidence it exists | Evidence Guide doesn't cover it |
|---|---|---|
| **Geocentric/Heliocentric world modes + night inversion** | `config/dial.py:586-591` `WORLD_MODES`, `WORLD_MODE_LABELS`; `app/watch_face/numerals.py:94-122` `_mode_group`; `render/layers/ring.py`, `core/world.py`; `tests/test_world_mode.py` | No "Geocentric"/"Heliocentric"/"Mode" string anywhere in `captions.json` (read in full) |
| **Live-rendered numeral bands** (outer/inner face, size, seating, relief, live crown) | `render/layers/ring.py:1-129`, `render/numeral_bands.py`; 9 user settings in `app/watch_face/numerals.py` (Mode, Ring face, Numeral size ×2, Outer ring size, Seating, Relief style, Depth, Light, Darkness, Contact blur, Border, Crown face, Time format) | No mention anywhere; ch. 6/7's screenshots imply the pre-rework fixed-plate ring |
| **The six ring presets + card picker** (DOMY/LOOP/Dollar/The One/Templar/CHI) | `Database/ring_presets.json` (6 entries, `about`/`legend`/`crown_text` fields); picker UI `app/watch_face/ring.py:89-121` `_preset_gallery` | Ch. 7 shows only Dollar, as a static plate — never the picker, never the other five |
| **CHI + ceramic finish** | `Database/ring_presets.json`: CHI, `"thematic": "ceramic"`; `config/constants.py:955,936,1006` | Zero mentions |
| **Crown-text hovers + letter alphabet-ordinal hovers** ("one term, one hover") | `Database/ring_presets.json` `crown_text[].reading`, `legend[].reading` fields wired; `render/compositor.py:2686-2853` reads them at hover time; content shipped from `crown_content.md` §1-2 (commit `9389405`) | Ch. 7's caption describes the ring's LOOK, never that hovering a crown word or a letter opens its own reading |
| **The Rose pointer** (7th pointer, 24 seats, added 2026-07-27) | `config/registry/pointers.py:76-79`; `config/constants.py:422` `"rose": "Rose"` | Ch. 2/3 show only 6 pointers (Prism/Seasons/Compass/Trinity/Aurora/Calendar) — Rose has never appeared in any Guide draft, including `guide_shotlist.md`'s "Five Pointers" |
| **The Watch Face window itself** (9 sections replacing the old menu tree) | `app/watch_face/window.py:37-47` `_SECTIONS`; opened by the single "🕹️ Watch Face…" menu entry, `app/controller.py:2863-2867` | Named nowhere in the Guide; ch. 6/7/14 imply settings live in menus/dialogs that were deleted the same round this window was built |
| **Weekday theme "Colored" look (4th metal)** | `config/constants.py:1262-1264` `THEME_METALS = ("gold","bronze","silver","colored")`, since 2026-07-12 | Ch. 6 shows only 3 |
| **Face Layout / subdials / the content tree** (replaces the old fixed Day-slot/Info-slot pair) | `app/watch_face/themes.py` — Full face / 1 / 2 / 3 subdials, slot medal picker, `theme_tree.py` content tree | No coverage — the Guide has never shown this (it postdates even `guide_shotlist.md`'s Day/Info-slot proposal, which is itself now obsolete) |
| **Weekday theme roster (35 themes today)** | `config/constants.py:1255` `WEEKDAY_THEMES = registry.THEMES`; groups in `config/registry/week.py:66-77` (Ancient Gods, Society, Scripture, Gaming — WoW/Cyberpunk, Films — Star Wars, Animals, Inner Wheel, Arcana) | The Guide has never shown more than 4 themes at once (ch. 2's old shot list assumed 11; today there are 35, including three entire franchise casts) |
| **Multi-Watch (Add/Remove Watch)** | `app/watch_manager.py`, `app/__about/watch_manager.md`, added 2026-07-21 | No mention anywhere, in any Guide draft |
| **Current right-click menu** (Watch Face…/Visible/Names/Legend/Solar rotation/Archetype/Click-through/Add-Remove Watch/Show) | `app/controller.py:2766-3061` (`_build_menu`, read in full) | The Guide has never had a menu screenshot, in either its current or its `guide_shotlist.md`-proposed form |
| **Settings dialog's real shape (Location/Language/System only)** | `app/settings_dialog/dialog.py:1-32,66-72` | Ch. 14's caption names Display/Colors/Themes as if still there — a direct, confirmed inaccuracy |

**Content that exists and is ready to paste in, unused anywhere yet:**
the two GEOCENTRIC/HELIOCENTRIC passages in `crown_content.md` §3 are
written for exactly this purpose (*"The GUIDE gets a short passage per
mode"*, `ring_rework.md` §1) and are confirmed **not** wired into
`captions.json`, `Database/encyclopedia.json`, or anywhere else — only a
short tooltip-length paraphrase lives in `app/watch_face/numerals.py:109-115`.
Likewise the CHI Encyclopedia article draft in `crown_content.md` §4
(~400 words) is confirmed absent from `Database/encyclopedia.json` and
`research/theme_staging.md` — unwired anywhere, ready reuse for both the
Guide and a future CHI Encyclopedia page.

### 1.5 A pre-existing gap the rework audit doesn't touch: content the 2026-07-20 rebuild dropped

Comparing the OLD ~16-page July Guide (`guide_shotlist.md`'s own
"why a redesign" section lists its images: `01_day-night`,
`07-10_umbra_*`, `11_earth-moon`, `12/13_*_legend`, `14_diamond_legend`,
`15-18_day/night/dawn/dusk_legend`) against the 14 pages that actually
shipped 2026-07-20 shows that **none of the Umbra, Earth/Moon-legend, or
Day/Night/Twilight-legend pages survived the rebuild** — confirmed by a
full read of the current `assets/instrument/guide/` directory (26 image
files, none named `umbra_*`, `earth_legend`, `moon_legend`,
`diamond_legend`, or `*_legend` for day/night/dawn/dusk) and of
`captions.json` (the word "umbra" does not appear). This is a real,
separate gap from the post-rework staleness above — basic dial-reading
material (how to read the night-shading wheel, how the Diamond legend
works, what the Day/Night/Dawn/Dusk arcs mean) is currently taught
**nowhere** in the shipped app.

---

<a id="2-the-new-shape"></a>
## 2. The New Shape

### 2.1 The navigation-model decision (needs the owner's word — see §5)

The Encyclopedia's own model is **Home (9 wholes, no scroll) → Themes
(the whole's own cards, scrolls) → Article (page slider + Previous/Next,
with a variant switcher `◀ Section ▶` beside the title for a theme that
carries several registers of one subject)** — `app/encyclopedia/dialog.py`
header comment, `config/encyclopedia_tree.py` (`WHOLES`, `VARIANT_SOURCES`).
The variant switcher is not cosmetic: `app/encyclopedia/reader.py:171-186`
already implements exactly "walk sections, keep your place, ◀▶ jumps
between them, Next/Previous reads straight through all of them in order" —
and the machinery is proven on five existing topics (Eclipses Solar/Lunar,
Bible/Bible II/Bible Dark, Creeds/Ancient religions, and the three
franchise casts). `reader.py:172`'s own comment even says Next/Previous
*"wraps around like the Guide pages"* — the reader was written with the
Guide's flat-book reading habit already in mind.

Two ways to give the Guide the "levels grouped by relatedness" the brief
asks for:

- **Option A — Sections as variants (recommended).** The Guide stays ONE
  topic card, seated where it is today (the "instrument" whole). Its
  pages group into named SECTIONS — the units in §2.2 below — and each
  section becomes one variant, exactly like Eclipses' Solar/Lunar split
  today. A reader opens the Guide, sees `◀ First Steps ▶` beside the
  title, can jump straight to any section, or just press Next and read
  the whole book front to back — sections included. **Zero new UI code**:
  `_guide_topic()` needs to compute `variants` from the pages' own section
  boundaries the same way `VARIANT_SOURCES` does for merged topics, and
  the existing switcher, breadcrumb and pager handle everything else
  unchanged.
- **Option B — the Guide gets its OWN mini-gallery, one level deeper.**
  Truer to the letter of "levels... not a flat chapter list": clicking the
  Guide card would open a small Themes-style gallery of section cards
  (mirroring Home → Themes exactly), and only THEN the page slider. This
  is a closer literal copy of the Encyclopedia's own three levels, but it
  is new UI — a second screen type the Guide alone would use, since no
  other topic in the Encyclopedia nests a gallery inside a single card.

Both satisfy "resemble the Encyclopedia" and "not a flat chapter list."
Option A costs a data-shape change only (reuses code that exists and is
tested); Option B costs a new screen. This document does not pick between
them — see [Open Question 1](#5-open-questions-for-the-owner).

### 2.2 The proposed sections

Nine sections, derived from where the app's own UI groups things today —
not copied from `guide_shotlist.md`'s pre-rework Design/Theme split. Each
section lists its pages; each page states its one-line purpose and the
screenshot(s) it needs (full recipes in §3.3).

**A. First Steps** (3 pages)
1. *Welcome to DOMY* — what the dial is, the 24h face, noon-top/midnight-
   bottom orientation. Shot: `dial_default` (REUSE).
2. *Moving and Closing the Dial* — click-drag to move (native OS move),
   Exit; the Win+D fact (owner-verified behavior, not a bug). Text only,
   no shot.
3. *Opening the Menu* — right-click the dial or the tray icon, same tree
   either place; today's flat top-level shape (Watch Face…/Visible/
   Names/Legend/Solar rotation/Archetype/Click-through/Add-Remove Watch/
   Settings…/Encyclopedia…/Observatory…/Guide…/Time Travel…/Shortcuts…/
   Exit). Shot: `menu_top_level` (NEW — this UI has never been screenshot
   in any Guide draft).

**B. Reading the Dial** (5 pages)
4. *The Seven Pointers* — Prism, Seasons, Compass, Trinity, Aurora,
   Calendar, **Rose**. Shots: 6 REUSE (`pointer_Prism/Seasons/Compass/
   Trinity/Aurora/Calendar`) + 1 NEW (`pointer_Rose`).
5. *The Umbra — Your Night Wheel* — the night-shading wheel, Fine (16
   shades)/Coarse (13 shades)/Gradient forms, contrast. Shot:
   `umbra_form_contrast` (NEW — restores content the 2026-07-20 rebuild
   dropped, §1.5).
6. *The Two Travelers* — Earth and Moon markers, their hover cards. Shots:
   `earth_card` (REUSE) + `moon_card` (NEW — restores the old
   `moon_legend` concept).
7. *Day, Night and the Twilights* — reading the four arc colors. Shot:
   `arc_legends` (NEW — restores the old day/night/dawn/dusk legend
   pages).
8. *The Archetypes* — lancet windows, the Omega double-click reveal. Shots:
   `archetype_prism`, `archetype_reveal` (both REUSE).

**C. The Two World-Modes** (3 pages)
9. *Geocentric (Ptolemy)* — the Ptolemy passage, verbatim from
   `crown_content.md` §3. Shot: `mode_geocentric` (NEW).
10. *Heliocentric (Copernicus)* — the Copernicus passage, verbatim from
    `crown_content.md` §3. Shot: `mode_heliocentric_day` (NEW).
11. *The Night Turn* — the flip animation, night vs day heliocentric.
    Shots: `mode_heliocentric_night` + optional `mode_night_turn_sequence`
    (NEW).

**D. The Ring** (5 pages)
12. *Choosing a Ring* — the preset picker (name + mini preview + About).
    Shot: `ring_picker` (NEW).
13. *The Six Rings* — DOMY, LOOP, Dollar, The One, Templar, CHI at a
    glance, one line each from their About text. Shots: `mason_g_crown_
    text`→rename/REUSE for Dollar, 5 NEW (`ring_domy`, `ring_loop`,
    `ring_the_one`, `ring_templar`, `ring_chi`).
14. *Letters, Finish and Ceramic* — gold/silver/bronze/thematic, CHI's
    ceramic ramp. Shot: `ring_finishes` (NEW).
15. *The Crown Speaks* — hovering a crown word or a ring letter opens its
    own reading (the "one term, one hover" law). Shots: `crown_hover_
    annuit`, `letter_hover_ordinal` (NEW).
16. *The Inner Band and Custom Rings* — the 8-tile inner gallery, building
    your own ring. Shot: `ring_inner_gallery`, `custom_ring` (NEW).

**E. The Numeral Bands & the Crown** (3 pages)
17. *The Two Bands* — outer (hour) vs inner (minute) band, faces, sizes,
    seating. Shot: `numerals_bands` (NEW).
18. *Relief* — Cast/Extrude/Emboss, depth, light, darkness. Shot:
    `numerals_relief` (NEW).
19. *The Live Crown* — the digital-time arc, `hh:mm` vs `12h 35min`, only
    on The One and Templar. Shot: `live_crown` (NEW).

**F. Weekday Themes** (4 pages)
20. *One Theme, Many Faces* — the 35-theme roster grouped exactly as the
    Watch Face window groups it (Ancient Gods, Society, Scripture,
    Gaming, Films, Animals, The Inner Wheel, Arcana). Shot: `theme_tree`
    (NEW).
21. *Four Metals* — gold/bronze/silver/**colored**. Shots: `metal_gold/
    bronze/silver` (REUSE) + `metal_colored` (NEW).
22. *Face Layout and Complications* — Full face/1/2/3 subdials, the slot
    medal picker (replaces the old Day-slot/Info-slot pair entirely).
    Shot: `face_layout` (NEW).
23. *Theme Rotation* — cycling checked themes, per-theme metal, Follow
    ring color. Shot: `theme_rotation` (NEW).

**G. Dressing the Dial** (3 pages)
24. *Hands* — the hand-pack gallery, custom hands. Shot: `hands_gallery`
    (NEW — `guide_shotlist.md`'s old proposal for this chapter was never
    shot).
25. *Size and Element Scales* — diameter presets, Earth/Moon/
    Complications/Indices/Crown Text/Hover-enlarge sliders. Shot:
    `size_scales` (NEW).
26. *Colors and Opacity* — palette, ring tint, saturation, clock/ring
    opacity. Shot: `colors_opacity` (NEW).

**H. The Sky and Time** (4 pages)
27. *Eclipses on the Dial* — REUSE `eclipse_solar`, `eclipse_lunar`.
28. *Time Travel and Quick Jump* — REUSE `time_travel`, `quick_jump`.
29. *The Observatory* — REUSE `observatory_full`, `observatory_zoom`,
    `observatory_enlarge`.
30. *Multi-Watch* — Add Watch/Remove Watch, each with its own settings
    and skin. Shot: `add_watch` (NEW).

**I. The Encyclopedia and Settings** (4 pages)
31. *The Encyclopedia* — the current Home → Themes → Article shape (nine
    wholes). Shot: `encyclopedia_home` (REPLACES the stale
    `encyclopedia_gallery`).
32. *Encyclopedia — Deep Lore* — REUSE `encyclopedia_eclipse`,
    `moon_phases_page`.
33. *This Guide's Own Home* — meta page: the Guide is itself a card in
    the "The Instrument" whole; how to jump back here. Shot:
    `guide_own_card` (NEW, small).
34. *Settings: Location, Language and System* — the three real sections
    left in the Settings dialog. Shot: `settings_nav` (REPLACES the
    stale current one).

Total: **9 sections, 34 pages** (up from 1 section, 14 pages) — a smaller,
more disciplined growth than `guide_shotlist.md`'s abandoned 30 chapters,
because this shape reads off the app's OWN current groupings (9 Watch
Face-adjacent themes) instead of re-deriving one from scratch.

---

<a id="3-the-shot-pipeline"></a>
## 3. The Shot Pipeline

### 3.1 Why this can be automated now (owner brief)

The owner's standing instruction: screenshots no longer wait on him.
Agents drive the real app into the needed state, capture, clean the
background and save. The mechanics already exist in
`.claude/skills/verify/SKILL.md`: `python main.py` launched as a
background task, a Win32 driver (`SetProcessDPIAware` +
`FindWindowW`/`GetWindowRect`/`MoveWindow`/`SetCursorPos`/`mouse_event`/
`keybd_event` + `CopyFromScreen`), settings read/write at
`%APPDATA%\DOMY Watch\settings.json` (atomic, 750 ms debounce after a
move), and the ground-truthed gotchas (find the window by PID rather than
class name; always re-read `GetWindowRect` immediately before capture;
pixel-sample rather than trust `IsWindowVisible`).

### 3.2 The recipe

1. **Reach the state the fast way.** Two paths, pick per shot:
   - **Settings-file seeding** — write the exact `Settings` fields the
     shot needs (pointer, ring, world_mode, numeral_*, ring_finish, hands,
     umbra_form, …) straight into `settings.json`, then launch/relaunch.
     Fastest and most reliable for dial-only shots (no click sequence to
     get wrong); the field names for every setting used above are listed
     inline in §1.4/§2.2 with their `app/watch_face/*.py` source.
   - **Live driving** — for anything that is itself UI chrome (the
     right-click menu, the Watch Face window's sidebar, the preset
     picker, a hover tooltip), the driver must actually right-click /
     open the window / hover, since the state IS the open widget, not a
     stored setting.
   - **Time Travel for sky states** — a specific moment (a night phase for
     the Heliocentric inversion, a real eclipse date, a particular moon
     phase) is reached by driving Time Travel or Quick Jump, or by
     seeding `settings.json`'s travel fields directly if the store
     supports it (UNVERIFIED — confirm the exact field before relying on
     it; `python -m core --city NAME --at ISO` can independently confirm
     WHICH date to target, e.g. the next eclipse or a clean night moment,
     without needing the GUI open at all).
2. **Capture at the window's current `GetWindowRect`**, re-read
   immediately before each shot (skill's own documented gotcha — a
   remembered rect drifts).
3. **Clean the background.**
   - Dial-only captures need no matting: the widget already paints with
     an alpha-transparent background (the existing 26 shipped images are
     already alpha PNGs — `GUIDE_SPISAK.md`'s own status note confirms
     this for the 2026-07-20 batch), so a raw `CopyFromScreen` crop to the
     circle's own edge already is a clean transparent PNG.
   - Dialog/menu captures (Watch Face window, Settings dialog, the
     right-click menu, tray menu) are opaque windows — "cleaning" here
     means cropping tightly to the window's own rect with no desktop,
     taskbar, or dev-tool chrome in frame, per `GUIDE_SPISAK.md`'s own
     existing rule ("Bez dev okruženja u kadru").
4. **Save under the naming convention** (§3.3) into
   `assets/instrument/guide/`, flat — this folder is INSTRUMENT FURNITURE
   in the asset tree law (`assets/___assets.md`: "the furniture is owner
   hand-made, suffix-less"), not a Gemini/ChatGPT-sourced figure tree, so
   it keeps its existing flat, non-suffixed, non-tree-law naming rather
   than adopting `category/group/theme/register/look/Figura` — new stems
   just extend the SAME descriptive-snake/PascalCase vocabulary already on
   disk (`dial_default`, `pointer_Prism`, `metal_gold`).

### 3.3 The shot list

Every shot the new shape (§2.2) needs, its app-state recipe, and whether
it reuses, renames, or is wholly new relative to the 26 images that exist
today.

| Filename | Section·Page | App-state recipe | Status |
|---|---|---|---|
| `dial_default` | A1 | Launch, defaults, noon | REUSE |
| `menu_top_level` | A3 | Right-click the dial; no submenu expanded | NEW |
| `pointer_Prism/Seasons/Compass/Trinity/Aurora/Calendar` | B4 | Watch Face ▸ Pointer, pick each | REUSE (6) |
| `pointer_Rose` | B4 | Watch Face ▸ Pointer ▸ Rose | NEW |
| `umbra_form_contrast` | B5 | Watch Face ▸ Umbra & Aura, one shot per Fine/Coarse/Gradient (3 crops or 1 composite) | NEW |
| `earth_card` | B6 | Hover the Earth marker | REUSE |
| `moon_card` | B6 | Hover the Moon marker | NEW |
| `arc_legends` | B7 | Crop the day/night/dawn/dusk arc band; hover each | NEW |
| `archetype_prism`, `archetype_reveal` | B8 | Archetype toggle on; double-click Omega | REUSE (2) |
| `mode_geocentric` | C9 | Watch Face ▸ Numerals ▸ Mode = Geocentric | NEW |
| `mode_heliocentric_day` | C10 | Mode = Heliocentric, daylight moment | NEW |
| `mode_heliocentric_night` | C11 | Mode = Heliocentric, night moment (via Time Travel) | NEW |
| `ring_picker` | D12 | Open Watch Face ▸ Ring, gallery visible, no tile hovered | NEW |
| `ring_domy/loop/the_one/templar/chi` | D13 | Watch Face ▸ Ring, pick each preset | NEW (5); Dollar reuses `mason_g_crown_text` renamed |
| `ring_finishes` | D14 | Ring ▸ Finish row, one crop per gold/silver/bronze/thematic (CHI active for thematic) | NEW |
| `crown_hover_annuit`, `letter_hover_ordinal` | D15 | Hover a crown word (Dollar's ANNUIT COEPTIS) and a ring letter, tooltip in frame | NEW |
| `ring_inner_gallery`, `custom_ring` | D16 | Ring ▸ Inner group; Ring ▸ Custom ring… button | NEW |
| `numerals_bands` | E17 | Watch Face ▸ Numerals, outer+inner groups visible | NEW |
| `numerals_relief` | E18 | Numerals ▸ Relief group, one crop per Cast/Extrude/Emboss | NEW |
| `live_crown` | E19 | Ring = The One, crown group visible, both time-format picks | NEW |
| `theme_tree` | F20 | Watch Face ▸ Themes & Slots, content tree expanded one level | NEW |
| `metal_gold/bronze/silver` | F21 | Theme metal picks, existing theme | REUSE (3) |
| `metal_colored` | F21 | Theme metal = Colored | NEW |
| `face_layout` | F22 | Themes & Slots ▸ Face layout row + slot medal picker, 2-subdial state | NEW |
| `theme_rotation` | F23 | Themes & Slots ▸ rotation group, enabled with a few themes checked | NEW |
| `hands_gallery` | G24 | Watch Face ▸ Hands | NEW |
| `size_scales` | G25 | Watch Face ▸ Size | NEW |
| `colors_opacity` | G26 | Watch Face ▸ Colors + ▸ Opacity | NEW |
| `eclipse_solar/lunar` | H27 | Time Travel to a cataloged eclipse | REUSE (2) |
| `time_travel`, `quick_jump` | H28 | Open each dialog/menu | REUSE (2) |
| `observatory_full/zoom/enlarge` | H29 | Open Observatory, zoom, enlarge one chart | REUSE (3) |
| `add_watch` | H30 | Right-click ▸ Add Watch, two dials visible | NEW |
| `encyclopedia_home` | I31 | Open Encyclopedia, Home screen (9 wholes) | NEW (replaces stale `encyclopedia_gallery`) |
| `encyclopedia_eclipse`, `moon_phases_page` | I32 | Existing Encyclopedia pages | REUSE (2) |
| `guide_own_card` | I33 | Encyclopedia ▸ The Instrument ▸ Guide card, Themes-level view | NEW |
| `settings_nav` | I34 | Settings…, Location section visible | NEW (replaces stale current shot) |

**Count: 26 shots exist today; 14 REUSE unchanged, 1 renames
(`mason_g_crown_text` → `ring_dollar`, content already correct), 2 REPLACE
a now-inaccurate shot (`encyclopedia_gallery`, `settings_nav`), and 30 are
NEW.**

### 3.4 What survives from `guide_shotlist.md`

Its shot list itself does not survive (§1.3 — built for a menu that no
longer exists), but two things do: the **crop/framing conventions**
(full-dial crops to the circle's own edge; two-column theme grids; shoot
comparison pairs — e.g. the four finishes, the three umbra forms — at the
identical crop rectangle and, where sky state matters, within the same few
minutes) and its **per-chapter prose voice**, reused as a style reference
for the new pages' one-line purposes above.

---

<a id="4-migration--effort"></a>
## 4. Migration & Effort

### 4.1 Reuse — zero new writing

- **The two world-mode passages** — `crown_content.md` §3, GEOCENTRIC (118
  words) and HELIOCENTRIC (134 words), owner-approved, unused anywhere.
  Paste verbatim into pages C9/C10.
- **The CHI article draft** — `crown_content.md` §4 (~400 words), unwired
  anywhere including the Encyclopedia. Can seed page D13's CHI paragraph
  (trimmed) and separately close the Encyclopedia's own CHI debt (out of
  this document's scope, flagged for the owner).
- **17 crown-text hovers + 21 alphabet-ordinal lines** — `crown_content.md`
  §1-2 — already wired into `Database/ring_presets.json`; page D15 only
  needs to SHOW one live example, no new prose.
- **14 existing images**, unchanged (§3.3's REUSE column).
- **Section E-G's Watch Face page purposes** can draw directly on the
  module docstrings already written for `app/watch_face/*.py` (numerals,
  ring, themes, hands, size, umbra_aura) — they are unusually complete and
  already explain the "why," not just the "what."

### 4.2 Written fresh

- Sections A3, B5-B7, C (all 3), D12/14/15/16, E (all 3), F (all 4), G
  (all 3), H30, I31/33/34 — roughly 25 of 34 pages' prose is new.
- Two restorations (B5 Umbra, B7 arc legends) are not "new content" in
  spirit — they rewrite dropped July material for the current app, so
  they can lean on the OLD captions (still readable in git history at the
  pre-2026-07-20 commit) rather than starting blank.

### 4.3 Wave plan (rough scope, for the coordinator to size)

1. **Wave 0 — the shape decision.** Owner answers §5's open questions
   (navigation model, depth, any cuts). Blocks every later wave.
2. **Wave 1 — wiring session.** Implements whichever navigation option is
   chosen (§2.1) in `app/encyclopedia/builders.py`/`tree.py` and
   `pages.json`'s own shape (flat list → sectioned list). Small, code-only.
3. **Wave 2 — shot wave (agents, parallel-safe).** Runs the §3.3 shot
   list. The REUSE/RENAME/REPLACE rows (17 shots) can run alongside the
   30 NEW rows since they touch disjoint files; NEW rows that share a
   Watch Face section (e.g. all of E17-E19 read Numerals) are cheaper run
   together in one drive session than three separate launches.
4. **Wave 3 — content wave (agents, parallel-safe by section).** Nine
   sections, roughly independent — each is a self-contained brief once its
   screenshots exist. Sections C and D lean most heavily on already-
   approved text (§4.1) and are the cheapest to close first.
5. **Wave 4 — wiring session.** Pastes the finished section text +
   filenames into `pages.json`/`captions.json`, runs
   `tests/test_docs_coverage.py`-equivalent sanity (no dedicated Guide
   guard exists today — worth asking whether one should, see §5).

---

<a id="5-open-questions-for-the-owner"></a>
## 5. Open Questions for the Owner

1. **Navigation model — Option A (reuse the variant switcher, zero new
   UI) or Option B (a dedicated mini-gallery of section cards, closer to
   the Encyclopedia's literal three levels but new screen code)?** §2.1
   lays out both. Option A is materially cheaper and reuses tested code;
   Option B reads closer to "levels" in the strictest sense. This is a
   real product decision, not a style nit — it changes how much of Wave 1
   is content-shaping versus new interaction design.
2. **Depth per section.** §2.2 proposes 34 pages across 9 sections — is
   that the right size, or should some sections (F Weekday Themes in
   particular, given 35 themes behind one page) get their own sub-gallery
   rather than a single overview page? The Encyclopedia itself splits
   "The Gods" and "The Worlds" into several theme cards each; the Guide's
   page 20 currently proposes to compress that same breadth into one
   page.
3. **Tone for the restored content (B5 Umbra, B7 arc legends).** These
   rewrite pages the 2026-07-20 rebuild dropped. Should they match the OLD
   pre-rebuild captions' voice as closely as possible (continuity for a
   returning reader), or should they be rewritten fresh in whatever voice
   the new sections settle into (consistency across the whole new book)?
4. **How much of the ring's doctrinal weight belongs in the Guide vs. the
   Encyclopedia.** The Guide's job is orientation; the Encyclopedia's is
   depth. Page D13 ("The Six Rings") could stay a one-line-each overview,
   or could carry each preset's full About text verbatim (§4.1 has all
   six ready). A full About per preset risks turning an orientation page
   into a second Encyclopedia article; a one-liner risks under-selling
   six presets the owner clearly cares about individually. Which way?
5. **Whether "This Guide's Own Home" (I33) is worth a page at all.** It is
   a meta page explaining that the Guide is itself an Encyclopedia card —
   useful once, easily skipped forever after. Keep it as page 1 of the
   whole book instead (so it's the very first thing a first-time reader
   sees, before "Welcome to DOMY"), fold it into A1, or drop it?

---

## Connections

### Uses
- [Guide Redesign and Shot List](guide_shotlist.md) — the superseded plan,
  read for its crop conventions and prose voice only (§1.3, §3.4)
- [The Ring Rework Ledger](ring_rework.md) — the rework this reform must
  fold in (§1.4)
- [Crown Content Dossier](crown_content.md) — the ready-to-reuse text
  (§4.1)
- `config/encyclopedia_tree.py`, `app/encyclopedia/` — the whole → theme
  → article model this reform borrows (§2.1)
- `app/watch_face/`, `app/controller.py`, `app/settings_dialog/` — the
  current UI surface the audit (§1) and shot pipeline (§3) are built from

### Used by
- The coordinator, to build the owner's approval presentation from this
  draft — no code, page, caption or asset changes originate here
