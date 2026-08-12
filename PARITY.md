# PARITY.md — The Parity Ledger

Born with the first CONTRACT PACK export (Phase 1 of the Pocket Watch
charter — [ANDROID.md](ANDROID.md) → THE PARITY LAW, mechanism 3, "PARITY
LEDGER — GATE"). THE PARITY LAW's exact rule: *"A feature shipped on one
platform and not the other records its own debt in the SAME commit (what,
where, which session owes it) — the exact mirror of the theme staging
ledger, proven on the 429 invisible images. Deferring is allowed;
deferring SILENTLY is not. A session that touched shared layers or shipped
platform features cannot end without an up-to-date ledger."*

This file is that record. It never lies by omission: every gap Phase 1
knowingly left open is named here, with what exists, what is owed, and
which future session owes it. An entry is closed by editing it in place
(strike the row or move it to "Closed") in the same commit that ships the
missing half — never by deleting it silently.

## How to read a row

| Column | Meaning |
|--------|---------|
| **What** | The shared-layer feature or table in question |
| **Shipped** | What exists today, and on which side (desktop / bakery / phone) |
| **Owed** | What is still missing for full parity |
| **Owed by** | Which future phase/session closes it (per ANDROID.md → The Phases) |

## Open Debts

| What | Shipped | Owed | Owed by |
|------|---------|------|---------|
| Per-theme art bake (WebP downscale + recolor) | **The downscale + WebP half is DONE and SHARED** (art-bakery round, 2026-08-12): `desktop/setup/make_art_bake.py` bakes the gitignored `masters/` inbox into `shared/assets/` at each area's `WORKING_SET_CEILINGS` ceiling, WebP q90 — 3.8 GB of masters into roughly half a gigabyte, and Compose reads WebP natively, so the phone consumes the SAME bytes the desktop does with no second encode | What remains is the phone-specific half: PER-THEME packing (one pack per theme, not one flat tree), a phone-resolution ceiling if 800/1200 px proves larger than a handset needs, and the RECOLOR pass done here rather than on the device — ANDROID.md §The Bakery, third bullet | A dedicated bakery-art session (later in Phase 1, before Phase 4's Widget MVP needs real art) |
| Databases as-is (byte-for-byte) | `Database/` JSON files already live under `shared/Database/` since the three-folder migration (2026-08-12) | No manifest/hash entry for the raw `Database/` tree yet distinguishes it from the CONTRACT PACK's own generated `shared/contract/` tables — a consumer cannot yet tell "read `Database/` directly" from "read `contract/tables/`" for a given fact without reading this repo's own docs | A dedicated bakery session, before Phase 2 (`:core` port) needs a single authoritative pointer |
| Baked-art manifest + versioning | `shared/assets/_bake_manifest.json` (art-bakery round, 2026-08-12) records the encode quality, the ceiling table in force, and per baked file: its MASTER's sha256, the output path, dimensions and byte size. The master hash is doing real work — the masters are gitignored, so this is the only way the repo can say which master a shipped file came from, or notice one was silently replaced | It is not VERSIONED the way `shared/contract/manifest.json` is (no `pack_version`), and no consumer pins it — the phone will need both once it ships art, so a stale device pack is detectable | The same dedicated bakery-art session as row 1 |
| `tables/encyclopedia_tree.json`'s companion, the encyclopedia ARTICLE bodies | `shared/contract/tables/encyclopedia_tree.json` exports the wholes → cards STRUCTURE only (deliberately, per this round's brief) | The article text itself (`Database/encyclopedia.json`) is not yet part of any CONTRACT PACK manifest — it already lives at `shared/Database/encyclopedia.json` and travels with the "Databases as-is" row above, but is not individually hashed in `shared/contract/manifest.json` | Folded into the row-2 bakery session above, or Phase 7 (Encyclopedia, Compose reader) if it needs its own cadence |
| `:core` module docs (MD-First) | `android/core` is ported and green against all 31 golden vectors (0.14.986/987), `android/README.md` carries the name story | The Kotlin project has no `___folder.md`/`__about` tier yet — the DOCS LAW's coverage guard scans `desktop/` only, so this debt is visible nowhere but here | The next android session (Phase 3 feasibility probe, or a dedicated docs round) |
| The pack-PIN guard (THE PARITY LAW, mechanism 1, phone half) | This repo's half exists: `desktop/tests/test_contract_pack.py` goes red when a registry table changes without a re-export | The consumer-side guard — a `:core` test failing when the app pins a pack older than `shared/contract/manifest.json`'s current version — does not exist yet (trivial while both live in one repo, but the law names both halves) | The next android session, together with the `:core` docs row above |

## Closed

*(none yet — this is Phase 1's first pack)*
