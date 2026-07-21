# God-File Split Plan — Phase 1 (Discussion Only, Rule #11)

**Status:** AWAITING OWNER APPROVAL. Zero code changed while producing this
document (Rule #11). Covers every file the brief's Phase 0 flagged, plus a
fresh recount (see below) that found three more files have crossed the
1,000-line line since that snapshot was taken.

## Methodology note — the Phase 0 numbers have drifted

Phase 0's line counts (measured earlier) and a fresh recount just now
(`git show HEAD:<file>` raw `\n` count — `Get-Content | Measure-Object -Line`
on this box under-counts `app/controller.py` by ~170 lines; the byte count
is ground truth) disagree, and not by rounding:

| File | Phase 0 count | Current count | Note |
|---|---:|---:|---|
| `app/controller.py` | 2990 | **3184** | +194, organic growth (ADD WATCH, R5b, R8a rounds landed since) |
| `config/defaults.py` | 2803 | **2986** | +183 |
| `render/compositor.py` | 2794 | **2942** | +148 |
| `render/layers.py` | 2574 | **2807** | +233 |
| `tests/test_pointer.py` | 2508 | **2820** | +312 |
| `app/encyclopedia.py` | 2147 | **2593** | +446 |
| `tests/test_settings_dialog.py` | 1607 | **2156** | +549 |
| `app/observatory.py` | 1491 | **1646** | +155 |
| `app/settings_dialog.py` | 1434 | **1566** | +132 |
| `tests/test_archetype.py` | 1143 | **1320** | +177 |
| `config/constants.py` | 1018 | **1116** | +98 |
| `render/assets.py` | 939 (smell) | **1027** | **crossed into violation** |
| `tests/test_eclipse.py` | 938 (smell) | **1080** | **crossed into violation** |
| `tests/test_skins.py` | 905 (smell) | **1155** | **crossed into violation** |

This plan uses the **current** numbers and treats all 14 files above as
in-scope violations. It's normal drift between a Phase 0 snapshot and Phase 1
planning on an actively-worked repo, not evidence of anything wrong — noted
for the record so the owner isn't surprised the totals moved.

**Current smell zone (500–1,000 lines, current recount):**

| File | Lines | One-line verdict |
|---|---:|---|
| `tests/test_observatory.py` | 921 | One responsibility (Observatory goldens + render smoke). Leave alone. |
| `app/settings_store.py` | 754 | One `Settings` dataclass + one `SettingsStore`. Cohesive despite size — the length is field count, not mixed concerns. **Recommend: never split.** |
| `tests/test_shortcuts_r5b.py` | 666 | Single round's golden tests. Cohesive. Leave alone. |
| `tests/test_menu_rework.py` | 644 | Single round's golden tests. Cohesive. Leave alone. |
| `tests/test_render.py` | 603 | One responsibility (offscreen render smoke). Leave alone. |
| `tests/test_settings_store.py` | 599 | Mirrors `settings_store.py` 1:1. Leave alone. |
| `app/time_travel.py` | 573 | One dialog class. Leave alone, watch it — Quick Jump rows keep growing. |

---

## Split-technique policy (applied consistently below)

1. **Data / independent-classes god-files** (`render/layers.py`,
   `config/defaults.py`, `config/constants.py`, `render/assets.py`) — no
   single object owns shared mutable state across the whole file. These
   become **real packages/sibling modules**: each piece moves verbatim into
   its own file, imports get specific, done.
2. **Single-God-Object god-files** (`WatchController`, `Compositor`,
   `SettingsDialog`, `EncyclopediaDialog`) — dozens of methods all
   reading/writing the SAME `self.*` state. Breaking these into independent
   classes changes calling convention everywhere and risks behavior drift
   under a "zero behavior change" mandate. Instead: **plain-Python mixin
   classes**, one file per responsibility cluster, method bodies moved
   verbatim, composed via multiple inheritance on the original class.
   **Hard rule:** mixins derive from nothing (never `QObject`) — mixing two
   `QObject`-branch bases breaks shiboken's metaclass. Only the shell class
   derives from `QObject`/`QDialog`. Verify zero method-name collisions
   across mixins before assembling.
3. **No barrel `__init__.py` re-exports.** When a file becomes a package,
   its `__init__.py` stays near-empty. Every caller's import is rewritten
   to the real new submodule path — a convenience re-export IS the
   forbidden shim in package clothing (Rule #6).

---

## 1. `app/controller.py` (3,184) — `WatchController`

**Responsibilities:** module-level skin assembly (~645 lines of pure
functions: `build_skin`, `apply_display_settings`, theme/metal resolution,
`watch_title`...); composition-root lifecycle (init/run/quit/tick/wake,
settings recovery, position persistence, secret buffer, translation
worker); menu building + gating (~410); dialog/mini-window openers (~345);
jump machinery (~330); shortcut dispatch (~300); settings-apply setters
(~260).

**Proposed map:**

```
📁 app/
  🐍 controller.py         ← shell: lifecycle only, composes 6 mixins (~900-1000; documented exception)
  🐍 skin_builder.py       ← build_skin, apply_display_settings, metal resolution (pure, ~300)
  🐍 weekday_set.py        ← themed/pantheon weekday sets, slot resolution (pure, ~250)
  🐍 menu_builder.py       ← _MenuBuilderMixin: _build_menu + gating + watch_title (~470)
  🐍 dialog_openers.py     ← _DialogOpenersMixin: every _open_*/_on_*_closed (~345)
  🐍 jump_engine.py        ← _JumpEngineMixin: jumps, simulation, coverage, TT (~430)
  🐍 shortcut_dispatch.py  ← _ShortcutDispatchMixin: _on_shortcut + cycles + fast travel (~340)
  🐍 settings_apply.py     ← _SettingsApplyMixin: every _set_*/_install_skin (~260)
```

**Risks:** highest-stakes move (the composition root; everything
owner-visible on every launch). Concrete caller sweep enumerated: tests
import `apply_display_settings` (×10 sites), `build_skin` (×7),
`_classic_slot_theme`, `_filtered_sun_anchors`/`_filtered_moon_events`,
`_next_rotation_theme`, `watch_title`, `WatchController` (×7 files) — every
`from app.controller import X` repoints to the real new module. Mixin
MRO/shiboken discipline mandatory. The ~900-line post-split shell is a
documented exception (true composition root), not forced smaller.

## 2. `config/defaults.py` (2,986) — domain split, no shim

One flat namespace: ~250 constants + ~17 pure functions across a dozen
disjoint domains. **Proposed:** 12 domain modules; `defaults.py` DELETED
(no re-export shim, Rule #6):

```
📁 config/
  🐍 window.py             ← dial/ring/hand/tray geometry (~230)
  🐍 runtime.py            ← scheduling, settings schema, warm tuning (~100)
  🐍 shortcuts.py          ← SHORTCUTS + display maps + FAST_TRAVEL_* (~200)
  🐍 art_paths.py          ← every *_ART_DIR, icons, rotation convention (~220)
  🐍 weekday_registry.py   ← the theme tables + pantheon + months (~550; flag if over)
  🐍 continents_poles.py   ← continents, poles, Greenwich (~120)
  🐍 metal_shades.py       ← METAL_SHADES + swap tuning (~55)
  🐍 eclipse.py            ← every ECLIPSE_*/GLOW_ECLIPSE_* (~180)
  🐍 palette.py            ← palettes, wedges, umbra, glows (~140)
  🐍 observatory.py        ← OBSERVATORY_*/REPORT_* chart tokens (~230)
  🐍 ui_chrome.py          ← buttons, theme colors, dialog sizing, encyclopedia (~260)
  🐍 subdial.py            ← SUBDIAL_*/SLOT_ROUNDEL_*/small seconds (~110)
  🐍 default_skin.py       ← DEFAULT_SKIN alone (only importer of skins.manifest) (~130)
```

**The real cost:** **46 files** import defaults (worst: `tests/
test_pointer.py` with 204 individual `defaults.NAME` references;
`app/encyclopedia.py` 145; `render/layers.py` 126; `render/compositor.py`
92). Mechanical (each name maps to exactly one destination) but wide — do
it as a scripted codemod, one domain batch at a time, suite green after
each batch. `config/paths.py`'s module globals (art_source, subdial_set,
metal shades) stay untouched. Layering preserved: new modules import only
paths/constants; only `default_skin.py` imports skins.manifest.

## 3. `render/compositor.py` (2,942) — shell + 4 mixins + pure helpers

**Proposed:** `compositor.py` shell (paint orchestration, caching, tooltip
hub, warm sweep, ~400) + `hover_html.py` (pure module-level helpers, ~310)
+ mixins: `encyclopedia_target.py` (~390), `hover_weekday_archetype.py`
(~545), `hover_astro_ring.py` (~450, dominated by the 245-line
`_arm_tooltip` — moved whole, internal decomposition is a later round),
`hover_astro_text.py` (~200), `hover_moon_earth_eclipse.py` (~460).

**Risks:** the most owner-scrutinized correctness surface (hover tuning
history); manual hover-every-element pass required after. Tests import 8
private names directly — repoint to `render.hover_html`. Sequence AFTER
the layers split so imports are written once.

## 4. `render/layers.py` (2,807) — real package split

```
📁 render/layers/
  🐍 base.py               ← Cadence, RenderContext, Layer ABC, shared paint primitives (~220)
  🐍 background_star.py    ← Background/Star layers + umbra/aurora/calendar-wheel geometry (~380)
  🐍 ring.py               ← RingLayer (~180)
  🐍 weekday.py            ← WeekdayLayer + body draw/label law (~330)
  🐍 slot.py               ← SlotLayer + everything a subdial slot shows (~700; 4× smaller than today)
  🐍 center_body.py        ← CenterBodyLayer + dual/ninth face law (~280)
  🐍 archetype.py          ← Archetype layers + figure geometry (~330)
  🐍 year_marker.py        ← YearMarkerLayer + glows/eclipse render state (~370)
  🐍 hand.py               ← HoverLift + HandLayer (~90)
```

**Risks:** heaviest render-side caller sweep (~25 private names imported
across compositor/assets/10+ tests). `calendar_wheel` family legitimately
shared by three consumers — documented, not duplicated.

## 5. `app/encyclopedia.py` (2,593) — package (topics + dialog mixins)

`html_helpers.py` (~230), `topics_weekday.py` (~290),
`topics_pantheon_wider.py` (~150), `topics_continents.py` (~100),
`topics_registry.py` (the 542-line `_topics()` split along its own
per-family dict boundaries into named sub-builders — an explicitly
separate, reviewable step, ~400-550), `dialog.py` shell (~350) +
`gallery_section.py` (~250) + `entry_view_section.py` (~440) mixins.
~15 test call sites import `_topics`/`_TOPIC_GROUPS`/block constants by
name — all repoint.

## 6. `app/observatory.py` (1,646) — package

`chart_base.py` (geometry helpers + `_ChartBase`, ~360), `line_chart.py`
(`_LineChart` + `_DayLengthChart`, ~290), `eclipse_chart.py` (~330),
`dialog.py` (`ObservatoryDialog` + info panel + `_EnlargeDialog`, ~635 —
composition-root exception).

## 7. `app/settings_dialog.py` (1,566) — mixin PILOT

The dialog already self-organizes into 7 nav sections — the cleanest split
boundary in the plan (UI-given, not inferred): `dialog.py` shell (~230) +
7 section mixins (location ~300, display ~230, colors ~280, custom art
~230, themes ~230, language/system ~200). Only 5 external call sites.
**Recommended as the mixin-technique pilot.**

## 8. `render/assets.py` (1,027) — surgical sibling extraction

`assets.py` keeps `AssetCache` at its current import path (20+ callers,
ZERO churn); extract `asset_recolor.py` (letter metals, recolored plates,
metal variants, tinted, ~250) + `asset_variants.py` (ring face color, moon
phase render, subdial plates, scaled variants, icons, ~330). ~15 total
callers. **Cheapest, safest — the opening move.**

## 9. `config/constants.py` (1,116) — DEFER

Same ~45-file fan-in as defaults, weaker cohesion case (its own .md frames
it as one topic: product invariants), and sequencing benefit: prove the
codemod on defaults first. Re-ask next inventory pass.

## 10. Test god-files — DEFER all five

They are flat pytest files already organized by section banners; nothing
outside tests imports them; they are the caller-sweep TARGET of every
production split above (heavily edited regardless); restructuring the
regression-catching tool during a behavior-preserving refactor is
asymmetric risk. Revisit in a dedicated round after production splits
stabilize.

---

## Explicit "do not split" list

| Item | Why |
|---|---|
| `app/settings_store.py` | One dataclass + one store; size is field count. Never split. |
| `config/constants.py` | Defer — prove the defaults codemod first. |
| 5 test god-files | Defer — see §10. |
| controller post-split shell (~900-1000) | True composition root; documented exception. |
| observatory `dialog.py` (~635) | Same reasoning, smaller scale. |

---

## Execution order (Phase 2, commit-sized steps)

Each step ends with: full pytest green, purity gate green, a `python -m
core` sanity read, and a real app launch exercising the moved feature.

| # | Step | Why here |
|---|---|---|
| 0 | **Owner approves this plan** | Hard gate (Rule #11) |
| 1 | `render/assets.py` surgical split | Smallest, safest — proves sibling extraction |
| 2 | `app/settings_dialog.py` → mixin package | Smallest God-Object, UI-given boundaries — proves the mixin technique |
| 3 | **Owner checkpoint** — review the two pilot diffs | Both techniques confirmed before scaling |
| 4 | `app/observatory.py` → package | Independent blast radius |
| 5 | `app/encyclopedia.py` → package (incl. the `_topics()` internal split as its own reviewable step) | Self-contained to one dialog + registry |
| 6 | `render/layers.py` → package | BEFORE compositor so its imports are written once |
| 7 | `render/compositor.py` → shell + mixins | Manual hover-everything pass required |
| 8 | **Owner checkpoint** — full app pass: every dialog, hover, shortcut | Before the two highest-risk moves |
| 9 | `config/defaults.py` → 12 modules, deleted | 46-file sweep as scripted per-domain batches, one domain committed at a time |
| 10 | `app/controller.py` → shell + mixins | Last, deliberately — techniques proven on lower stakes |
| 11 | **Owner checkpoint** — Definition of Done checklist | Closes Phase 2 |
| 12 | Phase 3 — all `___folder.md`/module docs + navigation chain | Rule #3 |

**Owner-approval checkpoints: 4** (steps 0, 3, 8, 11).

**Totals:** ~54 new modules replacing 8 old ones (`defaults.py` deleted
outright; the other 7 shrink to shells or packages).
