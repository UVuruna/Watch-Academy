"""RESTRUCTURE Phase 2 — rewrite every prompt-sheet drop path to the new
one-hierarchy tree (sourceless; PromptPainter injects the `_gem`/`_gpt`
source SUFFIX at generation time — Phase 4). Same relocation rules as
`research/build_relocation_manifest.py`, minus the source-folder collapse
(sheets are already sourceless) and minus the filename suffix.

Walks every `research/prompts/**.md`, transforms each backticked
`assets/…png|svg` path in place, and reports the count. Idempotent:
a path already under a new root is left untouched.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROMPTS = ROOT / "research" / "prompts"

THEME_GROUP = {
    "planets": "celestial_bodies", "cosmos": "celestial_bodies",
    "continents": "celestial_bodies",
    "greek": "myth", "norse": "myth", "egypt": "myth", "slavic": "myth",
    "monsters": "myth", "chinese_myth": "myth",
    "bible": "faith", "religion": "faith",
    "alchemy": "crafts", "japan": "crafts", "profession": "crafts",
    "corporate": "crafts",
    "wolf": "societies", "bee": "societies", "elephant": "societies",
}
THEME_RENAME = {"monsters": "age_of_heroes", "chinese_myth": "celestial_court",
                "religion": "creeds"}
WOW_BLOCK = {"alliance": "wow_alliance", "horde": "wow_horde", "evil": "wow_evil"}
CP_BLOCK = {"gangs": "cp_gangs", "street": "cp_street", "power": "cp_corpo"}
SW_BLOCK = {"svetla": "sw_jedi", "tamna": "sw_sith", "nova": "sw_dyad"}
ALT_FIGURE = {
    "Aldecaldos": "Mox", "Maelstrom": "Barghest", "Voodoo_Boys": "6th_Street",
    "Animals": "Scavengers", "Jackie": "Panam", "Wakako": "Padre",
    "Kerry": "Lizzy_Wizzy", "Saburo_Arasaka": "Rosalind_Myers",
    "Yorinobu": "Kurt_Hansen", "Alt_Cunningham": "Rache_Bartmoss",
    "Finn": "Phasma", "Maz": "DJ", "Ghosts": "Exegol",
}

_PATH_RE = re.compile(r"assets/[A-Za-z0-9_./-]+\.(?:png|svg)")


def _flatten_alt(parts: list[str]) -> list[str]:
    """`.../alt/<name>.png` -> figure-first, flattened into the register."""
    alt_idx = parts.index("alt")
    fname = parts[-1]
    stem, ext = fname[:-4], fname[-4:]
    if stem in ALT_FIGURE:
        new = ALT_FIGURE[stem]
    else:
        new = f"{stem}_v2"          # version-style sibling (mirrors parent)
    return parts[:alt_idx] + [new + ext]


def transform(path: str) -> str:
    parts = path.split("/")            # ['assets', root, ...]
    root = parts[1]
    rest = parts[2:]
    # A stray source segment (a legacy source-qualified example path):
    # sheets are sourceless — PromptPainter injects the suffix — so drop it.
    if rest and rest[0] in ("gemini", "chatgpt"):
        rest = rest[1:]
    is_alt = "alt" in rest

    def join(*segs) -> str:
        flat: list[str] = []
        for s in segs:
            flat.extend(s if isinstance(s, list) else [s])
        return "/".join(["assets"] + flat)

    if root == "weekday":
        theme = rest[0]
        tail = rest[1:]
        if theme in ("wow", "cyberpunk", "starwars"):
            block = tail[0]
            bmap = {"wow": WOW_BLOCK, "cyberpunk": CP_BLOCK,
                    "starwars": SW_BLOCK}[theme]
            new_theme = bmap.get(block, f"{theme}_{block}")
            group = "gaming" if theme != "starwars" else "films"
            inner = _flatten_alt(tail[1:]) if is_alt else tail[1:]
            return join("weeks", group, new_theme, inner)
        group = THEME_GROUP.get(theme)
        if group is None:
            return path
        new_theme = THEME_RENAME.get(theme, theme)
        inner = _flatten_alt(tail) if is_alt else tail
        return join("weeks", group, new_theme, inner)

    if root == "emblem":
        return join("weeks", "inner_wheel", rest)

    if root == "archetype":
        fam = rest[0]
        if fam == "calendar":
            return join("calendars", "almanac", rest[1:])
        inner = rest
        if is_alt:
            inner = _flatten_alt(rest)
        # Child_Dawn -> Child_Anchor (figure rename)
        inner = ["Child_Anchor.png" if s == "Child_Dawn.png" else s
                 for s in inner]
        return join("archetypes", inner)

    if root == "badge":
        kind = rest[0]
        if kind == "circle":
            return join("archetypes", rest[1], "circle", rest[2:])
        if kind == "scale":
            return join("archetypes", "scale", rest[1:])
        if kind == "trinity":
            return join("archetypes", "trinity", "badges", rest[1:])
        if kind == "season":
            return join("celestial", "seasons", "badges", rest[1:])
        return path

    if root == "eclipse":
        return join("celestial", "eclipse",
                    _flatten_alt(rest) if is_alt else rest)
    if root == "era":
        return join("celestial", "era",
                    _flatten_alt(rest) if is_alt else rest)
    if root == "earth":
        return join("celestial", "earth", rest)

    if root == "zodiac":
        if rest and rest[0] == "chinese":
            return join("calendars", "chinese", rest[1:])
        return join("calendars", "zodiac", rest)

    if root == "months":
        return join("calendars", "slavic_months", rest)

    if root in ("hands", "ring", "icons", "guide", "subdial"):
        return join("instrument", root, rest)

    return path                        # instrument, logos, unknown -> as-is


def main() -> int:
    changed_files = 0
    changed_paths = 0
    for md in sorted(PROMPTS.rglob("*.md")):
        text = md.read_text(encoding="utf-8")

        def _sub(m: re.Match) -> str:
            nonlocal changed_paths
            old = m.group(0)
            new = transform(old)
            # Child_Dawn -> Child_Anchor everywhere (lancet AND its 1:1
            # circle companion) — the figure rename, RESTRUCTURE §renames.
            new = new.replace("Child_Dawn", "Child_Anchor")
            if new != old:
                changed_paths += 1
            return new

        new_text = _PATH_RE.sub(_sub, text)
        if new_text != text:
            md.write_text(new_text, encoding="utf-8")
            changed_files += 1
    print(f"rewrote {changed_paths} paths across {changed_files} sheets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
