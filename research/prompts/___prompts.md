# prompts/

The image-generation prompt sheets — the owner generates art from these,
one theme at a time, top to bottom. Since the roster doctrine closed
(2026-07-15), **each weekday theme owns ONE complete file**: every plate
the theme needs across BOTH rosters (Planetary + Pantheon), in every
register the theme ships (bronze + colored), including the Sunday dual and
the Ninth — with **REUSE** notes where an existing plate serves a new seat
(nothing to generate) and **SUPERSEDED / DO NOT GENERATE** notes for
everything the doctrine retired. Check the root
[Roster](../../ROSTER.md) for what is already on disk per source.

## Before writing a NEW sheet

Read [How to Write a Prompt Sheet](../../../PromptPainter/instructions.md)
first — PromptPainter's own sheet contract, owned and enforced by its
parser (`painter/sheet_parser.py`), also behind the GUI's own
**Instructions** button. Every image needs a
`**Title** → \`path.png\`` line right in its own entry; skip it and the
tool silently drops that image with ZERO warning. Verify any sheet before
handing it to the owner:

```bash
python main.py "path/to/your_sheet.md" --dry-run
```

run from `Gadgets/PromptPainter/` — zero problems and the expected item
count means the sheet is safe to queue.

## Folders

| Folder | One line |
|--------|----------|
| [Weekday (subfolder)](weekday/___weekday.md) | One complete sheet per weekday theme — the doctrine's main body |
| [Archetype (subfolder)](archetype/___archetype.md) | One sheet per pointer archetype (Trinity/Prism/Compass/Calendar) plus the CUBE WAVE's third wheels and the Thirteen-Axes edge/sacred plates |
| [Calendars (subfolder)](calendars/___calendars.md) | The five new Dozens riding the Calendar pointer (RESTRUCTURE Phase 3) |
| [Emblem (subfolder)](emblem/___emblem.md) | The Inner Wheel emblem themes — Virtue, Sin, Mood, Intelligences |
| [Zodiac (subfolder)](zodiac/___zodiac.md) | Astrology (12 signs + Ophiuchus) and the Chinese 12-animal cycle |
| [Badge (subfolder)](badge/___badge.md) | The Judas–Lucifer Scale, the Trinity/Seasons/Turning-Point badges, the BADGE SISTEM 1:1 circles |
| [Instrument (subfolder)](instrument/___instrument.md) | "The Instrument" Encyclopedia chapter art and the subdial plates |
| [Months (subfolder)](months/___months.md) | The Slavic Months Calendar-pointer 12-set |
| [Era (subfolder)](era/___era.md) | The Age of Light / Age of Darkness ERA TERMS set |
| [Eclipse (subfolder)](eclipse/___eclipse.md) | The seven eclipse-category Encyclopedia emblems |
| [Titles (subfolder)](titles/___titles.md) | Every weekday theme's title-page plate, the one sheet that intentionally carries lettering |
| [Monsters (subfolder)](monsters/___monsters.md) | The Greek Monsters weekday theme |
| [Chinese (subfolder)](chinese/___chinese.md) | The Chinese Mythology weekday theme |
| [WoW (subfolder)](wow/___wow.md) | The World of Warcraft weekday theme — three parallel casts |
| [Cyberpunk (subfolder)](cyberpunk/___cyberpunk.md) | The Cyberpunk 2077 weekday theme — three parallel casts, the first rotation seats |
| [Star Wars (subfolder)](starwars/___starwars.md) | The Star Wars weekday theme — three casts, plus two copyright-workaround variant sheets |
| [Corporate (subfolder)](corporate/___corporate.md) | THE CORPORATION weekday theme |
| [Guide (subfolder)](guide/___guide.md) | The Guide dialog's owner-facing screenshot checklist (Serbian) |
| [Icons (subfolder)](icons/___icons.md) | The small SVG icon request list (Serbian) |

Every sheet not covered by the folders above (the legacy regeneration
sheets and closed sets folded straight into the Weekday folder) is listed
in [Weekday (subfolder)](weekday/___weekday.md).

## `COVERAGE.md`

[Prompt Coverage](COVERAGE.md) is the AGENT-FACING gap ledger — read it
before writing a sheet, not after. It covers everything
[Roster](../../ROSTER.md) does NOT walk: the archetype tree, era, eclipse,
the subdial masters, the Calendar-pointer 12-set, the BADGE SISTEM 1:1
circles, and the owner's own hand-built collections.

**The Rose of the Twenty-Four's GEOMETRY has no sheet** (CUBE.md §The
Rose): three identical octa stars offset 15°, 24 rays in 8 palette colours
— computed, drawn, never painted. The FIGURES that ride it are art, and
their round is open — [Rose Round (subfolder)](../rose_round/___rose_round.md).

## Connections

### Uses
- [The Pantheon Catalog](../pantheon_catalog.md) — the locked rosters and
  doctrine every sheet implements
- [Roster](../../ROSTER.md) — per-source coverage (what exists)

### Used by
- [Research (folder)](../___research.md) — this folder's own entry point
- The owner's generation sessions (Gemini / ChatGPT)

## Design Decisions
One theme = one file, because the owner generates in order and hunted
across files before (the colored Skoll case). Prompts are copied
byte-identical when they move; border identities are per-theme constants
(meander / knotwork / cartouche / kolovrat…) so a series stays
recognizable; images never carry lettering — the ONE documented exception
in the whole project is [Theme Title Prompts](titles/theme_title_prompts.md),
where the wordmark IS the point of the plate (owner item 7).
