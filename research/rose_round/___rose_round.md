# research/rose_round/

The Rose of the Twenty-Four's FIGURE round (2026-07-27/28) — the people who
ride the Rose's three wheels (Legacy/Character, Prophecy/Vertices, and the
Thirteen-Axes wave's Edge seats). The wheels' own SEAT lancets (arms +
circle companions) are written in `research/prompts/archetype/` sheets; this
folder is exclusively the PEOPLE who fill those seats — three registers
(archetypal, historical, modern) and, where a seat has one, both polarities
(luminous + fallen).

Not part of the app runtime — owner-facing prompt sheets and their matching
article sets, read by [PromptPainter](../../../PromptPainter/instructions.md)
and by the article-merge pipeline respectively.

## Files

| File | One line |
|------|----------|
| [Character Figure Plates](character_figures_prompts.md) | The Legacy (Character compass) wheel's 48 people — 8 directions × 3 registers × 2 polarities |
| [Character Figure Articles](character_figures_articles.md) | One Charter-rule-6 deed argument per Character figure, 48 entries |
| [Vertex Figure Plates](vertices_figures_prompts.md) | The Prophecy wheel's 48 people — the Cube's 8 vertices × 3 registers × 2 polarities |
| [Vertex Figure Articles](vertices_figures_articles.md) | One deed argument per Prophecy-wheel figure, 48 entries |
| [Cube Vertex Arm Plates](vertices_prompts.md) | The Prophecy wheel's own 8 SEAT windows (arms, not people) — parallel of the Character wheel's direction lancets |
| [Edge Figure Plates](edge_figures_prompts.md) | The Thirteen-Axes wave's 48 people — the 8 new edge seats × 3 registers × 2 polarities |

## Connections

### Uses
- [The Cube Canon](../../CUBE.md) — the seating doctrine every sheet here
  implements (the Eight Vertices, the Rose's Prophecy wheel, the
  Thirteen-Axes edge seats)
- [Character Archetype Prompts](../prompts/archetype/character_prompts.md),
  [Edge Cell Plates](../prompts/archetype/edges_prompts.md) — the SEAT
  lancets these figure sheets fill (not reopened here)

### Used by
- The owner's generation sessions; the article sets feed the article-merge
  pipeline the same way [Merge Articles](../__about/merge_articles.md) did
  for the pantheon wave

## Design Decisions

Figures are split from seats: a seat (lancet + circle) is written once in
`prompts/archetype/`, and the THREE register sets of people who might fill
it live here, so a re-cast of "who sits where" never touches the seat art.
Charter rule 6 (the subject is the ACT, the person's name is the label on
the deed) governs every article file in this folder.
