# ANDROID — The Pocket Watch Charter

The sealed decisions for the phone edition, cast by the owner on two ballot
pages (2026-08-10/11). This file is the SOURCE OF TRUTH for the founding
session of the phone project and for Phase 1 (the bakery) in this repo.
Nothing here is a proposal anymore — proposals died on the ballots; what
remains is law for the arc.

## Table of Contents

- [The Name](#the-name)
- [The Sealed Verdicts](#verdicts)
- [The Bakery — one source of truth](#bakery)
- [The Base Pack Agreement](#base-pack)
- [THE PARITY LAW — desktop and phone never diverge](#parity)
- [Platform Facts](#platform-facts)
- [The Phases](#phases)

<a id="the-name"></a>

## The Name

**Pocket Watch** (owner's pick, 2026-08-11). Watch Academy stays the desktop
edition; the phone carries its own name.

**The name story** (for the new project's README): *the phone is this
century's pocket — and the watch moves back in. Pocket Watch puts the full
DOMY dial on the home screen, the way a pocket watch once rode a waistcoat.*

The founding session still runs the formal START rules (scaffold, guards,
registration, logo, name story in the README) — the name itself is already
decided and is not reopened.

<a id="verdicts"></a>

## The Sealed Verdicts

| Question | Verdict |
|----------|---------|
| Technology | **Kotlin, native Android.** No KMP, no Flutter, no embedded Python. |
| Home | **New project with its own repo** (monorepo constitution), consuming the exported pack from this repo. |
| Widgets | **W1 dial-only + W2 dial-with-command-strip + W3 info bar.** Live Wallpaper NOT chosen. |
| W1 scope (owner's words) | The dial-only widget renders the COMPLETE watch face — jewels, pointer style, ring style (outer x inner), crown text, numerals, minutes, moving bodies — with per-instance settings. The widget IS the watch, never a reduced version. |
| Time travel | **Buttons on the widget strip + full mode in the app.** Offset ≠ 0 shows a visible TRAVEL badge on the widget; tapping the dial opens the app's Time Travel screen at the traveled moment. |
| Encyclopedia | **Native Compose reader**, same three-level model (wholes → cards → articles with variant switcher), from the same encyclopedia data. |
| Art delivery | **Base pack + themes on demand.** |
| Deep Time (56.6 MB) | **As on desktop: base install without it, download on demand.** Same two-tier doctrine, same detection and repository chaining. |
| Lock nature | **L1 — technical lock: not downloaded yet, download is free.** L1 is the foundation; if paid or progression unlocks ever come, they change the unlock CONDITION, never the lock machinery. |
| Sync | **THE PARITY LAW adopted** (see below). |

<a id="bakery"></a>

## The Bakery — one source of truth

This repo is the source of truth AND the bakery; the phone repo is a
consumer of the baked pack. THE ONE COPY RULE survives the platform split:
no table, text or image ever exists in two hand-maintained copies.

The bakery (Phase 1, work in THIS repo, before any Kotlin) produces the
**CONTRACT PACK**:

- **Golden vectors** — the golden test values exported as JSON so the
  Kotlin `:core` tests read the same truth the Python tests pin
  (Belgrade DST −4.17°→+10.76°, Tromsø regimes, moon 0.7400 on
  2026-07-07, mockup day 20.6.2025, equinox exactness…). The port of an
  algorithm is DONE when its vectors are green — no other criterion.
- **Config tables exported to JSON** — themes, rosters, ring presets,
  palette, encyclopedia tree. Tables are never re-typed in Kotlin.
- **Baked art** — phone-resolution downscale + WebP, recolored HERE by the
  existing transformer (the phone never recolors), packed PER THEME with a
  manifest. Measured 2026-08-10: `assets/` is 3,552 MB in 2,678 files —
  baking is not an optimization, it is the only way a phone app exists.
- **Databases as-is** — `Database/` JSON + SQLite travel byte-for-byte
  (67.9 MB, of which deep_time.sqlite 56.6 MB stays on-demand).
- **A manifest** — pack version + per-content hashes + the vector set.

<a id="base-pack"></a>

## The Base Pack Agreement (owner verdict 2026-08-11, refined the same day)

The boundary, in one line: **the sky is free; philosophy is locked.**

- **The instrument is INDIVISIBLE and never locked:** every plate (the ONE
  PLATE library), every ring preset (outer x inner), every pointer style
  with its color wheels and palettes, crown, backgrounds, hands, moving
  bodies — everything "where we change pointers, colors and all those
  styles" (owner's words). A watch missing one of its own parts is not a
  product.
- **All ASTRONOMICAL phenomena are base content, always:** the turning
  points (solstices, equinoxes, the seasons), the Moon (phases, tides),
  the Sun, the eclipses — what the sky itself shows and the dial itself
  displays, together with their encyclopedia topics.
- **Always-unlocked THEMES (owner's list):** **Planets**; **Months —
  Gregorian only** (the twelve Gregorian months with the named full moons;
  no other calendar's month cycle rides in the base); **Zodiac — BOTH the
  Western astrology zodiac AND the Chinese zodiac** (each in all its
  depictions, per "depictions are not themes").
- **LOCKED: every PHILOSOPHICAL thematic** — the figure casts, the Divine,
  the Character Cube, religions, creeds, pantheons, the Human Wheel… all of
  them L1 theme packs (free download). The exact per-theme manifest mapping
  is Phase 1 work, applying this boundary — never re-litigating it.
- **The THEME is the unit of locking** — one cast = one pack (its art AND
  its encyclopedia articles), the exact granularity THE THEME COMPLETION
  LAW already enforces.
- **A locked theme is VISIBLE but not enterable** (owner correction
  2026-08-11): its card shows in the picker and in the Encyclopedia wearing
  a lock; it cannot be opened — no article text, no art — until the theme
  is downloaded. The encyclopedia is gated WITH its theme, never separately.

<a id="parity"></a>

## THE PARITY LAW (owner decree 2026-08-11)

Born on the ballot from the owner's own instruction: design UP FRONT how new
implementations and changes are made so we never land in "changed on
desktop, stale on the phone — or the reverse."

Three mechanisms, with their enforcement classes declared:

1. **CONTRACT PACK with versions — LAW.** Every change to a SHARED layer
   (core math, `Database/`, config tables, texts, art) ends with a new pack
   export: version + manifest + current golden vectors. The phone repo pins
   exactly one pack version. Teeth: a guard test in the phone repo fails
   when the pin is older than the latest export; a guard test in this repo
   fails when a shared file changed with no new export — until either the
   pack is bumped or the debt is written into the ledger.
2. **Golden vectors as the semantic tooth — LAW.** The vectors travel IN
   the pack; Kotlin `:core` reads the same JSON the Python suite pins. A
   math change on desktop regenerates vectors, the new pack carries them,
   and a lagging phone goes RED instead of silently computing yesterday's
   truth.
3. **PARITY LEDGER — GATE.** A feature shipped on one platform and not the
   other records its own debt in the SAME commit (what, where, which
   session owes it) — the exact mirror of the theme staging ledger, proven
   on the 429 invisible images. Deferring is allowed; deferring SILENTLY is
   not. A session that touched shared layers or shipped platform features
   cannot end without an up-to-date ledger.

Conduct rules that follow:

- **Contract-first:** a feature touching shared layers lands its shared
  part in THIS repo first and ships as a pack — then both apps consume it.
  This holds for phone-born ideas too: their shared part returns to the
  bakery, never lives only on the phone.
- **Platform UI is NOT synced:** screens, menus, gestures are each
  platform's own. Truth is synced — data, math, texts, art — never looks.
- **The transition period is free:** until the phone project exists, the
  desktop moves unburdened. The law takes force with the FIRST pack export
  in Phase 1 — from then on every shared change is either in a pack or in
  the ledger. The law's guard tests and the ledger file are born in Phase 1,
  on both sides, together with that first pack.

<a id="platform-facts"></a>

## Platform Facts (established in the round-1 analysis, non-negotiable)

- An Android widget (AppWidget/RemoteViews) is handed a finished BITMAP —
  no free-form drawing. Our design has NO seconds hand: the hour hand moves
  0.25°/min, the minute hand 6°/min — **one refresh per minute suffices**,
  which is what makes the whole port reasonable.
- The stock `AnalogClock` widget cannot render this watch — its hour hand
  is hard-wired to a 12-hour revolution; ours is 24-hour. Own bitmap path,
  no exceptions.
- Clock-class apps legitimately hold exact-alarm rights
  (`SCHEDULE_EXACT_ALARM` / `USE_EXACT_ALARM`); nothing is drawn while the
  screen is off. Time/zone/date changes arrive as system broadcasts — the
  same events the desktop already handles (the SYNC lesson carries over as
  doctrine).
- Widget interaction is BUTTONS ONLY (PendingIntent) — no drag, no slider,
  no hover. Desktop hover legends become tap screens in the app.
- Transparency is native (alpha channel); a widget is a legitimate resident
  of the home screen — no Win+D problem exists there.
- Every widget instance has its own id and settings — "each watch its own
  observer and its own look", exactly the ONE COPY boundary.

<a id="phases"></a>

## The Phases

Sealed order; sizes are relative effort, not date promises. Phases 1 is
work in THIS repo; 2+ live in the Pocket Watch repo.

| # | Phase | Size | Status |
|---|-------|------|--------|
| 0 | Verdicts (two ballots) | — | **DONE 2026-08-11** |
| 1 | THE CONTRACT: golden-vector export, config→JSON export, the bakery (per-theme downscale+WebP+recolor, manifest), first pack + THE PARITY LAW's teeth on both sides | M | open |
| 2 | `:core` port — all math in pure Kotlin; done when every vector is green | M | open |
| 3 | `:render` port — FEASIBILITY PROBE: first complete DOMY bitmap at phone resolution, compared against the desktop render of the same moment | L | open |
| 4 | Widget MVP — dial-only, minute tick, transparent, city+theme at placement | M | open |
| 5 | App shell — Watch Face screen (8 sections), Settings, widget-instance management | L | open |
| 6 | Time Travel + Observatory in the app | L | open |
| 7 | Encyclopedia (Compose reader, lock-aware per the base pack agreement) | M | open |
| 8 | Widget variants W2+W3, battery audit, polish | M | open |

After all phases: the translation session and the first git/release — the
owner's call, outside this charter.
