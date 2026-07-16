"""Generate ROSTER.md — the root master systematics document (owner
2026-07-15): every theme, every figure, its seat in our position
system, and per-SOURCE asset coverage (Gemini / ChatGPT, colored,
dual, ninth) — the one place to check what is missing ("Gemini 9th
wolf", "ChatGPT tuesday Alchemy").

Run from the project root:  python research/build_roster.py
Regenerate after any theme-table change or art drop.
"""

import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from config import constants, defaults  # noqa: E402

SOURCES = ("gemini", "chatgpt")
SEATS = ("sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn")
DAYS = {
    "sun": "Sunday", "moon": "Monday", "mars": "Tuesday",
    "mercury": "Wednesday", "jupiter": "Thursday", "venus": "Friday",
    "saturn": "Saturday",
}
# The seat archetypes — the position system every figure serves.
ARCHETYPES = (
    ("sun", "Sunday", "white-gold", "Justice / Humility",
     "Pride / Servility", "Glory / Awe", "Ruler"),
    ("moon", "Monday", "blue", "Serenity", "Fear", "Calm", "Physician"),
    ("mars", "Tuesday", "orange", "Courage", "Wrath", "Zeal", "Soldier"),
    ("mercury", "Wednesday", "purple", "Wisdom", "Greed", "Sorrow",
     "Merchant"),
    ("jupiter", "Thursday", "yellow", "Generosity", "Excess", "Joy",
     "Priest"),
    ("venus", "Friday", "red", "Love", "Jealousy", "Passion", "Artist"),
    ("saturn", "Saturday", "green", "Patience", "Envy", "Renewal",
     "Farmer"),
)
# The Ninths (owner 8+1 doctrine) — keep in sync with the topic table
# in app/encyclopedia.py.
NINTHS = {
    "wolf": ("Sigma", "wolf/primary/sigma"),
    "bee": ("The Swarm", "bee/primary/swarm"),
    "elephant": ("The Graveyard", "elephant/primary/graveyard"),
    "cosmos": ("The Big Bang", "cosmos/primary/big_bang"),
    "greek": ("Hades", "greek/primary/hades"),
    "norse": ("Baldur", "norse/primary/baldur"),
    "egypt": ("Set", "egypt/primary/set"),
    "slavic": ("Crnobog", "slavic/primary/crnobog"),
    "alchemy": ("The Philosopher's Stone", "alchemy/primary/stone"),
    "profession": ("The Jester", "profession/primary/Jester"),
    "religion": ("The Unknown God", "religion/primary/unknown_god"),
    "religion_alt": ("The Lost Mystery", "religion/secondary/lost_mystery"),
    "bible": ("Melchizedek", "bible/primary/melchizedek"),
    "bible_dark": ("Legion", "bible/dark/legion"),
}
THEME_ORDER = (
    "planets", "planet_signs", "planets_art", "greek", "norse", "egypt",
    "slavic", "alchemy", "japan", "religion", "religion_alt",
    "profession", "wolf", "bee", "elephant", "bible", "bible2",
    "bible_dark", "cosmos", "virtues", "sins", "moods",
)

missing: list[str] = []


def mark(source: str, rel: str) -> str:
    """✔ / — per source-resolved file; a miss joins the shortage list.
    `rel` is canonical under weekday/ — the ../emblem step-ups the
    theme tables use resolve to their real root before the SOURCE
    segment lands (mirroring config.paths.art_file)."""
    import posixpath

    canonical = posixpath.normpath(f"weekday/{rel}")
    root, _, rest = canonical.partition("/")
    path = ROOT / "assets" / root / source / f"{rest}.png"
    if path.exists():
        return "✔"
    missing.append(f"{source}: {root} {rest}.png")
    return "—"


def theme_dir(theme: str) -> str:
    if theme == "planets":
        return "planets/primary"
    return defaults.WEEKDAY_THEME_DIRS[theme]


def colored_dir(theme: str) -> str | None:
    if theme not in constants.METAL_THEMES:
        return None
    base = theme_dir(theme)
    return base.rsplit("/", 1)[0] + "/colored"


def weekday_sections() -> list[str]:
    out = []
    for theme in THEME_ORDER:
        title = defaults.WEEKDAY_THEME_TITLES.get(
            theme, theme.replace("_", " ").title()
        )
        files = (
            defaults.WEEKDAY_THEME_FILES.get(theme)
            or {seat: seat for seat in SEATS}   # planets: body = file
        )
        names = defaults.WEEKDAY_THEME_NAMES.get(theme, {})
        colored = colored_dir(theme)
        head = "| Seat | Day | Figure | File | Gemini | ChatGPT |"
        rule = "|---|---|---|---|---|---|"
        if colored:
            head += " Colored G | Colored C |"
            rule += "---|---|"
        out.append(f"### {title} (`{theme}`)\n")
        out.append(head)
        out.append(rule)
        base = theme_dir(theme)
        for seat in SEATS:
            stem = files[seat]
            display = names.get(seat, stem)
            row = (
                f"| {seat} | {DAYS[seat]} | {display} | `{stem}` "
                f"| {mark('gemini', f'{base}/{stem}')} "
                f"| {mark('chatgpt', f'{base}/{stem}')} |"
            )
            if colored:
                row += (
                    f" {mark('gemini', f'{colored}/{stem}')} "
                    f"| {mark('chatgpt', f'{colored}/{stem}')} |"
                )
            out.append(row)
        dual = defaults.WEEKDAY_DUAL_FILES.get(theme)
        if dual:
            dual_name = defaults.WEEKDAY_DUAL_NAMES.get(theme, "Dual")
            if isinstance(dual_name, tuple):
                dual_name = " / ".join(dual_name)
            row = (
                f"| dual | Sunday | {dual_name} | `{dual.rsplit('/', 1)[-1]}` "
                f"| {mark('gemini', dual)} | {mark('chatgpt', dual)} |"
            )
            if colored:
                cdual = dual.replace("/primary/", "/colored/")
                if cdual != dual:
                    row += (
                        f" {mark('gemini', cdual)} "
                        f"| {mark('chatgpt', cdual)} |"
                    )
                else:
                    row += " n/a | n/a |"
            out.append(row)
        ninth = NINTHS.get(theme)
        if ninth:
            name, rel = ninth
            row = (
                f"| ninth | — | {name} | `{rel.rsplit('/', 1)[-1]}` "
                f"| {mark('gemini', rel)} | {mark('chatgpt', rel)} |"
            )
            if colored:
                crel = rel.replace("/primary/", "/colored/")
                row += (
                    f" {mark('gemini', crel)} | {mark('chatgpt', crel)} |"
                )
            out.append(row)
        out.append("")
    return out


PANTHEON_THEMES = ("greek", "norse", "egypt", "slavic")


def pantheon_sections() -> list[str]:
    out = ["## Pantheon vs Planetary — per-seat coverage\n"]
    out.append(
        "Per pantheon theme, the seated Pantheon name against the "
        "Planetary fallback, with per-source on-disk coverage of every "
        "PANTHEON candidate plate (`defaults.WEEKDAY_PANTHEON`).\n"
    )
    for theme in PANTHEON_THEMES:
        table = defaults.WEEKDAY_PANTHEON[theme]
        title = defaults.WEEKDAY_THEME_TITLES.get(theme, theme.title())
        out.append(f"### {title} — Pantheon (`{theme}`)\n")
        out.append(
            "| Seat | Day | Pantheon Name | Candidates | Gemini | ChatGPT |"
        )
        out.append("|---|---|---|---|---|---|")
        for seat in SEATS:
            candidates = table["files"][seat]
            name = table["names"][seat]
            cand_str = ", ".join(f"`{c.rsplit('/', 1)[-1]}`" for c in candidates)
            g_marks = " ".join(mark("gemini", c) for c in candidates)
            c_marks = " ".join(mark("chatgpt", c) for c in candidates)
            out.append(
                f"| {seat} | {DAYS[seat]} | {name} | {cand_str} "
                f"| {g_marks} | {c_marks} |"
            )
        dual = table.get("dual")
        if dual:
            dual_names = table.get("dual_names", ("Dual",))
            dual_name = " / ".join(dual_names)
            cand_str = ", ".join(f"`{c.rsplit('/', 1)[-1]}`" for c in dual)
            g_marks = " ".join(mark("gemini", c) for c in dual)
            c_marks = " ".join(mark("chatgpt", c) for c in dual)
            out.append(
                f"| dual | Sunday | {dual_name} | {cand_str} "
                f"| {g_marks} | {c_marks} |"
            )
        out.append("")
    return out


def zodiac_mark(source: str, rel: str) -> str:
    path = ROOT / "assets" / "zodiac" / source / f"{rel}.png"
    if path.exists():
        return "✔"
    missing.append(f"{source}: zodiac {rel}.png")
    return "—"


def zodiac_sections() -> list[str]:
    out = ["## Zodiac — Astrology (12 signs + the 13th)\n"]
    styles = constants.ZODIAC_STYLE_ART_DIRS       # sign/logo/const/colored
    signs = [name for name, _ in constants.ZODIAC_SIGNS]
    head = "| Sign | " + " | ".join(
        f"{style} G | {style} C" for style in styles
    ) + " |"
    out.append(head)
    out.append("|---|" + "---|" * (2 * len(styles)))
    for sign in signs + ["Ophiuchus"]:
        cells = []
        for style, folder in styles.items():
            cells.append(zodiac_mark("gemini", f"{folder}/{sign}"))
            cells.append(zodiac_mark("chatgpt", f"{folder}/{sign}"))
        out.append(f"| {sign} | " + " | ".join(cells) + " |")
    out.append("\n## Zodiac — Chinese (12 animals + the Cat)\n")
    dirs = {"primary": "chinese/primary", "colored": "chinese/colored"}
    out.append("| Animal | primary G | primary C | colored G | colored C |")
    out.append("|---|---|---|---|---|")
    for animal in list(constants.CHINESE_ANIMALS) + ["Cat"]:
        cells = []
        for folder in dirs.values():
            cells.append(zodiac_mark("gemini", f"{folder}/{animal}"))
            cells.append(zodiac_mark("chatgpt", f"{folder}/{animal}"))
        out.append(f"| {animal} | " + " | ".join(cells) + " |")
    out.append("")
    return out


def flat_mark(root: str, source: str, rel: str) -> str:
    path = ROOT / "assets" / root / source / f"{rel}.png"
    if path.exists():
        return "✔"
    missing.append(f"{source}: {root} {rel}.png")
    return "—"


def flat_section(title: str, root: str, groups: dict[str, list[str]]):
    out = [f"## {title}\n"]
    out.append("| Group | Item | Gemini | ChatGPT |")
    out.append("|---|---|---|---|")
    for group, items in groups.items():
        for item in items:
            out.append(
                f"| {group} | `{item.rsplit('/', 1)[-1]}` "
                f"| {flat_mark(root, 'gemini', item)} "
                f"| {flat_mark(root, 'chatgpt', item)} |"
            )
    out.append("")
    return out


def main() -> None:
    lines: list[str] = []
    lines.append("# ROSTER — the Master Systematics")
    lines.append("")
    lines.append(
        "**GENERATED — do not edit by hand.** Regenerate with "
        "`python research/build_roster.py` after any theme-table "
        "change or art drop. Every theme, every figure, its seat in "
        "the position system, and per-source asset coverage — the one "
        "place to check what is missing."
    )
    lines.append(f"\n_Last generated: {date.today().isoformat()}_\n")
    lines.append("## The Position System — seat archetypes\n")
    lines.append(
        "| Seat | Day | Color | Virtue | Vice | Mood | Estate |"
    )
    lines.append("|---|---|---|---|---|---|---|")
    for row in ARCHETYPES:
        lines.append("| " + " | ".join(row) + " |")
    lines.append(
        "\nEvery weekday theme seats SEVEN figures on these archetypes"
        " plus the Sunday DUAL (the Servant face) and the NINTH (the"
        " excluded one, Encyclopedia-seated). Legend: ✔ art on disk,"
        " — missing; G/C = Gemini/ChatGPT source.\n"
    )
    lines.append("## Weekday Themes\n")
    lines += weekday_sections()
    lines += pantheon_sections()
    lines += zodiac_sections()
    lines += flat_section(
        "Badges", "badge",
        {
            "trinity": ["trinity/Faith", "trinity/Hope", "trinity/Love"],
            "season": [
                f"season/{s}" for s in (
                    "Spring", "Summer", "Autumn", "Winter",
                    "WetSeason", "DrySeason",
                )
            ],
            "turning point": [
                f"season/turning_point/{s}" for s in (
                    "SummerSolstice", "WinterSolstice", "Equinox",
                )
            ],
            "meteorological": [
                f"season/meteorological/{s}" for s in (
                    "Spring", "Summer", "Autumn", "Winter",
                )
            ],
            "scale": [
                "scale/Lucifer_Triangle", "scale/Judas_Triangle",
                "scale/Union",
            ],
            "scale glass": [
                f"scale/glass/{s}" for s in (
                    "Judas_Triangle", "Lucifer_Triangle",
                    "Judas_Triangle_v2", "Lucifer_Triangle_v2",
                    "Union_Meeting", "Union",
                )
            ],
            # Only the silver master is REQUIRED art — gold and bronze
            # recolor from it at runtime (0.14.238 radial bezel mask).
            "subdial (silver master)": ["subdial/silver/center"],
        },
    )
    lines += flat_section(
        "Emblems", "emblem",
        {
            "virtue": [
                f"virtue/{v}" for v in (
                    "Justice", "Serenity", "Courage", "Wisdom",
                    "Generosity", "Love", "Patience", "Humility",
                )
            ],
            "sin": [
                f"sin/{s}" for s in (
                    "Pride", "Fear", "Wrath", "Greed", "Excess",
                    "Jealousy", "Envy", "Servility",
                )
            ],
            "mood": [
                f"mood/{m}" for m in (
                    "Glory", "Calm", "Zeal", "Sorrow", "Joy",
                    "Passion", "Renewal", "Awe", "Eclipse",
                )
            ],
            "intelligence": [
                f"intelligence/{i}" for i in (
                    "bodily_kinesthetic", "interpersonal", "linguistic",
                    "naturalist", "logical_mathematical", "musical",
                    "existential", "intrapersonal", "spatial",
                )
            ],
        },
    )
    lines.append("## Shortage List — everything the tables marked —\n")
    if missing:
        by_source: dict[str, list[str]] = {}
        for entry in missing:
            source, rest = entry.split(": ", 1)
            by_source.setdefault(source, []).append(rest)
        for source in sorted(by_source):
            items = by_source[source]
            lines.append(f"**{source}** ({len(items)}):")
            lines.append("")
            for item in items:
                lines.append(f"- {item}")
            lines.append("")
    else:
        lines.append("Nothing missing — every table cell is ✔.")
    (ROOT / "ROSTER.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )
    print(f"ROSTER.md written — {len(missing)} missing items flagged")


if __name__ == "__main__":
    main()
