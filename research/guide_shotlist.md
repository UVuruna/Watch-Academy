# Guide Redesign — Chapter Plan and Shot List

## Table of Contents

- [Why a Redesign](#why-a-redesign)
- [What the Task Brief Got Slightly Wrong](#brief-corrections)
- [Baseline Defaults for Every Shot](#baseline)
- [Chapter Plan](#chapter-plan)
- [The Shot List](#shot-list)
- [Appendix — Reused Images (No Reshoot Needed)](#appendix-reused)
- [Appendix — Naming and Crop Conventions](#appendix-conventions)

---

<a id="why-a-redesign"></a>
## Why a Redesign

The shipped Guide (`assets/guide/pages.json`) has **16 pages**, not 13 — later
commits after "Guide grows to 13 chapters" (0.14.113) folded in a second
color-worlds page, the custom-hands page and a settings split without a
title-count bump in any commit message. That is a minor bookkeeping note;
the real reason for a redesign is that the app's OPTION SURFACE grew
substantially on **2026-07-12**, all AFTER the Guide was last touched:

- The right-click menu was reorganized into **Design** (Pointer + palette
  style, Ring + letter finish, **Hands** — brand new, Umbra, Size) and
  **Theme** (exactly three entries since 0.14.167: Earth + date, **Day
  slot** and **Info slot** — the theme list with its metals and the Names
  switch lives INSIDE each slot's own identical Weekday submenu,
  replacing the old separate Weekday entry and the Slots wrapper). None
  of this structure exists in the current Guide.
- **Aurora**, the fifth pointer (arm-less, the day painted in bands), has
  no chapter, no palette page, and no menu mention anywhere in the Guide.
- The weekday **Colored** look (a fourth metal alongside Gold/Silver/
  Bronze on Greek gods, Norse gods and Professions) ships art on disk
  (`assets/weekday/<theme>/colored/`) but is never shown.
- Six of the eleven weekday themes are entirely absent from the Guide:
  Planet signs, Egyptian gods, Slavic gods, Alchemy, Japanese week,
  Religions II.
- The **Ascendant** badge, the Info slot's **second weekday theme**
  (pairing e.g. Norse left / Greek right), Theme Rotation, autostart,
  Solar rotation and Click-through are all live features with zero
  Guide coverage.
- The ring's own **tick anatomy** (the 360-arrow band the owner hovers
  for the Day/Year/Moon reading) has never been explained at all.

This document keeps every still-accurate chapter, folds new material into
the chapters it naturally extends, and adds the chapters the app has
outgrown the Guide without.

---

<a id="brief-corrections"></a>
## What the Task Brief Got Slightly Wrong

Two corrections, made from reading the live code rather than repeating
the brief, per the "accuracy > speed" project rule:

1. **Language and Theme Rotation are not right-click menu items.** They
   are groups inside the **Settings dialog** (`app/settings_dialog.py`).
   The right-click menu's own top-level toggles, after Elements, are
   only **Legend**, **Solar rotation** and **Click-through** — then
   Settings…/Time Travel…/Encyclopedia…/Guide…/Exit. The chapter plan
   below reflects this; a "Settings: Theme Rotation" and a "Settings:
   Language and System" chapter cover them where they actually live.
2. **Size has five presets, not three.** `defaults.SIZE_PRESETS =
   (360, 540, 720, 1080, 1440)`.

A third finding, from actually opening `assets/ring/domy.png` rather
than trusting the brief's tick-count phrase verbatim: the ring's 24
hour-tick tier is **12 bold-white ticks at the odd hours + 11 short
gray ticks at the remaining even hours + ONE unique arrow-shaped mark
at the 12h/noon position** (reserved for the "M" letter that overlays
it at render time — the raw face art leaves it blank under the arrow).
`12 + 11 + 1 = 24`, and `24 + 48 (medium, half-hour) + 288 (thin,
five-minute) = 360`. The brief's "12 white … + 12h" undercounts by
one tick; Chapter 3 below writes the corrected anatomy. This is a pure
documentation refinement, not a code-vs-asset conflict, so no owner
decision is needed — just noting the correction for the record.

---

<a id="baseline"></a>
## Baseline Defaults for Every Shot

Unless a row says otherwise, shoot at the app's own install defaults
(`app/settings_store.py`) so screenshots stay internally consistent:

| Setting | Value |
|---|---|
| Diameter | 720 px |
| Location | Belgrade (44.82, 20.46, Europe/Belgrade) |
| Pointer | Prism (hexa) |
| Palette style | Paint |
| Ring / Finish | DOMY / Gold |
| Hands | STEEL |
| Umbra form / contrast | Gradient / Dark |
| Earth style | Atmosphere |
| Weekday theme | Planets |
| Solar rotation | On |
| Elements (Earth/Moon/Weekday/Pointer/Colorful/Seconds) | All on |
| Legend / Click-through | Legend on, Click-through off |
| Language | English |

Every row below only lists what **differs** from this table. "Full
dial" means the whole circle, cropped tight to its edge (as the
existing 01/07-10/11 images already are). "Close crop" means a
zoomed region, as the existing 14/22/23 images already are. Menu
screenshots should be tall enough to show the full open submenu chain
in one shot (Windows: hold PrtScn while cascading, or use Snipping
Tool's delayed capture).

---

<a id="chapter-plan"></a>
## Chapter Plan

30 chapters (up from 16). Status: **REUSE** = existing image(s), no
change; **CHANGED** = existing chapter gains new image(s); **NEW** =
chapter did not exist before.

| # | Title | Status | Images (✦ = new) |
|---|---|---|---|
| 1 | One Dial, One Whole Day | REUSE | 01_day-night |
| 2 | Opening the Menu | NEW | ✦54_menu_top_level, ✦55_tray_menu |
| 3 | The Ring Tick Band — Anatomy of 360 Arrows | **NEW, mandatory** | ✦56_tick_anatomy, ✦57_tick_hover |
| 4 | The Five Pointers | CHANGED | 02, 04, 05, 06, ✦58_pointer_aurora |
| 5 | Two Color Worlds | CHANGED | 47-52, ✦59_palette_aurora_paint, ✦60_palette_aurora_light |
| 6 | The Umbra — Your Night Wheel | CHANGED | 07-10, ✦61_umbra_coarse, ✦62_umbra_gradient_form |
| 7 | The Ring — Faces, Finish and Numbers | CHANGED | 19, 22, 23, 36, ✦63_ring_domy_bronze, ✦64_ring_numbers_seal, ✦65_menu_design_ring |
| 8 | Hands — Classic, Steel and Your Own | NEW | ✦66_hands_classic, ✦67_hands_steel, ✦68_menu_design_hands |
| 9 | The Dial's Own Size | NEW | ✦69_menu_design_size, ✦70_size_compare |
| 10 | Theme: The Earth's Two Looks | NEW | ✦71_menu_theme_earth, ✦72_earth_clean_vs_atmo |
| 11 | Two Travelers | REUSE | 11_earth-moon |
| 12 | Reading the Travelers | REUSE | 12_earth_legend, 13_moon_legend |
| 13 | The Diamond Legends | REUSE | 14_diamond_legend |
| 14 | Day, Night and the Twilights | REUSE | 15-18 |
| 15 | Seven Days, Eleven Faces I | CHANGED | 24, 25, 26, ✦73_weekday_planet_signs, ✦74_weekday_egypt, ✦75_weekday_slavic |
| 16 | Seven Days, Eleven Faces II | CHANGED | 27, 28, ✦76_weekday_alchemy, ✦77_weekday_japan, ✦78_weekday_religion_alt |
| 17 | One Theme, Four Metals | NEW | ✦79_weekday_greek_colored, ✦80_menu_theme_weekday_metal |
| 18 | The Day Slot | CHANGED | 29, 30, ✦81_slot_ascendant, ✦82_menu_theme_slots_day |
| 19 | The Info Slot | NEW | ✦83_slot_info_time, ✦84_slot_info_paired_weekday, ✦85_menu_theme_slots_info |
| 20 | Elements — Every Switch | CHANGED | 35_menu_elements, ✦86_colorful_on_off |
| 21 | Legend, Solar Rotation, Click-through | NEW | ✦87_solar_rotation_off, ✦88_tray_click_through |
| 22 | One Clock, Any Color | REUSE | 41-46 |
| 23 | The Settings Window | REUSE | 40_settings_window |
| 24 | Settings: Location, Opacity, Element Sizes | REUSE | 31, 32, 33 |
| 25 | Settings: Palette and Ring Tint | REUSE | 37, 38 |
| 26 | Settings: Your Own Ring and Hands | REUSE | 34, 53 |
| 27 | Settings: Theme Rotation | NEW | ✦89_settings_theme_rotation |
| 28 | Settings: Language and System | CHANGED | 39, ✦90_settings_system |
| 29 | Time Travel | REUSE | 21_time_travel |
| 30 | Two Things Worth Knowing | NEW (text only) | none |

### Chapter briefs

**2 — Opening the Menu.** Right-click the dial anywhere inside its
circle, or right-click the tray icon — both open the exact same tree.
Two groups organize everything: **Design** is how the instrument
looks, **Theme** is what the figures on it show. This page orients the
reader before every later chapter says "found under Design ▸ …".

**3 — The Ring Tick Band.** The outer band carries four tiers of
tick: 12 bold white glowing ticks at the odd hours, 11 short gray
ticks at the remaining even hours, one unique arrow mark at 12h/noon
(reserved for the ring letter), 48 medium half-hour ticks and 288
thin five-minute ticks — 360 in total, one every four minutes of the
day. Hovering any of them opens a Day/Year/Moon reading of that exact
angle on all three wheels at once.

**4 — The Five Pointers.** Unchanged text for Prism/Seasons/Compass/
Trinity; adds Aurora, the arm-less fifth pointer that paints the day
itself in bands (a dawn hue, five day hues spanning the real
sunrise-sunset arc, a dusk hue) and is always solar-rotated regardless
of the Solar rotation toggle.

**5 — Two Color Worlds.** Unchanged for the four geometric pointers;
adds Aurora's own Paint and Light palettes (7 hues each).

**6 — The Umbra.** Unchanged contrast explanation; adds the two forms
not yet shown — Coarse (13 shades) and the seamless Gradient — beside
the existing Fine examples, making the Form × Contrast matrix explicit.

**7 — The Ring: Faces, Finish and Numbers.** Unchanged DOMY/MORPH gold
and silver explanation; adds the third bundled ring **Omega** (a Seal
layout wearing digits 12/16/20/Ω/4/8 instead of letters — a clean
demonstration that the Seal always wears ONE metal on all six), the
**Bronze** finish (never shown before, though its art has shipped since
2026-07-12), and the Design ▸ Ring menu itself.

**8 — Hands.** Brand new: the two bundled packs (Classic, teardrop
shapes; Steel, the current default) live under Design ▸ Hands, and
Settings ▸ Custom hands turns any three upward-pointing PNGs into a
third pack with automatic tip-to-pivot sizing.

**9 — The Dial's Own Size.** Distinct from the Settings ▸ Element
sizes sliders (chapter 24): Design ▸ Size sets the WHOLE window's
diameter across five presets, 360 to 1440 px.

**10 — Theme: The Earth's Two Looks.** Clean vs Atmosphere, and the
Date label toggle (grayed out below 540 px) — a menu this Guide has
never shown despite existing since M5.

**15/16 — Seven Days, Eleven Faces (I and II).** The old "Seven Days,
Seven Faces" page showed five of eleven themes. Split across two pages
(six themes each minus the three carried over — Planets, Greek, Norse
stay in part I with the three brand-new small themes; Religions and
Professions stay in part II with the three remaining new themes) to
keep each page's grid at a readable six images.

**17 — One Theme, Four Metals.** New: Greek gods, Norse gods and
Professions each wear Gold, Silver, Bronze or the freshly-shipped
**Colored** full-art look — chosen per theme via Theme ▸ Day slot ▸
Weekday ▸ <Theme> (the identical dropdown repeats under Info slot ▸
Weekday), independent of the ring's own finish unless "Follow ring
color" is checked in Settings.

**18 — The Day Slot.** Renamed from "The Compass Slot" — it is not
Compass-only. Keeps the zodiac/Chinese badge explanation, adds the
**Ascendant** (the sign rising on the eastern horizon right now,
changing roughly every two hours), and — since 0.14.167 — the
Time/Date/Day length text modes (pointer-off only) plus the Weekday
theme submenu itself: the theme list moved INSIDE the slot.

**19 — The Info Slot.** New: the OTHER bottom position — Time, Date,
Day length, a SECOND weekday theme (its own independent pick, so the
pinned layouts can read e.g. Norse on the left, Greek on the right,
both showing today), Astrology (with Text and the new Colored style)
and the Chinese year, each living wherever the Weekday or Pointer
element is off, or always on Compass/Trinity/Aurora.

**20 — Elements.** Unchanged menu screenshot; adds a Colorful on/off
comparison since "plain white transparency" is easier to show than to
describe.

**21 — Legend, Solar Rotation, Click-through.** New: the three
top-level toggles below Elements. Solar rotation OFF stands the whole
dial upright (12/24 at the top) for reading exact planet/season
positions; every other screenshot in this Guide already shows it ON
by default, so only the OFF state needs a new capture. Click-through
takes no clicks at all — recoverable only from the tray, which is why
its own screenshot is the tray menu, not the dial.

**27 — Settings: Theme Rotation.** New: cycling the checked weekday
themes on a timer, with per-theme metal defaults for the three
bronze-plate themes and a "Follow ring color" shortcut.

**28 — Settings: Language and System.** Unchanged Language box; adds
System — the single "Start with Windows" checkbox (a standard-user
registry entry, no elevation).

**30 — Two Things Worth Knowing.** Text-only, no screenshot: moving
the dial (click-drag anywhere on the circle — it's a native OS move,
correct across monitors and DPI) and the Win+D fact (Show Desktop
raises the OS's own desktop layer above every window, this one
included — the dial simply reappears the instant Show Desktop ends;
that is expected behavior, not a bug to report).

---

<a id="shot-list"></a>
## The Shot List

One row per NEW screenshot the owner needs to take (37 total, filenames
`54_…` through `90_…`). Reused images (53 of them) need no action —
see the [appendix](#appendix-reused).

<table>
<tr><th>#</th><th>Filename</th><th>How to get there</th><th>Preconditions (deltas from baseline)</th><th>Must be visible in frame</th></tr>

<tr><td>54</td><td>menu_top_level</td>
<td>Right-click anywhere inside the dial's circle.</td>
<td>Baseline. Do not expand any submenu.</td>
<td>The full top-level menu: Design, Theme, Elements, Legend, Solar rotation, Click-through, Settings…, Time Travel…, Encyclopedia…, Guide…, Exit — plus enough of the dial behind it to show it came from a right-click on DOMY Watch.</td></tr>

<tr><td>55</td><td>tray_menu</td>
<td>Right-click the tray icon in the Windows notification area.</td>
<td>Baseline.</td>
<td>The tray icon itself plus the identical top-level menu, to make the "same tree everywhere" point visually obvious next to image 54.</td></tr>

<tr><td>56</td><td>tick_anatomy</td>
<td>No menu — a close crop of the ring band.</td>
<td>Baseline. Crop the ring band spanning roughly hour 10 through hour 14 (centered on true solar noon at the top).</td>
<td>At least two bold-white odd-hour ticks (11h, 13h) either side of the unique noon arrow mark at 12h, at least one short gray even-hour tick (10h or 14h) at each end, and the fine ladder of medium/thin ticks filling the gaps between them — all four tiers in one frame.</td></tr>

<tr><td>57</td><td>tick_hover</td>
<td>Hover the mouse directly over one arrow inside the tick band (not on a hour numeral or letter).</td>
<td>Baseline. Any arrow away from 12h/0h reads best (shows a non-trivial Time/Angle pair).</td>
<td>The hovered arrow plus the Day/Year/Moon legend popup: Time + Angle + period word; Date + event/season + day/week ordinals; lunation ordinal + illumination % + phase name + cycle day.</td></tr>

<tr><td>58</td><td>pointer_aurora</td>
<td>Design ▸ Pointer ▸ Aurora.</td>
<td>Pointer = Aurora. Shoot near midday so the five day hues span a visible arc.</td>
<td>Full dial: the arm-less band pointer with its dawn/day/dusk color sweep, no diamonds, the ring visible around it.</td></tr>

<tr><td>59</td><td>palette_aurora_paint</td>
<td>Design ▸ Pointer ▸ Aurora; Design ▸ Pointer ▸ Paint palette (already default).</td>
<td>Pointer = Aurora, Palette style = Paint.</td>
<td>The Aurora band close-cropped to show its 7-hue paint sweep clearly (azure → green → yellow → orange → red → dark red).</td></tr>

<tr><td>60</td><td>palette_aurora_light</td>
<td>Design ▸ Pointer ▸ Aurora; Design ▸ Pointer ▸ Light palette.</td>
<td>Pointer = Aurora, Palette style = Light.</td>
<td>Same crop as 59 but the Light sweep (azure → cyan → green → yellow → red → dark red) for a direct paint-vs-light comparison.</td></tr>

<tr><td>61</td><td>umbra_coarse</td>
<td>Design ▸ Umbra ▸ Coarse (13 shades); Design ▸ Umbra ▸ Full contrast.</td>
<td>Umbra form = Coarse, contrast = Full (matches the existing 07_umbra_full's contrast for a clean form-only comparison).</td>
<td>Full dial, the visibly chunkier 13-shade gray wheel next to the existing Fine (16-shade) reference.</td></tr>

<tr><td>62</td><td>umbra_gradient_form</td>
<td>Design ▸ Umbra ▸ Gradient; Design ▸ Umbra ▸ Full contrast.</td>
<td>Umbra form = Gradient, contrast = Full.</td>
<td>Full dial, the seamless continuous sweep with no visible steps at all.</td></tr>

<tr><td>63</td><td>ring_domy_bronze</td>
<td>Design ▸ Ring ▸ DOMY; Design ▸ Ring ▸ Bronze letters.</td>
<td>Ring = DOMY, Ring finish = Bronze.</td>
<td>Close crop matching 22/23's framing: the M/Y/D triangle in bronze, Omega in silver (the bronze finish's accent rule).</td></tr>

<tr><td>64</td><td>ring_numbers_seal</td>
<td>Design ▸ Ring ▸ Omega.</td>
<td>Ring = Omega. Shoot once at Gold finish and, if the owner has time, again at Silver — one is enough for the Guide, both are useful for the caption text.</td>
<td>Close crop of the full ring showing all six positions (12/16/20/Ω/4/8) wearing digits instead of letters, all six in the SAME metal (the Seal's one-metal-on-all-six rule).</td></tr>

<tr><td>65</td><td>menu_design_ring</td>
<td>Right-click ▸ Design ▸ Ring, expanded but not yet clicked.</td>
<td>Baseline, at least one custom ring already added in Settings so the submenu shows more than the three bundled cards (optional but more representative).</td>
<td>The Ring submenu: DOMY / MORPH / Omega (+ any custom cards) above the separator, Gold/Silver/Bronze letters below it.</td></tr>

<tr><td>66</td><td>hands_classic</td>
<td>Design ▸ Hands ▸ CLASSIC.</td>
<td>Hands = CLASSIC.</td>
<td>Close crop centered on the hub, showing all three teardrop hands clearly at a readable time (e.g. ~10:10 equivalent on the 24h face) so their distinct lengths are visible.</td></tr>

<tr><td>67</td><td>hands_steel</td>
<td>Design ▸ Hands ▸ STEEL (already default).</td>
<td>Baseline.</td>
<td>Same crop/time as 66 for a direct side-by-side comparison.</td></tr>

<tr><td>68</td><td>menu_design_hands</td>
<td>Right-click ▸ Design ▸ Hands, expanded.</td>
<td>Baseline, ideally with a custom hand pack already added via Settings so the submenu shows 3 entries, not 2.</td>
<td>The Hands submenu listing CLASSIC, STEEL (+ any custom packs), with the active one checked.</td></tr>

<tr><td>69</td><td>menu_design_size</td>
<td>Right-click ▸ Design ▸ Size, expanded.</td>
<td>Baseline.</td>
<td>All five presets (360/540/720/1080/1440 px) with 720 checked.</td></tr>

<tr><td>70</td><td>size_compare</td>
<td>Design ▸ Size, shot three times.</td>
<td>Diameter = 360, then 720, then 1440; same pointer/theme/location each time.</td>
<td>Three full-dial captures at true relative scale (do not resize the images individually afterward — capture them at native pixel size so the size difference itself is the point), arranged smallest-to-largest.</td></tr>

<tr><td>71</td><td>menu_theme_earth</td>
<td>Right-click ▸ Theme ▸ Earth, expanded.</td>
<td>Baseline.</td>
<td>Clean / Atmosphere radio group, the separator, and the Date checkbox beneath it (note in the caption that Date grays out below 540 px).</td></tr>

<tr><td>72</td><td>earth_clean_vs_atmo</td>
<td>Theme ▸ Earth ▸ Clean, then Theme ▸ Earth ▸ Atmosphere (already default).</td>
<td>Two crops, only earth_style differs.</td>
<td>Close crop on the Earth marker alone, same season/day-night phase both times, so only the clean-vs-atmosphere art difference reads.</td></tr>

<tr><td>73</td><td>weekday_planet_signs</td>
<td>Theme ▸ Day slot ▸ Weekday ▸ Planet signs.</td>
<td>Weekday theme = planet_signs.</td>
<td>Full dial (2-column grid crop matching the existing 24-28 framing), the seven planet-glyph medallions on their arms.</td></tr>

<tr><td>74</td><td>weekday_egypt</td>
<td>Theme ▸ Day slot ▸ Weekday ▸ Egyptian gods.</td>
<td>Weekday theme = egypt.</td>
<td>Same framing; Ra/Khonsu/Montu/Thoth/Amun/Hathor/Osiris visible.</td></tr>

<tr><td>75</td><td>weekday_slavic</td>
<td>Theme ▸ Day slot ▸ Weekday ▸ Slavic gods.</td>
<td>Weekday theme = slavic.</td>
<td>Same framing; Dažbog/Hors/Svetovid/Veles/Perun/Mokoš/Morana visible.</td></tr>

<tr><td>76</td><td>weekday_alchemy</td>
<td>Theme ▸ Day slot ▸ Weekday ▸ Alchemy.</td>
<td>Weekday theme = alchemy.</td>
<td>Same framing; the seven metal still-lifes (Gold/Silver/Iron/Quicksilver/Tin/Copper/Lead) visible.</td></tr>

<tr><td>77</td><td>weekday_japan</td>
<td>Theme ▸ Day slot ▸ Weekday ▸ Japanese week.</td>
<td>Weekday theme = japan.</td>
<td>Same framing; the seven yōbi medallions with kanji labels visible.</td></tr>

<tr><td>78</td><td>weekday_religion_alt</td>
<td>Theme ▸ Day slot ▸ Weekday ▸ Religions II.</td>
<td>Weekday theme = religion_alt.</td>
<td>Same framing; Mithraism/Druidism/Zoroastrianism/Shamanism/Sikhism/Babylon/Voodoo visible.</td></tr>

<tr><td>79</td><td>weekday_greek_colored</td>
<td>Theme ▸ Day slot ▸ Weekday ▸ Greek gods ▸ Colored.</td>
<td>Weekday theme = greek, its metal = colored.</td>
<td>Same framing as the existing 25_weekday_greek, so the reader can flip between the bronze-plate look and this full-color art directly.</td></tr>

<tr><td>80</td><td>menu_theme_weekday_metal</td>
<td>Right-click ▸ Theme ▸ Day slot ▸ Weekday ▸ Greek gods, expanded (a metal-carrying theme opens its own sub-submenu instead of activating directly).</td>
<td>Baseline.</td>
<td>The Gold / Bronze / Silver / Colored radio group nested under Greek gods, to show this per-theme submenu exists only on the three metal themes (Greek, Norse, Professions) — the other eight activate with one click.</td></tr>

<tr><td>81</td><td>slot_ascendant</td>
<td>Theme ▸ Day slot ▸ Ascendant ▸ Sign.</td>
<td>Day slot mode = ascendant, style = sign.</td>
<td>The badge in the day-slot position with a visibly different sign than whatever the Info slot or the date would suggest is "today's" sign — make the point that Ascendant changes roughly every two hours, independent of the calendar.</td></tr>

<tr><td>82</td><td>menu_theme_slots_day</td>
<td>Right-click ▸ Theme ▸ Day slot, expanded (Astrology and Chinese zodiac as nested submenus, not expanded further).</td>
<td>Baseline.</td>
<td>Weekday / Time / Date / Day length / Astrology / Ascendant / Chinese zodiac as the Day slot submenu's entries (Weekday holds the 11-theme list + Names; the three text modes gray while the Pointer element is on).</td></tr>

<tr><td>83</td><td>slot_info_time</td>
<td>Design ▸ Pointer ▸ Compass (needed for the Info slot to always be available); Theme ▸ Info slot ▸ Time (already default mode).</td>
<td>Pointer = Compass (octa). Everything else baseline.</td>
<td>Full dial, the digital time readable in the Compass's reserved bottom arm.</td></tr>

<tr><td>84</td><td>slot_info_paired_weekday</td>
<td>Design ▸ Pointer ▸ Aurora; Elements ▸ Weekday on; Elements ▸ Info slot on; Theme ▸ Day slot ▸ Weekday ▸ Norse gods; Theme ▸ Info slot ▸ Weekday ▸ Greek gods.</td>
<td>Pointer = Aurora, Weekday theme = norse, Info slot mode = weekday with info_slot_theme = greek. Both the day-slot body and the info-slot body must be on at once.</td>
<td>Both bottom badges side by side — today's Norse god on one side, today's Greek god on the other — demonstrating the two slots can each run a fully independent theme.</td></tr>

<tr><td>85</td><td>menu_theme_slots_info</td>
<td>Right-click ▸ Theme ▸ Info slot, expanded (Weekday/Astrology/Ascendant/Chinese zodiac as nested submenus, not expanded further).</td>
<td>Baseline.</td>
<td>Weekday / Time / Date / Day length / Astrology / Ascendant / Chinese zodiac as the Info slot submenu's entries — the SAME shape as the Day slot's.</td></tr>

<tr><td>86</td><td>colorful_on_off</td>
<td>Elements ▸ Colorful, toggled off for the second half.</td>
<td>Two crops: Colorful on (baseline) and Colorful off.</td>
<td>The same daylight/twilight arc region both times — colored hues in one, plain white transparency in the other.</td></tr>

<tr><td>87</td><td>solar_rotation_off</td>
<td>Right-click ▸ Solar rotation, unchecked.</td>
<td>Solar rotation = off. Shoot at a moment where true solar noon is visibly offset from 12 at the default location (any non-equinox-noon moment in Belgrade works) so the "upright" effect is obvious against every other screenshot in the Guide, which shows it ON.</td>
<td>Full dial standing upright — 12 and 24 exactly at top and bottom, no tilt on the star, Aura or Umbra.</td></tr>

<tr><td>88</td><td>tray_click_through</td>
<td>Right-click ▸ Click-through, checked; then right-click the TRAY icon (the dial itself no longer takes clicks).</td>
<td>Click-through = on.</td>
<td>The tray menu with Click-through visibly checked, making clear the tray is the way back out of the mode.</td></tr>

<tr><td>89</td><td>settings_theme_rotation</td>
<td>Settings… ▸ scroll to "Theme rotation".</td>
<td>Enabled checked, at least 4-5 theme checkboxes ticked (enough to show the grid), "Every" set to a readable number, at least one metal-theme dropdown visible, Follow ring color unchecked so its three metal combos show as enabled.</td>
<td>The whole group: Enabled checkbox, the theme checkbox grid, the Every N minutes/hours row, the per-theme metal dropdowns, the Follow ring color checkbox.</td></tr>

<tr><td>90</td><td>settings_system</td>
<td>Settings… ▸ scroll to "System" (bottom of the dialog).</td>
<td>Baseline.</td>
<td>The single "Start with Windows" checkbox group.</td></tr>

</table>

---

<a id="appendix-reused"></a>
## Appendix — Reused Images (No Reshoot Needed)

These 53 images carry over unchanged from the current Guide into the
redesign; no action needed on any of them.

📁 assets/guide/
  🖼️ 01_day-night.png
  🖼️ 02_pointer_prism.png
  🖼️ 04_pointer_seasons.png
  🖼️ 05_pointer_compass.png
  🖼️ 06_pointer_trinity.png
  🖼️ 07_umbra_full.png
  🖼️ 08_umbra_half.png
  🖼️ 09_umbra_light.png
  🖼️ 10_umbra_dark.png
  🖼️ 11_earth_moon.png
  🖼️ 12_earth_legend.png
  🖼️ 13_moon_legend.png
  🖼️ 14_diamond_legend.png
  🖼️ 15_day_legend.png
  🖼️ 16_night_legend.png
  🖼️ 17_dawn_legend.png
  🖼️ 18_dusk_legend.png
  🖼️ 19_rings.png
  🖼️ 21_time_travel.png
  🖼️ 22_ring_domy_gold.png
  🖼️ 23_ring_domy_silver.png
  🖼️ 24_weekday_planets.png
  🖼️ 25_weekday_greek.png
  🖼️ 26_weekday_norse.png
  🖼️ 27_weekday_religion.png
  🖼️ 28_weekday_professions.png
  🖼️ 29_slot_zodiac.png
  🖼️ 30_slot_chinese.png
  🖼️ 31_settings_location.png
  🖼️ 32_settings_opacity.png
  🖼️ 33_settings_sizes.png
  🖼️ 34_settings_custom_ring.png
  🖼️ 35_menu_elements.png
  🖼️ 36_ring_morph_silver.png
  🖼️ 37_settings_palette.png
  🖼️ 38_settings_ring_tint.png
  🖼️ 39_settings_language.png
  🖼️ 40_settings_window.png
  🖼️ 41_tint_light_gold.png
  🖼️ 42_tint_dark_gold.png
  🖼️ 43_tint_green.png
  🖼️ 44_tint_blue.png
  🖼️ 45_tint_lavender.png
  🖼️ 46_tint_brown.png
  🖼️ 47_palette_prism_paint.png
  🖼️ 48_palette_prism_light.png
  🖼️ 49_palette_compass_paint.png
  🖼️ 50_palette_compass_light.png
  🖼️ 51_palette_seasons.png
  🖼️ 52_palette_trinity.png
  🖼️ 53_settings_custom_hands.png

Two existing captions need a light text edit even though their images
don't move (out of scope for this document, flagged for whoever writes
the new captions.json entries):

- `35_menu_elements`'s caption should note the Earth STYLE choice moved
  out of Elements and into Theme ▸ Earth (chapter 10) — Elements now
  only toggles the marker on/off, not clean-vs-atmosphere.
- `29_slot_zodiac`/`30_slot_chinese`'s captions currently say "The
  Compass slot" — should become "The Info slot" (chapter 19): the old
  Compass slot IS today's Info slot; the Day slot is the weekday unit's
  own position (chapter 18).

---

<a id="appendix-conventions"></a>
## Appendix — Naming and Crop Conventions

- New filenames continue the existing flat `NN_description` stem
  convention (`54_menu_top_level` … `90_settings_system`), all lower
  snake_case, no theme/chapter prefix beyond the description itself —
  matching every existing file in `assets/guide/`.
- Menu screenshots are the one genuinely new SHOT TYPE this redesign
  introduces — the current 53 images never show the menu chrome itself,
  only its effects on the dial or the Settings dialog's groups. Capture
  them at whatever OS scaling the owner normally runs; PySide6 menus
  are not part of the dial's own DPI-aware rendering, so no special
  diameter setting affects them.
- Full-dial crops: crop to the circle's own edge, transparent margin
  discarded (matching 01/07-10/11's existing framing).
- Two-column theme grids (chapters 15-16): keep the same crop framing
  used by the existing 24-28 set so the new theme images tile into the
  same grid cells at the same visual weight.
- Comparison pairs (59/60 paint vs light, 61/62 umbra forms, 72 clean
  vs atmo, 86 colorful on/off, 70 size compare): shoot both halves at
  the identical crop rectangle and, where time-of-day affects the
  render (daylight arc, Earth phase), within the same few minutes so
  only the toggled setting differs between the two.
