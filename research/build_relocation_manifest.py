"""RESTRUCTURE Phase 1 — deterministic relocation map generator.

Walks the REAL assets/ tree and computes, for EVERY .png/.svg, its new
home under the one-hierarchy taxonomy sealed in RESTRUCTURE.md
(2026-07-22). The rules encoded here ARE the Folder Relocation Map +
the Naming Convention (source folder -> filename suffix) + the Theme
Renames + the figure-first alt resolution.

This is the Gate-1 artifact's engine: run it to (re)produce
`research/relocation_manifest.md` — every old->new pair, per-root
PNG/SVG counts before and after, and a loss check (total in == total
out, no file dropped). The executing session runs `git mv` against the
emitted pairs (the `--emit-mv` mode prints a ready-to-run shell list),
then repoints the code in the SAME commit.

Pure stdlib, no Qt, no project imports — safe to run standalone.
Usage:
    python research/build_relocation_manifest.py            # write manifest
    python research/build_relocation_manifest.py --emit-mv  # print git mv list
"""

from __future__ import annotations

import sys
from pathlib import Path

ASSETS = Path(__file__).resolve().parents[1] / "assets"

# --- source folder -> terminal filename suffix (Naming Convention) -----------
SOURCE_SUFFIX = {"gemini": "_gem", "chatgpt": "_gpt"}

# --- Category-2 (weeks) group placement, folder-level ------------------------
# theme folder name (on disk, pre-rename) -> group key
THEME_GROUP = {
    "planets": "celestial_bodies", "cosmos": "celestial_bodies",
    "continents": "celestial_bodies",
    "greek": "myth", "norse": "myth", "egypt": "myth", "slavic": "myth",
    "monsters": "myth", "chinese_myth": "myth",
    "bible": "faith", "religion": "faith",
    "alchemy": "crafts", "japan": "crafts", "profession": "crafts",
    "corporate": "crafts",
    "wolf": "societies", "bee": "societies", "elephant": "societies",
    # wow / cyberpunk / starwars handled specially (block -> own theme, gaming)
}
# theme folder rename (key + folder + display are aligned elsewhere)
THEME_RENAME = {
    "monsters": "age_of_heroes",
    "chinese_myth": "celestial_court",
    "religion": "creeds",
}
# gaming block folder -> standalone theme key (RESTRUCTURE renames table)
WOW_BLOCK = {"alliance": "wow_alliance", "horde": "wow_horde", "evil": "wow_evil"}
CP_BLOCK = {"gangs": "cp_gangs", "street": "cp_street", "power": "cp_corpo"}
SW_BLOCK = {"svetla": "sw_jedi", "tamna": "sw_sith", "nova": "sw_dyad"}

# --- figure-first alt resolution: seat filename stem -> real figure stem -----
# From the prompt sheets (cyberpunk_prompts.md / starwars_prompts.md): a
# seat-named alt file (e.g. gangs/primary/alt/Aldecaldos.png) actually
# depicts a DIFFERENT rotating figure (Mox). Under figure-first the file
# carries the figure's OWN name and leaves alt/ into the parent register.
ALT_FIGURE = {
    "Aldecaldos": "Mox", "Maelstrom": "Barghest", "VoodooBoys": "6thStreet",
    "Animals": "Scavengers", "Jackie": "Panam", "Wakako": "Padre",
    "Kerry": "LizzyWizzy", "SaburoArasaka": "RosalindMyers",
    "Yorinobu": "KurtHansen", "AltCunningham": "RacheBartmoss",
    "Finn": "Phasma", "Maz": "DJ", "Ghosts": "Exegol",
}
# alt folders whose files MIRROR the parent's names (same figure, second
# artwork) -> the file becomes <stem>_v2 in the parent, NOT a rename.
# (Detected generically: if the alt file's stem also exists in the parent
# directory, it is a version sibling; otherwise it is a seat->figure alt.)


def _suffix_stem(stem: str, source: str | None) -> str:
    """Append the terminal source suffix (Naming Convention: source last)."""
    return stem + SOURCE_SUFFIX[source] if source else stem


def _split_source(parts: tuple[str, ...]) -> tuple[str | None, tuple[str, ...]]:
    """(source, remaining) — source is parts[1] when it is gemini/chatgpt,
    stripped from the path; else None and parts unchanged (from index 1)."""
    if len(parts) >= 2 and parts[1] in SOURCE_SUFFIX:
        return parts[1], parts[2:]
    return None, parts[1:]


def _resolve_alt(rest: list[str], parent_dir: Path, source: str | None) -> str:
    """Turn a `.../alt/<name>.png` tail into its flattened, figure-first
    filename. rest is the path segments BELOW the source (the last three
    are typically ['<register>', 'alt', '<name>.png'])."""
    alt_idx = rest.index("alt")
    fname = rest[-1]
    stem = fname[:-4] if fname.lower().endswith(".png") else fname
    parent_stem_exists = (parent_dir / fname).exists()
    if stem in ALT_FIGURE:
        new_stem = ALT_FIGURE[stem]
    elif parent_stem_exists:
        new_stem = f"{stem}_v2"          # same-figure second artwork
    else:
        new_stem = stem                   # unknown; keep name, flatten
    # drop the 'alt' segment: register folder keeps the file
    keep = rest[:alt_idx] + [_suffix_stem(new_stem, source) + ".png"]
    return "/".join(keep)


def new_path(rel: Path) -> str | None:
    """New assets-relative path for an old assets-relative path, or None
    to leave it in place (logo files, already-migrated, unknown)."""
    parts = rel.parts
    root = parts[0]
    name = parts[-1]

    # Untouched build-pipeline contract
    if root in {"logo.svg", "logo-setup.svg"} or rel.name in {
        "logo.svg", "logo-setup.svg"
    }:
        return None
    if root == "_state":
        return None  # Phase 2

    source, rest = _split_source(parts)  # rest excludes root+source
    rest = list(rest)
    is_alt = "alt" in rest

    # ---- weekday -> weeks/<group>/<theme> ----
    if root == "weekday":
        theme = rest[0]
        tail = rest[1:]
        if theme in {"wow", "cyberpunk", "starwars"}:
            block = tail[0]
            bmap = {"wow": WOW_BLOCK, "cyberpunk": CP_BLOCK,
                    "starwars": SW_BLOCK}[theme]
            new_theme = bmap.get(block, f"{theme}_{block}")
            inner = tail[1:]           # register/.../file
            group = "gaming" if theme != "starwars" else "films"
            base = ["weeks", group, new_theme]
        else:
            group = THEME_GROUP.get(theme)
            if group is None:
                return f"UNRESOLVED::weekday/{theme}"
            new_theme = THEME_RENAME.get(theme, theme)
            inner = tail
            base = ["weeks", group, new_theme]
        if is_alt:
            parent = ASSETS.joinpath(*parts[:-1]).parent  # dir above alt/
            flat = _resolve_alt(inner, parent, source)
            return "/".join(base + [flat])
        newname = _suffix_stem(name[:-4], source) + name[-4:]
        return "/".join(base + inner[:-1] + [newname])

    # ---- emblem -> weeks/inner_wheel/<family> ----
    if root == "emblem":
        newname = _suffix_stem(name[: name.rfind(".")], source) + \
            name[name.rfind("."):]
        return "/".join(["weeks", "inner_wheel"] + rest[:-1] + [newname])

    # ---- archetype -> archetypes/<family> ; calendar -> calendars/almanac ----
    if root == "archetype":
        family = rest[0]
        stem = name[:-4]
        # Figure rename (RESTRUCTURE renames table): Child_Dawn -> Child_Anchor
        # (the child's hearth-role becomes the Anchor; the Dawn survives as
        # the stacked time-reading only).
        if family == "family" and stem == "Child_Dawn":
            stem = "Child_Anchor"
        newname = _suffix_stem(stem, source) + name[-4:]
        if family == "calendar":       # English months Jan-Dec = almanac
            return "/".join(["calendars", "almanac"] + rest[1:-1] + [newname])
        if is_alt:                     # tetramorph/alt version siblings
            parent = ASSETS.joinpath(*parts[:-1]).parent
            flat = _resolve_alt(rest, parent, source)
            return "/".join(["archetypes"] + [flat])
        return "/".join(["archetypes"] + rest[:-1] + [newname])

    # ---- badge -> archetypes/<family>/circle | scale | trinity/badges ----
    if root == "badge":
        kind = rest[0]
        newname = _suffix_stem(name[:-4], source) + name[-4:]
        if kind == "circle":
            fam = rest[1]              # circle/<family>/...
            stem = name[:-4]
            if fam == "family" and stem == "Child_Dawn":  # figure rename
                stem = "Child_Anchor"
            cname = _suffix_stem(stem, source) + name[-4:]
            return "/".join(["archetypes", fam, "circle"] + rest[2:-1] +
                            [cname])
        if kind == "scale":
            return "/".join(["archetypes", "scale"] + rest[1:-1] + [newname])
        if kind == "trinity":
            return "/".join(["archetypes", "trinity", "badges"] + rest[1:-1] +
                            [newname])
        if kind == "season":
            return "/".join(["celestial", "seasons", "badges"] + rest[1:-1] +
                            [newname])
        return f"UNRESOLVED::badge/{kind}"

    # ---- eclipse / era / earth -> celestial/... ----
    if root == "eclipse":
        newname = _suffix_stem(name[:-4], source) + name[-4:]
        if is_alt:
            parent = ASSETS.joinpath(*parts[:-1]).parent
            return "/".join(["celestial", "eclipse"] +
                            [_resolve_alt(rest, parent, source)])
        return "/".join(["celestial", "eclipse"] + rest[:-1] + [newname])
    if root == "era":
        newname = _suffix_stem(name[:-4], source) + name[-4:]
        if is_alt:
            parent = ASSETS.joinpath(*parts[:-1]).parent
            return "/".join(["celestial", "era"] +
                            [_resolve_alt(rest, parent, source)])
        return "/".join(["celestial", "era"] + rest[:-1] + [newname])
    if root == "earth":               # flat, no source subtree
        return "/".join(["celestial", "earth"] + rest)

    # ---- zodiac -> calendars/zodiac (astrology) | calendars/chinese ----
    if root == "zodiac":
        fam = rest[0]
        newname = _suffix_stem(name[:-4], source) + name[-4:]
        if fam == "chinese":
            return "/".join(["calendars", "chinese"] + rest[1:-1] + [newname])
        # astrology (the zodiac proper)
        return "/".join(["calendars", "zodiac"] + rest[:-1] + [newname])

    # ---- months (Slavic) -> calendars/slavic_months ----
    if root == "months":
        newname = _suffix_stem(name[:-4], source) + name[-4:]
        return "/".join(["calendars", "slavic_months"] + rest[:-1] + [newname])

    # ---- instrument (+ merge hands/ring/icons/guide/subdial under it) ----
    if root == "instrument":
        newname = _suffix_stem(name[:-4], source) + name[-4:]
        return "/".join(["instrument"] + rest[:-1] + [newname])
    if root in {"hands", "ring", "icons", "guide", "subdial"}:
        # not source-split (rest already = parts[1:]); merge under instrument/
        return "/".join(["instrument", root] + list(parts[1:]))

    return f"UNRESOLVED::{root}"


def main() -> int:
    files = sorted(
        p for p in ASSETS.rglob("*")
        if p.is_file() and p.suffix.lower() in {".png", ".svg"}
    )
    pairs: list[tuple[str, str | None]] = []
    per_root_before: dict[str, int] = {}
    per_root_after: dict[str, int] = {}
    unresolved: list[str] = []
    for p in files:
        rel = p.relative_to(ASSETS)
        root = rel.parts[0] if not rel.parts[0].endswith((".svg",)) else "(root)"
        per_root_before[root] = per_root_before.get(root, 0) + 1
        np = new_path(rel)
        if np and np.startswith("UNRESOLVED::"):
            unresolved.append(f"{rel.as_posix()}  ->  {np}")
            np = None
        pairs.append((rel.as_posix(), np))
        nroot = (np.split("/", 1)[0] if np else root)
        per_root_after[nroot] = per_root_after.get(nroot, 0) + 1

    if "--emit-mv" in sys.argv:
        for old, np in pairs:
            if np and np != old:
                print(f'git mv "assets/{old}" "assets/{np}"')
        return 0

    total = len(pairs)
    changed = sum(1 for o, n in pairs if n and n != o)
    unchanged = sum(1 for o, n in pairs if n is None)

    lines: list[str] = []
    lines.append("# Relocation Manifest — RESTRUCTURE Phase 1\n")
    lines.append(
        "AUTO-GENERATED by `research/build_relocation_manifest.py` from a "
        "live walk of `assets/`. Do not hand-edit — re-run the generator.\n")
    lines.append(f"- Files scanned (png+svg): **{total}**")
    lines.append(f"- Relocated/renamed: **{changed}**")
    lines.append(f"- Left in place (logo, _state Phase 2): **{unchanged}**")
    lines.append(f"- UNRESOLVED: **{len(unresolved)}**\n")

    lines.append("## Per-root counts (before -> after)\n")
    lines.append("| Root | Before | Root (new) | After |")
    lines.append("|---|---:|---|---:|")
    allroots = sorted(set(per_root_before) | set(per_root_after))
    for r in allroots:
        lines.append(
            f"| {r} | {per_root_before.get(r, 0)} | {r} | "
            f"{per_root_after.get(r, 0)} |")
    lines.append(
        f"\n**Total before {sum(per_root_before.values())} == "
        f"total after {sum(per_root_after.values())}** "
        f"({'OK — no file lost' if sum(per_root_before.values()) == sum(per_root_after.values()) else 'MISMATCH'}).\n")

    if unresolved:
        lines.append("## UNRESOLVED (map by consumer before executing)\n")
        for u in unresolved:
            lines.append(f"- `{u}`")
        lines.append("")

    lines.append("## Every old -> new pair\n")
    lines.append("```")
    for old, np in pairs:
        if np is None:
            continue
        if np == old:
            continue
        lines.append(f"{old}")
        lines.append(f"    -> {np}")
    lines.append("```")

    out = ASSETS.parent / "research" / "relocation_manifest.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out}  ({changed} moves, {len(unresolved)} unresolved)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
